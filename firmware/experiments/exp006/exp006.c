#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <inttypes.h>
#include <limits.h>
#include <math.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "esp_log.h"
#include "esp_timer.h"

/* =========================================================
 * V-CORE: EXPERIMENT 006
 * COMPUTATIONAL LATENCY CHARACTERIZATION
 * ========================================================= */

#define NUM_SAMPLES       1000
#define WARMUP_SAMPLES    100
#define MAX_VECTOR_SIZE   4096

#define NUM_WORKLOADS     5

#define TEST_CORE         0
#define TEST_PRIORITY     5

static const char *TAG = "V-CORE";

/* Workload sizes: number of input elements */
static const size_t vector_sizes[NUM_WORKLOADS] = {
    16, 64, 256, 1024, 4096
};

/* Maximum-sized input vectors */
static int32_t a[MAX_VECTOR_SIZE];
static int32_t b[MAX_VECTOR_SIZE];

/* Prevent the computation result from being discarded */
static volatile int64_t dot_sink;

/* Measurement arrays */
static uint32_t cycle_samples[NUM_SAMPLES];
static int64_t wall_samples[NUM_SAMPLES];

/* =========================================================
 * CCOUNT MEASUREMENT
 * ========================================================= */

static inline uint32_t read_ccount(void)
{
    uint32_t cycles;

    __asm__ __volatile__(
        "rsr.ccount %0"
        : "=a"(cycles)
    );

    return cycles;
}

/* =========================================================
 * DOT PRODUCT
 * ========================================================= */

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

/* =========================================================
 * SORTING
 * ========================================================= */

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

static void sort_i64(int64_t *samples, size_t count)
{
    for (size_t i = 1; i < count; i++) {
        int64_t key = samples[i];
        size_t j = i;

        while (j > 0 && samples[j - 1] > key) {
            samples[j] = samples[j - 1];
            j--;
        }

        samples[j] = key;
    }
}

/* =========================================================
 * STATISTICS: CCOUNT
 * ========================================================= */

static void print_cycle_statistics(size_t count)
{
    sort_u32(cycle_samples, count);

    uint64_t sum = 0;
    double squared_deviation_sum = 0.0;

    for (size_t i = 0; i < count; i++) {
        sum += cycle_samples[i];
    }

    double mean = (double)sum / count;

    for (size_t i = 0; i < count; i++) {
        double difference = (double)cycle_samples[i] - mean;
        squared_deviation_sum += difference * difference;
    }

    double stddev = sqrt(squared_deviation_sum / count);

    size_t median_index = count / 2;
    size_t p95_index = (count * 95 / 100) - 1;
    size_t p99_index = (count * 99 / 100) - 1;

    ESP_LOGI(TAG, "CCOUNT statistics:");
    ESP_LOGI(TAG, "  Minimum: %" PRIu32 " cycles",
             cycle_samples[0]);
    ESP_LOGI(TAG, "  Mean: %.3f cycles", mean);
    ESP_LOGI(TAG, "  Median: %" PRIu32 " cycles",
             cycle_samples[median_index]);
    ESP_LOGI(TAG, "  Std deviation: %.3f cycles", stddev);
    ESP_LOGI(TAG, "  P95: %" PRIu32 " cycles",
             cycle_samples[p95_index]);
    ESP_LOGI(TAG, "  P99: %" PRIu32 " cycles",
             cycle_samples[p99_index]);
    ESP_LOGI(TAG, "  Maximum: %" PRIu32 " cycles",
             cycle_samples[count - 1]);
}

/* =========================================================
 * STATISTICS: WALL CLOCK
 * ========================================================= */

static void print_wall_statistics(size_t count)
{
    sort_i64(wall_samples, count);

    int64_t sum = 0;
    double squared_deviation_sum = 0.0;

    for (size_t i = 0; i < count; i++) {
        sum += wall_samples[i];
    }

    double mean = (double)sum / count;

    for (size_t i = 0; i < count; i++) {
        double difference = (double)wall_samples[i] - mean;
        squared_deviation_sum += difference * difference;
    }

    double stddev = sqrt(squared_deviation_sum / count);

    size_t median_index = count / 2;
    size_t p95_index = (count * 95 / 100) - 1;
    size_t p99_index = (count * 99 / 100) - 1;

    ESP_LOGI(TAG, "Wall-clock statistics:");
    ESP_LOGI(TAG, "  Minimum: %" PRId64 " us",
             wall_samples[0]);
    ESP_LOGI(TAG, "  Mean: %.3f us", mean);
    ESP_LOGI(TAG, "  Median: %" PRId64 " us",
             wall_samples[median_index]);
    ESP_LOGI(TAG, "  Std deviation: %.3f us", stddev);
    ESP_LOGI(TAG, "  P95: %" PRId64 " us",
             wall_samples[p95_index]);
    ESP_LOGI(TAG, "  P99: %" PRId64 " us",
             wall_samples[p99_index]);
    ESP_LOGI(TAG, "  Maximum: %" PRId64 " us",
             wall_samples[count - 1]);
}

