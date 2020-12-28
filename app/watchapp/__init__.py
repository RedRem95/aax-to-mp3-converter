from typing import List, Optional
import os
import tempfile
import shutil
from uuid import uuid4
from converter.ffmpeg import AudioBook, get_audiobook_by_file
from converter.AaxConverter import simple_conversion

from misc import InterruptableRepeatingThread
import misc.logging as logging


class WatchingApp(InterruptableRepeatingThread):

    def __init__(self, watch_folder: str, target_folder: str, thread_name="Main thread of folder watcher",
                 recursive: bool = False, debug: bool = False, scanning_interval: int = 1):
        super().__init__(daemon=True, name=thread_name, time_out=scanning_interval)
        self._watch_folder = watch_folder
        self._target_folder = target_folder
        self._recursive = recursive
        self._debug = debug
        logging.info(f"Starting watch on \"{watch_folder}\" as {self.__class__.__name__}")

    def one_run(self) -> bool:
        all_files = self.get_file_list(current_element=self._watch_folder, recursive=self._recursive)
        all_files = [x for x in all_files if
                     x.lower().endswith(".aax") or x.lower().endswith(".mp3") or x.lower().endswith(".aaxc")]
        if len(all_files) <= 0:
            return False
        work_file = self.prepare_file(selected_file=all_files[0])
        audiobook = get_audiobook_by_file(work_file)
        if audiobook is None:
            self.broken_input(selected_file=all_files[0], work_file=work_file)
            logging.notify(f"Audiobook conversion of {os.path.basename(all_files[0])} failed. "
                           f"Has been awarded 'broken' :(")
            return True
        if self.audiobook_already_exists(audiobook=audiobook, target_folder=self._target_folder) is None:
            logging.info(f"Audiobook {audiobook} already exists. Deleting and carrying on")
            self.cleanup(audiobook=audiobook, final_file=None, selected_file=all_files[0])
            return True
        cover = audiobook.get_cover()

        _extra = {"notification_title": "Conversion started"}
        if cover is not None:
            _extra["audiobook_cover"] = cover

        logging.notify(message=f"Conversion of {audiobook} initiated", extra=_extra)
        try:
            _ = audiobook.get_activation_bytes(create_if_missing=True)
        except TypeError:
            pass
        converted_file = simple_conversion(audiobook=audiobook, target_path=f"{work_file}.mp3")
        logging.debug(message=f"Conversion of {audiobook} finished. Saved to \"{converted_file}\"")
        if not self.finalize_file(final_file=converted_file, audiobook=audiobook, target_folder=self._target_folder):
            logging.info(f"Finalization of {audiobook} failed")
            logging.notify(message=f"Conversion of {audiobook} failed",
                           extra={"notification_title": "Conversion failed"})
            self.stale_input(selected_input=all_files[0])
        else:
            logging.info(f"Finalization of {audiobook} succeeded. Going to clean up")
            logging.success(message=f"Conversion and upload of {audiobook} secceded",
                            extra={"notification_title": "Conversion successful"})
            self.cleanup(audiobook=audiobook, final_file=converted_file, selected_file=all_files[0])
        return True

    def audiobook_already_exists(self, audiobook: AudioBook, target_folder: str) -> Optional[str]:
        target_file = audiobook.get_whole_target_path(output_folder=target_folder, name_template=self.get_template())
        if self.exists(path=target_file):
            return None
        return target_file

    # noinspection PyMethodMayBeStatic
    def broken_input(self, selected_file: Optional[str], work_file: Optional[str]):
        if selected_file is not None and os.path.exists(selected_file):
            os.rename(src=selected_file, dst=f"{selected_file}.broken")
        if work_file is not None and os.path.exists(work_file):
            os.remove(work_file)

    def exists(self, path: str) -> bool:
        return os.path.exists(path=path)

    def get_file_list(self, current_element: str, recursive: bool) -> List[str]:
        if os.path.isfile(current_element):
            return [current_element]
        if not os.path.isdir(current_element):
            return []
        complete_list = os.listdir(current_element)
        ret = []
        for element_name in complete_list:
            element_path = os.path.join(current_element, element_name)
            if os.path.isfile(element_path) or (recursive and os.path.isdir(element_path)):
                ret.extend(self.get_file_list(current_element=element_path, recursive=recursive))
        return ret

    # noinspection PyMethodMayBeStatic
    def get_temp_dir(self) -> str:
        my_tempdir = os.path.join(tempfile.gettempdir(), "aax_converter")
        if not os.path.exists(my_tempdir):
            os.mkdir(my_tempdir)
        return my_tempdir

    def prepare_file(self, selected_file: str) -> str:
        new_file = os.path.join(self.get_temp_dir(), str(uuid4()))
        shutil.copy(selected_file, new_file)
        return new_file

    # noinspection PyMethodMayBeStatic
    def get_template(self) -> str:
        return "{artist}/{album}/{title}.mp3"

    # noinspection PyMethodMayBeStatic
    def stale_input(self, selected_input: str):
        stale_template = "{selected_input}.failed{i}"
        stale_name = stale_template.format(selected_input=selected_input, i="")
        i = 0
        while os.path.exists(stale_name):
            i += 1
            stale_name = stale_template.format(selected_input=selected_input, i=f"_{i}")
        os.rename(src=selected_input, dst=stale_name)

    # noinspection PyMethodMayBeStatic
    def cleanup(self, audiobook: AudioBook, final_file: Optional[str], selected_file: Optional[str]):
        for to_remove in [audiobook.get_input_file(), audiobook.get_cover(), final_file, selected_file]:
            if to_remove is not None and os.path.exists(to_remove):
                os.remove(to_remove)

    def finalize_file(self, final_file: str, audiobook: AudioBook, target_folder: str) -> bool:
        target_file = self.audiobook_already_exists(audiobook=audiobook, target_folder=target_folder)
        if final_file is None or target_file is None:
            return False
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        shutil.move(src=final_file, dst=target_file)
        if audiobook.get_cover() is not None:
            shutil.move(src=audiobook.get_cover(), dst=f"{target_file}.jpg")
        return True
