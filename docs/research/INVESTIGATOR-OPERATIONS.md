# Local investigator operations — v1 development package 03

This is the single campaign under owner dispatch `tanduna-v1-research-20260908-lean-model-lab`. Investigators start only after the first actual native proposal→recipe→run→inspect/report→recovery→export workflow is retained. All investigators are verified GPT-6 Astra leaves; only the active root delegates. No public release or new spending is authorized.

## Exact product and resources

Run from the source workspace root. The executable is `.cache/packaged-v1-platform-20260908-03/lean-model-lab.pyz`, SHA-256 `f90c48dd0be36b29c3188c365ba6b8ab2cbe709897cd7f4cce0e4825a147db6f`, implementation `fe572bc610c0bc395672bf8b4e8f681260e2e6bdccf4280d6a7ec0784c30d5fe`. Its version is `1.0.0.dev0`, a local development candidate. Read [the user runbook](../RUNBOOK-V1.md), use its CLI, and retain every output. An investigator's scratch implementation cannot substitute for the platform.

The existing allocation is `.cache/allocation-0.4-20260908.json`: original monotonic start `267268865220540`, deadline `310468865220540`, at most 12 compute threads, 60 decimal GB RAM, 200 decimal GB project disk, and one heavy job. Waiting, development, failed requests, searches, compilation and review stay inside that clock; no reset or extra spend is authorized. Prefer two compute threads for 0.5B and at most six for additional 14B work. Final studies and reproduction share this finite envelope.

Use `python3 tools/run_queued_recipe.py` with the exact `--archive`, `--recipe`, `--server`, `--model`, `--setup`, `--output` arguments. The source helper serializes investigators and invokes the archive exactly once. Do not launch native `run` directly while other investigators are active. Do not rerun a failed confirmation automatically. The product acquires its own heavy lease and verifies actual model/runtime identities. Queue receipts and native attempt inventories are different evidence layers.

Already acquired model paths:

| Profile | Backend | Model entrypoint | Current allocation setup |
| --- | --- | --- | --- |
| Qwen2.5 0.5B FP16 | `.cache/prepared-20260908-01/build/bin/llama-server` | `.cache/prepared-20260908-01/qwen2.5-0.5b-instruct-fp16.gguf` | `.cache/adopted-0.5b-current-02/setup.json` after first-workflow adoption |
| Qwen2.5 14B FP16 | `.cache/prepared-14b-20260908-01/build/bin/llama-server` | `.cache/prepared-14b-20260908-01/qwen2.5-14b-instruct-fp16-00001-of-00008.gguf` | `.cache/prepared-14b-20260908-01/setup.json` |

Both pinned official checkpoints declare Apache-2.0; exact repositories, commits, shard hashes, sizes, template and acquisition evidence are in the platform profiles and preparation receipts. Weights are separate and are not included in research exports. The backend is the pinned MIT llama.cpp revision plus the retained local patch. Generated record tasks are original AGPL-3.0-only project data. Read notices and retain exact identities rather than inferring from the display name.

## Scientific and operational rules

Freeze question, nearest primary sources, model/runtime, mechanism, comparator/ablations, development and confirmation populations, seeds, quality/cost criteria, uncertainty and stopping rule before confirmation. Use the `research` and `recipe` CLI. Minimum measurement population is 128 requests and two balanced AB/BA pairs. The unchanged gate requires both arms to reach 95% task accuracy and no observed pair-level aggregate accuracy loss; same-input controls additionally require exact output token parity. Report per-request harmful and beneficial changes as well as aggregate accuracy. Do not tune on confirmation, lower a gate or describe service-only improvements as complete cost savings.

A dependency certificate proves only facts about the restricted record grammar. A symbolic interpreter solves these tasks without an LLM. The learned acceptance controller is an actual small trained tree with empirical calibration, not LLM training, a new architecture or a formal population-risk guarantee. Its fit/calibration populations must be prospectively frozen through `research training-protocol` before native label runs. `research train-controller` requires raw-audited actual completed development data, retains all four paired correctness classes, and refuses overlapping table groups. Preserve its label-source studies and training receipt with all deployments.

Use disjoint task directories assigned by root and one writer per file. Root owns production code. Dataset split streams and namespaces, source hashes and separate modules guard accidental mixing; same Unix identity means this is workflow separation, not malicious-writer isolation. No external human participation or hardware sensor reading is implied. No measured energy estimate is available without a sensor; wall time, CPU counters, RSS and bytes are the measured quantities.

Whenever the platform blocks useful work, send root: exact reproduction commands; expected versus actual behavior; missing capability; scientific or user impact; and the smallest acceptance check. Preserve the failure. Root will fix the capability, run relevant checks, identify a revised archive, and send back a bounded repeat/extension instruction if appropriate.

## Required result package

Each distinct finding needs a plain claim and classification, question/prior art, exact specifications and producer versions, raw and all-attempt inventory, provenance/rights, independent checks, figures/tables generated from retained data, uncertainty/limitations, complete cost attribution, rerun instructions and a polished cited manuscript draft. A strong negative or inconclusive study may qualify; its coverage and implications must justify the finding. Do not count routine tests, screenshots or the same experiment split across documents. Mark unsupported gates incomplete.

Each investigator operates `inspect`, `report` and `workbench` on their actual studies and retains those outputs. Export with `tools/export_study.py`; the root coordinates final distribution and browser review. A distinct skeptical/reproduction leaf will be assigned after results exist. Process separation is not external human or institutional validation.
