# V-Core Repository Restructure Report

**Date**: 2026-11-12  
**Purpose**: Document controlled repository restructuring for public GitHub release

---

## 1. Original Directory Structure

```
V-Core/
├── .vscode/
├── build/                          # ESP-IDF build artifacts (ignored)
├── docs/
│   ├── V-Core_Experiment_007_Report.docx
│   ├── V-Core_Experiments_006_008_009_Consolidated_Report.docx
│   └── vcore_experiment_001_dot_product_baseline.md
├── legacy-code/
│   ├── exp6.c
│   ├── exp7.c
│   ├── exp8.c
│   ├── exp8v2.c
│   ├── exp8v3.c
│   ├── exp9v2.c
│   ├── exp9v3.c
│   ├── exp10a.c
│   ├── exp10b.c
│   ├── exp11.c
│   └── expected.c
├── vcore/
│   ├── build/                      # ESP-IDF build artifacts (ignored)
│   ├── logs/
│   │   ├── experiment-002-repeatability.txt
│   │   ├── experiment-003-240mhz.txt
│   │   ├── experiment-004.txt
│   │   ├── experiment-005.txt
│   │   ├── experiment-006.txt
│   │   ├── experiment-007-core0-run2-3.txt
│   │   ├── experiment-007-core0.txt
│   │   ├── experiment-007-core1-run2-3.txt
│   │   ├── experiment-007-core1.txt
│   │   ├── experiment-008.md
│   │   ├── experiment-008.txt
│   │   ├── experiment-009.txt
│   │   ├── experiment-010b.txt
│   │   ├── experiment-10a.txt
│   │   └── experiment-11.txt
│   ├── main/
│   │   ├── CMakeLists.txt
│   │   └── vcore.c
│   ├── CMakeLists.txt
│   ├── calculate_time.py
│   ├── sdkconfig
│   └── sdkconfig.old
├── .DS_Store
├── .gitignore
├── 5th_Semester_Mini_Project_Presentation_Template.pptx
├── Circular3- CSE- Miniproject- BCS568-BIS568-BAD568-projectrubrics2112026 (1).pdf
├── LICENSE_RECOMMENDATION.md
├── Notes.txt
├── README.md
├── V-Core_Phase1_Progress_Review.pptx
├── V-Core_Phase1_Progress_Review_CLEAN.pptx
├── V-Core_Phase2_Final_Presentation.pptx
├── V1 api.png
├── create_phase1.py
├── create_phase2.py
├── exp11.png
└── exp9 table.png
```

---

## 2. Final Directory Structure

```
V-Core/
│
├── README.md
├── LICENSE_RECOMMENDATION.md
├── .gitignore
│
├── firmware/
│   ├── active/                     # Canonical active ESP-IDF project
│   │   ├── main/
│   │   │   └── vcore.c             # Experiment 011 firmware (active)
│   │   ├── CMakeLists.txt
│   │   ├── sdkconfig               # Tracked for reproducibility
│   │   └── calculate_time.py
│   │
│   └── experiments/                # Authoritative experiment implementations
│       ├── exp006/
│       │   └── exp006.c            # Exp 006 computational baseline
│       ├── exp007/
│       │   └── exp007.c            # Exp 007 core placement
│       ├── exp008/
│       │   └── exp008.c            # Exp 008 sync latency (FINAL CANDIDATE)
│       ├── exp009/
│       │   └── exp009.c            # Exp 009 interference
│       ├── exp010/
│       │   ├── exp010a.c           # Exp 010A single-core baseline
│       │   └── exp010b.c           # Exp 010B dual-core partitioned
│       ├── exp011/
│       │   └── exp011.c            # Exp 011 system/compute isolation
│       └── expected.c              # Checksum references
│
├── data/
│   ├── raw/                        # Original serial captures (unmodified)
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
│   └── processed/                  # Derived results and experiment summaries
│       └── experiment-008.md       # Exp 008 methodology & 4-run results
│
├── research/
│   ├── reports/                    # Formal DOCX reports
│   │   ├── V-Core_Experiment_007_Report.docx
│   │   └── V-Core_Experiments_006_008_009_Consolidated_Report.docx
│   │
│   └── methodology/                # Research methodology documentation
│       └── experiment-001-baseline.md
│
├── tools/
│   ├── create_phase1.py            # Phase 1 presentation generator (pathlib paths)
│   ├── create_phase2.py            # Phase 2 presentation generator (pathlib paths)
│   └── Notes.txt                   # Cycle/time conversions, cross-checks
│
├── archive/
│   ├── source/                     # Superseded experiment versions
│   │   ├── exp8.c
│   │   ├── exp8v2.c
│   │   └── exp9v2.c
│   │
│   ├── presentations/              # Superseded presentation files
│   │   ├── 5th_Semester_Mini_Project_Presentation_Template.pptx
│   │   ├── V-Core_Phase1_Progress_Review.pptx
│   │   ├── V-Core_Phase1_Progress_Review_CLEAN.pptx
│   │   └── V-Core_Phase2_Final_Presentation.pptx
│   │
│   └── images/                     # Diagram images
│       ├── V1 api.png
│       ├── exp11.png
│       └── exp9 table.png
│
└── vcore/                          # Backward-compatible copy of firmware/active/
    ├── main/
    │   └── vcore.c
    ├── CMakeLists.txt
    ├── sdkconfig
    └── calculate_time.py
```

