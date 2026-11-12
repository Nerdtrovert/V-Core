from pptx import Presentation
from pptx.util import Pt, Emu, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.chart.data import CategoryChartData
from io import BytesIO
from pathlib import Path

# Resolve archive paths relative to this script's location
SCRIPT_DIR = Path(__file__).resolve().parent
ARCHIVE_DIR = SCRIPT_DIR.parent / "archive" / "presentations"

# Load template and existing
template = Presentation(str(ARCHIVE_DIR / "5th_Semester_Mini_Project_Presentation_Template.pptx"))
existing = Presentation(str(ARCHIVE_DIR / "V-Core_Phase1_Progress_Review_CLEAN.pptx"))

# Create new presentation from template
prs = Presentation('../archive/presentations/5th_Semester_Mini_Project_Presentation_Template.pptx')

# Remove all slides except title slide
slides_to_remove = list(prs.slides)[1:]
for slide in slides_to_remove:
    rId = prs.slides._sldIdLst[-1].rId
    prs.part.drop_rel(rId)
    prs.slides._sldIdLst.remove(prs.slides._sldIdLst[-1])

# Color constants
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BLUE = RGBColor(0xBE, 0xD3, 0xE5)
DARK_GRAY = RGBColor(0x69, 0x78, 0x8A)
DARK_TEXT = RGBColor(0x26, 0x30, 0x3C)
TEAL_1 = RGBColor(0x24, 0x69, 0xAA)
TEAL_2 = RGBColor(0x00, 0x97, 0xA7)
ORANGE = RGBColor(0xEB, 0x99, 0x3A)
GREEN = RGBColor(0x2E, 0x7D, 0x32)

FONT_NAME = 'Aptos'

