# Reproducing the systems study

The retained producer inputs are the authority. The analysis can be recomputed without model execution; an actual rerun needs the separately acquired model/backend, a valid allocation, and the serialized native queue. The recorded allocation is finite and cannot be renewed by editing the recipe. A later independent campaign must create a new allocation and preserve its relationship to this one.

For the distributed self-contained investigation ZIP, use [PUBLICATION-RERUN.md](PUBLICATION-RERUN.md) and the [portable evidence manifest](evidence-manifest.json). The commands below also document the original private workspace layout and exact historical invocations.

## Recompute the reported tables and figures

Run from the `lean-model-lab` workspace root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/research/systems-study/analyze.py \
  .cache/v1-investigations-20260908/systems/analysis-manifest.json \
  --output docs/research/systems-study/tables
MPLCONFIGDIR=.cache/v1-investigations-20260908/systems/mplconfig \
TMPDIR=.cache/v1-investigations-20260908/systems/tmp \
PYTHONDONTWRITEBYTECODE=1 .cache/research-plot-env/bin/python \
  docs/research/systems-study/plot.py \
  --tables docs/research/systems-study/tables \
  --output docs/research/systems-study/figures
```

The analysis uses only Python's standard library; plotting uses the existing Matplotlib environment. The manifest records the workspace root and case directories. If relocating an intact producer package, change only that manifest's workspace root. The analysis binds report/config/workload identities, requires a complete attempt inventory, reconciles successful native new-plus-reused input tokens with the actual tokenized inputs, and retains all offered requests. It does not manufacture failed outputs or rerun a model. Tables expose exact outputs and token sequences, quality classes, request timings, full-attempt phases and native cache counters.

Each final report is the product's decision. The descriptive analysis never promotes an ineligible development case to an efficiency claim. Shared setup intervals are deduplicated across cases, and original-allocation spans are not summed. The source commands and plotting environment should be included in any later independent reproduction record.

## Verify the original D1 producer

D1 is retained at `.cache/v1-investigations-20260908/systems/d1-small-reuse24/`. Its `*.command.json` files contain exact argument vectors, monotonic start/end times, exit status and the producer archive digest. Matching stdout and stderr files preserve the original executions. The archive is:

```text
.cache/packaged-v1-platform-20260908-03/lean-model-lab.pyz
SHA-256 f90c48dd0be36b29c3188c365ba6b8ab2cbe709897cd7f4cce0e4825a147db6f
Implementation fe572bc610c0bc395672bf8b4e8f681260e2e6bdccf4280d6a7ec0784c30d5fe
```

Use that exact archive for the original case's inspection. Do not substitute the newest archive and call it the original producer. A later version is a new producer even when it preserves the old generator semantics.

```sh
python3 -I .cache/packaged-v1-platform-20260908-03/lean-model-lab.pyz \
  inspect .cache/v1-investigations-20260908/systems/d1-small-reuse24/study
python3 tools/audit_raw_study.py \
  .cache/v1-investigations-20260908/systems/d1-small-reuse24/study \
  --output .cache/v1-investigations-20260908/systems/d1-small-reuse24/raw-audit-recheck.json
```

The original `report.command.json`, `workbench.command.json` and `export.command.json` retain the other exact verification commands. Their already-produced outputs are `result.json`, `report.html`, `workbench.json`, `workbench.html`, `raw-audit.json` and the local `export/`. Avoid overwriting the historical command receipts with a recheck. The export is a verified local derivative with operational path redactions; the original raw producer and provenance remain retained. No public release is implied.

## Actual native repetition

The original workflow was `research propose`, `research protocol`, protocol authoring, `research freeze`, `research verify`, `research study-create`, `recipe validate`, then the queue helper. All exact commands and inputs are retained beside the case. The frozen recipe uses eight requests, two AB/BA pairs, `record-reuse`, 24 records, development seed `940101`, concurrency one and two threads. Its full-cache and slice-cache arms each start their own real cold cache.

For a prospectively authorized independent rerun, retain the existing case unchanged and choose a fresh output directory. The original native invocation was:

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=.cache/tmp python3 tools/run_queued_recipe.py \
  --archive .cache/packaged-v1-platform-20260908-03/lean-model-lab.pyz \
  --recipe .cache/v1-investigations-20260908/systems/d1-small-reuse24/recipe.json \
  --server .cache/prepared-20260908-01/build/bin/llama-server \
  --model .cache/prepared-20260908-01/qwen2.5-0.5b-instruct-fp16.gguf \
  --setup .cache/adopted-0.5b-current-02/setup.json \
  --output .cache/v1-investigations-20260908/systems/d1-small-reuse24/study
```

This command is a historical record, not a request to append to or replace that completed study. A rerun must use its own output path and the allocation that actually governs it. Preserve every failed or interrupted attempt and every first query of a table. A useful independent check should verify the reported cache counters and correctness against raw native responses, rather than merely checking the plotted numbers.

## Rights and exact dependencies

The generated record tasks and project code are original project materials under AGPL-3.0-only. The official checkpoint is `Qwen/Qwen2.5-0.5B-Instruct-GGUF`, revision `9217f5db79a29953eb74d5343926648285ec7e67`, declared Apache-2.0. The exact FP16 GGUF is 1,266,425,696 bytes and has SHA-256 `8e0ae26000627ed62de0e78e41860af70094558b9d2913385c842a6aa06cf3fc`. Profile `qwen2.5-0.5b-instruct-fp16-v2` has digest `13e85926dcbbf56e3004f3c72b8375d1b921355c15579ee92bb8bf141a5396e4`; template digest is `5e72fa95f7f6782b2363d5a3e2f93e181098b914d2994180b050ad8fc67196f7`.

