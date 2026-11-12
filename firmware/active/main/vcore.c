/*
 * Exp011 FINAL — System / Compute Workload Isolation
 *
 * Target: ESP32-WROOM-32 (dual-core Xtensa LX6), ESP-IDF 6.1
 *
 * Purpose:
 *   Compare system-event response latency when a higher-priority compute
 *   workload shares Core 0 versus when it is pinned to Core 1.
 *
 * Task placement:
 *   System event producer: Core 0, priority 7
 *   System task:           Core 0, priority 5
 *   Compute task:          Core 0 or Core 1, priority 6
 *   Coordinator:           Core 0, priority 4
 *
 * The firmware executes four runs in ABBA order:
 *   A1 (compute on Core 0), B1 (compute on Core 1),
 *   B2 (compute on Core 1), A2 (compute on Core 0).
 *
 * ABBA ordering helps expose simple run-order/drift effects. It is not a
 * substitute for repeated independent power cycles or randomized trials.
 *
 * Primary measurement:
 *   Core 0 CCOUNT at event release (producer)
 *   to Core 0 CCOUNT after system-task processing (system task).
 *
 * The primary interval includes queue handoff, scheduling delay and the
 * deterministic system-task workload. Both timestamps are read on Core 0.
 *
 * Compute diagnostic:
 *   Each compute task also measures elapsed CCOUNT around one arithmetic
 *   chunk on its own core. These are diagnostic chunk durations, not the
 *   primary system-response measurement. They can include preemption and
 *   interrupt time on that core.
 *
 * Important:
 *   - Keep CPU frequency, compiler optimization and ESP-IDF configuration
 *     identical across runs.
 *   - CCOUNT values are cycles, not microseconds.
 *   - At 240 MHz, cycles / 240 = microseconds.
 *   - The event period is nominally 10 ms and tick-granular.
 */

#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <math.h>
#include <stdatomic.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"

/* ---------------- Experiment parameters ---------------- */

#define WARMUP_EVENTS          100
#define MEASURED_EVENTS       1000
#define TOTAL_EVENTS          (WARMUP_EVENTS + MEASURED_EVENTS)

#define EVENT_PERIOD_MS        10
#define SYSTEM_WORK_ITERS      128
#define COMPUTE_CHUNK_ITERS    16384

#define SYSTEM_CORE            0
#define PRODUCER_CORE          0
#define COMPUTE_CORE_A         0
#define COMPUTE_CORE_B         1

#define SYSTEM_PRIORITY        5
#define COMPUTE_PRIORITY       6
#define PRODUCER_PRIORITY      7
#define COORD_PRIORITY         4

#define SYSTEM_STACK_SIZE      4096
#define PRODUCER_STACK_SIZE    3072
#define COMPUTE_STACK_SIZE     3072
#define COORD_STACK_SIZE       4096

#define EVENT_QUEUE_LENGTH     4
#define SETTLE_DELAY_MS        500
#define RUN_COUNT              4

/* ---------------- Task and data state ---------------- */

static TaskHandle_t coordinator_handle = NULL;
static TaskHandle_t system_task_handle = NULL;
static TaskHandle_t producer_task_handle = NULL;
static TaskHandle_t compute_task_handle[2] = { NULL, NULL };

static QueueHandle_t event_queue = NULL;

/* Response samples are written by the Core 0 system task. */
static uint32_t response_cycles[RUN_COUNT][MEASURED_EVENTS];
static uint32_t sorted_cycles[MEASURED_EVENTS];

/*
 * Cross-core run flags: accessed by coordinator and compute tasks.
 * volatile alone is not sufficient for inter-core synchronization.
 */
static _Atomic uint32_t compute_run[2] = { 0, 0 };
static _Atomic int active_run_index = 0;

static volatile uint32_t compute_sink[2] = { 0, 0 };
static volatile uint32_t system_sink = 0;

/* Per-run compute diagnostic, published before stop notification. */
typedef struct {
    uint32_t min_cycles;
    uint32_t max_cycles;
    uint64_t sum_cycles;
    uint32_t chunks;
} ComputeDiagnostics;

static ComputeDiagnostics compute_diag[2];

/* ---------------- Low-level timer ---------------- */

static inline uint32_t read_ccount(void)
{
    uint32_t count;
    __asm__ __volatile__("rsr.ccount %0" : "=a"(count));
    return count;
}

