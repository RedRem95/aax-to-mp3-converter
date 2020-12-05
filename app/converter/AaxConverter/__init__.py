from os import rename, remove

from converter.ffmpeg import AudioBook, ffmpeg
import misc.logging as logging


def simple_conversion(audiobook: AudioBook, target_path: str):
    try:
        logging.info(f"Converting {audiobook}")
        temporary_out_name = f"{target_path}.conv"
        ffmpeg_result = ffmpeg(input_file=audiobook.get_input_file(),
                               cover_file=audiobook.get_cover(),
                               output_file=temporary_out_name,
                               quality_level=5,
                               format="mp3",
                               activation_bytes=audiobook.get_activation_bytes())

        logging.info(f"Job for book {audiobook} exited good: {ffmpeg_result}")
        if ffmpeg_result:
            rename(temporary_out_name, target_path)
        else:
            remove(temporary_out_name)
        return target_path
    except:
        pass
    return None
