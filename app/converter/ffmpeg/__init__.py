import hashlib
from os import environ, linesep
from os.path import isfile, abspath, join as path_join
from re import compile as regex_compile
from subprocess import PIPE, Popen
import platform
from typing import AnyStr, Tuple, Optional, List, Generator, Iterable, Dict
from json import loads as loads_json
from converter.RainbowCrack import get_activation_bytes
import misc.logging as logging

FFPROBE_COMMAND = environ.get("AC_FFPROBE", "ffprobe.exe" if platform.system().lower() == "windows" else "ffprobe")
FFMPEG_COMMAND = environ.get("AC_FFMPEG", "ffmpeg.exe" if platform.system().lower() == "windows" else "ffmpeg")

__checksum_line = regex_compile(r"\[aax\] file checksum == .{40}")
__checksum_prefix = regex_compile(f"\[aax\] file checksum == ")


def ffprobe(file: str, ffprobe_commands: List[AnyStr] = None) -> Optional[Tuple[AnyStr, AnyStr]]:
    ffprobe_commands = ffprobe_commands or list(["-hide_banner"])
    file = abspath(file)
    if not isfile(file):
        return None

    ffprobe_process = Popen([FFPROBE_COMMAND] + ffprobe_commands + [file], stdout=PIPE, stderr=PIPE)
    ffprobe_result = ffprobe_process.communicate()
    return ffprobe_result[0].decode("utf-8") if isinstance(ffprobe_result[0], bytes) else str(ffprobe_result[0]), \
           ffprobe_result[1].decode("utf-8") if isinstance(ffprobe_result[1], bytes) else str(ffprobe_result[1])


def get_checksum(file: str) -> Optional[AnyStr]:
    ffprobe_result = ffprobe(file)
    ffprobe_result = ffprobe_result[1]
    if ffprobe_result:
        for ffprobe_line in ffprobe_result.split(linesep):
            ffprobe_line = str(ffprobe_line)
            if __checksum_line.search(ffprobe_line):
                return ffprobe_line[__checksum_prefix.search(ffprobe_line).end():].strip()
    return None


def ffmpeg(input_file: str, output_file: str, activation_bytes: str, quality_level: int = 5,
           format: str = None, cover_file: str = None) -> bool:
    if not isfile(input_file) or isfile(output_file):
        return False
    ffmpeg_process = [FFMPEG_COMMAND, "-activation_bytes", activation_bytes, "-i", input_file]
    if isinstance(cover_file, str):
        ffmpeg_process = ffmpeg_process + ["-i", cover_file]
    ffmpeg_process = ffmpeg_process + ["-q:a", quality_level, "-vn"]
    if isinstance(cover_file, str):
        ffmpeg_process = ffmpeg_process + ["-c:v", "copy", "-id3v2_version", "3", "-metadata:s:v",
                                           "title=\"Album cover\"", "-metadata:s:v", "comment=\"Cover (front)\""]
    if isinstance(format, str):
        ffmpeg_process = ffmpeg_process + ["-f", format]
    ffmpeg_process = ffmpeg_process + [output_file]
    logging.debug(f"Executing ffmpeg process {' '.join(str(x) for x in ffmpeg_process)}")
    ffmpeg_process = Popen([str(x) for x in ffmpeg_process], stdout=PIPE, stderr=PIPE)
    ffmpeg_process.communicate()
    return ffmpeg_process.returncode == 0


def get_cover(input_file: str, output_file: str):
    ffmpeg_process = Popen([FFMPEG_COMMAND, "-i", input_file, "-an", "-vcodec", "copy", output_file], stdout=PIPE, stderr=PIPE)
    ffmpeg_process.communicate()


class AudioBookChapter:

    def __init__(self, start: int, end: int, title: str, other_tags: dict):
        self.__start = start
        self.__end = end
        self.__title = title
        other_tags.pop("title")
        self.__other_tags = other_tags

    def get_start(self) -> int:
        return self.__start

    def get_end(self) -> int:
        return self.__end

    def get_title(self) -> str:
        return self.__title

    def get_other_tags(self) -> dict:
        return dict(self.__other_tags)

    def __str__(self) -> str:
        return f"Audiobook-Chapter<\"{self.get_title()}\" from {self.get_start()} to {self.get_end()}>"


