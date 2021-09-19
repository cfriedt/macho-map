# Copyright (c) 2021 Friedt Professional Engineering Services, Inc
# SPDX-License-Identifier: MIT

import collections
import io

from machotools.enums import *
from machotools.structs import MachHeader
from machotools.loadcommand import LoadCommand
from machotools.util import align_up


class MachOFile(object):
    def __init__(self, input_file_name=None):
        self._sections = None
        self._symtab = None
        self._strtab = None
        self._text = None
        if input_file_name:
            self.parse(input_file_name)

    def parse(self, input_file_name):
        with open(input_file_name, 'rb') as f:
            self._header = MachHeader(f)
            align = self._header.align()
            pad = align_up(f.tell(), align) - f.tell()
            f.seek(pad, io.SEEK_CUR)

            lcs = dict()
            n = 8 if self._header.is_64() else 4
            for i in range(0, self._header._ncmds):
                offset = f.tell()
                lc = LoadCommand.parse(f, self._header.order(), n)
                lcs[offset] = lc
                offset = f.tell()
                pad = align_up(offset, align) - offset
                f.seek(pad, io.SEEK_CUR)

            self._load_commands = lcs

    def sections(self):
        if not self._sections:
            self._sections = []
            for offset, lc in self._load_commands.items():
                if not (lc._cmd == LCCommand.LC_SEGMENT or lc._cmd == LCCommand.LC_SEGMENT_64):
                    continue
                for s in lc._sects.values():
                    self._sections.append(s)
        return self._sections

    def symtab(self):
        if not self._symtab:
            for offset, lc in self._load_commands.items():
                if lc._cmd == LCCommand.LC_SYMTAB:
                    self._symtab = lc._symtab
                    break
        return self._symtab

    def strtab(self):
        if not self._strtab:
            for offset, lc in self._load_commands.items():
                if lc._cmd == LCCommand.LC_SYMTAB:
                    self._strtab = lc._strtab
                    break
        return self._strtab

    def is_64(self) -> bool:
        return self._header.is_64()

    def order(self):
        return self._header.order()

    def get_text_segment(self):
        if not self._text:
            for offset, lc in self._load_commands.items():
                if lc._cmd == LCCommand.LC_SEGMENT_64 and lc._segname == '__TEXT':
                    self._text = lc
                    break

            if not self._text:
                raise ValueError('did not find a __TEXT segment!')

        return self._text

    def __repr__(self):
        return '{' f'header: {self._header}, lc: {self._load_commands}' '}'
