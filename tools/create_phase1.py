from pptx import Presentation
from pptx.util import Pt, Emu, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.chart.data import CategoryChartData
from io import BytesIO
import copy
from pathlib import Path

# Resolve archive paths relative to this script's location
SCRIPT_DIR = Path(__file__).resolve().parent
ARCHIVE_DIR = SCRIPT_DIR.parent / "archive" / "presentations"

# Load template
template = Presentation(str(ARCHIVE_DIR / "5th_Semester_Mini_Project_Presentation_Template.pptx"))
existing = Presentation(str(ARCHIVE_DIR / "V-Core_Phase1_Progress_Review_CLEAN.pptx"))

# Create new presentation from template
prs = Presentation(str(ARCHIVE_DIR / "5th_Semester_Mini_Project_Presentation_Template.pptx"))

# Remove all slides except title slide (keep slide 0)
slides_to_remove = list(prs.slides)[1:]  # All except first
for slide in slides_to_remove:
    rId = prs.slides._sldIdLst[-1].rId
    prs.part.drop_rel(rId)
    prs.slides._sldIdLst.remove(prs.slides._sldIdLst[-1])

# Color constants from template
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BLUE = RGBColor(0xBE, 0xD3, 0xE5)
DARK_GRAY = RGBColor(0x69, 0x78, 0x8A)
DARK_TEXT = RGBColor(0x26, 0x30, 0x3C)
TEAL_1 = RGBColor(0x24, 0x69, 0xAA)
TEAL_2 = RGBColor(0x00, 0x97, 0xA7)
ORANGE = RGBColor(0xEB, 0x99, 0x3A)

FONT_NAME = 'Aptos'

def add_textbox(slide, left, top, width, height, text, font_size=14, bold=False, color=DARK_TEXT, alignment=PP_ALIGN.LEFT, font_name=FONT_NAME):
    """Add a textbox with formatted text"""
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
    """Add a textbox with multiple lines (paragraphs)"""
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
    """Add a textbox with bullet points"""
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

# ==========================================
# SLIDE 1: TITLE SLIDE - Copy from existing
# ==========================================
title_slide = prs.slides[0]

# Clear existing shapes except background image
shapes_to_keep = []
for shape in title_slide.shapes:
    if hasattr(shape, 'image'):
        shapes_to_keep.append(shape)

# Remove all non-image shapes
for shape in list(title_slide.shapes):
    if shape not in shapes_to_keep:
        sp = shape._element
        sp.getparent().remove(sp)

# Add title slide content from existing Phase 1
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
# SLIDE 2: INTRODUCTION AND MOTIVATION
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])

title_shape = slide.shapes.title
title_shape.text = "1. Introduction and Motivation"
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
            "02", font_size=9, color=DARK_GRAY, alignment=PP_ALIGN.RIGHT)

content_lines = [
    "Embedded systems increasingly demand real-time responsiveness and computational throughput within strict power and area constraints.",
    "The ESP32 dual-core Xtensa LX6 processor (240 MHz) offers parallel computing capability, but effective utilization requires understanding synchronization, core placement, and scheduling behavior.",
    "V-Core investigates dual-core parallel computing on ESP32 using vector dot-product as a representative computational workload.",
    "Phase 1 Focus: Single-core computational characterization, synchronization latency measurement, and cross-core behavior analysis.",
    "Motivation: Establish rigorous timing baselines before implementing parallel vector computation across both cores."
]
add_multiline_textbox(slide, 1092200, 2200000, 10000000, 4500000,
                      content_lines, font_size=16, color=DARK_TEXT, line_spacing=1.3)

# ==========================================
# SLIDE 3: PROBLEM STATEMENT
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])

title_shape = slide.shapes.title
title_shape.text = "2. Problem Statement"
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
            "03", font_size=9, color=DARK_GRAY, alignment=PP_ALIGN.RIGHT)

