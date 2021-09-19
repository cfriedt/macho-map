# Copyright (c) 2021 Friedt Professional Engineering Services, Inc
# SPDX-License-Identifier: MIT

from enum import Enum


class MHMagic(Enum):
    # Constant for the magic field of the mach_header (32-bit architectures)
    MH_MAGIC = 0xfeedface  # the mach magic number
    MH_CIGAM = 0xcefaedfe  # NXSwapInt(MH_MAGIC)

    # Constant for the magic field of the mach_header (32-bit architectures)
    MH_MAGIC_64 = 0xfeedfacf  # the 64-bit mach magic number
    MH_CIGAM_64 = 0xcffaedfe  # NXSwapInt(MH_MAGIC_64)


class MHCpuMask(Enum):
    CPU_ARCH_MASK = 0xff000000  # mask for architecture bits
    CPU_SUBTYPE_MASK = 0xff000000  # mask for feature flags
    CPU_SUBTYPE_LIB64 = 0x80000000  # 64 bit libraries
    # pointer authentication with versioned ABI
    CPU_SUBTYPE_PTRAUTH_ABI = 0x80000000


class MHCpuType(Enum):
    CPU_ARCH_ABI64 = 0x01000000  # 64 bit ABI
    CPU_ARCH_ABI64_32 = 0x02000000  # ABI for 64-bit hardware with 32-bit types; LP32

    CPU_TYPE_ANY = -1
    CPU_SUBTYPE_ANY = -1
    CPU_SUBTYPE_MULTIPLE = -1
    CPU_SUBTYPE_LITTLE_ENDIAN = 0
    CPU_SUBTYPE_BIG_ENDIAN = 1

    CPU_TYPE_VAX = 1
    CPU_TYPE_MC680x0 = 6
    CPU_TYPE_X86 = 7
    CPU_TYPE_I386 = CPU_TYPE_X86
    CPU_TYPE_X86_64 = (CPU_TYPE_X86 | CPU_ARCH_ABI64)
    CPU_TYPE_MIPS = 8
    CPU_TYPE_MC98000 = 10
    CPU_TYPE_HPPA = 11
    CPU_TYPE_ARM = 12
    CPU_TYPE_ARM64 = (CPU_TYPE_ARM | CPU_ARCH_ABI64)
    CPU_TYPE_ARM64_32 = (CPU_TYPE_ARM | CPU_ARCH_ABI64_32)
    CPU_TYPE_MC88000 = 13
    CPU_TYPE_SPARC = 14
    CPU_TYPE_I860 = 15
    CPU_TYPE_ALPHA = 16
    CPU_TYPE_POWERPC = 18
    CPU_TYPE_POWERPC64 = (CPU_TYPE_POWERPC | CPU_ARCH_ABI64)

    # TODO: add cpusubtypes from machine.h

    # The layout of the file depends on the filetype.  For all but the MH_OBJECT
    # file type the segments are padded out and aligned on a segment alignment
    # boundary for efficient demand pageing.  The MH_EXECUTE, MH_FVMLIB, MH_DYLIB,
    # MH_DYLINKER and MH_BUNDLE file types also have the headers included as part
    # of their first segment.
    #
    # The file type MH_OBJECT is a compact format intended as output of the
    # assembler and input (and possibly output) of the link editor (the .o
    # format).  All sections are in one unnamed segment with no segment padding.
    # This format is used as an executable format when the file is so small the
    # segment padding greatly increases its size.
    #
    # The file type MH_PRELOAD is an executable format intended for things that
    # are not executed under the kernel (proms, stand alones, kernels, etc).  The
    # format can be executed under the kernel but may demand paged it and not
    # preload it before execution.
    #
    # A core file is in MH_CORE format and can be any in an arbritray legal
    # Mach-O file.


class MHFiletype(Enum):
    """ Constants for the filetype field of the mach_header
    """
    MH_OBJECT = 0x1  # relocatable object file
    MH_EXECUTE = 0x2  # demand paged executable file
    MH_FVMLIB = 0x3  # fixed VM shared library file
    MH_CORE = 0x4  # core file
    MH_PRELOAD = 0x5  # preloaded executable file
    MH_DYLIB = 0x6  # dynamically bound shared library
    MH_DYLINKER = 0x7  # dynamic link editor
    MH_BUNDLE = 0x8  # dynamically bound bundle file
    MH_DYLIB_STUB = 0x9  # shared library stub for static linking only, no section contents
    MH_DSYM = 0xa  # companion file with only debug sections
    MH_KEXT_BUNDLE = 0xb  # x86_64 kexts