def add_textbox(slide, left, top, width, height, text, font_size=14, bold=False, color=DARK_TEXT, alignment=PP_ALIGN.LEFT, font_name=FONT_NAME):
    txBox = slide.shapes.add_textbox(Emu(left), Emu(top), Emu(width), Emu(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = alignment
    return txBox

def add_multiline_textbox(slide, left, top, width, height, lines, font_size=14, bold=False, color=DARK_TEXT, alignment=PP_ALIGN.LEFT, line_spacing=1.15, font_name=FONT_NAME):
    txBox = slide.shapes.add_textbox(Emu(left), Emu(top), Emu(width), Emu(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = line
        p.font.size = Pt(font_size)
        p.font.bold = bold
        p.font.color.rgb = color
        p.font.name = font_name
        p.alignment = alignment
        p.space_after = Pt(font_size * (line_spacing - 1))
    return txBox

def add_bullet_textbox(slide, left, top, width, height, bullets, font_size=14, color=DARK_TEXT, bold_first=False, font_name=FONT_NAME):
    txBox = slide.shapes.add_textbox(Emu(left), Emu(top), Emu(width), Emu(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, bullet in enumerate(bullets):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = bullet
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.name = font_name
        p.level = 0
        if bold_first and i == 0:
            p.font.bold = True
        p.space_after = Pt(4)
    return txBox

def style_title(slide, title_text, slide_num):
    title_shape = slide.shapes.title
    title_shape.text = title_text
    for p in title_shape.text_frame.paragraphs:
        for run in p.runs:
            run.font.size = Pt(28)
            run.font.bold = True
            run.font.color.rgb = WHITE
            run.font.name = FONT_NAME
    add_textbox(slide, 1092200, 1500000, 6000000, 400000,
                "5TH SEMESTER MINI PROJECT", font_size=10, bold=True, color=LIGHT_BLUE)
    add_textbox(slide, 9000000, 1500000, 2500000, 400000,
                "Dept of CSE | HNN College of Engineering", font_size=9, color=DARK_GRAY, alignment=PP_ALIGN.RIGHT)
    add_textbox(slide, 10500000, 1500000, 1200000, 400000,
                f"{slide_num:02d}", font_size=9, color=DARK_GRAY, alignment=PP_ALIGN.RIGHT)

# ==========================================
# SLIDE 1: TITLE SLIDE
# ==========================================
title_slide = prs.slides[0]
shapes_to_keep = []
for shape in title_slide.shapes:
    if hasattr(shape, 'image'):
        shapes_to_keep.append(shape)
for shape in list(title_slide.shapes):
    if shape not in shapes_to_keep:
        sp = shape._element
        sp.getparent().remove(sp)

add_textbox(title_slide, 1092200, 1143000, 9800000, 1500000, 
            "V-Core: Dual-Core Parallel Computing Using ESP32", 
            font_size=40, bold=True, color=WHITE)
add_textbox(title_slide, 1092200, 2400000, 9800000, 800000,
            "Academic Year 2026-2027", font_size=24, color=LIGHT_BLUE)
add_textbox(title_slide, 1092200, 2900000, 9800000, 800000,
            "5th Semester Mini Project Presentation", font_size=24, color=LIGHT_BLUE)
add_textbox(title_slide, 1092200, 3400000, 9800000, 800000,
            "(BCS568/BIS568/BAD568)", font_size=24, color=LIGHT_BLUE)
add_textbox(title_slide, 1092200, 4200000, 9800000, 600000,
            "Submitted by:", font_size=17, color=WHITE)
add_textbox(title_slide, 1092200, 4700000, 9800000, 600000,
            "Prajwal Navada G P – 1HC24CS058", font_size=17, color=WHITE)
add_textbox(title_slide, 1092200, 5400000, 9800000, 600000,
            "Under the guidance of:", font_size=16, bold=True, color=WHITE)
add_textbox(title_slide, 1092200, 5900000, 9800000, 600000,
            "Dr Suma Swamy, Professor", font_size=16, bold=True, color=WHITE)
add_textbox(title_slide, 1092200, 6400000, 9800000, 600000,
            "Dept of CSE", font_size=15, color=WHITE)

# ==========================================
# SLIDE 2: PROJECT OVERVIEW
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "1. Project Overview", 2)

overview_lines = [
    "Project Title: V-Core: Dual-Core Parallel Computing Using ESP32",
    "Domain: Embedded Systems, Computer Architecture, Real-Time Computing",
    "Platform: ESP32 DevKit V1 (ESP32-WROOM-32), Dual-core Xtensa LX6 @ 240 MHz",
    "Framework: ESP-IDF v6.1, FreeRTOS SMP, C (C99)",
    "",
    "Project Scope:",
    "  • Phase 1: Measurement foundation – computational latency, synchronization, core behavior",
    "  • Phase 2: Parallel implementation – partitioned dual-core computation, interference analysis, workload isolation",
    "",
    "Key Contribution: Measurement-first approach to dual-core parallel computing on ESP32",
    "  – Synchronization characterized BEFORE parallel implementation",
    "  – Rigorous cycle-accurate baselines using hardware CCOUNT register",
    "  – 11 controlled experiments (001–011) with repeatable methodology",
    "",
    "Evaluation: VTU 5th Semester Mini Project (BCS568/BIS568/BAD568)"
]
add_multiline_textbox(slide, 1092200, 2200000, 10000000, 4500000,
                      overview_lines, font_size=15, color=DARK_TEXT, line_spacing=1.25)

# ==========================================
# SLIDE 3: INTRODUCTION AND MOTIVATION
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "2. Introduction and Motivation", 3)

intro_lines = [
    "Embedded systems increasingly demand real-time responsiveness and computational throughput within strict power and area constraints.",
    "The ESP32 dual-core Xtensa LX6 processor (240 MHz) offers parallel computing capability, but effective utilization requires understanding synchronization, core placement, and scheduling behavior.",
    "V-Core investigates dual-core parallel computing on ESP32 using vector dot-product as a representative computational workload.",
    "",
    "Why This Matters:",
    "  • Dual-core MCUs are ubiquitous (ESP32, STM32H7, RP2040, etc.) but parallel behavior is often assumed, not measured",
    "  • Claims of \"2× speedup\" ignore synchronization overhead, cache contention, and scheduling interference",
    "  • Real-time systems need predictable timing, not just peak throughput",
    "",
    "Approach: Establish rigorous timing baselines (Phase 1) BEFORE implementing parallel computation (Phase 2)",
    "  – Single-core computational latency characterization (5 vector sizes, 1000+ samples)",
    "  – Synchronization latency taxonomy (4 configurations × 1000 samples)",
    "  – Core-to-core variation, interference, and workload isolation analysis"
]
add_multiline_textbox(slide, 1092200, 2200000, 10000000, 4500000,
                      intro_lines, font_size=15, color=DARK_TEXT, line_spacing=1.25)

# ==========================================
# SLIDE 4: PROBLEM STATEMENT
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "3. Problem Statement", 4)

problem_bullets = [
    "Dual-core microcontrollers like ESP32 are widely adopted, but characterization of their parallel execution behavior is often anecdotal rather than measured.",
    "Existing literature lacks systematic measurement of:",
    "  • Computational latency across vector sizes using hardware cycle counters (CCOUNT)",
    "  • Synchronization latency: polling vs. FreeRTOS task notifications, same-core vs. cross-core",
    "  • Core-to-core variation in computational throughput",
    "  • Cross-core interference: cache/memory contention under concurrent workloads",
    "  • System/compute workload isolation: scheduling interaction between tasks of different priorities",
    "  • Interaction between masked-interrupt critical sections and FreeRTOS scheduling",
    "Without measured baselines, claims of \"dual-core speedup\" cannot be substantiated or reproduced.",
    "Operating Environment: ESP32 DevKit V1, ESP-IDF v6.1, FreeRTOS SMP, 240 MHz"
]
add_bullet_textbox(slide, 1092200, 2200000, 10000000, 4500000,
                   problem_bullets, font_size=15, color=DARK_TEXT)

# ==========================================
# SLIDE 5: OBJECTIVES AND SCOPE
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "4. Objectives and Scope", 5)

add_textbox(slide, 1092200, 2100000, 4800000, 400000,
            "Phase 1 Objectives (Completed: Experiments 007, 008)", font_size=16, bold=True, color=TEAL_1)

obj1_bullets = [
    "O1: Compare Core 0 vs Core 1 computational behavior (Experiment 007)",
    "O2: Measure sender-side request-to-acknowledgment latency for 4 synchronization configurations (Exp 008)"
]
add_bullet_textbox(slide, 1092200, 2500000, 4800000, 3000000,
                   obj1_bullets, font_size=13, color=DARK_TEXT)

add_textbox(slide, 6200000, 2100000, 4800000, 400000,
            "Phase 2 Objectives (Completed: Experiments 006, 009, 010, 011)", font_size=16, bold=True, color=TEAL_2)

obj2_bullets = [
    "O3: Characterize single-core dot-product computational latency & repeatability (Experiment 006)",
    "O4: Measure Core 1 workload interference on Core 0 computational latency (Experiment 009)",
    "O5: Implement and measure partitioned dual-core dot-product computation (Experiment 010)",
    "O6: Measure system/compute workload isolation via core separation (Experiment 011)",
    "O7: Validate speedup claims against single-core baseline with measured overhead",
    "O8: Analyze scaling behavior: identify crossover point where parallelism becomes beneficial",
    "O9: Document honest limitations and scope of measured results"
]
add_bullet_textbox(slide, 6200000, 2500000, 4800000, 3000000,
                   obj2_bullets, font_size=13, color=DARK_TEXT)

# Scope
add_textbox(slide, 1092200, 5200000, 10000000, 400000,
            "Scope", font_size=16, bold=True, color=ORANGE)

scope_bullets = [
    "Included: ESP32 DevKit V1, ESP-IDF v6.1, FreeRTOS SMP, 240 MHz, Vector sizes 16/64/256/1024/4096",
    "Included: CCOUNT cycle counting, wall-clock timing, FreeRTOS synchronization primitives",
    "Out of Scope: Wi-Fi/BT stack interaction, power profiling, thermal analysis, formal WCET",
    "Out of Scope: Generalization beyond tested hardware/software configuration"
]
add_bullet_textbox(slide, 1092200, 5600000, 10000000, 1500000,
                   scope_bullets, font_size=13, color=DARK_TEXT)

# ==========================================
# SLIDE 6: BACKGROUND - EMBEDDED MULTICORE COMPUTING
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "5. Background: Embedded Multicore Computing", 6)

bg_lines = [
    "Multicore in Embedded Systems:",
    "  • Trend: Single-core → dual/quad-core MCUs (ESP32, STM32H7, RP2040, NXP i.MX RT)",
    "  • Drivers: Performance, real-time determinism, task isolation, power efficiency",
    "  • Challenges: Cache coherence, memory contention, synchronization overhead, scheduling complexity",
    "",
    "ESP32 Dual-Core Xtensa LX6 Architecture:",
    "  • Two identical Xtensa LX6 cores (Core 0: PRO_CPU, Core 1: APP_CPU) @ 240 MHz",
    "  • Each core: 32 KB L1 instruction cache, 32 KB L1 data cache, independent CCOUNT register",
    "  • Shared: 520 KB SRAM (divided into IRAM/DRAM), peripheral bus, interrupt matrix",
    "  • No hardware cache coherence between cores – software-managed consistency",
    "",
    "FreeRTOS SMP on ESP32:",
    "  • Symmetric multiprocessing: tasks can run on any core, pinned via xTaskCreatePinnedToCore()",
    "  • Inter-core communication: task notifications, queues, semaphores, spinlocks",
    "  • Critical sections: portENTER_CRITICAL() masks interrupts on calling core only",
    "  • Scheduler: Per-core run queues, global priority ordering with core affinity"
]
add_multiline_textbox(slide, 1092200, 2200000, 10000000, 4500000,
                      bg_lines, font_size=14, color=DARK_TEXT, line_spacing=1.2)

# ==========================================
# SLIDE 7: ESP32 HARDWARE PLATFORM AND XTENSA LX6
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "6. ESP32 Hardware Platform and Xtensa LX6 Architecture", 7)

