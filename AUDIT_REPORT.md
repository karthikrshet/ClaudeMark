# CLAUDEMARK END-TO-END ENGINEERING AUDIT

**Version:** 2.1.0  
**Commit:** faaf547  
**Audit Date:** 2026-08-17  
**Auditor:** Antigravity AI - Lead Security / QA / Architecture Review  
**Repository:** https://github.com/karthikrshet/ClaudeMark  
**Platform Tested:** Windows 11 AMD64, Python 3.10.11  

---

## Executive Summary

ClaudeMark is a local-first, zero-egress AI watermark detection and provenance forensics toolkit. It ships a functional CLI, REST API, web dashboard, Unicode forensics engine, provenance inspector, metadata sanitizer, security scanner, SARIF exporter, benchmark system, and AI-agent tool schemas without mandatory network dependencies.

The audit found the project **genuinely functional at its core** with 97 passing tests and correct behavior on the majority of tested features. However, several **real, confirmed bugs** and **documentation mismatches** were found that must be addressed before claiming production readiness.

**CRITICAL:** The rewrite/disruption engine always returns `rewritten_text == original_text` with `word_change_ratio: 0.0` — it performs **no actual text transformation**. This directly contradicts README claims about watermark disruption.

**CRITICAL:** `validate_safe_path()` without a `base_dir` does NOT prevent path traversal — arbitrary absolute paths are returned from user input.

**HIGH:** JSON reports hardcode version `0.1.0` instead of `2.1.0`.

**HIGH:** `claudemark --version` flag is not recognized (exits with error).

---

## Overall Score: 70/100

| Dimension | Score |
|---|---|
| Architecture | 82/100 |
| Correctness (core) | 65/100 |
| Security | 74/100 |
| Privacy / Zero-Egress | 91/100 |
| CLI Quality | 76/100 |
| API Quality | 72/100 |
| Web UI | 68/100 |
| Watermark Research Quality | 45/100 |
| Unicode Forensics | 88/100 |
| Provenance Handling | 70/100 |
| Sanitization | 71/100 |
| Multimedia Support | 52/100 |
| AI-Agent Integration | 78/100 |
| CI/CD | 72/100 |
| SARIF Exporter | 82/100 |
| Packaging | 77/100 |
| Testing | 60/100 |
| Performance | 75/100 |
| Documentation | 62/100 |
| Developer Experience | 78/100 |
| Scientific Validity | 48/100 |
| Release Readiness | 64/100 |

**Classification: REQUIRES FIXES** (before claiming v2.1.0 Production Stable)

---

## 1. FEATURE COVERAGE

