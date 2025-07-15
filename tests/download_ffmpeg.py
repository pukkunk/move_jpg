# tests/download_ffmpeg.py
import os
import sys
import pathlib
import shutil
import urllib.request
import zipfile

SCR_PATH = os.path.abspath(__file__)
SCR_FOLDER = os.path.dirname(SCR_PATH)

def is_ffprobe() -> bool:
    from shutil import which
    return which("ffprobe") is not None

def is_ffmpeg() -> bool:
    from shutil import which
    return which("ffmpeg") is not None

def progress_hook(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size)
    percent = min(100, percent)
    bar = f"[{'=' * (percent // 2):50}]"
    print(f"\rDownloading {bar} {percent}% complete", end='')
    sys.stdout.flush()

def download_and_extract_ffmpeg(zip_url: str, extract_path: str) -> bool:
    targets = ["ffprobe.exe", "ffmpeg.exe"] if os.name == "nt" else ["ffprobe", "ffmpeg"]

    print(f"{', '.join(targets)} not found. Downloading...")

    suffix = pathlib.Path(zip_url).suffix.lower()
    if suffix not in ['.zip']:
        print(f"Unsupported archive type: {suffix}")
        return False

    zip_path = os.path.join(extract_path, f"ffmpeg{suffix}")

    try:
        urllib.request.urlretrieve(zip_url, zip_path, reporthook=progress_hook)
        print("\nDownload complete:", zip_path)
    except Exception as e:
        print(f"Failed to download ffmpeg/ffprobe:", e)
        return False

    try:
        print("Extracting archive...")
        with zipfile.ZipFile(zip_path, 'r') as archive:
            archive.extractall(extract_path)

        # Move executables to extract_path root
        extracted_files = []
        for root, dirs, files in os.walk(extract_path):
            for f in files:
                if f in targets:
                    src = os.path.join(root, f)
                    dst = os.path.join(extract_path, f)
                    if src != dst:
                        shutil.move(src, dst)
                    extracted_files.append(f)

        if set(targets).issubset(extracted_files):
            print("Extraction complete.")
        else:
            print("Warning: Some ffmpeg executables were not found after extraction.")
            return False

    except Exception as e:
        print("Failed to extract the archive:", e)
        return False
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

    return True

def main():
    extract_path = os.path.abspath(os.path.join(SCR_FOLDER, "../"))
    if is_ffmpeg() and is_ffprobe():
        print("ffmpeg and ffprobe already found. No download needed.")
        return

    url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
    success = download_and_extract_ffmpeg(url, extract_path)

    if success:
        print("ffmpeg and ffprobe downloaded successfully.")
    else:
        print("ffmpeg and ffprobe download failed.")

if __name__ == "__main__":
    main()
