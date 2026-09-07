# Lean Model Lab contributor tasks

All 24 tasks start **PLANNED**. [STATUS.md](STATUS.md) is the mutable progress authority; this file is the initial task contract. [plan/tasks.json](plan/tasks.json) is the machine-readable copy of that initial contract. Update both task descriptions together when scope changes. Tanduna publication/review and task execution are separate operations.

Before an implementation task starts, bind it to an actual repository branch/commit, inspect existing paths and dependencies, identify one primary owner and record the exact verification commands available in that checkout. Proposed directory names below are ownership boundaries to establish, not claims of existing modules. Later outcome packages may need decomposition at their wave gate; do not treat all 24 as one autonomous job.

Protected across every task: evaluator/holdouts outside the task's authority, accepted evidence, unrelated source, credentials, data rights, domain safety rules and resource ceilings. No production deploy, physical system connection, external outreach or paid compute is authorized by a task description. Do not commit, push or publish unless the specific contribution task authorizes it. The maintainer reviews source contributions and scientific claims separately.

## LM-001 — Freeze the first model/data workload

- Wave: 1; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: none.
- Owned scope: `docs/benchmarks/`.
- Acceptance: Record lawful model/data sources, tokenizer, prompt/output distributions, quality target, latency requirements and evaluation split.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-002 — Audit backends and measurement support

- Wave: 1; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-001.
- Owned scope: `docs/decisions/`.
- Acceptance: Review exact versions/licenses/security, local hardware availability, energy measurement and approved resource limits.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-003 — Build the experiment skeleton

- Wave: 1; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-001, LM-002.
- Owned scope: `src/`, `tests/`, `workloads/`.
- Acceptance: CLI schema distinguishes simulated/measured runs, rejects missing quality metadata and runs a synthetic trace parser without model downloads.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-004 — Integrate one inference backend

- Wave: 2; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-001, LM-002, LM-003.
- Owned scope: `adapters/inference/`.
- Acceptance: Record complete request/token accounting, warmup/startup and latency distributions on a pinned local workload.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-005 — Implement a tiny training baseline

- Wave: 2; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-001, LM-002, LM-003.
- Owned scope: `adapters/training/`.
- Acceptance: Reproduce held-out loss and total work across declared seeds; record optimizer, data order and memory.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-006 — Calibrate analytical cost models

- Wave: 2; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-001, LM-002, LM-003.
- Owned scope: `adapters/simulation/`.
- Acceptance: Fit only on calibration runs and report prediction error on held-out workloads; label simulated outputs.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-007 — Compare batching and cache policies

- Wave: 3; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-004, LM-005, LM-006.
- Owned scope: `experiments/inference/`.
- Acceptance: Use identical arrival traces and model outputs/quality constraints; include dropped, timed-out and failed requests.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-008 — Compare packing or checkpointing in training

- Wave: 3; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-004, LM-005, LM-006, LM-007.
- Owned scope: `experiments/training/`.
- Acceptance: Compare time-to-quality and memory with equivalent data exposure; include all overhead and failed runs.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-009 — Publish the baseline Pareto report

- Wave: 3; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-004, LM-005, LM-006, LM-008.
- Owned scope: `src/reports/`.
- Acceptance: Regenerate quality, latency, memory and cost tradeoffs from raw traces with uncertainty and no universal speedup claim.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-010 — Test evaluator and workload immutability

- Wave: 4; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-007, LM-008, LM-009.
- Owned scope: `tests/integrity/`.
- Acceptance: Reject changed tokenizers, truncated outputs, missing requests and altered quality thresholds.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-011 — Measure variance and tail behavior

- Wave: 4; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-007, LM-008, LM-009.
- Owned scope: `src/statistics/`.
- Acceptance: Randomize run order, repeat baseline/candidate pairs and report confidence intervals and p95/p99 behavior.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-012 — Confirm on untouched workloads

- Wave: 4; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-007, LM-008, LM-009.
- Owned scope: `benchmarks/holdout/`.
- Acceptance: Separate search from confirmation prompts/data and document hardware/thermal controls.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-013 — Evaluate quantization and speculative decoding

- Wave: 5; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-010, LM-011, LM-012.
- Owned scope: `experiments/inference/`.
- Acceptance: Test quality loss and output equivalence where claimed; compare equal workloads and end-to-end overhead.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-014 — Evaluate precision, optimizer and kernel choices

- Wave: 5; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-010, LM-011, LM-012.
- Owned scope: `experiments/training/`.
- Acceptance: Use numerical/gradient checks and quality targets; reject unstable or silently lower-precision comparisons.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-015 — Model distributed training and serving

- Wave: 5; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-010, LM-011, LM-012.
- Owned scope: `adapters/distributed/`.
- Acceptance: Account for communication, stragglers and memory; hardware results require approved real runs distinct from simulation.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-016 — Build profiler-grounded hypotheses

- Wave: 6; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-013, LM-014, LM-015.
- Owned scope: `src/agents/`.
- Acceptance: Tie each proposal to a measured bottleneck and a falsifiable performance/quality expectation.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-017 — Compare search with fixed baselines

- Wave: 6; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-013, LM-014, LM-015.
- Owned scope: `src/search/`.
- Acceptance: Use equal experiment/compute budgets and protected quality tests; keep negative results.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-018 — Confirm and package robust recipes

- Wave: 6; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-013, LM-014, LM-015.
- Owned scope: `src/evaluation/`.
- Acceptance: A fresh run reproduces selected gains with the exact hardware/workload scope and failure conditions.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-019 — Build the efficiency comparison view

- Wave: 7; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-016, LM-017, LM-018.
- Owned scope: `apps/workbench/`.
- Acceptance: Expose simulated/measured labels, quality gates, full costs and invalid results with accessible tables.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-020 — Add resource-limited workers

- Wave: 7; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-016, LM-017, LM-018.
- Owned scope: `src/workers/`.
- Acceptance: Enforce process, storage and time quotas; stop runaway jobs and reconcile interrupted experiment costs.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-021 — Export reproducible recipe bundles

- Wave: 7; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-016, LM-017, LM-018.
- Owned scope: `src/export/`.
- Acceptance: Bundle lawful configurations and traces; another machine can inspect without credentials and reproduce supported tests.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-022 — Replicate on a second device or backend

- Wave: 8; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-019, LM-020, LM-021.
- Owned scope: `benchmarks/replication/`.
- Acceptance: Report which recipes transfer; keep per-hardware outcomes separate rather than averaging away regressions.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-023 — Audit measurement and researcher workflow

- Wave: 8; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-019, LM-020, LM-021.
- Owned scope: `docs/review/`.
- Acceptance: An independent reviewer checks quality parity, accounting and fresh reproduction of a claimed improvement.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
## LM-024 — Prepare the research preview

- Wave: 8; status: **PLANNED**; owner: unassigned until accepted by Lucas Santana.
- Dependencies: LM-019, LM-020, LM-021.
- Owned scope: `docs/releases/`.
- Acceptance: Ship a bounded benchmark suite and supported recipes with maintainer approval; no unsupported best-in-class claims.
- Verification: reproduce the stated observable outcome; include one representative invalid/failure case when implementing behavior. Record exact commands and source revision after the harness exists; this plan makes no claim that those commands or tests currently exist.
- Delivery: focused diff, result/diagnostics, known limitations and a concise reproduction note. Preserve unrelated work.