problem_bullets = [
    "Dual-core microcontrollers like ESP32 are widely adopted, but characterization of their parallel execution behavior is often anecdotal rather than measured.",
    "Existing literature lacks systematic measurement of:",
    "  • Computational latency across vector sizes using hardware cycle counters (CCOUNT)",
    "  • Synchronization latency: polling vs. FreeRTOS task notifications, same-core vs. cross-core",
    "  • Core-to-core variation in computational throughput",
    "  • Interaction between masked-interrupt critical sections and FreeRTOS scheduling",
    "Without measured baselines, claims of \"dual-core speedup\" cannot be substantiated.",
    "Operating Environment: ESP32 DevKit V1, ESP-IDF v6.1, FreeRTOS, 240 MHz"
]
add_bullet_textbox(slide, 1092200, 2200000, 10000000, 4500000,
                   problem_bullets, font_size=15, color=DARK_TEXT)

# ==========================================
# SLIDE 4: OBJECTIVES AND SCOPE
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])

title_shape = slide.shapes.title
title_shape.text = "3. Objectives and Scope"
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
            "04", font_size=9, color=DARK_GRAY, alignment=PP_ALIGN.RIGHT)

# Left column - Objectives
add_textbox(slide, 1092200, 2100000, 4800000, 400000,
            "Phase 1 Objectives (Completed)", font_size=16, bold=True, color=TEAL_1)

obj_bullets = [
    "O1: Characterize single-core dot-product computational latency (16–4096 elements) using CCOUNT and wall-clock timing",
    "O2: Measure timing variability and repeatability across 5 independent runs (Experiments 002, 006)",
    "O3: Evaluate periodic task interval stability under ordinary and masked-interrupt compute loads (Exp 004)",
    "O4: Characterize instrumentation overhead for CCOUNT and esp_timer_get_time() (Exp 005)",
    "O5: Measure sender-side request-to-acknowledgment latency for 4 synchronization configurations (Exp 008)",
    "O6: Compare Core 0 vs Core 1 computational behavior (Experiment 007)"
]
add_bullet_textbox(slide, 1092200, 2550000, 4800000, 3800000,
                   obj_bullets, font_size=14, color=DARK_TEXT)

# Right column - Scope
add_textbox(slide, 6200000, 2100000, 4800000, 400000,
            "Scope", font_size=16, bold=True, color=TEAL_2)

scope_bullets = [
    "Included: ESP32 DevKit V1, ESP-IDF v6.1, FreeRTOS, 240 MHz",
    "Included: Vector sizes 16/64/256/1024/4096 elements",
    "Included: CCOUNT cycle counting, wall-clock timing",
    "Included: FreeRTOS synchronization primitives (polling, notifications)",
    "",
    "Out of Scope: Simultaneous dual-core vector computation (Phase 2)",
    "Out of Scope: Wi-Fi/BT stack interaction, power profiling",
    "Out of Scope: Thermal analysis, formal WCET analysis"
]
add_bullet_textbox(slide, 6200000, 2550000, 4800000, 3800000,
                   scope_bullets, font_size=14, color=DARK_TEXT)

# ==========================================
# SLIDE 5: PROPOSED SYSTEM AND CONCEPTUAL EXECUTION MODEL
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])

title_shape = slide.shapes.title
title_shape.text = "4. Proposed System and Conceptual Execution Model"
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
            "05", font_size=9, color=DARK_GRAY, alignment=PP_ALIGN.RIGHT)

proposed_lines = [
    "V-Core: Dual-Core Parallel Computing Framework for ESP32",
    "",
    "Phase 1 (Completed) – Measurement Foundation (Experiments 007, 008):",
    "  • Core placement comparison: Core 0 vs Core 1 (Experiment 007)",
    "  • Synchronization latency taxonomy: 4 configurations measured (Experiment 008)",
    "",
    "Phase 2 (Completed) – Parallel Computation (Experiments 006, 009, 010A, 010B, 011):",
    "  • Computational baseline & repeatability (Experiment 006)",
    "  • Interference analysis (Experiment 009)",
    "  • Partitioned dual-core computation (Experiment 010A/010B)",
    "  • System/compute workload isolation (Experiment 011)",
    "",
    "Historical Foundation (Experiments 001–005):",
    "  • Early computational benchmarking, repeatability, timing sources, periodic task behavior, instrumentation overhead",
    "",
    "Key Innovation: Measurement-first approach – synchronization characterized BEFORE parallel implementation"
]
add_multiline_textbox(slide, 1092200, 2200000, 10000000, 4500000,
                      proposed_lines, font_size=15, color=DARK_TEXT, line_spacing=1.25)