class MHFlag(Enum):
    """Constants for the flags field of the mach_header
    """
    MH_NOUNDEFS = 0x1  # the object file has no undefined references
    MH_INCRLINK = 0x2  # the object file is the output of an incremental link against a base file and can't be link edited again
    # the object file is input for the dynamic linker and can't be staticly link edited again
    MH_DYLDLINK = 0x4
    # the object file's undefined references are bound by the dynamic linker when loaded
    MH_BINDATLOAD = 0x8
    MH_PREBOUND = 0x10  # the file has its dynamic undefined references prebound
    MH_SPLIT_SEGS = 0x20  # the file has its read-only and read-write segments split
    # the shared library init routine is to be run lazily via catching memory faults to its writeable segments (obsolete)
    MH_LAZY_INIT = 0x40
    MH_TWOLEVEL = 0x80  # the image is using two-level name space bindings
    # the executable is forcing all images to use flat name space bindings
    MH_FORCE_FLAT = 0x100
    MH_NOMULTIDEFS = 0x200  # this umbrella guarantees no multiple defintions of symbols in its sub-images so the two-level namespace hints can always be used
    # do not have dyld notify the prebinding agent about this executable
    MH_NOFIXPREBINDING = 0x400
    # the binary is not prebound but can have its prebinding redone. only used when MH_PREBOUND is not set
    MH_PREBINDABLE = 0x800
    MH_ALLMODSBOUND = 0x1000  # indicates that this binary binds to all two-level namespace modules of its dependent libraries. only used when MH_PREBINDABLE and MH_TWOLEVEL are both set
    # safe to divide up the sections into sub-sections via symbols for dead code stripping
    MH_SUBSECTIONS_VIA_SYMBOLS = 0x2000
    MH_CANONICAL = 0x4000  # the binary has been canonicalized via the unprebind operation
    MH_WEAK_DEFINES = 0x8000  # the final linked image contains external weak symbols
    MH_BINDS_TO_WEAK = 0x10000  # the final linked image uses weak symbols
    # When this bit is set, all stacks in the task will be given stack execution privilege.  Only used in MH_EXECUTE filetypes
    MH_ALLOW_STACK_EXECUTION = 0x20000
    # When this bit is set, the binary declares it is safe for use in processes with uid zero
    MH_ROOT_SAFE = 0x40000
    # When this bit is set, the binary declares it is safe for use in processes when issetugid() is true
    MH_SETUID_SAFE = 0x80000
    # When this bit is set on a dylib, the static linker does not need to examine dependent dylibs to see if any are re-exported
    MH_NO_REEXPORTED_DYLIBS = 0x100000
    MH_PIE = 0x200000  # When this bit is set, the OS will load the main executable at a random address.  Only used in MH_EXECUTE filetypes
    MH_DEAD_STRIPPABLE_DYLIB = 0x400000  # Only for use on dylibs.  When linking against a dylib that has this bit set, the static linker will automatically not create a LC_LOAD_DYLIB load command to the dylib if no symbols are being referenced from the dylib
    # Contains a section of type S_THREAD_LOCAL_VARIABLES
    MH_HAS_TLV_DESCRIPTORS = 0x800000
    # When this bit is set, the OS will run the main executable with a non-executable heap even on platforms(e.g. i386) that don't require it. Only used in MH_EXECUTE filetypes
    MH_NO_HEAP_EXECUTION = 0x1000000
    # The code was linked for use in an application extension
    MH_APP_EXTENSION_SAFE = 0x0200000


# After MacOS X 10.1 when a new load command is added that is required to be
# understood by the dynamic linker for the image to execute properly the
# LC_REQ_DYLD bit will be or'ed into the load command constant.  If the dynamic
# linker sees such a load command it it does not understand will issue a
# "unknown load command required for execution" error and refuse to use the
# image.  Other load commands without this bit that are not understood will
# simply be ignored.

