# Copyright (c) 2021 Friedt Professional Engineering Services, Inc
# SPDX-License-Identifier: MIT

import io

from machotools.enums import *
from machotools.segments import *
from machotools.structs import *
from machotools.util import align_up

# The load commands directly follow the mach_header.  The total size of all
# of the commands is given by the sizeofcmds field in the mach_header.  All
# load commands must have as their first two fields cmd and cmdsize.  The cmd
# field is filled in with a constant for that command type.  Each command type
# has a structure specifically for it.  The cmdsize field is the size in bytes
# of the particular load command structure plus anything that follows it that
# is a part of the load command(i.e. section structures, strings, etc.).  To
# advance to the next load command the cmdsize can be added to the offset or
# pointer of the current load command.  The cmdsize for 32-bit architectures
# MUST be a multiple of 4 bytes and for 64-bit architectures MUST be a multiple
# of 8 bytes(these are forever the maximum alignment of any load commands).
# The padded bytes must be zero.  All tables in the object file must also
# follow these rules so the file can be memory mapped.  Otherwise the pointers
# to these tables will not work well or at all on some machines.  With all
# padding zeroed like objects will compare byte for byte.


class LCGeneric(object):
    def __init__(self, cmd, file, order):
        self._cmd = cmd
        self._cmdsize = int.from_bytes(file.read(4), order)
        file.seek(self._cmdsize - 8, io.SEEK_CUR)

    def __repr__(self):
        return '{' f'cmd: {self._cmd}, cmdsize: {self._cmdsize}' '}'


class LCSymTab(object):
    def __init__(self, file, order, n):
        self._cmd = LCCommand.LC_SYMTAB
        self._cmdsize = int.from_bytes(file.read(4), order)
        self._symoff = int.from_bytes(file.read(4), order)
        self._nsyms = int.from_bytes(file.read(4), order)
        self._stroff = int.from_bytes(file.read(4), order)
        self._strsize = int.from_bytes(file.read(4), order)
        # parse symbol table and then return to original offset
        origin = file.tell()
        offset = self._symoff
        file.seek(offset, io.SEEK_SET)
        values = set()
        symtab = []
        strtab = dict()
        for i in range(0, self._nsyms):
            sym = NList(file, order, self._stroff) if n == 4 else NList64(
                file, order, self._stroff)
            if sym._n_value in values:
                continue
            values.add(sym._n_value)
            symtab.append(sym)
            strtab[self._stroff + sym._n_strx] = sym._n_name
        file.seek(origin, io.SEEK_SET)
        self._symtab = symtab
        self._strtab = strtab

    def __repr__(self):
        return '{' f'cmd: {self._cmd}, cmdsize: {self._cmdsize} symoff: {self._symoff:08x} nsyms: {self._nsyms} stroff: {self._stroff:08x} strsize: {self._strsize}' '}'


class LoadCommand(object):
    # @staticmethod
    def parse(file, order, n):
        cmd = LCCommand(int.from_bytes(file.read(4), order))

        if cmd == LCCommand.LC_SEGMENT:
            return LCSegment(file, order)
        if cmd == LCCommand.LC_SEGMENT_64:
            return LCSegment64(file, order)
        if cmd == LCCommand.LC_SYMTAB:
            return LCSymTab(file, order, n)

        return LCGeneric(cmd, file, order)
