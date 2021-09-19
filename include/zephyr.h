/*
 * Copyright (c) 2015 Intel Corporation
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <stdint.h>
#include <sys/__assert.h>
#include <sys/printk.h>
#include <sys/debug.h>
#include <unistd.h>

#define _CONCAT(x, y) x##y
#define _CONCAT2(x, y) _CONCAT(x, y)
#define STRINGIFY(x) #x

#if defined(__APPLE__) && defined(__MACH__)
#include <sys/macho_map.h>
#define __z_section(x) __attribute__((used, section("__RODATA,z_sad_mac")))
#define ___in_section(a, b, c) __attribute__((used, section("__DATA,z_sad_mac")))
#define UNIQUE_STRUCT(struct_type) struct struct_type _CONCAT2(struct_type##_, __COUNTER__)
#define __z_macho_map(sect, ptr)                                            \
	__attribute__((used, section(MACHO_MAP_SEGMENT "," MACHO_MAP_SECTION))) \
	__used static const UNIQUE_STRUCT(z_macho_map) = {                      \
		.elf_section_name = sect,                                           \
		.symbol_addr = (void *)ptr,                                         \
		.symbol_size = sizeof(*(ptr)),                                      \
	}
#else
#define ___in_section(a, b, c) \
	__attribute__((section(STRINGIFY(a) "_" STRINGIFY(b) "_" STRINGIFY(c))))
#define __z_section(x) __attribute__((__section__(x)))
#define __z_macho_map(sect, ptr)
#endif

#define __in_section(a, b, c) ___in_section(a, b, c)
#define __in_section_unique(seg) ___in_section(seg, __FILE__, __COUNTER__)
#define __stackmem __z_section("stackmem")

typedef void (*k_thread_entry_t)(void *p1, void *p2, void *p3);

struct k_thread
{
	unsigned long reserved;
};

typedef struct k_thread *k_tid_t;

struct z_thread_stack_element
{
	uint8_t *data;
};

typedef struct z_thread_stack_element k_thread_stack_t;

typedef int k_timeout_t;

#define Z_KERNEL_STACK_OBJ_ALIGN 16
#define Z_KERNEL_STACK_SIZE_ADJUST(size) size

#ifndef __used
#define __used __attribute__((used))
#endif

#ifndef __weak
#define __weak __attribute__((weak))
#endif

#define __aligned(x) __attribute__((__aligned__(x)))

#define _SYS_INIT_LEVEL_PRE_KERNEL_1 0
#define _SYS_INIT_LEVEL_PRE_KERNEL_2 1
#define _SYS_INIT_LEVEL_POST_KERNEL 2
#define _SYS_INIT_LEVEL_APPLICATION 3

#define K_NO_WAIT 0
#define K_FOREVER -1
#define K_MSEC(x) x

#define STRUCT_SECTION_FOREACH(struct_type, iterator)                 \
	extern struct struct_type _CONCAT(_##struct_type, _list_start)[]; \
	extern struct struct_type _CONCAT(_##struct_type, _list_end)[];   \
	for (struct struct_type *iterator =                               \
			 _CONCAT(_##struct_type, _list_start);                    \
		 ({ __ASSERT(iterator <= _CONCAT(_##struct_type, _list_end), \
                         "unexpected list end location"); \
                iterator < _CONCAT(_##struct_type, _list_end); });                                                       \
		 iterator++)

#define _FOREACH_STATIC_THREAD(thread_data) \
	STRUCT_SECTION_FOREACH(_static_thread_data, thread_data)

#define Z_THREAD_STACK_DEFINE_IN(sym, size, lsect) \
	struct z_thread_stack_element lsect            \
	__aligned(Z_KERNEL_STACK_OBJ_ALIGN)            \
		sym[Z_KERNEL_STACK_SIZE_ADJUST(size)]

#define K_THREAD_STACK_DEFINE(sym, size) \
	Z_THREAD_STACK_DEFINE_IN(sym, size, __stackmem)

struct _static_thread_data
{
	struct k_thread *init_thread;
	k_thread_stack_t *init_stack;
	size_t init_stack_size;
	k_thread_entry_t init_entry;
	void *init_p1;
	void *init_p2;
	void *init_p3;
	int init_prio;
	uint32_t init_options;
	int32_t init_delay;
	void (*init_abort)(void);
	const char *init_name;
};

#define Z_THREAD_INITIALIZER(thread, stack, stack_size,          \
							 entry, p1, p2, p3,                  \
							 prio, options, delay, abort, tname) \
	{                                                            \
		.init_thread = (thread),                                 \
		.init_stack = (stack),                                   \
		.init_stack_size = (stack_size),                         \
		.init_entry = (k_thread_entry_t)entry,                   \
		.init_p1 = (void *)p1,                                   \
		.init_p2 = (void *)p2,                                   \
		.init_p3 = (void *)p3,                                   \
		.init_prio = (prio),                                     \
		.init_options = (options),                               \
		.init_abort = (void (*)(void))(abort),                   \
		.init_name = STRINGIFY(tname),                           \
	}

#define STRUCT_SECTION_ITERABLE(struct_type, name) \
	struct struct_type name;                       \
	__z_macho_map(STRINGIFY(struct_type), &name);  \
	struct struct_type                             \
		name                                       \
		__z_section(STRINGIFY(struct_type))        \
			__used

#define K_THREAD_DEFINE(name, stack_size,                                 \
						entry, p1, p2, p3,                                \
						prio, options, delay)                             \
	K_THREAD_STACK_DEFINE(_k_thread_stack_##name, stack_size);            \
	struct k_thread _k_thread_obj_##name;                                 \
	STRUCT_SECTION_ITERABLE(_static_thread_data, _k_thread_data_##name) = \
		Z_THREAD_INITIALIZER(&_k_thread_obj_##name,                       \
							 _k_thread_stack_##name, stack_size,          \
							 entry, p1, p2, p3, prio, options, delay,     \
							 &_k_thread_obj_##name, name);                \
	const k_tid_t name = (k_tid_t)&_k_thread_obj_##name

#define Z_INIT_ENTRY_DEFINE(_entry_name, _init_fn, _device, _level, _prio) \
	static const Z_DECL_ALIGN(struct init_entry)                           \
		_CONCAT(__init_, _entry_name) __used                               \
			__z_section(".z_init_" #_level STRINGIFY(_prio) "_") = {       \
				.init = (_init_fn),                                        \
				.dev = (_device),                                          \
	};                                                                     \
	__z_macho_map(".z_init_" #_level STRINGIFY(_prio) "_", &_CONCAT(__init_, _entry_name))

int k_msleep(int ms);
k_tid_t k_thread_create(struct k_thread *new_thread, k_thread_stack_t *stack, size_t stack_size, k_thread_entry_t entry, void *p1, void *p2, void *p3, int prio, uint32_t options, k_timeout_t delay);
int k_thread_join(struct k_thread *thread, k_timeout_t timeout);
