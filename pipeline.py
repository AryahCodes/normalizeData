import argparse
import concurrent.futures
import os
import shutil
import subprocess
import tempfile
import time

import cv2
from cv2 import dnn_superres


def check_dependencies(model_path):
    if not shutil.which('ffmpeg'):
        raise RuntimeError("ffmpeg not found. Install with: brew install ffmpeg")
    if not shutil.which('ffprobe'):
        raise RuntimeError("ffprobe not found. Install with: brew install ffmpeg")
    if not os.path.isfile(model_path):
        raise RuntimeError(f"EDSR model not found at '{model_path}'. Download EDSR_x4.pb and place it in the project root, or pass --model <path>.")


def get_fps(video_path):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
             '-show_entries', 'stream=r_frame_rate', '-of', 'csv=p=0', video_path],
            capture_output=True, text=True
        )
    except FileNotFoundError:
        raise RuntimeError("ffprobe not found on PATH.")
    if result.returncode != 0:
        raise ValueError(f"ffprobe failed for '{video_path}': {result.stderr.strip()}")
    raw = result.stdout.strip()
    if '/' not in raw:
        raise ValueError(f"Unexpected ffprobe output for '{video_path}': {raw!r}")
    num, den = raw.split('/')
    return int(num) / int(den)


def fps_normalize(src, dst, target_fps=60):
    orig_fps = get_fps(src)
    print(f"  [FPS] {orig_fps:.2f} -> {target_fps} fps ... ", end='', flush=True)
    if abs(orig_fps - target_fps) <= 0.01:
        shutil.copy2(src, dst)
        print("already at target, copied.")
        return
    subprocess.run([
        'ffmpeg', '-y', '-i', src,
        '-filter:v', f'minterpolate=fps={target_fps}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-an',
        dst
    ], check=True, capture_output=True)
    print("done.")


def upscale_video(src, dst, model_path, scale=4):
    sr = dnn_superres.DnnSuperResImpl_create()
    sr.readModel(model_path)
    sr.setModel("edsr", scale)

    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError(f"OpenCV could not open '{src}'.")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(dst, fourcc, fps, (width * scale, height * scale))

    print(f"  [SR]  Upscaling {width}x{height} -> {width*scale}x{height*scale} ...")
    frame_count = 0
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            out.write(sr.upsample(frame))
            frame_count += 1
            if frame_count % 100 == 0:
                print(f"  [SR]  {frame_count} frames processed...", flush=True)
    finally:
        cap.release()
        out.release()
    print(f"  [SR]  Done. ({frame_count} frames)")


def process_video(filename, videos_dir, tmp_dir, final_dir, model_path, target_fps, scale):
    src = os.path.join(videos_dir, filename)
    tmp_dst = os.path.join(tmp_dir, filename)
    final_dst = os.path.join(final_dir, filename)

    print(f"\n[{filename}] Starting...")
    try:
        t0 = time.time()
        fps_normalize(src, tmp_dst, target_fps)
        t1 = time.time()
        print(f"  [FPS] completed in {t1-t0:.1f}s")

        upscale_video(tmp_dst, final_dst, model_path, scale)
        t2 = time.time()
        print(f"  [SR]  completed in {t2-t1:.1f}s")
        print(f"[{filename}] Done. Total: {t2-t0:.1f}s -> {final_dst}")
        return filename, True, None
    except Exception as e:
        print(f"[{filename}] FAILED — {e}")
        return filename, False, str(e)


def main():
    parser = argparse.ArgumentParser(description="Normalize video FPS and upscale resolution.")
    parser.add_argument('--videos-dir', default='videos', help='Input directory (default: videos)')
    parser.add_argument('--output-dir', default='final_videos', help='Output directory (default: final_videos)')
    parser.add_argument('--model', default='EDSR_x4.pb', help='Path to EDSR model file (default: EDSR_x4.pb)')
    parser.add_argument('--fps', type=int, default=60, help='Target FPS (default: 60)')
    parser.add_argument('--scale', type=int, default=4, help='Super-resolution scale factor (default: 4)')
    parser.add_argument('--workers', type=int, default=1, help='Parallel workers (default: 1)')
    args = parser.parse_args()

    try:
        check_dependencies(args.model)
    except RuntimeError as e:
        print(f"Error: {e}")
        return

    os.makedirs(args.output_dir, exist_ok=True)

    try:
        mp4_files = [f for f in os.listdir(args.videos_dir) if f.endswith('.mp4')]
    except FileNotFoundError:
        print(f"Error: Videos directory '{args.videos_dir}' not found.")
        return

    if not mp4_files:
        print(f"No .mp4 files found in '{args.videos_dir}'. Nothing to do.")
        return

    print(f"Found {len(mp4_files)} video(s) to process.")

    tmp_dir = tempfile.mkdtemp(prefix='pipeline_tmp_')
    wall_start = time.time()
    results = []

    try:
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(
                    process_video, f, args.videos_dir, tmp_dir,
                    args.output_dir, args.model, args.fps, args.scale
                ): f for f in mp4_files
            }
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
    finally:
        try:
            shutil.rmtree(tmp_dir)
        except Exception as e:
            print(f"Warning: failed to clean up temp dir '{tmp_dir}': {e}")

    wall_end = time.time()
    succeeded = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]

    print(f"\n{'='*50}")
    print(f"Complete. {len(succeeded)}/{len(results)} succeeded in {wall_end-wall_start:.1f}s")
    if failed:
        print("Failed files:")
        for name, _, reason in failed:
            print(f"  - {name}: {reason}")


if __name__ == '__main__':
    main()