---

## 3. Complete Old-Path → New-Path Mapping

### Firmware — Canonical Active ESP-IDF Project (`firmware/active/`) and Backward-Compatible Copy (`vcore/`)

| Old Path | New Path | Action |
|----------|----------|--------|
| vcore/CMakeLists.txt | firmware/active/CMakeLists.txt | Copied |
| vcore/sdkconfig | firmware/active/sdkconfig | Copied (tracked) |
| vcore/sdkconfig.old | (removed) | Removed; backup only |
| vcore/calculate_time.py | firmware/active/calculate_time.py | Copied |
| vcore/main/CMakeLists.txt | firmware/active/main/CMakeLists.txt | Copied |
| vcore/main/vcore.c | firmware/active/main/vcore.c | Copied |
| (same files) | vcore/... | Retained for backward compatibility |

### Firmware — Experiment Implementations (legacy-code/ → firmware/experiments/)

| Old Path | New Path | Action |
|----------|----------|--------|
| legacy-code/exp6.c | firmware/experiments/exp006/exp006.c | Moved |
| legacy-code/exp7.c | firmware/experiments/exp007/exp007.c | Moved |
| legacy-code/exp8v3.c | firmware/experiments/exp008/exp008.c | Moved (renamed) |
| legacy-code/exp9v3.c | firmware/experiments/exp009/exp009.c | Moved (renamed) |
| legacy-code/exp10a.c | firmware/experiments/exp010/exp010a.c | Moved |
| legacy-code/exp10b.c | firmware/experiments/exp010/exp010b.c | Moved |
| legacy-code/exp11.c | firmware/experiments/exp011/exp011.c | Moved |
| legacy-code/expected.c | firmware/experiments/expected.c | Moved |

### Archive — Superseded Source Versions (legacy-code/ → archive/source/)

| Old Path | New Path | Action |
|----------|----------|--------|
| legacy-code/exp8.c | archive/source/exp8.c | Moved |
| legacy-code/exp8v2.c | archive/source/exp8v2.c | Moved |
| legacy-code/exp9v2.c | archive/source/exp9v2.c | Moved |

### Data — Raw Serial Captures (vcore/logs/ → data/raw/)