hw_lines = [
    "ESP32-WROOM-32 (DevKit V1) Specifications:",
    "  • Processor: Dual-core Xtensa LX6 microprocessor @ 240 MHz",
    "  • Memory: 520 KB SRAM (320 KB DRAM + 128 KB IRAM + 80 KB RTC), 4 MB external Flash",
    "  • Caches: Per-core 32 KB I-cache + 32 KB D-cache (4-way set associative)",
    "  • Peripherals: GPIO, SPI, I2C, I2S, UART, ADC, DAC, Touch, Hall, Pulse Counter, RMT, LED PWM",
    "  • Wireless: Wi-Fi 802.11 b/g/n, Bluetooth v4.2 BR/EDR and BLE",
    "",
    "Xtensa LX6 Core Features (per core):",
    "  • 32-bit RISC architecture with configurable ISA",
    "  • CCOUNT register: 32-bit cycle counter, increments every cycle (read via RSR instruction)",
    "  • CCMPARE0/1/2: Comparator registers for timer interrupts",
    "  • Windowed register file (16 register windows) for fast context switching",
    "  • Interrupt controller: 32 interrupts per core (6 internal + 26 from interrupt matrix)",
    "",
    "Key Implication for Parallel Computing:",
    "  • No hardware cache coherence → shared data requires explicit cache maintenance or uncached access",
    "  • Independent CCOUNT per core → cycle counts not directly comparable across cores without synchronization",
    "  • Interrupt matrix routes peripheral interrupts to either/both cores → configurable affinity"
]
add_multiline_textbox(slide, 1092200, 2200000, 10000000, 4500000,
                      hw_lines, font_size=14, color=DARK_TEXT, line_spacing=1.2)

# ==========================================
# SLIDE 8: PROPOSED V-CORE SYSTEM ARCHITECTURE
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "7. Proposed V-Core System Architecture", 8)

arch_lines = [
    "V-Core: Dual-Core Parallel Computing Framework for ESP32",
    "",
    "Phase 1 (Completed) – Measurement Foundation (Experiments 007, 008):",
    "  • Core placement comparison: Core 0 vs Core 1 (Experiment 007)",
    "  • Synchronization latency taxonomy: 4 configurations measured (Experiment 008)",
    "",
    "Phase 2 (Completed) – Parallel Computation & Analysis (Experiments 006, 009, 010, 011):",
    "  • Computational baseline & repeatability (Experiment 006)",
    "  • Interference analysis (Experiment 009)",
    "  • Partitioned dual-core computation (Experiment 010)",
    "  • System/compute workload isolation (Experiment 011)",
    "",
    "Historical Foundation (Experiments 001–005):",
    "  • Early computational benchmarking, repeatability, timing sources, periodic task behavior, instrumentation overhead",
    "",
    "System Components (Implemented):",
    "  1. Timing Module: CCOUNT/esp_timer abstraction, cycle-to-µs conversion, overhead characterization",
    "  2. Dot-Product Kernel: Vector sizes 16–4096, int16_t inputs, int32_t accumulation, checksum",
    "  3. Synchronization Module: Request/ack queues in shared DRAM, polling & notification-wait receivers",
    "  4. Periodic Task Module: vTaskDelayUntil() 10 ms task, interval error measurement",
    "  5. Experiment Controller: Sequences experiments, manages core affinity, serial reporting",
    "",
    "Key Innovation: Measurement-first approach – synchronization characterized BEFORE parallel implementation"
]
add_multiline_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                      arch_lines, font_size=14, color=DARK_TEXT, line_spacing=1.15)

# ==========================================
# SLIDE 9: SOFTWARE ARCHITECTURE AND FREERTOS TASK MODEL
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "8. Software Architecture and FreeRTOS Task Model", 9)

sw_lines = [
    "Task Model (Phase 2 Implementation):",
    "",
    "Experiment 010 – Partitioned Dual-Core Computation:",
    "  • Core 0 (Producer/Coordinator): Dispatches work, waits for completion, measures total elapsed",
    "  • Core 1 (Worker): Persistent task, receives partition, computes partial dot-product, signals done",
    "  • Synchronization: Shared request/ack queues in DRAM, polling-based coordination (per Exp 008)",
    "  • Data Partitioning: Static – first half on Core 0, second half on Core 1",
    "  • Checksum Verification: Core 0 validates combined result matches single-core baseline",
    "",
    "Experiment 011 – System/Compute Workload Isolation:",
    "  • Configuration A (Shared-core): Producer, system task, compute task all on Core 0",
    "  • Configuration B (Core-separated): Producer + system task on Core 0, compute task on Core 1",
    "  • System Task: Low priority (tskIDLE_PRIORITY), periodic 10 ms, represents OS/housekeeping",
    "  • Compute Task: High priority (tskIDLE_PRIORITY + 2), periodic compute chunk",
    "  • Measurement: Event release-to-completion latency using Core 0 CCOUNT",
    "",
    "FreeRTOS Primitives Used:",
    "  • xTaskCreatePinnedToCore() – Explicit core affinity for all tasks",
    "  • ulTaskNotifyTake() / xTaskNotifyGive() – Inter-core signaling (Exp 008, 010)",
    "  • vTaskDelayUntil() – Periodic task timing (Exp 004, 011)",
    "  • portENTER/EXIT_CRITICAL() – Interrupt masking for instrumentation (Exp 004)",
    "  • Spinlocks (portMUX) – Not used; polling preferred per Exp 008 results"
]
add_multiline_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                      sw_lines, font_size=14, color=DARK_TEXT, line_spacing=1.15)

