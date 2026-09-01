# Synthetic Mutation Testing & LENS Calibration Harness

## The "Who Watches the Watcher" Invariant
A verification engine that never fails is as useless as one that always fails. To ensure LENS is not giving **Silent False PASSes** due to stale selectors, broken scripts, or loose assertions, LENS must execute a **Synthetic Mutation Benchmark** prior to auditing a production build.

---

## 1. Mutation Operators (Mutant Catalog)

The harness injects 5 distinct synthetic visual defects into a temporary sandbox copy of the target page:

| Mutant | Operator | Injected Defect | Target Gate | Expected Failure Code |
|---|---|---|---|---|
| **M1** | `InjectUndefinedText` | Injects string `"user: undefined"` into a randomly selected visible heading or card label. | Gate 1 | `G1_FORBIDDEN_TOKEN` |
| **M2** | `BreakImageSource` | Replaces an `<img>` `src` with a 404 URL and clears `naturalWidth`. | Gate 1 | `G1_BROKEN_IMAGE` |
| **M3** | `BlindContrast` | Sets text color equal to background color (`rgba(255,255,255,0.99)` on white). | Gate 2 | `G2_CONTRAST_FAIL` |
| **M4** | `ForceTextClipping` | Sets container style `height: 12px; overflow: hidden; white-space: normal;` on a 3-line paragraph. | Gate 2 | `G2_SILENT_CLIPPING` |
| **M5** | `EmptySVGContent` | Removes all child nodes from a navigation icon `<svg></svg>`. | Gate 1 | `G1_EMPTY_SVG` |

---

## 2. Calibration Execution Protocol

```
┌────────────────────────────────────────────────────────┐
│ 1. Launch Isolated Headless Browser Sandbox Context   │
└───────────────────────────┬────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│ 2. Run Mutation Suite (M1 through M5 sequentially)     │
│    For each Mutant k:                                 │
│    ├─ Inject Mutant k into sandbox DOM                │
│    ├─ Run LENS Gate 0 - Gate 2 verification pipeline  │
│    ├─ Assert that Gate reports expected failure code  │
│    └─ Rollback mutation                              │
└───────────────────────────┬────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│ 3. Calculate Mutation Score (MS)                      │
│    MS = (Detected Mutants / 5) * 100%                 │
└───────────────────────────┬────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│ 4. Calibration Gate:                                  │
│    ├─ If MS === 100%: CALIBRATION PASS -> Run Prod QA │
│    └─ If MS < 100%: CALIBRATION FAIL -> ABORT AUDIT    │
└────────────────────────────────────────────────────────┘
```

---

## 3. Calibration Invariant
$$\text{Mutation Score} = 100\% \quad (\text{Strict Invariant})$$

If LENS fails to catch even a single synthetic mutant:
- The audit run is immediately aborted.
- Verdict is set to `HARNESS_UNCALIBRATED_FAIL`.
- An incident ticket is dispatched stating which mutant bypassed detection.
- LENS is strictly forbidden from certifying production code while uncalibrated.
