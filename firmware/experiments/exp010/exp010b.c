/*
 * Exp010B — Dual-core partitioned dot-product benchmark
 *
 * ESP32-WROOM-32 / ESP-IDF / FreeRTOS
 *
 * Core 0: coordinator + first half of dot product
 * Core 1: persistent worker + second half of dot product
 *
 * Measurement:
 *   Core 0 CCOUNT immediately before dispatch
 *   through Core 0 CCOUNT after worker completion is received.
 *
 * This is an end-to-end elapsed-cycle measurement in Core 0's counter
 * domain. It includes dispatch, both computation halves, notification
 * synchronization, and waiting for the slower half.
 *
 * Keep the Exp010A build configuration and compiler optimization settings
 * unchanged when comparing A and B.
 */

#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_err.h"

#define MAX_N               4096
#define NUM_SIZES           5
#define WARMUP_SAMPLES      100
#define MEASURED_SAMPLES   1000

#define COORDINATOR_CORE    0
#define WORKER_CORE         1
#define TASK_PRIORITY       5
#define TASK_STACK_SIZE     4096

static const int vector_sizes[NUM_SIZES] = {16, 64, 256, 1024, 4096};
static const int64_t expected_checksums[NUM_SIZES] = {
    911, 3928, 15904, 64149, 257987
};

static int32_t a[MAX_N];
static int32_t b[MAX_N];

/* Written by Core 1, read by Core 0 after completion notification. */
static volatile int64_t worker_partial_result = 0;
static volatile int current_job_n = 0;

/* Large benchmark buffers must not live on the coordinator task stack. */
static uint32_t sample_cycles[MEASURED_SAMPLES];
static uint32_t sorted_cycles[MEASURED_SAMPLES];

/* Task handles. */
static TaskHandle_t coordinator_task_handle = NULL;
static TaskHandle_t worker_task_handle = NULL;

/* CCOUNT is a per-core cycle counter. All benchmark reads occur on Core 0. */
static inline uint32_t read_ccount(void)
{
    uint32_t count;
    __asm__ __volatile__("rsr.ccount %0" : "=a"(count));
    return count;
}

static void initialize_vectors(void)
{
    for (int i = 0; i < MAX_N; ++i) {
        a[i] = (i % 17) + 1;
        b[i] = (i % 13) + 1;
    }
}

static int64_t dot_product_range(int start, int end)
{
    int64_t sum = 0;

    for (int i = start; i < end; ++i) {
        sum += (int64_t)a[i] * (int64_t)b[i];
    }

    return sum;
}

/*
 * Persistent Core 1 worker.
 *
 * Startup notification tells the coordinator that this task has started.
 * Thereafter, each coordinator notification dispatches one job.
 * The worker publishes its partial result before notifying completion.
 */
static void core1_worker_task(void *arg)
{
    (void)arg;

    xTaskNotifyGive(coordinator_task_handle);

    for (;;) {
        /* Wait for one job from Core 0. */
        (void)ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        int n = current_job_n;
        int midpoint = n / 2;

        int64_t partial = dot_product_range(midpoint, n);
        worker_partial_result = partial;

        /* Signal that the partial result is ready. */
        xTaskNotifyGive(coordinator_task_handle);
    }
}

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

    Stats stats = {
        .min = sorted_cycles[0],
        .mean = mean,
        .median = sorted_cycles[count / 2],
        .stddev = sqrt(squared_diff_sum / (double)count),
        .p95 = sorted_cycles[((count * 95) + 99) / 100 - 1],
        .p99 = sorted_cycles[((count * 99) + 99) / 100 - 1],
        .max = sorted_cycles[count - 1],
    };

    return stats;
}

