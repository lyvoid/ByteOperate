#!/usr/bin/env python3
# -*-coding:utf-8-*-

from io import BytesIO
from stream_io_exception import *


class StreamIO(BytesIO):
    def __init__(self, *args, convert_type='big', **kwargs):
        self.convert_type = convert_type
        super().__init__(*args, **kwargs)

    def _write_u_number(self, value: int, length: int):
        self.write(value.to_bytes(length, self.convert_type))

    def _read_u_number(self, length: int) -> int:
        return int.from_bytes(self.read(length), self.convert_type)

    def _write_number(self, value: int, length: int):
        max_number = (1 << (length * 8 - 1)) - 1
        min_number = - (1 << (length * 8 - 1))
        if not min_number <= value <= max_number:
            raise CastException("can not cast int number out of %s to %s to proper type" % (
                min_number, max_number
            ))

        # if value < 0, set first bit to 1
        if value < 0:
            if value != min_number:
                value = value + min_number
            value = -value
        self.write(value.to_bytes(length, self.convert_type))

    def _read_number(self, length: int) -> int:
        max_number = 1 << (length * 8 - 1)
        value = int.from_bytes(self.read(length), self.convert_type)
        if value == max_number:
            return -max_number
        if value > max_number:
            return -(value - max_number)
        return value

    def write_u_short(self, value: int):
        self._write_u_number(value, 2)

    def read_u_short(self) -> int:
        return self._read_u_number(2)

    def write_short(self, value: int):
        self._write_number(value, 2)

    def read_short(self):
        return self._read_number(2)

    def write_str(self, value: str, encoding='utf-8'):
        bytes_value_ = value.encode(encoding)
        length = len(bytes_value_)
        if length > 65535:
            raise CastException('can not write string bytes whose length larger than 65535 to stream')
        self.write_u_short(length)
        self.write(bytes_value_)

    def read_str(self, encoding='utf-8') -> str:
        length = self.read_u_short()
        return self.read(length).decode(encoding)


if __name__ == '__main__':
    si = StreamIO()
    si.write_short(-32576)
    si.write_u_short(65535)
    si.write_str("shelly")

    bytes_value = si.getvalue()
    print(bytes_value)

    si = StreamIO(bytes_value)
    print(si.read_short())
    print(si.read_u_short())
    print(si.read_str())