| Old Path | New Path | Action |
|----------|----------|--------|
| vcore/logs/experiment-002-repeatability.txt | data/raw/experiment-002-repeatability.txt | Moved |
| vcore/logs/experiment-003-240mhz.txt | data/raw/experiment-003-240mhz.txt | Moved |
| vcore/logs/experiment-004.txt | data/raw/experiment-004.txt | Moved |
| vcore/logs/experiment-005.txt | data/raw/experiment-005.txt | Moved |
| vcore/logs/experiment-006.txt | data/raw/experiment-006.txt | Moved |
| vcore/logs/experiment-007-core0.txt | data/raw/experiment-007-core0.txt | Moved |
| vcore/logs/experiment-007-core1.txt | data/raw/experiment-007-core1.txt | Moved |
| vcore/logs/experiment-007-core0-run2-3.txt | data/raw/experiment-007-core0-run2-3.txt | Moved |
| vcore/logs/experiment-007-core1-run2-3.txt | data/raw/experiment-007-core1-run2-3.txt | Moved |
| vcore/logs/experiment-008.txt | data/raw/experiment-008.txt | Moved |
| vcore/logs/experiment-009.txt | data/raw/experiment-009.txt | Moved |
| vcore/logs/experiment-10a.txt | data/raw/experiment-010a.txt | Moved (renamed) |
| vcore/logs/experiment-010b.txt | data/raw/experiment-010b.txt | Moved |
| vcore/logs/experiment-11.txt | data/raw/experiment-011.txt | Moved (renamed) |

### Data — Processed Results (vcore/logs/ → data/processed/)

| Old Path | New Path | Action |
|----------|----------|--------|
| vcore/logs/experiment-008.md | data/processed/experiment-008.md | Moved |

### Research — Reports (docs/ → research/reports/)

| Old Path | New Path | Action |
|----------|----------|--------|
| docs/V-Core_Experiment_007_Report.docx | research/reports/V-Core_Experiment_007_Report.docx | Moved |
| docs/V-Core_Experiments_006_008_009_Consolidated_Report.docx | research/reports/V-Core_Experiments_006_008_009_Consolidated_Report.docx | Moved |

### Research — Methodology (docs/ → research/methodology/)

| Old Path | New Path | Action |
|----------|----------|--------|
| docs/vcore_experiment_001_dot_product_baseline.md | research/methodology/experiment-001-baseline.md | Moved (renamed) |

### Tools (root → tools/)

| Old Path | New Path | Action |
|----------|----------|--------|
| create_phase1.py | tools/create_phase1.py | Moved |
| create_phase2.py | tools/create_phase2.py | Moved |
| Notes.txt | tools/Notes.txt | Moved |

### Archive — Presentations (root → archive/presentations/)

| Old Path | New Path | Action |
|----------|----------|--------|
| 5th_Semester_Mini_Project_Presentation_Template.pptx | archive/presentations/5th_Semester_Mini_Project_Presentation_Template.pptx | Moved |
| V-Core_Phase1_Progress_Review.pptx | archive/presentations/V-Core_Phase1_Progress_Review.pptx | Moved |
| V-Core_Phase1_Progress_Review_CLEAN.pptx | archive/presentations/V-Core_Phase1_Progress_Review_CLEAN.pptx | Moved |
| V-Core_Phase2_Final_Presentation.pptx | archive/presentations/V-Core_Phase2_Final_Presentation.pptx | Moved |

### Archive — Images (root → archive/images/)

| Old Path | New Path | Action |
|----------|----------|--------|
| V1 api.png | archive/images/V1 api.png | Moved |
| exp11.png | archive/images/exp11.png | Moved |
| exp9 table.png | archive/images/exp9 table.png | Moved |

### Archive — PDF (root → archive/)

| Old Path | New Path | Action |
|----------|----------|--------|
| Circular3- CSE- Miniproject- BCS568-BIS568-BAD568-projectrubrics2112026 (1).pdf | archive/Circular3- CSE- Miniproject- BCS568-BIS568-BAD568-projectrubrics2112026 (1).pdf | Moved |

---

## 4. Files Intentionally Retained

