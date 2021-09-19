# Copyright (c) 2021 Friedt Professional Engineering Services, Inc
# SPDX-License-Identifier: MIT

import json
import io
import sys

from machotools.enums import *
from machotools.sections import *


class MachHeader(object):
    def __init__(self, file):
        # mach magic number identifier
        self._magic = MHMagic(int.from_bytes(file.read(4), sys.byteorder))

        order = self.order()
        self._cputype = MHCpuType(int.from_bytes(
            file.read(4), order))  # cpu specifier
        self._cpusubtype = int.from_bytes(
            file.read(4), order)  # machine specifier
        self._filetype = MHFiletype(int.from_bytes(
            file.read(4), order))  # type of file
        self._ncmds = int.from_bytes(
            file.read(4), order)  # number of load commands
        # the size of all the load commands
        self._sizeofcmds = int.from_bytes(file.read(4), order)

        self._flags = set()
        flags = int.from_bytes(file.read(4), order)  # flags
        for e in MHFlag:
            if flags & e.value:
                self._flags.add(e)

        if self._magic == MHMagic.MH_MAGIC_64 or self._magic == MHMagic.MH_CIGAM_64:
            self._reserved = int.from_bytes(file.read(4), order)

    def is_swapped(self):
        return self._magic == MHMagic.MH_CIGAM or self._magic == MHMagic.MH_CIGAM_64

    def order(self):
        order = sys.byteorder
        if self.is_swapped():
            order = 'big' if sys.byteorder == 'little' else 'big'
        return order

    def is_64(self):
        return self._magic == MHMagic.MH_CIGAM_64 or self._magic == MHMagic.MH_MAGIC_64

    def align(self):
        return 8 if self.is_64() else 4

    def __str__(self):
        return '{' f'magic: {self._magic}, cputype: {self._cputype}, cpusubtype: {self._cpusubtype}, filetype: {self._filetype}, ncmds: {self._ncmds}, sizeofcmds: {self._sizeofcmds}, flags: {self._flags}' '}'


class NListCommon(object):
    def __init__(self, file, order, stroff, n):
        self._n_strx = int.from_bytes(file.read(4), order)
        n_type = int.from_bytes(file.read(1), order)
        self._n_type = set()
        if n_type & NLTypeMask.N_STAB.value:
            self._n_type.add(NLStab(n_type))
        else:
            if n_type & NLTypeMask.N_PEXT.value:
                self._n_type.add(NLTypeMask.N_PEXT)
            self._n_type.add(NLType(n_type & NLTypeMask.N_TYPE.value))
            if n_type & NLTypeMask.N_EXT.value:
                self._n_type.add(NLTypeMask.N_EXT)

        self._n_sect = int.from_bytes(file.read(1), order)
        self._n_desc = int.from_bytes(file.read(2), order)
        self._n_value = int.from_bytes(file.read(n), order)

        offset = file.tell()
        self._n_name = ''
        file.seek(stroff + self._n_strx, io.SEEK_SET)
        while True:
            ch = file.read(1).decode('utf-8')
            if ch == '\0':
                break
            self._n_name += ch
        file.seek(offset, io.SEEK_SET)

    def __str__(self):
        name = '<binary symbol>' if not self._n_name.strip() else self._n_name
        return '{' f'n_name: {name}, n_type: {self._n_type}, n_sect: {self._n_sect}, n_desc: {self._n_desc:04x}, n_value: {self._n_value:08x}' '}'


class NList(NListCommon):
    def __init__(self, file, order, stroff):
        super().__init__(file, order, stroff, 4)


class NList64(NListCommon):
    def __init__(self, file, order, stroff):
        super().__init__(file, order, stroff, 8)
