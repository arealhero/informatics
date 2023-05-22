#!/usr/bin/env python

import sys
import csv
from math import log

def print_usage():
    print('usage: entropy.py <csv-file>')

if __name__ == '__main__':
    argc = len(sys.argv)

    if argc != 2:
        print_usage()
        exit(1)

    filename = sys.argv[1]
    print(f'calculating entropy for "{filename}"...')

    entropy = 0.
    letters_count = 0
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            letter = row['letter']
            p = float(row['frequency'])
            entropy -= p * log(p, 2)
            letters_count += 1

    max_entropy = log(letters_count, 2)
    print(f'entropy: {entropy} (max entropy: {max_entropy})')

    relative_entropy = entropy / max_entropy
    print(f'relative entropy: {relative_entropy}')

    redundancy = 1 - relative_entropy
    print(f'redundancy: {redundancy}')