static void print_stats(const char *label, const uint32_t *samples,
                        int count, int n, int64_t checksum)
{
    Stats s = calculate_stats(samples, count);

    printf("\n[%s] N=%d\n", label, n);
    printf("min=%" PRIu32 ", mean=%.3f, median=%" PRIu32
           ", SD=%.3f, P95=%" PRIu32 ", P99=%" PRIu32
           ", max=%" PRIu32 "\n",
           s.min, s.mean, s.median, s.stddev, s.p95, s.p99, s.max);
    printf("checksum=%" PRId64 "\n", checksum);
}

static void run_exp010b(void)
{
    uint32_t *samples = sample_cycles;

    printf("\n========================================\n");
    printf("Exp010B: Dual-core partitioned dot product\n");
    printf("Core 0: coordinator + first half\n");
    printf("Core 1: worker + second half\n");
    printf("Warm-up: %d | Measured: %d\n",
           WARMUP_SAMPLES, MEASURED_SAMPLES);
    printf("========================================\n");

    for (int size_index = 0; size_index < NUM_SIZES; ++size_index) {
        const int n = vector_sizes[size_index];
        const int midpoint = n / 2;

        int64_t final_checksum = 0;

        /*
         * Warm-up. The worker is persistent; task creation is not timed.
         */
        for (int i = 0; i < WARMUP_SAMPLES; ++i) {
            current_job_n = n;
            xTaskNotifyGive(worker_task_handle);

            int64_t core0_partial = dot_product_range(0, midpoint);

            (void)ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
            int64_t core1_partial = worker_partial_result;

            final_checksum = core0_partial + core1_partial;
        }

        /*
         * Measured samples.
         * CCOUNT is read only on Core 0. Unsigned subtraction handles
         * counter wraparound naturally.
         */
        for (int i = 0; i < MEASURED_SAMPLES; ++i) {
            current_job_n = n;
            uint32_t start = read_ccount();

            xTaskNotifyGive(worker_task_handle);

            int64_t core0_partial = dot_product_range(0, midpoint);

            (void)ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
            int64_t core1_partial = worker_partial_result;

            uint32_t end = read_ccount();

            samples[i] = (uint32_t)(end - start);
            final_checksum = core0_partial + core1_partial;
        }

        print_stats("Exp010B", samples, MEASURED_SAMPLES,
                    n, final_checksum);

        if (final_checksum == expected_checksums[size_index]) {
            printf("checksum_validation=PASS (matches Exp010A)\n");
        } else {
            printf("checksum_validation=FAIL expected=%" PRId64
                   " actual=%" PRId64 "\n",
                   expected_checksums[size_index], final_checksum);
        }
    }

    printf("\nExp010B complete.\n");
}

static void coordinator_task(void *arg)
{
    (void)arg;

    coordinator_task_handle = xTaskGetCurrentTaskHandle();

    BaseType_t created = xTaskCreatePinnedToCore(
        core1_worker_task,
        "exp010b_core1_worker",
        TASK_STACK_SIZE,
        NULL,
        TASK_PRIORITY,
        &worker_task_handle,
        WORKER_CORE
    );

    if (created != pdPASS) {
        printf("ERROR: Failed to create Core 1 worker task.\n");
        vTaskDelete(NULL);
        return;
    }

    /*
     * Wait for the worker's startup notification. The worker sends this
     * before entering its notification wait. If dispatch arrives before
     * it blocks, FreeRTOS retains the notification for it.
     */
    (void)ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

    printf("Core 1 worker ready. Starting Exp010B.\n");
    run_exp010b();

    printf("Exp010B finished. Coordinator task deleting itself.\n");
    vTaskDelete(NULL);
}

void app_main(void)
{
    initialize_vectors();

    printf("\nExp010B booting...\n");
    printf("CPU frequency configured by ESP-IDF.\n");

    BaseType_t created = xTaskCreatePinnedToCore(
        coordinator_task,
        "exp010b_coordinator",
        TASK_STACK_SIZE,
        NULL,
        TASK_PRIORITY,
        NULL,
        COORDINATOR_CORE
    );

    if (created != pdPASS) {
        printf("ERROR: Failed to create Core 0 coordinator task.\n");
    }
}
