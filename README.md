# Lean Model Lab

**Find reproducible training and inference efficiency gains without hiding quality tradeoffs.**

Create an open experimental laboratory for reducing the time, memory, energy and cost of training and serving LLMs at a declared quality level. Combine analytical hardware/workload simulation with bounded, reproducible software benchmarks. Measure which techniques help on which hardware and workloads, including when they fail.

Created and maintained by **Lucas Santana** ([thepianistdirector](https://github.com/thepianistdirector)). [Tanduna project](https://tanduna.com/p/lean-model-lab) · [Public repository](https://github.com/thepianistdirector/lean-model-lab)

> **Architecture foundation completed.** The three Wave 0 tasks are **DONE**: the architecture contract, outcome/dependency roadmap, and executable next-work packet with a standard-library plan validator. The original 24 scientific/build tasks remain **PLANNED**. No simulator, model integration, application, autonomous research runtime or scientific result is implemented. Acceptance and reproduced checks are recorded in [STATUS.md](STATUS.md).

## Who this is for

LLM systems researchers, inference engineers, training-framework contributors and teams running models on constrained hardware.

## First useful experiment

Define one small lawful language-model workload and a synthetic request trace. Build a reproducible baseline, then compare batching and cache policies while holding model, tokenizer, quality checks and request distribution fixed. Add a tiny training experiment with an equal-quality target. Simulated predictions and measured runs are separate result classes.

Software experiments make it possible to compare ideas repeatedly, inspect failures and share reproducible evidence without operating physical systems. They remain bounded by the quality and applicability of their models. A convincing visualization or agent report is not independent validation.

## What we want to build

### Training efficiency bench

Data loading, sequence packing, mixed precision, activation checkpointing, optimizer choices and distributed strategies, always measured against validation quality and total work.

### Inference efficiency bench

Prefill/decode separation, batching, KV-cache policies, quantization, speculative decoding and serving policies under declared workloads and quality gates.

### Hardware and workload simulation

Analytical roofline, memory and queueing models calibrated with real measurements; simulation guides experiments but cannot substantiate measured speedups.

### Quality-constrained experiment search

Agent proposals and classical search compete under equal budgets with fixed evaluators, holdouts and regression constraints.

### Portable efficiency recipes

Publish settings, source, environment, raw traces and a scoped Pareto report; reproduce on a second device before cross-hardware claims.

## Architecture in one paragraph

Use a local Python controller, versioned experiment contracts, backend adapters and a protected evaluator. Provenance binds model weights/config, data, tokenizer, workload, runtime and hardware to every attempt. Training keeps tokens, modeled/measured compute, elapsed time and time-to-quality separate; inference keeps queueing, prefill, decode, TTFT, inter-token latency, tails, throughput and SLO-qualified goodput separate. Run bundles retain raw events, full-wall costs, unavailable telemetry and negative outcomes. Begin with a no-compute contract harness, one CPU control and one reviewed local backend. Before untrusted candidates, agents or protected confirmation run, enforce read/write, credential, network and resource isolation with an OS sandbox, container or VM. Add Metal or CUDA only after exact capability probes, and add remote/distributed execution only after local budget, cancellation, recovery and replay behavior pass.

Agents propose and interpret experiments; numerical engines and protected evaluators determine results. Every experiment retains its inputs, assumptions, source version, environment, resource budget and failure state.

## Build plan

| Wave | Outcome | Gate |
| --- | --- | --- |
| 0 | Architecture and research-programme foundation | Contracts, roadmap, next packet and plan validator agree and pass authorized root review. |
| 1 | Workload and comparison contract | Quality, hardware and resource limits are specified before tuning. |
| 2 | Repeatable local baselines | Measurement and simulation are separately reproducible. |
| 3 | First efficiency comparisons | Two narrow improvements are evaluated at fixed quality. |
| 4 | Benchmark integrity and holdouts | The laboratory rejects metric gaming and noise. |
| 5 | Advanced efficiency methods | New methods are added only with correctness and quality checks. |
| 6 | Agent-guided efficiency search | Agents propose useful changes under fixed budgets and evaluators. |
| 7 | Workbench and portable execution | Contributors can inspect and compare experiments safely. |
| 8 | Independent efficiency preview | Performance claims survive independent reproduction. |

Read the [roadmap](ROADMAP.md), [27 contributor tasks](TASKS.md), [architecture](ARCHITECTURE.md), [experiment and evaluation contract](EXPERIMENTS.md), [sources and data policy](SOURCES.md) and [current state](STATUS.md). Wave 0 is accepted documentation/tooling; Waves 1–8 are future work. A plan is not execution authorization.

## Scientific and operating boundaries

No speedup from dropping requests, shortening outputs, changing tokenizers, skipping quality evaluation or hiding compile/startup/evaluation time. Keep workload, quality target and hardware/runtime conditions comparable. Record failed, OOM, cancelled and inconclusive runs. Keep development search separate from untouched confirmation evidence. No private prompts, unauthorized model weights, arbitrary model loading code or unapproved cloud/GPU spend. Simulation, profiler output and upstream capability tables cannot be presented as measured application performance.

If the gain is smaller than run-to-run variance or the predeclared practical threshold, report no demonstrated improvement. If quality fails or latency tails worsen beyond the predeclared bound, reject the candidate even when tokens per second improves. Report sensor scope and method for measured energy; when telemetry is absent, unsupported or ambiguous, mark it unavailable rather than inferring it from TDP.

## Contribute

Start with [CONTRIBUTING.md](CONTRIBUTING.md). The immediate gate is authorized root review of Wave 0. After acceptance, LM-001 freezes a bounded model/tokenizer/workload selection, LM-002 binds the local hardware/backend envelope, and LM-003 builds the standard-library no-compute contract harness. The sequence installs no backend and downloads no weights. Run `python3 tools/validate_plan.py` to check plan/document consistency; this validates the repository plan, not scientific behavior.

## Related independent projects

- [Vital Rehearsal](https://github.com/thepianistdirector/vital-rehearsal): An open simulation laboratory for physiology, disease research and safer care workflows.
- [Grid Horizons](https://github.com/thepianistdirector/grid-horizons): Simulate better grids, transformers and energy systems before proposing physical changes.
- [Earth Rehearsal](https://github.com/thepianistdirector/earth-rehearsal): A software laboratory for cleaner water, less pollution and testable climate interventions.
- [Civic Safelab](https://github.com/thepianistdirector/civic-safelab): Test public-safety sensing in synthetic worlds while measuring privacy and false alarms.
- [Research Continuum](https://github.com/thepianistdirector/research-continuum): A reproducible autonomous research system that turns hypotheses into independently checked experiments.

These repositories are independently buildable. Shared experiment formats are a design intention; there is no shared service or integration implemented today. Extract a common library only after two real implementations demonstrate the need.

## License

Original repository content is licensed under **AGPL-3.0-only**; see [LICENSE](LICENSE). Third-party data, models, papers and code retain their own terms and are not relicensed by this repository. No third-party dataset, model weights or upstream implementation is bundled in this initial planning release.
