#!/usr/bin/env python3
# Copyright (c) 2021 Friedt Professional Engineering Services, Inc
# SPDX-License-Identifier: MIT

import argparse
import io
#import shutil

from machotools.machofile import MachOFile
from machotools.enums import *


def get_text_string(file, text, ptr):
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


def get_offset_string(file, offs):
    s = ''
    orig_offset = file.tell()

    file.seek(offs, io.SEEK_SET)

    while True:
        ch = file.read(1).decode('utf-8')
        if ch == '\0':
            break
        s += ch

    file.seek(orig_offset, io.SEEK_SET)
    return s


def get_bytes_at(file, offs, size):
    orig_offset = file.tell()

    file.seek(offs, io.SEEK_SET)
    data = file.read(size)

    file.seek(orig_offset, io.SEEK_SET)

    return data


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input',
                        help='input file', metavar='FILE', required=True)
    parser.add_argument('-o', '--output', dest='output',
                        help='output file', metavar='FILE', required=True)
    args = parser.parse_args()

    return args


def gen_getter(output, names, type, fname):
    output.write(
        f'static {type} *get_{fname}(const char *section_name)\n')
    output.write('{\n')
    output.write('\tif (false) {\n')
    for name in names:
        output.write(
            f'\t\t}} else if (0 == strcmp("{name}", section_name)) {{\n')
        output.write(f'\t\t\treturn _{name}_{fname};\n')
    output.write('\t}\n')
    output.write(f'\treturn NULL;\n')
    output.write('}\n')
    output.write('\n')


def gen_map(mf, input, output):

    names = set()
    counts = dict()
    sizes = dict()
    sections = mf.sections()
    macho_map_syms = []

    for sym in mf.symtab():
        sect = sections[sym._n_sect - 1]
        if sect._sectname == 'z_macho_map' and NLType.N_SECT in sym._n_type:
            macho_map_syms.append(sym)

    for sym in macho_map_syms:
        sect = sections[sym._n_sect - 1]
        symoffs = sym._n_value - sect._addr + sect._offset
        n = 8 if mf._header.is_64() else 4
        input.seek(symoffs, io.SEEK_SET)
        # FIXME: this ~0x30000000000000 (BIT(54) | BIT(53)) is kind of puzzling
        mask = (1 << 53) | (1 << 52)
        namep = int.from_bytes(input.read(n), mf.order()) & ~mask
        addr = int.from_bytes(input.read(n), mf.order()) & ~mask
        size = int.from_bytes(input.read(n), mf.order())
        name = get_offset_string(input, namep)

        #data = get_bytes_at(input, addr, size)

        names.add(name)
        if name in counts.keys():
            counts[name] += 1
            assert sizes[name] == size
        else:
            counts[name] = 1
            sizes[name] = size

    for name in names:
        # cannot simply copy bytes out of macho-o file because relocations still need to happen at runtime
        output.write('__attribute__((used,aligned(16)))\n')
        output.write(
            f'uint8_t _{name}_list_start[{counts[name] * sizes[name]}] = {{0}};\n')
        output.write(
            f'uint8_t _{name}_list_end[0] = {{}};\n')

    # generate list offsets
    for name in names:
        output.write('__attribute__((used))\n')
        output.write(f'static size_t _{name}_list_offset[1];\n')
    output.write('\n')

    # generate get_list_start(), get_list_end(), get_list_offset()
    gen_getter(output, names, 'uint8_t', 'list_start')
    gen_getter(output, names, 'uint8_t', 'list_end')
    gen_getter(output, names, 'size_t', 'list_offset')


def main():
    args = parse_args()

    mf = MachOFile(args.input)

    with open(args.input, 'rb') as input:
        with open(args.output, 'w') as output:
            gen_map(mf, input, output)


if __name__ == '__main__':
    main()

# void macho_map(void)
# {
#     extern struct z_macho_map section_start[] __asm("section$start$" MACHO_MAP_SEGMENT "$" MACHO_MAP_SECTION);
#     extern struct z_macho_map section_stop[] __asm("section$end$" MACHO_MAP_SEGMENT "$" MACHO_MAP_SECTION);

#     for (struct z_macho_map *mm = section_start; mm < section_stop; ++mm)
#     {
#         D("mm: elf_section_name: '%s' addr: %p size: %zu", mm->elf_section_name, mm->symbol_addr, mm->symbol_size);
#     }
# }
