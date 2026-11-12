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
 * V-CORE EXPERIMENT 008 — FINAL CANDIDATE
 *
 * Measures sender-side request-publication to sender-observed acknowledgment
 * elapsed time for four configurations:
 * A: same core, receiver polls for request sequence changes
 * B: same core, receiver waits for a task notification
 * C: cross-core, receiver polls for request sequence changes
 * D: cross-core, receiver waits for a task notification
 *
 * This is end-to-end request/acknowledgment latency, not pure notification
 * overhead or one-way signaling delay. It includes receiver processing,
 * scheduling, acknowledgment delivery, and timer-read overhead.
 *
 * Protocol:
 * - ready_sequence identifies the next request the receiver is armed to accept.
 * - Sender waits for ready_sequence == request sequence before each sample.
 * - In notification-wait mode, sender yields for one RTOS tick after readiness
 *   and before starting the timer, giving the receiver time to enter its wait.
 * - request_sequence and acknowledgment sequence are atomic 32-bit values.
 * - Receiver exit is acknowledged before the next test reuses shared state.
 *
 * Note: the one-tick pre-sample settling delay is outside the timed interval.
 * It improves the blocked-mode setup but is not a formal proof of task state.
 */

#define NUM_SAMPLES       1000
#define WARMUP_SAMPLES    100
#define RECEIVER_STACK    4096
#define EXPERIMENT_STACK  8192
#define TEST_TIMEOUT_MS   2000
#define CORE_A            0
#define CORE_B            1
#define TEST_PRIORITY     5

/*
 * Build check:
 * Confirm eTaskGetState() is enabled/available in the project's
 * ESP-IDF FreeRTOS configuration. The compiler will flag it if unavailable.
 */

static const char *TAG = "V-CORE-EXP008";

typedef enum {
    TEST_SAME_POLL = 0,
    TEST_SAME_NOTIFY,
    TEST_CROSS_POLL,
    TEST_CROSS_NOTIFY,
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
    { "B: Same-core / receiver notification-wait", CORE_A, CORE_A, false },
    { "C: Cross-core / receiver polling", CORE_A, CORE_B, true  },
    { "D: Cross-core / receiver notification-wait", CORE_A, CORE_B, false }
};

static TaskHandle_t sender_task_handle;
static TaskHandle_t receiver_task_handle;

static uint32_t request_sequence;
static uint32_t acknowledgment_sequence;
static uint32_t ready_sequence;
static bool receiver_exit;
static bool receiver_exited;

static int64_t latency_samples[NUM_SAMPLES];
static int64_t sorted_samples[NUM_SAMPLES];

static inline void store_u32(uint32_t *ptr, uint32_t value)
{
    __atomic_store_n(ptr, value, __ATOMIC_RELEASE);
}

static inline uint32_t load_u32(const uint32_t *ptr)
{
    return __atomic_load_n(ptr, __ATOMIC_ACQUIRE);
}

static inline void store_bool(bool *ptr, bool value)
{
    __atomic_store_n(ptr, value, __ATOMIC_RELEASE);
}

static inline bool load_bool(const bool *ptr)
{
    return __atomic_load_n(ptr, __ATOMIC_ACQUIRE);
}

static bool wait_for_u32(uint32_t *ptr, uint32_t expected)
{
    const int64_t deadline = esp_timer_get_time() + (int64_t)TEST_TIMEOUT_MS * 1000;

    while (load_u32(ptr) != expected) {
        if (esp_timer_get_time() >= deadline) {
            return false;
        }
        taskYIELD();
    }
    return true;
}

static bool wait_for_bool(bool *ptr, bool expected)
{
    const int64_t deadline = esp_timer_get_time() + (int64_t)TEST_TIMEOUT_MS * 1000;

    while (load_bool(ptr) != expected) {
        if (esp_timer_get_time() >= deadline) {
            return false;
        }
        taskYIELD();
    }
    return true;
}

