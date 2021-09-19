# Copyright (c) 2021 Friedt Professional Engineering Services, Inc
# SPDX-License-Identifier: MIT

def align_up(value, align):
    rem = value % align
    if rem == 0:
        return value
    pad = align - rem
    return value + pad
