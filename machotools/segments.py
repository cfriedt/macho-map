# Copyright (c) 2021 Friedt Professional Engineering Services, Inc
# SPDX-License-Identifier: MIT

import io

from machotools.enums import *
from machotools.sections import *


class LCSegmentCommon(object):
    def __init__(self, cmd, file, order):
        self._cmd = cmd
        n = 4 if cmd == LCCommand.LC_SEGMENT else 8
        self._cmdsize = int.from_bytes(file.read(4), order)
        self._segname = file.read(16).decode('utf-8').replace('\0', '')
        self._vmaddr = int.from_bytes(file.read(n), order)
        self._vmsize = int.from_bytes(file.read(n), order)
        self._fileoff = int.from_bytes(file.read(n), order)
        self._filesize = int.from_bytes(file.read(n), order)
        self._maxprot = int.from_bytes(file.read(4), order)
        self._initprot = int.from_bytes(file.read(4), order)
        self._nsects = int.from_bytes(file.read(4), order)

        self._flags = set()
        flags = int.from_bytes(file.read(4), order)  # flags
        for e in SGFlag:
            if flags & e.value:
                self._flags.add(e)

        sects = dict()
        for j in range(0, self._nsects):
            offset = file.tell()
            sect = SSection(file, order) if n == 4 else SSection64(file, order)
            sects[offset] = sect

        self._sects = sects

    def __repr__(self):
        # TODO: would be great if all classes were JSON serializable / deserializable
        # return json.dumps(self.__dict__, sort_keys=True)
        return '{' f'cmd: {self._cmd}, cmdsize: {self._cmdsize}, segname: {self._segname}, vmaddr: {self._vmaddr:x}, vmsize: {self._vmsize:x}, fileoff: {self._fileoff}, filesize: {self._filesize}, maxprot: {self._maxprot}, initprot: {self._initprot}, nsects: {self._nsects}, flags: {self._flags}' '}'


class LCSegment(LCSegmentCommon):
    def __init__(self, file, order):
        super().__init__(LCCommand.LC_SEGMENT, file, order)


class LCSegment64(LCSegmentCommon):
    def __init__(self, file, order):
        super().__init__(
            LCCommand.LC_SEGMENT_64, file, order)
