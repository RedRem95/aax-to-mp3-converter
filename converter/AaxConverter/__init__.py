from queue import Queue
from threading import Thread
from os import rename, remove

from converter.ffmpeg import AudioBook, ffmpeg
from misc import AtomicType

__in_conversion_atomic_data = AtomicType(False)


def in_conversion_atomic():
    return __in_conversion_atomic_data


def simple_conversion(audiobook: AudioBook, target_path: str):
    temporary_out_name = f"{target_path}.conv"
    ffmpeg_result = ffmpeg(input_file=audiobook.get_input_file(),
                           cover_file=audiobook.get_cover(),
                           output_file=temporary_out_name,
                           quality_level=5,
                           format="mp3",
                           activation_bytes=audiobook.get_activation_bytes())

    print(f"Job for book {audiobook} exited good: {ffmpeg_result}")
    if ffmpeg_result:
        rename(temporary_out_name, target_path)
    else:
        remove(temporary_out_name)
    return target_path

class __ConverionJob:

    def __init__(self, audiobook: AudioBook, session=None):
        self.__audiobook = audiobook
        self.__session = session

    def run_job(self):
        raise NotImplementedError("Not reimplemented after Converter redesign")
        in_conversion_atomic().set(True)
        print(f"Starting conversion of {self.__audiobook}")
        if self.__audiobook.already_converted(self.__session):
            return
        temporary_out_name = f"{self.__audiobook.get_whole_target_path(self.__session)}.conv"
        simple_conversion(self.__audiobook, target_path=self.__audiobook.get_whole_target_path(session=self.__session))
        in_conversion_atomic().set(False)


__conversion_queue: "Queue[__ConverionJob]" = Queue()


def conversion_queue_empty():
    return __conversion_queue.empty()


def conversion_queue_running():
    return (not conversion_queue_empty()) or in_conversion_atomic().get()


def add_audiobook_to_queue(audiobook: AudioBook, session=None):
    if audiobook and not audiobook.already_converted(session):
        __conversion_queue.put(__ConverionJob(audiobook, session))


def __run_conversion_thread():
    while True:
        job = __conversion_queue.get()
        job.run_job()


__worker_thread = Thread(daemon=True, name="conversion", target=__run_conversion_thread)
__worker_thread.start()