/*
 * Wait until the receiver task is actually blocked.
 *
 * This is used only for notification-wait tests and is deliberately called
 * before the timed interval. In this protocol, after publishing ready_sequence,
 * the receiver's next blocking operation is ulTaskNotifyTake().
 */
static bool wait_until_receiver_blocked(void)
{
    const int64_t deadline = esp_timer_get_time() + (int64_t)TEST_TIMEOUT_MS * 1000;

    while (eTaskGetState(receiver_task_handle) != eBlocked) {
        if (esp_timer_get_time() >= deadline) {
            return false;
        }
        taskYIELD();
    }

    return true;
}

static void receiver_task(void *arg)
{
    const test_config_t *cfg = (const test_config_t *)arg;
    uint32_t seen_sequence = 0;

    for (;;) {
        if (load_bool(&receiver_exit)) {
            break;
        }

        /* Announce the exact next sequence this receiver is prepared to handle. */
        store_u32(&ready_sequence, seen_sequence + 1U);

        if (cfg->receiver_polls) {
            uint32_t seq;
            do {
                if (load_bool(&receiver_exit)) {
                    goto receiver_done;
                }
                seq = load_u32(&request_sequence);
                if (seq == seen_sequence) {
                    taskYIELD();
                }
            } while (seq == seen_sequence);

            /* Reject unexpected sequence progression rather than silently accepting it. */
            if (seq != seen_sequence + 1U) {
                ESP_LOGE(TAG, "Polling receiver sequence error: seen=%" PRIu32 ", got=%" PRIu32,
                         seen_sequence, seq);
                goto receiver_done;
            }
            seen_sequence = seq;
        } else {
            TickType_t wait_ticks = pdMS_TO_TICKS(TEST_TIMEOUT_MS);
            if (wait_ticks < 1) wait_ticks = 1;

            if (ulTaskNotifyTake(pdTRUE, wait_ticks) == 0) {
                if (load_bool(&receiver_exit)) {
                    break;
                }
                ESP_LOGE(TAG, "Receiver notification wait timed out");
                goto receiver_done;
            }

            if (load_bool(&receiver_exit)) {
                break;
            }

            uint32_t seq = load_u32(&request_sequence);
            if (seq != seen_sequence + 1U) {
                ESP_LOGE(TAG, "Notification receiver sequence error: seen=%" PRIu32 ", got=%" PRIu32,
                         seen_sequence, seq);
                goto receiver_done;
            }
            seen_sequence = seq;
        }

        store_u32(&acknowledgment_sequence, seen_sequence);
        xTaskNotifyGive(sender_task_handle);
    }

receiver_done:
    store_bool(&receiver_exited, true);
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

    const double mean = (double)sum / (double)count;
    for (size_t i = 0; i < count; i++) {
        const double d = (double)source[i] - mean;
        squared_deviation_sum += d * d;
    }

    const double stddev = sqrt(squared_deviation_sum / (double)count);
    const size_t median_index = count / 2;
    const size_t p95_index = (count * 95 / 100) - 1;
    const size_t p99_index = (count * 99 / 100) - 1;

    ESP_LOGI(TAG, "  Min: %" PRId64 " us", sorted_samples[0]);
    ESP_LOGI(TAG, "  Mean: %.3f us", mean);
    ESP_LOGI(TAG, "  Median: %" PRId64 " us", sorted_samples[median_index]);
    ESP_LOGI(TAG, "  Std deviation: %.3f us", stddev);
    ESP_LOGI(TAG, "  P95: %" PRId64 " us", sorted_samples[p95_index]);
    ESP_LOGI(TAG, "  P99: %" PRId64 " us", sorted_samples[p99_index]);
    ESP_LOGI(TAG, "  Max: %" PRId64 " us", sorted_samples[count - 1]);
}

static bool wait_for_sender_ack(uint32_t expected_sequence)
{
    TickType_t timeout_ticks = pdMS_TO_TICKS(TEST_TIMEOUT_MS);
    if (timeout_ticks < 1) timeout_ticks = 1;

    if (ulTaskNotifyTake(pdTRUE, timeout_ticks) == 0) {
        return false;
    }
    return load_u32(&acknowledgment_sequence) == expected_sequence;
}