# ==========================================
# SLIDE 10: COMPUTATIONAL WORKLOAD AND DATA PARTITIONING
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "9. Computational Workload and Data Partitioning", 10)

workload_lines = [
    "Representative Workload: Vector Dot-Product",
    "  • Operation: Σ(a[i] × b[i]) for i = 0 to n-1",
    "  • Data Types: int16_t inputs, int32_t accumulation (prevents overflow)",
    "  • Vector Sizes: 16, 64, 256, 1,024, 4,096 elements",
    "  • Memory Layout: Contiguous arrays in DRAM, aligned to 4 bytes",
    "  • Checksum: Final sum verified against known reference value",
    "",
    "Why Dot-Product?",
    "  • Fundamental linear algebra kernel (BLAS Level 1)",
    "  • Representative of DSP, ML inference, sensor fusion workloads",
    "  • Predictable O(n) complexity, memory-bound for large vectors",
    "  • Easy to partition: contiguous chunks with independent accumulation",
    "",
    "Partitioning Strategy (Experiment 010):",
    "  • Static Partitioning: Vector split at midpoint (n/2)",
    "  • Core 0 computes indices [0, n/2), Core 1 computes [n/2, n)",
    "  • No overlap, no redundancy – each element processed exactly once",
    "  • Coordination Overhead: Dispatch → Core 1 computation → Wait for completion → Combine",
    "  • Persistent Worker: Core 1 task stays alive across iterations (avoids task create/destroy overhead)",
    "",
    "Alternative Strategies (Future Work):",
    "  • Dynamic work-stealing: Idle core pulls chunks from shared queue",
    "  • Block-cyclic distribution: Better cache utilization for strided access",
    "  • Pipeline parallelism: Overlap computation with data transfer"
]
add_multiline_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                      workload_lines, font_size=14, color=DARK_TEXT, line_spacing=1.15)

# ==========================================
# SLIDE 11: EXPERIMENTAL METHODOLOGY AND MEASUREMENT STRATEGY
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "10. Experimental Methodology and Measurement Strategy", 11)

method_lines = [
    "Core Measurement Principle: Hardware Cycle Counter (CCOUNT)",
    "  • Xtensa CCOUNT: 32-bit register, increments every CPU cycle (4.17 ns @ 240 MHz)",
    "  • Accessed via __builtin_rsr(\"CCOUNT\") intrinsic – single instruction, 1 cycle overhead",
    "  • Per-core: Each core has independent CCOUNT, not synchronized across cores",
    "  • Cross-validation: esp_timer_get_time() (µs resolution) for wall-clock correlation",
    "",
    "Measurement Protocol (All Computational Experiments):",
    "  1. Warm-up: 100 iterations (cache/TLB stabilization, branch predictor warm-up)",
    "  2. Measured Phase: 1,000 iterations per vector size per configuration",
    "  3. Per Iteration:",
    "     a) start = CCOUNT",
    "     b) result = dot_product(a, b, n)",
    "     c) end = CCOUNT",
    "     d) cycles = end - start; wall_time = esp_timer_get_time() diff",
    "     e) Verify checksum",
    "  4. Statistics: Min, Mean, Median, StdDev, P95, P99, Max",
    "  5. Repeatability: 5 independent runs (Experiments 002, 006, 009)",
    "",
    "Synchronization Measurement (Experiment 008):",
    "  • End-to-end request-to-acknowledgment latency (sender-side)",
    "  • Sender: timestamp at request publish → wait for ack → elapsed = now - start_ts",
    "  • Four configurations: Same/Cross-core × Polling/Notification-wait",
    "  • 100 warm-up + 1000 measured samples per configuration",
    "",
    "Interference/Isolation Measurement (Experiments 009, 011):",
    "  • ABBA run order (A1→B1→B2→A2) for repeatability on single board/boot",
    "  • Core 0 CCOUNT for all latency measurements (consistent timebase)",
    "  • Compute task periodically yields (vTaskDelay) – not uninterrupted saturation"
]
add_multiline_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                      method_lines, font_size=14, color=DARK_TEXT, line_spacing=1.15)

# ==========================================
# SLIDE 12: DEVELOPMENT ENVIRONMENT AND TECHNOLOGY STACK
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[3])
style_title(slide, "11. Development Environment and Technology Stack", 12)

left_items = [
    ("Hardware", "ESP32 DevKit V1 (ESP32-WROOM-32) – Dual-core Xtensa LX6 @ 240 MHz, 4 MB Flash, 520 KB SRAM"),
    ("Framework", "ESP-IDF v6.1 – Official Espressif IoT Development Framework"),
    ("RTOS", "FreeRTOS SMP (v10.4.3) – Symmetric multiprocessing kernel with core affinity"),
    ("Language", "C (C99) – Embedded C with Xtensa-specific intrinsics (__builtin_rsr)"),
    ("Build System", "CMake + Ninja – ESP-IDF standard build system")
]

right_items = [
    ("Timing", "Xtensa CCOUNT register – Per-core cycle counter (1 cycle @ 240 MHz = 4.17 ns)"),
    ("", "esp_timer_get_time() – High-resolution timer (µs resolution, 64-bit)"),
    ("Debug/Monitor", "idf_monitor (115200 baud) – Serial output capture and log parsing"),
    ("Analysis", "Python 3.11 – Statistical analysis, table generation, visualization"),
    ("Source", "vcore/main/vcore.c – Modular experiment controller (~2000 LOC)")
]

y = 2200000
for label, desc in left_items:
    if label:
        add_textbox(slide, 1092200, y, 4800000, 300000, label, font_size=14, bold=True, color=TEAL_1)
        y += 350000
    add_textbox(slide, 1092200, y, 4800000, 300000, desc, font_size=13, color=DARK_TEXT)
    y += 400000

y = 2200000
for label, desc in right_items:
    if label:
        add_textbox(slide, 6200000, y, 4800000, 300000, label, font_size=14, bold=True, color=TEAL_2)
        y += 350000
    add_textbox(slide, 6200000, y, 4800000, 300000, desc, font_size=13, color=DARK_TEXT)
    y += 400000

# ==========================================
# SLIDE 13: IMPLEMENTATION PROGRESSION AND PROJECT MILESTONES
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "12. Implementation Progression and Project Milestones", 13)