| Path | Reason |
|------|--------|
| vcore/ | **Ignored local legacy copy** of firmware/active/ (listed in .gitignore); retained for local backward compatibility only — not tracked in git |
| vcore/build/ | Build artifacts (excluded by .gitignore) |
| vcore/logs/ | Empty directory retained (original logs moved to data/raw/) |
| .vscode/ | IDE configuration (excluded by .gitignore) |
| build/ | Root build artifacts (excluded by .gitignore) |
| .DS_Store | macOS metadata (excluded by .gitignore) |

---

## 5. Files Removed / Archived

| File | New Location / Action | Reason |
|------|----------------------|--------|
| sdkconfig.old (both locations) | Removed | Generated backup only; not needed for reproducibility |
| legacy-code/ (entire directory) | Contents migrated, directory removed | All files migrated to firmware/experiments/ or archive/source/ |
| research/analysis/ | Removed (empty) | Empty placeholder |
| research/paper/ | Removed (empty) | Empty placeholder |
| docs/ | Removed (empty) | Empty placeholder |
| exp8.c, exp8v2.c, exp9v2.c | archive/source/ | Superseded experiment versions |
| 4 PPTX presentation files | archive/presentations/ | Superseded presentation versions |
| 3 PNG diagram images | archive/images/ | Supporting images for presentations |
| 1 PDF rubric | archive/ | Course rubric document |

---

## 6. Checksum Verification Results

All critical source files and raw logs verified byte-for-byte identical before and after restructuring.

### Source Files (.c) — All Match ✅

| File | Original MD5 | New Location MD5 | Match |
|------|--------------|------------------|-------|
| exp6.c | c75a91ca7eb2f74be2874f1052a6a763 | firmware/experiments/exp006/exp006.c | ✅ |
| exp7.c | 8d22d1f05654902176c0e4f13c978405 | firmware/experiments/exp007/exp007.c | ✅ |
| exp8v3.c | 112b129a6c4f1742b39087fe73840e07 | firmware/experiments/exp008/exp008.c | ✅ |
| exp9v3.c | bf6306c0f18445da384927110db5c2d8 | firmware/experiments/exp009/exp009.c | ✅ |
| exp10a.c | c69cbe156400a96cf5e139f2772b6167 | firmware/experiments/exp010/exp010a.c | ✅ |
| exp10b.c | b99a514b7b279775bcf46ee3ef52ece6 | firmware/experiments/exp010/exp010b.c | ✅ |
| exp11.c | 9c2e6fb66f2cd3532310d35e9f73f2c6 | firmware/experiments/exp011/exp011.c | ✅ |
| expected.c | 7676a1df0d6d38c5f2031cfcb7b1db79 | firmware/experiments/expected.c | ✅ |
| vcore.c (active) | 112b129a6c4f1742b39087fe73840e07 | firmware/active/main/vcore.c, vcore/main/vcore.c | ✅ |

### Raw Logs (.txt) — All Match ✅

| File | Original MD5 | New Location MD5 | Match |
|------|--------------|------------------|-------|
| experiment-002-repeatability.txt | abe94e48b104e7c1e0d2f0c48b732398 | data/raw/experiment-002-repeatability.txt | ✅ |
| experiment-003-240mhz.txt | 9f91466fc4cf43ad1b2434c164e3022f | data/raw/experiment-003-240mhz.txt | ✅ |
| experiment-004.txt | ffc626fd1b880e9af7d73e390c08d586 | data/raw/experiment-004.txt | ✅ |
| experiment-005.txt | be621966373be1e91750b81fd9c92a51 | data/raw/experiment-005.txt | ✅ |
| experiment-006.txt | 6455495a96046888a5f2d49ab11c49fe | data/raw/experiment-006.txt | ✅ |
| experiment-007-core0.txt | b83c3947a77c54cc94880d9bd159cac8 | data/raw/experiment-007-core0.txt | ✅ |
| experiment-007-core1.txt | 84a3e786491f3cdab4354a6de6c2a093 | data/raw/experiment-007-core1.txt | ✅ |
| experiment-007-core0-run2-3.txt | 92a5fadc506bd886568f5fc09167cecc | data/raw/experiment-007-core0-run2-3.txt | ✅ |
| experiment-007-core1-run2-3.txt | 3e07ad707eb16ee1780b7546436e1538 | data/raw/experiment-007-core1-run2-3.txt | ✅ |
| experiment-008.txt | 26101caf448cc54369749bec981cb002 | data/raw/experiment-008.txt | ✅ |
| experiment-009.txt | 45ae193c6f7f6af15973f6a948ee0675 | data/raw/experiment-009.txt | ✅ |
| experiment-10a.txt → 010a.txt | e6d00bcfeb02a103c8d9eed866a6cb18 | data/raw/experiment-010a.txt | ✅ |
| experiment-010b.txt | 6ba649818fc4b6e5ff6b272db10d2ce7 | data/raw/experiment-010b.txt | ✅ |
| experiment-11.txt → 011.txt | 4a6c5cf03ccaf31d1ae5bbd08e2dfe50 | data/raw/experiment-011.txt | ✅ |

