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
 * V-CORE EXPERIMENT 008
 *
 * Measures sender-side request-to-acknowledgment round-trip elapsed time.
 *
 * A: Same core, receiver actively polls for requests. 
 * B: Same core, receiver blocks waiting for a task notification.
 * C: Cross-core, receiver actively polls for requests.
 * D: Cross-core, receiver blocks waiting for a task notification.
 *
 * In all tests the sender waits for the acknowledgment using the same
 * task-notification mechanism. The request mechanism differs only where
 * needed to make the receiver polling or blocked.
 *
 * Results include scheduling, request delivery, receiver processing,
 * acknowledgment delivery, and timer-read overhead. This is not a pure
 * one-way signaling delay.
 */

#define NUM_SAMPLES       1000
#define WARMUP_SAMPLES    100
#define RECEIVER_STACK    4096
#define EXPERIMENT_STACK  8192
#define TEST_TIMEOUT_MS   2000
#define CORE_A            0
#define CORE_B            1
#define TEST_PRIORITY     5

static const char *TAG = "V-CORE-EXP008";

typedef enum {
    TEST_SAME_READY = 0,
    TEST_SAME_BLOCKED,
    TEST_CROSS_READY,
    TEST_CROSS_BLOCKED,
    TEST_COUNT
} test_id_t;

typedef struct {
    const char *name;
    BaseType_t sender_core;
    BaseType_t receiver_core;
    bool receiver_polls;
} test_config_t;

static const test_config_t tests[TEST_COUNT] = {
    { "A: Same-core / receiver polling", CORE_A, CORE_A, true  },
    { "B: Same-core / receiver blocked", CORE_A, CORE_A, false },
    { "C: Cross-core / receiver polling", CORE_A, CORE_B, true  },
    { "D: Cross-core / receiver blocked",CORE_A, CORE_B, false }
};

static TaskHandle_t sender_task_handle;
static TaskHandle_t receiver_task_handle;

/* Shared, naturally aligned 32-bit state; use atomic builtins for ordering. */
static uint32_t current_sequence;
static uint32_t receiver_ack_sequence;
static bool receiver_waiting;
static bool receiver_exit;

static int64_t latency_samples[NUM_SAMPLES];
static int64_t sorted_samples[NUM_SAMPLES];

static inline void publish_u32(uint32_t *ptr, uint32_t value)
{
    __atomic_store_n(ptr, value, __ATOMIC_RELEASE);
}

static inline uint32_t load_u32(const uint32_t *ptr)
{
    return __atomic_load_n(ptr, __ATOMIC_ACQUIRE);
}

static inline void publish_bool(bool *ptr, bool value)
{
    __atomic_store_n(ptr, value, __ATOMIC_RELEASE);
}

static inline bool load_bool(const bool *ptr)
{
    return __atomic_load_n(ptr, __ATOMIC_ACQUIRE);
}

