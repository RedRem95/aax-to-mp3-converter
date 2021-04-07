from typing import Any
try:
    from packaging.version import parse as _parse
except ImportError:
    def _parse(version: str) -> Any:
        return version

_VERSION = "0.10.3"


def get_version() -> Any:
    return _parse(_VERSION)