| Feature | Status | Evidence | Problems | Recommendation |
|---|---|---|---|---|
| `claudemark version` | PASS | Returns v2.1.0 | None | - |
| `claudemark version --json` | PASS | JSON correct | None | - |
| `claudemark capabilities` | PASS | All tools listed | None | - |
| `claudemark doctor` | PASS | Runtime, tools, modules shown | None | - |
| `claudemark analyze --text` | PASS | Output rendered | JSON version field says 0.1.0 | Fix JSON version |
| `claudemark --version` | FAIL | Exit 1: unrecognized argument | Should work per convention | Add --version flag |
| `claudemark agent tools` | FAIL | Exit 2: invalid choice | Real subcommand is `agent list` | Fix docs |
| `claudemark agent exec` | FAIL | Exit 2: arg parse fails | Invocation format broken | Fix arg parser |
| `claudemark unicode inspect` | PASS | All 15 anomaly types detected | - | - |
| `claudemark unicode visualize` | PASS | Renders ZWSP markers | - | - |
| `claudemark unicode normalize` | PASS | Idempotent, removes ZWSP | - | - |
| `claudemark unicode clean` | PASS | Strips zero-width chars | - | - |
| `claudemark rewrite` | FAIL | word_change_ratio=0.0 always | No text transformation occurs | Fix or document |
| `claudemark audit dir` | PASS | Recursive audit works | - | - |
| `claudemark audit ../../etc` | PASS | Fails gracefully | Path not hardened without base_dir | Add CWD containment |
| `claudemark benchmark` | PASS | Matrix output renders | - | - |
| `claudemark schema` | PASS | JSON schema output | - | - |
| `claudemark security` | PASS | Help shows | risk_level named threat_level in actual dict | Fix docs |
| `claudemark serve` | PASS | Help correct | Dockerfile port mismatch | Align ports |
| Statistical detectors | PARTIAL | 4 detectors present | `composite_score` always 0.0 via Python API | Fix API field |
| Watermark disruption | FAIL | rewritten_text==original always | Zero words changed | Feature broken |
| Unicode forensics API | PASS | All anomaly types detected | - | - |
| Provenance inspection | PASS | inspect_single_file works | Needs exiftool/c2patool for full capability | Document |
| Metadata sanitization | PASS | clean_single_file runs | Needs pypdf/python-docx | Document |
| SARIF exporter | PASS | Valid SARIF 2.1.0 produced | `build_sarif_report()` not exported | Update docs |
| Agent tools schema | PASS | 8 tools, all schema-valid | - | - |
| Path traversal with base_dir | PASS | Correctly blocked | - | - |
| Path traversal no base_dir | CONCERN | `../../etc/passwd` ALLOWED | Arbitrary paths accepted | Add default CWD containment |
| Null byte injection | PASS | Blocked at validate_safe_path | - | - |
| REST API auth | PASS | Bearer token enforced when key set | CORS wildcard on all responses | Restrict in prod |
| REST API endpoints | PASS | /health /capabilities /api/analyze work | - | - |
| Sentence heatmap | NOT TESTABLE | Exists in web dashboard | Cannot test without browser | - |
| Docker | PARTIAL | Dockerfile valid | Runs as root; port 8765 vs 8950 | Fix both |
| GitHub Action | PARTIAL | action.yml present | --version fails; action may break | Fix --version |
| Pre-commit hooks | PARTIAL | .pre-commit-hooks.yaml present | Untested end-to-end | - |
| claudemark.pixel.backends | FAIL | ImportError: No module | Advertised in capabilities but missing | Fix or remove |
| CHANGELOG for 2.1.0 | FAIL | Only 2.0.0 entry exists | No 2.1.0 changelog | Add entry |

---

## 2. TEST RESULTS

| Metric | Value |
|---|---|
| Total Tests | 97 |
| Passed | 97 |
| Failed | 0 |
| Skipped | 0 |
| XFailed | 0 |
| Coverage | Not measured (pytest-cov not configured) |

> **Important caveat:** All 97 tests pass but several do NOT verify documented behavior. The rewrite test checks a result is returned, not that text changes. The watermark test checks a score is returned, not that `composite_score` is populated. Tests pass but do not prove correctness of key documented features.

---

## 3. SECURITY FINDINGS

### SEC-001 - HIGH: Path Traversal Not Blocked Without base_dir

**Component:** claudemark/provenance/base.py -> validate_safe_path()

**Evidence (executed):**
```
validate_safe_path("../../../etc/passwd")      => c:\Users\karti\etc\passwd  [ALLOWED]
validate_safe_path("../../Windows/System32")   => [arbitrary path]  [ALLOWED]
validate_safe_path(".", base_dir="tests")      => blocked correctly  [PASS]
```

**Attack Scenario:** An agent tool call `execute_agent_tool("inspect_provenance", {"file_path": "../../etc/shadow"})` resolves to an arbitrary absolute path. Fails gracefully only because the target does not exist, not because it was blocked.

**Impact:** File enumeration and read if any handler opens the resolved path before checking existence.

**Recommended Fix:**
```python
if base_dir is None:
    base_dir = Path.cwd()
```
**Priority:** P0  **Status:** OPEN

---

### SEC-002 - MEDIUM: Dockerfile Runs as Root

**Evidence:** No USER directive in Dockerfile.  
**Impact:** Any RCE or file write grants full container control.  
**Fix:** Add `RUN addgroup --system cmuser && adduser --system --ingroup cmuser cmuser` then `USER cmuser`.  
**Priority:** P1  **Status:** OPEN

---

### SEC-003 - MEDIUM: Port Mismatch Between Dockerfile and CLI

**Evidence:** Dockerfile EXPOSE 8765 but server.py defaults to port 8950.  
**Impact:** Docker container serves on 8950 while 8765 is exposed — service unreachable without explicit port mapping.  
**Fix:** Align Dockerfile CMD to `--port 8765`.  
**Priority:** P1  **Status:** OPEN

---

### SEC-004 - LOW: CORS Wildcard on All Endpoints

**Evidence:** `Access-Control-Allow-Origin: *` on every response.  
**Impact:** Cross-origin API calls from any web page.  
**Fix:** `CLAUDEMARK_CORS_ORIGINS` environment variable.  
**Priority:** P2  **Status:** OPEN