/* ---------------- Statistics ---------------- */

static void sort_u32(uint32_t *values, int count)
{
    for (int i = 1; i < count; ++i) {
        uint32_t key = values[i];
        int j = i - 1;

        while (j >= 0 && values[j] > key) {
            values[j + 1] = values[j];
            --j;
        }

        values[j + 1] = key;
    }
}

typedef struct {
    uint32_t min;
    double mean;
    uint32_t median;
    double stddev;
    uint32_t p95;
    uint32_t p99;
    uint32_t max;
} Stats;

static Stats calculate_stats(const uint32_t *samples, int count)
{
    memcpy(sorted_cycles, samples, (size_t)count * sizeof(uint32_t));
    sort_u32(sorted_cycles, count);

    double sum = 0.0;
    for (int i = 0; i < count; ++i) {
        sum += (double)samples[i];
    }

    double mean = sum / (double)count;

    double squared_diff_sum = 0.0;
    for (int i = 0; i < count; ++i) {
        double diff = (double)samples[i] - mean;
        squared_diff_sum += diff * diff;
    }

    Stats result = {
        .min = sorted_cycles[0],
        .mean = mean,
        .median = sorted_cycles[count / 2],
        .stddev = sqrt(squared_diff_sum / (double)count),
        .p95 = sorted_cycles[((count * 95) + 99) / 100 - 1],
        .p99 = sorted_cycles[((count * 99) + 99) / 100 - 1],
        .max = sorted_cycles[count - 1],
    };

    return result;
}

static void print_response_stats(const char *label, int run_index)
{
    Stats s = calculate_stats(response_cycles[run_index],
                              MEASURED_EVENTS);

    printf("\n[%s] System response latency (Core 0 CCOUNT)\n", label);
    printf("min=%" PRIu32 ", mean=%.3f, median=%" PRIu32
           ", SD=%.3f, P95=%" PRIu32 ", P99=%" PRIu32
           ", max=%" PRIu32 " cycles\n",
           s.min, s.mean, s.median, s.stddev,
           s.p95, s.p99, s.max);

    printf("mean=%.3f us at 240 MHz | median=%.3f us at 240 MHz\n",
           s.mean / 240.0, (double)s.median / 240.0);
}

static void print_compute_diagnostics(int core)
{
    const ComputeDiagnostics *d = &compute_diag[core];

    if (d->chunks == 0) {
        printf("Compute diagnostics Core %d: no chunks recorded\n", core);
        return;
    }

    double mean = (double)d->sum_cycles / (double)d->chunks;

    printf("Compute chunk diagnostics Core %d: "
           "chunks=%" PRIu32 ", min=%" PRIu32
           ", mean=%.2f, max=%" PRIu32 " cycles\n",
           core, d->chunks, d->min_cycles, mean, d->max_cycles);
}

/* ---------------- Workloads ---------------- */

static void process_system_event(void)
{
    uint32_t value = system_sink + 1U;

    for (int i = 0; i < SYSTEM_WORK_ITERS; ++i) {
        value = value * 1664525U + 1013904223U;
    }

    system_sink = value;
}

/*
 * Core 0 system task.
 *
 * Queue payload is the producer's Core 0 CCOUNT release timestamp.
 * Completion timestamp is also read on Core 0.
 */
static void system_task(void *arg)
{
    (void)arg;

    xTaskNotifyGive(coordinator_handle); /* startup ready */

    int event_index = 0;

    for (;;) {
        uint32_t release_cycle = 0;

        if (xQueueReceive(event_queue, &release_cycle,
                          portMAX_DELAY) != pdTRUE) {
            continue;
        }

        process_system_event();

        uint32_t completion_cycle = read_ccount();
        uint32_t elapsed = (uint32_t)(completion_cycle - release_cycle);

        if (event_index >= WARMUP_EVENTS &&
            event_index < TOTAL_EVENTS) {
            int sample_index = event_index - WARMUP_EVENTS;

            /*
             * The coordinator does not read this run's samples until it
             * receives the completion notification below.
             */
            int run_index = atomic_load_explicit(&active_run_index,
                                                 memory_order_acquire);
            response_cycles[run_index][sample_index] = elapsed;
        }

        event_index++;

        if (event_index >= TOTAL_EVENTS) {
            event_index = 0;
            xTaskNotifyGive(coordinator_handle);
        }
    }
}

