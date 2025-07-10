# SPDX-License-Identifier: MIT
# Copyright (c) 2025 pukkun
# coding: utf-8

import argparse,textwrap
import os
import shutil
import sys
import re
import datetime
from pathlib import Path
import urllib.request
import zipfile
import platform
from typing import List, Dict, Tuple, Optional, Any, TypedDict
OK_VAL = 0
NG_VAL = 1
try:
    import ini_cfg_parser as ini
except ImportError as e:
    msg = f"The 'ini_cfg_parser' module is required but not installed.\n"
    msg += f"You can install it with: pip install ini_cfg_parser\n"
    msg += f"Details: {e}"
    print(msg)
    raise SystemExit(NG_VAL)
try:
    from PIL import Image   # type: ignore
    from PIL.ExifTags import TAGS   # type: ignore
except ImportError as e:
    msg = f"The 'PIL' module is required but not installed.\n"
    msg += f"You can install it with: pip install Pillow\n"
    msg += f"Details: {e}"
    print(msg)
    raise SystemExit(NG_VAL)
try:
    import piexif   # type: ignore
except ImportError as e:
    msg = f"The 'piexif' module is required but not installed.\n"
    msg += f"You can install it with: pip install piexif\n"
    msg += f"Details: {e}"
    print(msg)
    raise SystemExit(NG_VAL)
try:
    import ffmpeg# type: ignore
except ImportError as e:
    msg = f"The 'ffmpeg' module is required but not installed.\n"
    msg += f"You can install it with: pip install ffmpeg-python\n"
    msg += f"Details: {e}"
    print(msg)
    raise SystemExit(NG_VAL)
try:
    from packaging import version
except ImportError as e:
    msg = f"The 'packaging' module is required but not installed.\n"
    msg += f"You can install it with: pip install packaging\n"
    msg += f"Details: {e}"
    print(msg)
    raise SystemExit(NG_VAL)

class ExtDict(TypedDict):
    picture_ext: List[str]
    raw_ext: List[str]
    mtime_ext: List[str]
    movie_ext: List[str]

__version__ = f"0.1.1, python={platform.python_version()} {platform.architecture()[0]}"
__copyright__    = 'pukkun'
__author__       = 'pukkun'

SCR_PATH = os.path.abspath(sys.argv[0])
SCR_FOLDER = os.path.dirname(SCR_PATH)

