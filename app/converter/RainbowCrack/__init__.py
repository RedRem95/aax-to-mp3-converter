from os import environ, linesep, listdir
from os.path import isfile, isdir, join as path_join
from subprocess import PIPE, Popen
from re import search as re_search
from typing import Optional
import misc.logging as logging

RCRACK_DIR = environ.get("AC_RCRACK", None)


def is_rcrack_enabled() -> bool:
    if RCRACK_DIR is not None and isdir(RCRACK_DIR):
        if isfile(path_join(RCRACK_DIR, "rcrack")):
            for file in listdir(RCRACK_DIR):
                if file.endswith(".rt") or file.endswith(".rtc"):
                    return True
    return False


def get_activation_bytes(checksum: str) -> Optional[str]:

    if not is_rcrack_enabled():
        return None

    logging.debug(f"Getting activation on {checksum}")
    has_rtc = len([x for x in listdir(RCRACK_DIR) if x.endswith(".rtc")]) > 0
    rcrack_command = ["./rcrack", "." if has_rtc else "*.rt", "-h", checksum]

    rcrack_process = Popen(rcrack_command, stdout=PIPE, stderr=PIPE, cwd=RCRACK_DIR)
    rcrack_result = rcrack_process.communicate()[0]

    if isinstance(rcrack_result, bytes):
        rcrack_result = rcrack_result.decode("utf-8")

    rcrack_result = [x.strip() for x in rcrack_result.split(linesep) if len(x.strip()) > 0][-1]

    rcrack_result = rcrack_result[re_search(r"hex:", rcrack_result).end():].strip()

    logging.debug(f"Activation for {checksum} is {rcrack_result}")

    return rcrack_result
