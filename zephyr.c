/*
 * Copyright (c) 2021 Friedt Professional Engineering Services, Inc
 *
 * SPDX-License-Identifier: MIT
 */

#include <errno.h>
#include <pthread.h>
#include <soc.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/util.h>
#include <unistd.h>
#include <zephyr.h>

static void *thread_wrapper(void *arg)
{
    struct _static_thread_data td;
    struct _static_thread_data *_tdata = (struct _static_thread_data *)arg;
    bool *done = (bool *)&_tdata->init_stack;

    memcpy(&td, _tdata, sizeof(td));
    *done = true;

    if (td.init_delay != K_FOREVER)
    {
        k_msleep(td.init_delay);

        // D("ENTER: %s", td.init_name);
        td.init_entry(td.init_p1, td.init_p2, td.init_p3);
        // D("EXIT: %s", td.init_name);
    }

    return NULL;
}

int k_msleep(int ms)
{
    int r = usleep(ms * 1000);
    if (r == -1)
    {
        D("usleep() failed: %d", errno);
        return -errno;
    }

    return 0;
}

static k_tid_t k_thread_create_static(struct k_thread *new_thread, struct _static_thread_data *thread_data)
{
    int rv;
    volatile bool *done = (volatile bool *)&thread_data->init_stack;

    rv = pthread_create((pthread_t *)new_thread, NULL, thread_wrapper, thread_data);
    if (rv != 0)
    {
        D("pthread_create() failed: %d", rv);
        return NULL;
    }

    for (; !*done;)
    {
        k_msleep(1);
    }

    return new_thread;
}

k_tid_t k_thread_create(struct k_thread *new_thread, k_thread_stack_t *stack, size_t stack_size, k_thread_entry_t entry, void *p1, void *p2, void *p3, int prio, uint32_t options, k_timeout_t delay)
{
    struct _static_thread_data _tdata = {
        .init_stack = stack,
        .init_stack_size = stack_size,
        .init_entry = entry,
        .init_p1 = p1,
        .init_p2 = p2,
        .init_p3 = p3,
        .init_prio = prio,
        .init_options = options,
        .init_delay = delay,
        .init_name = "non-static thread",
    };

    return k_thread_create_static(new_thread, &_tdata);
}

int k_thread_join(struct k_thread *thread, k_timeout_t timeout)
{
    int r;
    void *unused;

    r = pthread_join(*((pthread_t *)thread), &unused);
    if (r != 0)
    {
        D("pthread_join() failed: %d", r);
        return -r;
    }

    return 0;
}

static void run_native_tasks(int level)
{
    STRUCT_SECTION_FOREACH(native_task, it)
    {
        if (it->native_level == level)
        {
            it->task_function();
        }
    }
}

static int compare_native_tasks(const void *a, const void *b)
{
    const struct native_task *aa = (const struct native_task *)a;
    const struct native_task *bb = (const struct native_task *)b;

    if (aa->native_level < bb->native_level)
    {
        return -1;
    }
    else if (aa->native_level > bb->native_level)
    {
        return 1;
    }

    if (aa->priority < bb->priority)
    {
        return -1;
    }
    else if (aa->priority > bb->priority)
    {
        return 1;
    }

    return 0;
}

static void premain(void)
{

    /* for macOS / native_posix_64 */
    macho_map();

    /* declare compatible _start[] and _end[] */
    STRUCT_SECTION_FOREACH(native_task, it);

    qsort(_native_task_list_start, (_native_task_list_end - _native_task_list_start),
          sizeof(struct native_task), compare_native_tasks);

    run_native_tasks(_NATIVE_PRE_BOOT_1_LEVEL);
    // native_handle_cmd_line(argc, argv);
    run_native_tasks(_NATIVE_PRE_BOOT_2_LEVEL);
    // hwm_init();
    run_native_tasks(_NATIVE_PRE_BOOT_3_LEVEL);
    // posix_boot_cpu();
    run_native_tasks(_NATIVE_FIRST_SLEEP_LEVEL);

    _FOREACH_STATIC_THREAD(thread_data)
    {
        if (thread_data->init_delay != K_FOREVER)
        {
            k_tid_t tid = k_thread_create_static((struct k_thread *)thread_data->init_abort, thread_data);
            __ASSERT(tid != NULL, "k_thread_create() failed");
        }
    }
}

#undef main

int main(int argc, char *argv[])
{
    extern void fake_main(void);

    premain();
    fake_main();

    return 0;
}