The MIT backend is `ggml-org/llama.cpp`, revision `bb4caa7540188872173c44d161602d9271386413`, with retained local patch SHA-256 `598d10a911e4d9c33926bd2dfd75735d143b84db14ad644a7502f35bec8e0f1c`. The actual server digest is `22bb24feddd1b44d0b793d044fd86dad4119b40d5485e58d9a6213d296cf71b2`. Preparation receipts retain acquisition/build commands and logs. Model weights and backend binaries are separate dependencies and are not included in the study export.

No human subjects, external institutional review, measured energy sensor, or external independent reproduction is represented by these artifacts. A separate skeptical reproduction remains outstanding until a distinct investigator actually performs and retains it.

## D2 producer differences

The matched 14B development alternative is retained at `.cache/v1-investigations-20260908/systems/d2-large-reuse24/`, with the same command-receipt structure. Its archive is `.cache/packaged-v1-platform-20260908-04/lean-model-lab.pyz`, SHA-256 `5f1aabf84635e33dd166ee656d5bcb5830f25a5f4f5d68433e2fd3e4498fb986`, implementation `18c28e8075ebc9e5651bf4e0a66c2fca332480b4834a7342fc49d43775a9ab32`. The retained `matched-population-check.json` compares every generated request record against D1; all are identical. The original grammar has not been replaced with the separately versioned explicit-language grammar.

D2 uses six threads instead of two, and its separately built server has digest `e6e4555daed18ae36a87276f16bd4c9f859c92787884b726b7967474d8c4681e`, at the same pinned source revision and local patch as D1. Therefore the model-scale comparison is a bounded transfer between these admitted configurations, not a controlled claim that every timing difference is caused solely by parameter count.

The model is the official `Qwen/Qwen2.5-14B-Instruct-GGUF` checkpoint, revision `b466e1f8c07172155743e8e1307507d8a4f91fbd`, declared Apache-2.0. Its profile `qwen2.5-14b-instruct-fp16-v1` has digest `f248b9b5b491f829653205e6a1878a81e217f3830a53198cbc2810ed61623caf`. The first of eight FP16 shards has digest `18ccd380458642716373134dd9aeb194bf11b97085c5ce78aaec768f0f2a51aa`; all eight exact filenames, sizes and hashes are preserved in `study/config.json`, and each attempt's model-verification receipt checks the actual files. Its template digest matches D1. The queue uses `.cache/prepared-14b-20260908-01/build/bin/llama-server`, `.cache/prepared-14b-20260908-01/qwen2.5-14b-instruct-fp16-00001-of-00008.gguf` and `.cache/prepared-14b-20260908-01/setup.json`. Weights and server binaries remain external to the local study export.

## Frozen held-out negative challenge

The [matrix freeze](provenance/heldout-matrix-freeze.json) binds all three recipes and protocols before the first held-out native request. Every case uses the original `record-reuse` grammar, confirmation split, 128 distinct queries over 16 tables, two balanced pairs, concurrency one, and `slice-versus-full-cache-v1` with identical caching enabled for both arms.

| Case | Model profile | Record count | Frozen seed | Threads |
|---|---|---:|---:|---:|
| H1: `h1-small-reuse24` | 0.5B FP16 v2 | 24 | 940129 | 2 |
| H2: `h2-small-reuse64` | 0.5B FP16 v2 | 64 | 940193 | 2 |
| H3: `h3-large-reuse24` | 14B FP16 v1 | 24 | 940129 | 6 |

All three use exact archive 04 and the dependencies documented above. H1 and H3 have identical request records; H2 has a separately seeded population. The per-case portable provenance retains original proposals, protocols, recipes, budget admissions, native queue commands or labeled documentary transcriptions, queue registration/receipt, and the original finalization commands. The [population check](population-check.json) verifies table separation and matched-population equality from retained workload bytes.

Preserve the generator's split-dependent namespaces when interpreting or reproducing these cases: D1/D2 keys and values have a `D` prefix, whereas H1/H2/H3 keys and values have a `C` prefix; each prefix is followed by four generated uppercase letters. In the exact producer modules, the pseudorandom stream is seeded from the SHA-256 digest of canonical fields `generator_version: 3`, `seed`, `family` and `split`. Archive 04 first resolves separately named explicit families to their source family; every systems case uses original `record-reuse`, so that mapping leaves its family unchanged. The [namespace verification record](generator-namespace-check.json) binds both exact producer modules and all five retained workloads to this check. The held-out groups are fresh generated populations, but namespace separation and split-derived streams do not establish IID sampling or exchangeability with development, and this study does not test lexical invariance. Cross-split comparisons include that distribution difference; H1/H3 retain identical confirmation inputs.

This is the predeclared negative challenge following failed development quality, with at most 1,600 newly offered native requests including D1 and D2. It does not relax the quality gate or authorize a new search. Every cell had to pass a prospective runtime check with a 1.5 safety factor against the remaining 90-minute investigator execution ceiling and the same original allocation deadline. Queue waiting and product execution are retained separately. No later reader archive changes the original producer identity.

An unintended duplicate H1 finalization performed only a read-only inspection before the report overwrite guard stopped it. The [metadata incident record](duplicate-finalization-metadata-incident.json) preserves the duplicate hashes and proves restoration of the earlier command/output bytes against already retained original provenance. The scientific report, raw responses and export were unchanged; no native run was repeated.
