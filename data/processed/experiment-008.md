Experiment 008: Synchronization Latency Characterization

1. Objective

Measure sender-side request-to-acknowledgment latency on the ESP32 under four configurations:

* Same-core execution with a polling receiver.
* Same-core execution with a notification-wait receiver.
* Cross-core execution with a polling receiver.
* Cross-core execution with a notification-wait receiver.

The objective is to characterize the elapsed time associated with request delivery, receiver processing, acknowledgment delivery, and task scheduling.

2. Hardware and Software Configuration

Parameter	Configuration
Board	ESP32 DevKit V1
Module	ESP32-WROOM-32
Processor	Dual-core Xtensa LX6
CPU frequency	240 MHz
Framework	ESP-IDF v6.1
Operating system	FreeRTOS
Timing source	esp_timer_get_time()
Sender core	Core 0
Receiver core, same-core tests	Core 0
Receiver core, cross-core tests	Core 1
Warm-up samples per test	100
Measured samples per test	1,000
Total measured samples	4,000

3. Measurement Methodology

The sender publishes a request containing a sequence number and records the start timestamp. The receiver processes the request, publishes the corresponding acknowledgment sequence, and notifies the sender.

The sender waits for the acknowledgment and records the elapsed time.

Measured metric: Request publication to sender-observed acknowledgment, in microseconds.

The measurement includes:

* Request publication and observation.
* Receiver scheduling and request processing.
* Acknowledgment publication and notification.
* Sender scheduling and acknowledgment observation.
* Timing instrumentation overhead.

This is an end-to-end request-to-acknowledgment measurement. It is not a measurement of pure notification overhead or one-way signaling latency.

The notification-wait configurations include an untimed RTOS-tick settling delay after receiver readiness is announced.

4. Experimental Configurations

Test	Configuration	Sender Core	Receiver Core	Receiver Behavior
A	Same-core polling	0	0	Actively polls for requests
B	Same-core notification-wait	0	0	Waits using a FreeRTOS task notification
C	Cross-core polling	0	1	Actively polls for requests
D	Cross-core notification-wait	0	1	Waits using a FreeRTOS task notification

5. Results

Summary Statistics (Four-Run Averages)

All values below are the averages across four independent runs of the current Experiment 008 implementation (exp8v3.c). Each run executed 100 warm-up + 1,000 measured samples per configuration (4,000 measured samples per run, 16,000 total measured samples).

Metric	A: Same-Core Polling	B: Same-Core Notification-Wait	C: Cross-Core Polling	D: Cross-Core Notification-Wait
Minimum (µs)	20	25	18	24
Mean (µs)	20.776	25.794	18.825	28.650
Median (µs)	21	26	19	29
Standard deviation (µs)	0.677	0.546	0.647	0.560
P95 (µs)	21	26	19	29
P99 (µs)	21	26	19	29
Maximum (µs)	33	33	34	35

Individual Run Means (µs):
Run 1: 20.785, 26.024, 18.805, 28.655
Run 2: 20.771, 25.729, 18.825, 28.650
Run 3: 20.776, 25.703, 18.838, 28.645
Run 4: 20.771, 25.718, 18.833, 28.649

Test A: Same-Core Polling

* Sender core: Core 0
* Receiver core: Core 0
* Four-run mean latency: 20.776 µs (Run 1: 20.785, Run 2: 20.771, Run 3: 20.776, Run 4: 20.771)
* Median latency: 21 µs
* P95 latency: 21 µs
* Maximum latency: 33 µs

Test B: Same-Core Notification-Wait

* Sender core: Core 0
* Receiver core: Core 0
* Four-run mean latency: 25.794 µs (Run 1: 26.024, Run 2: 25.729, Run 3: 25.703, Run 4: 25.718)
* Median latency: 26 µs
* P95 latency: 26 µs
* Maximum latency: 33 µs

Test C: Cross-Core Polling

* Sender core: Core 0
* Receiver core: Core 1
* Four-run mean latency: 18.825 µs (Run 1: 18.805, Run 2: 18.825, Run 3: 18.838, Run 4: 18.833)
* Median latency: 19 µs
* P95 latency: 19 µs
* Maximum latency: 34 µs

Test D: Cross-Core Notification-Wait

* Sender core: Core 0
* Receiver core: Core 1
* Four-run mean latency: 28.650 µs (Run 1: 28.655, Run 2: 28.650, Run 3: 28.645, Run 4: 28.649)
* Median latency: 29 µs
* P95 latency: 29 µs
* Maximum latency: 35 µs

6. Comparative Analysis

Same-Core Comparison: A vs. B

Metric	Polling	Notification-Wait	Difference
Mean latency	20.776 µs	25.794 µs	5.018 µs

