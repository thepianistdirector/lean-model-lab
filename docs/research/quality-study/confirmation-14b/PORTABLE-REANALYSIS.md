# Portable reanalysis of exported evidence

The public entrypoint is `portable_reanalysis.py`. It accepts explicit paths in an evidence manifest and a **new** output directory. It does not load a model, require a private `.cache` tree, change source constants, or extend a producer's allocation clock with the current machine's monotonic clock.

After extracting the supplied study/source archives, create or use the final distribution's populated evidence manifest. Paths resolve relative to the manifest file; absolute paths are also accepted for local verification. `evidence-manifest.example.json` shows the role and path contract. Safe study-directory names and archive locations are configurable; the example names are not asserted to be final integration names.

```sh
python3 -m venv reanalysis-env
reanalysis-env/bin/pip install -r PATH/TO/quality-study/confirmation-14b/requirements-portable.txt
reanalysis-env/bin/python PATH/TO/quality-study/confirmation-14b/portable_reanalysis.py \
  --evidence-manifest PATH/TO/evidence-manifest.json \
  --output NEW-REANALYSIS-DIRECTORY
```

Use an already prepared Python/Matplotlib environment when available. Python 3.12+ and Matplotlib 3.10.6 are the declared local renderer environment. The evidence itself can be inspected with the packaged CLI without Matplotlib. No network access is used by the reanalysis script. Matplotlib is only needed to render standalone PNG/SVG/PDF figures; its own installed distribution supplies its dependency licenses and font notices.

Each manifest study entry has a stable **role ID** and explicit `study`, `report` and `raw_audit` paths. Required roles are `14b`, `legacy-comparison`, `legacy-protocol-failure` and `development`. Add `confirmation-14b` for the distinct held-out follow-up. These IDs determine the intended comparison labels; they do not identify a private directory. The study folders inside publication archives follow `evidence/SAFE_STUDY_NAME/study`.

The report must be the exported derivative's verified report. The raw audit must be generated from that actual derivative, not silently copied from a different raw-byte tree. The root source distribution supplies the raw auditor:

```sh
python3 PATH/TO/EXTRACTED-SOURCE/tools/audit_raw_study.py \
  evidence/SAFE_STUDY_NAME/study --output NEW-AUDIT.json
```

Put that audit path into the manifest. The auditor's process exit is not its scientific status: the retained protocol failure should remain `INCOMPLETE_OR_FAILED`. Optional `report_sha256` and `raw_audit_sha256` fields pin exact files. Optional `producer_archive` and required accompanying `producer_archive_sha256` fields verify the bytes of a supplied `producer-<SHA>.pyz`; they do not authenticate who ran it or establish that raw observations came from that execution.

The entrypoint checks config bindings, optional file/archive hashes, every observed exact-answer count and every paired token-mismatch list against retained report evidence. It emits all observed requests, attempts, pairs, output differences, producer cost views, supplied interval reconciliation, source-relative file hashes and standalone figures. Ineligible efficiency ratios remain null. If the confirmation role is present, it additionally emits the full-prompt split audit and the separately frozen quality/efficiency/tail gate evaluation. No failed cell is replaced or omitted.

Output must not exist and cannot be inside an input study. The script's temporary and Matplotlib configuration directories live under the chosen new output. Producer clock cutoffs remain as reported; reanalysis elapsed time is a separate local measurement. Interval identity includes the recorded boot, and a combined interval union is unavailable across different boot clocks. The script makes no claim that supplied phase ledgers enumerate every piece of prior work.

`reanalysis-receipt.json` identifies the supplied manifest and script hashes and scopes the result to local consistency checks. Final publication figures require their reviewed source-relative SHA inventory; changing a figure or table requires refreshing that inventory. The unchanged original package remains available one directory above, while this publication revision resolves paths through the manifest.

Local validation uses actual exported derivatives with fresh raw audits. Its populated local manifest and outputs are investigator evidence, not a requirement that an external researcher reproduce those local paths. Final distribution manifests supply the portable relative mapping after integration.
