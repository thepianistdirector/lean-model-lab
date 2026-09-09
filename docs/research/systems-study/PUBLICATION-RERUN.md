# Reanalysis from the self-contained investigation package

Extract the systems investigation ZIP. Its root contains `lean-model-lab-source/`, `evidence/`, the relevant exact producer archives and study workbenches. Each retained study is under `evidence/systems-CASE_ID/study/`. Model weights and native backend binaries are separate licensed dependencies; they are not needed to reproduce the reported tables and figures.

The portable [evidence manifest](evidence-manifest.json) explicitly maps each completed case to its exported study, report, fresh export inspection, raw audit and original queue receipt. It contains no required `.cache` path. The [provenance catalog](provenance-catalog.json) supplies hashes for exact scientific specifications and documented operational metadata derivatives. The [redaction ledger](provenance-redactions.json) records original/derived hashes and replacement counts where historical workspace/interpreter paths become named portable tokens. Exact originals remain privately retained. The reanalysis resolves only explicit manifest paths under the supplied root; recipe, protocol, cost, token and timestamp fields remain unchanged.

Archived stdout, stderr and queue log files carry an additional `.txt` suffix so the source distribution includes them, with original filenames retained in the catalog. Their bytes remain unchanged except for explicitly logged operational path redactions. Neighboring command JSON records retain argument order, return codes and times, with named path tokens where required.

## Recompute without model execution

From the extracted investigation root, choose a **new** output directory:

```sh
python3 -I lean-model-lab-source/docs/research/systems-study/analyze.py \
  lean-model-lab-source/docs/research/systems-study/evidence-manifest.json \
  --evidence-root . \
  --output rerun-tables
```

The analysis uses Python's standard library. `--evidence-root` can be an absolute path to an independently relocated package, and `--output` can be any new directory. There is no need to edit Python code. If your exported studies have a different layout, copy the JSON manifest and change its explicit `study`, `report`, `inspect`, `raw_audit` and `queue_receipt` paths. Relative paths resolve beneath `--evidence-root`; absolute paths are also accepted for independently supplied artifacts.

The output files are `requests.csv`, `pairs.csv`, `tables.csv`, `attempts.csv`, `cases.csv` and `summary.json`. The analysis validates report/config/workload identity, inventory completeness and native input-token accounting, preserves all offered requests, and calculates descriptive outcomes from actual exported raw responses. Attempt rows separate native prompt/generation durations, the client dispatch-to-completion interval union and service time outside those intervals; that diagnostic decomposition does not identify the cause of each gap. Pairwise and tablewise either-answer-correct counts are observed two-output ceilings, not a deployable oracle. The original platform's eligibility decision remains authoritative.

The standalone population check verifies eight distinct queries per retained table, development/confirmation table separation and equality of matched model populations:

```sh
python3 -I lean-model-lab-source/docs/research/systems-study/check-populations.py \
  lean-model-lab-source/docs/research/systems-study/evidence-manifest.json \
  --evidence-root . \
  --output rerun-population-check.json
```

The checked [export reanalysis record](export-reanalysis-check.json) compares these outputs with reanalysis of the original retained studies. Operational response metadata such as model filesystem paths may be redacted, while scientific payloads and token/timing outcomes remain unchanged. Export verification and raw-response auditing are separate from quality eligibility: a faithfully reproduced negative result remains negative.

To render PNG, SVG and PDF figures, use a Python environment with Matplotlib and direct its writable cache and temporary files to local directories:

```sh
mkdir -p rerun-mplconfig rerun-tmp
MPLCONFIGDIR="$PWD/rerun-mplconfig" TMPDIR="$PWD/rerun-tmp" \
python3 -I lean-model-lab-source/docs/research/systems-study/plot.py \
  --tables rerun-tables \
  --output rerun-figures
```

