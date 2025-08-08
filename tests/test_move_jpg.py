import os
import sys
import pathlib
import pytest
import shutil
from pathlib import Path
import urllib.request
import zipfile
import configparser
from tests import test_utils
import move_jpg  # target script
from unittest import mock  # 追加

SCR_PATH = os.path.abspath(__file__)
SCR_FOLDER = os.path.dirname(SCR_PATH)

def set_ini_value(ini_file: str, section: str, key: str, val: str):
    ini_path = Path(ini_file)
    config = configparser.ConfigParser(interpolation=None)

    if ini_path.exists():
        config.read(ini_file, encoding="shiftjis")

    # If the section does not exist, add it.
    if not config.has_section(section):
        config.add_section(section)

    # set value
    config.set(section, key, val)

    # save file
    with ini_path.open("w", encoding="shiftjis") as f:
        config.write(f)

def add_tardir_envpath(dirname: str) -> None :
    # Get the current PATH environment variable
    current_path = os.environ.get("PATH", "")

    # Add SCR_FOLDER to the beginning of the environment variable PATH.
    if dirname not in current_path:
        os.environ["PATH"] = dirname + os.pathsep + current_path

## @fn          is_ffprobe()
#  @brief       Check that ffprobe is on your path.
#  @param[in]   None            : None
#  @retval      bool            : result value [type bool]
def is_ffprobe() -> bool:
    # Check that ffprobe is on your path.
    tool_path = shutil.which("ffprobe")
    if not tool_path:
        return False
    else:
        return True

## @fn          is_ffmpeg()
#  @brief       Check that ffmpeg is on your path.
#  @param[in]   None            : None
#  @retval      bool            : result value [type bool]
def is_ffmpeg() -> bool:
    # Check that ffmpeg is on your path.
    tool_path = shutil.which("ffmpeg")
    if not tool_path:
        return False
    else:
        return True

# Hook function for displaying progress
def progress_hook(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size)
    percent = min(100, percent)
    bar = f"[{'=' * (percent // 2):50}]"
    print(f"\rDownloading {bar} {percent}% complete", end='')
    sys.stdout.flush()

def download_and_extract_ffprobe(zip_url: str, extract_path: str) -> bool:
    enb_ffprobe = True
    enb_ffmpeg = True
    if not (enb_ffprobe or enb_ffmpeg):
        print("download is disabled.")
        return True

    targets = []
    if enb_ffprobe:
        targets.append("ffprobe.exe")
    if enb_ffmpeg:
        targets.append("ffmpeg.exe")

    target_list_str = " and ".join(targets)
    print(f"{target_list_str} not found. downloading")
    #user_input = input(f"{target_list_str} not found. Would you like to download it? [y/N]: ").strip().lower()
    #if user_input != "y":
    #    print("Canceled download.")
    #    return False

    suffix = pathlib.Path(zip_url).suffix.lower()
    if suffix not in ['.zip', '.7z']:
        print(f"Unsupported archive type: {suffix}")
        return False

    zip_path = os.path.join(extract_path, f"ffmpeg{suffix}")

    proxy_dict = {}
    if os.environ.get("HTTP_PROXY"):
        proxy_dict["http"] = os.environ["HTTP_PROXY"]
    if os.environ.get("HTTPS_PROXY"):
        proxy_dict["https"] = os.environ["HTTPS_PROXY"]
    if proxy_dict:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxy_dict))
        urllib.request.install_opener(opener)

    try:
        urllib.request.urlretrieve(zip_url, zip_path, reporthook=progress_hook)
        print("\nDownload complete:", zip_path)
    except Exception as e:
        print(f"Failed to download {target_list_str}:", e)
        return False

    # Extract
    try:
        print("Extraction of the archive has started.")
        root_dir = None
        all_names = []

        if suffix == '.zip':
            with zipfile.ZipFile(zip_path, 'r') as archive:
                all_names = archive.namelist()
                root_dir = all_names[0].split('/')[0] if all_names else None
                archive.extractall(extract_path)

        #elif suffix == '.7z':
        #    with py7zr.SevenZipFile(zip_path, mode='r') as archive:
        #        archive.extractall(path=extract_path)
        #        all_names = archive.getnames()
        #        root_dir = os.path.commonpath(all_names) if all_names else None

        for exe_name in targets:
            match = [f for f in all_names if f.endswith(exe_name)]
            if match:
                extracted_path = os.path.join(extract_path, match[0])
                target_path = os.path.join(extract_path, exe_name)
                shutil.move(extracted_path, target_path)
                print(f"Extraction complete: {target_path}")
            else:
                print(f"{exe_name} not found in the archive.")
                return False
    except Exception as e:
        print("Failed to extract the archive:", e)
        return False

    finally:
        try:
            if os.path.exists(zip_path):
                os.remove(zip_path)
            if root_dir:
                root_dir_path = os.path.join(extract_path, root_dir)
                if os.path.exists(root_dir_path):
                    shutil.rmtree(root_dir_path)
                    print(f"Removed extracted folder: {root_dir_path}")
        except Exception as e:
            print(f"Cleanup error: {e}")
            return False

    return True