The notification-wait configuration recorded a mean latency approximately 24.1% higher than the polling configuration across four runs.

Cross-Core Comparison: C vs. D

Metric	Polling	Notification-Wait	Difference
Mean latency	18.825 µs	28.650 µs	9.825 µs

The notification-wait configuration recorded a mean latency approximately 52.2% higher than the polling configuration across four runs.

These percentages describe the observed four-run means. They do not establish that polling is universally faster than notification-based waiting.

Same-Core vs. Cross-Core Polling

Cross-core polling recorded a mean latency of 18.825 µs, compared with 20.776 µs for same-core polling.

The cross-core polling mean was approximately 1.951 µs lower across four runs. Further protocol validation is required before drawing conclusions about the effect of core placement.

Same-Core vs. Cross-Core Notification-Wait

Cross-core notification-wait recorded a mean latency of 28.650 µs, compared with 25.794 µs for same-core notification-wait.

The cross-core mean was approximately 2.856 µs higher across four runs.

The results show different observed behavior across the two receiver modes. They do not, by themselves, identify the underlying cause.

7. Observations

1. All four tests completed in each of the four independent runs.
2. The lowest observed mean latency was 18.825 µs in Test C, cross-core polling.
3. The highest observed mean latency was 28.650 µs in Test D, cross-core notification-wait.
4. Notification-wait recorded higher mean latency than polling in both the same-core and cross-core comparisons across all four runs.
5. The maximum recorded latency ranged from 33 to 35 µs across the four tests.
6. The observed standard deviations ranged from 0.546 to 0.677 µs.
7. These statistics characterize four independent runs and should not be interpreted as proof of worst-case latency or hard real-time guarantees.

8. Limitations

* The measurements include scheduling, request processing, acknowledgment delivery, and timing overhead.
* The experiment does not isolate the cost of an individual FreeRTOS notification operation.
* A settling delay after readiness is announced does not independently prove that the receiver was already blocked before every request.
* The current results represent four independent runs; repeatability across independent runs has been established.
* The measurements do not establish universal performance advantages for polling, notification-wait, same-core execution, or cross-core execution.
* The experiment does not measure the computational speedup of V-Core’s dual-core vector computation.

Validation note: The firmware completed all four tests without timeout or acknowledgment-mismatch errors in the recorded serial output. The exact receiver-state protocol should still be audited before making a rigorous claim that the notification-wait tests measured a receiver that was already blocked before each request.

9. Conclusion

Experiment 008 characterized sender-side request-to-acknowledgment latency for four receiver configurations on the ESP32-WROOM-32 at 240 MHz.

In the recorded run, polling produced lower mean latency than notification-wait in both same-core and cross-core configurations. Cross-core polling recorded the lowest mean latency, while cross-core notification-wait recorded the highest.

These are observations from the current implementation, not universal conclusions about synchronization mechanisms. The results should be retained alongside the exact firmware source and raw serial output, with the receiver-state validation limitation documented.

10. Artifacts and Reproducibility

Preserve the following artifacts together:

* main/vcore.c — exact source used for this run.
* logs/experiment-008.md — experiment methodology and summarized results.
* logs/experiment-008-serial.txt — complete raw serial output.

Do not overwrite earlier Experiment 008 logs. Record any future protocol changes or repeated runs separately so that results remain traceable to the firmware version that produced them.


