/*
 * Copyright (c) 2021 Friedt Professional Engineering Services, Inc
 *
 * SPDX-License-Identifier: MIT
 */

#include <stdbool.h>
#include <stdio.h>
#include <sys/printk.h>
#include <zephyr.h>
#include <soc.h>

#define PRIO_HIGH -1
#define PRIO_MED 0
#define PRIO_LOW 1

static bool ran[10];

static void pre_boot_1_task_high_prio(void)
{
    D("");
    ran[0] = true;
}
static void pre_boot_1_task_med_prio(void)
{
    D("");
    ran[1] = true;
}
static void pre_boot_1_task_low_prio(void)
{
    D("");
    ran[2] = true;
}

NATIVE_TASK(pre_boot_1_task_high_prio, PRE_BOOT_1, 0);
NATIVE_TASK(pre_boot_1_task_med_prio, PRE_BOOT_1, 1);
NATIVE_TASK(pre_boot_1_task_low_prio, PRE_BOOT_1, 2);

static void pre_boot_2_task(void)
{
    D("");
    ran[3] = true;
}

NATIVE_TASK(pre_boot_2_task, PRE_BOOT_2, 0);

static void pre_boot_3_task_high_prio(void)
{
    D("");
    ran[4] = true;
}
static void pre_boot_3_task_med_prio(void)
{
    D("");
    ran[5] = true;
}
static void pre_boot_3_task_low_prio(void)
{
    D("");
    ran[6] = true;
}

NATIVE_TASK(pre_boot_3_task_high_prio, PRE_BOOT_3, 0);
NATIVE_TASK(pre_boot_3_task_med_prio, PRE_BOOT_3, 1);
NATIVE_TASK(pre_boot_3_task_low_prio, PRE_BOOT_3, 2);

static void first_sleep_task(void)
{
    D("");
    ran[7] = true;
}

NATIVE_TASK(first_sleep_task, FIRST_SLEEP, 0);

static void on_exit_task(void)
{
    D("");
    ran[8] = true;
}
NATIVE_TASK(on_exit_task, ON_EXIT, 0);

static void thread1_fun(void *p1, void *p2, void *p3)
{
    D("p1: %p, p2: %p, p3: %p", p1, p2, p3);
}
K_THREAD_DEFINE(thread1, 1024, thread1_fun, (void *)1, (void *)2, (void *)3, PRIO_HIGH, 0, 0);

static void thread2_fun(void *p1, void *p2, void *p3)
{
    D("p1: %p, p2: %p, p3: %p", p1, p2, p3);
}
K_THREAD_DEFINE(thread2, 2048, thread2_fun, (void *)1, (void *)2, (void *)3, PRIO_MED, 0, 1000);

static void thread3_fun(void *p1, void *p2, void *p3)
{
    D("p1: %p, p2: %p, p3: %p", p1, p2, p3);
}
K_THREAD_DEFINE(thread3, 4096, thread3_fun, (void *)1, (void *)2, (void *)3, PRIO_LOW, 0, 2000);

void main(void)
{
    // ensure that each task (except for the on_exit task) ran before main()
    for (int i = 0; i < 8; ++i)
    {
        __ASSERT_NO_MSG(ran[i]);
    }

    __ASSERT_NO_MSG(0 == k_thread_join(thread1, K_FOREVER));
    __ASSERT_NO_MSG(0 == k_thread_join(thread2, K_FOREVER));
    __ASSERT_NO_MSG(0 == k_thread_join(thread3, K_FOREVER));

    printk("SUCCESS\n");
}