Matplotlib version and renderer differences can affect binary image bytes. Compare the numerical tables, labels, units, order, gates and plotted values; do not mistake PDF creation metadata for a scientific discrepancy. The original reviewed binary assets have an explicit final figure manifest when packaged.

The [final figure catalog](figure-assets.json) binds the reviewed binary assets to their source and analysis. All 14 actual PDF pages were also rendered with the already installed PDFium dependency and visually inspected; the [PDF review record](pdf-visual-review.json) retains exact PDF, rendered-preview, helper and native renderer hashes. The original 28 PNG/PDF figure bytes were unchanged by that check. QA previews remain privately retained; the reviewed source PDFs and PNGs are the distributed artifacts.

## Independently recheck an exported producer

Use the exact archive associated with the case in its retained queue receipt and command records. D1 uses SHA-256 `f90c48dd0be36b29c3188c365ba6b8ab2cbe709897cd7f4cce0e4825a147db6f`; D2 and the frozen held-out cases use `5f1aabf84635e33dd166ee656d5bcb5830f25a5f4f5d68433e2fd3e4498fb986`. The distribution names these files `producer-<SHA>.pyz`.

For D1, run the exact archive supplied at the extracted investigation root and retain new recheck outputs:

```sh
python3 -I producer-f90c48dd0be36b29c3188c365ba6b8ab2cbe709897cd7f4cce0e4825a147db6f.pyz inspect \
  evidence/systems-d1-small-reuse24/study > rerun-inspect-d1.json
python3 -I lean-model-lab-source/tools/audit_raw_study.py \
  evidence/systems-d1-small-reuse24/study \
  --output rerun-raw-audit-d1.json
```

The packaged provenance already contains successful fresh checks performed on the exported derivatives. An independent reviewer can replace the manifest's inspection/audit paths with their newly generated records and repeat the analysis. Preserve both the original and new verification records.

## Native reproduction is a new resource-bound campaign

An actual model rerun additionally needs the separately licensed model shards, the exact backend source revision/local patch and an admitted build, plus a valid allocation for the host and time window where it runs. The original allocation deadline is historical; do not silently reset it or append to an old completed study. The [rerun guide](reproduce.md), per-case `provenance/CASE_ID/recipe.json`, `protocol.json`, `proposal.json`, `queue-command.json` and `*.command.json` files retain the exact original task population, runtime parameters and invocation history. The global [held-out freeze](provenance/heldout-matrix-freeze.json) binds all three negative-challenge cells before their execution.

The source tree includes `patches/llama-cpp-v0.2.0-gcc8-ctad.patch`, whose SHA-256 is `598d10a911e4d9c33926bd2dfd75735d143b84db14ad644a7502f35bec8e0f1c`, matching the retained backend configurations. Model repositories, revisions and every shard hash are in each exported `study/config.json`; the source includes `tools/prepare_profile.py` and the profile registry for acquisition/build procedures. Model weights and compiled servers remain separate from this package.

Use a new output directory and record a separately declared reproduction allocation. Preserve the scientific population, seeds, original grammar, both-cached comparator, quality gates, first-use requests and balanced pair design; disclose operational differences such as hardware, threads, build or allocation. Run the packaged `research study-create` and `recipe validate` workflow with the admitted reproduction allocation and retained scientific specifications, then use the source tree's serialized `tools/run_queued_recipe.py` helper. A new native campaign is not expected to reproduce monotonic timestamps or machine-specific timings byte for byte.

The archived `provenance/original-run-scripts/` files document original authoring and finalization, including their historical workspace paths. They are not required by portable reanalysis and should not be blindly executed to overwrite old studies. `prepare-portable.py` is a publication-preparation utility for an owner who has the original workspace, rather than a dependency of a reader's reanalysis.

All generated record tasks and project code retain the project's AGPL-3.0-only terms. Official Qwen checkpoints declare Apache-2.0 and the pinned llama.cpp backend is MIT with the retained patch. No model weights, new model acquisition, extra spending, external publication or energy measurement is implied by these instructions.
