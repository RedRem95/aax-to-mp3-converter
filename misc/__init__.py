import asyncio
from typing import Optional, Callable, Any, Iterable, Mapping
import time
from werkzeug.routing import BaseConverter
from threading import Thread
from abc import ABC, abstractmethod


class BytesConverter(BaseConverter):

    def to_python(self, value):
        return str(value).encode("utf-8")

    def to_url(self, value):
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return str(value)


class AtomicType:

    def __init__(self, init_value):
        self.__value = init_value
        #self.__lock = asyncio.Lock()

    def get(self):
        val = None
        val = self.__value
        return val

    def set(self, value):
        self.__value = value


class InterruptableThread(Thread, ABC):

    def __init__(self, group: None = ..., target: Optional[Callable[..., Any]] = ..., name: Optional[str] = ...,
                 args: Iterable[Any] = ..., kwargs: Mapping[str, Any] = ..., *, daemon: Optional[bool] = ...) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.__run = True

    def interrupt(self):
        self.__run = False

    def run(self) -> None:
        if not hasattr(self, "__run"):
            self.__run = True
        while self.__run:
            self.one_run()
            time.sleep(1)

    @abstractmethod
    def one_run(self) -> None:
        pass