class LCCommand(Enum):
    """Constants for the cmd field of all load commands, the type
    """

    LC_REQ_DYLD = 0x80000000

    LC_SEGMENT = 0x1  # segment of this file to be mapped
    LC_SYMTAB = 0x2  # link-edit stab symbol table info
    LC_SYMSEG = 0x3  # link-edit gdb symbol table info (obsolete)
    LC_THREAD = 0x4  # thread
    LC_UNIXTHREAD = 0x5  # unix thread (includes a stack)
    LC_LOADFVMLIB = 0x6  # load a specified fixed VM shared library
    LC_IDFVMLIB = 0x7  # fixed VM shared library identification
    LC_IDENT = 0x8  # object identification info (obsolete)
    LC_FVMFILE = 0x9  # fixed VM file inclusion (internal use)
    LC_PREPAGE = 0xa  # prepage command (internal use)
    LC_DYSYMTAB = 0xb  # dynamic link-edit symbol table info
    LC_LOAD_DYLIB = 0xc  # load a dynamically linked shared library
    LC_ID_DYLIB = 0xd  # dynamically linked shared lib ident
    LC_LOAD_DYLINKER = 0xe  # load a dynamic linker
    LC_ID_DYLINKER = 0xf  # dynamic linker identification
    LC_PREBOUND_DYLIB = 0x10  # modules prebound for a dynamically linked shared library
    LC_ROUTINES = 0x11  # image routines
    LC_SUB_FRAMEWORK = 0x12  # sub framework
    LC_SUB_UMBRELLA = 0x13  # sub umbrella
    LC_SUB_CLIENT = 0x14  # sub client
    LC_SUB_LIBRARY = 0x15  # sub library
    LC_TWOLEVEL_HINTS = 0x16  # two-level namespace lookup hints
    LC_PREBIND_CKSUM = 0x17  # prebind checksum
    # load a dynamically linked shared library that is allowed to be missing (all symbols are weak imported)
    LC_LOAD_WEAK_DYLIB = (0x18 | LC_REQ_DYLD)
    LC_SEGMENT_64 = 0x19  # 64-bit segment of this file to be mapped
    LC_ROUTINES_64 = 0x1a  # 64-bit image routines
    LC_UUID = 0x1b  # the uuid
    LC_RPATH = (0x1c | LC_REQ_DYLD)  # runpath additions
    LC_CODE_SIGNATURE = 0x1d  # local of code signature
    LC_SEGMENT_SPLIT_INFO = 0x1e  # local of info to split segments
    LC_REEXPORT_DYLIB = (0x1f | LC_REQ_DYLD)  # load and re-export dylib
    LC_LAZY_LOAD_DYLIB = 0x20  # delay load of dylib until first use
    LC_ENCRYPTION_INFO = 0x21  # encrypted segment information
    LC_DYLD_INFO = 0x22  # compressed dyld information
    # compressed dyld information only
    LC_DYLD_INFO_ONLY = (0x22 | LC_REQ_DYLD)
    LC_LOAD_UPWARD_DYLIB = (0x23 | LC_REQ_DYLD)  # load upward dylib
    LC_VERSION_MIN_MACOSX = 0x24  # build for MacOSX min OS version
    LC_VERSION_MIN_IPHONEOS = 0x25  # build for iPhoneOS min OS version
    LC_FUNCTION_STARTS = 0x26  # compressed table of function start addresses
    LC_DYLD_ENVIRONMENT = 0x27  # string for dyld to treat like environment variable
    LC_MAIN = (0x28 | LC_REQ_DYLD)  # replacement for LC_UNIXTHREAD
    LC_DATA_IN_CODE = 0x29  # table of non-instructions in __text
    LC_SOURCE_VERSION = 0x2A  # source version used to build binary
    LC_DYLIB_CODE_SIGN_DRS = 0x2B  # Code signing DRs copied from linked dylibs
    LC_ENCRYPTION_INFO_64 = 0x2C  # 64-bit encrypted segment information
    LC_LINKER_OPTION = 0x2D  # linker options in MH_OBJECT files
    LC_LINKER_OPTIMIZATION_HINT = 0x2E  # optimization hints in MH_OBJECT files
    LC_VERSION_MIN_TVOS = 0x2F  # build for AppleTV min OS version
    LC_VERSION_MIN_WATCHOS = 0x30  # build for Watch min OS version
    LC_NOTE = 0x31  # arbitrary data included within a Mach-O file
    LC_BUILD_VERSION = 0x32  # build for platform min OS version

    # used with linkedit_data_command, payload is trie
    LC_DYLD_EXPORTS_TRIE = (0x33 | LC_REQ_DYLD)
    # used with linkedit_data_command
    LC_DYLD_CHAINED_FIXUPS = (0x34 | LC_REQ_DYLD)
    LC_FILESET_ENTRY = (0x35 | LC_REQ_DYLD)  # used with fileset_entry_command


