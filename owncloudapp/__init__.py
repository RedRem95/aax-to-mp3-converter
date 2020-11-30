from typing import List, Optional

import owncloud
import os
from threading import Thread
from uuid import uuid4
from converter.ffmpeg import AudioBook, get_audiobook_file
from converter.AaxConverter import simple_conversion
from misc import InterruptableThread


class __OwncloudApp(InterruptableThread):

    def __init__(self, username: str, password: str, watch_folder: str, destination_folder: str, tmp_dir: str,
                 debug: bool = False):
        super().__init__(daemon=True, name="Mainthread of owncloud watcher")
        self.__username = username
        self.__watch_folder = watch_folder
        self.__destination_folder = destination_folder
        self.__debug = debug
        self.__oc = owncloud.Client("https://owncloud.botschmot.de")
        self.__oc.login(user_id=username, password=password)
        self.__tmp_dir = tmp_dir

    def __mkdir_recursive(self, path_parts: List[str]) -> Optional[str]:

        print(f"Trying to create directory {os.path.join(*path_parts)}")

        for i in range(1, len(path_parts) + 1, 1):
            try:
                self.__oc.mkdir(os.path.join(*path_parts[:i]))
            except owncloud.owncloud.HTTPResponseError as e:
                if e.status_code != 405:
                    return None

        return os.path.join(*path_parts)

    def one_run(self):
        found_files = self.__oc.list(path=self.__watch_folder, depth=1)
        for file in found_files:
            file: owncloud.owncloud.FileInfo = file
            if file.file_type == "file":
                print(f"Found input file {file.path}")
                tmp_filename = uuid4().__str__()
                if str(file.path).lower().endswith("AAX".lower()) or str(file.path).lower().endswith("MP3".lower()):
                    print("  -> File is aax")
                    tmp_target = os.path.join(self.__tmp_dir, f"{tmp_filename}")
                    print("Downloading to", tmp_target)
                    if self.__oc.get_file(remote_path=file.path, local_file=tmp_target):
                        audiobook = get_audiobook_file(file=tmp_target, add_to_hashtable=False)
                        if audiobook is not None:
                            print(f"Download complete of {audiobook}")
                            if str(file.path).lower().endswith("AAX".lower()):
                                if audiobook.get_activation_bytes(create_if_missing=True) is None:
                                    audiobook = None
                            if audiobook is not None:
                                upload_file = simple_conversion(audiobook=audiobook, target_path=f"{tmp_target}.mp3")
                                cover = audiobook.get_cover()
                                remote_path = self.__mkdir_recursive([self.__destination_folder,
                                                                      audiobook.get_sure_artist(),
                                                                      audiobook.get_title()])
                                if remote_path is not None and upload_file is not None:
                                    remote_file = os.path.join(remote_path, audiobook.get_output_name("{title}"))
                                    self.__oc.put_file(remote_path=f"{remote_file}.jpg", local_source_file=cover)
                                    print("Cover uploaded")
                                    self.__oc.put_file(remote_path=f"{remote_file}.mp3", local_source_file=upload_file)
                                    print("Mp3 Uploaded")

                print("Cleanup")
                for tmp_file_delete in os.listdir(path=self.__tmp_dir):
                    if os.path.exists(os.path.join(self.__tmp_dir, tmp_file_delete)) and \
                            tmp_file_delete.startswith(tmp_filename):
                        print(f"Deleting local {os.path.join(self.__tmp_dir, tmp_file_delete)}")
                        os.remove(os.path.join(self.__tmp_dir, tmp_file_delete))
                print(f"Deleting remote {file.path}")
                self.__oc.delete(path=file.path)
                break


def get_instance(username: str, password: str, watch_folder: str, destination_folder: str, tmp_dir: str,
                 debug: bool = False) -> Thread:
    print(f"Starting to run Owncloud app as {username}")
    print(f"\tOrigin folder: {watch_folder}")
    print(f"\tTarget folder: {destination_folder}")
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    cloud_app = __OwncloudApp(username=username, password=password, watch_folder=watch_folder,
                              destination_folder=destination_folder, tmp_dir=tmp_dir, debug=debug)
    cloud_app.start()
    return cloud_app
