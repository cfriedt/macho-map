#!/usr/bin/env python3
# Copyright (c) 2021 Friedt Professional Engineering Services, Inc
# SPDX-License-Identifier: MIT

"""Workaround for Section-Name Limits in the Mach-O Binary Format

"""

import argparse
import io
import shutil

from machotools.machofile import MachOFile
from machotools.enums import *


class ZMachoTuple(object):

    @staticmethod
    def get_text_string(file, text, text_offset, ptr):
        s = ''
        orig_offset = file.tell()

        string_offset = ptr - text._vmaddr
        file.seek(string_offset, io.SEEK_SET)

        while True:
            ch = file.read(1).decode('utf-8')
            if ch == '\0':
                break
            s += ch

        file.seek(orig_offset, io.SEEK_SET)
        return s

    def __init__(self, file, mf):
        self._mf = mf
        n = 8 if mf.is_64() else 4
        order = mf.order()

        text = None
        text_offset = None
        for offset, lc in mf._load_commands.items():
            if lc._cmd == LCCommand.LC_SEGMENT_64 and lc._segname == '__TEXT':
                text = lc
                text_offset = offset

        self._name_p = int.from_bytes(file.read(n), order)
        self._elf_section_name = ZMachoTuple.get_text_string(
            file, text, text_offset, self._name_p)
        self._symbol_value = int.from_bytes(file.read(n), order)
        self._symbol_size = int.from_bytes(file.read(n), order)

    def __str__(self):
        return f'name: {self._elf_section_name}, value: {self._symbol_value:x}, size: {self._symbol_size}'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input',
                        help='input file', metavar='FILE', required=True)
    parser.add_argument('-o', '--output', dest='output',
                        help='output file', metavar='FILE', required=True)
    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    mf = MachOFile(args.input)
    print(f'{mf._header}')

    sect = None
    sections = mf.sections()

    for sym in mf.symtab():
        #print(f'sym: {sym}')
        if sections[sym._n_sect - 1]._sectname == 'z_macho_map':
            sect = sections[sym._n_sect - 1]
            n_sect = sym._n_sect - 1

    if sect:
        z_macho_tuples = []
        with open(args.input, 'rb') as file:
            file.seek(sect._offset, io.SEEK_CUR)
            n = 8 if mf.is_64() else 4
            order = mf.order()
            ntuples = int(sect._size / (3 * n))
            for i in range(0, ntuples):
                z_macho_tuples.append(ZMachoTuple(file, mf))

        for tup in z_macho_tuples:
            print(f'z_macho_tuple: {tup}')

    # TODO: replace later
    shutil.copy(args.input, args.output)


if __name__ == '__main__':
    main()
