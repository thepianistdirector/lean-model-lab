# Reproduce the candidate study from its complete package

The complete investigation ZIP contains the source tree, eight actual study exports, original producer archives, frozen protocols, native training artifacts, complete population tables and standalone figures. The commands below need no developer cache paths, model weights, edits to code constants, or native inference. Run them from the extraction root, using Python 3.12, which was used for the retained portable checks.

## Layout and data identities

```text
lean-model-lab-source/
  docs/research/plotting-requirements.txt
  docs/research/candidate-study/
    manuscript.md
    figures/...
    publication/
      evidence-manifest-final.json
      scripts/reanalyze.py
      scripts/validate_training.py
      scripts/illustrations.py
      scripts/plot.py
      artifacts/protocols/...
      artifacts/training/...
      artifacts/<study-id>/queue-receipt.json
      tables/final/...
evidence/<study-id>/
  study/...
  report.json
  report.html
  EXPORT-READY.json
producer-<original-archive-SHA256>.pyz
```

The stable `publication/evidence-manifest-final.json` maps logical IDs to all eight actual exported studies. The original logical/native study `clarification-0.5b-study04` is packaged under the safe directory/CLI alias `clarification-05b-study04`; its evidence paths are `evidence/clarification-05b-study04/study` and `evidence/clarification-05b-study04/report.json`. This directory alias satisfies the builder name boundary without changing original native identities or file contents. The manifest records that explicit mapping. It binds exported configuration, workload, report and queue-receipt hashes; original producers; the native controller and all five training files; and the prospectively frozen illustration rule. Paths resolve under the explicit `--evidence-root`. The preserved export provenance distinguishes original producer hashes from metadata-redacted derivative hashes.

## Recompute every offered outcome

Choose a new output directory for each invocation:

```bash
python3 lean-model-lab-source/docs/research/candidate-study/publication/scripts/reanalyze.py \
  --manifest lean-model-lab-source/docs/research/candidate-study/publication/evidence-manifest-final.json \
  --evidence-root . \
  --output reanalysis-final-01
```

This standard-library analysis verifies exact producer bytes without executing them. It independently resolves original record tables, reconstructs dependency and gate prompts, requires the complete declared arm/pair and offered-request inventories, and reconciles quality, symbolic preservation, qualified-service counts and goodput with the actual exported product reports. Every retained offered question remains in the output tables, including jointly wrong, rejected or otherwise failed cases. A missing request record or incomplete declared matrix makes this complete-evidence check fail; it cannot silently be represented as a complete result.

The output separates per-pair observed-output oracle ceilings from the conservative rule requiring one arm to be correct in every repetition. It verifies identical confirmation populations, disjoint development/confirmation table-body groups, the matched control's exact record budgets, and equality between the actually deployed controller and its frozen native artifact. Symbolic preservation in the deliberately nonsemantic prefix control is measured separately from correctness.

## Validate the actual native training artifact

```bash
python3 lean-model-lab-source/docs/research/candidate-study/publication/scripts/validate_training.py \
  --manifest lean-model-lab-source/docs/research/candidate-study/publication/evidence-manifest-final.json \
  --evidence-root . \
  --output training-validation-01.json
```

This checks the original fit and calibration labels against exported native responses, independent graph features, group identities and exact cost sums. It reconciles the fitted node counts and every frozen calibration-grid row, including the selected `ALWAYS_FULL` refusal. It neither fits a replacement tree nor selects a new threshold. The parameter JSON alone is not the training provenance; all five original native files are included.

## Reproduce the selected illustrations

```bash
python3 lean-model-lab-source/docs/research/candidate-study/publication/scripts/illustrations.py \
  --manifest lean-model-lab-source/docs/research/candidate-study/publication/evidence-manifest-final.json \
  --evidence-root . \
  --analysis reanalysis-final-01 \
  --output illustrations-final-01
```

The selector verifies that its rule was frozen before native confirmation execution. It selects the first repeated harmful direct lookup, with the declared fallback, and the first repeated benefit. Each JSON/Markdown pair retains complete original and selected prompts, all repetitions, certificates and raw-file hashes. Native SSE content and token IDs are independently reconstructed; prompt-progress events that declare zero predicted tokens are kept distinct from generated output. The illustrations accompany the complete population tables and do not alter denominators.

## Regenerate standalone figures

Only plotting needs external Python packages. The shared dependency lock includes all installed plotting dependencies and exact versions:

```bash
python3 -m venv .venv-analysis
.venv-analysis/bin/python -m pip install \
  -r lean-model-lab-source/docs/research/plotting-requirements.txt

OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
.venv-analysis/bin/python \
  lean-model-lab-source/docs/research/candidate-study/publication/scripts/plot.py \
  --manifest lean-model-lab-source/docs/research/candidate-study/publication/evidence-manifest-final.json \
  --evidence-root . \
  --analysis reanalysis-final-01 \
  --output figures-final-01
```

The plotter emits PNG, SVG and PDF. Numeric values, units, orders and denominators come from reproduced CSVs. Colors, hatches and direct counts distinguish arms and outcome classes without relying on color alone. Source images were visually inspected, and the published PDFs were separately rendered with PDFium and inspected. An optional PDF-rendering helper is included in `publication/scripts/render_pdf_for_review.py`; it is not needed for native-evidence reanalysis or figure generation.

File hashes for regenerated PDF/SVG figures can differ because of timestamps, fonts and rendering metadata. Declared data identities and scientific table values are the reproduction targets; the original reviewed assets retain their own exact hashes. The final portable check receipt records the actual staged script, manifest and export identities used in validation.

## Reconcile observed memory and process timing

```bash
python3 lean-model-lab-source/docs/research/candidate-study/publication/scripts/summarize_resources.py \
  --manifest lean-model-lab-source/docs/research/candidate-study/publication/evidence-manifest-final.json \
  --evidence-root . \
  --output memory-and-timing-summary-01.json
```

This standard-library command verifies manifest-bound report, config and queue-receipt hashes, reconciles server VmHWM with all 32 raw resource files, retains exact observed bytes and configured limits, and separates archive-process execution from queue waiting. Per-attempt raw resource hashes accompany the per-model ranges. Both timing intervals remain inside original-allocation accounting; overlapping scopes must not be added.

## Inspect with the original product

For the negative investigation, this exact original producer was also tested against the exported study without model weights:

```bash
python3 -I producer-5f1aabf84635e33dd166ee656d5bcb5830f25a5f4f5d68433e2fd3e4498fb986.pyz \
  inspect evidence/negative-confirm-slice-study04/study
```

The separate 14B feasibility study uses its own archive03 producer listed in the manifest. The final reader/runtime is a separate presentation artifact; it does not replace original producer identity or native outputs. Original command streams use supported `.txt` extensions in the publication copy. `operational-derivatives.json` records any literal producer-workspace path replacement with a named documentary token, together with original/derived hashes and byte counts. Frozen scientific artifacts and the five native training files remain byte-exact, as recorded in `original-scientific-artifacts.json`.

Earlier staged manifests, checks and scripts are retained as labeled development provenance. The final manifest and the four portable entrypoints above are the complete-package interface. `original-scripts/` preserves earlier workspace-oriented orchestration and analysis versions for provenance; they are not prerequisites for running this guide.

Additional native execution is a new experiment with a valid allocation and new output directories. It must preserve the intended scientific settings and record its own timing, model/runtime verification and actual outcomes. The closed positive-advance branches do not authorize prompt/seed searches, and editing an old monotonic deadline does not create a fresh original experiment. A separate native reproduction is reported separately from the original observations; reanalyzing retained outputs creates no new model responses or independent population samples.
