/*
 * Copyright (c) 2017 Oticon A/S
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include <zephyr.h>

#define _NATIVE_PRE_BOOT_1_LEVEL 0
#define _NATIVE_PRE_BOOT_2_LEVEL 1
#define _NATIVE_PRE_BOOT_3_LEVEL 2
#define _NATIVE_FIRST_SLEEP_LEVEL 3
#define _NATIVE_ON_EXIT_LEVEL 4

struct native_task
{
    void (*task_function)(void);
    int native_level;
    int priority;
};

#define NATIVE_TASK(fn, level, prio)                    \
    STRUCT_SECTION_ITERABLE(native_task, fn##_task) = { \
        .task_function = fn,                            \
        .native_level = _NATIVE_##level##_LEVEL,        \
        .priority = prio,                               \
    }

#define main fake_main