# ==========================================
# SLIDE 6: ESP32 DUAL-CORE SYSTEM ARCHITECTURE
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])

title_shape = slide.shapes.title
title_shape.text = "5. ESP32 Dual-Core System Architecture"
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
            "06", font_size=9, color=DARK_GRAY, alignment=PP_ALIGN.RIGHT)

arch_lines = [
    "Phase 1 Measurement Architecture (Implemented on ESP32 DevKit V1)",
    "",
    "Hardware Platform:",
    "  • ESP32-WROOM-32: Dual-core Xtensa LX6 @ 240 MHz, 520 KB SRAM, 4 MB Flash",
    "  • Each core: Independent CCOUNT register, interrupt controller, cache",
    "  • Shared: Main memory (DRAM), peripheral bus, interrupt matrix",
    "",
    "Measurement Flow (Experiment 008):",
    "  1. Sender publishes request + timestamp →",
    "  2. Receiver processes (poll or notification-wait) →",
    "  3. Receiver publishes acknowledgment + notifies sender →",
    "  4. Sender observes ack + records elapsed cycles",
    "",
    "Four Configurations Tested:",
    "  • Same-core polling          • Same-core notification-wait",
    "  • Cross-core polling        • Cross-core notification-wait",
    "",
    "Core Affinity: xTaskCreatePinnedToCore() for explicit placement"
]
add_multiline_textbox(slide, 1092200, 2200000, 10000000, 4500000,
                      arch_lines, font_size=15, color=DARK_TEXT, line_spacing=1.2)

# ==========================================
# SLIDE 7: EXPERIMENTAL METHODOLOGY
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])

title_shape = slide.shapes.title
title_shape.text = "6. Experimental Methodology"
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
            "07", font_size=9, color=DARK_GRAY, alignment=PP_ALIGN.RIGHT)

method_lines = [
    "Dot-Product Computational Kernel (Experiments 006/007)",
    "  int32_t dot_product(const int16_t* a, const int16_t* b, size_t n) {",
    "      int32_t sum = 0;",
    "      for (size_t i = 0; i < n; i++) sum += (int32_t)a[i] * (int32_t)b[i];",
    "      return sum; }",
    "",
    "Measurement Protocol (Computational Latency):",
    "  1. Warm-up: 100 iterations (cache/TLB stabilization)",
    "  2. For each of 1,000 measured samples:",
    "     a) start = CCOUNT (Xtensa cycle counter)",
    "     b) result = dot_product(a, b, n)",
    "     c) end = CCOUNT",
    "     d) cycles = end - start; wall_time = esp_timer_get_time() diff",
    "     e) Verify checksum",
    "  3. Report: Min, Mean, Median, StdDev, P95, P99, Max",
    "",
    "Synchronization Protocol (Experiment 008):",
    "  Sender: publish request + seq_no + start_ts → wait for ack(seq_no) → elapsed = now - start_ts",
    "  Receiver: poll/wait for request → process → publish ack(seq_no) → notify sender",
    "",
    "Repeatability: 5 independent runs per experiment (Exp 002, 006)"
]
add_multiline_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                      method_lines, font_size=14, color=DARK_TEXT, line_spacing=1.15)

# ==========================================
# SLIDE 8: TECHNOLOGY STACK AND DEVELOPMENT ENVIRONMENT
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[3])

title_shape = slide.shapes.title
title_shape.text = "7. Technology Stack and Development Environment"
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
            "08", font_size=9, color=DARK_GRAY, alignment=PP_ALIGN.RIGHT)

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
    ("Source", "vcore/main/vcore.c – Modular experiment controller")
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
# SLIDE 9: IMPLEMENTATION PROGRESS - EXPERIMENTS 001-008
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])

title_shape = slide.shapes.title
title_shape.text = "8. Implementation Progress – Experiments 001–008"
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
            "09", font_size=9, color=DARK_GRAY, alignment=PP_ALIGN.RIGHT)

