# License Recommendation for V-Core

## Recommendation: **BSD-3-Clause (Modified BSD License)**

### Rationale

| Criterion | MIT | BSD-3-Clause | Apache-2.0 |
|-----------|-----|--------------|------------|
| **Permissive** | ✅ | ✅ | ✅ |
| **Source code reuse allowed** | ✅ | ✅ | ✅ |
| **Attribution required** | ✅ | ✅ | ✅ |
| **No endorsement clause** | ❌ | ✅ | ✅ |
| **Patent grant** | ❌ | ❌ | ✅ |
| **Complexity** | Lowest | Low | Medium |
| **Academic/embedded common** | Very High | High | Medium |
| **Hardware/ESP32 ecosystem** | Common | Common | Less common |

### Why BSD-3-Clause for V-Core?

1. **Academic/Embedded Norm**: BSD licenses are standard in embedded systems and academic projects (FreeRTOS uses MIT, ESP-IDF uses Apache-2.0, but many research projects use BSD).

2. **No Endorsement Clause**: The BSD-3-Clause explicitly prohibits using the author's name to endorse derived products — appropriate for academic work.

3. **Simple & Clear**: Less verbose than Apache-2.0, well-understood by embedded developers.

4. **Compatible**: Compatible with ESP-IDF (Apache-2.0) and FreeRTOS (MIT) dependencies.

5. **Attribution Preserved**: Requires keeping copyright notice and license text in source distributions.

### Alternative: MIT License

If you prefer maximum simplicity and the widest adoption:
- MIT is the shortest permissive license
- Used by FreeRTOS itself
- Slightly more permissive (no endorsement restriction)

### Alternative: Apache-2.0

If patent protection matters:
- Explicit patent grant from contributors
- Used by ESP-IDF
- More verbose, requires NOTICE file for modifications

---

## Decision Required

**No LICENSE file has been created.** The project maintainer should:

1. Review the three options above
2. Select one (BSD-3-Clause recommended)
3. Create `LICENSE` file with chosen license text
4. Add SPDX headers to source files (optional but recommended)

### Example BSD-3-Clause Header for Source Files

```c
/*
 * V-Core: Dual-Core Parallel Computing on ESP32
 * Copyright (c) 2026, Prajwal Navada G P
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived from
 *    this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */
```

---

## Next Steps

- [ ] Maintainer selects license
- [ ] Create `LICENSE` file
- [ ] Add SPDX headers to `vcore/main/vcore.c` and `legacy-code/*.c`
- [ ] Verify compatibility with ESP-IDF v6.1 (Apache-2.0) and FreeRTOS (MIT) dependencies