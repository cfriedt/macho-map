/*
 * Copyright (c) 2021 Friedt Professional Engineering Services, Inc
 *
 * SPDX-License-Identifier: MIT
 */

#pragma once

#define D(fmt, args...) printk("%s(): " fmt "\n", __func__, ##args)
