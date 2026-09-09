# Recipe, serving replay and workbench runbook

Current correction: the 0.5B profile `qwen2.5-0.5b-instruct-fp16-v2` preserves the same pinned weights and corrects the artifact byte count. The older `v1` declaration remains available only to interpret earlier frozen recipes; use `v2` for new native work. See [the size correction](decisions/0.5b-profile-size-correction.md).

This is the local 0.4 development workflow. It does not declare a public release, external reproduction or a successful efficiency result. The original 0.1 recipe and observations remain separately documented in [RUNBOOK.md](RUNBOOK.md) and [the original finding](results/cpu-20260908.md).

## Workspace and admission

Use Python 3.12+ on the reviewed Linux x86_64 environment. Unpack the source bundle and run inference commands from the source root containing `WORKSPACE.json`. Acquisition, run and resume share one project heavy-job lease and count the entire workspace against the disk allocation. Nested working directories and inference artifacts outside that workspace are refused. Read-only reporting and the standalone HTML can be used elsewhere.

Approval is an operator decision; CLI flags record it and cannot grant it. Obtain the exact approved model/backend graph and local RAM, disk, compute-thread and full-wall limits before acquisition. Record one allocation only after approval. The following is the form of the command, not a new allocation for this retained study:

```sh
PYTHONPATH=src python3 -m lean_model_lab allocation create \
  --hours 12 --disk-gb 200 --memory-gb 60 --threads 12 \
  --approval-reference 'Exact operator decision and scope reference' \
  --approve --output .cache/operator-allocation.json
```

Never rerun allocation creation to extend existing work. Restarts, downloads, compilation, development, review, idle time, inference, recovery and export consume the original deadline. Keep partial files and failed phases. A process guardian keeps the preparation lease while its owned commands are stopping, including coordinator death.

List the reviewed profiles without downloading or loading a model:

```sh
PYTHONPATH=src python3 -m lean_model_lab profiles
```

The larger profile consists of eight FP16 GGUF shards, each bound by exact size and SHA-256. Its first shard is the entrypoint. Acquisition is explicit and sequential under the one-heavy-job lease:

```sh
python3 tools/prepare_profile.py \
  --allocation .cache/operator-allocation.json \
  --profile qwen2.5-14b-instruct-fp16-v1 \
  --output .cache/prepared-profile
```

The tool retains exact source, shard verification, build options, logs, phases and the setup receipt. It does not install global packages or execute inference. Backend and model files are separately obtained dependencies, not included in the project archive.

## Freeze a recipe before execution

Create the workload, engine and evaluation contract together. This example is a simultaneous finite batch with four balanced pairs per concurrency; it is not an online-service load test:

```sh
PYTHONPATH=src python3 -m lean_model_lab recipe create \
  --allocation .cache/operator-allocation.json \
  --model-profile qwen2.5-14b-instruct-fp16-v1 \
  --requests 128 --seed 20260908 --max-output-tokens 32 \
  --concurrency 1 4 --pairs 4 --threads 12 --purpose MEASUREMENT \
  --output .cache/measurement-recipe.json
PYTHONPATH=src python3 -m lean_model_lab recipe validate .cache/measurement-recipe.json
```

Choose `DEVELOPMENT` for smaller feasibility populations. Eight requests and two pairs can establish native compatibility but are always ineligible as a measurement claim. The supported population is 4–1024 in multiples of four, output ceilings 32–128, concurrency modes 1–8, and an even 2–8 pairs. These are software bounds, not permission to use all combinations.

For paced arrivals, add `--arrival paced --interval-ms N`. For bursts, use `--arrival burst --interval-ms N --burst-size K`. Freeze `--queue-capacity Q`, optional `--admission-deadline-ms D`, and `--ttft-slo-ms T --end-to-end-slo-ms E` before running. An experiment must explain why its chosen load and latency requirements matter; the software supplies no universal latency target.

The waiting queue capacity excludes active requests. Overflow rejects the new arrival; it does not delete it. A deadline runs from offered arrival and may expire a request before dispatch; it never cancels an already executing request. Each request stays assigned to its deterministic lane. Scheduler observations, native dispatch and token receipt times remain separate.

## Run the exact archive and retain predecessors