@pytest.fixture(scope="session", autouse=True)
def setup_ffmpeg():
    extract_path = os.path.abspath(os.path.join(SCR_FOLDER, "../"))
    add_tardir_envpath(extract_path)
    if not (is_ffmpeg() and is_ffprobe()):
        url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
        res_flag = download_and_extract_ffprobe(url, extract_path=extract_path)

@pytest.fixture(scope="function")
def setup_test_files():
    """
    A fixture that uses create_test_files() in test_utils.py 
    to create test files in ../test_dir under SCR_FOLDER and 
    automatically deletes them after the tests are completed.
    """
    path_str = os.path.abspath(os.path.join(SCR_FOLDER, "../test_dir"))
    if os.path.exists(path_str):
        shutil.rmtree(path_str)

    test_dir = pathlib.Path(path_str)
    test_dir.mkdir(exist_ok=True)

    # Create a file by passing the output path to create_test_files()
    # Example: test_utils.create_test_files(output_dir: Path)
    test_utils.create_test_files(test_dir)

    yield test_dir

    #if test_dir.exists():
    #    shutil.rmtree(test_dir)

def test_move_files_by_date(setup_test_files):
    """
    Test the file move process of move_jpg.py
    """
    enb_delete_folder = True
    test_dir = setup_test_files

    for i in range(1, 6):
        file_path = test_dir / f"ammonite_{i:03}.jpg"
        assert file_path.exists(), f"{file_path.name} should be created"
    png_file = test_dir / "ammonite_007.png"
    assert png_file.exists(), "PNG file should be created"
    for i in range(8, 10):
        file_path = test_dir / f"ammonite_{i:03}.tif"
        assert file_path.exists(), f"{file_path.name} should be created"
    for i in range(1, 2):
        file_path = test_dir / f"sample_{i:03}.jpg"
        assert file_path.exists(), f"{file_path.name} should be created"

    # Since main() in move_jpg.py checks sys.argv, replace it only during testing.
    move_jpg_path = os.path.abspath('move_jpg.py')
    test_args = [move_jpg_path, "-t", str(test_dir)]

    with mock.patch.object(sys, 'argv', test_args):
        # Mock input() to always return "y"
        with mock.patch('builtins.input', return_value='y'):
            with pytest.raises(SystemExit) as exc_info:
                move_jpg.main()
            assert exc_info.type == SystemExit
            assert exc_info.value.code == 0

    # Check the result of the move
    for i in range(1, 6):
        file_path = test_dir / f"ammonite_{i:03}.jpg"
        assert not file_path.exists(), f"{file_path.name} should have been moved and must not exist"
    png_file = test_dir / "ammonite_007.png"
    assert png_file.exists(), "PNG file should not have been moved"
    for i in range(8, 10):
        file_path = test_dir / f"ammonite_{i:03}.tif"
        assert not file_path.exists(), f"{file_path.name} should have been moved and must not exist"

    for i in range(1, 2):
        file_path = test_dir / f"sample_{i:03}.jpg"
        assert not file_path.exists(), f"{file_path.name} should have been moved and must not exist"

    if(enb_delete_folder):
        if test_dir.exists():
            shutil.rmtree(test_dir)

