---
name: evaluation-methodology-gate
description: Reject misleading or non-comparable evaluations.
version: 1.0.0
author: Fleet Upgrade Research
license: MIT
metadata:
  hermes:
    tags: [evaluation, benchmark, statistics, experiment]
    category: fleet-upgrade
---
# Evaluation Methodology Gate

## When to Use
Use for model/agent benchmarks, A/B tests, backtests, quality scores, performance comparisons, or claims that one approach is better.

## Procedure
1. State hypothesis and decision the evaluation should support.
2. Define units/samples, inclusion/exclusion, time window, prompt/config/version, and baseline.
3. Check comparability: same task set, scoring rule, resource budget, retry policy, and environment unless explicitly studying a difference.
4. Audit leakage, selection bias, survivorship, cherry-picking, duplicate samples, and evaluator contamination.
5. Report raw counts/distribution, not only averages. Quantify uncertainty when statistically meaningful.
6. Include failure slices and counterexamples.
7. Preserve reproducibility: dataset/version, code/config, seeds where relevant, commands, timestamp.
8. Separate statistical evidence from practical impact.
9. State limits and what would falsify the conclusion.

## Verification
No winner/ranking claim without a comparable baseline, reproducible setup, sample definition, uncertainty/limitations, and evidence sufficient for the decision.
