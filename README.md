# V-Core: Dual-Core Parallel Computing on ESP32

V-Core is a measurement-first investigation of dual-core parallel computing on the **ESP32-WROOM-32** (dual-core Xtensa LX6 @ 240 MHz). The project characterizes computational latency, synchronization overhead, cross-core interference, and workload isolation through **11 controlled experiments** executed on physical hardware.

**Key Result**: **48.55×** system-event latency improvement via core separation (Experiment 011, ABBA validation).

---

## Hardware & Software

| Component | Specification |
|-----------|---------------|
| **Board** | ESP32 DevKit V1 (ESP32-WROOM-32, silicon rev v3.1) |
| **Processor** | Dual-core Xtensa LX6 @ 240 MHz |
| **Framework** | ESP-IDF v6.1 |
| **RTOS** | FreeRTOS SMP |
| **Language** | C (C99) with Xtensa `rsr.ccount` intrinsics |
| **Build System** | CMake + Ninja |
| **Timing Resolution** | 4.17 ns nominal cycle interval at 240 MHz (CCOUNT) |

---

## Experiment Summary

### Phase 1: Measurement Foundation (Experiments 007, 008)
| Exp | Title | Key Finding |
|-----|-------|-------------|
| 007 | Core Placement Comparison | Core 0 ≡ Core 1 median latency; Core 1 shows lower variance |
| 008 | Synchronization Latency | 4 configs × 4 runs: polling outperforms notification-wait; cross-core polling fastest (18.8 µs) |

### Phase 2: Parallel Computation & Analysis (Experiments 006, 009, 010, 011)
| Exp | Title | Key Finding |
|-----|-------|-------------|
| 006 | Computational Baseline | ~30 cycles/element; repeatability validated (2 runs, exact median match) |
| 009 | Workload Interference | Core 1 load increases tail latency (StdDev/P99), not median |
| 010 | Partitioned Dual-Core | 1.45× speedup at 4096 elements; crossover between 256–1024 elements |
| 011 | System/Compute Isolation | 48.55× event latency improvement via core separation (ABBA, 4 runs) |

### Historical Foundation (Experiments 001–005)
Early computational benchmarking, timing repeatability, timing source cross-validation, periodic task behavior, instrumentation overhead characterization.

---

## Repository Structure

```
V-Core/
│
├── README.md
├── LICENSE_RECOMMENDATION.md
├── .gitignore
│
├── firmware/
│   ├── active/                 # Active ESP-IDF project (buildable)
│   │   ├── main/
│   │   │   └── vcore.c         # Experiment 011 firmware (active)
│   │   ├── CMakeLists.txt
│   │   ├── sdkconfig
│   │   ├── sdkconfig.old
│   │   └── calculate_time.py
│   │
│   └── experiments/            # Authoritative experiment implementations
│       ├── exp006/
│       │   └── exp006.c        # Exp 006 computational baseline
│       ├── exp007/
│       │   └── exp007.c        # Exp 007 core placement
│       ├── exp008/
│       │   └── exp008.c        # Exp 008 sync latency (FINAL CANDIDATE)
│       ├── exp009/
│       │   └── exp009.c        # Exp 009 interference
│       ├── exp010/
│       │   ├── exp010a.c       # Exp 010A single-core baseline
│       │   └── exp010b.c       # Exp 010B dual-core partitioned
│       ├── exp011/
│       │   └── exp011.c        # Exp 011 system/compute isolation
│       └── expected.c          # Checksum references
│
├── data/
│   ├── raw/                    # Original serial captures (unmodified)
│   │   ├── experiment-002-repeatability.txt
│   │   ├── experiment-003-240mhz.txt
│   │   ├── experiment-004.txt
│   │   ├── experiment-005.txt
│   │   ├── experiment-006.txt
│   │   ├── experiment-007-core0.txt
│   │   ├── experiment-007-core1.txt
│   │   ├── experiment-007-core0-run2-3.txt
│   │   ├── experiment-007-core1-run2-3.txt
│   │   ├── experiment-008.txt
│   │   ├── experiment-009.txt
│   │   ├── experiment-010a.txt
│   │   ├── experiment-010b.txt
│   │   └── experiment-011.txt
│   │
│   └── processed/              # Derived results and experiment summaries
│       └── experiment-008.md   # Exp 008 methodology & 4-run results
│
├── research/
│   ├── reports/                # Formal DOCX reports
│   │   ├── V-Core_Experiment_007_Report.docx
│   │   └── V-Core_Experiments_006_008_009_Consolidated_Report.docx
│   │
│   ├── methodology/            # Research methodology documentation
│   │   └── experiment-001-baseline.md
│   │
│   ├── analysis/               # Analysis and reconciliation (if any)
│   │
│   └── paper/                  # Research paper drafts (future)
│
├── tools/
│   ├── create_phase1.py        # Phase 1 presentation generator
│   ├── create_phase2.py        # Phase 2 presentation generator
│   └── Notes.txt               # Cycle/time conversions, cross-checks
│
├── archive/
│   ├── source/                 # Superseded experiment versions
│   │   ├── exp8.c
│   │   ├── exp8v2.c
│   │   └── exp9v2.c
│   │
│   ├── presentations/          # Superseded presentation files
│   │   ├── 5th_Semester_Mini_Project_Presentation_Template.pptx
│   │   ├── V-Core_Phase1_Progress_Review.pptx
│   │   ├── V-Core_Phase1_Progress_Review_CLEAN.pptx
│   │   └── V-Core_Phase2_Final_Presentation.pptx
│   │
│   └── images/                 # Diagram images
│       ├── V1 api.png
│       ├── exp11.png
│       └── exp9 table.png
│
└── docs/
    └── [project documentation index or other useful documentation]
```

