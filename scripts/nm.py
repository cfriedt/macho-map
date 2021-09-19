#!/usr/bin/env python3
# Copyright (c) 2021 Friedt Professional Engineering Services, Inc
# SPDX-License-Identifier: MIT

import argparse
import collections
import magic
import re

from machotools.enums import *
from machotools.machofile import MachOFile


class add_files(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):

        # Modify value of "input" in the namespace
        if hasattr(namespace, 'files'):
            current_values = getattr(namespace, 'files')
            try:
                current_values.extend(values)
            except AttributeError:
                current_values = values
            finally:
                setattr(namespace, 'files', current_values)
        else:
            setattr(namespace, 'files', values)


def parse_args():
    # https://www.unix.com/man-page/osx/1/nm/
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', dest='a', action="store_true",
                        help='Display all symbol table entries, including those inserted for use by debuggers.')
    parser.add_argument('-g', dest='g', action="store_true",
                        help='Display only global (external) symbols.')
    parser.add_argument(
        '-n', dest='n', action="store_true", help='Sort numerically rather than alphabetically.')
    parser.add_argument(
        '-o', dest='o', action="store_true", help='Prepend file or archive element name to each output line, rather than only once.')
    parser.add_argument(
        '-p', dest='p', action="store_true", help="Don't sort display in symbol-table order.")
    parser.add_argument('-r', dest='r', action="store_true",
                        help='Sort in reverse order.')
    parser.add_argument(
        '-u', dest='u', action="store_true", help=' Display only undefined symbols.')
    parser.add_argument('-m', dest='m', action="store_true", help='Display  the  N_SECT  type  symbols (Mach-O symbols) as (segment_name, section_name) followed by either external or non-external and then the symbol name.  Undefined, common, absolute and indirect symbols get displayed  as  (undefined),  (common),  (absolute),  and (indirect), respectively.')
    parser.add_argument(
        '-x', dest='x', action="store_true", help="Display the symbol table entry's fields in hexadecimal, along with the name as a string.")
    parser.add_argument(
        '-j', dest='j', action="store_true", help='Just display the symbol names (no value or type).')
    parser.add_argument('-s', dest='s', metavar='segname sectname',
                        help='List only those symbols in the section (segname,sectname).')
    parser.add_argument(
        '-l', dest='l', action="store_true", help=' List  a  pseudo  symbol .section_start if no symbol has as its value the starting address of the section.  (This is used with the -s option above.)')
    parser.add_argument('-arch', dest='arch', metavar='arch_type', help='Specifies the architecture, arch_type, of the file for nm(1) to operate on when the file is a universal file (see  arch(3)  for  the currently known arch_types).  The arch_type can be "all" to operate on all architectures in the file.  The default is to display the symbols from only the host architecture, if the file contains it; otherwise, symbols for all architectures  in  the  file  are  displayed.')
    parser.add_argument(
        '-f', dest='f', action="store_true", help='Display the symbol table of a dynamic library flat (as one file not separate modules).')
    parser.add_argument(
        '-A', dest='A', action="store_true", help='Write the pathname or library name of an object on each line.')
    parser.add_argument(
        '-P', dest='P', action="store_true", help='Write information in a portable output format.')
    parser.add_argument('-t', dest='t', metavar='format', help='For  the -P output, write the numeric value in the specified format. The format shall be dependent on the single character used as the format option-argument:\nd:\tThe value shall be written in decimal (default).\no:The value shall be written in octal.\nx:\tThe value shall be written in hexadecimal.')

    parser.add_argument('file', nargs='*', action=add_files)

    args = parser.parse_args()

    if not args.files:
        args.files = ['a.out']

    return args


def charcode(sect, sym):
    code = '?'

    if NLType.N_UNDF in sym._n_type:
        code = 'u'
    elif sect._segname == '__TEXT':
        code = 't'
    elif SectionType.S_ZEROFILL in sect._flags:
        code = 'b'
    elif NLType.N_ABS in sym._n_type:
        code = 'a'
    elif sect._segname == '__common':
        code = 'd'
    else:
        code = 'd'

    if NLTypeMask.N_EXT in sym._n_type or NLStab.N_GSYM in sym._n_type:
        code = code.upper()

    return code


def nm(args, filename):
    mf = MachOFile(filename)
    sections = mf.sections()

    sorted_syms = sorted(
        mf.symtab(), key=lambda sym: sym._n_value if args.n else sym._n_name)
    for sym in sorted_syms:

        if not args.a:
            skippable = (NLStab.N_SO, NLStab.N_OSO, NLStab.N_BNSYM)
            if sym._n_type.intersection(skippable):
                continue

        sect = sections[sym._n_sect - 1]

        if sym._n_name == '':
            # i guess these are binary (unnamed) symbols?
            continue

        code = charcode(sect, sym)
        value = ' ' * 16 if code == 'U' else f'{sym._n_value:016x}'
        print(f'{value} {code} {sym._n_name}')


def main():
    args = parse_args()

    for fn in args.files:
        # some inputs may be .a files
        # some may be lib.a(foo.o) references
        # need to account for those too
        nm(args, fn)


if __name__ == '__main__':
    main()