/*
 * Core 0 periodic event producer.
 * The coordinator starts one batch by notifying this task.
 */
static void producer_task(void *arg)
{
    (void)arg;

    xTaskNotifyGive(coordinator_handle); /* startup ready */

    const TickType_t period = pdMS_TO_TICKS(EVENT_PERIOD_MS);

    for (;;) {
        (void)ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        TickType_t last_wake = xTaskGetTickCount();

        for (int i = 0; i < TOTAL_EVENTS; ++i) {
            vTaskDelayUntil(&last_wake, period);

            uint32_t release_cycle = read_ccount();

            if (xQueueSend(event_queue, &release_cycle,
                           portMAX_DELAY) != pdTRUE) {
                printf("ERROR: event queue send failed at event %d\n", i);
            }
        }
    }
}

/*
 * Persistent compute task pinned to its designated core.
 *
 * It runs a fixed arithmetic chunk, records elapsed cycles on its own core,
 * then delays one RTOS tick. The delay allows the idle task to run and avoids
 * starving the task watchdog.
 *
 * In A, priority 6 can preempt the priority-5 system task on Core 0.
 * In B, the compute task runs on Core 1 and does not occupy Core 0.
 */
static void compute_task(void *arg)
{
    int core = (int)(intptr_t)arg;
    uint32_t value = 0x12345678U + (uint32_t)core;

    xTaskNotifyGive(coordinator_handle); /* startup ready */

    for (;;) {
        (void)ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        ComputeDiagnostics local = {
            .min_cycles = UINT32_MAX,
            .max_cycles = 0,
            .sum_cycles = 0,
            .chunks = 0,
        };

        while (atomic_load_explicit(&compute_run[core],
                                    memory_order_acquire) != 0U) {
            uint32_t start = read_ccount();

            for (int i = 0; i < COMPUTE_CHUNK_ITERS; ++i) {
                value = value * 1664525U + 1013904223U;
            }

            uint32_t end = read_ccount();
            uint32_t elapsed = (uint32_t)(end - start);

            compute_sink[core] = value;

            if (elapsed < local.min_cycles) {
                local.min_cycles = elapsed;
            }
            if (elapsed > local.max_cycles) {
                local.max_cycles = elapsed;
            }

            local.sum_cycles += elapsed;
            local.chunks++;

            /* Let the idle task run; also creates periodic scheduling points. */
            vTaskDelay(1);
        }

        /*
         * Publish diagnostics before notifying the coordinator that this
         * compute task has stopped. Coordinator reads only after notification.
         */
        compute_diag[core] = local;

        xTaskNotifyGive(coordinator_handle); /* stopped / quiescent */
    }
}

/* ---------------- Configuration runner ---------------- */

static void run_configuration(const char *label,
                             int run_index,
                             int compute_core)
{
    printf("\n================================================\n");
    printf("%s\n", label);
    printf("System task: Core 0 | Producer: Core 0 | Compute: Core %d\n",
           compute_core);
    printf("Warm-up: %d | Measured: %d | Event period: %d ms\n",
           WARMUP_EVENTS, MEASURED_EVENTS, EVENT_PERIOD_MS);
    printf("Priorities: producer=%d, compute=%d, system=%d\n",
           PRODUCER_PRIORITY, COMPUTE_PRIORITY, SYSTEM_PRIORITY);
    printf("Compute chunk: %d iterations, then 1 RTOS tick delay\n",
           COMPUTE_CHUNK_ITERS);
    printf("================================================\n");

    memset(response_cycles[run_index], 0,
           sizeof(response_cycles[run_index]));

    atomic_store_explicit(&active_run_index, run_index,
                          memory_order_release);

    memset(&compute_diag[compute_core], 0,
           sizeof(compute_diag[compute_core]));

    atomic_store_explicit(&compute_run[compute_core],
                          1U, memory_order_release);

    xTaskNotifyGive(compute_task_handle[compute_core]);

    /* Start this configuration's periodic event batch. */
    xTaskNotifyGive(producer_task_handle);

    /* Wait for system task to process warm-up + measured events. */
    (void)ulTaskNotifyTake(pdFALSE, portMAX_DELAY);

    /* Stop compute at its next chunk boundary / delay point. */
    atomic_store_explicit(&compute_run[compute_core],
                          0U, memory_order_release);

    /* Wait for compute task to publish its diagnostics and stop. */
    (void)ulTaskNotifyTake(pdFALSE, portMAX_DELAY);

    print_response_stats(label, run_index);
    print_compute_diagnostics(compute_core);

    printf("compute_sink_core%d=%" PRIu32 "\n",
           compute_core, compute_sink[compute_core]);
}

