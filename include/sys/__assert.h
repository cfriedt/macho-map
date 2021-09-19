/*
 * Copyright (c) 2021 Friedt Professional Engineering Services, Inc
 *
 * SPDX-License-Identifier: MIT
 */

#pragma once

#include <assert.h>
#include <sys/printk.h>

#define __ASSERT(x, fmt, args...)                                    \
    do                                                               \
    {                                                                \
        if (!(x))                                                    \
        {                                                            \
            printk("%s: %d: " fmt "\n", __FILE__, __LINE__, ##args); \
        }                                                            \
        assert(x);                                                   \
    } while (0)
#define __ASSERT_NO_MSG(x) assert(x)
