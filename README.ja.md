# move_jpg.py

English version → [README.md](README.md)

さまざまな形式の画像ファイルや動画ファイルを自動的に移動・整理するためのシンプルなPythonユーティリティです。

画像・動画ファイルから日付情報を取得し、日付ごとのフォルダに整理します。

1. 対象フォルダ内の画像・動画ファイル情報を取得します。
2. ファイルのExif情報や動画のメタデータなどから日付情報を取得します。
3. 日付フォルダを作成し、対象ファイルを移動します。

## 動作環境

- Windows 11
- Linux（WSL2 Ubuntuなど）
- Python 3.11以降

Python 3.8および3.10はサポート対象外です。

Python 3.11は2027年10月までセキュリティ修正が予定されています。Pythonのサポート期間を考慮し、今後もサポート対象のPythonバージョンを使用してください。

参考：[Python Developer's Guide - Status of Python versions](https://devguide.python.org/versions/)

## 機能

以下の情報を設定ファイルから取得して処理を行います。

- 静止画ファイルの拡張子
- 動画ファイルの拡張子
- RAWファイルの拡張子
- Mtime（日付）情報で処理するファイルの拡張子
- HEIC形式の画像ファイル
- ffmpegのダウンロードURL
- 日付のフォーマット
- 対象フォルダ

## インストール方法

### 1. 通常のPythonスクリプトとして使用する場合

Python 3.11以降をインストールしてください。

プロジェクトフォルダで依存ライブラリをインストールします。

```cmd
uv sync
```

または、必要なライブラリを個別にインストールしてください。

```cmd
pip install piexif pillow-heif ini_cfg_parser Pillow ffmpeg-python numpy
```

実行方法：

```cmd
python move_jpg.py
```

uvを使用して実行する場合：

```cmd
uv run move_jpg.py
```

### 2. uv tool installでインストールする場合

`uv tool install` を使用すると、専用のPython環境にプログラムと依存ライブラリがインストールされ、コマンドとして実行できるようになります。

#### uvのインストール

uvは、Pythonのパッケージや実行環境を管理するツールです。

uvをまだインストールしていない場合は、WindowsのコマンドプロンプトまたはPowerShellで、以下のコマンドを実行してください。

```cmd
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

インストール後、コマンドプロンプトを再起動し、以下のコマンドでインストールを確認します。

```cmd
uv --version
```

その他のOSやインストール方法については、[uv公式インストールガイド](https://docs.astral.sh/uv/getting-started/installation/)を参照してください。

#### move_jpgのインストール

`pyproject.toml` があるプロジェクトフォルダに移動し、以下を実行します。

```cmd
uv tool install .
```

インストールが完了すると、Windowsでは通常、次のフォルダに move_jpg.exe が配置されます。

```TEXT
%USERPROFILE%\.local\bin\move_jpg.exe
```

カレントフォルダに作成されるわけではありません。

**PATHに関する警告が表示された場合**

インストール時に、次のような警告が表示される場合があります。

```cmd
warning: `C:\Users\ユーザー名\.local\bin` is n
ot on your PATH.
To use installed tools, run `$env:PATH = "C:\Users\ユーザー名\.local\bin;$env:PATH"` or `uv tool update-shell`.
```

これは、インストール先のフォルダがPATHに登録されていないことを示しています。

次のコマンドをPowerShellで実行してください。

```cmd
uv tool update-shell
```

実行後、ターミナルを再起動してください。

それでもPATHが反映されない場合は、Windowsの環境変数PATHに次のフォルダを追加してください。

```TEXT
%USERPROFILE%\.local\bin
```

※ move_jpg(exeファイル) は、Python本体を含む単独実行ファイルではありません。uvが管理するPython環境でアプリケーションを起動するためのコマンドランチャーです。

実行方法：

```cmd
move_jpg
```

バージョン確認：

```cmd
move_jpg --version
```

**補足**

`uv tool install .` で作成される `move_jpg`(exeファイル) は、PyInstallerなどでPython本体を含めて単独実行可能なファイルにしたものではありません。

uvが専用環境にインストールしたPythonプログラムを起動するためのコマンドランチャーです。実行にはuvが管理するPython環境を使用します。

## 使用方法

### 基本的な実行

実行時のカレントフォルダを対象にする場合は、以下のように実行します。

```cmd
python move_jpg.py
```

または

```cmd
move_jpg
```

### 対象フォルダを指定する場合

`-t` オプションで対象フォルダを指定できます。

```cmd
move_jpg -t D:\PHOTO
```

通常のPython実行でも同じオプションを使用できます。

```cmd
python move_jpg.py -t D:\PHOTO
```

`-t` を指定した場合は、INIファイルの `tar_folder` の設定よりもコマンドラインの指定が優先されます。

## 設定ファイル（move_jpg.ini）

設定ファイルは `move_jpg.ini` です。

初回実行時に設定ファイルが存在しない場合は、初期設定のINIファイルが作成されます。

### INIファイルの初期設定

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

### 設定項目

| 設定項目 | 説明 |
| --- | --- |
| picture_ext | 静止画ファイルの拡張子 |
| movie_ext | 動画ファイルの拡張子 |
| raw_ext | RAWファイルの拡張子 |
| mtime_ext | Mtime（日付）情報で処理するファイルの拡張子 |
| heic_ext | HEIC形式画像の拡張子 |
| url_ffmpeg | ffmpegのダウンロードURL |
| date_format | 日付フォルダのフォーマット |
| tar_folder | 対象フォルダ |

`ffprob` が存在しない場合、`url_ffmpeg` に指定したURLから取得します。

### INIファイルの配置場所

INIファイルは、実行時のカレントフォルダを基準に使用します。

- `-t` を指定した場合：指定したフォルダ内の `move_jpg.ini`
- `-t` を省略した場合：カレントフォルダ内の `move_jpg.ini`

INIファイルが存在しない場合は、該当フォルダに初期設定のINIファイルを作成します。

### 対象フォルダ（tar_folder）の指定

`-t` を指定しない場合は、INIファイルの `tar_folder` の設定を使用します。

`-t` を指定した場合は、INIファイルの `tar_folder` は使用せず、コマンドラインで指定したフォルダを対象にします。

`tar_folder = .` は、実行時のカレントフォルダを意味します。

### 相対パスと絶対パス

`-t` とINIファイルの `tar_folder` は、どちらも相対パスと絶対パスを指定できます。

相対パスは、実行時のカレントフォルダを基準に解決します。

**相対パスの例**

```ini
tar_folder = .
tar_folder = .\PHOTO
tar_folder = ..\PHOTO
```

**絶対パスの例**

```ini
tar_folder = D:\PHOTO
tar_folder = D:\PHOTO\..\xxx
```

絶対パスの中に `..` が含まれていても、絶対パスとして扱います。

## 動作確認済み環境

| OS | Python Version |
| --- | ---: |
| Windows 11 Pro (64-bit) | 3.11 |
| WSL2 Ubuntu-24.04 LTS | 3.12 |

## 依存ライブラリ

以下のライブラリを使用しています。

- piexif
- pillow-heif
- ini_cfg_parser
- Pillow
- ffmpeg-python
- numpy

uvを使用する場合は、`pyproject.toml` に定義された依存ライブラリがインストールされます。

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

### メタデータ取得に関する注意点

Canon EOS R5の `.CR3` ファイルは、MP4ベースのコンテナ形式（ISO Base Media File Format）です。

この形式に対応するには、`movie_ext` に `.cr3` を含める必要があります。

## pytestによる動作確認

### step1: ffmpegとffprobeの準備

以下を実行して、テスト用のffmpegとffprobeを準備してください。

```cmd
python tests\download_ffmpeg.py
```

### step2: テストの実行

通常のpytest：

```cmd
pytest -v -s
```

uv経由のpytest：

```cmd
uv run pytest -v -s
```

## License

MIT License

## Author

pukkunk
