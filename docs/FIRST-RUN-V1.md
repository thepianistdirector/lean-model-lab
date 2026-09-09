# First run from a prepared v1 package

This guide describes the local review candidate. Public v1 download, external-person use and independent human review remain unverified until recorded in the final release evidence. The repository is [thepianistdirector/lean-model-lab](https://github.com/thepianistdirector/lean-model-lab); project coordination is [Lean Model Lab on Tanduna](https://tanduna.com/projects/lean-model-lab).

## Inspect without inference

Obtain the complete approved `lean-model-lab-1.0.0-review-bundle.zip` and its external SHA-256 release record. Extract it with paths preserved and open its `START-HERE.txt`; the `lean-model-lab-1.0.0` directory contains the full offline index, CLI, source, study and research artifacts. The wrapper includes its exact executable construction source and `FILE-MANIFEST.json`. Individual artifacts remain available separately. Locate the enclosed `CANDIDATE-MANIFEST.json`. Verify the artifact SHA-256 values against the exact release record; a manifest shipped beside a file establishes local consistency, not an independently authenticated publisher. Keep the producer archives as well as the current CLI.

Open `index.html` directly in a browser. Each linked study has its own workbench, report and evidence ZIP. Inspect quality failures, output differences, cold/startup costs and retained unsuccessful attempts before interpreting a timing metric. Download and extract a study ZIP when you need its full raw inventory. No web server, model, account or developer credentials are required to read evidence.

Extract `lean-model-lab-source.zip`; work from its `lean-model-lab-source` directory. Copy the supplied `lean-model-lab.pyz` into that directory. Check the documented Python version and then run:

```sh
python3 -I lean-model-lab.pyz --version
python3 -I lean-model-lab.pyz profiles
python3 -I lean-model-lab.pyz research mechanisms
python3 -I lean-model-lab.pyz trace validate workloads/synthetic-key-copy-v1.json
```

The ZIP root's `FILE-MANIFEST.json` inventories source and research files. It is separate from the executable's embedded `BUILD-MANIFEST.json`. Source/runtime identity is also recorded in the candidate manifest. Original source, documentation and synthetic data are AGPL-3.0-only; third-party dependencies keep their own licenses.

## Execute a bounded experiment

Use a supported Linux x86_64 machine and your own authorized finite CPU, RAM, disk and wall-time allocation. The campaign's allocation file is historical evidence; copying it does not grant resources or start a new clock. Read [the recipe runbook](RUNBOOK-0.4.md) for exact model/backend acquisition, reviewed hashes, resource admission and preparation commands. No paid API or GPU is required by the admitted CPU lane. Model weights and backend binaries are intentionally separate from this distribution.

Follow [the proposal-to-experiment runbook](RUNBOOK-V1.md) to create and freeze a registered proposal, protocol and development recipe; run the actual CLI; inspect the persisted study; produce HTML/JSON; and export retained evidence. Use a small development study to verify operation before a prospectively frozen confirmation campaign. Development is not eligible confirmation. Keep every attempt and the exact producing archive.

To reproduce a research result, use that package's rerun specification, comparator and seeds, with your own fresh study/allocation and measured environment. Report environmental differences and discrepancies. A rerun is not expected to reproduce wall time bit for bit on another host; native quality/output differences still need complete reporting. Reconstructing tables from included raw outputs checks analysis, whereas executing the model again checks a different part of reproducibility.

For the complete investigation ZIPs, [the reanalysis guide](research/REANALYSIS.md) identifies the source/evidence layout, shared exact plotting-dependency lock and each portable entrypoint.

## Verify supported recovery

Start by inspecting the study. The supplied recovery procedure retains the interrupted attempt, repairs only the journal index when needed, reconciles same-boot unfinished work and resumes into a new attempt ID. It never silently replaces missing observations. Use the original executable and recipe, and retain both failure and replacement costs. The release's clean-environment receipt must state exactly which interruption was exercised and on what environment; a same-host worktree is not a separate machine or external person.

See [compatibility and troubleshooting](COMPATIBILITY-AND-TROUBLESHOOTING.md) for refusal meanings and evidence to include in a report. Concrete contributor opportunities are in [CONTRIBUTING.md](../CONTRIBUTING.md).

When assembling your own distribution with `tools/build_v1_release_bundle.py`, use letters, digits, underscores and hyphens for `--study SAFE_NAME=EXPORT_DIRECTORY` and `--research SAFE_NAME=SPECIFICATION`. A public package alias may differ from a native study directory or model profile; keep the portable evidence manifest aligned with the published alias. Periods are not accepted in these packaging identifiers.
