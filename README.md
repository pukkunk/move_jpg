# move_jpg.py

This script organizes image files into date folders.
- (1) Get image file information for the target folder.
- (2) Get date information from the image file.
- (3) Create a date folder and move the image files into it.

## function
The following information is obtained from the configuration file and processed:
- (1) Still image file extension
- (2) Video file extension
- (3) Raw file extension
- (4) Mtime information processing file extension
- (5) HCIE format image file.
- (6) ffmepg download URL
- (7) Date format
- (8) Target folder

## Usage

To organize image files in a folder containing a script, use
```python
python move_jpg.py
or
move_jpg.exe
```

Ini setting file (move_jpg.ini)
Initial settings
```cmd
[move_jpg]
picture_ext = .jpg,.jpeg,.tif
movie_ext = .mp4,.mov
raw_ext = .orf
mtime_ext = .mts
heic_ext = .heic
url_ffmpeg = https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
date_format = %Y_%m_%d
tar_folder = .
```

- picture_ext = Still image file extension
- movie_ext = Movie file extension
- raw_ext = Raw file extension
- mtime_ext = Mtime information processing file extension
- heic_ext = The file extension for HCIE format images.
- url_ffmpeg = ffmepg download URL
　If the program file "ffprobe.exe" does not exist, obtain it from the URL.
- date_format = Date format
- tar_folder = Target folder


## license
MIT License

## author
pukkunk