/* =========================================================
 * INITIALIZE INPUT VECTORS
 * ========================================================= */

static void initialize_vectors(void)
{
    /*
     * Deterministic input values.
     * Keep the same inputs for every workload size.
     */
    for (size_t i = 0; i < MAX_VECTOR_SIZE; i++) {
        a[i] = (int32_t)((i % 17) + 1);
        b[i] = (int32_t)((i % 13) + 1);
    }
}

/* =========================================================
 * RUN ONE WORKLOAD SIZE
 * ========================================================= */

static void run_workload(size_t vector_size)
{
    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "Vector size: %u elements",
             (unsigned)vector_size);
    ESP_LOGI(TAG, "Warm-up samples: %d", WARMUP_SAMPLES);
    ESP_LOGI(TAG, "Measured samples: %d", NUM_SAMPLES);
    ESP_LOGI(TAG, "========================================");

    /*
     * Warm-up runs are excluded from the measured dataset.
     */
    for (int i = 0; i < WARMUP_SAMPLES; i++) {
        dot_sink = dot_product(a, b, vector_size);
    }

    /*
     * Collect CCOUNT and wall-clock measurements.
     *
     * Both timers surround the same dot-product operation.
     * The wall-clock measurement also includes the overhead
     * of reading CCOUNT at the beginning and end.
     */
    for (int i = 0; i < NUM_SAMPLES; i++) {
        int64_t start_us = esp_timer_get_time();
        uint32_t start_cycles = read_ccount();

        dot_sink = dot_product(a, b, vector_size);

        uint32_t end_cycles = read_ccount();
        int64_t end_us = esp_timer_get_time();

        cycle_samples[i] =
            (uint32_t)(end_cycles - start_cycles);

        wall_samples[i] = end_us - start_us;
    }

    ESP_LOGI(TAG, "Results for %u elements:",
             (unsigned)vector_size);

    print_cycle_statistics(NUM_SAMPLES);
    print_wall_statistics(NUM_SAMPLES);

    ESP_LOGI(TAG, "Result checksum: %" PRId64, dot_sink);

    /*
     * Approximate throughput using the median CCOUNT time.
     * This is an estimate of dot products per second,
     * not individual arithmetic operations per second.
     */
    sort_u32(cycle_samples, NUM_SAMPLES);

    uint32_t median_cycles = cycle_samples[NUM_SAMPLES / 2];

    if (median_cycles > 0) {
        double seconds =
            (double)median_cycles / 240000000.0;

        double throughput = 1.0 / seconds;

        ESP_LOGI(TAG,
                 "Approx. throughput: %.2f dot products/sec",
                 throughput);
    }

    ESP_LOGI(TAG, "========================================");
}

/* =========================================================
 * EXPERIMENT TASK
 * ========================================================= */

static void experiment_task(void *arg)
{
    (void)arg;

    ESP_LOGI(TAG, "V-CORE EXPERIMENT 006");
    ESP_LOGI(TAG, "Computational Latency Characterization");
    ESP_LOGI(TAG, "CPU frequency: 240 MHz");
    ESP_LOGI(TAG, "Core: %d", TEST_CORE);
    ESP_LOGI(TAG, "Workload sizes: 16, 64, 256, 1024, 4096");
    ESP_LOGI(TAG, "========================================");

    initialize_vectors();

    for (size_t i = 0; i < NUM_WORKLOADS; i++) {
        run_workload(vector_sizes[i]);
    }

    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "EXPERIMENT 006 COMPLETE");
    ESP_LOGI(TAG, "========================================");

    vTaskDelete(NULL);
}

/* =========================================================
 * APPLICATION ENTRY
 * ========================================================= */

void app_main(void)
{
    BaseType_t result = xTaskCreatePinnedToCore(
        experiment_task,
        "exp006_task",
        6144,
        NULL,
        TEST_PRIORITY,
        NULL,
        TEST_CORE
    );

    if (result != pdPASS) {
        ESP_LOGE(TAG, "Failed to create Experiment 006 task");
    }
}