if not exist venv (
    python -m venv venv
)
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.spec del *.spec
call venv\Scripts\activate.bat
python.exe -m pip install --upgrade pip
pip install ini-cfg-parser --no-binary :all:
pip install pyinstaller --no-binary :all:
pip install Pillow --only-binary :all:
pip install piexif --only-binary :all:
pip install ffmpeg-python --only-binary :all:
pip install packaging --only-binary :all:
pyinstaller move_jpg.py --onefile --hidden-import=PIL._imaging --hidden-import=PIL.Image --hidden-import=PIL.ExifTags --hidden-import=piexif --hidden-import=ffmpeg --hidden-import=ffmpeg._run --hidden-import=ffmpeg._probe
