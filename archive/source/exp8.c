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
 * V-CORE: EXPERIMENT 008
 * Synchronization round-trip latency characterization.
 *
 * A: Same core, receiver ready/polling.
 * B: Same core, receiver blocked on a task notification.
 * C: Cross-core, receiver ready/polling.
 * D: Cross-core, receiver blocked on a task notification.
 *
 * The measured metric is sender-side elapsed time from publishing a
 * request until the sender observes the receiver's acknowledgment.
 * It includes scheduling/notification/acknowledgment overhead; it is
 * not a pure one-way hardware signaling delay.
 */

#define NUM_SAMPLES       1000
#define WARMUP_SAMPLES    100
#define TASK_STACK_SIZE   4096
#define EXPERIMENT_STACK  8192
#define TEST_TIMEOUT_US   2000000LL
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
    bool receiver_stays_ready;
} test_config_t;

static const test_config_t tests[TEST_COUNT] = {
    { "A: Same-core / receiver ready",    CORE_A, CORE_A, true  },
    { "B: Same-core / receiver blocked",  CORE_A, CORE_A, false },
    { "C: Cross-core / receiver ready",   CORE_A, CORE_B, true  },
    { "D: Cross-core / receiver blocked", CORE_A, CORE_B, false }
};

static TaskHandle_t sender_task_handle;
static TaskHandle_t receiver_task_handle;

/* Aligned 32-bit shared sequence/state variables. */
static volatile uint32_t current_sequence;
static volatile uint32_t receiver_ack_sequence;
static volatile bool receiver_ready;
static volatile bool receiver_exit;

/* Static storage avoids consuming 8 KB of task stack for sorting. */
static int64_t latency_samples[NUM_SAMPLES];
static int64_t sorted_samples[NUM_SAMPLES];

static void receiver_task(void *arg)
{
    const test_config_t *cfg = (const test_config_t *)arg;
    uint32_t seen_sequence = 0;

    receiver_ready = true;

    for (;;) {
        if (receiver_exit) {
            break;
        }

        if (cfg->receiver_stays_ready) {
            uint32_t seq = current_sequence;

            if (seq == seen_sequence) {
                taskYIELD();
                continue;
            }

            seen_sequence = seq;
            receiver_ack_sequence = seq;

            /* A notification wakes the sender if it is waiting. */
            xTaskNotifyGive(sender_task_handle);
        } else {
            /*
             * This task blocks here between requests. The sender waits
             * until the task state is eBlocked before timing each request.
             */
            ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

            if (receiver_exit) {
                break;
            }

            uint32_t seq = current_sequence;
            seen_sequence = seq;
            receiver_ack_sequence = seq;
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

static bool wait_until_ready(void)
{
    int64_t deadline = esp_timer_get_time() + TEST_TIMEOUT_US;

    while (!receiver_ready) {
        if (esp_timer_get_time() >= deadline) {
            return false;
        }
        taskYIELD();
    }

    return true;
}

static bool wait_until_receiver_blocked(void)
{
    int64_t deadline = esp_timer_get_time() + TEST_TIMEOUT_US;

    while (eTaskGetState(receiver_task_handle) != eBlocked) {
        if (esp_timer_get_time() >= deadline) {
            return false;
        }
        taskYIELD();
    }

    return true;
}

static bool wait_for_ack(uint32_t expected_sequence, bool blocked_receiver)
{
    int64_t deadline = esp_timer_get_time() + TEST_TIMEOUT_US;

    if (blocked_receiver) {
        int64_t remaining_us = deadline - esp_timer_get_time();
        TickType_t timeout_ticks =
            (TickType_t)((remaining_us * configTICK_RATE_HZ) / 1000000LL);

        if (timeout_ticks < 1) {
            timeout_ticks = 1;
        }

        if (ulTaskNotifyTake(pdTRUE, timeout_ticks) == 0) {
            return false;
        }

        return receiver_ack_sequence == expected_sequence;
    }

    while (receiver_ack_sequence != expected_sequence) {
        if (esp_timer_get_time() >= deadline) {
            return false;
        }
        taskYIELD();
    }

    return true;
}

static void stop_receiver(void)
{
    receiver_exit = true;
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
    ESP_LOGI(TAG, "Metric: sender-side request-to-acknowledgment elapsed time");
    ESP_LOGI(TAG, "========================================");

    current_sequence = 0;
    receiver_ack_sequence = 0;
    receiver_ready = false;
    receiver_exit = false;

    BaseType_t rc = xTaskCreatePinnedToCore(
        receiver_task,
        "exp008_receiver",
        TASK_STACK_SIZE,
        (void *)cfg,
        TEST_PRIORITY,
        &receiver_task_handle,
        cfg->receiver_core
    );

    if (rc != pdPASS) {
        ESP_LOGE(TAG, "Failed to create receiver task");
        return false;
    }

    if (!wait_until_ready()) {
        ESP_LOGE(TAG, "Receiver failed to become ready");
        stop_receiver();
        return false;
    }

    /* Let the receiver enter its polling or blocked wait loop. */
    vTaskDelay(pdMS_TO_TICKS(10));

    const size_t total_samples = WARMUP_SAMPLES + NUM_SAMPLES;

    for (size_t i = 0; i < total_samples; i++) {
        uint32_t seq = (uint32_t)i + 1;

        if (!cfg->receiver_stays_ready) {
            if (!wait_until_receiver_blocked()) {
                ESP_LOGE(TAG, "Receiver did not block before sample %u",
                         (unsigned)i);
                stop_receiver();
                return false;
            }

            /* Clear any stale sender notification before the exchange. */
            (void)ulTaskNotifyTake(pdTRUE, 0);
        }

        int64_t start_us = esp_timer_get_time();
        current_sequence = seq;

        if (!cfg->receiver_stays_ready) {
            xTaskNotifyGive(receiver_task_handle);
        }

        if (!wait_for_ack(seq, !cfg->receiver_stays_ready)) {
            ESP_LOGE(TAG, "Timeout or sequence mismatch at sample %u",
                     (unsigned)i);
            stop_receiver();
            return false;
        }

        /*
         * Take the end timestamp on the sender after it observes the ack.
         * This avoids sharing non-atomic 64-bit timestamps between cores.
         */
        int64_t elapsed_us = esp_timer_get_time() - start_us;

        if (elapsed_us < 0) {
            ESP_LOGE(TAG, "Negative elapsed time; invalid sample");
            stop_receiver();
            return false;
        }

        if (i >= WARMUP_SAMPLES) {
            latency_samples[i - WARMUP_SAMPLES] = elapsed_us;
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
    ESP_LOGI(TAG, "Four tests: same/cross core x ready/blocked receiver");
    ESP_LOGI(TAG, "Reported metric includes scheduling and acknowledgment.");
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
        TEST_PRIORITY,
        NULL,
        CORE_A
    );

    if (rc != pdPASS) {
        ESP_LOGE(TAG, "Failed to create Experiment 008 task");
    }
}