milestones = [
    "Phase 1 – Measurement Foundation (Experiments 007, 008)",
    "  Exp 007: Core placement comparison – Core 0 vs Core 1, identical workload",
    "  Exp 008: Synchronization latency – 4 configs, 4 independent runs each",
    "",
    "Phase 2 – Parallel Computation & Analysis (Experiments 006, 009, 010, 011)",
    "  Exp 006: Computational baseline – 5 vector sizes, repeatability validated",
    "  Exp 009: Workload interference analysis – Core 1 load on Core 0 computation",
    "  Exp 010: Partitioned dual-core dot-product – 1.45× speedup at 4096 elements",
    "  Exp 011: System/compute workload isolation – 48.55× latency improvement (ABBA)",
    "",
    "Historical Foundation (Experiments 001–005)",
    "  Early benchmarking, repeatability, timing sources, periodic task, instrumentation overhead",
    "",
    "Milestones Achieved:",
    "  ✓ All 11 experiments (001–011) implemented, executed, and validated on hardware",
    "  ✓ Phase 1: Core placement & synchronization characterized with repeatability",
    "  ✓ Phase 2: Parallel implementation complete with speedup & isolation characterized",
    "  ✓ Honest limitations documented for all experimental results"
]
add_bullet_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                   milestones, font_size=13, color=DARK_TEXT)

# ==========================================
# SLIDE 14: EXPERIMENT 006 - COMPUTATIONAL BASELINE
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "13. Experiment 006 – Computational Baseline (Single-Core)", 14)

exp6_lines = [
    "Single-Core Dot-Product Latency Characterization",
    "  • Platform: ESP32 DevKit V1, 240 MHz, ESP-IDF v6.1",
    "  • Method: 100 warm-up + 1,000 measured iterations per vector size",
    "  • Measurement: Xtensa CCOUNT (cycles) + esp_timer_get_time() (µs)",
    "  • Repeatability: 2 independent runs (Exp 006 Run 1 & Run 2)",
    "  • Checksum verification on every iteration",
    "",
    "Results – Median CCOUNT Cycles:",
    "  Vector Size  │  Median Cycles  │  Cycles/Element  │  Wall-clock (µs)",
    "  ────────────┼─────────────────┼──────────────────┼────────────────",
    "  16           │  515            │  32.2            │  2.15",
    "  64           │  1,955          │  30.5            │  8.15",
    "  256          │  7,715          │  30.1            │  32.15",
    "  1,024        │  30,755         │  30.0            │  128.15",
    "  4,096        │  122,915        │  30.0            │  512.15",
    "",
    "Key Findings:",
    "  • Near-linear scaling: ~30.0 cycles/element for large vectors (1024, 4096)",
    "  • Run 1 & Run 2 medians match EXACTLY for all 5 vector sizes",
    "  • Overhead-dominated for small vectors (16 elements: 32.2 cycles/elem)",
    "  • Computational cost: 128 µs for 1024-element dot product at 240 MHz",
    "  • Wall-clock aligns with cycle count: 240 MHz → 4.17 ns/cycle"
]
add_multiline_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                      exp6_lines, font_size=13, color=DARK_TEXT, line_spacing=1.15)

# ==========================================
# SLIDE 15: EXPERIMENT 007 - CORE PLACEMENT COMPARISON
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "14. Experiment 007 – Core Placement Comparison", 15)

exp7_lines = [
    "Core 0 vs Core 1 Computational Behavior",
    "  • Same computational workload (dot-product) pinned to Core 0 and Core 1 separately",
    "  • Identical vector sizes: 16, 64, 256, 1024, 4096",
    "  • 100 warm-up + 1000 measured iterations per size per core",
    "  • This is INDIVIDUAL core placement comparison, NOT simultaneous dual-core execution",
    "",
    "Results:",
    "  • Median cycles IDENTICAL across all vector sizes for Core 0 and Core 1",
    "  • Core 1 shows consistently lower StdDev (less variability):",
    "    – 64 elements: Core 0 StdDev 41, Core 1 StdDev 30",
    "    – 1024 elements: Core 0 StdDev 145, Core 1 StdDev 107",
    "    – 4096 elements: Core 0 StdDev 283, Core 1 StdDev 210",
    "",
    "What This Establishes:",
    "  ✓ Both cores have equivalent computational throughput for this workload",
    "  ✓ Core 1 (APP_CPU) exhibits slightly lower timing variability",
    "  ✓ No hardware asymmetry in ALU/FPU performance for integer dot-product",
    "",
    "What This Does NOT Establish:",
    "  ✗ Does NOT measure simultaneous dual-core execution",
    "  ✗ Does NOT account for cache/memory contention when both cores active",
    "  ✗ Does NOT measure synchronization overhead for parallel coordination",
    "  ✗ Results specific to this workload, clock frequency, and memory configuration"
]
add_multiline_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                      exp7_lines, font_size=14, color=DARK_TEXT, line_spacing=1.15)

# ==========================================
# SLIDE 16: EXPERIMENT 008 - SYNCHRONIZATION LATENCY
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "15. Experiment 008 – Synchronization Latency Characterization", 16)

exp8_lines = [
    "End-to-End Request-to-Acknowledgment Latency (Sender-Side)",
    "  • Four configurations: Same/Cross-core × Polling/Notification-wait",
    "  • 100 warm-up + 1000 measured samples per configuration",
    "  • Receiver: Polling (busy-wait) vs. Notification-wait (ulTaskNotifyTake)",
    "  • Sender: Publishes request + timestamp → waits for ack → records elapsed",
    "  • These are END-TO-END protocol measurements, NOT pure API overhead",
    "",
    "Results – Mean Latency:",
    "  Configuration                    │  Mean (µs)  │  Max (µs)  │  vs Polling",
    "  ─────────────────────────────────┼────────────┼───────────┼────────────",
    "  Same-core polling                │  20.78      │  33        │  baseline",
    "  Same-core notification-wait      │  25.87      │  35        │  +24.5%",
    "  Cross-core polling               │  18.82      │  33        │  baseline",
    "  Cross-core notification-wait     │  28.51      │  35        │  +51.5%",
    "",
    "Key Findings:",
    "  • Polling outperforms notification-wait in ALL configurations",
    "  • Cross-core polling (18.8 µs) faster than same-core polling (20.8 µs) – unexpected",
    "  • Notification overhead: ~5 µs (same-core), ~10 µs (cross-core) vs polling",
    "  • Max observed latency: 33–35 µs across all configurations",
    "  • 4 independent runs – repeatability established",
    "  • Implication: Polling preferred for low-latency coordination in Exp 010"
]
add_multiline_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                      exp8_lines, font_size=13, color=DARK_TEXT, line_spacing=1.15)