### Documentation (.md) — All Match ✅

| File | Original MD5 | New Location MD5 | Match |
|------|--------------|------------------|-------|
| vcore_experiment_001_dot_product_baseline.md | 37e3265fcb51f4208843c3965e76354b | research/methodology/experiment-001-baseline.md | ✅ |
| experiment-008.md | d4566aa155e6e1f41b61bfe5e77aff0a | data/processed/experiment-008.md | ✅ |

### Files Modified (Expected)

| File | Original MD5 | New MD5 | Reason |
|------|--------------|---------|--------|
| create_phase1.py | 664fbbf4b6295d879fd567ea2a2a5f5a | d4f3c7bf652586cb401ee656d45af0ac | Pathlib-based PPTX path resolution |
| create_phase2.py | ef1585a5d2cfb7b87a2048b82ef67560 | 2d75a416886c6c1c65a000fd431b3b9c | Pathlib-based PPTX path resolution |
| README.md | b9fc1887b81a25f04bd8a0260c85e6fa | c39fd2dcd60b4d875261348c8f997207 | Repository structure and paths updated |
| .gitignore | (not tracked) | (updated) | sdkconfig tracked, sdkconfig.old ignored, archive tracked |

---

## 7. Build Verification Results

### Canonical Active ESP-IDF Project (`firmware/active/`)
- **Structure verified**: CMakeLists.txt, main/CMakeLists.txt, main/vcore.c, sdkconfig, calculate_time.py all present
- **Build system**: Standard ESP-IDF CMake project
- **Expected result**: Buildable with `cd firmware/active && idf.py build` (ESP-IDF v6.1 required)

### Backward-Compatible Copy (`vcore/`)
- **Structure verified**: Identical to firmware/active/
- **Expected result**: Buildable with `cd vcore && idf.py build`

### Build Verification Status: ❌ Not Executed
> **Blocker**: ESP-IDF v6.1 not available in current environment (`idf.py` not in PATH). Source file equivalence verified via checksums (all match), but actual buildability cannot be confirmed. Per instructions, both copies retained until build verification is possible.

---

## 8. Broken References Found and Corrected

### README.md
- **Repository Structure section**: Updated from old flat structure to new hierarchical structure
- **Building & Running**: Path updated from `cd vcore` to `cd firmware/active` (with note about vcore/ backward compatibility)
- **Key Results sources**: Updated from `vcore/logs/*` to `data/raw/*` and `data/processed/*`
- **Documentation Index**: Updated all paths to new locations
- **Original Contributions #6**: Updated from `legacy-code/` to `firmware/experiments/` and `vcore/logs/` to `data/raw/`

### tools/create_phase1.py
- **Lines 12-16**: Hardcoded relative paths replaced with pathlib-based resolution:
  ```python
  SCRIPT_DIR = Path(__file__).resolve().parent
  ARCHIVE_DIR = SCRIPT_DIR.parent / "archive" / "presentations"
  template = Presentation(str(ARCHIVE_DIR / "5th_Semester_Mini_Project_Presentation_Template.pptx"))
  existing = Presentation(str(ARCHIVE_DIR / "V-Core_Phase1_Progress_Review_CLEAN.pptx"))
  prs = Presentation(str(ARCHIVE_DIR / "5th_Semester_Mini_Project_Presentation_Template.pptx"))
  ```
