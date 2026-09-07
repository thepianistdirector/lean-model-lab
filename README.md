# Lean Model Lab

**Find reproducible training and inference efficiency gains without hiding quality tradeoffs.**

Create an open experimental laboratory for reducing the time, memory, energy and cost of training and serving LLMs at a declared quality level. Combine analytical hardware/workload simulation with bounded, reproducible software benchmarks. Measure which techniques help on which hardware and workloads, including when they fail.

Created and maintained by **Lucas Santana** ([thepianistdirector](https://github.com/thepianistdirector)). [Tanduna project](https://tanduna.com/p/lean-model-lab) · [Public repository](https://github.com/thepianistdirector/lean-model-lab)

> **Starting from zero.** This repository currently contains project design, architecture and a contributor plan. No simulator, application, autonomous research system or benchmark result has been implemented here. All 24 build tasks are planned. Proposed capabilities below describe what we want to build.

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

Use a Python experiment controller, workload generator, process-isolated backend adapters and a protected evaluation service. Each run declares whether it is simulated or measured. A local artifact store keeps traces, token counts, quality measurements, hardware state and failures. Training and serving share experiment metadata but use different metrics and quality contracts. Begin with one local backend and small model; add distributed execution only after single-device measurements are repeatable. A future Research Continuum adapter can request experiments through the public contract without controlling this lab's evaluator.

Agents propose and interpret experiments; numerical engines and protected evaluators determine results. Every experiment retains its inputs, assumptions, source version, environment, resource budget and failure state.

## Build plan

| Wave | Outcome | Gate |
| --- | --- | --- |
| 1 | Workload and comparison contract | Quality, hardware and resource limits are specified before tuning. |
| 2 | Repeatable local baselines | Measurement and simulation are separately reproducible. |
| 3 | First efficiency comparisons | Two narrow improvements are evaluated at fixed quality. |
| 4 | Benchmark integrity and holdouts | The laboratory rejects metric gaming and noise. |
| 5 | Advanced efficiency methods | New methods are added only with correctness and quality checks. |
| 6 | Agent-guided efficiency search | Agents propose useful changes under fixed budgets and evaluators. |
| 7 | Workbench and portable execution | Contributors can inspect and compare experiments safely. |
| 8 | Independent efficiency preview | Performance claims survive independent reproduction. |

Read the [roadmap](ROADMAP.md), [24 contributor tasks](TASKS.md), [architecture](ARCHITECTURE.md), [experiment and evaluation contract](EXPERIMENTS.md), [sources and data policy](SOURCES.md) and [current state](STATUS.md). All waves are future work; a plan is not execution authorization.

## Scientific and operating boundaries

No speedup from dropping requests, shortening outputs, changing tokenizers, skipping quality evaluation or hiding compile time. Keep workload, quality target and hardware conditions comparable. Record failed/OOM runs. No private prompts, unauthorized model weights, arbitrary model loading code or unapproved cloud/GPU spend. Simulation cannot be presented as measured hardware performance.

If the gain is smaller than run-to-run variance, report no demonstrated improvement. If quality fails or latency tails worsen beyond the predeclared bound, reject the candidate even when tokens per second improves. If energy sensors are absent, leave measured energy unavailable instead of fabricating it.

## Contribute

Start with [CONTRIBUTING.md](CONTRIBUTING.md). The next eligible work is the first benchmark/contract task. Implementation follows review of exact dependency choices and a maintainer-accepted bounded task. There are no install or runtime commands yet; do not interpret proposed paths or commands as an existing application.

## Related independent projects

- [Vital Rehearsal](https://github.com/thepianistdirector/vital-rehearsal): An open simulation laboratory for physiology, disease research and safer care workflows.
- [Grid Horizons](https://github.com/thepianistdirector/grid-horizons): Simulate better grids, transformers and energy systems before proposing physical changes.
- [Earth Rehearsal](https://github.com/thepianistdirector/earth-rehearsal): A software laboratory for cleaner water, less pollution and testable climate interventions.
- [Civic Safelab](https://github.com/thepianistdirector/civic-safelab): Test public-safety sensing in synthetic worlds while measuring privacy and false alarms.
- [Research Continuum](https://github.com/thepianistdirector/research-continuum): A reproducible autonomous research system that turns hypotheses into independently checked experiments.

These repositories are independently buildable. Shared experiment formats are a design intention; there is no shared service or integration implemented today. Extract a common library only after two real implementations demonstrate the need.

## License

Original repository content is licensed under **AGPL-3.0-only**; see [LICENSE](LICENSE). Third-party data, models, papers and code retain their own terms and are not relicensed by this repository. No third-party dataset, model weights or upstream implementation is bundled in this initial planning release.
