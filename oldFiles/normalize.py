import subprocess
import shutil
import os


def get_fps(path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
         '-show_entries', 'stream=r_frame_rate', '-of', 'csv=p=0', path],
        capture_output=True, text=True
    )
    num, den = result.stdout.strip().split('/')
    return int(num) / int(den)


def main():
    FPS = 60
    os.makedirs('normalized_videos', exist_ok=True)

    if not shutil.which('ffmpeg'):
        print("Error: ffmpeg not found. Install it with: brew install ffmpeg")
        return

    for file in os.listdir('videos'):
        if not file.endswith('.mp4'):
            continue

        src = os.path.join('videos', file)
        dst = os.path.join('normalized_videos', file)
        orig_fps = get_fps(src)

        print(f"{file}: {orig_fps:.2f} -> {FPS} fps ... ", end='', flush=True)

        if abs(orig_fps - FPS) <= 0.01:
            shutil.copy2(src, dst)
            print("already at target, copied.")
            continue

        # minterpolate synthesizes real in-between frames via motion estimation
        subprocess.run([
            'ffmpeg', '-y', '-i', src,
            '-filter:v', f'minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-an',
            dst
        ], check=True, capture_output=True)
        print("done.")


if __name__ == "__main__":
    main()