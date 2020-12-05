from typing import Any
import time
from threading import Thread, Lock
from abc import ABC, abstractmethod
import misc.logging as logging


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
        except (ValueError, TypeError):
            time_out = 1
        self.__time_out = max(time_out, 1)

    def interrupt(self):
        self.__run.set(False)

    def run(self) -> None:
        logging.debug(f"Starting interruptable thread with {self.__time_out}s as timeout")
        if not hasattr(self, "__run"):
            self.__run = AtomicType(init_value=True)
        while self.__run.get():
            run_result = self.one_run()
            if (run_result is None) or (not run_result):
                time.sleep(self.__time_out)

    @abstractmethod
    def one_run(self) -> bool:
        pass