- **Path robustness**: Paths now resolve relative to script location, not working directory

### tools/create_phase2.py
- **Lines 11-15**: Same pathlib-based resolution applied
- **Path robustness**: Paths now resolve relative to script location, not working directory

### .gitignore
- **Removed**: `sdkconfig` and `sdkconfig.old` from ignore list (primary sdkconfig now tracked)
- **Added**: `sdkconfig.old` explicitly ignored (backup only)
- **Added**: `firmware/active/build/` to build exclusions
- **Removed**: `archive/` from ignore list (archive directory now tracked)
- **Retained**: `vcore/` in ignore list (local legacy copy, not tracked in git)

---

## 9. Final Integrity Verification

| Check | Status | Evidence |
|-------|--------|----------|
| All authoritative C source files unchanged | ✅ | 8 files, all MD5 match |
| All 14 raw serial captures byte-for-byte unchanged | ✅ | 14 files, all MD5 match |
| Processed Exp008 documentation unchanged | ✅ | 1 file, MD5 match |
| README paths valid | ✅ | All 12 referenced paths exist |
| Single canonical active ESP-IDF project | ✅ | `firmware/active/` (vcore/ retained as copy) |
| No research evidence deleted | ✅ | All logs, reports, methodology preserved |
| .gitignore preserves research files | ✅ | Archive, data, research, firmware all tracked |

---

## 10. Remaining Organizational Issues

| Issue | Description | Priority |
|-------|-------------|----------|
| Dual project copies | Both `vcore/` (ignored, local only) and `firmware/active/` (canonical, tracked) exist; buildability of canonical not verified | Medium — remove vcore/ after successful build test |
| vcore/logs/ empty | Directory retained but empty after log migration | Low — harmless |
| Root build/ directory | Build artifacts (excluded by .gitignore) | Low — harmless |

---

## 11. Actions Requiring Maintainer Approval

1. **License selection**: `LICENSE_RECOMMENDATION.md` recommends BSD-3-Clause; no `LICENSE` file created yet
2. **Git initialization**: Repository not yet initialized; `git init` and initial commit pending
3. **Build verification**: Install ESP-IDF v6.1, test `cd firmware/active && idf.py build`
4. **Large file handling**: PPTX files (~2 MB total) in `archive/presentations/` — consider Git LFS
5. **Local legacy copy**: `vcore/` is intentionally ignored in .gitignore; decide whether to keep it locally after build verification or remove it

---

## Summary

✅ **All original files accounted for** — 47 files tracked through restructuring  
✅ **All raw logs preserved byte-for-byte** — 14 serial captures in `data/raw/`  
✅ **All authoritative experiment implementations preserved** — 8 source files in `firmware/experiments/`  
✅ **Canonical active ESP-IDF project established** — `firmware/active/` (with `vcore/` as ignored local legacy copy)  
✅ **Configuration cleanup complete** — sdkconfig tracked, sdkconfig.old ignored and removed  
✅ **Empty directories removed** — research/analysis/, research/paper/, docs/  
✅ **Python script path robustness** — create_phase1.py, create_phase2.py use pathlib  
✅ **All Markdown links resolved** — README.md updated with new paths  
✅ **README.md reflects new structure** — Complete rewrite with new hierarchy  
✅ **.gitignore preserves research evidence** — Archive, data, research, firmware tracked; build artifacts excluded; vcore/ intentionally ignored  
✅ **No accidental duplicates or orphans** — Every file has exactly one canonical location (except vcore/ as ignored local copy)  
✅ **No source, log, PPTX, or PNG content modified** — Only path references updated in scripts and documentation  

The repository is now clean, traceable, and ready for the subsequent research evidence audit and public GitHub release, pending ESP-IDF build verification of the canonical firmware project.