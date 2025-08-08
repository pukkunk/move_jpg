# move_jpg.py
English version → [README.md](README.md)

このスクリプトは、画像ファイルを日付ごとのフォルダに整理します。
- (1) 対象フォルダ内の画像ファイル情報を取得します  
- (2) 画像ファイルから日付情報を取得します  
- (3) 日付フォルダを作成し、画像ファイルをその中に移動します

## 機能
以下の情報を設定ファイルから取得して処理を行います：
- (1) 静止画ファイルの拡張子  
- (2) 動画ファイルの拡張子  
- (3) RAWファイルの拡張子  
- (4) Mtime（日付）情報で処理するファイルの拡張子  
- (5) HCIE形式の画像ファイル  
- (6) ffmpeg のダウンロードURL  
- (7) 日付のフォーマット  
- (8) 対象フォルダ  

## 使用方法

スクリプトと同じフォルダ内の画像ファイルを整理するには、以下のように実行します(Default設定時)：
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
movie_ext = .mp4,.mov,.cr3
raw_ext = .orf,.nef,.arw
mtime_ext = .mts
heic_ext = .heic
url_ffmpeg = https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
date_format = %Y_%m_%d
tar_folder = .
```

- picture_ext = 静止画ファイルの拡張子  
- movie_ext = 動画ファイルの拡張子  
- raw_ext = RAWファイルの拡張子  
- mtime_ext = Mtime（日付）情報で処理するファイルの拡張子  
- heic_ext = HCIE形式画像の拡張子  
- url_ffmpeg = ffmpeg ダウンロードURL  
    ffprobe.exe が存在しない場合、このURLから取得されます  
- date_format = 日付のフォーマット  
- tar_folder = 対象フォルダ  

## 動作確認済み環境

| OS                    | Python Version   |
|----------------------|-----------------:|
| Windows 11 Pro (64-bit) | 3.8.10 (64-bit) |
| WSL2 Ubuntu-24.04 LTS  | 3.12.3 (64-bit) |

---

## 依存ライブラリのバージョン

### Windows 11 Pro (64-bit)
| Library          | Version  |
|------------------|--------:|
| piexif           | 1.1.3   |
| pillow_heif      | 0.18.0  |
| ini_cfg_parser   | 0.1.7   |
| Pillow           | 10.4.0  |
| ffmpeg-python    | 0.2.0   |
| numpy            | 1.24.4  |

### WSL2 Ubuntu-24.04 LTS
| Library          | Version  |
|------------------|--------:|
| piexif           | 1.1.3   |
| pillow_heif      | 1.0.0   |
| ini_cfg_parser   | 0.1.7   |
| Pillow           | 11.3.0  |
| ffmpeg-python    | 0.2.0   |
| numpy            | 2.3.1   |

## Tested Image Files
  - Canon RAW Files
    - EOS R5 (.CR3)
  - Nikon RAW Files
    - NIKON Z9 (.NEF)
  - Sony RAW Files
    - Sony a7 IV (.ARW)
  - Olympus RAW Files
    - E-M10 Mark II (.ORF)

### メタデータ取得に関する注意点
- Canon EOS R5 の .CR3 ファイルは、MP4ベースのコンテナ形式（ISO Base Media File Format）です。これに対応するには、movie_ext に .cr3 を含める必要があります。

## pytest による動作確認
- step1: ffmpeg と ffprobe をダウンロードするには、以下を実行してください。
```python
python tests\download_ffmpeg.py
```
- step2: テストを実行
```python
pytest
```

## license
MIT License

## author
pukkunk
