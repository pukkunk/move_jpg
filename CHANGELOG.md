# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [v0.1.9] - 2025-08-08
### Changed
- `README.md`: 
  - Fixed to be able to switch between Japanese and English.
- `tests/test_move_jpg.py`: 
  - Added "interpolation=None" to the configparser options. Fixed to not perform interpolation.
- `move_jpg.py`: 
  - Corrected the version number.
### Added
- `README.ja.md`: 

## [v0.1.8] - 2025-07-31
### Changed
- `move_jpg.py`: 
  - Stopped managing versions with the "VERSION" file and corrected it to the original description.
  - Create short version information.

## [v0.1.7] - 2025-07-31
### Changed
- `move_jpg.py`: 
  - Fixed to display version information for libraries with dependencies when option -v is used.
  - Modified move_jpg.py to include the version information in the "VERSION" file.
- `README.md`: 
  - Added version information of dependent libraries for the environment used in the test.
- `make_exe_py.bat`: 
  - Modified .bat to use the file "VERSION" as version information.
- `make_exe_py.sh`: 
  - Modified .sh to use the file "VERSION" as version information.
### Added
- `VERSION`: 

## [v0.1.6] - 2025-07-23
###Fixed
- `tests/download_ffmpeg.py`: 
  - Fixed a bug in the download folder.
### Changed
- `move_jpg.py`: 
  - Removed unnecessary duplicate piexif import.
- `README.md`: 
  - Modified step 1 command of "Check operation with pytest".
### Added
- `requirements.txt`: 
- `tests/requirements.txt`: 

## [v0.1.5] - 2025-07-22
### Changed
- `move_jpg.py`: 
  - Fixed to allow ffprobe to be downloaded on Windows and Linux (Ubuntu).
  - Added the notation "raw" to the regular expression description of def movie_get_date().
- `tests/download_ffmpeg.py`: 
  - Fixed to allow ffmpeg to be downloaded on Windows and Linux (Ubuntu).
- `README.md`: 
  - Added WSL2 Ubuntu-24.04 LTS to 'Tested Environments'.

## [v0.1.4] - 2025-07-19
### Changed
- `move_jpg.py`: 
  - Added the extension '.cr3' to movie_ext.
  - Added the extensions '.nef' and '.arw' to raw_ext.
  - Fixed the process of adding the current folder to the environment variables so that it is not performed multiple times.
- `tests/test_move_jpg.py`: 
  - def test_no_argument(): Added
- `README.md`: 
  - Added 'Tested Environments'.
  - Added extension information to move_jpg.ini.

## [v0.1.3] - 2025-07-15
### Changed
- `move_jpg.py`: 
  - Fixed so that it can be executed from a test script for pytest.
### Added
- `pytest.ini`: 
- `tests/__init__.py`: 
- `tests/download_ffmpeg.py`: 
- `tests/test_move_jpg.py`: 
- `tests/test_utils.py`: 

## [v0.1.2] - 2025-07-11
### Changed
- `move_jpg.py`: 
  - Modified to support HCIE format image files.

## [v0.1.1] - 2025-07-10
### Changed
- `move_jpg.py`: 
  - Delete ".png" from the extension information of "picture_ext".
  - Changed type dict to Dict.
  - Delete check_version().

## [v0.1.0] - 2025-06-19
### Added
- Initial commit for public release
