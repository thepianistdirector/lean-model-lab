# Reanalyze a complete research ZIP

Extract one `*-research.zip` into its own directory and verify every file against its root `FILE-MANIFEST.json`. The package contains the complete source in `lean-model-lab-source/`, selected exports in `evidence/`, and the exact producing executables at the package root. Workbench HTML opens directly without Python, a model, a server or an account.

For figure regeneration, use an existing matching environment or create a local one. The shared lock records all eleven plotting dependencies used in this campaign:

```sh
python3 -m venv reanalysis-env
reanalysis-env/bin/pip install \
  -r lean-model-lab-source/docs/research/plotting-requirements.txt
```

These commands install optional analysis dependencies. The product CLI itself uses the Python standard library. The lock records the observed environment; another platform or font renderer may produce different figure bytes. Retained scientific tables and raw outputs have their own exact identities.

Run the relevant analysis from the extracted package root, using a new output directory:

```sh
# Quality package: its populated manifest and five export audits are at root.
reanalysis-env/bin/python \
  lean-model-lab-source/docs/research/quality-study/confirmation-14b/portable_reanalysis.py \
  --evidence-manifest evidence-manifest.json --output new-quality-analysis
```

The [candidate rerun guide](candidate-study/PUBLICATION-RERUN.md) uses its source-local `publication/evidence-manifest-final.json`, including the actual training artifacts. The [systems rerun guide](systems-study/reproduce.md) uses its source-local `evidence-manifest.json`. Both accept an explicit evidence root and a fresh output directory. Their full commands and expected comparisons belong to those guides so that one authoritative command stays beside each analysis implementation.

The final research packages also carry their corresponding separate-agent repetition under `evidence/reproduction-quality/`, `evidence/reproduction-candidate/` or `evidence/reproduction-systems/`. This additional export has its own workbench and export receipt. It is separate from each original analysis manifest: do not add its observations to the original sample, confirmation denominator or effect estimate. Each individual research ZIP supplies its own repeated cell; the complete review bundle supplies all three. The common source tree contains the review's cross-study receipts and discussion.

Reanalysis reads retained native evidence; it does not execute the model or provide new independent observations. A native rerun needs your own finite resource decision and the exact admitted model/backend, as described in each research guide and the [external first-run guide](../FIRST-RUN-V1.md). Keep a discrepancy, incomplete run or failed quality gate in the resulting report. Never change a frozen input or discard an unfavorable attempt to obtain agreement.