# ==========================================
# SLIDE 17: EXPERIMENT 009 - WORKLOAD INTERFERENCE
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "16. Experiment 009 – Core 1 Workload Interference Analysis", 17)

exp9_lines = [
    "Core 0 Computation Under Core 1 Load",
    "  • Compared Core 0 dot-product under two conditions:",
    "    A: Core 1 WITHOUT additional arithmetic workload",
    "    B: Core 1 RUNNING a periodic arithmetic workload",
    "  • Vector sizes: 16, 64, 256, 1024, 4096",
    "  • 100 warm-up + 1000 measured samples per size per condition",
    "  • Three runs with different execution orders",
    "  • Workload periodically yields – NOT uninterrupted full-core saturation",
    "",
    "Results:",
    "  • Median computational cycle counts: IDENTICAL between Condition A and B",
    "  • Additional Core 1 activity increased timing variability and tail latency",
    "  • Effect most pronounced for medium and larger workloads (256, 1024, 4096)",
    "  • StdDev and P99 increased under Condition B",
    "",
    "Interpretation:",
    "  • No measurable impact on median (typical-case) computational latency",
    "  • Increased variability suggests cache/memory contention under concurrent load",
    "  • Workload yields periodically – not worst-case continuous saturation",
    "  • Results suggest increased timing variability under TESTED workload",
    "  • NOT a universal proof of all multicore interference effects",
    "  • Relevant for real-time systems: tail latency matters for deadline guarantees"
]
add_multiline_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                      exp9_lines, font_size=13, color=DARK_TEXT, line_spacing=1.15)

# ==========================================
# SLIDE 18: EXPERIMENT 010 - PARTITIONED DUAL-CORE COMPUTATION
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "17. Experiment 010 – Partitioned Dual-Core Computation", 18)

exp10_lines = [
    "Two Configurations Evaluated",
    "",
    "A – Single-Core Baseline:",
    "  • Dot product executed entirely on Core 0",
    "  • 100 warm-up + 1000 measured iterations",
    "  • Median CCOUNT cycles:",
    "    16→517, 64→1,957, 256→7,717, 1024→30,757, 4096→122,917",
    "",
    "B – Partitioned Dual-Core Computation:",
    "  • Workload divided: Core 0 computes first half, Core 1 computes second half",
    "  • Persistent Core 1 worker task (avoids create/destroy overhead)",
    "  • Total elapsed = dispatch + coordination + computation + wait for completion",
    "  • Checksums match single-core baseline",
    "  • Median CCOUNT cycles (total elapsed on Core 0):",
    "    16→7,593, 64→8,021, 256→11,527, 1024→26,119, 4096→84,486",
    "",
    "Speedup Analysis:",
    "  Vector Size  │  Single-Core  │  Dual-Core  │  Speedup  │  Faster?",
    "  ────────────┼───────────────┼─────────────┼───────────┼─────────",
    "  16           │  517          │  7,593      │  0.07×    │  No",
    "  64           │  1,957        │  8,021      │  0.24×    │  No",
    "  256          │  7,717        │  11,527     │  0.67×    │  No",
    "  1,024        │  30,757       │  26,119     │  1.18×    │  YES (15.1%)",
    "  4,096        │  122,917      │  84,486     │  1.45×    │  YES (31.3%)",
    "",
    "Interpretation:",
    "  • Small workloads: coordination overhead dominates → SLOWER than single-core",
    "  • Crossover ~500-800 elements: parallelism becomes beneficial",
    "  • At 4096: 31.3% faster (not 2×) due to synchronization + partitioning overhead",
    "  • Applies to THIS implementation, workload, and test configuration ONLY",
    "  • NOT a universal ESP32 speedup claim"
]
add_multiline_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                      exp10_lines, font_size=12, color=DARK_TEXT, line_spacing=1.1)

# ==========================================
# SLIDE 19: EXPERIMENT 011 - SYSTEM/COMPUTE WORKLOAD ISOLATION
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "18. Experiment 011 – System/Compute Workload Isolation", 19)

exp11_lines = [
    "Core Separation for Improved Event Response Latency",
    "  • Configuration A (Shared-core): Producer, system task, compute task ALL on Core 0",
    "  • Configuration B (Core-separated): Producer + system task on Core 0, compute task on Core 1",
    "  • Compute task: High priority, periodically yields (not uninterrupted)",
    "  • System task: Low priority (tskIDLE_PRIORITY), 10 ms periodic",
    "  • Measurement: Event release-to-completion latency via Core 0 CCOUNT",
    "  • Four runs: ABBA order (A1→B1→B2→A2) – repeatability on one board, one boot",
    "",
    "Results – Mean Latency:",
    "  Configuration              │  Mean Latency (cycles)  │  vs Shared-core",
    "  ───────────────────────────┼─────────────────────────┼────────────────",
    "  A1 – Shared-core           │  286,648.358            │  baseline",
    "  B1 – Core-separated        │  5,904.370              │  48.55× faster",
    "  B2 – Core-separated        │  5,904.370              │  48.55× faster",
    "  A2 – Shared-core           │  286,648.358            │  baseline",
    "",
    "Interpretation:",
    "  • 48.55× improvement in system-event response latency",
    "  • NOT a claim that processor became 48.55× faster",
    "  • Mechanism: High-priority compute task preempted low-priority system task in Config A",
    "  • In Config B: Compute task on Core 1 runs without preemption interference",
    "  • Compute chunk durations comparable across cores (isolated execution)",
    "  • ABBA demonstrates repeatability across 4 runs on ONE physical board in ONE boot",
    "  • NOT independent hardware replication – single-board, single-boot validation"
]
add_multiline_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                      exp11_lines, font_size=13, color=DARK_TEXT, line_spacing=1.15)

# ==========================================
# SLIDE 20: CONSOLIDATED RESULTS AND COMPARATIVE ANALYSIS
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "19. Consolidated Results and Comparative Analysis", 20)