class SGFlag(Enum):
    """Constants for the flags field of the segment_command
    """
    SG_HIGHVM = 0x1  # the file contents for this segment is for the high part of the VM space, the low part is zero filled(for stacks in core files)
    SG_FVMLIB = 0x2  # this segment is the VM that is allocated by a fixed VM library, for overlap checking in the link editor
    SG_NORELOC = 0x4  # this segment has nothing that was relocated in it and nothing relocated to it, that is it maybe safely replaced without relocation
    SG_PROTECTED_VERSION_1 = 0x8  # This segment is protected.  If the segment starts at file offset 0, the first page of the segment is not protected.  All other pages of the segment are protected
    SG_READ_ONLY = 0x10  # This segment is made read-only after fixups


class SectionFlagMask(Enum):
    SECTION_TYPE = 0x000000ff  # 256 section types
    SECTION_ATTRIBUTES = 0xffffff00  # 24 section attributes
    SECTION_ATTRIBUTES_USR = 0xff000000  # User setable attributes
    SECTION_ATTRIBUTES_SYS = 0x00ffff00  # system settable attributes


class SectionType(Enum):
    """Constants for the type of a section"""
    S_REGULAR = 0x0  # regular section
    S_ZEROFILL = 0x1  # zero fill on demand section
    S_CSTRING_LITERALS = 0x2  # section with only literal C strings
    S_4BYTE_LITERALS = 0x3  # section with only 4 byte literals
    S_8BYTE_LITERALS = 0x4  # section with only 8 byte literals
    S_LITERAL_POINTERS = 0x5  # section with only pointers to literals */

    # For the two types of symbol pointers sections and the symbol stubs section
    # they have indirect symbol table entries.  For each of the entries in the
    # section the indirect symbol table entries, in corresponding order in the
    # indirect symbol table, start at the index stored in the reserved1 field
    # of the section structure.  Since the indirect symbol table entries
    # correspond to the entries in the section the number of indirect symbol table
    # entries is inferred from the size of the section divided by the size of the
    # entries in the section.  For symbol pointers sections the size of the entries
    # in the section is 4 bytes and for symbol stubs sections the byte size of the
    # stubs is stored in the reserved2 field of the section structure.

    S_NON_LAZY_SYMBOL_POINTERS = 0x6  # section with only non-lazy symbol pointers
    S_LAZY_SYMBOL_POINTERS = 0x7  # section with only lazy symbol pointers
    # section with only symbol stubs, byte size of stub in the reserved2 field
    S_SYMBOL_STUBS = 0x8
    # section with only function pointers for initialization
    S_MOD_INIT_FUNC_POINTERS = 0x9
    # section with only function pointers for termination
    S_MOD_TERM_FUNC_POINTERS = 0xa
    S_COALESCED = 0xb  # section contains symbols that are to be coalesced
    # zero fill on demand section (that can be larger than 4 gigabytes)
    S_GB_ZEROFILL = 0xc
    S_INTERPOSING = 0xd  # section with only pairs of function pointers for interposing
    S_16BYTE_LITERALS = 0xe  # section with only 16 byte literals
    S_DTRACE_DOF = 0xf  # section contains DTrace Object Format
    # section with only lazy symbol pointers to lazy loaded dylibs
    S_LAZY_DYLIB_SYMBOL_POINTERS = 0x10

    # Section types to support thread local variables
    S_THREAD_LOCAL_REGULAR = 0x11  # template of initial values for TLVs
    S_THREAD_LOCAL_ZEROFILL = 0x12  # template of initial values for TLVs
    S_THREAD_LOCAL_VARIABLES = 0x13  # TLV descriptors
    S_THREAD_LOCAL_VARIABLE_POINTERS = 0x14  # pointers to TLV descriptors
    # functions to call to initialize TLV values
    S_THREAD_LOCAL_INIT_FUNCTION_POINTERS = 0x15
    S_INIT_FUNC_OFFSETS = 0x16  # 32-bit offsets to initializers


