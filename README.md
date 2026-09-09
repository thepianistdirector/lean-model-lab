# Lean Model Lab

Discover and test new mechanisms for substantially better LLM training and inference. Lean Model Lab combines a reusable catalog of existing techniques with a research workflow for ambitious hypotheses, decisive experiments, complete costs and reproducible findings. Its objectives include both efficiency at a declared quality level and higher quality at a fixed resource budget.

The [research mission](docs/RESEARCH-MISSION.md) defines Astra's role in proposing and challenging new mechanisms. Known optimizations supply tools and strong baselines; novelty and large gains require evidence. The current cache comparison validates the measurement infrastructure and is not presented as a discovery.

**Local review candidate: application `1.0.0`, proposed prerelease `v1.0.0-rc.1`; no public v1 release.** The [v1.0 contract](docs/V1-CONTRACT.md) requires a complete proposal-to-experiment workflow, three substantive research packages and separate reproduction. The first actual packaged native workflow, deliberate crash/recovery and verified export are complete. All three finite native research matrices are complete, including adverse confirmation evidence. The small acceptance controller has an actual training/deployment trace and selects full context on every confirmation request; it produces no learned efficiency advance. Three actual research ZIPs pass inventory/hash/link checks. The exact CLI and source ZIP complete native first use and supported recovery in a fresh Python environment on this host; a separate agent completed three retained-cell repetitions totaling 1,536 new observations, with discrepancies and timing variation recorded in the [review](docs/research/reproduction-review/report.md). Final distribution checks bind the tested code, original scientific artifacts and reviewed offline pages to the proposed delivery. Underlying LLM training remains unsupported. See the [proposal-to-experiment runbook](docs/RUNBOOK-V1.md) and [STATUS.md](STATUS.md) for observed gates.

The retained 0.1 CPU comparison completed all 1,536 requests. Every arm scored 99/128 (77.34375%), below the frozen 95% gate; concurrency-4 token parity also failed. **No eligible efficiency gain is claimed from that study.** Its [finding and full costs](docs/results/cpu-20260908.md) remain unchanged. Human validation, external reproduction and public publication remain pending. [STATUS.md](STATUS.md) records the evidence gates.

## Start with v1

Use the [first-run guide](docs/FIRST-RUN-V1.md) to inspect the prepared evidence offline or complete a native experiment on supported resources. The complete review ZIP opens at `lean-model-lab-1.0.0/index.html`; its three research packages include the manuscripts, exact experimental producers, raw evidence and portable analysis. Native execution also requires the separately acquired pinned model and backend.

Read the [three findings](docs/release/FINDINGS-OVERVIEW.md), [release notes](docs/release/V1-RELEASE-NOTES.md) and [actual product screenshots](docs/release/screenshots/README.md). Public download, external-person first use and qualified review have their own evidence gates in the [publication packet](docs/release/PUBLICATION-PACKET.md).

## Validate or build from source

Tested with Python 3.12.14 on Linux x86_64. The control package uses only the Python standard library.

```sh
PYTHONPATH=src python3 -m lean_model_lab trace validate workloads/synthetic-key-copy-v1.json
PYTHONPATH=src python3 -m lean_model_lab trace create --output .cache/my-trace.json
mkdir -p .cache/tmp
PYTHONPATH=src TMPDIR=.cache/tmp python3 -m unittest discover -s tests -v
```

The trace contains 128 synthetic key-copy requests, four filler-word strata, at most 32 requested output tokens, and concurrency modes 1 and 4. Expected answers and the 95% exact-answer quality gate are fixed before any model runs. Validation rejects changed prompts, answers, quality thresholds, arrivals and sampling rules. This command does not run inference.

Build a standalone local archive without installing a package:

```sh
python3 tools/build_archive.py --output .cache/lean-model-lab.pyz
python3 -I .cache/lean-model-lab.pyz trace validate workloads/synthetic-key-copy-v1.json
```

