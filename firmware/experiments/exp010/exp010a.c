#include <stdint.h>
#include <stddef.h>
#include <inttypes.h>
#include <math.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "esp_log.h"

/*
 * V-CORE EXPERIMENT 010A
 * SINGLE-CORE COMPUTATIONAL BASELINE
 *
 * Configuration A:
 *   - Entire dot product executes on Core 0.
 *   - Uses the same deterministic inputs and dot-product implementation
 *     as Experiment 006.
 *   - CCOUNT is the primary measurement source.
 *
 * CCOUNT is read immediately before and after the computation. No
 * esp_timer_get_time() call is made inside the measured interval.
 *
 * This is the single-core reference configuration for Experiment 010.
 * Experiment 010B will partition the same dot product across Core 0/Core 1.
 */

#define NUM_SAMPLES       1000
#define WARMUP_SAMPLES    100
#define MAX_VECTOR_SIZE   4096
#define NUM_WORKLOADS     5

#define TEST_CORE         0
#define TEST_PRIORITY     5
#define EXPERIMENT_STACK  6144

static const char *TAG = "V-CORE-EXP010A";

static const size_t vector_sizes[NUM_WORKLOADS] = {
    16, 64, 256, 1024, 4096
};

static int32_t a[MAX_VECTOR_SIZE];
static int32_t b[MAX_VECTOR_SIZE];

/* Prevent the compiler from discarding the computed result. */
static volatile int64_t dot_sink;

/* Per-sample cycle measurements. */
static uint32_t cycle_samples[NUM_SAMPLES];
static uint32_t sorted_samples[NUM_SAMPLES];

/* Read the Xtensa cycle counter on the core executing this task. */
static inline uint32_t read_ccount(void)
{
    uint32_t cycles;

    __asm__ __volatile__(
        "rsr.ccount %0"
        : "=a"(cycles)
    );

    return cycles;
}

/* Same dot-product operation as Experiment 006. */
static int64_t dot_product(
    const int32_t *x,
    const int32_t *y,
    size_t count)
{
    int64_t sum = 0;

    for (size_t i = 0; i < count; i++) {
        sum += (int64_t)x[i] * y[i];
    }

    return sum;
}

static void sort_u32(uint32_t *samples, size_t count)
{
    for (size_t i = 1; i < count; i++) {
        uint32_t key = samples[i];
        size_t j = i;

        while (j > 0 && samples[j - 1] > key) {
            samples[j] = samples[j - 1];
            j--;
        }

        samples[j] = key;
    }
}

static void print_cycle_statistics(size_t count)
{
    uint64_t sum = 0;
    double squared_deviation_sum = 0.0;

    for (size_t i = 0; i < count; i++) {
        sorted_samples[i] = cycle_samples[i];
        sum += cycle_samples[i];
    }

    sort_u32(sorted_samples, count);

    const double mean = (double)sum / (double)count;

    for (size_t i = 0; i < count; i++) {
        const double difference = (double)cycle_samples[i] - mean;
        squared_deviation_sum += difference * difference;
    }

    const double stddev = sqrt(squared_deviation_sum / (double)count);
    const size_t median_index = count / 2;
    const size_t p95_index = (count * 95 / 100) - 1;
    const size_t p99_index = (count * 99 / 100) - 1;

    ESP_LOGI(TAG, "CCOUNT statistics:");
    ESP_LOGI(TAG, "  Minimum: %" PRIu32 " cycles", sorted_samples[0]);
    ESP_LOGI(TAG, "  Mean: %.3f cycles", mean);
    ESP_LOGI(TAG, "  Median: %" PRIu32 " cycles", sorted_samples[median_index]);
    ESP_LOGI(TAG, "  Std deviation: %.3f cycles", stddev);
    ESP_LOGI(TAG, "  P95: %" PRIu32 " cycles", sorted_samples[p95_index]);
    ESP_LOGI(TAG, "  P99: %" PRIu32 " cycles", sorted_samples[p99_index]);
    ESP_LOGI(TAG, "  Maximum: %" PRIu32 " cycles", sorted_samples[count - 1]);
}