/* ---------------- Coordinator ---------------- */

static void coordinator_task(void *arg)
{
    (void)arg;

    coordinator_handle = xTaskGetCurrentTaskHandle();

    event_queue = xQueueCreate(EVENT_QUEUE_LENGTH, sizeof(uint32_t));
    if (event_queue == NULL) {
        printf("FATAL: Failed to create event queue.\n");
        vTaskDelete(NULL);
        return;
    }

    if (xTaskCreatePinnedToCore(
            system_task, "exp011_system",
            SYSTEM_STACK_SIZE, NULL, SYSTEM_PRIORITY,
            &system_task_handle, SYSTEM_CORE) != pdPASS) {
        printf("FATAL: Failed to create system task.\n");
        vTaskDelete(NULL);
        return;
    }

    if (xTaskCreatePinnedToCore(
            producer_task, "exp011_producer",
            PRODUCER_STACK_SIZE, NULL, PRODUCER_PRIORITY,
            &producer_task_handle, PRODUCER_CORE) != pdPASS) {
        printf("FATAL: Failed to create producer task.\n");
        vTaskDelete(NULL);
        return;
    }

    if (xTaskCreatePinnedToCore(
            compute_task, "exp011_compute_c0",
            COMPUTE_STACK_SIZE, (void *)(intptr_t)0,
            COMPUTE_PRIORITY, &compute_task_handle[0], 0) != pdPASS) {
        printf("FATAL: Failed to create Core 0 compute task.\n");
        vTaskDelete(NULL);
        return;
    }

    if (xTaskCreatePinnedToCore(
            compute_task, "exp011_compute_c1",
            COMPUTE_STACK_SIZE, (void *)(intptr_t)1,
            COMPUTE_PRIORITY, &compute_task_handle[1], 1) != pdPASS) {
        printf("FATAL: Failed to create Core 1 compute task.\n");
        vTaskDelete(NULL);
        return;
    }

    /*
     * Four startup notifications: system, producer, compute Core 0,
     * compute Core 1. pdFALSE consumes one notification at a time.
     */
    for (int i = 0; i < 4; ++i) {
        (void)ulTaskNotifyTake(pdFALSE, portMAX_DELAY);
    }

    printf("\nExp011 FINAL starting: balanced ABBA execution order.\n");

    /*
     * ABBA sequence:
     *   A1 -> B1 -> B2 -> A2
     * This provides two observations per placement in one firmware run.
     */
    run_configuration("Exp011 A1: Shared-core", 0, COMPUTE_CORE_A);
    vTaskDelay(pdMS_TO_TICKS(SETTLE_DELAY_MS));

    run_configuration("Exp011 B1: Core-separated", 1, COMPUTE_CORE_B);
    vTaskDelay(pdMS_TO_TICKS(SETTLE_DELAY_MS));

    run_configuration("Exp011 B2: Core-separated", 2, COMPUTE_CORE_B);
    vTaskDelay(pdMS_TO_TICKS(SETTLE_DELAY_MS));

    run_configuration("Exp011 A2: Shared-core", 3, COMPUTE_CORE_A);

    printf("\n================================================\n");
    printf("Exp011 FINAL complete.\n");
    printf("Execution order: A1 -> B1 -> B2 -> A2\n");
    printf("Compare A1/A2 against B1/B2 for order consistency.\n");
    printf("================================================\n");

    vTaskDelete(NULL);
}

/* ---------------- Application entry ---------------- */

void app_main(void)
{
    printf("\nExp011 FINAL booting...\n");
    printf("CPU frequency configured by ESP-IDF.\n");
    printf("Expected target: ESP32-WROOM-32 dual-core.\n");

    BaseType_t result = xTaskCreatePinnedToCore(
        coordinator_task,
        "exp011_coordinator",
        COORD_STACK_SIZE,
        NULL,
        COORD_PRIORITY,
        NULL,
        SYSTEM_CORE
    );

    if (result != pdPASS) {
        printf("ERROR: Failed to create coordinator task.\n");
    }
}
