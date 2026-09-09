# Local workflow and current gates

The current candidate is tested with Python 3.12 on Linux x86_64. The real admitted Qwen/llama.cpp comparison and packaged same-boot recovery were executed locally on 8 September 2026. [Quality and concurrency-4 parity failed](results/cpu-20260908.md), so no efficiency gain is eligible. No public 0.1 exists yet.

## Model-free checks now

From the repository root:

```sh
mkdir -p .cache/tmp
PYTHONPATH=src TMPDIR=.cache/tmp python3 -m unittest discover -s tests
python3 tools/validate_plan.py
python3 tools/validate_plan.py --self-test
python3 tools/verify_archive.py --output .cache/package-review-new
PYTHONPATH=src python3 -m lean_model_lab trace validate workloads/synthetic-key-copy-v1.json
```

Tests exercise the real coordinator/HTTP/process/recovery plumbing against an explicitly synthetic local test server. They establish no model quality, latency or throughput result.

The archive check uses a fresh output directory and Python isolated mode. It
checks deterministic packaging, manifest and implementation identity, trace
and evaluator commands, no-clobber behavior, complete inventory reporting,
damaged-journal rejection and recovery. Its fixture report remains ineligible
for measured claims. See [the release gate assessment](review/release-gates.md).

## Exact acquisition and study after approval

Read `docs/decisions/backend-audit.md` and `docs/benchmarks/first-workload.md`. `docs/decisions/admission-proposal.json` remains the historical pending template. The completed local run used the separate `docs/decisions/admission-approved-20260908.json`. For a new run, obtain the exact local operator allocation and save its own admission record with `approved: true` and the actual approval reference; preserve the reviewed identity/limit fields. The completed owner allocation is not reusable authority for unlimited new runs. This record is operator authorization metadata, not a signature or a sandbox.

```sh
python3 tools/prepare_backend.py --admission .cache/admission.json --output .cache/prepared-01
PYTHONPATH=src python3 -m lean_model_lab run \
  --server .cache/prepared-01/build/bin/llama-server \
  --model .cache/prepared-01/qwen2.5-0.5b-instruct-fp16.gguf \
  --setup .cache/prepared-01/setup.json --admission .cache/admission.json \
  --output runs/study-01
PYTHONPATH=src python3 -m lean_model_lab inspect runs/study-01
PYTHONPATH=src python3 -m lean_model_lab report runs/study-01 \
  --output .cache/study-01-report.json --html .cache/study-01-report.html
```

The real path was exercised with retained GCC 8 build recoveries and a corrected native stream adapter. Preparation now includes the hash-checked compatibility patch and existing GCC 8 filesystem link flag; see `decisions/gcc8-build-recovery.md`. Preparation verifies the pinned source commit and model SHA-256, builds only the reviewed CPU target, and retains setup failures and costs. It installs nothing machine-wide. The two-hour allocation starts with acquisition, includes build and intervening wall time, and never expands automatically. Always operate from the same project root so setup and studies share its one-heavy-job lease. The compiled native binary is device-specific; reproduce by building the same source on another admitted Linux x86_64 host.

The tool verifies model/server bytes before execution, uses four or one slots within two compute threads, binds loopback only, retains raw SSE and overhead, and enforces a bounded budget. Process/RSS polling can overshoot between observations; process limits are not an untrusted-code sandbox. No cloud/GPU or upstream inference is used. Do not provide another backend, arbitrary model code or a remote endpoint.

## Interrupt, inspect, reconcile and resume

Ctrl-C requests durable interruption, closes the owned process group and retains completed/partial observations. Inspect the study before taking another action:

```sh
PYTHONPATH=src python3 -m lean_model_lab inspect runs/study-01
PYTHONPATH=src python3 -m lean_model_lab recover-journal runs/study-01
PYTHONPATH=src python3 -m lean_model_lab reconcile runs/study-01
PYTHONPATH=src python3 -m lean_model_lab resume runs/study-01 \
  --server .cache/prepared-01/build/bin/llama-server \
  --model .cache/prepared-01/qwen2.5-0.5b-instruct-fp16.gguf \
  --admission .cache/admission.json
```

Journal repair archives its old bytes and rebuilds only from immutable events. Reconciliation closes same-boot orphan attempts with retained checkpoints; the unobserved interval remains unattributed wall time, not invented engine work. It refuses a still-running recorded process or an incompatible boot. Resume requires the original implementation, artifacts, boot and remaining allocation; restarted cells get new attempt IDs. Earlier failed/interrupted attempts remain and make this fixed-design campaign ineligible for a positive efficiency claim. No best retry is silently selected.

Cross-boot inference resumption is unsupported in this candidate; preserve the original evidence for explicit reconciliation review. Static reports and completed raw evidence remain inspectable. Report export does not append the renderer's clock to the producer's study; a separate `.receipt.json` records rendering costs in its own environment.

Never delete old attempts to obtain eligibility. Do not restart an expired allocation, swap weights, change quality thresholds or reuse an output directory. Files are immutable and existing output paths are refused. For invalid or partial evidence, use `inspect`; an unreconciled inventory cannot generate a completed-study report.

## Release and evidence boundaries

The standalone zipapp can be built with `python3 tools/build_archive.py --output .cache/lean-model-lab.pyz`. The archive is local and development-labeled. Public packaging must include lawful retrieval instructions, source/dependency notices, fixed trace, invalid controls, sanitized real raw/rendered results and checksums; preserve the original raw provenance when sanitizing operational logs. Never distribute developer paths, credentials or unapproved weights/binaries.

Actual first-run/recovery passed locally within the original allocation, with the adverse history preserved. Accessible visual/browser checks, qualified/human evidence, public-artifact external reproduction, GitHub publication and native Tanduna publication remain gates. The current native export is preparation material only. See `docs/decisions/publication-workflow.md`.

## Inspect the measured review bundle without inference

After extracting `lean-model-lab-evidence.zip` beside `lean-model-lab.pyz` (the distribution archive has exactly the same Python runtime as the included `measured-producer.pyz`):

```sh
python3 -I lean-model-lab.pyz inspect evidence/comparison/study
python3 -I lean-model-lab.pyz report evidence/comparison/study \
  --output regenerated-comparison.json --html regenerated-comparison.html
```

Use a new output path. The result must stay INELIGIBLE and match the included report JSON. `evidence/*/study/EXPORT-PROVENANCE.json` describes path-only metadata redactions and original hashes. Original-provenance catalogs are provenance, not a second executable study. The protocol-failure and recovery-control studies must remain visibly incomplete/ineligible. No model or server is needed for static inspection/report generation.
