# Contributing to Lean Model Lab

Read [README.md](README.md), [STATUS.md](STATUS.md), the relevant [task](TASKS.md), [architecture](ARCHITECTURE.md) and [experiment contract](EXPERIMENTS.md). Project artifacts are in English. Lucas Santana is the maintainer and decides scope and source integration.

Choose one bounded task whose prerequisites are accepted. Before implementation, agree the actual base branch/commit, owned files, acceptance evidence, available commands and resource/permission limits. One primary owner handles a coherent change. Preserve other contributors' files and avoid speculative shared infrastructure.

The first implementation task creates the runnable skeleton and documents real setup/test commands. Until then, there is nothing to install or run. Referenced engines are candidates; do not install dependencies, download model weights or datasets, or start paid experiments without the corresponding task authority and exact dependency/data review.

A contribution should contain a focused change, why it addresses the task, actual checks and failures, reproduction inputs, source/license notices and honest limitations. Unit checks prove local behavior; benchmark agreement and independent scientific interpretation require their own evidence. Never weaken a metric, tolerance, holdout or privacy boundary to make a result pass.

No speedup from dropping requests, shortening outputs, changing tokenizers, skipping quality evaluation or hiding compile time. Keep workload, quality target and hardware conditions comparable. Record failed/OOM runs. No private prompts, unauthorized model weights, arbitrary model loading code or unapproved cloud/GPU spend. Simulation cannot be presented as measured hardware performance.

Use ordinary GitHub changes for code and documentation, and the [Tanduna project](https://tanduna.com/p/lean-model-lab) for project discussion and task coordination. Submitting a contribution does not authorize automatic merge, release, deployment or real-world action. Do not post sensitive vulnerabilities, personal data or credentials publicly; contact the maintainer through an appropriate private route if needed.

Contributions of original material must be compatible with [AGPL-3.0-only](LICENSE). Keep third-party licensing and attribution intact. Cite research precisely and avoid copying paper text or datasets into the repository without the applicable rights.