---

### SEC-005 - LOW: Security Scanner Field Name Mismatch

**Evidence:** Actual report dict key is `threat_level` but documentation and examples reference `risk_level`. Consumer code using `risk_level` gets KeyError.  
**Priority:** P2  **Status:** MINOR

---

### SEC-006 - INFO: No Rate Limiting on REST API

**Impact:** DoS via resource exhaustion on public deployments.  
**Fix:** Document reverse proxy (nginx/caddy) requirement.  
**Priority:** P3  **Status:** OPEN

---

## 4. FUNCTIONAL BUGS

### BUG-001 - CRITICAL: Watermark Rewrite Returns Identical Text

**Component:** claudemark/rewrite/paraphrase.py

**Evidence (executed):**
```python
res = disrupt_watermark(
    "The following content demonstrates AI-generated patterns.",
    strategy="synonym_cadence"
)
d = res.to_dict()
assert d["rewritten_text"] == d["original_text"]  # True — identical
assert d["word_change_ratio"] == 0.0              # True — always zero
assert d["watermark_score_delta"] == 0.0          # True — always zero
```
All strategies (`synonym_cadence`, `cadence_only`) and all inputs (long AI text, human text, short text) return unchanged text.

**Impact:** The primary advertised feature — watermark disruption — performs no transformation. Users are misled.  
**Recommendation:** Implement synonym substitution via NLTK WordNet, or clearly document as "not yet implemented."

---

### BUG-002 - CRITICAL: composite_score Missing from Python API

**Component:** claudemark/__init__.py -> analyze_text() return value

**Evidence (executed):**
```python
res = analyze_text("text", detector_name="claude")
wm = res["watermark_result"].to_dict()
# Actual keys: algorithm_name, signal_score, confidence, status,
#              interpretation, threshold, features, hypothesis,
#              limitations, is_watermarked
# composite_score does NOT exist
wm.get("composite_score", 0)  # => 0 silently — always
```

**Impact:** All agent tools and Python consumers receive 0.0 for the watermark score, making automated decisions impossible.

---

### BUG-003 - HIGH: --version Flag Not Supported

**Evidence (executed):**
```
$ python claudemark.py --version
error: unrecognized arguments: --version   [exit code 1]
```
**Impact:** GitHub Action, CI scripts, and README install verification fail.  
**Fix:** Add `parser.add_argument("--version", action="version", ...)` at top-level parser.

---

### BUG-004 - HIGH: agent tools Subcommand Does Not Exist

**Evidence (executed):**
```
$ claudemark agent tools
error: argument subcommand: invalid choice: 'tools' (choose from 'list', 'exec')
```

---

### BUG-005 - HIGH: JSON Report Hardcodes Version 0.1.0

**Evidence (executed):**
```json
{"tool": "ClaudeMark", "version": "0.1.0", "source": "<raw_text>"}
```
**Fix:** Use `from claudemark import __version__` dynamically in json_report.py.

---

### BUG-006 - MEDIUM: claudemark.pixel.backends Module Missing

**Evidence (executed):**
```
ImportError: No module named 'claudemark.pixel.backends'
```
Capabilities output lists 6 pixel backends (synthid-image, ctrlregen, etc.) but the submodule does not exist.

---

### BUG-007 - MEDIUM: CHANGELOG Missing v2.1.0 Entry

**Evidence:** CHANGELOG.md highest entry is `[2.0.0] - 2026-08-16`. No 2.1.0 entry exists.

---

### BUG-008 - MEDIUM: normalize_text() Returns Object Not String

**Evidence (live crash):**
```python
from claudemark import normalize_text
result = normalize_text("Hello world")
# type(result) => NormalizationResult, NOT str
# len(result) => TypeError: object of type 'NormalizationResult' has no len()
```
**Fix:** Add `normalize_text_str()` convenience wrapper or document `.normalized_text` attribute prominently.

---

## 5. DOCUMENTATION MISMATCHES

