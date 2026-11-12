# V-Core Experiment Log

## Experiment 001 — Dot-product baseline

**Date:** 2026-10-14  
**Status:** Completed  
**Project:** V-Core  
**Board:** ESP32 (Xtensa)  
**CPU frequency assumed for conversion:** 160 MHz  
**Firmware environment:** ESP-IDF 6.1.0  
**Measurement method:** `esp_cpu_get_cycle_count()`  
**Trials per workload:** 1,000  

### Objective

Establish a baseline for the execution cost of an integer dot product at two input sizes, verify numerical correctness, and observe how cycle counts scale with workload size.

### Workload

The firmware initializes two deterministic vectors:

```c
a[i] = (int32_t)(i % 100) - 50;
b[i] = (int32_t)(i % 70) - 35;
```

It computes:

```c
sum += (int64_t)a[i] * b[i];
```

The tested vector sizes were 64 and 1,024 elements.

### Results

| Metric | Small workload | Large workload |
|---|---:|---:|
| Vector size | 64 | 1,024 |
| Trials | 1,000 | 1,000 |
| Computed result | 25,984 | 15,634 |
| Expected result | 25,984 | 15,634 |
| Correctness check | PASS | PASS |
| Minimum | 1,974 cycles | 31,716 cycles |
| Median | 1,974 cycles | 31,716 cycles |
| Mean | 1,976.63 cycles | 31,742.17 cycles |
| Maximum | 3,292 cycles | 33,033 cycles |

### Derived calculations

Assuming the CPU runs at 160 MHz:

- One cycle is approximately 6.25 ns.
- 64-element median: `1,974 / 160,000,000` ≈ **12.34 µs**.
- 1,024-element median: `31,716 / 160,000,000` ≈ **198.23 µs**.
- Workload-size ratio: `1,024 / 64` = **16×**.
- Median cycle-count ratio: `31,716 / 1,974` ≈ **16.06×**.

The measured median cycle count scales approximately linearly with the number of elements for these two workloads.

### Initial observations

1. Both workloads passed their expected-result checks.
2. Increasing the vector size by 16× increased the median cycle count by approximately 16.06×.
3. The observed minimum-to-maximum ranges were:
   - 64 elements: `3,292 - 1,974 = 1,318` cycles.
   - 1,024 elements: `33,033 - 31,716 = 1,317` cycles.
4. The minimum and median were identical for both workloads. The sample distribution should be examined before drawing conclusions about how often measurements landed at the minimum.
5. The similar observed ranges may be consistent with occasional runtime interference, but these measurements alone do not identify the cause.

### Limitations

- These are observed execution-cycle measurements under the current firmware build and runtime conditions.
- The results do not establish worst-case execution time (WCET).
- The results do not prove that interrupts or task scheduling caused the upper-tail measurements.
- The conversion to microseconds assumes a stable 160 MHz CPU clock.
- The expected values validate the implementation against the chosen deterministic input and reference calculation; they do not by themselves prove the benchmark is free from all measurement bias.
- Compiler barriers were used around the measured computation to discourage memory operations from moving across the timing boundaries. This does not remove all measurement overhead or runtime interference.

### Next experiment

Extend the measurement analysis to calculate:

- Standard deviation.
- 90th, 95th, and 99th percentiles.
- Number and percentage of samples above the minimum.

Retain the raw per-trial cycle samples in `results/raw/` so the distribution can be reanalysed later. Keep the firmware source and build configuration associated with each result.

### Reproduction notes

Project directory:

```text
/Users/prajwalnavadagp/Engineering/Projects/V-Core/vcore
```

Serial device used:

```text
/dev/cu.usbserial-0001
```

Firmware was built and run with ESP-IDF 6.1.0. Record the exact commit, build configuration, CPU frequency configuration, and firmware changes when these are available for a formal report.
