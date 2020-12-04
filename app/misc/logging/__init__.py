import logging
from typing import Optional, Dict, Any

from misc.logging.notifications import NotificationHandler, NOTIFICATION_LEVEL, SUCCESS_LEVEL
from logging import CRITICAL as CRITICAL_LEVEL, FATAL as FATAL_LEVEL, ERROR as ERROR_LEVEL, WARNING as WARNING_LEVEL
from logging import WARN as WARN_LEVEL, INFO as INFO_LEVEL, DEBUG as DEBUG_LEVEL


class TracebackInfoFilter(logging.Filter):
    """Clear or restore the exception on log records"""

    def __init__(self, clear=True):
        super().__init__()
        self.clear = clear

    def filter(self, record):
        if self.clear:
            record._exc_info_hidden, record.exc_info = record.exc_info, None
            # clear the exception traceback text cache, if created.
            record.exc_text = None
        elif hasattr(record, "_exc_info_hidden"):
            record.exc_info = record._exc_info_hidden
            del record._exc_info_hidden
        return True


logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger()
_logger.handlers = []
_logger_handler = logging.StreamHandler()
_logger_handler.setFormatter(
    logging.Formatter(
        f"%(threadName)-25s - %(asctime)s - [%(levelname)-12s] - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'))
_logger_handler.addFilter(TracebackInfoFilter())
_logger_handler.setLevel(logging.getLevelName("INFO"))
_logger.addHandler(_logger_handler)
_notification_handler = NotificationHandler()
_notification_handler.addFilter(TracebackInfoFilter())
_logger.addHandler(_notification_handler)


def set_commandline_level(level: int):
    _logger_handler.setLevel(level=level)


def add_notification_url(*apprise_urls: str):
    _notification_handler.add_apprise_url(*apprise_urls)


def log(message: str, level: int, extra: Optional[Dict[str, Any]] = None):
    _logger.log(msg=message, level=level, extra=extra)


def debug(message: str, extra: Optional[Dict[str, Any]] = None):
    log(message=message, level=DEBUG_LEVEL, extra=extra)


def info(message: str, extra: Optional[Dict[str, Any]] = None):
    log(message=message, level=INFO_LEVEL, extra=extra)


def warn(message: str, extra: Optional[Dict[str, Any]] = None):
    log(message=message, level=WARN_LEVEL, extra=extra)


def warning(message: str, extra: Optional[Dict[str, Any]] = None):
    log(message=message, level=WARNING_LEVEL, extra=extra)


def error(message: str, extra: Optional[Dict[str, Any]] = None):
    log(message=message, level=ERROR_LEVEL, extra=extra)


def fatal(message: str, extra: Optional[Dict[str, Any]] = None):
    log(message=message, level=FATAL_LEVEL, extra=extra)


def critical(message: str, extra: Optional[Dict[str, Any]] = None):
    log(message=message, level=CRITICAL_LEVEL, extra=extra)


def success(message: str, extra: Optional[Dict[str, Any]] = None):
    log(message=message, level=SUCCESS_LEVEL, extra=extra)


def notification(message: str, extra: Optional[Dict[str, Any]] = None):
    log(message=message, level=NOTIFICATION_LEVEL, extra=extra)


def notify(message: str, extra: Optional[Dict[str, Any]] = None):
    notification(message=message, extra=extra)