Build and verify the standalone implementation before a study. Keep the exact archive because resume refuses implementation drift:

```sh
python3 tools/verify_archive.py --output .cache/verified-package
python3 -I .cache/verified-package/lean-model-lab.pyz run \
  --recipe .cache/measurement-recipe.json \
  --server .cache/prepared-profile/build/bin/llama-server \
  --model .cache/prepared-profile/qwen2.5-14b-instruct-fp16-00001-of-00008.gguf \
  --setup .cache/prepared-profile/setup.json \
  --output .cache/measurement-study
```

Run admission automatically discovers locally retained producer studies from the same exact allocation and carries their setup and attempts forward once, with original identities and outcomes. `--predecessor PATH` can also name provenance explicitly; it cannot narrow the discovered set. An unfinished or damaged matching producer blocks a new study until reconciliation or restoration. Identical original copies deduplicate by their validated event history; redacted derivatives cannot replace the original producer. Starting a new study of a previously measured recipe cannot replace the earlier outcome with a new eligible result. Development and distinct recipes remain separately identified and charged. This mechanism is local provenance, not external authentication or protected confirmation.

Only `cache_prompt` changes between baseline and candidate. Every reserved attempt verifies all shards, binary identity and pinned version, checks actual slot/context settings, then retains raw tokenization, SSE and scheduling evidence. Cancellation and deadline checks run during hashing. Signals or coordinator errors stop owned inference before executor shutdown; exceptions remain failed or interrupted observations.

## Inspect and recover

```sh
python3 -I .cache/verified-package/lean-model-lab.pyz inspect .cache/measurement-study
python3 -I .cache/verified-package/lean-model-lab.pyz recover-journal .cache/measurement-study
python3 -I .cache/verified-package/lean-model-lab.pyz reconcile .cache/measurement-study
python3 -I .cache/verified-package/lean-model-lab.pyz resume .cache/measurement-study \
  --recipe .cache/measurement-recipe.json \
  --server .cache/prepared-profile/build/bin/llama-server \
  --model .cache/prepared-profile/qwen2.5-14b-instruct-fp16-00001-of-00008.gguf
```

Use journal repair only when inspection reports a damaged index. Reconciliation retains observed checkpoints, unavailable intervals and missing requests. It refuses a still-live recorded backend. Resume uses the same boot, original allocation, frozen recipe and implementation; replacement cells receive new attempt IDs. A recovered study with adverse or repeated cells remains ineligible even if replacement requests succeed.

The intentional same-boot development recovery harness is `tools/verify_recipe_recovery.py`. It kills its own coordinator after checkpoints, verifies backend cleanup, damages and repairs only its new study's journal, reconciles, restarts the first cell and retains every extra attempt. Its receipt is recovery evidence, not a second performance comparison.

## Report and inspect request evidence

```sh
python3 -I .cache/verified-package/lean-model-lab.pyz report .cache/measurement-study \
  --output .cache/measurement-report.json --html .cache/measurement-report.html
python3 -I .cache/verified-package/lean-model-lab.pyz workbench \
  --study .cache/measurement-study --study .cache/another-study \
  --output .cache/workbench.json --html .cache/workbench.html
```

Open the HTML locally; it has no remote assets, telemetry, model loading or inference controls. The workbench validates immutable input inventories and raw evidence before rendering. Families with different model/tokenizer, workload or evaluation semantics remain separate. No speedup is pooled across studies or profiles. Request views expose outputs, token IDs, exact-answer checks, cache and timing evidence; cost views retain failed and prior work.

Every offered request remains in the quality denominator, including rejected, expired, failed, cancelled and missing work. A qualified request succeeds with an exact answer and observed first-token/end-to-end times within both frozen SLOs. Goodput divides qualified requests by the complete service envelope. Offered rate uses the declared last-minus-first arrival span; simultaneous batches have no offered rate. Descriptive serving counts never override failed global quality/parity gates.

Use `tools/audit_raw_study.py` for raw/native/normalized cache-token reconciliation and `tools/export_study.py` to prepare a disclosed model-path-redacted derivative. Originals stay unchanged. Export checks are scoped integrity/privacy controls; they do not approve publication, independently authenticate measurements or provide human validation.