exp_bullets = [
    "Phase 1 – Measurement Foundation (Completed):",
    "  Experiment 007: Core placement comparison – Core 0 vs Core 1, identical workload",
    "  Experiment 008: Synchronization latency – 4 configs (polling/notification × same/cross-core), 4 runs",
    "",
    "Phase 2 – Parallel Computation & Analysis (Completed):",
    "  Experiment 006: Computational baseline – 5 vector sizes, repeatability validated",
    "  Experiment 009: Workload interference analysis – Core 1 load on Core 0 computation",
    "  Experiment 010: Dual-core partitioned computation – 1.45× speedup at 4096 elements",
    "  Experiment 011: System/compute workload isolation – 48.55× latency improvement",
    "",
    "Historical Foundation (Experiments 001–005):",
    "  Early benchmarking, repeatability, timing sources, periodic task, instrumentation overhead",
    "",
    "✓ All 11 experiments (001–011) COMPLETED and validated on hardware",
]
add_bullet_textbox(slide, 1092200, 2100000, 10000000, 4800000,
                   exp_bullets, font_size=15, color=DARK_TEXT)

# ==========================================
# SLIDE 10: EXPERIMENTAL RESULTS AND ANALYSIS - TABLES
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])

title_shape = slide.shapes.title
title_shape.text = "9. Experimental Results and Analysis"
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
            "10", font_size=9, color=DARK_GRAY, alignment=PP_ALIGN.RIGHT)

# Computational latency table
rows, cols = 7, 6
table_shape = slide.shapes.add_table(rows, cols, Emu(1092200), Emu(2100000), Emu(5500000), Emu(3000000))
table = table_shape.table

col_widths = [1200000, 900000, 900000, 900000, 900000, 700000]
for i, w in enumerate(col_widths):
    table.columns[i].width = Emu(w)

headers = ["Vector Size", "Core 0 Median", "Core 1 Median", "Core 0 StdDev", "Core 1 StdDev", "Wall-clock (µs)"]
data = [
    ["16", "515", "515", "2", "2", "2.15"],
    ["64", "1,955", "1,955", "41", "30", "8.15"],
    ["256", "7,715", "7,715", "110", "107", "32.15"],
    ["1,024", "30,755", "30,755", "145", "107", "128.15"],
    ["4,096", "122,915", "122,915", "283", "210", "512.15"],
]

for j, h in enumerate(headers):
    cell = table.cell(0, j)
    cell.text = h
    for p in cell.text_frame.paragraphs:
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.font.name = FONT_NAME
        p.alignment = PP_ALIGN.CENTER
    cell.fill.solid()
    cell.fill.fore_color.rgb = TEAL_1

for i, row_data in enumerate(data):
    for j, val in enumerate(row_data):
        cell = table.cell(i+1, j)
        cell.text = val
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(11)
            p.font.color.rgb = DARK_TEXT
            p.font.name = FONT_NAME
            p.alignment = PP_ALIGN.CENTER
        if i % 2 == 0:
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(0xF0, 0xF4, 0xF8)

# Sync results table
rows2, cols2 = 5, 3
table_shape2 = slide.shapes.add_table(rows2, cols2, Emu(7000000), Emu(2100000), Emu(4000000), Emu(2200000))
table2 = table_shape2.table

col_widths2 = [1800000, 1100000, 1100000]
for i, w in enumerate(col_widths2):
    table2.columns[i].width = Emu(w)

headers2 = ["Configuration", "Mean Latency (µs)", "Max (µs)"]
sync_data = [
    ["Same-core polling", "20.78", "33"],
    ["Same-core notification", "25.87", "35"],
    ["Cross-core polling", "18.82", "33"],
    ["Cross-core notification", "28.51", "35"],
]

for j, h in enumerate(headers2):
    cell = table2.cell(0, j)
    cell.text = h
    for p in cell.text_frame.paragraphs:
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.font.name = FONT_NAME
        p.alignment = PP_ALIGN.CENTER
    cell.fill.solid()
    cell.fill.fore_color.rgb = TEAL_2