def main() -> None :
    h_word = "Refer to the date information of the image files and move the files to the date folder."
    parser = argparse.ArgumentParser(
        prog=os.path.basename(SCR_PATH),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        version={ver}
        {descpt}
        Copyright :{copyright}
        author :{auth}\
        '''.format(copyright=__copyright__, auth=__author__, ver=__version__,descpt=h_word)))
    parser.add_argument('-v','--version', action='version', version=os.path.basename(SCR_PATH) + " version=" +__version__)
    parser.add_argument('-p','--picture_ext',required=False ,type=str ,nargs='*' , default=None , help="Picture extension")
    parser.add_argument('-t','--tar_folder',required=False ,type=str ,default=None , help="target folder")
    parser.add_argument('-e','--encoding',required=False, default="utf8", choices=['utf8', 'shift_jis', 'euc_jp'], help="encoding char code(default: %(default)s)")

    args = parser.parse_args()
    lst_picture_ext = args.picture_ext
    str_tar_folder = args.tar_folder
    encoding = args.encoding

    opt:Dict[str, Any] = {}
    opt['picture_ext'] = lst_picture_ext
    opt['tar_folder'] = str_tar_folder

    # Get the ini file name.
    ini_file = get_inifile()
    section = os.path.splitext(os.path.basename(SCR_PATH))[0]

    # Set the desired default value with the function get_ini_dict_val()
    default_ini = get_ini_dict_val(section)
    # Check whether the dict variable default_ini for default values ​​is of the expected type.
    if(ini.IniParser.is_valid_ini_dict(default_ini) == False):
        msg = f"def {sys._getframe().f_code.co_name}()\n"
        msg += f"Error detect. The type of the variable default_ini is invalid. type is not 'ini.IniDict'\n"
        msg += f"Check the type of the dict variable default_ini."
        die_print(msg)

    try:
        ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    except ini.IniParserError as e:
        die_print(e)

    # When there is no information for the target key of the variable opt (when the key does not exist or the value of opt[key] is None), the information obtained from the ini file is supplemented.
    for key in default_ini[section].keys():
        # when the key does not exist or the value of opt[key] is None
        if (key not in opt) or (opt[key] is None):
            opt[key] = ini_parser.get(section, key)

    str_ext = ""
    list_ext = []   #Initialization
    # Extend to list "list_ext"
    list_ext.extend(opt['picture_ext'])
    list_ext.extend(opt['movie_ext'])
    list_ext.extend(opt['raw_ext'])
    list_ext.extend(opt['mtime_ext'])
    url_ffmpeg = opt['url_ffmpeg']
    date_format = opt['date_format']
    res_flag = is_valid_date_format(date_format)
    if(res_flag == False):
        msg = "Error detect. Invalid date format found in the configuration file.\nkey='date_format', val={date_format}"
        die_print(msg)

    tar_folder = opt['tar_folder']
    if not os.path.isabs(tar_folder):
        tar_folder = os.path.abspath(os.path.join(SCR_FOLDER, tar_folder))
    if not os.path.isdir(tar_folder):
        msg = f"Error detect. There is not folder. folder={tar_folder}"
        die_print(msg)
    files = []  # Initialization
    for file in os.listdir(tar_folder):
        base, ext = os.path.splitext(file)
        if ext.lower() in list_ext:
            files.append(file)

    dict_tar_ext: ExtDict = {
        'picture_ext': opt['picture_ext'],
        'raw_ext': opt['raw_ext'],
        'mtime_ext': opt['mtime_ext'],
        'movie_ext': opt['movie_ext'],
    }

    print(f"{os.path.basename(SCR_PATH)} version={__version__ }")
    print(f"<<  target  folder:{tar_folder}  >>")
    current_path = os.getcwd()  # Preserve original current directory information
    os.chdir(tar_folder)        # Change to the target directory
    move_picture(files, dict_tar_ext, url_ffmpeg, date_format)
    os.chdir(current_path)      # Change to the original current directory
    sys.exit(OK_VAL)

def move_picture(files: List[str], dict_tar_ext: ExtDict, url_ffmpeg: str, date_format: str):
    picture_ext = dict_tar_ext['picture_ext']
    raw_ext = dict_tar_ext['raw_ext']
    mtime_ext = dict_tar_ext['mtime_ext']
    movie_ext = dict_tar_ext['movie_ext']

    required_keys = ['year', 'month', "day"]
    for file in files:
        print("file=%s" % file)
        base, ext = os.path.splitext(file)
        year = None
        month = None
        day = None
        if(ext.lower() in picture_ext):
            id,value = get_exif(file,"DateTimeOriginal")[0]
            if not (value == None):
                # Extracting date information
                year, month ,day = get_dateinf(value)
            else:
                id,value = get_exif(file,"DateTime")[0]
                #print("id=%s,value=%s" % (id,value))
                if not (value == None):
                    year, month ,day = get_dateinf(value)
                else:
                    year = None
                    month = None
                    day = None
        elif(ext.lower() in raw_ext):
            tag = piexif.ExifIFD.DateTimeOriginal
            erropt = 0
            inf = get_date_info_fm_raw(file, tag, erropt)
            if all(key in inf for key in required_keys):
                year = inf['year']
                month = inf['month']
                day = inf['day']
        elif(ext.lower() in mtime_ext):
            # Get date information.
            inf = file_get_mtime(file)
            if all(key in inf for key in required_keys):
                year = inf['year']
                month = inf['month']
                day = inf['day']
        elif(ext.lower() in movie_ext):
            # Add the script folder to the PATH environment variable.
            add_tardir_envpath(SCR_FOLDER)
            # Get date information.
            inf = movie_get_date(file, url_ffmpeg)
            if all(key in inf for key in required_keys):
                year = inf['year']
                month = inf['month']
                day = inf['day']

        if (year is not None) and (month is not None) and (day is not None):
            # Creating and Changing Directories
            dt = datetime.datetime(int(year), int(month), int(day))  # Explicitly create a datetime object.
            dir_date = dt.strftime(date_format)
            if not os.path.exists(dir_date):
                os.makedirs(dir_date)
            dirname, finebasename = os.path.split(file)
            newdir = os.path.join(dirname , dir_date)
            newfile = os.path.join(newdir ,finebasename)
            # If the file exists, display a warning.
            if(os.path.exists(newfile)):
                print (f"{newfile} already exists.")
            else:
                new_path = shutil.move(file, newdir)
                print(f"{file} is moved. {newdir}")
        else:
            #if(ext.lower()==".jpg") or (ext.lower()==".jpeg"):
            if(ext.lower() in picture_ext):
                print (f"    {file} not exist exif. exif='DateTimeOriginal'.")
            else:
                print (f"    {file} not exist Date information. ")

## @fn          is_valid_date_format()
#  @brief       Checks whether the string indicating the specified format information is valid as strftime of datetime.datetime.
#  @param[in]   fmt             : format string [type str]
#  @retval      bool            : result value [type bool]
def is_valid_date_format(fmt: str) -> bool:
    try:
        # Try out the format using fake dates and times
        datetime.datetime(2000, 1, 1).strftime(fmt)
        return True
    except (ValueError, TypeError):
        return False

## @fn          file_get_ctime()
#  @brief       Get the "ctime" of the target file. The "ctime" is the time when the file's index node (inode) information was last changed.
#  @param[in]   filename        : file file [type str]
#  @retval      exif_data       : file timestamp [type Dict[str, str]]
def file_get_ctime(filename: str) -> Dict[str, str] :
    ctime = os.path.getctime(filename)
    fts = datetime.datetime.fromtimestamp(ctime)
    inf: Dict[str, str] = {}
    inf['year']  = fts.strftime('%Y')
    inf['month'] = fts.strftime('%m')
    inf['day']   = fts.strftime('%d')
    inf['hour']  = fts.strftime('%H')
    inf['min']   = fts.strftime('%M')
    inf['sec']   = fts.strftime('%S')
    return inf

## @fn          file_get_mtime()
#  @brief       Get the "mtime" of the target file. "mtime" = Get the date and time when the file contents were last changed.
#  @param[in]   filename        : file file [type str]
#  @retval      exif_data       : exif info (key,value) [type list]
def file_get_mtime(filename: str) -> Dict[str, str] :
    mtime = os.path.getmtime(filename)
    fts = datetime.datetime.fromtimestamp(mtime)
    inf = {}
    inf['year']  = fts.strftime('%Y')
    inf['month'] = fts.strftime('%m')
    inf['day']   = fts.strftime('%d')
    inf['hour']  = fts.strftime('%H')
    inf['min']   = fts.strftime('%M')
    inf['sec']   = fts.strftime('%S')
    return inf

def add_tardir_envpath(dirname: str) -> None :
    # Get the current PATH environment variable
    current_path = os.environ.get("PATH", "")

    # Add SCR_FOLDER to the beginning of the environment variable PATH.
    if SCR_FOLDER not in current_path:
        os.environ["PATH"] = dirname + os.pathsep + current_path

## @fn          is_ffprobe()
#  @brief       Check that ffprobe is on your path.
#  @param[in]   None            : None
#  @retval      bool            : result value [type bool]
def is_ffprobe() -> bool:
    # Check that ffprobe is on your path.
    ffprobe_path = shutil.which("ffprobe")
    if not ffprobe_path:
        return False
    else:
        return True

# Hook function for displaying progress
def progress_hook(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size)
    percent = min(100, percent)
    bar = f"[{'=' * (percent // 2):50}]"
    print(f"\rDownloading {bar} {percent}% complete", end='')

def download_and_extract_ffprobe(zip_url: str) -> bool:
    user_input = input("ffprobe.exe not found. Would you like to download it? [y/N]: ").strip().lower()
    if user_input != "y":
        print("Canceled download.")
        return False

    print("Start downloading program file...")

    zip_path = "ffmpeg.zip"
    extracted_folder_base = os.path.splitext(zip_path)[0]  # Remove the ".zip" string and get ffmpeg.

    proxy_dict = {}
    if os.environ.get("HTTP_PROXY"):
        proxy_dict["http"] = os.environ["HTTP_PROXY"]
    if os.environ.get("HTTPS_PROXY"):
        proxy_dict["https"] = os.environ["HTTPS_PROXY"]

    if proxy_dict:
        proxy_handler = urllib.request.ProxyHandler(proxy_dict)
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)

    try:
        urllib.request.urlretrieve(zip_url, zip_path, reporthook=progress_hook)
        print("\nDownload complete:", zip_path)
    except Exception as e:
        print("Failed to download ffprobe:", e)
        return False

    try:
        print("Extraction of the zip file has started.")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get the root folder name in the ZIP（example：ffmpeg-7.1.1-essentials_build）
            all_names = zip_ref.namelist()
            root_dir = all_names[0].split('/')[0] if all_names else None

            ffprobe_member = [f for f in all_names if f.endswith("ffprobe.exe")]
            if ffprobe_member:
                print("Extracting ffprobe.exe...")
                zip_ref.extract(ffprobe_member[0], ".")
                extracted_path = os.path.join(".", ffprobe_member[0])
                shutil.move(extracted_path, "ffprobe.exe")
                print("Extraction complete: ffprobe.exe")
            else:
                print("ffprobe.exe not found in the ZIP archive.")
                return False
    except Exception as e:
        print("Failed to extract the ZIP archive:", e)
        return False
    finally:
        if os.path.exists(zip_path):
            try:
                os.remove(zip_path)
            except OSError as e:
                print(f"Failed to remove zip file: {e}")
                return False

        # Delete the root folder name in the obtained ZIP
        if root_dir and os.path.exists(root_dir):
            try:
                shutil.rmtree(root_dir)
                print(f"Removed extracted folder: {root_dir}")
            except OSError as e:
                print(f"Failed to remove folder {root_dir}: {e.strerror} (Error Code: {e.errno})")
                return False
    return True

## @fn          movie_get_date()
## @brief       Get date information from a video file
## @param[in]   filename        : input file [type str]
## @param[in]   url             : URL info [type str]
## @retval      exif_data       : exif info (key,value) [type List[Tuple[str, Any]]]
def movie_get_date(filename: str, url: str) -> Dict[str, Optional[str]] :
    flag = False    # Initializing variables
    inf: Dict[str, Optional[str]] = {'year':None, 'month':None, 'day':None , 'hour':None, 'min':None, 'sec':None} #変数の初期化

    if(is_ffprobe() == False):
        # If a proxy is set in the environment variables, the proxy information will be used for downloading.
        # If you downloaded the zip file, unzip and extract ffprobe into the same folder as the script.
        res_flag = download_and_extract_ffprobe(url)
        if(res_flag == False):
            print("Error detect. Failed to download ffprobe.")
            return inf

    video_info = ffmpeg.probe(filename)
    move_format = video_info.get('format')
    tags = move_format.get('tags')
    # Checks if tags is not None & 'creation_time' key exists.
    inf_time = tags.get('creation_time') if tags and 'creation_time' in tags else None
    if (inf_time != None):
        pattern = re.compile("(?P<year>[0-9]{4})-(?P<month>[0-9]{1,2})-(?P<day>[0-9]{1,2})T(?P<hour>[0-9]{1,2}):(?P<min>[0-9]{1,2}):(?P<sec>[0-9]+)[\.][0-9]+Z")
        # 2022-10-29T07:28:08.000000Z
        if(pattern.match(inf_time)):
            m = pattern.match(inf_time)
            if m is not None:
                flag = True    #set flag
                inf['year']  = m.group('year')
                inf['month'] = m.group('month')
                inf['day']   = m.group('day')
                inf['hour']  = m.group('hour')
                inf['min']   = m.group('min')
                inf['sec']   = m.group('sec')
            else:
                inf['year']  = None
                inf['month'] = None
                inf['day']   = None
                inf['hour']  = None
                inf['min']   = None
                inf['sec']   = None
    if(flag == False):
        print(f"Warning. Date information could not be retrieved. \n    file={filename}")
    return inf

##
# @brief        Obtain jpeg exif information. Easily obtain exif using library PIL.
# @param[in]    file            : input file [type str]
# @param[in]    field           : exif tag info [type str]
# @retval       exif_data       : exif info (key,value) [type List[Tuple[str, Any]]]
def get_exif(file: str,field: str) -> List[Tuple[str, Any]] :
    #参考URL: https://qiita.com/Gen6/items/88c69ab3a0666895e7a8
    try:
        img = Image.open(file)
    except Exception as e:
        s = os.path.basename(__file__) + " version=" + __version__ + "\n"
        s = s + "----detect error. image file open error.\n"
        s = s + "file=%s\n" % (file)
        s = s +"%s\n%s" % (type(e),e)
        die_print(s)
    try:
        exif = img.getexif()
    except Exception as e:
        s = os.path.basename(__file__) + " version=" + __version__ + "\n"
        s = s + "----detect error. exif error.\n"
        s = s + "file=%s\n" % (file)
        s = s +"%s\n%s" % (type(e),e)
        die_print(s)

    exif_data: List[Tuple[str, Any]] = []
    if exif is None:
        exif_data = [(field, None)]
    else:
        flag_det=0
        for id, value in exif.items():
            if TAGS.get(id) == field:
                flag_det=1
                tag = (str(TAGS.get(id, id)), value)
                exif_data.append(tag)
        if(flag_det==0):
            exif_data = [(field, None)]
    return exif_data


##
# @brief        Get date information from string information
# @param[in]    str             : string [type str]
# @retval       year,month,day  : date info [type list]
def get_dateinf(str_s) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    # Reference URL: https://qiita.com/shoku-pan/items/7045ca15f79bcc97f2d3
    # 2021:08:26 19:47:16
    # 2021/08/26 19:47:16
    pattern = re.compile(r'(?P<year>[12]\d{3})[:/](?P<month>0?[1-9]|1[0-2])[:/](?P<day>0?[1-9]|[12][0-9]|3[01]) ')
    res = pattern.search(str_s)
    if res is None:
        year = None
        month = None
        day = None
    else:
        year = res.group('year')
        month = res.group('month')
        day = res.group('day')
    return year,month,day

##
# @brief        Get date information from string information
# @param[in]    filename        : file name [type str]
# @param[in]    tag             : tag value [type int]
# @param[in]    erropt          : error option [type int]
# @retval       inf             : date info [type Dict]
def get_date_info_fm_raw(filename: str, tag: int, erropt=0)->Dict:
    exif_dict = piexif.load(filename)
    #pprint(exif_dict)
    inf: Dict[str,  Optional[str]] = {}
    if(tag in exif_dict['Exif']):
        date = exif_dict['Exif'][tag]
    else:
        if(erropt==1):
            name = piexif.TAGS['Exif'][tag]["name"]
            msg = os.path.basename(__file__) + " version=" + __version__ + "\n"
            msg += f"----detect error. exif not tag.\n"
            msg += f"    tag={name}"
            die_print(msg)
        else:
            date = None
            inf["date"] = None
            inf["time"] = None
            inf["year"] = None
            inf["month"] = None
            inf["day"] = None
            inf["hour"] = None
            inf["min"] = None
            inf["sec"] = None
    if(date == None) or (date == ""):
        if(erropt==1):
            name = piexif.TAGS['Exif'][tag]["name"]
            msg = os.path.basename(__file__) + " version=" + __version__ + "\n"
            msg = msg + "----detect error. exif tag value is none.\n"
            msg = msg + "    tag=%s\n" % (name)
            die_print(msg)
        else:
            inf["date"] = None
            inf["time"] = None
            inf["year"] = None
            inf["month"] = None
            inf["day"] = None
            inf["hour"] = None
            inf["min"] = None
            inf["sec"] = None
    else:
        date,time=str(date).split(" ")
        date = date.replace("b'", '')
        time = time.replace("'",'')
        year, month, day = date.split(":")
        hour, min, sec = time.split(":")
        inf["date"] = date
        inf["time"] = time
        inf["year"] = year
        inf["month"] = month
        inf["day"] = day
        inf["hour"] = hour
        inf["min"] = min
        inf["sec"] = sec
    return inf

def get_ini_dict_val(section: str) -> ini.IniDict:
    '''
    Set the information you want to set in section="DEFAULT" of the ini file in dict format.
    '''
    return {
        section: {
            'picture_ext': {'type': List[str], 'inf': ['.jpg', '.jpeg' ,'.tif']},
            'movie_ext': {'type': List[str], 'inf': ['.mp4', '.mov', '.mts']},
            'raw_ext': {'type': List[str], 'inf': ['.orf']},
            'mtime_ext': {'type': List[str], 'inf': ['.mts']},
            'url_ffmpeg': {'type': str, 'inf': "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"},
            'date_format': {'type': str, 'inf': "%Y_%m_%d"},
            'tar_folder': {'type': str, 'inf': '.'},
        }
    }

## @fn         get_inifile()
#  @brief      Gets the ini file name. Gets the script file name + the file name with the ".ini" extension.
#  @param[in]  None            : 
#  @retval     ini_file        : ini file name [type str]
def get_inifile() -> str:
    (src_root,src_ext) = os.path.splitext(SCR_PATH)
    if src_ext != "":
        ini_file = SCR_PATH.replace(src_ext, '.ini')
    else:
        # linux のpyinstallerでbinary作成していると拡張子がない
        ini_file = f"{SCR_PATH}.ini"
    return ini_file

##
# @brief        After displaying the string msg, execute sys.exit(1).
# @param[in]    filename        : target file name [type str]
# @retval       none            : 
def die_print(msg: str) -> None:
    print(msg)
    sys.exit(NG_VAL)

if __name__ == "__main__":
    main()