def test_move_png(setup_test_files):
    """
    Test the file move process of move_jpg.py
    """
    enb_delete_folder = True
    test_dir = setup_test_files

    for i in range(1, 6):
        file_path = test_dir / f"ammonite_{i:03}.jpg"
        assert file_path.exists(), f"{file_path.name} should be created"
    png_file = test_dir / "ammonite_007.png"
    assert png_file.exists(), "PNG file should be created"
    for i in range(8, 10):
        file_path = test_dir / f"ammonite_{i:03}.tif"
        assert file_path.exists(), f"{file_path.name} should be created"
    for i in range(1, 2):
        file_path = test_dir / f"sample_{i:03}.jpg"
        assert file_path.exists(), f"{file_path.name} should be created"

    ini_file = os.path.abspath(os.path.join(SCR_FOLDER, "../move_jpg.ini"))
    section = 'move_jpg'
    key = 'mtime_ext'
    val = '.mts,.png'
    set_ini_value(ini_file, section, key, val)
    # Since main() in move_jpg.py checks sys.argv, replace it only during testing.
    move_jpg_path = os.path.abspath('move_jpg.py')
    test_args = [move_jpg_path, "-t", str(test_dir)]

    with mock.patch.object(sys, 'argv', test_args):
        # Mock input() to always return "y"
        with mock.patch('builtins.input', return_value='y'):
            with pytest.raises(SystemExit) as exc_info:
                move_jpg.main()
            assert exc_info.type == SystemExit
            assert exc_info.value.code == 0

    # Check the result of the move
    for i in range(1, 6):
        file_path = test_dir / f"ammonite_{i:03}.jpg"
        assert not file_path.exists(), f"{file_path.name} should have been moved and must not exist"
    png_file = test_dir / "ammonite_007.png"
    assert not png_file.exists(), "PNG file should have been moved and must not exist"
    for i in range(8, 10):
        file_path = test_dir / f"ammonite_{i:03}.tif"
        assert not file_path.exists(), f"{file_path.name} should have been moved and must not exist"

    for i in range(1, 2):
        file_path = test_dir / f"sample_{i:03}.jpg"
        assert not file_path.exists(), f"{file_path.name} should have been moved and must not exist"

    section = 'move_jpg'
    key = 'mtime_ext'
    val = '.mts'
    set_ini_value(ini_file, section, key, val)

    if(enb_delete_folder):
        if test_dir.exists():
            shutil.rmtree(test_dir)

