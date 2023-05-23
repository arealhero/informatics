import math
from contextlib import contextmanager

class BufferedSerializer:
    def __init__(self, filename):
        self.file = open(filename, 'wb')

        self.buffer = ''
        self.bytes_sent = 0

    def close(self):
        self.__try_to_flush_buffer(align=True)

    def send_bits(self, bits):
        if bits == '':
            return 0

        self.buffer += bits

        return self.__try_to_flush_buffer()

    def get_sent_bytes(self):
        return self.bytes_sent + math.ceil(len(self.buffer) / 8)

    def get_sent_bits(self):
        return 8 * self.bytes_sent + len(self.buffer)

    def __try_to_flush_buffer(self, align=False):
        if self.buffer == '':
            return 0

        if align:
            padding_size = (8 - len(self.buffer) % 8) % 8
            self.buffer += '0' * padding_size

        bytes_count = self.__send_bytes(self.buffer)
        if bytes_count != 0:
            self.buffer = self.buffer[8*bytes_count:]

        return bytes_count

    def __send_bytes(self, bits_buffer):
        bytes_count = len(bits_buffer) // 8

        if bytes_count == 0:
            return 0

        byte_array = [bits_buffer[8*i:8*(i+1)] for i in range(bytes_count)]
        byte_array = [int(i, 2) for i in byte_array]

        self.file.write(bytes(byte_array))
        self.bytes_sent += bytes_count

        return bytes_count

class BufferedDeserializer:
    def __init__(self, filename):
        self.file = open(filename, 'rb')
        self.buffer = ''

    def close(self):
        self.file.close()

    def read_char(self):
        return self.read_bits(8) # FIXME: convert to char or something

    def read_int8(self):
        return int(self.read_bits(8), 2)

    def read_int16(self):
        return int(self.read_bits(16), 2)

    def read_int32(self):
        return int(self.read_bits(32), 2)

    def read_int64(self):
        return int(self.read_bits(64), 2)

    def read_bits(self, count):
        if count == 0:
            return ''

        buffer_size = len(self.buffer)
        if buffer_size < count:
            deficit = count - buffer_size
            bytes_number = math.ceil(deficit / 8)
            data = self.file.read(bytes_number)

            if data is None:
                raise RuntimeError('cannot read more bits')

            for byte in data:
                self.buffer += f'{byte:08b}'

        result = self.buffer[:count]
        self.buffer = self.buffer[count:]

        return result

    def read_bit(self):
        return self.read_bits(1)

    def read_bytes(self, count):
        return self.read_bits(8 * count)

    def read_byte(self):
        return self.read_bytes(1)

@contextmanager
def open_serializer(*args, **kwds):
    serializer = BufferedSerializer(*args, **kwds)
    try:
        yield serializer
    finally:
        serializer.close()

@contextmanager
def open_deserializer(*args, **kwds):
    serializer = BufferedDeserializer(*args, **kwds)
    try:
        yield serializer
    finally:
        serializer.close()

