#!/usr/bin/env python

import sys, os
import logging

from math import log

from huffman_tree import HuffmanTree
from serialization import open_serializer, open_deserializer

LOG_FORMAT = os.getenv('LOG_FORMAT', '[%(asctime)s %(name)s] %(levelname)s: %(message)s')
logging.basicConfig(format=LOG_FORMAT, level=logging.WARNING)

def print_usage():
    print('usage: huffman.py <-e|-d> <file>')

def print_frequencies(frequencies):
    print(f'read {len(frequencies)} bytes, frequencies are:')
    print('    ', end='')
    for i in range(16):
        print(f'\t{i:x}', end='')
    print()
    for i in range(16):
        print(f'{hex(i)}:', end='')
        for j in range(16):
            print(f'\t{frequencies[16 * i + j]}', end='')
        print()

def encode(filename):
    frequencies = [0] * 256
    uncompressed_size = 0

    logging.debug('counting frequencies')
    with open(filename, 'rb') as f:
        while (byte := f.read(1)):
            frequencies[int.from_bytes(byte)] += 1
            uncompressed_size += 1

    print(f'{filename}:     size = {uncompressed_size} bytes')
    # print_frequencies(frequencies)

    tree = HuffmanTree()
    logging.debug('building tree')
    tree.build(frequencies)

    byte_dict = tree.to_dict()

    bits_per_symbol = 0
    entropy = 0
    for i in range(256):
        p = frequencies[i] / uncompressed_size
        if p != 0:
            entropy -= p * log(p, 2)
            bits_per_symbol += frequencies[i] * len(byte_dict[i])
    bits_per_symbol /= uncompressed_size

    print(f'\n----------------------------------------------')
    print(f'entropy:             {entropy}')
    print(f'bits per symbol:     {bits_per_symbol}')
    print(f'code redundancy:     {bits_per_symbol - entropy}')
    print()

    max_entropy = log(256, 2)
    print(f'max entropy:         {max_entropy}')
    print(f'relative entropy:    {entropy / max_entropy}')
    print(f'relative redundancy: {1 - entropy / max_entropy}')
    print(f'----------------------------------------------\n')

    # for key, value in sorted(byte_dict.items(), key=lambda item: len(item[1])):
    #     print(f'{hex(key)}: {value}')

    compressed_size_in_bits = 0
    for i in range(256):
        frequency = frequencies[i]
        if frequency != 0:
            compressed_size_in_bits += frequency * len(byte_dict[i])
    padding = (8 - compressed_size_in_bits % 8) % 8

    bytes_sent = 0
    compressed_filename = filename + '.huf'
    with open_serializer(compressed_filename) as serializer:
        logging.debug('serializing tree')
        tree.serialize(serializer)
        padding = (padding - len(serializer.buffer)) % 8

        logging.debug('serializing body')
        serializer.send_bits(f'{uncompressed_size:064b}')

        with open(filename, 'rb') as f:
            while (byte := f.read(1)):
                bits = byte_dict[int.from_bytes(byte)]
                serializer.send_bits(bits)

            serializer.send_bits('0' * padding)

        bytes_sent = serializer.get_sent_bytes()

    print(f'{compressed_filename}: size = {bytes_sent} bytes')
    space_saving = 1 - bytes_sent / uncompressed_size
    print(f'space saving: {space_saving * 100}%')

def decode(filename):
    uncompressed_filename, filename_extension = os.path.splitext(filename)

    if filename_extension != ".huf":
        uncompressed_filename = filename + '.uncompressed'

    with open_deserializer(filename) as deserializer:
        tree = HuffmanTree.deserialize(deserializer)

        # byte_dict = tree.to_dict()
        # for key, value in sorted(byte_dict.items(), key=lambda item: len(item[1])):
        #     print(f'{hex(key)}: {value}')

        body_size_in_bytes = deserializer.read_int64()

        with open_serializer(uncompressed_filename) as uncompressed_file:
            for _ in range(body_size_in_bytes):
                symbol = tree.decode_one_letter(deserializer)
                uncompressed_file.send_bits(f'{symbol:08b}')


if __name__ == '__main__':
    argc = len(sys.argv)

    if argc != 3:
        print_usage()
        exit(1)

    flag = sys.argv[1]
    filename = sys.argv[2]

    if flag == '-e':
        encode(filename)
    elif flag == '-d':
        decode(filename)
    else:
        print_usage()
        exit(1)