for i, row_data in enumerate(sync_data):
    for j, val in enumerate(row_data):
        cell = table2.cell(i+1, j)
        cell.text = val
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(11)
            p.font.color.rgb = DARK_TEXT
            p.font.name = FONT_NAME
            p.alignment = PP_ALIGN.CENTER
        if i % 2 == 0:
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(0xF0, 0xF4, 0xF8)

# Key findings
findings = [
    "• Median cycles scale linearly: ~30.0 cycles/element for large vectors (1024, 4096)",
    "• Core 0 vs Core 1: Median cycles IDENTICAL across all vector sizes – no core placement difference",
    "• Core 1 shows lower StdDev (e.g., 107 vs 145 at 1024 elements)",
    "• Polling outperforms notification-wait in ALL configurations (same: +24.5%, cross: +51.5%)",
    "• Cross-core polling (18.8 µs) faster than same-core polling (20.8 µs) – unexpected, needs verification",
    "• Notification overhead: ~5 µs (same-core), ~10 µs (cross-core) additional vs polling",
    "• These are END-TO-END request-to-acknowledgment measurements, not pure API overhead"
]
add_bullet_textbox(slide, 1092200, 5200000, 10000000, 2000000,
                   findings, font_size=13, color=DARK_TEXT)

# ==========================================
# SLIDE 11: PHYSICAL HARDWARE DEMONSTRATION AND VALIDATION
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])

title_shape = slide.shapes.title
title_shape.text = "10. Physical Hardware Demonstration and Validation"
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
            "11", font_size=9, color=DARK_GRAY, alignment=PP_ALIGN.RIGHT)

hw_lines = [
    "Hardware Setup",
    "  • ESP32 DevKit V1 connected via USB-UART (/dev/cu.usbserial-0001)",
    "  • 115200 baud serial monitor (idf_monitor) for real-time log capture",
    "  • Powered via USB (5V → 3.3V regulator on DevKit)",
    "",
    "Key Implementation Highlights",
    "  • xTaskCreatePinnedToCore() for explicit core placement (Core 0 / Core 1)",
    "  • CCOUNT accessed via Xtensa RSR instruction (__builtin_rsr(\"CCOUNT\"))",
    "  • portENTER_CRITICAL()/portEXIT_CRITICAL() for interrupt masking (Exp 004)",
    "  • ulTaskNotifyTake(pdTRUE, portMAX_DELAY) for notification-wait receiver",
    "  • xTaskNotifyGive() for sender-to-receiver signaling",
    "  • 5 independent runs per experiment for repeatability (Exp 002, 006)",
    "",
    "Code Structure (vcore/main/vcore.c)",
    "  • app_main() → experiment selector → experiment runner",
    "  • Modular functions: run_dot_product_exp(), run_sync_exp(), run_periodic_exp()",
    "",
    "[Insert: Photo of ESP32 DevKit V1 setup]",
    "[Insert: Serial monitor output screenshot showing experiment results]"
]
add_multiline_textbox(slide, 1092200, 2200000, 10000000, 4500000,
                      hw_lines, font_size=14, color=DARK_TEXT, line_spacing=1.2)

# ==========================================
# SLIDE 12: VALIDATION RESULTS
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])

title_shape = slide.shapes.title
title_shape.text = "11. Validation Results"
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
            "12", font_size=9, color=DARK_GRAY, alignment=PP_ALIGN.RIGHT)

val_lines = [
    "Validation Methodology",
    "  ✓ Functional correctness: Checksum verification on every dot-product result",
    "  ✓ Repeatability: 5 independent runs (Exp 002, 006) – median CCOUNT matches exactly",
    "  ✓ Cross-validation: CCOUNT-derived time vs. wall-clock time (Exp 003: 33.2% vs 33.3% theoretical)",
    "  ✓ Instrumentation sanity: Back-to-back CCOUNT reads = 1 cycle (Exp 005)",
    "  ✓ Baseline comparison: Idle periodic task = 0 µs interval error (Exp 005)",
    "",
    "Test Results Summary",
    "  Dot-product 64-elem:    Expected 25984 → Actual 25984 → PASS",
    "  Dot-product 1024-elem:  Expected 15634 → Actual 15634 → PASS",
    "  Exp 002 Repeatability:  5 runs → Exact median match → PASS",
    "  Exp 006 Repeatability:  2 runs → Exact median match → PASS",
    "  CCOUNT overhead:        ~1 cycle → 1.000 cycle → PASS",
    "  esp_timer overhead:     <1 µs → 0.531 µs mean → PASS",
    "  Sync Exp 008:           4 configs × 4 runs × 1000 samples → All complete → PASS",
    "  Core 0 vs Core 1:       Identical workload → Medians match exactly → PASS"
]
add_multiline_textbox(slide, 1092200, 2200000, 10000000, 4500000,
                      val_lines, font_size=13, color=DARK_TEXT, line_spacing=1.15)