| Documented Claim | Actual Behavior | Severity |
|---|---|---|
| `claudemark --version` works | Exit 1: unrecognized argument | HIGH |
| `claudemark agent tools` is valid | Command is `agent list` | HIGH |
| Watermark disruption changes text | word_change_ratio=0.0, text identical | CRITICAL |
| JSON report version is current | Hardcoded "0.1.0" | HIGH |
| `pip install claudemark && claudemark --version` | --version fails | HIGH |
| CHANGELOG entry for v2.1.0 | Only 2.0.0 entry exists | MEDIUM |
| claudemark.pixel.backends importable | ImportError | MEDIUM |
| `build_sarif_report()` function | Is `convert_audit_report_to_sarif()` | MEDIUM |
| `normalize_text()` returns str | Returns NormalizationResult | MEDIUM |
| Dev Status: Production/Stable | Multiple P0 bugs | LOW |
| Dockerfile EXPOSE 8765 | CLI default port is 8950 | MEDIUM |

---

## 6. SCIENTIFIC VALIDITY

**Detector Methodology Assessment:**

- PASS: Output includes explicit caveats ("This is a probabilistic research result", "must not be used as definitive proof")
- PASS: Hypothesis test framework (null/alternative hypotheses, p-values) is structurally correct
- PASS: Short text limitations are documented
- CONCERN: "Kirchenbauer detector" does not implement Kirchenbauer et al. 2023 green/red token lists — it uses heuristic entropy/burstiness analysis. Naming implies algorithm fidelity that does not exist.
- CONCERN: Benchmark metrics are deterministic but datasets are synthetic fixtures, not real human/AI corpora. External validity is unproven.
- FAIL: Rewrite disruption claims "watermark disruption" but produces no textual change. A system that changes nothing cannot claim to disrupt anything.

**Verdict:** Appropriate for a research prototype labeled as such. Not appropriate as a production system without honest algorithm naming and a functional rewrite engine.

---

## 7. ZERO-EGRESS AUDIT

| Operation | Network Access | Verdict |
|---|---|---|
| analyze_text() | None | Confirmed offline |
| unicode inspect/normalize/clean | None | Confirmed offline |
| audit_directory() | None | Confirmed offline |
| scan_security() | None | Confirmed offline |
| disrupt_watermark() | None | Confirmed offline |
| doctor command | None | Confirmed offline |
| REST API /api/analyze | None | Confirmed offline |
| inspect_single_file() | Optional local binary only (exiftool/c2patool) | Local subprocess only |
| benchmark --reproduce | None | Confirmed offline |
| pixel.registry | None | Confirmed offline |

**Zero-egress verdict: PASS** for all core operations. Stdlib-only runtime. No telemetry detected. All analysis, forensics, and API operations confirmed local.

---

## 8. DEPENDENCY AUDIT

| Dependency | Status | Notes |
|---|---|---|
| pillow>=9.0.0 | Optional, available | Image processing |
| pypdf>=3.0.0 | Optional, NOT installed | PDF sanitization unavailable |
| python-docx>=0.8.11 | Optional, NOT installed | DOCX sanitization unavailable |
| pytest>=7.0.0 | Dev only | OK |
| Zero mandatory runtime deps | PASS | stdlib-only core |

pip-audit: Not run. No known CVEs in stdlib-only core.

**Risk:** Package name `claudemark` is not published on PyPI. Squatting risk — register immediately even if not publishing yet.

---

## 9. PERFORMANCE RESULTS

| Workload | Time | Notes |
|---|---|---|
| analyze_text() — 200 words | ~0.3ms | Excellent |
| analyze_unicode_forensics() — 200 chars | ~0.1ms | Excellent |
| disrupt_watermark() — 320 chars | ~1ms | Acceptable |
| audit_directory() — 3 files | ~50ms | Acceptable |
| Full test suite (97 tests) | ~10s | Good |
| CLI startup | ~1.5s | Python import cost |
| claudemark doctor | ~3s | Tool discovery overhead |

No O(n^2) bottlenecks identified. No memory leaks detected in tested paths.

---

## 10. API / CLI COMPATIBILITY

### Broken Commands

| Command | Expected | Actual |
|---|---|---|
| `claudemark --version` | Version string | Exit 1: unrecognized argument |
| `claudemark agent tools` | Tool list | Exit 2: invalid choice 'tools' |
| `claudemark agent exec --tool X --args {}` | Execute tool | Exit 2: argument parsing fails |

### Schema Issues

| Field | Expected | Actual |
|---|---|---|
| JSON report `version` | `"2.1.0"` | `"0.1.0"` (hardcoded) |
| WatermarkResult.composite_score | float | Field does not exist; use signal_score |
| SecurityScanReport.risk_level | str | Field is named `threat_level` |

---

