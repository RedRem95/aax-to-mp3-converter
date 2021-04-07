import json
import uuid
from os import rename, remove

from converter.ffmpeg import AudioBook, ffmpeg, add_cover
import misc.logging as logging


def simple_conversion(audiobook: AudioBook, target_path: str, output_format: str = "mp3"):
    try:
        logging.info(f"Converting {audiobook}")
        temporary_out_name = f"{target_path}.conv"
        ffmpeg_result, (stdout, stderr) = ffmpeg(input_file=audiobook.get_input_file(),
                                                 output_file=temporary_out_name,
                                                 quality_level=2,
                                                 output_format=output_format,
                                                 activation_bytes=audiobook.get_activation_bytes())

        logging.info(f"Job for book {audiobook} exited good: {ffmpeg_result}")
        if ffmpeg_result:
            if audiobook.get_cover() is not None:
                logging.debug(f"Adding cover to {audiobook} -> {audiobook.get_cover()}")
                add_cover(temporary_out_name, audiobook.get_cover())
            rename(temporary_out_name, target_path)
            return target_path
        else:
            error_name = f"/tmp/error_{uuid.uuid4()}.json"
            with open(error_name, "w") as f_err:
                if isinstance(stdout, bytes):
                    stdout = stdout.decode("utf-8")
                else:
                    stdout = str(stdout)
                if isinstance(stderr, bytes):
                    stderr = stderr.decode("utf-8")
                else:
                    stderr = str(stderr)
                json.dump({"stdout": stdout, "stderr": stderr}, f_err)
            logging.notify("FFMPEG had an error during conversion",
                           extra={"notification_title": "FFMPEG-ERROR", "attach": error_name})
            remove(temporary_out_name)
            remove(error_name)
    except:
        pass
    return None
