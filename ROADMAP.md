# Lean Model Lab roadmap

All eight waves and 24 tasks are **PLANNED**. No delivery date, compute allocation or completed research is promised.

## Product objective

Create an open experimental laboratory for reducing the time, memory, energy and cost of training and serving LLMs at a declared quality level. Combine analytical hardware/workload simulation with bounded, reproducible software benchmarks. Measure which techniques help on which hardware and workloads, including when they fail.

## First milestone

Define one small lawful language-model workload and a synthetic request trace. Build a reproducible baseline, then compare batching and cache policies while holding model, tokenizer, quality checks and request distribution fixed. Add a tiny training experiment with an equal-quality target. Simulated predictions and measured runs are separate result classes.

Waves 1–3 establish the first integrated experiment. Wave 4 tests whether its evidence is robust. Later waves expand domains, add agents, improve collaboration and prepare an independently reproduced research preview. Wave order is an integration dependency, not a calendar. The explicit task dependencies are in [TASKS.md](TASKS.md).

## Capacity and next planning window

Assume one maintainer and one implementation owner per coherent surface. Human reviewer availability, hardware and paid-compute budget are currently unallocated. Plan the next one or two weeks around Waves 1–2 only after measuring the first task's throughput; later tasks are outcome packages to split when prerequisites exist. The conservative dependency graph waits for the previous wave's accepted gate. Within a wave, use disjoint work only when dependencies and shared resources permit it.

Proposed initial experiment ceiling for future approval: one local worker, at most 20 trial runs, at most two elapsed compute hours and 5 GiB of new artifacts per campaign. Agent inference costs count toward an explicitly approved budget. These are draft limits, not permission to start or spend. Reduce the workload if the first benchmark cannot fit. GPU, cloud, domain-review time and additional workers need an explicit allocation before execution.

## Waves and tasks

## Wave 1: Workload and comparison contract

Outcome/gate: Quality, hardware and resource limits are specified before tuning.

Entry: No implementation prerequisite; inspect the initial plan.
- **LM-001: Freeze the first model/data workload.** Record lawful model/data sources, tokenizer, prompt/output distributions, quality target, latency requirements and evaluation split.
- **LM-002: Audit backends and measurement support.** Review exact versions/licenses/security, local hardware availability, energy measurement and approved resource limits.
- **LM-003: Build the experiment skeleton.** CLI schema distinguishes simulated/measured runs, rejects missing quality metadata and runs a synthetic trace parser without model downloads.

Gate decision: continue when the outcome is reproduced and reviewed at its appropriate evidence level; otherwise repair, reduce scope or hold. No later wave may weaken this gate.
## Wave 2: Repeatable local baselines

Outcome/gate: Measurement and simulation are separately reproducible.

Entry: Wave 1 accepted with its evidence recorded.
- **LM-004: Integrate one inference backend.** Record complete request/token accounting, warmup/startup and latency distributions on a pinned local workload.
- **LM-005: Implement a tiny training baseline.** Reproduce held-out loss and total work across declared seeds; record optimizer, data order and memory.
- **LM-006: Calibrate analytical cost models.** Fit only on calibration runs and report prediction error on held-out workloads; label simulated outputs.

Gate decision: continue when the outcome is reproduced and reviewed at its appropriate evidence level; otherwise repair, reduce scope or hold. No later wave may weaken this gate.
## Wave 3: First efficiency comparisons

Outcome/gate: Two narrow improvements are evaluated at fixed quality.

Entry: Wave 2 accepted with its evidence recorded.
- **LM-007: Compare batching and cache policies.** Use identical arrival traces and model outputs/quality constraints; include dropped, timed-out and failed requests.
- **LM-008: Compare packing or checkpointing in training.** Compare time-to-quality and memory with equivalent data exposure; include all overhead and failed runs.
- **LM-009: Publish the baseline Pareto report.** Regenerate quality, latency, memory and cost tradeoffs from raw traces with uncertainty and no universal speedup claim.

Gate decision: continue when the outcome is reproduced and reviewed at its appropriate evidence level; otherwise repair, reduce scope or hold. No later wave may weaken this gate.
## Wave 4: Benchmark integrity and holdouts

Outcome/gate: The laboratory rejects metric gaming and noise.

Entry: Wave 3 accepted with its evidence recorded.
- **LM-010: Test evaluator and workload immutability.** Reject changed tokenizers, truncated outputs, missing requests and altered quality thresholds.
- **LM-011: Measure variance and tail behavior.** Randomize run order, repeat baseline/candidate pairs and report confidence intervals and p95/p99 behavior.
- **LM-012: Confirm on untouched workloads.** Separate search from confirmation prompts/data and document hardware/thermal controls.

