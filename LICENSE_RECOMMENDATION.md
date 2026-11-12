# V-Core License Decision (Implemented)

Apache-2.0 has been selected and implemented for V-Core original work. This decision supersedes the former BSD-3-Clause recommendation.

Copyright 2026 Prajwal Navada G P.

SPDX-License-Identifier: Apache-2.0

The root [LICENSE](LICENSE) contains the complete, unmodified official Apache License, Version 2.0 text downloaded from <https://www.apache.org/licenses/LICENSE-2.0.txt>, including its appendix. The appendix placeholders are intentionally unchanged; the project copyright statement appears here and in [README.md](README.md#license).

Users may use, modify and distribute V-Core original work subject to the license terms. Apache-2.0 includes an express contributor patent grant, subject to its terms.

## Scope and third-party materials

The license applies only to V-Core original work. The [README exclusions](README.md#third-party-materials-and-exclusions) identify the archived college rubric and presentation template, third-party elements reused from the template, and ESP-IDF and its dependencies. Their original attribution and terms remain applicable; no third-party material is relicensed under the project's copyright.

The rubric PDF listed in `RESTRUCTURE_REPORT.md` is absent from this checkout, so its contents and terms could not be verified. The presentation template's text and metadata were inspected; no explicit license notice was found. The template is excluded from the original-work license, and the file and existing credits are unchanged.

## Implementation notes

- No experimental source headers, firmware, measurements, research reports, presentations, images or build configuration were changed in this licensing pass.
- No NOTICE file was added: inspection identified no actual attribution notices requiring a repository NOTICE file. Apache-2.0 does not require creating a NOTICE file merely because work is modified; section 4(d) addresses notices when a distributed work includes one. Preserve applicable third-party notices when distributing dependencies or other third-party materials.
- Source-level copyright and SPDX headers may be considered separately.