static void receiver_task(void *arg)
{
    const test_config_t *cfg = (const test_config_t *)arg;
    uint32_t seen_sequence = 0;

    for (;;) {
        if (load_bool(&receiver_exit)) {
            break;
        }

        if (cfg->receiver_polls) {
            uint32_t seq;

            publish_bool(&receiver_waiting, true);

            do {
                if (load_bool(&receiver_exit)) {
                    vTaskDelete(NULL);
                }

                seq = load_u32(&current_sequence);

                if (seq == seen_sequence) {
                    taskYIELD();
                }
            } while (seq == seen_sequence);

            seen_sequence = seq;
            publish_u32(&receiver_ack_sequence, seq);
            xTaskNotifyGive(sender_task_handle);
            publish_bool(&receiver_waiting, false);
        } else {
            /*
             * Publish readiness before blocking. If the sender notifies
             * just before ulTaskNotifyTake(), the notification remains
             * pending and is consumed when this task enters the wait.
             */
            publish_bool(&receiver_waiting, true);
            (void)ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

            if (load_bool(&receiver_exit)) {
                break;
            }

            publish_bool(&receiver_waiting, false);

            uint32_t seq = load_u32(&current_sequence);
            seen_sequence = seq;
            publish_u32(&receiver_ack_sequence, seq);
            xTaskNotifyGive(sender_task_handle);
        }
    }

    vTaskDelete(NULL);
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

static void print_statistics(const int64_t *source, size_t count)
{
    int64_t sum = 0;
    double squared_deviation_sum = 0.0;

    for (size_t i = 0; i < count; i++) {
        sorted_samples[i] = source[i];
        sum += source[i];
    }

    sort_i64(sorted_samples, count);

    double mean = (double)sum / (double)count;

    for (size_t i = 0; i < count; i++) {
        double d = (double)source[i] - mean;
        squared_deviation_sum += d * d;
    }

    double stddev = sqrt(squared_deviation_sum / (double)count);
    size_t median_index = count / 2;
    size_t p95_index = (count * 95 / 100) - 1;
    size_t p99_index = (count * 99 / 100) - 1;

    ESP_LOGI(TAG, "  Min: %" PRId64 " us", sorted_samples[0]);
    ESP_LOGI(TAG, "  Mean: %.3f us", mean);
    ESP_LOGI(TAG, "  Median: %" PRId64 " us", sorted_samples[median_index]);
    ESP_LOGI(TAG, "  Std deviation: %.3f us", stddev);
    ESP_LOGI(TAG, "  P95: %" PRId64 " us", sorted_samples[p95_index]);
    ESP_LOGI(TAG, "  P99: %" PRId64 " us", sorted_samples[p99_index]);
    ESP_LOGI(TAG, "  Max: %" PRId64 " us", sorted_samples[count - 1]);
}

static bool wait_for_flag(bool *flag, bool expected)
{
    int64_t deadline = esp_timer_get_time() + ((int64_t)TEST_TIMEOUT_MS * 1000);

    while (load_bool(flag) != expected) {
        if (esp_timer_get_time() >= deadline) {
            return false;
        }
        taskYIELD();
    }

    return true;
}

static bool wait_for_sender_ack(uint32_t expected_sequence)
{
    TickType_t timeout_ticks = pdMS_TO_TICKS(TEST_TIMEOUT_MS);
    if (timeout_ticks < 1) {
        timeout_ticks = 1;
    }

    if (ulTaskNotifyTake(pdTRUE, timeout_ticks) == 0) {
        return false;
    }

    return load_u32(&receiver_ack_sequence) == expected_sequence;
}

static void stop_receiver(void)
{
    publish_bool(&receiver_exit, true);
    xTaskNotifyGive(receiver_task_handle);
    vTaskDelay(pdMS_TO_TICKS(10));
}

static bool run_one_test(test_id_t id)
{
    const test_config_t *cfg = &tests[id];

    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "%s", cfg->name);
    ESP_LOGI(TAG, "Sender core: %d; receiver core: %d",
             (int)cfg->sender_core, (int)cfg->receiver_core);
    ESP_LOGI(TAG, "Warm-up: %d; measured: %d",
             WARMUP_SAMPLES, NUM_SAMPLES);
    ESP_LOGI(TAG, "Metric: request publication to sender-observed acknowledgment");
    ESP_LOGI(TAG, "========================================");

    publish_u32(&current_sequence, 0);
    publish_u32(&receiver_ack_sequence, 0);
    publish_bool(&receiver_waiting, false);
    publish_bool(&receiver_exit, false);

    BaseType_t rc = xTaskCreatePinnedToCore(
        receiver_task,
        "exp008_receiver",
        RECEIVER_STACK,
        (void *)cfg,
        TEST_PRIORITY + 1, /* Must be able to run while sender waits for readiness. */
        &receiver_task_handle,
        cfg->receiver_core
    );

    if (rc != pdPASS) {
        ESP_LOGE(TAG, "Failed to create receiver task");
        return false;
    }

    if (!wait_for_flag(&receiver_waiting, true)) {
        ESP_LOGE(TAG, "Receiver failed to become ready");
        stop_receiver();
        return false;
    }

    /* Allow the receiver to enter its polling loop or notification wait. */
    vTaskDelay(pdMS_TO_TICKS(10));

    const size_t total_samples = WARMUP_SAMPLES + NUM_SAMPLES;

    for (size_t i = 0; i < total_samples; i++) {
        uint32_t seq = (uint32_t)i + 1;

        /*
         * Blocked mode: ensure receiver has returned to its wait state.
         * Polling mode: receiver_waiting indicates its polling loop is active.
         */
        if (!wait_for_flag(&receiver_waiting, true)) {
            ESP_LOGE(TAG, "Receiver not ready at sample %u", (unsigned)i);
            stop_receiver();
            return false;
        }

        /* Remove any stale acknowledgment notification before this request. */
        (void)ulTaskNotifyTake(pdTRUE, 0);

        int64_t start_us = esp_timer_get_time();
        publish_u32(&current_sequence, seq);

        if (!cfg->receiver_polls) {
            xTaskNotifyGive(receiver_task_handle);
        }

        if (!wait_for_sender_ack(seq)) {
            ESP_LOGE(TAG, "Acknowledgment timeout/mismatch at sample %u; ack=%" PRIu32,
                     (unsigned)i, load_u32(&receiver_ack_sequence));
            stop_receiver();
            return false;
        }

        int64_t elapsed_us = esp_timer_get_time() - start_us;

        if (elapsed_us < 0) {
            ESP_LOGE(TAG, "Negative elapsed time; invalid sample");
            stop_receiver();
            return false;
        }

        if (i >= WARMUP_SAMPLES) {
            latency_samples[i - WARMUP_SAMPLES] = elapsed_us;
        }

        /*
         * For polling mode, wait until the receiver returns to its active
         * polling state. For blocked mode, it publishes receiver_waiting
         * before entering its next notification wait.
         */
        if (!wait_for_flag(&receiver_waiting, true)) {
            ESP_LOGE(TAG, "Receiver failed to re-arm after sample %u", (unsigned)i);
            stop_receiver();
            return false;
        }
    }

    stop_receiver();

    ESP_LOGI(TAG, "Results (elapsed microseconds):");
    print_statistics(latency_samples, NUM_SAMPLES);
    ESP_LOGI(TAG, "========================================");

    return true;
}

