# move_jpg.py

日本語版 → [README.ja.md](README.ja.md)

A simple Python utility for automatically moving and organizing image and video files in various formats.

It extracts date information from image and video files and organizes them into folders by date.

1. Retrieves information about image and video files in the target folder.
2. Extracts date information from EXIF data, video metadata, and other sources.
3. Creates date-based folders and moves the target files into them.

## Requirements

- Windows 11
- Linux (such as WSL2 Ubuntu)
- Python 3.11 or later

Python 3.8 and 3.10 are no longer supported.

Python 3.11 is scheduled to receive security updates until October 2027. Please use a Python version that is still supported, taking the Python support lifecycle into consideration.

Reference: [Python Developer's Guide - Status of Python versions](https://devguide.python.org/versions/)

## Features

The application reads the following settings from the configuration file:

- Static image file extensions
- Video file extensions
- RAW image file extensions
- File extensions to be processed using Mtime (file modification date) information
- HEIC image file extension
- ffmpeg download URL
- Date folder format
- Target folder

## Installation

### 1. Using as a regular Python script

Install Python 3.11 or later.

Install the required libraries in the project folder:

```cmd
uv sync
```

Alternatively, install the required libraries individually:

```cmd
pip install piexif pillow-heif ini_cfg_parser Pillow ffmpeg-python numpy
```

Run the script:

```cmd
python move_jpg.py
```

To run it using uv:

```cmd
uv run move_jpg.py
```

### 2. Installing with uv tool install

Using `uv tool install` installs the application and its dependencies in an isolated Python environment and makes it available as a command.

#### Installing uv

If uv is not installed, follow the official installation guide:

https://docs.astral.sh/uv/getting-started/installation/

#### Installing move_jpg

Navigate to the project folder containing `pyproject.toml` and run:

```cmd
uv tool install .
```

After installation, `move_jpg.exe` is normally placed in the following directory on Windows:

```text
%USERPROFILE%\.local\bin\move_jpg.exe
```

**It is not created in the current folder.**

If this directory is included in your PATH environment variable, you can run the command from any folder.

**If a PATH warning is displayed**

During installation, you may see a warning similar to the following:

```text
warning: `C:\Users\YourUserName\.local\bin` is not on your PATH.
To use installed tools, run `$env:PATH = "C:\Users\YourUserName\.local\bin;$env:PATH"` or `uv tool update-shell`.
```

This means that the installation directory is not included in your PATH environment variable.

Run the following command in PowerShell:

```powershell
uv tool update-shell
```

Then restart your terminal.

If the PATH setting is still not updated, add the following directory to the Windows PATH environment variable:

```text
%USERPROFILE%\.local\bin
```

**Note:** `move_jpg`(exe file) is not a standalone executable that includes the Python runtime. It is a command launcher that starts the application using the Python environment managed by uv.

Run the application:

```cmd
move_jpg
```

Check the version:

```cmd
move_jpg --version
```

**Additional information**

The `move_jpg` created by `uv tool install .` is not a standalone executable bundled with Python, such as one created by PyInstaller.

It is a command launcher that starts the Python application installed in an isolated environment managed by uv. The application runs using that environment.

## Usage

### Basic execution

To process the current working directory, run:

```cmd
python move_jpg.py
```

Or:

```cmd
move_jpg
```

### Specifying the target folder

You can specify the target folder using the `-t` option:

```cmd
move_jpg -t D:\PHOTO
```

The same option can be used when running the regular Python script:

```cmd
python move_jpg.py -t D:\PHOTO
```

When `-t` is specified, the command-line folder takes precedence over the `tar_folder` setting in the INI file.

## Configuration File (move_jpg.ini)

The configuration file is named `move_jpg.ini`.

If the configuration file does not exist when the application is first run, an INI file with the default settings is created.

### Default INI settings

```ini
[move_jpg]
picture_ext = .jpg,.jpeg,.tif
movie_ext = .mp4,.mov,.cr3
raw_ext = .orf,.nef,.arw
mtime_ext = .mts
heic_ext = .heic
url_ffmpeg = https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
date_format = %Y_%m_%d
tar_folder = .
```

### Configuration options

| Setting | Description |
| --- | --- |
| picture_ext | Static image file extensions |
| movie_ext | Video file extensions |
| raw_ext | RAW image file extensions |
| mtime_ext | File extensions to be processed using Mtime (file modification date) information |
| heic_ext | HEIC image file extension |
| url_ffmpeg | URL used to download ffmpeg |
| date_format | Date folder format |
| tar_folder | Target folder |

If `ffprobe` does not exist, it is downloaded from the URL specified by `url_ffmpeg`.

### INI file location

The INI file is located relative to the current working directory at the time of execution.

- When `-t` is specified: `move_jpg.ini` in the specified target folder.
- When `-t` is omitted: `move_jpg.ini` in the current working directory.

If the INI file does not exist, a default INI file is created in the corresponding folder.

### Specifying the target folder (`tar_folder`)

When `-t` is not specified, the application uses the `tar_folder` setting in the INI file.

When `-t` is specified, the application ignores the `tar_folder` setting and uses the folder specified on the command line.

`tar_folder = .` means the current working directory.

### Relative and absolute paths

Both `-t` and the INI file's `tar_folder` setting accept relative and absolute paths.

Relative paths are resolved based on the current working directory at the time of execution.

**Examples of relative paths**

```ini
tar_folder = .
tar_folder = .\PHOTO
tar_folder = ..\PHOTO
```

**Examples of absolute paths**

```ini
tar_folder = D:\PHOTO
tar_folder = D:\PHOTO\..\xxx
```

Even if an absolute path contains `..`, it is treated as an absolute path.

## Tested Environments

| OS | Python Version |
| --- | ---: |
| Windows 11 Pro (64-bit) | 3.11 |
| WSL2 Ubuntu-24.04 LTS | 3.12 |

## Dependencies

The application uses the following libraries:

- piexif
- pillow-heif
- ini_cfg_parser
- Pillow
- ffmpeg-python
- numpy

When using uv, the dependencies defined in `pyproject.toml` are installed automatically.

## Tested Image Files

- Canon RAW Files
  - EOS R5 (.CR3)
- Nikon RAW Files
  - NIKON Z9 (.NEF)
- Sony RAW Files
  - Sony a7 IV (.ARW)
- Olympus RAW Files
  - E-M10 Mark II (.ORF)
- OM SYSTEM
  - OM-1 (.ORF)

### Notes on Metadata Extraction

Canon EOS R5 `.CR3` files use an MP4-based container format (ISO Base Media File Format).

To process this format, `.cr3` must be included in the `movie_ext` setting.

## Testing with pytest

### Step 1: Preparing ffmpeg and ffprobe

Run the following command to prepare ffmpeg and ffprobe for testing:

```cmd
python tests\download_ffmpeg.py
```

### Step 2: Running the tests

Using pytest directly:

```cmd
pytest -v -s
```

Using pytest through uv:

```cmd
uv run pytest -v -s
```

## License

MIT License

## Author

pukkunk
