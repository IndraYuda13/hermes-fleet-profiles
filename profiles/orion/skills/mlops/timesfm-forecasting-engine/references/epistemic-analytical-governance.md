# Epistemic & Analytical Governance Reference (Data Analysis & Quantitative QA)

## 1. Epistemic Partitioning Standard
Every quantitative telemetry and statistical evaluation must enforce a strict 4-level epistemic partition:
1. **Level 1 — Ground Truth / Synthetic Rules**: Parameters, code rules, and failure modes injected deterministically.
2. **Level 2 — Observed Statistical Signals**: Empirical telemetry metrics directly observable in the dataset (RPS, CPU, Memory, Latencies, Errors, Queue Depths).
3. **Level 3 — Diagnostic Inferences**: Derived mathematical models, queueing approximations (e.g. Kingman, Little's Law), and structured failure hypotheses.
4. **Level 4 — Causal Assertions & Observational Bounds**: Clear distinction between statistical correlation and causality, explicitly citing unobserved confounders (e.g. internal lock contention, missing distributed tracing spans).

---

## 2. Correlation vs Causality Discipline
- **Invariant**: Cross-correlation ($R_{xy}(k)$) and lead-lag temporal precedence do **NOT** prove architectural causality.
- **Reporting Language**: Frame lagged correlations strictly as *"directional precedence in observed signals"* or *"temporal co-movement"*.
- **Observational Limitations**: State explicitly what additional instrumentation (e.g. APM distributed tracing, synthetic fault injection experiments) is required to establish true causal proof.

---

## 3. Composite Index Sensitivity & Robustness Testing
When ranking services or assets via a composite instability/risk score:
- **Mandate**: Never present a single weighting scheme as definitive.
- **Perturbation Testing**: Evaluate rankings across at least 4-5 distinct weighting schemes:
  1. *Baseline Scheme* (Standard weighted balance)
  2. *Equal Weights* (Unbiased multi-attribute baseline)
  3. *Error-Dominated* (Availability / SLO focus)
  4. *Tail-Dominated* (Latency jitter & tail risk)
  5. *Operational-Focused* (MTBF & queue stress)
- **Robustness Check**: Prove that the top/bottom tier rankings remain invariant across the weight perturbations.

---

## 4. Recommendation Proportionality & Operational Safety
- **Evidence-Bounded**: Operational recommendations must be strictly anchored to observed metrics without unevidenced architectural leaps (e.g. do not recommend database read replicas unless read vs write query distribution is measured).
- **Phased Diagnostic Safety**: Avoid destructive or aggressive automated remediation (e.g. hard pod restart at 75% heap). Use phased lifecycles:
  - *Phase 1*: Profiling & alerting threshold.
  - *Phase 2*: Diagnostic artifact collection (automated heap dump).
  - *Phase 3*: Graceful pod drain & recycle.
