# Lean Model Lab roadmap

Wave 0 is **DONE**: its three architecture-foundation tasks were accepted by the authorized root after independent review and reproduced checks. All 24 original scientific/build tasks remain **PLANNED** across Waves 1–8. The programme now contains nine waves and 27 tasks; no scientific result or runtime is claimed.

## Product objective

Create an open experimental laboratory for reducing the time, memory, energy and cost of training and serving LLMs at a declared quality level. Combine analytical hardware/workload simulation with bounded, reproducible software benchmarks. Measure which techniques help on which hardware and workloads, including when they fail.

## First implemented milestone

Define one small lawful language-model workload and a synthetic request trace. Build a reproducible baseline, then compare batching and cache policies while holding model, tokenizer, quality checks and request distribution fixed. Add a tiny training experiment with an equal-quality target. Simulated predictions and measured runs are separate result classes.

Wave 0 establishes the research and execution contract. Waves 1–3 establish the first integrated experiment. Wave 4 tests whether its evidence is robust. Later waves expand methods, add bounded search, improve contributor inspection and prepare an independently reproduced research preview. Wave order is an integration dependency, not a calendar. The explicit task dependencies are in [TASKS.md](TASKS.md).

## Research-programme horizon

The eight build waves are the path to a credible first research preview, not the ceiling of the project. After independent reproduction, later programmes may study model/data/compute allocation, end-to-end training systems, online serving under mixed workloads, memory/energy constraints and transfer across heterogeneous devices. Each new programme needs a new model/workload/evaluator envelope and its own evidence gate. A result from a tiny local model cannot be extrapolated into a frontier-training, fleet-serving or cross-hardware claim.

The scale sequence is evidence-driven:

1. prove contracts and failure handling without model compute;
2. reproduce one CPU/local-backend control under a bounded workload;
3. qualify one accelerator/backend combination without changing workload semantics;
4. establish useful ablation/search/confirmation separation;
5. reproduce on a second exact device or backend;
6. add multiple local and then remote workers only after budgets, leases, cancellation, recovery and artifact validation are reliable.

## Capacity and next planning window

Assume one maintainer and one implementation owner per coherent surface. Human reviewer availability and paid-compute budget are currently unallocated. The planning host observed on 2026-09-07 is an arm64 Apple M5 Mac with 16 GiB memory and Metal 4; this is an inventory observation, not an approved benchmark target or proof of backend compatibility. No CUDA device, `llama-cli` or `llama-server` was found on that host. Python 3.14.6 is present, but candidate packages must prove version compatibility before adoption.

Plan the next one or two weeks around the Wave 0 review and Waves 1–2 only after measuring the first packet's throughput; later tasks are outcome packages to split when prerequisites exist. The conservative dependency graph waits for the previous wave's accepted gate. Within a wave, use disjoint work only when dependencies and shared resources permit it.

Proposed initial experiment ceiling for future approval: one local worker, at most 20 trial runs, at most two elapsed compute hours and 5 GiB of new artifacts per campaign. Agent inference costs count toward an explicitly approved budget. These are draft limits, not permission to start or spend. Reduce the workload if the first benchmark cannot fit. GPU, cloud, domain-review time and additional workers need an explicit allocation before execution.

## Waves and tasks

## Wave 0: Architecture and research-programme foundation

Outcome/gate: The product, measurement, isolation, evaluator, artifact, execution and scale contracts are coherent; the original task graph remains intact; and the next no-compute packet can start without guessing after authorized root acceptance.

Entry: Documentation-only repository at commit `f55f872c74caf0a5fa6f4503042ec22733adc2e3`; no runtime or scientific evidence inherited.

- **LM-F01: Establish the architecture and experiment contract.** Define provenance, metric semantics, measurement controls, candidate/evaluator isolation, artifacts, durable execution and platform seams.
- **LM-F02: Establish the outcome and dependency roadmap.** Connect local-first evidence gates to later heterogeneous and remote research without inventing dates, budget or implemented capability.
- **LM-F03: Establish an executable next-work packet and repository-plan validation.** Specify the bounded workload/model/hardware decision and no-compute harness entry; provide a standard-library graph/document validator.

Gate decision: the authorized root reviews the exact diff and validator result. On acceptance, record evidence in [STATUS.md](STATUS.md), move LM-F01–LM-F03 to `DONE`, and admit LM-001. If corrections reopen the batch, move all three coherently to `IN_PROGRESS` or `BLOCKED` and record the finding. Waves 1–8 stay blocked until this gate passes.

## Wave 1: Workload and comparison contract

Outcome/gate: Quality, hardware and resource limits are specified before tuning.

Entry: Wave 0 accepted with its evidence recorded; LM-001 additionally depends on LM-F03.
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

All scientific, quality, performance, energy, cost and portability claims stay within [EXPERIMENTS.md](EXPERIMENTS.md). A final release needs the exact candidate, clean reproducibility instructions, lawful inputs, resolved material defects and maintainer approval. No production deploy, physical action or unrestricted autonomous execution is included.

## Stop and reduce-scope rules

If the gain is smaller than run-to-run variance, report no demonstrated improvement. If quality fails or latency tails worsen beyond the predeclared bound, reject the candidate even when tokens per second improves. If energy sensors are absent, leave measured energy unavailable instead of fabricating it.

Stop a campaign when its approved budget is exhausted, the evaluator is compromised, required provenance is missing or the task crosses its safety boundary. Do not keep adding agents to rescue an unsupported hypothesis. Cut rich visuals, distributed compute and additional domains before the initial benchmark. Reforecast after accepted task evidence, not from speculative agent throughput.
