import argparse
import concurrent.futures
import os
import shutil
import subprocess
import time


def check_dependencies():
    if not shutil.which('ffmpeg'):
        raise RuntimeError("ffmpeg not found. Install with: brew install ffmpeg")
    if not shutil.which('ffprobe'):
        raise RuntimeError("ffprobe not found. Install with: brew install ffmpeg")



def process_video(filename, videos_dir, final_dir, target_fps):
    src = os.path.join(videos_dir, filename)
    dst = os.path.join(final_dir, filename)

    print(f"\n[{filename}] Starting...")

    try:
        t0 = time.time()

        subprocess.run([
            'ffmpeg', '-y', '-i', src,
            '-vf', f'scale=1280:720,fps={target_fps}',
            '-c:v', 'libx264',
            '-preset', 'fast',   # KEY CHANGE (speed)
            '-crf', '23',        # slightly lower quality but much faster
            '-an',
            dst
        ], check=True, capture_output=True)
        t1 = time.time()
        print(f"[{filename}] Done in {t1-t0:.1f}s → {dst}")
        return filename, True, None

    except Exception as e:
        print(f"[{filename}] FAILED — {e}")
        return filename, False, str(e)


def main():
    parser = argparse.ArgumentParser(description="Normalize video FPS to 60 and resolution to 720p.")
    parser.add_argument('--videos-dir', default='videos', help='Input directory (default: videos)')
    parser.add_argument('--output-dir', default='final_videos', help='Output directory (default: final_videos)')
    parser.add_argument('--fps', type=int, default=60, help='Target FPS (default: 60)')
    parser.add_argument('--workers', type=int, default=1, help='Parallel workers (default: 1)')
    args = parser.parse_args()

    try:
        check_dependencies()
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

    wall_start = time.time()
    results = []

    try:
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(process_video, f, args.videos_dir, args.output_dir, args.fps): 
                f for f in mp4_files
            }
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
    except Exception as e:
        print(f"Error during processing: {e}")

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
