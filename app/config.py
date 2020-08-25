from os import environ, mkdir
from os.path import join, dirname, isdir, exists
import json
from typing import Optional
from uuid import uuid4
from os.path import isfile, join as path_join
from os import listdir

from config_path import ConfigPath

VERSION = "0.9.3"

__config = {
    "NAME": "AAX to Mp3 - Web converter",
    "DEBUG": "FLASK_DEBUG" in environ and environ.get("FLASK_DEBUG", "").lower() in ["1", "true", "on", "yes"],
    "SESSION_TYPE": environ.get("CONVERTER_SESSION_TYPE", "filesystem"),
    "SESSION_COOKIE_NAME": "audials_converter_session",
    "SECRET_KEY": "6h2&9TrhUF5Yh@",
    "SESSION_USE_SIGNER": True,
    "SESSION_KEY_PREFIX": "ac_session:",
    "SESSION_FILE_DIR": join(dirname(__file__), "sessions"),
    "SESSION_BASED_MODE": False,
    "OUTPUT_TEMPLATE": "{title} - {artist}"
}

__config_description = {
    "OUTPUT_TEMPLATE": "You can use placeholders. Available placeholders: {title}, {artist}, {album}, {album_artist}"
}

__config_visual_name = {
    "INPUT_FOLDER": "Folder for input aax files. Also used for upload",
    "OUTPUT_TEMPLATE": "Template naming the mp3 output",
    "OUTPUT_FOLDER": "Folder for converted mp3 files",
    "SESSION_BASED_MODE": "Every session should get its own folder structure and only has access to its own books",
}

__config["CONFIG_FOLDER"] = environ.get("CONVERTER_CONFIG_PATH",
                                        ConfigPath("botschmot.de", __config["NAME"].replace(" ", "_"),
                                                   "json").readFolderPath(mkdir=True)
                                        )
__config["CONFIG_FILE"] = join(__config["CONFIG_FOLDER"], "config.json")
__config["INPUT_FOLDER"] = join(__config["CONFIG_FOLDER"], "in")
__config["OUTPUT_FOLDER"] = join(__config["CONFIG_FOLDER"], "out")

__file_configs = ["INPUT_FOLDER", "OUTPUT_FOLDER", "SESSION_BASED_MODE", "OUTPUT_TEMPLATE"]
__flask_configs = ["SESSION_TYPE", "SESSION_COOKIE_NAME", "SECRET_KEY", "SESSION_USE_SIGNER", "SESSION_KEY_PREFIX",
                   "SESSION_FILE_DIR", "DEBUG", "NAME"]
__ui_edit_settings = __file_configs


def is_in_session_mode():
    return isinstance(get_config_value("SESSION_BASED_MODE"), bool) and get_config_value("SESSION_BASED_MODE")


def __create_config_from_list(key_list):
    ret = {}
    for x in key_list:
        if x in __config:
            ret[x] = get_config_value(x, "")
    return ret


def get_config_descriptions(key: str) -> Optional[str]:
    return __config_description.get(key, None)


def get_config_descriptive_name(key: str) -> str:
    return __config_visual_name.get(key, key)


def get_config_value(key: str, default=None):
    return __config.get(str(key), default)


def set_config_value(key: str, value):
    __config[str(key)] = value


def get_file_config():
    return __create_config_from_list(__file_configs)


def get_flask_config():
    return __create_config_from_list(__flask_configs)


def get_editable_config():
    return __create_config_from_list(__ui_edit_settings)


def save_file_config():
    with open(__config["CONFIG_FILE"], "w") as fout:
        json.dump(get_file_config(), fout, sort_keys=True, indent=4)


def read_file_config():
    if not exists(__config["CONFIG_FILE"]):
        save_file_config()
        return
    with open(__config["CONFIG_FILE"], "r") as fin:
        data = json.load(fin)
        for key, value in data.items():
            set_config_value(key, value)


def get_out_folder(session=None):
    if session and is_in_session_mode():
        session["id"] = session.get("id", str(uuid4()))
        return join(get_config_value("OUTPUT_FOLDER"), session.get("id", str(uuid4())))
    else:
        return get_config_value("OUTPUT_FOLDER")


def get_in_folder(session=None):
    if session and is_in_session_mode():
        session["id"] = session.get("id", str(uuid4()))
        return join(get_config_value("INPUT_FOLDER"), session.get("id", str(uuid4())))
    else:
        return get_config_value("INPUT_FOLDER")


def get_potential_audio_book_files(session=None):
    folder = get_in_folder(session)
    return [y for y in
            (path_join(folder, x) for x in listdir(folder) if isfile(path_join(folder, x)) and x.lower().endswith(".aax"))]


def get_upload_name(session=None, file_name: str = None):
    if file_name is None:
        file_name = f"{str(uuid4())}.aax"
    return join(get_in_folder(session), file_name)


read_file_config()

if not isdir(__config["INPUT_FOLDER"]):
    mkdir(__config["INPUT_FOLDER"])

if not isdir(__config["OUTPUT_FOLDER"]):
    mkdir(__config["OUTPUT_FOLDER"])
