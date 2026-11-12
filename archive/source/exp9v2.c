#include <stdint.h>
#include <stddef.h>
#include <inttypes.h>
#include <stdbool.h>
#include <math.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_timer.h"

/*
 * V-CORE EXPERIMENT 009 - INTERFERENCE ANALYSIS
 * Core 0: dot-product workload (same function/input pattern as Exp006).
 * Core 1: optional repetitive arithmetic workload.
 *
 * Condition A: Core 1 arithmetic task is inactive.
 * Condition B: Core 1 runs the arithmetic task while Core 0 computes.
 *
 * The arithmetic task periodically delays one RTOS tick to let idle/system
 * tasks run. It is a high-duty-cycle workload, not a literally uninterrupted
 * loop. Compare results on the same firmware/build and board.
 */

#define NUM_SAMPLES          1000
#define WARMUP_SAMPLES       100
#define MAX_VECTOR_SIZE      4096
#define NUM_WORKLOADS        5
#define CORE_COMPUTE         0
#define CORE_INTERFERENCE    1
#define TEST_PRIORITY        5
#define INTERFERENCE_STACK   3072
#define EXPERIMENT_STACK     8192
#define INTERFERENCE_CHUNK   4096U

static const char *TAG = "V-CORE-EXP009";

static const size_t vector_sizes[NUM_WORKLOADS] = {4096, 1024, 256, 64, 16};
static int32_t a[MAX_VECTOR_SIZE];
static int32_t b[MAX_VECTOR_SIZE];
static volatile int64_t dot_sink;
static volatile uint32_t interference_sink;

static uint32_t cycle_samples[NUM_SAMPLES];
static int64_t wall_samples[NUM_SAMPLES];
/* Large sorting buffers live in static memory, not the task stack. */
static uint32_t sorted_cycle_samples[NUM_SAMPLES];
static int64_t sorted_wall_samples[NUM_SAMPLES];

static bool interference_run;
static bool interference_ready;

static inline void store_bool(bool *ptr, bool value)
{
    __atomic_store_n(ptr, value, __ATOMIC_RELEASE);
}

static inline bool load_bool(const bool *ptr)
{
    return __atomic_load_n(ptr, __ATOMIC_ACQUIRE);
}

static inline uint32_t read_ccount(void)
{
    uint32_t cycles;
    __asm__ __volatile__("rsr.ccount %0" : "=a"(cycles));
    return cycles;
}

static int64_t dot_product(const int32_t *x, const int32_t *y, size_t count)
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

static void print_cycle_statistics(const uint32_t *source, size_t count)
{
    uint32_t *sorted = sorted_cycle_samples;
    uint64_t sum = 0;
    double squared_deviation_sum = 0.0;

    for (size_t i = 0; i < count; i++) {
        sorted[i] = source[i];
        sum += source[i];
    }
    sort_u32(sorted, count);

    double mean = (double)sum / (double)count;
    for (size_t i = 0; i < count; i++) {
        double d = (double)source[i] - mean;
        squared_deviation_sum += d * d;
    }

    double stddev = sqrt(squared_deviation_sum / (double)count);

    ESP_LOGI(TAG, "CCOUNT: min=%" PRIu32 ", mean=%.3f, median=%" PRIu32
                  ", stddev=%.3f, P95=%" PRIu32 ", P99=%" PRIu32
                  ", max=%" PRIu32,
             sorted[0], mean, sorted[count / 2], stddev,
             sorted[(count * 95 / 100) - 1],
             sorted[(count * 99 / 100) - 1], sorted[count - 1]);
}

static void print_wall_statistics(const int64_t *source, size_t count)
{
    int64_t *sorted = sorted_wall_samples;
    int64_t sum = 0;
    double squared_deviation_sum = 0.0;

    for (size_t i = 0; i < count; i++) {
        sorted[i] = source[i];
        sum += source[i];
    }
    sort_i64(sorted, count);

    double mean = (double)sum / (double)count;
    for (size_t i = 0; i < count; i++) {
        double d = (double)source[i] - mean;
        squared_deviation_sum += d * d;
    }

    double stddev = sqrt(squared_deviation_sum / (double)count);

    ESP_LOGI(TAG, "Wall time: min=%" PRId64 " us, mean=%.3f us, median=%"
                  PRId64 " us, stddev=%.3f, P95=%" PRId64
                  " us, P99=%" PRId64 " us, max=%" PRId64 " us",
             sorted[0], mean, sorted[count / 2], stddev,
             sorted[(count * 95 / 100) - 1],
             sorted[(count * 99 / 100) - 1], sorted[count - 1]);
}