## 11. SECURITY HARDENING RECOMMENDATIONS

| Priority | Finding | Recommendation |
|---|---|---|
| P0 | SEC-001: Path traversal without base_dir | Default base_dir=Path.cwd() in validate_safe_path() |
| P0 | BUG-001: Rewrite returns original text | Fix or document as not-yet-implemented |
| P1 | BUG-002: composite_score always 0.0 | Add alias or document signal_score |
| P1 | BUG-003: --version flag broken | Add top-level --version argument |
| P1 | SEC-002: Docker runs as root | Add USER directive to Dockerfile |
| P1 | SEC-003: Docker port mismatch | Align Dockerfile CMD port to 8765 |
| P2 | BUG-005: JSON report version wrong | Use __version__ dynamically |
| P2 | BUG-006: pixel.backends missing | Add stub or remove from capabilities |
| P2 | SEC-004: CORS wildcard | Add CLAUDEMARK_CORS_ORIGINS env var |
| P3 | SEC-006: No rate limiting | Document reverse proxy requirement |

---

## 12. TOP 20 IMPROVEMENTS

| # | Priority | Problem | Why It Matters | Recommended Fix | Expected Benefit |
|---|---|---|---|---|---|
| 1 | P0 | Rewrite engine is a no-op | Core selling point broken | Implement NLTK WordNet synonym substitution | Turns broken feature real |
| 2 | P0 | Path traversal no base_dir | Real security vulnerability | Default base_dir=Path.cwd() | Closes attack surface |
| 3 | P1 | composite_score missing | Silent failure for all API consumers | Add composite_score = signal_score alias | Fixes downstream consumers |
| 4 | P1 | --version broken | Breaks CI and GitHub Action | Add top-level --version argument | Immediate CI fix |
| 5 | P1 | JSON version hardcoded 0.1.0 | Wrong metadata everywhere | Use __version__ dynamically | Fixes all consumers |
| 6 | P1 | Docker runs as root | Security violation | Add USER cmuser to Dockerfile | Container hardening |
| 7 | P1 | Docker port mismatch | Service unreachable | Align CMD to --port 8765 | Fixes Docker deployment |
| 8 | P1 | CHANGELOG not updated | Users cannot track changes | Add [2.1.0] section | Maintainability |
| 9 | P1 | normalize_text() type surprise | TypeError crashes consumer code | Add normalize_text_str() wrapper | Developer experience |
| 10 | P1 | pixel.backends import fails | False capability listing | Create stub or remove from listing | Correctness |
| 11 | P1 | agent tools command missing | Broken documented example | Add tools as alias for list | Documentation trust |
| 12 | P2 | PyPI package not published | pip install fails | Publish or remove install claim | Adoption |
| 13 | P2 | Coverage not measured | Unknown code paths | Add pytest-cov with 60% gate | Quality assurance |
| 14 | P2 | Detector names misleading | Implies algorithm fidelity | Rename to heuristic-style names | Scientific integrity |
| 15 | P2 | SARIF function name inconsistent | Docs show non-existent function | Export build_sarif_report alias | API consistency |
| 16 | P2 | No /api/unicode/analyze integration test | Endpoint in OpenAPI, untested | Add integration test | Test completeness |
| 17 | P2 | CORS wildcard | Unrestricted cross-origin access | CLAUDEMARK_CORS_ORIGINS env var | Security posture |
| 18 | P3 | serve port not configurable via env | Confusing for deployments | Add CLAUDEMARK_PORT env var | Developer experience |
| 19 | P3 | No rate limiting | DoS risk on public deployments | Document nginx reverse proxy | Operational safety |
| 20 | P3 | Dev Status 5-Production/Stable | Misleading with active P0 bugs | Change to 4-Beta | Honest signalling |

---

## 13. WHAT IS WORKING WELL

### Unicode Forensics Engine — Outstanding
Correctly detects all 15 tested anomaly types: ZWSP, ZWNJ, ZWJ, BOM, BiDi LRE/RLO, NBSP, hair space, Cyrillic homoglyphs, Unicode Tags (U+E0074), multiple zero-width characters, and null bytes. Normalization is idempotent. Visualization renders correctly. **This is the strongest part of the project.**

### Zero-Egress Architecture — Genuine
All core operations confirmed offline by execution. Stdlib-only runtime enables air-gapped deployment — a real engineering achievement.

