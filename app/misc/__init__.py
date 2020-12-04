from typing import Any
import time
from threading import Thread, Lock
from abc import ABC, abstractmethod


class AtomicType:

    def __init__(self, init_value: Any):
        self.__value: Any = init_value
        self.__lock = Lock()

    def get(self) -> Any:
        with self.__lock:
            return self.__value

    def set(self, value: Any):
        with self.__lock:
            self.__value = value


class InterruptableRepeatingThread(Thread, ABC):

    def __init__(self, time_out: int = 1, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.__run = AtomicType(init_value=True)
        try:
            time_out = int(time_out)
        except ValueError:
            time_out = 0
        self.__time_out = time_out if time_out > 0 else 0

    def interrupt(self):
        self.__run.set(False)

    def run(self) -> None:
        if not hasattr(self, "__run"):
            self.__run = AtomicType(init_value=True)
        while self.__run.get():
            self.one_run()
            time.sleep(self.__time_out)

    @abstractmethod
    def one_run(self) -> None:
        pass