def test_no_argument(setup_test_files):
    """
    Test the file move process of move_jpg.py
    """
    enb_delete_folder = True
    test_dir = setup_test_files

    for i in range(1, 6):
        file_path = test_dir / f"ammonite_{i:03}.jpg"
        assert file_path.exists(), f"{file_path.name} should be created"
    png_file = test_dir / "ammonite_007.png"
    assert png_file.exists(), "PNG file should be created"
    for i in range(8, 10):
        file_path = test_dir / f"ammonite_{i:03}.tif"
        assert file_path.exists(), f"{file_path.name} should be created"
    for i in range(1, 2):
        file_path = test_dir / f"sample_{i:03}.jpg"
        assert file_path.exists(), f"{file_path.name} should be created"

    ini_file = os.path.abspath(os.path.join(SCR_FOLDER, "../move_jpg.ini"))
    section = 'move_jpg'
    key = 'tar_folder'
    val = './test_dir'
    set_ini_value(ini_file, section, key, val)

    # Since main() in move_jpg.py checks sys.argv, replace it only during testing.
    move_jpg_path = os.path.abspath('move_jpg.py')
    test_args = [move_jpg_path]

    with mock.patch.object(sys, 'argv', test_args):
        # Mock input() to always return "y"
        with mock.patch('builtins.input', return_value='y'):
            with pytest.raises(SystemExit) as exc_info:
                move_jpg.main()
            assert exc_info.type == SystemExit
            assert exc_info.value.code == 0

    # Check the result of the move
    for i in range(1, 6):
        file_path = test_dir / f"ammonite_{i:03}.jpg"
        assert not file_path.exists(), f"{file_path.name} should have been moved and must not exist"
    png_file = test_dir / "ammonite_007.png"
    assert png_file.exists(), "PNG file should not have been moved"
    for i in range(8, 10):
        file_path = test_dir / f"ammonite_{i:03}.tif"
        assert not file_path.exists(), f"{file_path.name} should have been moved and must not exist"

    for i in range(1, 2):
        file_path = test_dir / f"sample_{i:03}.jpg"
        assert not file_path.exists(), f"{file_path.name} should have been moved and must not exist"

    section = 'move_jpg'
    key = 'tar_folder'
    val = '.'
    set_ini_value(ini_file, section, key, val)

    if(enb_delete_folder):
        if test_dir.exists():
            shutil.rmtree(test_dir)

def test_move_files_by_date_fmt_yyyymmdd(setup_test_files):
    """
    Test the file move process of move_jpg.py
    """
    enb_delete_folder = False
    test_dir = setup_test_files

    ini_file = os.path.abspath(os.path.join(SCR_FOLDER, "../move_jpg.ini"))
    section = 'move_jpg'
    key = 'date_format'
    val = r'%Y%m%d'
    set_ini_value(ini_file, section, key, val)

    for i in range(1, 6):
        file_path = test_dir / f"ammonite_{i:03}.jpg"
        assert file_path.exists(), f"{file_path.name} should be created"
    png_file = test_dir / "ammonite_007.png"
    assert png_file.exists(), "PNG file should be created"
    for i in range(8, 10):
        file_path = test_dir / f"ammonite_{i:03}.tif"
        assert file_path.exists(), f"{file_path.name} should be created"
    for i in range(1, 2):
        file_path = test_dir / f"sample_{i:03}.jpg"
        assert file_path.exists(), f"{file_path.name} should be created"

    # Since main() in move_jpg.py checks sys.argv, replace it only during testing.
    move_jpg_path = os.path.abspath('move_jpg.py')
    test_args = [move_jpg_path, "-t", str(test_dir)]

    with mock.patch.object(sys, 'argv', test_args):
        # Mock input() to always return "y"
        with mock.patch('builtins.input', return_value='y'):
            with pytest.raises(SystemExit) as exc_info:
                move_jpg.main()
            assert exc_info.type == SystemExit
            assert exc_info.value.code == 0

    # Check the result of the move
    for i in range(1, 6):
        file_path = test_dir / f"ammonite_{i:03}.jpg"
        assert not file_path.exists(), f"{file_path.name} should have been moved and must not exist"
    png_file = test_dir / "ammonite_007.png"
    assert png_file.exists(), "PNG file should not have been moved"
    for i in range(8, 10):
        file_path = test_dir / f"ammonite_{i:03}.tif"
        assert not file_path.exists(), f"{file_path.name} should have been moved and must not exist"

    for i in range(1, 2):
        file_path = test_dir / f"sample_{i:03}.jpg"
        assert not file_path.exists(), f"{file_path.name} should have been moved and must not exist"

    section = 'move_jpg'
    key = 'date_format'
    val = '%Y_%m_%d'
    set_ini_value(ini_file, section, key, val)

    if(enb_delete_folder):
        if test_dir.exists():
            shutil.rmtree(test_dir)