I (169) cpu_start: Pro cpu start user code
I (169) cpu_start: cpu freq: 240000000 Hz
I (171) app_init: Application information:
I (174) app_init: Project name:     vcore
I (178) app_init: App version:      1
I (182) app_init: Compile time:     Oct 15 2026 12:07:14
I (187) app_init: ELF file SHA256:  5d420d33b...
I (191) app_init: ESP-IDF:          v6.1
I (195) efuse_init: Min chip rev:     v0.0
I (198) efuse_init: Max chip rev:     v3.99 
I (202) efuse_init: Chip rev:         v3.1
I (206) heap_init: Initializing. RAM available for dynamic allocation:
I (213) heap_init: At 3FFAE6E0 len 00001920 (6 KiB): DRAM
I (218) heap_init: At 3FFB73D0 len 00028C30 (163 KiB): DRAM
I (223) heap_init: At 3FFE0440 len 00003AE0 (14 KiB): D/IRAM
I (228) heap_init: At 3FFE4350 len 0001BCB0 (111 KiB): D/IRAM
I (234) heap_init: At 4008AC00 len 00015400 (85 KiB): IRAM
I (240) spi_flash: detected chip: generic
I (243) spi_flash: flash io: dio
I (247) main_task: Started on CPU0
I (247) main_task: Calling app_main()
I (247) V-CORE-EXP008: V-CORE EXPERIMENT 008
I (247) V-CORE-EXP008: Synchronization Latency Characterization
I (257) V-CORE-EXP008: Timing source: esp_timer_get_time()
I (267) V-CORE-EXP008: Four tests: same/cross core x polling/notification-wait receiver
I (267) V-CORE-EXP008: Metric includes scheduling, request and acknowledgment work.
I (277) V-CORE-EXP008: Notification-wait setup includes one untimed RTOS tick settling delay.
I (287) V-CORE-EXP008: ========================================
I (287) V-CORE-EXP008: 
I (297) V-CORE-EXP008: ========================================
I (297) V-CORE-EXP008: A: Same-core / receiver polling
I (307) V-CORE-EXP008: Sender core: 0; receiver core: 0
I (307) V-CORE-EXP008: Warm-up: 100; measured: 1000
I (317) V-CORE-EXP008: Metric: request publication to sender-observed acknowledgment
I (317) V-CORE-EXP008: ========================================
I (357) V-CORE-EXP008: Results (elapsed microseconds):
I (367) V-CORE-EXP008:   Min: 20 us
I (367) V-CORE-EXP008:   Mean: 20.782 us
I (367) V-CORE-EXP008:   Median: 21 us
I (367) V-CORE-EXP008:   Std deviation: 0.677 us
I (367) V-CORE-EXP008:   P95: 21 us
I (367) V-CORE-EXP008:   P99: 21 us
I (377) V-CORE-EXP008:   Max: 33 us
I (377) V-CORE-EXP008: ========================================
I (377) V-CORE-EXP008: 
I (387) V-CORE-EXP008: ========================================
I (387) V-CORE-EXP008: B: Same-core / receiver notification-wait
I (397) V-CORE-EXP008: Sender core: 0; receiver core: 0
I (397) V-CORE-EXP008: Warm-up: 100; measured: 1000
I (407) V-CORE-EXP008: Metric: request publication to sender-observed acknowledgment
I (417) V-CORE-EXP008: ========================================
I (457) V-CORE-EXP008: Results (elapsed microseconds):
I (467) V-CORE-EXP008:   Min: 25 us
I (467) V-CORE-EXP008:   Mean: 25.868 us
I (467) V-CORE-EXP008:   Median: 26 us
I (467) V-CORE-EXP008:   Std deviation: 0.546 us
I (467) V-CORE-EXP008:   P95: 26 us
I (477) V-CORE-EXP008:   P99: 26 us
I (477) V-CORE-EXP008:   Max: 33 us
I (477) V-CORE-EXP008: ========================================
I (487) V-CORE-EXP008: 
I (487) V-CORE-EXP008: ========================================
I (497) V-CORE-EXP008: C: Cross-core / receiver polling
I (497) V-CORE-EXP008: Sender core: 0; receiver core: 1
I (507) V-CORE-EXP008: Warm-up: 100; measured: 1000
I (507) V-CORE-EXP008: Metric: request publication to sender-observed acknowledgment
I (517) V-CORE-EXP008: ========================================
I (517) main_task: Returned from app_main()
I (547) V-CORE-EXP008: Results (elapsed microseconds):
I (557) V-CORE-EXP008:   Min: 18 us
I (557) V-CORE-EXP008:   Mean: 18.818 us
I (557) V-CORE-EXP008:   Median: 19 us
I (557) V-CORE-EXP008:   Std deviation: 0.647 us
I (557) V-CORE-EXP008:   P95: 19 us
I (567) V-CORE-EXP008:   P99: 19 us
I (567) V-CORE-EXP008:   Max: 34 us
I (567) V-CORE-EXP008: ========================================
I (577) V-CORE-EXP008: 
I (577) V-CORE-EXP008: ========================================
I (587) V-CORE-EXP008: D: Cross-core / receiver notification-wait
I (587) V-CORE-EXP008: Sender core: 0; receiver core: 1
I (597) V-CORE-EXP008: Warm-up: 100; measured: 1000
I (597) V-CORE-EXP008: Metric: request publication to sender-observed acknowledgment
I (607) V-CORE-EXP008: ========================================
I (657) V-CORE-EXP008: Results (elapsed microseconds):
I (667) V-CORE-EXP008:   Min: 24 us
I (667) V-CORE-EXP008:   Mean: 28.505 us
I (667) V-CORE-EXP008:   Median: 29 us
I (667) V-CORE-EXP008:   Std deviation: 0.560 us
I (667) V-CORE-EXP008:   P95: 29 us
I (677) V-CORE-EXP008:   P99: 29 us
I (677) V-CORE-EXP008:   Max: 35 us
I (677) V-CORE-EXP008: ========================================
I (687) V-CORE-EXP008: 
I (687) V-CORE-EXP008: ========================================
I (697) V-CORE-EXP008: EXPERIMENT 008 FINISHED
I (697) V-CORE-EXP008: ========================================