Output files are immutable: choose a fresh output path for another build or trace. The archive is a development artifact, not a published release or a backend/model bundle.

The complete admitted workflow, interruption and restart commands are in [the runbook](docs/RUNBOOK.md). The packaged real-model run and same-boot interruption/restart were verified locally; external reproduction is still pending.

Prepared v1 distributions use [the external first-run guide](docs/FIRST-RUN-V1.md) and [compatibility/troubleshooting](docs/COMPATIBILITY-AND-TROUBLESHOOTING.md). Those guides distinguish offline evidence inspection, local isolated verification and actual external-person reproduction.

## Inspect evidence

The [early standalone report](docs/review/model-free-preview.html) is explicitly fabricated evaluator test data. It illustrates complete attempt accounting and can be opened without remote scripts or assets. It is **not** a scientific result. The new workbench has a separate browser-validation workflow; a successful browser launch alone is not proof of a reviewed page.

For a directory containing raw attempt JSON and frozen sidecars:

```sh
PYTHONPATH=src python3 -m lean_model_lab evaluate \
  --workload path/to/workload.json --config path/to/config.json \
  --attempts path/to/attempts --output .cache/result.json --html .cache/report.html
```

The evaluator retains adverse attempts, quality failures, missing request counts, generated-versus-visible token counts, paired output parity, all three pair ratios, client latency and unstable tails. Test fixtures cannot become measured claims. A complete release bundle must also reconcile its attempt inventory and setup/acquisition ledger; digest consistency alone cannot authenticate external evidence.

## Historical first scope: 0.1

An external researcher will obtain the public tool and an exact lawful model recipe, verify identities, run one CPU baseline versus a same-slot prefix-cache policy, evaluate quality and full costs, inspect raw evidence, and recover/reproduce the study. The [frozen workload proposal](docs/benchmarks/first-workload.md) and [backend review](docs/decisions/backend-audit.md) specify the narrow cut. A legitimate no-gain or regression finding is useful; simulated timings or missing inference cannot satisfy this release.

The admitted model is official Qwen2.5-0.5B FP16 with pinned llama.cpp CPU source and a recorded GCC 8 compatibility patch. The [owner decision](docs/decisions/admission-approved-20260908.json) covered the bounded local run; another allocation requires its own admission. No automatic model downloads, remote model code, GPU/cloud spend or general dashboard belong to this increment.

## Programme and contribution

Read the [249 contributor tasks](TASKS.md), [roadmap](ROADMAP.md), [architecture](ARCHITECTURE.md), [experiment contract](EXPERIMENTS.md), [sources](SOURCES.md) and [contribution guide](CONTRIBUTING.md). The new plan maps all 27 original source records without deleting their acceptance history or dependency graph. The three foundation completions establish accepted documentation/tooling; they do not establish runtime completion.

`plan/tasks.json` is the canonical task/evidence ledger; generated views and the Tanduna export are projections. [STATUS.md](STATUS.md) summarizes actual evidence and remaining gates. Run `python3 tools/validate_plan.py` for graph, lineage and projection checks.

Public Tanduna [roadmap](https://tanduna.com/projects/lean-model-lab/roadmap) and [tasks](https://tanduna.com/p/lean-model-lab/tasks) are separate publication requirements. At the latest public audit, neither native task collection nor roadmap was published. A local export is not publication.

## Boundaries and license

No gain from dropped requests, shortened outputs, changed tokenizers, relaxed thresholds or hidden startup/evaluation/retry costs. No general language competence from synthetic key copying; no online-service claim from a finite queued batch. Missing energy/engine telemetry is UNAVAILABLE. Results stay device-specific and negative results remain visible.

Original source, documentation and synthetic fixtures are **AGPL-3.0-only**; see [LICENSE](LICENSE). See [source and dependency notices](THIRD_PARTY_NOTICES.md) for fixture provenance and separately obtained dependencies. Third-party code, models, tokenizers and data retain their own licenses. No third-party weights or backend binary is redistributed in this development artifact.
