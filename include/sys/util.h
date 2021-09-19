/*
 * Copyright (c) 2021 Friedt Professional Engineering Services, Inc
 *
 * SPDX-License-Identifier: MIT
 */

#pragma once

#define BIT(n) (1UL << (n))
#define ARRAY_SIZE(x) (sizeof(x) / sizeof((x)[0]))
#define BUILD_ASSERT(x, msg) _Static_assert((x) && msg)