# ==========================================
# SLIDE 13: FUTURE WORK AND PHASE 1 CONCLUSION
# ==========================================
slide = prs.slides.add_slide(prs.slide_layouts[1])

title_shape = slide.shapes.title
title_shape.text = "12. Future Work and Phase 1 Conclusion"
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
            "13", font_size=9, color=DARK_GRAY, alignment=PP_ALIGN.RIGHT)

# Phase 1 Achievements
add_textbox(slide, 1092200, 2100000, 4800000, 400000,
            "Phase 1 Achievements (Experiments 007, 008)", font_size=16, bold=True, color=TEAL_1)

achievements = [
    "✓ Core placement comparison: Core 0 ≡ Core 1 median latency; Core 1 slightly lower variance (Exp 007)",
    "✓ Synchronization taxonomy: 4 configurations, 4 runs each, polling preferred for low latency (Exp 008)",
    "✓ Verified repeatability: Exact median match across independent runs (Exp 002, 006)",
    "✓ Instrumentation characterized: CCOUNT = 1 cycle (4.17 ns), esp_timer = 0.53 µs (Exp 005)",
    "✓ Periodic task stability measured: 0 µs error (idle), +3243 µs (masked-interrupt) (Exp 004)",
    "✓ Rigorous single-core computational latency baseline (5 vector sizes, 1000 samples, 5 repeat runs) (Exp 006)"
]
add_bullet_textbox(slide, 1092200, 2500000, 4800000, 3000000,
                   achievements, font_size=13, color=DARK_TEXT)

# Phase 2 Next Steps
add_textbox(slide, 6200000, 2100000, 4800000, 400000,
            "Phase 2 – Completed", font_size=16, bold=True, color=TEAL_2)

next_steps = [
    "✓ Experiment 006: Computational baseline & repeatability",
    "✓ Experiment 009: Interference Analysis – cross-core cache/memory contention",
    "✓ Experiment 010: Dual-Core Partitioned Computation – 1.45× speedup at 4096",
    "✓ Experiment 011: System/Compute Workload Isolation – 48.55× improvement",
    "",
    "Future Extensions:",
    "• Dynamic work-stealing scheduler for load balancing",
    "• Matrix multiplication, FFT, convolution kernels",
    "• Multi-board validation across ESP32 revisions",
]
add_bullet_textbox(slide, 6200000, 2500000, 4800000, 3000000,
                   next_steps, font_size=13, color=DARK_TEXT)

# Honest Limitations
add_textbox(slide, 1092200, 5000000, 10000000, 400000,
            "Honest Limitations", font_size=16, bold=True, color=ORANGE)

limitations = [
    "• Exp 004 vs Exp 006 baseline discrepancy (3.05%) remains unresolved",
    "• Exp 008: 4 runs completed – repeatability established on single board",
    "• Masked-interrupt mechanism not independently verified",
    "• Results specific to ESP32 DevKit V1, ESP-IDF v6.1, 240 MHz configuration",
    "• Single hardware unit – no multi-board validation",
    "• No cache coherence management for shared data"
]
add_bullet_textbox(slide, 1092200, 5400000, 10000000, 1500000,
                   limitations, font_size=13, color=DARK_TEXT)

# ==========================================
# SLIDE 14: THANK YOU
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
output_path = 'V-Core_Phase1_Progress_Review.pptx'
prs.save(output_path)
print(f"Phase 1 presentation saved to {output_path}")
print(f"Total slides: {len(prs.slides)}")
