# Reuse an already prepared profile

`tools/adopt_prepared_profile.py` verifies existing model and backend bytes under an already approved, active allocation. It creates a new compatible v2 setup receipt without downloading, copying model weights, compiling, launching the server or running inference. The old preparation receipt and its costs remain intact in a separate ancestor scope.

Use this when the prepared model belongs to an earlier allocation and the current allocation admits its reuse. A legacy schema-1 receipt can admit only its exact reviewed Qwen2.5 0.5B FP16 profile. A schema-2 source must match the requested admitted profile exactly. The current allocation may also have prepared a different model: adopting the 0.5B profile does not relabel the 14B preparation receipt.

## Run from the source workspace

Start at the outermost supplied workspace containing `WORKSPACE.json`. Every input and the new output directory must stay within this workspace. The output's parent must exist; the output itself must not. Symlink components, parent traversal, nonregular inputs and overwriting an existing output are refused.

The following is the repository's existing 0.5B-to-current-allocation reuse example. It is a command to run after the current heavy study releases the shared lease, not evidence that adoption has already run:

```bash
python3 tools/adopt_prepared_profile.py \
  --allocation .cache/allocation-0.4-20260908.json \
  --source-setup .cache/prepared-20260908-01/setup-with-protocol-recovery.json \
  --server .cache/prepared-20260908-01/build/bin/llama-server \
  --model .cache/prepared-20260908-01/qwen2.5-0.5b-instruct-fp16.gguf \
  --profile qwen2.5-0.5b-instruct-fp16-v2 \
  --output .cache/adopted-0.5b-current-02
```

For another prepared workspace, substitute its explicit current allocation, full source setup receipt, existing server/model paths and admitted profile ID. Pass the **full** prior receipt including failures and recovery, not a hand-selected successful-build record. The tool verifies what the supplied receipt binds; it cannot discover omitted historical experiments or authenticate its author.

The current allocation must be approved, active on this Linux boot and within the existing time/memory/disk/thread ceilings. Source setup records must end before the current allocation starts; a v2 source must have a distinct allocation identity. Schema 1 contains no allocation object, so the tool retains that limitation instead of inventing an old allocation ID or closure proof. Cross-boot reconciliation is not supported by this command.

Only one acquisition/build/study/adoption may hold the workspace heavy lease. A busy lease causes immediate refusal before creating the output; the command does not start another allocation or wait indefinitely. Deadline and process RSS are checked between model-hash chunks. Workspace disk is scanned initially, between phases and periodically during hashing, with deadline/RSS checks within the scan. Limits stop work; they are never reset or extended.

## What is verified and retained

The command validates the original schema-1/schema-2 receipt, its pinned backend revision/patch and reviewed model identity; hashes the workspace's reviewed patch; checks every expected model filename, size and SHA-256; and hashes the exact executable server against the source receipt. Inputs are checked for changes during verification. It does not rebuild or execute the binary, independently certify a source checkout or qualify another environment. The runtime still performs its own actual-attempt admission checks.

The output contains:

- `setup.json`: final success marker, accepted by the existing v2 receipt validator and runtime with the exact current allocation/profile.
- `source-setup.json`: exact original receipt bytes, including formatting and all recorded failures.
- `ancestor-costs.json`: original receipt SHA-256 and text, original records, historical attributed phase time, elapsed setup span, gaps, acquired bytes, terminal counts and source allocation when available.
- `allocation.json`, `model-profile.json`, model/backend verification records, an append-only setup event journal and one immutable receipt per phase.
- `adoption.json`: verification manifest, source/setup identities, artifact paths, measured current verification time and the explicit cost boundary. This manifest alone is insufficient without a valid `setup.json`.

The v2 schema requires the phase labels `source-acquisition`, `model-acquisition` and `build`. Here their details explicitly identify **reuse and verification**. Each reports zero newly acquired model/source/build artifact bytes; each records measured current verification time. Small receipt/journal output files still consume disk and allocation time. No new acquisition/build work is fabricated, and the old acquisition/build costs are not declared zero.

Historical intervals never enter the current allocation's setup ledger. The full original UTF-8 receipt and historical cost summary are also embedded in the first phase's structured `details` JSON under `ancestor`, so normal runtime copying and raw evidence export of setup records retain ancestry even without the sidecars. Its `source_receipt_raw_utf8` re-encodes to the exact original bytes and is bound by `source_receipt_sha256`. Nested ancestor scopes, if any, remain explicit rather than being summed twice.

Current workbench totals describe current-allocation intervals; they do not automatically add or display the separate ancestor costs. Inspect the retained ancestor JSON when reporting total historical preparation costs. Do not compare a verification-only total against a fresh-build total as though their cost scopes were identical. Legacy source receipts provide recorded setup costs, not an invented total for all historical allocation activity.

Use the existing server/model paths with the newly emitted `setup.json` and a recipe bound to that same current allocation/profile. The command produces preparation evidence only: no quality result, runtime verification, study success, training claim or public-release permission follows from adoption.

## Failures and interruption

After an output directory is created, malformed receipts, profile/hash mismatches, resource exhaustion and handled SIGINT/SIGTERM cancellation retain `setup-failure.json`, completed/failed/interrupted phase records, the journal and any copied source receipt. A failed run does not emit a valid new `setup.json`. Admission errors such as an inactive allocation, occupied lease or invalid output path occur before output creation and are reported on stderr. Existing artifacts are never overwritten or removed.

Choose a new output directory for a corrected attempt and retain the failed one for cost accounting. An uncatchable termination can leave only the already flushed journal and partial receipts; their existence is not success. There are no child processes to supervise or orphan: hashing and metadata verification run in the coordinator itself, so no shell or process-guard launcher is needed.

Path and mutation checks support an explicitly trusted workspace. They do not create an OS security boundary against a malicious process sharing the same Unix identity.

## Validation evidence

The automated tests use tiny inert local files and substituted reviewed-profile pins. They perform no real model hashing, download, build or native execution. They cover both source receipt schemas, exact ancestor preservation, current-versus-historical allocation separation, malformed identity/profile/JSON, corrupted model/server, allocation admission, symlink/overwrite refusal, mutation detection, heavy-lease exclusion, cancellation and resource checks. Real adoption and subsequent native inference remain separate evidence to be recorded when run.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests \
  python3 -m unittest tests/test_adopt_profile.py -v
```