static void initialize_vectors(void)
{
    for (size_t i = 0; i < MAX_VECTOR_SIZE; i++) {
        a[i] = (int32_t)((i % 17) + 1);
        b[i] = (int32_t)((i % 13) + 1);
    }
}

static void run_workload(size_t vector_size)
{
    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "Configuration A: single-core baseline");
    ESP_LOGI(TAG, "Core: %d", TEST_CORE);
    ESP_LOGI(TAG, "Vector size: %u elements", (unsigned)vector_size);
    ESP_LOGI(TAG, "Warm-up samples: %d", WARMUP_SAMPLES);
    ESP_LOGI(TAG, "Measured samples: %d", NUM_SAMPLES);
    ESP_LOGI(TAG, "Measurement: CCOUNT immediately around dot product");
    ESP_LOGI(TAG, "========================================");

    /* Warm-up samples are excluded from the measured dataset. */
    for (int i = 0; i < WARMUP_SAMPLES; i++) {
        dot_sink = dot_product(a, b, vector_size);
    }

    /*
     * CCOUNT brackets only the dot-product operation.
     * Unsigned subtraction handles counter wraparound for short intervals.
     */
    for (int i = 0; i < NUM_SAMPLES; i++) {
        const uint32_t start_cycles = read_ccount();

        dot_sink = dot_product(a, b, vector_size);

        const uint32_t end_cycles = read_ccount();

        cycle_samples[i] = (uint32_t)(end_cycles - start_cycles);
    }

    ESP_LOGI(TAG, "Results for %u elements:", (unsigned)vector_size);
    print_cycle_statistics(NUM_SAMPLES);
    ESP_LOGI(TAG, "Result checksum: %" PRId64, dot_sink);

    /* Same throughput interpretation used in Experiment 006. */
    sort_u32(cycle_samples, NUM_SAMPLES);
    const uint32_t median_cycles = cycle_samples[NUM_SAMPLES / 2];

    if (median_cycles > 0) {
        const double seconds = (double)median_cycles / 240000000.0;
        const double throughput = 1.0 / seconds;

        ESP_LOGI(TAG, "Approx. throughput: %.2f dot products/sec", throughput);
    }

    ESP_LOGI(TAG, "========================================");
}

static void experiment_task(void *arg)
{
    (void)arg;

    ESP_LOGI(TAG, "V-CORE EXPERIMENT 010A");
    ESP_LOGI(TAG, "Computational Workload Partitioning");
    ESP_LOGI(TAG, "Configuration A: single-core reference");
    ESP_LOGI(TAG, "CPU frequency assumption: 240 MHz");
    ESP_LOGI(TAG, "Execution core: %d", TEST_CORE);
    ESP_LOGI(TAG, "Workload sizes: 16, 64, 256, 1024, 4096");
    ESP_LOGI(TAG, "Primary timing source: Xtensa CCOUNT");
    ESP_LOGI(TAG, "No esp_timer calls inside the measured interval.");
    ESP_LOGI(TAG, "========================================");

    initialize_vectors();

    for (size_t i = 0; i < NUM_WORKLOADS; i++) {
        run_workload(vector_sizes[i]);
    }

    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "EXPERIMENT 010A COMPLETE");
    ESP_LOGI(TAG, "========================================");

    vTaskDelete(NULL);
}

void app_main(void)
{
    BaseType_t result = xTaskCreatePinnedToCore(
        experiment_task,
        "exp010a_task",
        EXPERIMENT_STACK,
        NULL,
        TEST_PRIORITY,
        NULL,
        TEST_CORE
    );

    if (result != pdPASS) {
        ESP_LOGE(TAG, "Failed to create Experiment 010A task");
    }
}
