import asyncio

from werkzeug.routing import BaseConverter


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

