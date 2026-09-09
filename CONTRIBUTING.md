# Contributing to Lean Model Lab

Read [README.md](README.md), [STATUS.md](STATUS.md), the relevant [task](TASKS.md), [architecture](ARCHITECTURE.md) and [experiment contract](EXPERIMENTS.md). Project artifacts are in English. Lucas Santana is the maintainer and decides scope and source integration.

Choose one bounded task whose prerequisites are accepted. Before implementation, agree the actual base branch/commit, owned files, acceptance evidence, available commands and resource/permission limits. One primary owner handles a coherent change. Preserve other contributors' files and avoid speculative shared infrastructure.

The current v1 lane has a runnable standard-library CLI, pinned CPU model/backend profiles, strict paired experiments, recovery, evidence export and registered research interventions. Start with [the research runbook](docs/RUNBOOK-V1.md). Local contract tests run with `PYTHONPATH=src python3 -m unittest discover -s tests -v`; plan checks use `python3 tools/validate_plan.py`. Fixture tests do not load the real model. Actual model experiments require the operator's finite resource allocation and admitted dependencies; existing authorization persists within its scope.

A contribution should contain a focused change, why it addresses the task, actual checks and failures, reproduction inputs, source/license notices and honest limitations. Unit checks prove local behavior; benchmark agreement and independent scientific interpretation require their own evidence. Never weaken a metric, tolerance, holdout or privacy boundary to make a result pass.

No speedup from dropping requests, shortening outputs, changing tokenizers, skipping quality evaluation or hiding compile/startup/evaluation time. Keep workload, quality target and hardware/runtime conditions comparable. Record failed, OOM, cancelled and inconclusive attempts. No private prompts, unauthorized model weights, arbitrary model loading code or unapproved cloud/GPU spend. Simulation, profiler output and upstream capability tables cannot be presented as measured application performance.

Use ordinary GitHub changes for code and documentation, and the [Tanduna project](https://tanduna.com/projects/lean-model-lab) for project discussion and task coordination. Submitting a contribution does not authorize automatic merge, release, deployment or real-world action. Do not post sensitive vulnerabilities, personal data or credentials publicly; contact the maintainer through an appropriate private route if needed.

Contributions of original material must be compatible with [AGPL-3.0-only](LICENSE). Keep third-party licensing and attribution intact. Cite research precisely and avoid copying paper text or datasets into the repository without the applicable rights.

Useful contributions include an independent rerun of a frozen published study with all failures retained; an accessible-workbench review using actual keyboard, zoom and narrow-screen observations; a prospective workload that tests a specific limitation of the structured grammar; and a bounded mechanism with source-backed prior-art analysis, an explicit comparator and causal ablation. Confirm the current task ledger before claiming a slot. Do not tune against an existing confirmation population or count a second analysis of one study as an independent finding.

Include the exact CLI hash, recipe, environment, command, expected behavior and observed error when reporting a runtime problem. Preserve the original study; use a fresh directory for a corrective run. See [compatibility and troubleshooting](docs/COMPATIBILITY-AND-TROUBLESHOOTING.md) for schema and recovery boundaries.

Another concrete contribution is to measure and reduce coordinator/resource-monitor overhead under a controlled workspace inventory while preserving disk, memory, deadline and process-ownership protections. The separate reproduction identifies whole-workspace traversal as a plausible timing confound, not a proven cause or an already validated optimization. Such a change needs its own controlled comparison and must not rewrite the frozen producer's results.
