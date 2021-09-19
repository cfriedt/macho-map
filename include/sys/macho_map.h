/*
 * Copyright (c) 2021 Friedt Professional Engineering Services, Inc
 *
 * SPDX-License-Identifier: MIT
 */

#pragma once

#include <stddef.h>
#include <stdint.h>

#define MACHO_MAP_SEGMENT "__RODATA"
#define MACHO_MAP_SECTION "z_macho_map"
struct z_macho_map
{
    const char *elf_section_name;
    const void *symbol_addr;
    unsigned long symbol_size;
};

#if defined(__APPLE__) && defined(__MACH__)
void macho_map(void);
void macho_map_append_to_section(const char *section_name, const void *data, size_t data_size);
#else
#define macho_map()
#endif
