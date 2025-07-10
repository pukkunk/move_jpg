if not exist venv (
    python -m venv venv
)
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.spec del *.spec
call venv\Scripts\activate.bat
python.exe -m pip install --upgrade pip
pip install ini_cfg_parser
pip install pyinstaller
pip install Pillow
pip install piexif
pip install ffmpeg-python
pip install packaging
pyinstaller move_jpg.py --onefile --hidden-import=PIL._imaging --hidden-import=PIL.Image --hidden-import=PIL.ExifTags --hidden-import=piexif --hidden-import=ffmpeg --hidden-import=ffmpeg._run --hidden-import=ffmpeg._probe