---

## Building & Running

```bash
# Prerequisites: ESP-IDF v6.1 installed and sourced
cd firmware/active
idf.py build
idf.py flash monitor
```

The firmware runs experiments sequentially and outputs results via serial (115200 baud).

> **Note**: The active ESP-IDF project is also available at `vcore/` for backward compatibility. Both locations contain identical source code.

---

## Key Results

### Experiment 008: Synchronization Latency (4 runs × 4 configs × 1000 samples)

| Configuration | 4-Run Mean (µs) | Max (µs) |
|---------------|-----------------|----------|
| Same-core polling | 20.776 | 33 |
| Same-core notification-wait | 25.794 | 33 |
| Cross-core polling | 18.825 | 34 |
| Cross-core notification-wait | 28.650 | 35 |

> **Source**: `data/raw/experiment-008.txt` (raw serial captures) → `data/processed/experiment-008.md` (documented four-run averages)
> 
> **Individual run means (µs)**:
> - Same-core polling: 20.785, 20.771, 20.776, 20.771
> - Same-core notification-wait: 26.024, 25.729, 25.703, 25.718
> - Cross-core polling: 18.805, 18.825, 18.838, 18.833
> - Cross-core notification-wait: 28.655, 28.650, 28.645, 28.649

### Experiment 010: Dual-Core Speedup (Median CCOUNT cycles)

| Vector Size | Single-Core (Exp 010A) | Dual-Core (Exp 010B) | Speedup | Improvement |
|-------------|------------------------|----------------------|---------|-------------|
| 1,024 | 30,757 | 26,119 | 1.18× | 15.1% |
| 4,096 | 122,917 | 84,486 | 1.45× | 31.3% |

> **Source**: `data/raw/experiment-010a.txt` and `data/raw/experiment-010b.txt` (raw serial captures)
> 
> **Crossover**: Between 256–1,024 elements (dual-core overhead exceeds benefit below this threshold; measured slower at 256, faster at 1,024)
> **Checksum validation**: PASS for all sizes (dual-core output matches single-core reference)

### Experiment 011: System/Compute Isolation — ABBA Counterbalanced (4 runs × 1000 samples)

| Phase | Configuration | Mean Latency (cycles) | Mean Latency (µs) | Improvement |
|-------|---------------|----------------------|-------------------|-------------|
| A1 | Shared-core (sys+prod+compute on Core 0) | 286,648 | 1194.4 | baseline |
| B1 | Core-separated (sys+prod on Core 0, compute on Core 1) | 5,904 | 24.6 | **48.55×** |
| B2 | Core-separated (replicate) | 5,904 | 24.6 | **48.55×** |
| A2 | Shared-core (return to baseline) | 286,648 | 1194.4 | baseline |