class SectionAttribute(Enum):
    """Constants for the section attributes part of the flags field of a section structure."""
    # section contains only true machine instructions
    S_ATTR_PURE_INSTRUCTIONS = 0x80000000
    # section contains coalesced symbols that are not to be in a ranlib table of contents
    S_ATTR_NO_TOC = 0x4000000
    # ok to strip static symbols in this section in files with the MH_DYLDLINK flag
    S_ATTR_STRIP_STATIC_SYMS = 0x20000000
    S_ATTR_NO_DEAD_STRIP = 0x10000000  # no dead stripping
    S_ATTR_LIVE_SUPPORT = 0x08000000  # blocks are live if they reference live blocks
    # Used with i386 code stubs written on by dyld
    S_ATTR_SELF_MODIFYING_CODE = 0x04000000

    # If a segment contains any sections marked with S_ATTR_DEBUG then all
    # sections in that segment must have this attribute.  No section other than
    # a section marked with this attribute may reference the contents of this
    # section.  A section with this attribute may contain no symbols and must have
    # a section type S_REGULAR.  The static linker will not copy section contents
    # from sections with this attribute into its output file.  These sections
    # generally contain DWARF debugging info.

    S_ATTR_DEBUG = 0x02000000  # a debug section
    # section contains some machine instructions
    S_ATTR_SOME_INSTRUCTIONS = 0x00000400
    S_ATTR_EXT_RELOC = 0x00000200  # section has external relocation entries
    S_ATTR_LOC_RELOC = 0x00000100  # section has local relocation entries


# The n_type field really contains four fields:
#	unsigned char N_STAB:3,
#		      N_PEXT:1,
#		      N_TYPE:3,
#		      N_EXT:1;
# which are used via the following masks.

class NLTypeMask(Enum):
    N_STAB = 0xe0  # if any of these bits set, a symbolic debugging entry
    N_PEXT = 0x10  # private external symbol bit
    N_TYPE = 0x0e  # mask for the type bits
    N_EXT = 0x01  # external symbol bit, set for external symbols

# Values for N_TYPE bits of the n_type field.


class NLType(Enum):
    N_UNDF = 0x0  # undefined, n_sect == NO_SECT
    N_ABS = 0x2  # absolute, n_sect == NO_SECT
    N_SECT = 0xe  # defined in section number n_sect
    N_PBUD = 0xc  # prebound undefined (defined in a dylib)
    N_INDR = 0xa  # indirect


class NLStab(Enum):
    N_GSYM = 0x20  # global symbol: name,,NO_SECT,type,0
    N_FNAME = 0x22  # procedure name (f77 kludge): name,,NO_SECT,0,0
    N_FUN = 0x24  # procedure: name,,n_sect,linenumber,address
    N_STSYM = 0x26  # static symbol: name,,n_sect,type,address
    N_LCSYM = 0x28  # .lcomm symbol: name,,n_sect,type,address
    N_BNSYM = 0x2e  # begin nsect sym: 0,,n_sect,0,address
    N_AST = 0x32  # AST file path: name,,NO_SECT,0,0
    N_OPT = 0x3c  # emitted with gcc2_compiled and in gcc source
    N_RSYM = 0x40  # register sym: name,,NO_SECT,type,register
    N_SLINE = 0x44  # src line: 0,,n_sect,linenumber,address
    N_ENSYM = 0x4e  # end nsect sym: 0,,n_sect,0,address
    N_SSYM = 0x60  # structure elt: name,,NO_SECT,type,struct_offset
    N_SO = 0x64  # source file name: name,,n_sect,0,address
    N_OSO = 0x66  # object file name: name,,(see below),0,st_mtime
    # historically N_OSO set n_sect to 0. The N_OSO
    # n_sect may instead hold the low byte of the
    # cpusubtype value from the Mach-O header. */
    N_LSYM = 0x80  # local sym: name,,NO_SECT,type,offset
    N_BINCL = 0x82  # include file beginning: name,,NO_SECT,0,sum
    N_SOL = 0x84  # included file name: name,,n_sect,0,address
    N_PARAMS = 0x86  # compiler parameters: name,,NO_SECT,0,0
    N_VERSION = 0x88  # compiler version: name,,NO_SECT,0,0
    N_OLEVEL = 0x8A  # compiler -O level: name,,NO_SECT,0,0
    N_PSYM = 0xa0  # parameter: name,,NO_SECT,type,offset
    N_EINCL = 0xa2  # include file end: name,,NO_SECT,0,0
    N_ENTRY = 0xa4  # alternate entry: name,,n_sect,linenumber,address
    N_LBRAC = 0xc0  # left bracket: 0,,NO_SECT,nesting level,address
    N_EXCL = 0xc2  # deleted include file: name,,NO_SECT,0,sum
    N_RBRAC = 0xe0  # right bracket: 0,,NO_SECT,nesting level,address
    N_BCOMM = 0xe2  # begin common: name,,NO_SECT,0,0
    N_ECOMM = 0xe4  # end common: name,,n_sect,0,0
    N_ECOML = 0xe8  # end common (local name): 0,,n_sect,0,address
    N_LENG = 0xfe  # second stab entry with length information
