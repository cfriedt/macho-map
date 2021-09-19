# Copyright (c) 2021 Friedt Professional Engineering Services, Inc
# SPDX-License-Identifier: MIT

import io

from machotools.util import align_up
from machotools.enums import *


class SSectionCommon(object):
    def __init__(self, n, file, order):
        self._sectname = file.read(16).decode('utf-8').replace('\0', '')
        self._segname = file.read(16).decode('utf-8').replace('\0', '')
        self._addr = int.from_bytes(file.read(n), order)
        self._size = int.from_bytes(file.read(n), order)
        self._offset = int.from_bytes(file.read(4), order)
        self._align = int.from_bytes(file.read(4), order)
        self._reloff = int.from_bytes(file.read(4), order)
        self._nreloc = int.from_bytes(file.read(4), order)

        self._flags = set()
        flags = int.from_bytes(file.read(4), order)
        self._flags.add(SectionType(
            SectionFlagMask.SECTION_TYPE.value & flags))
        for e in SectionAttribute:
            if flags & e.value:
                self._flags.add(e)

        self._reserved1 = int.from_bytes(file.read(4), order)
        self._reserved2 = int.from_bytes(file.read(4), order)
        if n == 8:
            self._reserved3 = int.from_bytes(file.read(4), order)

        pad = align_up(file.tell(), n) - file.tell()
        file.seek(pad, io.SEEK_CUR)

    def __repr__(self):
        # TODO: would be great if all classes were JSON serializable / deserializable
        # return json.dumps(self.__dict__, sort_keys=True)
        return '{' f'sectname: {self._sectname}, segname: {self._segname}, addr: {self._addr:x}, size: {self._size}, offset: {self._offset}, align: {self._align}, reloff: {self._reloff}, nreloc: {self._nreloc}, flags: {self._flags}, reserved1: {self._reserved1}, reserved2: {self._reserved2}' '}'


class SSection(SSectionCommon):
    def __init__(self, file, order):
        super().__init__(4, file, order)


class SSection64(SSectionCommon):
    def __init__(self, file, order):
        super().__init__(8, file, order)