class AudioBook:

    def __init__(self, title: str, artist: str, album_artist: str, album: str, comment: str,
                 file_path: str, chapter: Iterable[AudioBookChapter]):
        self.__activation_bytes = None
        self.__title = title
        self.__artist = artist
        self.__album_artist = album_artist
        self.__album = album
        self.__comment = comment
        self.__chapter = [x for x in chapter]
        self.__file_path = file_path
        self.__checksum = None
        self.get_cover()

    def get_title(self) -> str:
        return self.__title

    def get_artist(self) -> str:
        return self.__artist

    def get_album_artist(self) -> str:
        return self.__album_artist

    def get_sure_artist(self) -> str:
        return self.get_album_artist() if self.get_artist() is None else self.get_artist()

    def get_album(self) -> str:
        return self.__album

    def get_comment(self) -> str:
        return self.__comment

    def iterate_chapters(self) -> Generator[AudioBookChapter, None, None]:
        for x in sorted(self.__chapter, key=lambda x: x.get_start()):
            yield x

    def get_chapter_dict(self) -> Dict[int, Dict[str, str]]:
        ret = dict()
        for i, chapter in enumerate(self.iterate_chapters()):
            ret[i+1] = {
                "start": chapter.get_start(),
                "end": chapter.get_end(),
                "title": chapter.get_title(),
                "tags": chapter.get_other_tags()
            }
        return ret

    def get_info(self) -> Dict[str, object]:
        ret = dict()
        ret["title"] = self.get_title()
        ret["artist"] = self.get_sure_artist()
        if self.get_album():
            ret["album"] = self.get_album()
        if self.get_album_artist():
            ret["album_artist"] = self.get_album_artist()
        if self.get_comment():
            ret["comment"] = self.get_comment()
        ret["chapter"] = self.get_chapter_dict()
        return ret

    def get_checksum(self) -> str:
        if not self.__checksum:
            self.__checksum = get_checksum(self.__file_path)
        return self.__checksum

    def generate_activation_bytes(self) -> str:
        logging.debug(f"Generating activation bytes for {self}")
        self.set_activation_bytes(get_activation_bytes(self.get_checksum()))
        return self.get_activation_bytes()

    def get_activation_bytes(self, create_if_missing: bool = False) -> str:
        if self.__activation_bytes is None and create_if_missing:
            return self.generate_activation_bytes()
        return self.__activation_bytes

    def set_activation_bytes(self, activation_bytes: str):
        self.__activation_bytes = activation_bytes

    def get_output_name(self, template: str):
        return template.format(
            artist=self.get_sure_artist() or "",
            title=self.get_title() or "",
            album=self.get_album() or "",
            album_artist=self.get_album_artist() or ""
        )

    def get_whole_target_path(self, output_folder: str, name_template: str):
        return path_join(output_folder, self.get_output_name(name_template))

    def get_input_file(self):
        return self.__file_path

    def get_cover(self) -> Optional[str]:
        cover_file = f"{self.__file_path}.jpg"
        if not isfile(cover_file):
            get_cover(self.__file_path, cover_file)
        return cover_file if isfile(cover_file) else None

    def already_converted(self, session=None) -> bool:
        return isfile(self.get_whole_target_path(session))

    def get_id(self) -> str:
        return self.hash_string()

    def __eq__(self, other):
        if isinstance(other, AudioBook):
            return self.hash_string() == other.hash_string()
        return False

    def __hash__(self):
        return self.hash_string().__hash__()

    def hash_string(self):
        return AudioBook.hash_filename(self.__file_path)

    def __str__(self):
        return f"Audiobook<{self.get_title()} by {self.get_artist()}>"

    @staticmethod
    def hash_filename(file_path: str) -> str:
        return hashlib.sha256(str(file_path).encode("utf-8")).hexdigest()


__audio_books: Dict[str, AudioBook] = dict()


def get_audiobook_by_file(file: str, add_to_hashtable: bool = False) -> Optional[AudioBook]:
    file = abspath(file)
    ab_hash = AudioBook.hash_filename(file)
    if ab_hash in __audio_books and add_to_hashtable:
        return __audio_books[ab_hash]
    ffprobe_result = ffprobe(file, ffprobe_commands=["-show_format", "-show_chapters", "-print_format", "json",
                                                     "-hide_banner", "-v", "quiet"])
    if ffprobe_result and ffprobe_result[0]:
        ffprobe_result = loads_json(ffprobe_result[0])

        new_ab = AudioBook(title=ffprobe_result["format"]["tags"].get("title", None),
                           artist=ffprobe_result["format"]["tags"].get("artist", None),
                           album_artist=ffprobe_result["format"]["tags"].get("album_artist", None),
                           album=ffprobe_result["format"]["tags"].get("album", None),
                           comment=ffprobe_result["format"]["tags"].get("comment", None),
                           file_path=file,
                           chapter=(AudioBookChapter(start=int(chapter["start"]),
                                                     end=int(chapter["end"]),
                                                     title=str(chapter["tags"].get("title", f"Chapter: {i}")),
                                                     other_tags=chapter["tags"])
                                    for i, chapter in enumerate(sorted(ffprobe_result.get("chapters", []),
                                                                       key=lambda x: int(x["start"]))))
                           )
        if add_to_hashtable:
            __audio_books[new_ab.hash_string()] = new_ab
        return new_ab

    return None


def is_audiobook_allowed(audiobook_id: str, potential_audiobooks: Iterable[str]) -> bool:
    return audiobook_id in [AudioBook.hash_filename(x) for x in potential_audiobooks]


def get_audiobook_by_id(audiobook_id: str, session=None) -> Optional[AudioBook]:
    if is_audiobook_allowed(audiobook_id, session) and audiobook_id in __audio_books:
        return __audio_books[audiobook_id]
    return None


def generate_bytes_by_id(audiobook_id: str, session=None):
    if is_audiobook_allowed(audiobook_id, session) and audiobook_id in __audio_books:
        __audio_books[audiobook_id].generate_activation_bytes()


def use_for_all_for_id(audiobook_id: str, potential_audiobooks: Iterable[str]):
    if is_audiobook_allowed(audiobook_id) and audiobook_id in __audio_books:
        activation_bytes = __audio_books[audiobook_id].get_activation_bytes(False)
        for book_id in (AudioBook.hash_filename(x) for x in potential_audiobooks):
            if book_id in __audio_books:
                __audio_books[book_id].set_activation_bytes(activation_bytes)


def get_chapters(file: str) -> Generator[AudioBookChapter, None, None]:
    return get_audiobook_by_file(file).iterate_chapters()
