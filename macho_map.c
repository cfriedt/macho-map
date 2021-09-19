/*
 * Copyright (c) 2021 Friedt Professional Engineering Services, Inc
 *
 * SPDX-License-Identifier: MIT
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <sys/macho_map.h>
#include <sys/debug.h>
#include <sys/printk.h>
#include <sys/__assert.h>

void macho_map(void)
{
    extern struct z_macho_map macho_map_section_start[] __asm("section$start$" MACHO_MAP_SEGMENT "$" MACHO_MAP_SECTION);
    extern struct z_macho_map macho_map_section_stop[] __asm("section$end$" MACHO_MAP_SEGMENT "$" MACHO_MAP_SECTION);

    for (struct z_macho_map *mm = macho_map_section_start; mm < macho_map_section_stop; ++mm)
    {
        // D("elf_section_name: '%s' addr: %p size: %zu", mm->elf_section_name, mm->symbol_addr, mm->symbol_size);
        macho_map_append_to_section(mm->elf_section_name, mm->symbol_addr, mm->symbol_size);
    }
}
