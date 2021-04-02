from typing import List, Optional
from uuid import uuid4

import owncloud
from owncloud.owncloud import FileInfo as OwncloudFileInfo
import os
from watchapp import WatchingApp
from converter.ffmpeg import AudioBook
import misc.logging as logging
import time


class OwncloudApp(WatchingApp):

    def __init__(self, username: str, password: str, watch_folder: str, destination_folder: str, host: str,
                 debug: bool = False, scanning_interval: int = 1, template: str = "{artist}/{album}/{title}.mp3"):
        super().__init__(watch_folder=watch_folder, target_folder=destination_folder, debug=debug, recursive=True,
                         thread_name="Main thread of owncloud watcher", scanning_interval=scanning_interval,
                         template=template)
        self._username = username
        self._host = host
        self._oc = owncloud.Client(host)
        _wait = 5
        while True:
            try:
                self._oc.login(user_id=username, password=password)
                break
            except owncloud.owncloud.HTTPResponseError as e:
                logging.error(f"Got Connection Error while connection to owncloud. Waiting {_wait}min for retry. "
                              f"HTTP-Error: {e.status_code}")
                time.sleep(_wait * 60)
        logging.info(f"Connected to owncloud {host}. Host runs version {self._oc.get_version()}")

    def __mkdir_recursive(self, path_parts: List[str]) -> Optional[str]:

        logging.debug(f"Trying to create directory {os.path.join(*path_parts)}")

        for i in range(1, len(path_parts) + 1, 1):
            try:
                self._oc.mkdir(os.path.join(*path_parts[:i]))
            except owncloud.owncloud.HTTPResponseError as e:
                if e.status_code != 405:
                    return None

        return os.path.join(*path_parts)

    def get_file_list(self, current_element: str, recursive: bool) -> List[str]:
        elements: List[OwncloudFileInfo] = self._oc.list(path=current_element, depth=2_147_483_647 if recursive else 1)
        return [x.path for x in elements if x.file_type == "file"]

    def prepare_file(self, selected_file: str) -> str:
        new_file = os.path.join(self.get_temp_dir(), str(uuid4()))
        logging.debug(f"Starting download of {selected_file} from {self._host}")
        self._oc.get_file(selected_file, new_file)
        logging.debug(f"Finished download of {selected_file} from {self._host}")
        return new_file

    def cleanup(self, audiobook: AudioBook, final_file: Optional[str], selected_file: Optional[str]):
        super().cleanup(audiobook=audiobook, final_file=final_file, selected_file=None)
        try:
            if selected_file is not None:
                self._oc.delete(path=selected_file)
        except owncloud.owncloud.HTTPResponseError:
            pass

    def stale_input(self, selected_input: str):
        stale_template = "{selected_input}.failed{i}"
        stale_name = stale_template.format(selected_input=selected_input, i="")
        i = 0
        while self.exists(stale_name):
            i += 1
            stale_name = stale_template.format(selected_input=selected_input, i=f"_{i}")
        try:
            self._oc.move(remote_path_source=selected_input, remote_path_target=stale_name)
        except owncloud.owncloud.HTTPResponseError:
            pass

    def broken_input(self, selected_file: Optional[str], work_file: Optional[str]):
        super().broken_input(None, work_file)
        if selected_file is not None and self.exists(selected_file):
            self._oc.move(remote_path_source=selected_file, remote_path_target=f"{selected_file}.broken")

    def exists(self, path: str):
        try:
            _ = self._oc.file_info(path=path)
            return True
        except owncloud.owncloud.HTTPResponseError as e:
            if e.status_code != 404:
                return True
        return False

    def finalize_file(self, final_file: str, audiobook: AudioBook, target_folder: str) -> bool:
        target_file = self.audiobook_already_exists(audiobook=audiobook, target_folder=target_folder)
        if final_file is None or target_file is None:
            return False
        self.__mkdir_recursive(os.path.dirname(target_file).split("/"))
        logging.info(f"Starting upload of {audiobook} to \"{target_file}\" on {self._host}")
        self._oc.put_file(remote_path=target_file, local_source_file=final_file)
        if audiobook.get_cover() is not None:
            self._oc.put_file(remote_path=f"{target_file}.jpg", local_source_file=audiobook.get_cover())
        logging.info(f"Finished upload of {audiobook} to \"{target_file}\" on {self._host}")
        return True

    def __repr__(self):
        return f"{self.__class__.__name__}<\"{self._watch_folder}\" -> \"{self._target_folder}\" on {self._host}[{self._oc.get_version()}]>"