static void experiment_task(void *arg)
{
    (void)arg;
    sender_task_handle = xTaskGetCurrentTaskHandle();

    ESP_LOGI(TAG, "V-CORE EXPERIMENT 008");
    ESP_LOGI(TAG, "Synchronization Latency Characterization");
    ESP_LOGI(TAG, "Timing source: esp_timer_get_time()");
    ESP_LOGI(TAG, "Four tests: same/cross core x polling/blocked receiver");
    ESP_LOGI(TAG, "Same sender-side acknowledgment protocol in all tests.");
    ESP_LOGI(TAG, "Metric includes scheduling, request and acknowledgment work.");
    ESP_LOGI(TAG, "========================================");

    for (int i = 0; i < TEST_COUNT; i++) {
        if (!run_one_test((test_id_t)i)) {
            ESP_LOGE(TAG, "Test %d failed; stopping experiment", i + 1);
            break;
        }
    }

    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "EXPERIMENT 008 FINISHED");
    ESP_LOGI(TAG, "========================================");

    vTaskDelete(NULL);
}

void app_main(void)
{
    BaseType_t rc = xTaskCreatePinnedToCore(
        experiment_task,
        "exp008_task",
        EXPERIMENT_STACK,
        NULL,
        TEST_PRIORITY + 1,
        NULL,
        CORE_A
    );

    if (rc != pdPASS) {
        ESP_LOGE(TAG, "Failed to create Experiment 008 task");
    }
}