consolidated = [
    "Summary of All Experimental Results",
    "",
    "┌─────────────────────────────────────────────────────────────────────────────────────┐",
    "│ Experiment          │ Key Metric                                    │ Result          │",
    "├─────────────────────────────────────────────────────────────────────────────────────┤",
    "│ Exp 006: Baseline   │ 1024-elem dot-product                         │ 30,755 cycles   │",
    "│ Exp 007: Core Cmp   │ Core 0 vs Core 1 median                       │ IDENTICAL       │",
    "│ Exp 008: Sync       │ Best config (cross-core polling)              │ 18.82 µs mean   │",
    "│ Exp 009: Interfere  │ Median impact of Core 1 load on Core 0        │ 0% (median)     │",
    "│                     │ Tail latency (P99) increase                   │ Measurable      │",
    "│ Exp 010: Dual-Core  │ Speedup at 4096 elements                      │ 1.45× (31.3%)   │",
    "│ Exp 011: Isolation  │ Event latency improvement (core separation)   │ 48.55×          │",
    "└─────────────────────────────────────────────────────────────────────────────────────┘",
    "",
    "Cross-Cutting Insights:",
    "  1. Synchronization is the primary bottleneck for fine-grained parallelism",
    "     – Exp 008: ~19-29 µs per sync operation",
    "     – Exp 010: Overhead dominates below ~500 elements",
    "  2. Core separation eliminates priority inversion between system and compute tasks",
    "     – Exp 011: 48.55× latency improvement by isolating workloads",
    "  3. Median latency robust to interference; tail latency is not",
    "     – Exp 009: Median unchanged, but StdDev/P99 increase under load",
    "  4. Polling outperforms notification-wait for low-latency coordination",
    "     – Exp 008: 24-51% lower latency with polling",
    "  5. Results are configuration-specific; do not generalize to all ESP32 workloads"
]
add_multiline_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                      consolidated, font_size=12, color=DARK_TEXT, line_spacing=1.1)

# ==========================================
# SLIDE 21: DEMONSTRATION AND IMPLEMENTATION EVIDENCE
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "20. Demonstration and Implementation Evidence", 21)

demo_lines = [
    "Physical Implementation on ESP32 DevKit V1",
    "  • Hardware: ESP32-WROOM-32, USB-UART (/dev/cu.usbserial-0001), 115200 baud",
    "  • Power: USB 5V → 3.3V regulator on DevKit",
    "  • Serial Monitor: idf_monitor for real-time log capture and parsing",
    "",
    "Code Base (vcore/main/vcore.c):",
    "  • ~2000 lines of embedded C (C99) with Xtensa intrinsics",
    "  • Modular: app_main() → experiment selector → experiment runners",
    "  • Functions: run_dot_product_exp(), run_sync_exp(), run_periodic_exp(), run_interference_exp()",
    "  • run_dual_core_exp(), run_isolation_exp() for Phase 2",
    "",
    "Key Implementation Highlights:",
    "  • xTaskCreatePinnedToCore() for explicit core placement",
    "  • CCOUNT via __builtin_rsr(\"CCOUNT\") – 1 cycle read overhead",
    "  • portENTER/EXIT_CRITICAL() for interrupt masking (Exp 004)",
    "  • ulTaskNotifyTake(pdTRUE, portMAX_DELAY) for notification-wait",
    "  • xTaskNotifyGive() for sender-to-receiver signaling",
    "  • Persistent Core 1 worker task for Exp 010 (avoids create/destroy)",
    "  • ABBA run sequencing for Exp 011 repeatability",
    "",
    "Evidence to Present During Demo:",
    "  [ ] Live ESP32 hardware running experiment sequence",
    "  [ ] Serial output showing Exp 006/007/008/009/010/011 results",
    "  [ ] Checksum verification passing for all computational experiments",
    "  [ ] Repeatability: exact median match across runs (Exp 006, 011)"
]
add_multiline_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                      demo_lines, font_size=14, color=DARK_TEXT, line_spacing=1.15)

# ==========================================
# SLIDE 22: LIMITATIONS AND ENGINEERING CHALLENGES
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "21. Limitations and Engineering Challenges", 22)

limitations = [
    "Honest Limitations – Experimental Scope",
    "  1. Single hardware unit: All results from ONE ESP32 DevKit V1 board",
    "  2. Single software configuration: ESP-IDF v6.1, FreeRTOS SMP, 240 MHz",
    "  3. Single workload: Integer vector dot-product with int16_t/int32_t",
    "  4. No cache coherence management: Shared DRAM, no explicit cache maintenance",
    "  5. No power/thermal profiling: Results at room temperature, USB-powered",
    "  6. Exp 008 repeatability: 4 independent runs (4000 samples each), repeatability established",
    "  7. Exp 004 vs Exp 006 baseline discrepancy: 3.05% unresolved",
    "  8. Masked-interrupt mechanism not independently verified (Exp 004)",
    "",
    "Engineering Challenges Encountered:",
    "  1. CCOUNT per-core independence: Cannot directly compare cycles across cores without sync",
    "  2. Cache effects: No hardware coherence → shared data access patterns affect timing",
    "  3. Interrupt latency variability: FreeRTOS tick, peripheral interrupts add noise",
    "  4. Synchronization overhead: ~19-29 µs dominates fine-grained parallelism",
    "  5. Priority inversion: High-priority compute preempts low-priority system task (Exp 011)",
    "  6. Measurement perturbation: Instrumentation itself affects timing (characterized in Exp 005)",
    "  7. DRAM contention: Both cores accessing shared memory simultaneously (Exp 009)",
    "",
    "Scope of Claims:",
    "  • Results apply to tested configuration only",
    "  • No universal ESP32 dual-core speedup claims",
    "  • Speedup (Exp 010) and isolation (Exp 011) are implementation-specific"
]
add_multiline_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                      limitations, font_size=13, color=DARK_TEXT, line_spacing=1.15)

# ==========================================
# SLIDE 23: CONCLUSION AND KEY ACHIEVEMENTS
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "22. Conclusion and Key Achievements", 23)

conclusion = [
    "V-Core Project: Complete Dual-Core Parallel Computing Study on ESP32",
    "",
    "Phase 1 – Measurement Foundation (Experiments 007, 008):",
    "  ✓ Core placement: Core 0 ≡ Core 1 median; Core 1 lower variance (Exp 007)",
    "  ✓ Synchronization taxonomy: 4 configs, 4 runs, polling preferred (Exp 008)",
    "",
    "Phase 2 – Parallel Computation & Analysis (Experiments 006, 009, 010, 011):",
    "  ✓ Computational baseline: 5 vector sizes, repeatability validated (Exp 006)",
    "  ✓ Interference analysis: Core 1 load increases tail latency, not median (Exp 009)",
    "  ✓ Partitioned dual-core computation: 31.3% speedup at 4096 elements (Exp 010)",
    "  ✓ Crossover identified: ~500-800 elements where parallelism becomes beneficial",
    "  ✓ System/compute isolation: 48.55× event latency improvement via core separation (Exp 011)",
    "  ✓ ABBA repeatability demonstrated on single board/boot",
    "",
    "Historical Foundation (Experiments 001–005):",
    "  ✓ Rigorous single-core computational latency baseline (5 vector sizes, 5 repeat runs)",
    "  ✓ Instrumentation characterized: CCOUNT = 1 cycle (4.17 ns), esp_timer = 0.53 µs",
    "  ✓ Verified repeatability: Exact median match across independent runs",
    "  ✓ Periodic task stability: 0 µs error (idle), +3243 µs (masked-interrupt)",
    "",
    "Key Technical Contributions:",
    "  1. Measurement-first methodology for dual-core embedded parallel computing",
    "  2. Cycle-accurate synchronization latency characterization (4 configurations × 4 runs)",
    "  3. Quantified crossover point for ESP32 dual-core dot-product parallelism",
    "  4. Demonstrated core separation for real-time event latency improvement",
    "  5. Honest documentation of limitations and scope of all results",
    "",
    "All 11 experiments implemented, executed, and validated on physical ESP32 hardware"
]
add_multiline_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                      conclusion, font_size=13, color=DARK_TEXT, line_spacing=1.15)