### Path Injection Security — Much Improved (with base_dir)
`validate_safe_path()` now uses `normpath + abspath + prefix check` satisfying CodeQL taint analysis. Null bytes blocked. `_resolve_agent_path()` in tools.py adds a second defensive layer. Server uploads use `tempfile.TemporaryDirectory` with base_dir containment.

### SARIF 2.1.0 Export — Correct
`convert_audit_report_to_sarif()` produces valid SARIF 2.1.0 with correct `version`, `runs`, `tool.driver`, and `results`. Verified by JSON parse and field inspection.

### Agent Tool Schema — Well Structured
All 8 agent tools have complete JSON Schema definitions with `required` arrays and `enum` constraints. `execute_agent_tool()` correctly raises ValueError on unknown tools and blocks null bytes.

### REST API Authentication — Correct
Bearer token authentication works when `CLAUDEMARK_SERVER_API_KEY` is set. `/health` and static assets bypass auth correctly. 401 returned with request body consumed.

### Doctor / Diagnostics — Useful
Checks Python version, 6 active detectors, 3 optional system binaries, 3 format modules, and 5 agent ecosystems. Output is clear and actionable.

### Test Infrastructure — Solid Foundation
97 tests across 23 files covering Unicode, API, CLI, security scanner, watermark, edge cases, and zero-egress. Platform-safe on Windows.

---

## 14. RELEASE DECISION

**Decision: NO-GO for "Production Stable"**

**Acceptable as: GO (Beta / v2.1.0-beta)**

**Reasoning:**
- Rewrite engine (core selling point) performs no transformation — alone disqualifies "production stable"
- JSON report hardcodes wrong version — a basic CI check would catch this
- `--version` flag broken — breaks documented install verification
- Docker silently misconfigured (port mismatch + runs as root)
- CHANGELOG missing for current version

The project **is** suitable for open-source beta release once BUG-001 (rewrite), BUG-003 (--version), SEC-001 (path traversal default), and BUG-005 (JSON version) are fixed.

---

## 15. NEXT RELEASE ROADMAP

### v2.1.1 — Security Patch (target: within 1 week)
- Fix SEC-001: default `base_dir=Path.cwd()` in `validate_safe_path()`
- Fix BUG-003: add `--version` top-level flag to CLI parser
- Fix BUG-005: use `__version__` dynamically in `json_report.py`
- Fix SEC-002/003: Dockerfile non-root user + port alignment to 8765
- Add CHANGELOG entry for v2.1.0 and v2.1.1

### v2.2 — Correctness Release (target: 4 weeks)
- Fix BUG-001: implement word-level synonym substitution in rewrite engine (NLTK WordNet or curated map)
- Fix BUG-002: add `composite_score` alias property to `WatermarkResult`
- Fix BUG-008: add `normalize_text_str()` convenience wrapper
- Fix BUG-006: resolve `claudemark.pixel.backends` import or remove from capabilities
- Add `tools` as alias for `list` in agent subparser
- Add `pytest-cov` with 60% minimum coverage gate
- Publish to PyPI

### v3.0 — Research Integrity Release (target: 3 months)
- Rename detectors to reflect actual implementation (heuristic, not peer-reviewed algorithm)
- Implement Kirchenbauer et al. green/red list detection with tokenizer integration
- Implement basic synonym substitution rewrite (NLTK WordNet)
- Add real human/AI benchmark corpus (1000+ samples per class)
- Bundle `pypdf` + `python-docx` as optional-but-easily-installed default extras
- Add rate limiting middleware or document reverse proxy setup
- Graduate from `Development Status :: 4 - Beta` to `5 - Production/Stable`

---

## FIX THESE FIRST

1. **BUG-001** — Rewrite engine returns identical text: implement synonym substitution or remove the feature from marketing claims
2. **SEC-001** — `validate_safe_path()` allows arbitrary paths when `base_dir` is unset: add default CWD containment
3. **BUG-003** — `claudemark --version` exits with error: add standard `--version` flag to top-level parser
4. **BUG-005** — JSON report shows version `0.1.0`: use `__version__` dynamically in `json_report.py`
5. **SEC-002/003** — Dockerfile runs as root with wrong exposed port: add `USER` directive and fix `CMD --port`

---

*This report was produced by evidence-based execution audit. All findings are reproducible on commit `faaf547` of https://github.com/karthikrshet/ClaudeMark. No test results were fabricated. Features marked FAIL were confirmed broken by direct invocation. Audit conducted: 2026-08-17.*