static void initialize_vectors(void)
{
    for (size_t i = 0; i < MAX_VECTOR_SIZE; i++) {
        a[i] = (int32_t)((i % 17) + 1);
        b[i] = (int32_t)((i % 13) + 1);
    }
}

/* Deterministic unsigned arithmetic; volatile publication keeps work observable. */
static void interference_task(void *arg)
{
    (void)arg;
    uint32_t value = 1U;
    store_bool(&interference_ready, true);

    while (load_bool(&interference_run)) {
        for (uint32_t i = 0; i < INTERFERENCE_CHUNK; i++) {
            value = value * 1664525U + 1013904223U;
        }
        interference_sink = value;

        /* Allow idle/system tasks to run and avoid starving the task watchdog. */
        vTaskDelay(1);
    }

    vTaskDelete(NULL);
}

static bool start_interference(void)
{
    store_bool(&interference_ready, false);
    store_bool(&interference_run, true);

    BaseType_t result = xTaskCreatePinnedToCore(
        interference_task, "exp009_load", INTERFERENCE_STACK, NULL,
        TEST_PRIORITY, NULL, CORE_INTERFERENCE);

    if (result != pdPASS) {
        store_bool(&interference_run, false);
        ESP_LOGE(TAG, "Failed to create Core 1 workload task");
        return false;
    }

    const int64_t deadline = esp_timer_get_time() + 2000000;
    while (!load_bool(&interference_ready)) {
        if (esp_timer_get_time() >= deadline) {
            ESP_LOGE(TAG, "Core 1 workload did not become ready");
            store_bool(&interference_run, false);
            return false;
        }
        vTaskDelay(1);
    }
    return true;
}

static void stop_interference(void)
{
    store_bool(&interference_run, false);
    vTaskDelay(2);
}

static void run_condition(size_t vector_size, bool interference_active)
{
    ESP_LOGI(TAG, "%s",
             interference_active
                 ? "Condition B: Core 1 arithmetic workload ACTIVE"
                 : "Condition A: Core 1 arithmetic workload INACTIVE");

    for (int i = 0; i < WARMUP_SAMPLES; i++) {
        dot_sink = dot_product(a, b, vector_size);
    }

    for (int i = 0; i < NUM_SAMPLES; i++) {
        int64_t start_us = esp_timer_get_time();
        uint32_t start_cycles = read_ccount();

        dot_sink = dot_product(a, b, vector_size);

        uint32_t end_cycles = read_ccount();
        int64_t end_us = esp_timer_get_time();

        cycle_samples[i] = (uint32_t)(end_cycles - start_cycles);
        wall_samples[i] = end_us - start_us;
    }

    ESP_LOGI(TAG, "Vector size: %u elements", (unsigned)vector_size);
    print_cycle_statistics(cycle_samples, NUM_SAMPLES);
    print_wall_statistics(wall_samples, NUM_SAMPLES);
    ESP_LOGI(TAG, "Result checksum: %" PRId64, dot_sink);
}

static void experiment_task(void *arg)
{
    (void)arg;

    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "V-CORE EXPERIMENT 009 - Interference Analysis");
    ESP_LOGI(TAG, "Dot product: Core %d | arithmetic workload: Core %d",
             CORE_COMPUTE, CORE_INTERFERENCE);
    ESP_LOGI(TAG, "Warm-up: %d | measured: %d",
             WARMUP_SAMPLES, NUM_SAMPLES);
    ESP_LOGI(TAG, "========================================");

    initialize_vectors();

    for (size_t i = 0; i < NUM_WORKLOADS; i++) {
        size_t n = vector_sizes[i];
        ESP_LOGI(TAG, "");
        ESP_LOGI(TAG, "========== N = %u ==========", (unsigned)n);

        /* A: Core 1 workload task is absent. */
        run_condition(n, false);

        /* B: Core 1 runs the repetitive arithmetic workload. */
        if (!start_interference()) {
            ESP_LOGE(TAG, "Could not start interference condition");
            break;
        }
        run_condition(n, true);
        stop_interference();

        ESP_LOGI(TAG, "========================================");
    }

    ESP_LOGI(TAG, "EXPERIMENT 009 COMPLETE");
    vTaskDelete(NULL);
}

void app_main(void)
{
    BaseType_t result = xTaskCreatePinnedToCore(
        experiment_task, "exp009_task", EXPERIMENT_STACK, NULL,
        TEST_PRIORITY, NULL, CORE_COMPUTE);

    if (result != pdPASS) {
        ESP_LOGE(TAG, "Failed to create Experiment 009 task");
    }
}