> **Source**: `data/raw/experiment-011.txt` (raw serial capture)
> 
> **Verification**: 286,648.358 / 5,904.370 = 48.549… ≈ 48.55×
> 
> **ABBA Design**: Execution order A1 → B1 → B2 → A2 controls for thermal/time drift. A1 and A2 means match to 3 decimal places (286,648.358), confirming no systematic drift.
> 
> **Configuration Note**: The 48.55× improvement is measured under the tested configuration where a priority-6 compute task and priority-5 system task both run on Core 0 in the shared-core phases (A1, A2). In the core-separated phases (B1, B2), moving the compute task to Core 1 prevents it from preempting the system task on Core 0. The effect reflects this scheduling interaction under the tested priorities and period (10 ms); it is not necessarily attributable to core separation alone.

---

## Documentation Index

| File | Description |
|------|-------------|
| `LICENSE_RECOMMENDATION.md` | License analysis (BSD-3-Clause recommended) |
| `research/reports/V-Core_Experiment_007_Report.docx` | Phase 1 formal report |
| `research/reports/V-Core_Experiments_006_008_009_Consolidated_Report.docx` | Phase 2 consolidated report |
| `research/methodology/experiment-001-baseline.md` | Exp 001 baseline methodology |
| `data/raw/experiment-*.txt` | Raw serial captures (13 files) |
| `data/processed/experiment-008.md` | Exp 008 methodology & 4-run results |
| `tools/create_phase1.py` / `tools/create_phase2.py` | Presentation generators (updated phases) |
| `tools/Notes.txt` | Cycle/time conversions, cross-checks |

---

## Original Contributions

This work provides the following original contributions to the study of dual-core parallel computing on ESP32/FreeRTOS:

1. **Systematic synchronization characterization** — Comparative characterization of four synchronization configurations (same-core/cross-core × polling/notification-wait) with hardware cycle counters, establishing that cross-core polling is fastest (18.8 µs) and notification-wait adds ~5–10 µs overhead.

2. **ABBA counterbalanced experimental design** — Applied A1→B1→B2→A2 execution ordering with 1000-sample runs. The counterbalanced sequence provides evidence against a simple time-order or drift explanation under the tested conditions; A1 and A2 baselines match to <0.001% difference.

3. **Workload interference taxonomy** — Demonstrated that cross-core compute load selectively degrades tail latency (P99, StdDev) while leaving median latency unchanged, quantifying the "noisy neighbor" effect on FreeRTOS SMP.

4. **Partitioned dual-core crossover analysis** — Identified the crossover between 256 and 1,024 elements (dual-core slower at 256, faster at 1,024) where synchronization overhead is amortized, with 1.45× speedup at 4096 elements for integer dot-product workloads.

5. **Hardware cycle counter methodology** — Timing via `rsr.ccount` (4.17 ns nominal cycle interval at 240 MHz) with no `esp_timer` calls in measured intervals for the documented experiments, providing microarchitecturally transparent measurements.

6. **Reproducible firmware artifacts** — Authoritative source implementations for Experiments 006–011 in `firmware/experiments/` (7 files covering Exp 006, 007, 008, 009, 010A, 010B, 011) with raw serial captures preserved in `data/raw/`, enabling independent verification of all documented claims.

---

## License

**Pending decision** — Recommendation: **BSD-3-Clause** (see `LICENSE_RECOMMENDATION.md`)

No `LICENSE` file has been created yet. The project maintainer will select a license before publication.

---

## Citation

If you use this work, please cite:

```
Prajwal Navada G P, "V-Core: Dual-Core Parallel Computing on ESP32",
VTU 5th Semester Mini Project (BCS568/BIS568/BAD568), 2026-27.
```

---

## Limitations

- Single hardware unit (ESP32 DevKit V1, silicon rev v3.1)
- Single software configuration (ESP-IDF v6.1, 240 MHz, default FreeRTOS config)
- Integer dot-product workload only (no floating-point, no SIMD)
- No cache coherence management (workloads operate on disjoint memory regions; cache effects not characterized)
- No power/thermal profiling
- Results are configuration-specific; generalizability requires cross-platform validation

---

## Future Work

See `tools/create_phase1.py` / `tools/create_phase2.py` (Future Scope slides) for 16 research extensions including:
- Cache coherence protocols, memory bandwidth saturation, heterogeneous workloads
- RTOS tickless operation, priority inheritance, inter-core interrupts
- Power profiling, thermal characterization, multi-chip modules
- Comparison with RP2040, ESP32-S3, ESP32-P4 dual-core architectures