Gate decision: continue when the outcome is reproduced and reviewed at its appropriate evidence level; otherwise repair, reduce scope or hold. No later wave may weaken this gate.
## Wave 5: Advanced efficiency methods

Outcome/gate: New methods are added only with correctness and quality checks.

Entry: Wave 4 accepted with its evidence recorded.
- **LM-013: Evaluate quantization and speculative decoding.** Test quality loss and output equivalence where claimed; compare equal workloads and end-to-end overhead.
- **LM-014: Evaluate precision, optimizer and kernel choices.** Use numerical/gradient checks and quality targets; reject unstable or silently lower-precision comparisons.
- **LM-015: Model distributed training and serving.** Account for communication, stragglers and memory; hardware results require approved real runs distinct from simulation.

Gate decision: continue when the outcome is reproduced and reviewed at its appropriate evidence level; otherwise repair, reduce scope or hold. No later wave may weaken this gate.
## Wave 6: Agent-guided efficiency search

Outcome/gate: Agents propose useful changes under fixed budgets and evaluators.

Entry: Wave 5 accepted with its evidence recorded.
- **LM-016: Build profiler-grounded hypotheses.** Tie each proposal to a measured bottleneck and a falsifiable performance/quality expectation.
- **LM-017: Compare search with fixed baselines.** Use equal experiment/compute budgets and protected quality tests; keep negative results.
- **LM-018: Confirm and package robust recipes.** A fresh run reproduces selected gains with the exact hardware/workload scope and failure conditions.

Gate decision: continue when the outcome is reproduced and reviewed at its appropriate evidence level; otherwise repair, reduce scope or hold. No later wave may weaken this gate.
## Wave 7: Workbench and portable execution

Outcome/gate: Contributors can inspect and compare experiments safely.

Entry: Wave 6 accepted with its evidence recorded.
- **LM-019: Build the efficiency comparison view.** Expose simulated/measured labels, quality gates, full costs and invalid results with accessible tables.
- **LM-020: Add resource-limited workers.** Enforce process, storage and time quotas; stop runaway jobs and reconcile interrupted experiment costs.
- **LM-021: Export reproducible recipe bundles.** Bundle lawful configurations and traces; another machine can inspect without credentials and reproduce supported tests.

Gate decision: continue when the outcome is reproduced and reviewed at its appropriate evidence level; otherwise repair, reduce scope or hold. No later wave may weaken this gate.
## Wave 8: Independent efficiency preview

Outcome/gate: Performance claims survive independent reproduction.

Entry: Wave 7 accepted with its evidence recorded.
- **LM-022: Replicate on a second device or backend.** Report which recipes transfer; keep per-hardware outcomes separate rather than averaging away regressions.
- **LM-023: Audit measurement and researcher workflow.** An independent reviewer checks quality parity, accounting and fresh reproduction of a claimed improvement.
- **LM-024: Prepare the research preview.** Ship a bounded benchmark suite and supported recipes with maintainer approval; no unsupported best-in-class claims.

Gate decision: continue when the outcome is reproduced and reviewed at its appropriate evidence level; otherwise repair, reduce scope or hold. No later wave may weaken this gate.


## Acceptance and release

Numerical benchmarks, source rights, failure behavior and an end-to-end reproduction take precedence over task counts. Scientific extensions need their own applicability evidence; domain reviewer availability is a real dependency. High-risk interpretations require an independent qualified reviewer. A software preview can pass without demonstrating a novel scientific improvement; state the distinction explicitly.

All source and clinical/environmental/privacy/performance claims stay within [EXPERIMENTS.md](EXPERIMENTS.md). A final release needs the exact candidate, clean reproducibility instructions, lawful inputs, resolved material defects and maintainer approval. No production deploy, physical action or unrestricted autonomous execution is included.

## Stop and reduce-scope rules

If the gain is smaller than run-to-run variance, report no demonstrated improvement. If quality fails or latency tails worsen beyond the predeclared bound, reject the candidate even when tokens per second improves. If energy sensors are absent, leave measured energy unavailable instead of fabricating it.

Stop a campaign when its approved budget is exhausted, the evaluator is compromised, required provenance is missing or the task crosses its safety boundary. Do not keep adding agents to rescue an unsupported hypothesis. Cut rich visuals, distributed compute and additional domains before the initial benchmark. Reforecast after accepted task evidence, not from speculative agent throughput.