static bool stop_receiver(void)
{
    store_bool(&receiver_exit, true);
    /* Wakes notification-wait mode; polling mode observes the exit flag. */
    xTaskNotifyGive(receiver_task_handle);

    if (!wait_for_bool(&receiver_exited, true)) {
        ESP_LOGE(TAG, "Receiver failed to confirm shutdown");
        return false;
    }
    return true;
}

static bool run_one_test(test_id_t id)
{
    const test_config_t *cfg = &tests[id];

    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "%s", cfg->name);
    ESP_LOGI(TAG, "Sender core: %d; receiver core: %d",
             (int)cfg->sender_core, (int)cfg->receiver_core);
    ESP_LOGI(TAG, "Warm-up: %d; measured: %d", WARMUP_SAMPLES, NUM_SAMPLES);
    ESP_LOGI(TAG, "Metric: request publication to sender-observed acknowledgment");
    ESP_LOGI(TAG, "========================================");

    store_u32(&request_sequence, 0);
    store_u32(&acknowledgment_sequence, 0);
    store_u32(&ready_sequence, 0);
    store_bool(&receiver_exit, false);
    store_bool(&receiver_exited, false);

    BaseType_t rc = xTaskCreatePinnedToCore(
        receiver_task,
        "exp008_receiver",
        RECEIVER_STACK,
        (void *)cfg,
        TEST_PRIORITY + 1,
        &receiver_task_handle,
        cfg->receiver_core);

    if (rc != pdPASS) {
        ESP_LOGE(TAG, "Failed to create receiver task");
        return false;
    }

    const size_t total_samples = WARMUP_SAMPLES + NUM_SAMPLES;

    for (size_t i = 0; i < total_samples; i++) {
        const uint32_t seq = (uint32_t)i + 1U;

        if (!wait_for_u32(&ready_sequence, seq)) {
            ESP_LOGE(TAG, "Receiver did not arm for sample %u", (unsigned)i);
            (void)stop_receiver();
            return false;
        }

        /*
         * For notification-wait tests, verify that the receiver has actually
         * entered the blocked state before starting the timed exchange.
         * This check is outside the measured interval.
         */
        if (!cfg->receiver_polls && !wait_until_receiver_blocked()) {
            ESP_LOGE(TAG, "Receiver did not enter blocked state before sample %u",
                     (unsigned)i);
            (void)stop_receiver();
            return false;
        }

        /* Clear any stale sender notification before publishing this request. */
        (void)ulTaskNotifyTake(pdTRUE, 0);

        const int64_t start_us = esp_timer_get_time();
        store_u32(&request_sequence, seq);

        if (!cfg->receiver_polls) {
            xTaskNotifyGive(receiver_task_handle);
        }

        if (!wait_for_sender_ack(seq)) {
            ESP_LOGE(TAG, "Acknowledgment timeout/mismatch at sample %u; ack=%" PRIu32,
                     (unsigned)i, load_u32(&acknowledgment_sequence));
            (void)stop_receiver();
            return false;
        }

        const int64_t elapsed_us = esp_timer_get_time() - start_us;
        if (elapsed_us < 0) {
            ESP_LOGE(TAG, "Negative elapsed time; invalid sample");
            (void)stop_receiver();
            return false;
        }

        if (i >= WARMUP_SAMPLES) {
            latency_samples[i - WARMUP_SAMPLES] = elapsed_us;
        }
    }

    if (!stop_receiver()) {
        return false;
    }

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
    ESP_LOGI(TAG, "Four tests: same/cross core x polling/notification-wait receiver");
    ESP_LOGI(TAG, "Metric includes scheduling, request and acknowledgment work.");
    ESP_LOGI(TAG, "Notification-wait tests verify eBlocked state before each timed request.");
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
        CORE_A);

    if (rc != pdPASS) {
        ESP_LOGE(TAG, "Failed to create Experiment 008 task");
    }
}