# ==========================================
# SLIDE 24: FUTURE SCOPE
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "23. Future Scope", 24)

future = [
    "Immediate Extensions (V-Core Framework):",
    "  1. Experiment 008: Expand to 5 independent runs (4 completed)",
    "  2. Implement dynamic work-stealing scheduler for load balancing",
    "  3. Extend to matrix multiplication, FFT, convolution kernels",
    "  4. Investigate core-to-core variation under thermal/throttling conditions",
    "  5. Integrate with ESP-IDF FreeRTOS SMP task groups for cache affinity",
    "",
    "Advanced Research Directions:",
    "  6. Power profiling: Energy per operation (single vs dual-core)",
    "  7. Formal WCET analysis using measurement-derived distributions",
    "  8. Cache coherence protocols for shared-data parallel workloads",
    "  9. Heterogeneous workloads: DSP + control, sensor fusion + communication",
    "  10. Multi-board validation: Generalize across ESP32 revisions and silicon variants",
    "",
    "Software Engineering:",
    "  11. Release V-Core as open-source benchmark suite for ESP32 dual-core characterization",
    "  12. Contribute findings to ESP-IDF / FreeRTOS documentation",
    "  13. Build regression test suite for ESP-IDF SMP scheduler changes",
    "",
    "Research Dissemination:",
    "  14. Submit measurement methodology paper to embedded systems conference (EMSOFT, RTAS, DAC)",
    "  15. Publish dataset and analysis scripts for reproducibility",
    "  16. Collaborate with Espressif on ESP32-S3/P4 dual-core characterization"
]
add_multiline_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                      future, font_size=14, color=DARK_TEXT, line_spacing=1.2)

# ==========================================
# SLIDE 25: REFERENCES AND ACKNOWLEDGEMENTS
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])
style_title(slide, "24. References and Acknowledgements", 25)

refs = [
    "References",
    "[1] Espressif Systems, \"ESP32 Technical Reference Manual,\" v4.7, 2024.",
    "[2] Espressif Systems, \"ESP-IDF Programming Guide,\" v6.1, 2024.",
    "[3] FreeRTOS, \"Symmetric Multiprocessing (SMP) Guide,\" FreeRTOS v10.4.3, 2023.",
    "[4] Xtensa, \"Xtensa Instruction Set Architecture (ISA) Reference Manual,\" Cadence Design Systems.",
    "[5] Bach, P. et al., \"Multi-Core Real-Time Scheduling on ESP32,\" Proc. WFCS, 2021.",
    "[6] Wolf, M., \"Computers as Components: Principles of Embedded Computing System Design,\" 4th ed., Morgan Kaufmann, 2016.",
    "[7] Burns, A. & Wellings, A., \"Real-Time Systems and Programming Languages,\" 4th ed., Addison-Wesley, 2009.",
    "[8] V-Core Experiment Logs (Exp 001–011), /vcore/logs/, 2026.",
    "[9] ESP-IDF Source Code, components/esp_timer, components/freertos, components/xtensa, 2024.",
    "[10] VTU 2022 Scheme, BCS568/BIS568/BAD568 Mini Project Guidelines.",
    "",
    "Acknowledgements",
    "  • Dr. Suma Swamy, Professor, Dept of CSE – Project Guide and Mentor",
    "  • HNN College of Engineering, Dept of CSE – Infrastructure and Support",
    "  • VTU Belagavi – 5th Semester Mini Project Curriculum (BCS568/BIS568/BAD568)",
    "  • Espressif Systems – ESP32 Hardware, ESP-IDF Framework, Technical Documentation",
    "  • FreeRTOS Community – SMP Implementation and Documentation",
    "",
    "Citation Style: IEEE (consistent throughout)"
]
add_multiline_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                      refs, font_size=13, color=DARK_TEXT, line_spacing=1.15)

# ==========================================
# SLIDE 26: THANK YOU
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[6])

# Copy background from existing last slide
for shape in existing.slides[-1].shapes:
    if hasattr(shape, 'image'):
        img_blob = shape.image.blob
        img_stream = BytesIO(img_blob)
        pic = slide.shapes.add_picture(
            img_stream, Emu(0), Emu(0), 
            prs.slide_width, prs.slide_height
        )
        sp = pic._element
        sp.getparent().remove(sp)
        slide.shapes._spTree.insert(2, sp)
        break

add_textbox(slide, 1092200, 1500000, 9800000, 1500000,
            "THANK YOU", font_size=42, bold=True, color=WHITE, alignment=PP_ALIGN.CENTER)

add_textbox(slide, 1092200, 3200000, 9800000, 1000000,
            "Questions & Discussion", font_size=24, color=LIGHT_BLUE, alignment=PP_ALIGN.CENTER)

add_textbox(slide, 1092200, 4200000, 9800000, 800000,
            "V-Core: Dual-Core Parallel Computing Using ESP32", font_size=20, color=WHITE, alignment=PP_ALIGN.CENTER)

add_textbox(slide, 1092200, 4900000, 9800000, 800000,
            "Prajwal Navada G P", font_size=18, color=WHITE, alignment=PP_ALIGN.CENTER)

add_textbox(slide, 1092200, 5500000, 9800000, 800000,
            "H N N College of Engineering • 2026-27", font_size=16, color=WHITE, alignment=PP_ALIGN.CENTER)

# Save
output_path = 'V-Core_Phase2_Final_Presentation.pptx'
prs.save(output_path)
print(f"Phase 2 presentation saved to {output_path}")
print(f"Total slides: {len(prs.slides)}")
