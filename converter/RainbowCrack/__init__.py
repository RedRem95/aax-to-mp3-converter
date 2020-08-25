from os import environ, linesep
from os.path import join as path_join, abspath, dirname
from subprocess import PIPE, Popen
from re import search as re_search

RCRACK_DIR = environ.get("AC_RCRACK", path_join(dirname(abspath(__file__)), "tables"))


def get_activation_bytes(checksum: str) -> str:

    print(f"Getting activation on {checksum}", flush=True)

    rcrack_process = Popen(["./rcrack", ".", "-h", checksum], stdout=PIPE, stderr=PIPE, cwd=RCRACK_DIR)
    rcrack_result = rcrack_process.communicate()[0]

    if isinstance(rcrack_result, bytes):
        rcrack_result = rcrack_result.decode("utf-8")

    rcrack_result = [x.strip() for x in rcrack_result.split(linesep) if len(x.strip()) > 0][-1]

    rcrack_result = rcrack_result[re_search(r"hex:", rcrack_result).end():].strip()

    print(f"Activation for {checksum} is {rcrack_result}", flush=True)

    return rcrack_result
