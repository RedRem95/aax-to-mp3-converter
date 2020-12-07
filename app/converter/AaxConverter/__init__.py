from os import rename, remove

from converter.ffmpeg import AudioBook, ffmpeg, add_cover
import misc.logging as logging


def simple_conversion(audiobook: AudioBook, target_path: str, output_format: str = "mp3"):
    try:
        logging.info(f"Converting {audiobook}")
        temporary_out_name = f"{target_path}.conv"
        ffmpeg_result = ffmpeg(input_file=audiobook.get_input_file(),
                               output_file=temporary_out_name,
                               quality_level=5,
                               output_format=output_format,
                               activation_bytes=audiobook.get_activation_bytes())

        logging.info(f"Job for book {audiobook} exited good: {ffmpeg_result}")
        if ffmpeg_result:
            if audiobook.get_cover() is not None:
                logging.debug(f"Adding cover to {audiobook} -> {audiobook.get_cover()}")
                add_cover(temporary_out_name, audiobook.get_cover())
            rename(temporary_out_name, target_path)
        else:
            remove(temporary_out_name)
        return target_path
    except:
        pass
    return None
