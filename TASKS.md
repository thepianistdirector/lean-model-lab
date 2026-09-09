# Lean Model Lab contributor tasks

Generated from [plan/tasks.json](plan/tasks.json); edit the canonical ledger, then run `python3 tools/generate_plan.py`. Task states and evidence live in that ledger; [STATUS.md](STATUS.md) summarizes the root execution evidence. Native publication is separate.


249 active outcomes in 32 waves. Release horizons: 0.1: 40, 0.2: 8, 0.3: 8, 0.4: 8, 1.0: 14, exploratory: 8, foundation: 3, later 0.x: 64, long-term: 96.

The three historical foundation outcomes remain DONE. New planning rows do not establish implementation, automated pass, runtime proof, user validation or release. Full original contracts and history remain in [immutable lineage](plan/lineage/821c6364/plan/tasks.json). Historical source contracts are not additional active outcomes.

Before executing a new packet, the root records owned files, actual commands, falsifiers, resource/permission bounds and exit evidence. Model-free checks are preparation; 0.1 requires real inference and quality evaluation.

## Wave 0: Accepted architecture and planning foundation

Horizon: foundation. Exit evidence: Accepted root review and plan-tool checks in immutable foundation STATUS.md.

### LM-F01 — Establish the architecture and experiment contract

- Project key: `lean-model-lab:LM-F01`; feature area: foundation; target: foundation; status: **DONE**; evidence: **DONE**.

- Outcome: Define versioned model/data/tokenizer/workload/hardware/runtime provenance; distinct training and inference metrics; measurement controls; enforced OS/container/VM isolation before untrusted candidate/agent or protected-confirmation execution; protected candidate/evaluator/holdout boundaries; multi-objective search and confirmation; durable run/failure artifacts; resource accounting, cancellation/recovery and conditional CPU/Metal/CUDA/remote seams, with current primary sources and explicit nonclaims.

- Dependencies: none.

- Acceptance: Define versioned model/data/tokenizer/workload/hardware/runtime provenance; distinct training and inference metrics; measurement controls; enforced OS/container/VM isolation before untrusted candidate/agent or protected-confirmation execution; protected candidate/evaluator/holdout boundaries; multi-objective search and confirmation; durable run/failure artifacts; resource accounting, cancellation/recovery and conditional CPU/Metal/CUDA/remote seams, with current primary sources and explicit nonclaims.

- Origin: accepted source requirement; references: lean-model-lab:LM-F01.

- Risk/evidence needs: Accepted documentation/tooling only; no scientific/runtime completion inferred.

- Recorded evidence: plan/lineage/821c6364/STATUS.md (Accepted architecture documentation and plan tooling, 2026-09-07.).

### LM-F02 — Establish the outcome and dependency roadmap

- Project key: `lean-model-lab:LM-F02`; feature area: foundation; target: foundation; status: **DONE**; evidence: **DONE**.

- Outcome: Add an outcome-based Wave 0 and evidence-driven scale path while preserving all original LM-001–LM-024 IDs, acceptance text, dependency edges, Waves 1–8 and their gates; connect the original entry to LM-F03 without converting plans into delivery claims.

- Dependencies: LM-F01.

- Acceptance: Add an outcome-based Wave 0 and evidence-driven scale path while preserving all original LM-001–LM-024 IDs, acceptance text, dependency edges, Waves 1–8 and their gates; connect the original entry to LM-F03 without converting plans into delivery claims.

- Origin: accepted source requirement; references: lean-model-lab:LM-F02.

- Risk/evidence needs: Accepted documentation/tooling only; no scientific/runtime completion inferred.

- Recorded evidence: plan/lineage/821c6364/STATUS.md (Accepted architecture documentation and plan tooling, 2026-09-07.).

### LM-F03 — Establish an executable next-work packet and repository-plan validation

- Project key: `lean-model-lab:LM-F03`; feature area: foundation; target: foundation; status: **DONE**; evidence: **DONE**.

- Outcome: Define an immediately executable LM-001 selection packet and the dependent LM-002 hardware/backend decision and LM-003 no-compute harness entry; bound one lawful decoder-only model/tokenizer, a deterministic synthetic 128-request workload and representative rejection fixtures; validate the repository plan without installing dependencies or running model compute.

- Dependencies: LM-F02.

- Acceptance: Define an immediately executable LM-001 selection packet and the dependent LM-002 hardware/backend decision and LM-003 no-compute harness entry; bound one lawful decoder-only model/tokenizer, a deterministic synthetic 128-request workload and representative rejection fixtures; validate the repository plan without installing dependencies or running model compute.

- Origin: accepted source requirement; references: lean-model-lab:LM-F03.

- Risk/evidence needs: Accepted documentation/tooling only; no scientific/runtime completion inferred.

- Recorded evidence: plan/lineage/821c6364/STATUS.md (Accepted architecture documentation and plan tooling, 2026-09-07.).

## Wave 1: A lawful workload has a frozen quality contract

Horizon: 0.1. Exit evidence: Bind model, tokenizer, trace, hardware, runtime, quality plan and finite paired schedule; reject unresolved mandatory fields before compute.

### LM-W01-T01 — Pin model rights and exact artifacts

- Project key: `lean-model-lab:LM-W01-T01`; feature area: specification; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Record immutable weight/config revision, byte hashes, license, acquisition route and safe format.

- Dependencies: LM-F03.

- Acceptance: Record immutable weight/config revision, byte hashes, license, acquisition route and safe format; reject missing or incompatible terms.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-001, lean-model-lab:LM-002, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/results/cpu-20260908.md (Actual approved artifact retrieval, model SHA and license inventory; source rights reviewed. Public/external retrieval still pending.).

### LM-W01-T02 — Bind tokenizer and text semantics

- Project key: `lean-model-lab:LM-W01-T02`; feature area: specification; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Pin vocabulary, normalization, special tokens and prompt template.

- Dependencies: LM-W01-T01.

- Acceptance: Pin vocabulary, normalization, special tokens and prompt template; a changed asset invalidates the comparison identity.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-001, lean-model-lab:LM-002, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/results/cpu-20260908.md (Actual GGUF vocabulary/special-token/template inventory and identical tokenized inputs across 12 real arms; no external attestation.).

### LM-W01-T03 — Admit one CPU backend

- Project key: `lean-model-lab:LM-W01-T03`; feature area: specification; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Record exact version, dependency graph, license, loading behavior, supported policy and local feasibility.

- Dependencies: LM-W01-T02.

- Acceptance: Record exact version, dependency graph, license, loading behavior, supported policy and local feasibility; obtain missing adoption approval before installation.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-001, lean-model-lab:LM-002, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/results/cpu-20260908.md (Owner-approved pinned CPU backend built with declared GCC 8 patch; actual service/slot/settings verification and inference succeeded.).

### LM-W01-T04 — Bound the shared-host experiment

- Project key: `lean-model-lab:LM-W01-T04`; feature area: specification; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Freeze CPU threads, memory, storage, duration and attempt limits using current host evidence.

- Dependencies: LM-W01-T03.

- Acceptance: Freeze CPU threads, memory, storage, duration and attempt limits using current host evidence; preflight refuses excess reservations.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-001, lean-model-lab:LM-002, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/results/cpu-20260908.md (Original two-hour, 5-GiB, 4-GiB, two-thread allocation bound setup/run/recovery; sampled limits are not a sandbox or exhaustive peak proof.).

### LM-W01-T05 — Freeze the 128-request workload

- Project key: `lean-model-lab:LM-W01-T05`; feature area: specification; target: 0.1; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: Store four prompt-length strata, fixed seed, maximum 32 requested output tokens and concurrency 1/4.

- Dependencies: LM-W01-T04.

- Acceptance: Store four prompt-length strata, fixed seed, maximum 32 requested output tokens and concurrency 1/4; deterministic regeneration matches the digest.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-001, lean-model-lab:LM-002, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.).

### LM-W01-T06 — Predeclare a real quality rule

- Project key: `lean-model-lab:LM-W01-T06`; feature area: specification; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Publish the quality metric, reference/evaluation inputs, threshold and competence limits before candidate outputs.

- Dependencies: LM-W01-T05.

- Acceptance: Publish the quality metric, reference/evaluation inputs, threshold and competence limits before candidate outputs; a placeholder fails admission.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-001, lean-model-lab:LM-002, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/results/cpu-20260908.md (Frozen exact-answer 95% gate evaluated on real outputs: all arms fail at 99/128; no threshold relaxation. External publication/review pending.).

### LM-W01-T07 — Freeze one policy and interpretation threshold

- Project key: `lean-model-lab:LM-W01-T07`; feature area: specification; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Specify exactly one supported batching or cache change, unchanged sampling/stop rules, practical-effect threshold and explicit no-gain interpretation..

- Dependencies: LM-W01-T06.

- Acceptance: Specify exactly one supported batching or cache change, unchanged sampling/stop rules, practical-effect threshold and explicit no-gain interpretation.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-001, lean-model-lab:LM-002, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/results/cpu-20260908.md (Exactly one declared same-slot prefix-cache policy executed under frozen practical and tail gates; no eligible speed estimate after quality/parity failures.).

### LM-W01-T08 — Approve the immutable comparison manifest

- Project key: `lean-model-lab:LM-W01-T08`; feature area: specification; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Bind model, tokenizer, trace, hardware, runtime, quality plan and finite paired schedule.

- Dependencies: LM-W01-T01, LM-W01-T02, LM-W01-T03, LM-W01-T04, LM-W01-T05, LM-W01-T06, LM-W01-T07.

- Acceptance: Bind model, tokenizer, trace, hardware, runtime, quality plan and finite paired schedule; reject unresolved mandatory fields before compute.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-001, lean-model-lab:LM-002, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/results/cpu-20260908.md (Measured config binds model/tokenizer/workload/backend+patch/implementation/hardware/settings and fixed schedule; owner admission recorded.).

## Wave 2: Model-free checks reject invalid evidence

Horizon: 0.1. Exit evidence: A documented model-free command runs representative defect fixtures and exits nonzero for each invalid family; zero-test success cannot pass.

### LM-W02-T01 — Validate versioned comparison records

- Project key: `lean-model-lab:LM-W02-T01`; feature area: contracts; target: 0.1; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: Unknown execution fields, unsupported schema versions and missing measured/simulated labels produce actionable validation errors..

- Dependencies: LM-W01-T08.

- Acceptance: Unknown execution fields, unsupported schema versions and missing measured/simulated labels produce actionable validation errors.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-003, lean-model-lab:LM-010, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.).

### LM-W02-T02 — Reproduce the synthetic request trace

- Project key: `lean-model-lab:LM-W02-T02`; feature area: contracts; target: 0.1; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: The fixed generator emits 128 uniquely identified requests in four strata.

- Dependencies: LM-W02-T01.

- Acceptance: The fixed generator emits 128 uniquely identified requests in four strata; duplicate IDs, malformed arrivals and overlong output budgets fail.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-003, lean-model-lab:LM-010, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.).

### LM-W02-T03 — Validate identity and quality mutations

- Project key: `lean-model-lab:LM-W02-T03`; feature area: contracts; target: 0.1; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: Mutating model/tokenizer/trace/stop rules or a quality threshold rejects eligibility even if reported speed improves..

- Dependencies: LM-W02-T02.

- Acceptance: Mutating model/tokenizer/trace/stop rules or a quality threshold rejects eligibility even if reported speed improves.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-003, lean-model-lab:LM-010, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.).

### LM-W02-T04 — Validate timing units and event order

- Project key: `lean-model-lab:LM-W02-T04`; feature area: contracts; target: 0.1; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: Negative durations, inconsistent units, backwards monotonic clocks and first tokens after completion fail with request IDs..

- Dependencies: LM-W02-T03.

- Acceptance: Negative durations, inconsistent units, backwards monotonic clocks and first tokens after completion fail with request IDs.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-003, lean-model-lab:LM-010, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.).

### LM-W02-T05 — Reconcile the full request population

- Project key: `lean-model-lab:LM-W02-T05`; feature area: contracts; target: 0.1; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: Dropped, timed-out, failed and absent requests remain in the expected denominator.

- Dependencies: LM-W02-T04.

- Acceptance: Dropped, timed-out, failed and absent requests remain in the expected denominator; omission cannot increase eligible goodput.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-003, lean-model-lab:LM-010, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.).

### LM-W02-T06 — Represent unavailable telemetry explicitly

- Project key: `lean-model-lab:LM-W02-T06`; feature area: contracts; target: 0.1; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: Unsupported memory, token gaps and energy serialize as UNAVAILABLE with scope/reason.

- Dependencies: LM-W02-T05.

- Acceptance: Unsupported memory, token gaps and energy serialize as UNAVAILABLE with scope/reason; numeric placeholders are rejected.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-003, lean-model-lab:LM-010, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.).

### LM-W02-T07 — Validate attempt and artifact identities

- Project key: `lean-model-lab:LM-W02-T07`; feature area: contracts; target: 0.1; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: Duplicate terminal attempts, altered input hashes and mismatched parent artifacts fail.

- Dependencies: LM-W02-T06.

- Acceptance: Duplicate terminal attempts, altered input hashes and mismatched parent artifacts fail; clean interrupted-attempt records remain inspectable.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-003, lean-model-lab:LM-010, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.).

### LM-W02-T08 — Prove falsifier discovery in the CLI

- Project key: `lean-model-lab:LM-W02-T08`; feature area: contracts; target: 0.1; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: A documented model-free command runs representative defect fixtures and exits nonzero for each invalid family.

- Dependencies: LM-W02-T01, LM-W02-T02, LM-W02-T03, LM-W02-T04, LM-W02-T05, LM-W02-T06, LM-W02-T07.

- Acceptance: A documented model-free command runs representative defect fixtures and exits nonzero for each invalid family; zero-test success cannot pass.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-003, lean-model-lab:LM-010, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.).

## Wave 3: One CPU backend executes both comparison arms

Horizon: 0.1. Exit evidence: Real baseline/candidate artifacts pass identity, arrival, stop-rule and completeness checks; unsupported timing remains unavailable.

### LM-W03-T01 — Probe the admitted backend locally

- Project key: `lean-model-lab:LM-W03-T01`; feature area: execution; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: The exact backend reports usable CPU execution, policy controls, context bounds and observable events.

- Dependencies: LM-W01-T08, LM-W02-T08.

- Acceptance: The exact backend reports usable CPU execution, policy controls, context bounds and observable events; unsupported settings fail before generation.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-004, lean-model-lab:LM-007, owner-launch:2026-09-07:section-5, lean-model-lab:LM-010, lean-model-lab:LM-020.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/results/cpu-20260908.md (Actual CPU server readback and raw request execution verified locally; initial native-protocol failure retained before corrected frozen client.).

### LM-W03-T02 — Load reviewed local model artifacts

- Project key: `lean-model-lab:LM-W03-T02`; feature area: execution; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Load only hash-matched approved weights/tokenizer with remote-code execution disabled.

- Dependencies: LM-W03-T01.

- Acceptance: Load only hash-matched approved weights/tokenizer with remote-code execution disabled; a missing or changed file stops preparation.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-004, lean-model-lab:LM-007, owner-launch:2026-09-07:section-5, lean-model-lab:LM-010, lean-model-lab:LM-020.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/results/cpu-20260908.md (Approved hash-matched FP16 GGUF loaded locally with exact metadata inventory; no model remote-code execution.).

### LM-W03-T03 — Capture actual request lifecycle events

- Project key: `lean-model-lab:LM-W03-T03`; feature area: execution; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Record arrival, admission, execution start, first token and terminal outcome from observable runtime events.

- Dependencies: LM-W03-T02.

- Acceptance: Record arrival, admission, execution start, first token and terminal outcome from observable runtime events; distinguish client and engine clocks.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-004, lean-model-lab:LM-007, owner-launch:2026-09-07:section-5, lean-model-lab:LM-010, lean-model-lab:LM-020.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.); docs/results/cpu-20260908.md (All 1536 real main requests reconciled to raw SSE; client timestamps observed, engine execution start and individual token emission times UNAVAILABLE.).

### LM-W03-T04 — Execute the baseline under both concurrency modes

- Project key: `lean-model-lab:LM-W03-T04`; feature area: execution; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: All 128 requests run through the real decoder at concurrency 1 and 4 with retained outputs, token counts and failures..

- Dependencies: LM-W03-T03.

- Acceptance: All 128 requests run through the real decoder at concurrency 1 and 4 with retained outputs, token counts and failures.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-004, lean-model-lab:LM-007, owner-launch:2026-09-07:section-5, lean-model-lab:LM-010, lean-model-lab:LM-020.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/results/cpu-20260908.md (Real baseline completed all 128 requests in each of six baseline arms at concurrency 1/4, with retained outputs and failed quality.).

### LM-W03-T05 — Implement the single declared policy arm

- Project key: `lean-model-lab:LM-W03-T05`; feature area: execution; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Run the same trace and quality contract with only the approved policy changed.

- Dependencies: LM-W03-T04.

- Acceptance: Run the same trace and quality contract with only the approved policy changed; configuration diff detects any second experimental variable.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-004, lean-model-lab:LM-007, owner-launch:2026-09-07:section-5, lean-model-lab:LM-010, lean-model-lab:LM-020.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.); docs/results/cpu-20260908.md (Real candidate completed six arms; raw cache_n confirms reuse with identical prompt-token inputs; C4 output parity fails and blocks eligibility.).

### LM-W03-T06 — Account for cold and warm preparation

- Project key: `lean-model-lab:LM-W03-T06`; feature area: execution; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Retain process startup, model load, compilation if present, cache preparation and warmup intervals separately from useful execution..

- Dependencies: LM-W03-T05.

- Acceptance: Retain process startup, model load, compilation if present, cache preparation and warmup intervals separately from useful execution.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-004, lean-model-lab:LM-007, owner-launch:2026-09-07:section-5, lean-model-lab:LM-010, lean-model-lab:LM-020.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.); docs/results/cpu-20260908.md (Actual build failures, model load, tokenization/cache preparation and service intervals retained; fresh process does not imply cold OS cache.).

### LM-W03-T07 — Interrupt and recover a real attempt

- Project key: `lean-model-lab:LM-W03-T07`; feature area: execution; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Cancellation preserves completed requests and consumed costs.

- Dependencies: LM-W03-T06.

- Acceptance: Cancellation preserves completed requests and consumed costs; restart uses a new attempt and never duplicates terminal request records.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-004, lean-model-lab:LM-007, owner-launch:2026-09-07:section-5, lean-model-lab:LM-010, lean-model-lab:LM-020.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.); docs/results/cpu-20260908.md (Actual packaged real-model crash after five checkpoints; backend stopped, torn journal retained/repaired, new attempt completed 128; control campaign incomplete.).

### LM-W03-T08 — Demonstrate backend parity of contracts

- Project key: `lean-model-lab:LM-W03-T08`; feature area: execution; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Real baseline/candidate artifacts pass identity, arrival, stop-rule and completeness checks.

- Dependencies: LM-W03-T01, LM-W03-T02, LM-W03-T03, LM-W03-T04, LM-W03-T05, LM-W03-T06, LM-W03-T07.

- Acceptance: Real baseline/candidate artifacts pass identity, arrival, stop-rule and completeness checks; unsupported timing remains unavailable.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-004, lean-model-lab:LM-007, owner-launch:2026-09-07:section-5, lean-model-lab:LM-010, lean-model-lab:LM-020.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/results/cpu-20260908.md (Actual identity/arrival/settings/completeness audit passes; output-token parity fails at C4 and remains an explicit gate failure.).

## Wave 4: Full costs and quality constrain measured findings

Horizon: 0.1. Exit evidence: The conclusion follows frozen eligibility/practical thresholds and measured uncertainty; quality failure or noise cannot become a positive claim.

### LM-W04-T01 — Evaluate actual outputs against the frozen rule

- Project key: `lean-model-lab:LM-W04-T01`; feature area: evaluation; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Evaluate retained generated outputs with the predeclared quality contract.

- Dependencies: LM-W02-T08, LM-W03-T08.

- Acceptance: Evaluate retained generated outputs with the predeclared quality contract; failed quality blocks efficiency eligibility without deleting outputs.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-009, lean-model-lab:LM-010, lean-model-lab:LM-011, lean-model-lab:LM-020, owner-launch:2026-09-07:section-5, lean-model-lab:LM-004, lean-model-lab:LM-007, lean-model-lab:LM-021.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/results/cpu-20260908.md (All twelve real arm qualities evaluated at 99/128; original 95% gate blocks efficiency claims and retains all outputs.).

### LM-W04-T02 — Aggregate latency from observable events

- Project key: `lean-model-lab:LM-W04-T02`; feature area: evaluation; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Queue delay, TTFT and end-to-end metrics trace to supported raw timestamps and declare client/engine boundary.

- Dependencies: LM-W04-T01.

- Acceptance: Queue delay, TTFT and end-to-end metrics trace to supported raw timestamps and declare client/engine boundary; unobservable metrics stay unavailable.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-009, lean-model-lab:LM-010, lean-model-lab:LM-011, lean-model-lab:LM-020, owner-launch:2026-09-07:section-5, lean-model-lab:LM-004, lean-model-lab:LM-007, lean-model-lab:LM-021.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.); docs/results/cpu-20260908.md (Real raw client clocks support queue/TTFT/end-to-end summaries; engine execution start and engine token gaps remain UNAVAILABLE.).

### LM-W04-T03 — Compute throughput with complete denominators

- Project key: `lean-model-lab:LM-W04-T03`; feature area: evaluation; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Report request and actual output-token throughput with failed/missing counts and elapsed envelope.

- Dependencies: LM-W04-T02.

- Acceptance: Report request and actual output-token throughput with failed/missing counts and elapsed envelope; shortened outputs cannot masquerade as equivalent work.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-009, lean-model-lab:LM-010, lean-model-lab:LM-011, lean-model-lab:LM-020, owner-launch:2026-09-07:section-5, lean-model-lab:LM-004, lean-model-lab:LM-007, lean-model-lab:LM-021.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.); docs/results/cpu-20260908.md (1536/1536 main requests and 5887 actual tokens retained; raw throughput descriptive only; quality/parity failures null eligible ratios.).

### LM-W04-T04 — Execute counterbalanced repeated pairs

- Project key: `lean-model-lab:LM-W04-T04`; feature area: evaluation; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Retain every predeclared baseline/candidate pair, order, warm state and host load.

- Dependencies: LM-W04-T03.

- Acceptance: Retain every predeclared baseline/candidate pair, order, warm state and host load; incomplete pairs and contaminated runs are visibly flagged.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-009, lean-model-lab:LM-010, lean-model-lab:LM-011, lean-model-lab:LM-020, owner-launch:2026-09-07:section-5, lean-model-lab:LM-004, lean-model-lab:LM-007, lean-model-lab:LM-021.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/results/cpu-20260908.md (All 12 predeclared AB/BA/AB real arms retained with host load and fresh-process state; partly counterbalanced, no selection of fastest samples.).

### LM-W04-T05 — Report small-sample uncertainty and tails

- Project key: `lean-model-lab:LM-W04-T05`; feature area: evaluation; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Recompute effect intervals and p95/p99 from retained groups with explicit estimators and small-sample limitations.

- Dependencies: LM-W04-T04.

- Acceptance: Recompute effect intervals and p95/p99 from retained groups with explicit estimators and small-sample limitations; never select only the fastest run.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-009, lean-model-lab:LM-010, lean-model-lab:LM-011, lean-model-lab:LM-020, owner-launch:2026-09-07:section-5, lean-model-lab:LM-004, lean-model-lab:LM-007, lean-model-lab:LM-021.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/results/cpu-20260908.md (All pair records and nearest-rank tails retained; ratios/ranges unavailable after gate failure; 128-request tails are unstable, no confidence claim.).

### LM-W04-T06 — Reconcile full-wall resource accounting

- Project key: `lean-model-lab:LM-W04-T06`; feature area: evaluation; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Include startup, warmup, evaluation, cancellation, retries and failed work.

- Dependencies: LM-W04-T05.

- Acceptance: Include startup, warmup, evaluation, cancellation, retries and failed work; totals reconcile to attempt records and supported memory probes.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-009, lean-model-lab:LM-010, lean-model-lab:LM-011, lean-model-lab:LM-020, owner-launch:2026-09-07:section-5, lean-model-lab:LM-004, lean-model-lab:LM-007, lean-model-lab:LM-021.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.); docs/results/cpu-20260908.md (Full wall through comparison closure 2423.214019209 seconds including failed acquisition/build/protocol history and idle; recovery costs separately retained without reset.).

### LM-W04-T07 — Regenerate an accessible evidence report

- Project key: `lean-model-lab:LM-W04-T07`; feature area: evaluation; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: From raw bundles alone generate a readable report exposing validity, quality, uncertainty, all attempts and unavailable telemetry at narrow widths..

- Dependencies: LM-W04-T06.

- Acceptance: From raw bundles alone generate a readable report exposing validity, quality, uncertainty, all attempts and unavailable telemetry at narrow widths.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-009, lean-model-lab:LM-010, lean-model-lab:LM-011, lean-model-lab:LM-020, owner-launch:2026-09-07:section-5, lean-model-lab:LM-004, lean-model-lab:LM-007, lean-model-lab:LM-021.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.); docs/results/cpu-20260908.md (Real raw study regenerates identical JSON finding and standalone HTML; browser/keyboard/narrow-layout and human usability remain NOT TESTED.).

### LM-W04-T08 — Record a scoped gain, null or regression finding

- Project key: `lean-model-lab:LM-W04-T08`; feature area: evaluation; target: 0.1; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: The conclusion follows frozen eligibility/practical thresholds and measured uncertainty.

- Dependencies: LM-W04-T01, LM-W04-T02, LM-W04-T03, LM-W04-T04, LM-W04-T05, LM-W04-T06, LM-W04-T07.

- Acceptance: The conclusion follows frozen eligibility/practical thresholds and measured uncertainty; quality failure or noise cannot become a positive claim.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-009, lean-model-lab:LM-010, lean-model-lab:LM-011, lean-model-lab:LM-020, owner-launch:2026-09-07:section-5, lean-model-lab:LM-004, lean-model-lab:LM-007, lean-model-lab:LM-021.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/results/cpu-20260908.md (Scoped INELIGIBLE measured finding follows frozen quality/parity gates; no comparable-quality gain or statistically established no-speedup claim.).

## Wave 5: External researchers can reproduce the public finding

Horizon: 0.1. Exit evidence: Publish approved waves/tasks/dependencies via supported review workflow and read back counts, IDs, release status and actual access instructions.

### LM-W05-T01 — Package the runnable local tool

- Project key: `lean-model-lab:LM-W05-T01`; feature area: release; target: 0.1; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: Build an installable/source release with exact version, CLI, fixed trace, evaluation plan, invalid controls and reproducible build instructions..

- Dependencies: LM-W04-T08.

- Acceptance: Build an installable/source release with exact version, CLI, fixed trace, evaluation plan, invalid controls and reproducible build instructions.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-019, lean-model-lab:LM-021, lean-model-lab:LM-022, lean-model-lab:LM-023, lean-model-lab:LM-024, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/evidence/automated-tests.json (99 discovered automated software tests pass locally; test-server fixtures are synthetic. Real-model observations are separate evidence; full release/human acceptance is not implied.).

### LM-W05-T02 — Document lawful first-run retrieval

- Project key: `lean-model-lab:LM-W05-T02`; feature area: release; target: 0.1; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: A new user can obtain exact approved model/tokenizer assets and verify hashes using public instructions without developer credentials..

- Dependencies: LM-W05-T01.

- Acceptance: A new user can obtain exact approved model/tokenizer assets and verify hashes using public instructions without developer credentials.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-019, lean-model-lab:LM-021, lean-model-lab:LM-022, lean-model-lab:LM-023, lean-model-lab:LM-024, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/review/release-gates.md (Local retrieval, packaged execution/recovery, licenses and sanitized export implemented and checked; public artifact, external environment and full acceptance remain pending.).

### LM-W05-T03 — Test a clean packaged execution and recovery

- Project key: `lean-model-lab:LM-W05-T03`; feature area: release; target: 0.1; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: A fresh environment executes the packaged artifact through both arms, quality evaluation, report regeneration and interruption/restart with evidence retained..

- Dependencies: LM-W05-T02.

- Acceptance: A fresh environment executes the packaged artifact through both arms, quality evaluation, report regeneration and interruption/restart with evidence retained.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-019, lean-model-lab:LM-021, lean-model-lab:LM-022, lean-model-lab:LM-023, lean-model-lab:LM-024, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/review/release-gates.md (Local retrieval, packaged execution/recovery, licenses and sanitized export implemented and checked; public artifact, external environment and full acceptance remain pending.).

### LM-W05-T04 — Review first-run and report accessibility

- Project key: `lean-model-lab:LM-W05-T04`; feature area: release; target: 0.1; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Record keyboard, labels, error recovery, zoom/narrow-layout checks and actual user/domain-review evidence separately from automated assertions..

- Dependencies: LM-W05-T03.

- Acceptance: Record keyboard, labels, error recovery, zoom/narrow-layout checks and actual user/domain-review evidence separately from automated assertions.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-019, lean-model-lab:LM-021, lean-model-lab:LM-022, lean-model-lab:LM-023, lean-model-lab:LM-024, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

### LM-W05-T05 — Prepare the rights-complete release candidate

- Project key: `lean-model-lab:LM-W05-T05`; feature area: release; target: 0.1; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: Inventory source/model/fixture/dependency licenses, limitations, failures and sanitized raw results.

- Dependencies: LM-W05-T04.

- Acceptance: Inventory source/model/fixture/dependency licenses, limitations, failures and sanitized raw results; no private paths or secrets enter the archive.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-019, lean-model-lab:LM-021, lean-model-lab:LM-022, lean-model-lab:LM-023, lean-model-lab:LM-024, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

- Recorded evidence: docs/review/release-gates.md (Local retrieval, packaged execution/recovery, licenses and sanitized export implemented and checked; public artifact, external environment and full acceptance remain pending.).

### LM-W05-T06 — Publish and read back the authorized version

- Project key: `lean-model-lab:LM-W05-T06`; feature area: release; target: 0.1; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: After exact destination/artifact authorization, publish a versioned public 0.1 with checksums and confirm unauthenticated artifact retrieval..

- Dependencies: LM-W05-T05.

- Acceptance: After exact destination/artifact authorization, publish a versioned public 0.1 with checksums and confirm unauthenticated artifact retrieval.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-019, lean-model-lab:LM-021, lean-model-lab:LM-022, lean-model-lab:LM-023, lean-model-lab:LM-024, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

### LM-W05-T07 — Verify the external researcher workflow

- Project key: `lean-model-lab:LM-W05-T07`; feature area: release; target: 0.1; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: An external participant obtains the public artifact and completes run/report/recovery.

- Dependencies: LM-W05-T06.

- Acceptance: An external participant obtains the public artifact and completes run/report/recovery; record platform, version, observed result and remaining limitations.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-019, lean-model-lab:LM-021, lean-model-lab:LM-022, lean-model-lab:LM-023, lean-model-lab:LM-024, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

### LM-W05-T08 — Publish and verify the native Tanduna programme

- Project key: `lean-model-lab:LM-W05-T08`; feature area: release; target: 0.1; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Publish approved waves/tasks/dependencies via supported review workflow and read back counts, IDs, release status and actual access instructions..

- Dependencies: LM-W05-T01, LM-W05-T02, LM-W05-T03, LM-W05-T04, LM-W05-T05, LM-W05-T06, LM-W05-T07.

- Acceptance: Publish approved waves/tasks/dependencies via supported review workflow and read back counts, IDs, release status and actual access instructions.

- Origin: owner-authorized narrow outcome; references: lean-model-lab:LM-019, lean-model-lab:LM-021, lean-model-lab:LM-022, lean-model-lab:LM-023, lean-model-lab:LM-024, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Requires real model/quality/output and resource evidence; no planning completion substitutes for runtime, user or public-release proof.

## Wave 6: Arrival and service semantics stay comparable

Horizon: 0.3. Exit evidence: A report contrasts offline and online scopes using matched traces and explains where throughput conclusions fail to transfer. Owner execution disposition, 2026-09-08: unstarted long paced/burst measurements are DEFERRED with frozen definitions retained. Existing implementation/tests remain evidenced; the full serving acceptance is still open.

### LM-W06-T01 — Define offered and achieved load separately

- Project key: `lean-model-lab:LM-W06-T01`; feature area: serving; target: 0.3; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: A workload manifest identifies offered arrivals and accepted/completed rates.

- Dependencies: LM-W04-T08.

- Acceptance: A workload manifest identifies offered arrivals and accepted/completed rates; overload cannot be reported as a lower-load comparison.

- Origin: expanded source requirement; references: lean-model-lab:LM-007, lean-model-lab:LM-011, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

- Recorded evidence: docs/evidence/automated-tests-0.4.json (2026-09-08 local 0.4 progress: Versioned replay stores offered population separately from dispatch/completion; rejection and expiry remain in quality denominators. Replay/evaluation controls passed. Actual paced and overload traces are predeclared but not yet executed.).

### LM-W06-T02 — Support reproducible nonuniform arrivals

- Project key: `lean-model-lab:LM-W06-T02`; feature area: serving; target: 0.3; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: Store deterministic burst/interarrival traces with seed and timestamps.

- Dependencies: LM-W06-T01.

- Acceptance: Store deterministic burst/interarrival traces with seed and timestamps; replay preserves the same arrivals in both arms.

- Origin: expanded source requirement; references: lean-model-lab:LM-007, lean-model-lab:LM-011, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

- Recorded evidence: docs/evidence/automated-tests-0.4.json (2026-09-08 local 0.4 progress: Seeded simultaneous, paced and burst traces regenerate deterministically and both arms share the accepted offsets. Nine workload and eighteen replay controls passed; actual nonuniform measurement remains pending.).

### LM-W06-T03 — Separate client and engine queue intervals

- Project key: `lean-model-lab:LM-W06-T03`; feature area: serving; target: 0.3; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Cross-boundary events carry clock provenance.

- Dependencies: LM-W06-T02.

- Acceptance: Cross-boundary events carry clock provenance; absent engine admission cannot be silently inferred from client send time.

- Origin: expanded source requirement; references: lean-model-lab:LM-007, lean-model-lab:LM-011, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

- Recorded evidence: docs/results/14b-development-20260908.md (2026-09-08 local 0.4 progress: Actual development records preserve client offered/dispatch/chunk/completion timing and clock provenance. Engine admission time remains unavailable and is not inferred from client dispatch. Paced-serving execution remains pending.).

### LM-W06-T04 — Resolve prefill and decode phases

- Project key: `lean-model-lab:LM-W06-T04`; feature area: serving; target: 0.3; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Backend capability probes establish real phase events and synchronization.

- Dependencies: LM-W06-T03.

- Acceptance: Backend capability probes establish real phase events and synchronization; unsupported phase splits remain unavailable.

- Origin: expanded source requirement; references: lean-model-lab:LM-007, lean-model-lab:LM-011, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

- Recorded evidence: docs/results/14b-development-20260908.md (2026-09-08 local 0.4 progress: Actual pinned-native terminal prompt/decode summaries are retained with their limited scope. Engine phase-boundary events and synchronized token-emission timestamps are unavailable; no phase split is fabricated. This does not complete a broad phase capability programme.).

### LM-W06-T05 — Measure streamed inter-token behavior

- Project key: `lean-model-lab:LM-W06-T05`; feature area: serving; target: 0.3; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: Retained token events support ITL/TPOT definitions with zero/one-token cases explicitly handled and no fabricated gaps..

- Dependencies: LM-W06-T04.

- Acceptance: Retained token events support ITL/TPOT definitions with zero/one-token cases explicitly handled and no fabricated gaps.

- Origin: expanded source requirement; references: lean-model-lab:LM-007, lean-model-lab:LM-011, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

- Recorded evidence: docs/evidence/automated-tests-0.4.json (2026-09-08 local 0.4 progress: Client stream metrics preserve observed chunks and explicit zero/one-token cases, progress sentinels and empty-content EOS token distinctions. These are client observations, not proven engine inter-token emission gaps.).

### LM-W06-T06 — Score SLO-qualified goodput

- Project key: `lean-model-lab:LM-W06-T06`; feature area: serving; target: 0.3; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: Only requests satisfying predeclared quality and latency SLOs count as goodput, while all offered requests remain in the denominator ledger..

- Dependencies: LM-W06-T05.

- Acceptance: Only requests satisfying predeclared quality and latency SLOs count as goodput, while all offered requests remain in the denominator ledger.

- Origin: expanded source requirement; references: lean-model-lab:LM-007, lean-model-lab:LM-011, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

- Recorded evidence: docs/evidence/automated-tests-0.4.json (2026-09-08 local 0.4 progress: SLO-qualified counts require exact quality and both predeclared latency conditions; all offered requests remain in the ledger and global ineligibility clears scientific ratios. Actual low-load/saturation campaign remains pending.).

### LM-W06-T07 — Expose saturation and overload failures

- Project key: `lean-model-lab:LM-W06-T07`; feature area: serving; target: 0.3; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: Load sweeps retain rejection, timeout, OOM and tail evidence.

- Dependencies: LM-W06-T06.

- Acceptance: Load sweeps retain rejection, timeout, OOM and tail evidence; the first unstable regime is identified rather than hidden.

- Origin: expanded source requirement; references: lean-model-lab:LM-007, lean-model-lab:LM-011, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

- Recorded evidence: docs/evidence/automated-tests-0.4.json (2026-09-08 local 0.4 progress: Admission overload/deadline/cancellation fixtures retain the offered population and adverse outcomes. Two predeclared real load probes remain pending; they will not constitute a calibrated load sweep or identify the first unstable regime, so broader acceptance remains open.).

### LM-W06-T08 — Publish a serving-semantics comparison

- Project key: `lean-model-lab:LM-W06-T08`; feature area: serving; target: 0.3; status: **IN PROGRESS**; evidence: **IMPLEMENTED**.

- Outcome: A report contrasts offline and online scopes using matched traces and explains where throughput conclusions fail to transfer..

- Dependencies: LM-W06-T01, LM-W06-T02, LM-W06-T03, LM-W06-T04, LM-W06-T05, LM-W06-T06, LM-W06-T07.

- Acceptance: A report contrasts offline and online scopes using matched traces and explains where throughput conclusions fail to transfer.

- Origin: expanded source requirement; references: lean-model-lab:LM-007, lean-model-lab:LM-011, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

- Recorded evidence: docs/decisions/14b-measurement-recipes-01.md (2026-09-08 local 0.4 progress: Report rendering separates queued batch, paced and burst scopes and preserves fixed denominators. Real matched serving observations, full load-frontier acceptance, publication and qualified review remain outstanding.).

## Wave 7: Cache and batching policies expose their true costs

Horizon: later 0.x. Exit evidence: Compare valid policies by quality, memory, full cost and latency strata, retaining workloads where each policy regresses.

### LM-W07-T01 — Define cache ownership and lifecycle

- Project key: `lean-model-lab:LM-W07-T01`; feature area: inference policies; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Document cache key identity, population, reuse and invalidation.

- Dependencies: LM-W06-T08.

- Acceptance: Document cache key identity, population, reuse and invalidation; cross-tokenizer or model reuse is rejected.

- Origin: expanded source requirement; references: lean-model-lab:LM-007, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W07-T02 — Measure cache preparation amortization

- Project key: `lean-model-lab:LM-W07-T02`; feature area: inference policies; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Report preparation cost and break-even requests separately from warm hits.

- Dependencies: LM-W07-T01.

- Acceptance: Report preparation cost and break-even requests separately from warm hits; cold misses remain in total cost.

- Origin: expanded source requirement; references: lean-model-lab:LM-007, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W07-T03 — Compare eviction under memory pressure

- Project key: `lean-model-lab:LM-W07-T03`; feature area: inference policies; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: A bounded trace records evictions, recomputation and quality parity at fixed memory budgets including OOM failures..

- Dependencies: LM-W07-T02.

- Acceptance: A bounded trace records evictions, recomputation and quality parity at fixed memory budgets including OOM failures.

- Origin: expanded source requirement; references: lean-model-lab:LM-007, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W07-T04 — Quantify cache contention at concurrent admission

- Project key: `lean-model-lab:LM-W07-T04`; feature area: inference policies; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Matched concurrent traces expose lock/queue costs and per-request tails.

- Dependencies: LM-W07-T03.

- Acceptance: Matched concurrent traces expose lock/queue costs and per-request tails; shared-cache benefit cannot omit blocked requests.

- Origin: expanded source requirement; references: lean-model-lab:LM-007, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W07-T05 — Compare static and dynamic batching contracts

- Project key: `lean-model-lab:LM-W07-T05`; feature area: inference policies; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Specify admission windows, padding and maximum wait before running equal arrivals and output constraints..

- Dependencies: LM-W07-T04.

- Acceptance: Specify admission windows, padding and maximum wait before running equal arrivals and output constraints.

- Origin: expanded source requirement; references: lean-model-lab:LM-007, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W07-T06 — Measure padding and batch fragmentation

- Project key: `lean-model-lab:LM-W07-T06`; feature area: inference policies; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Report useful versus padding work and batch occupancy without counting padded tokens as achieved output throughput..

- Dependencies: LM-W07-T05.

- Acceptance: Report useful versus padding work and batch occupancy without counting padded tokens as achieved output throughput.

- Origin: expanded source requirement; references: lean-model-lab:LM-007, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W07-T07 — Test cache cancellation and retry integrity

- Project key: `lean-model-lab:LM-W07-T07`; feature area: inference policies; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Cancellation/restart cannot reuse partial invalid state or omit prior preparation cost.

- Dependencies: LM-W07-T06.

- Acceptance: Cancellation/restart cannot reuse partial invalid state or omit prior preparation cost; corrupted entries fail validation.

- Origin: expanded source requirement; references: lean-model-lab:LM-007, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W07-T08 — Publish policy applicability boundaries

- Project key: `lean-model-lab:LM-W07-T08`; feature area: inference policies; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Compare valid policies by quality, memory, full cost and latency strata, retaining workloads where each policy regresses..

- Dependencies: LM-W07-T01, LM-W07-T02, LM-W07-T03, LM-W07-T04, LM-W07-T05, LM-W07-T06, LM-W07-T07.

- Acceptance: Compare valid policies by quality, memory, full cost and latency strata, retaining workloads where each policy regresses.

- Origin: expanded source requirement; references: lean-model-lab:LM-007, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 8: Training starts with a reproducible baseline

Horizon: later 0.x. Exit evidence: Held-out loss, time-to-quality and seed variation regenerate from raw records; nonconvergence remains visible.

### LM-W08-T01 — Freeze lawful training and held-out data

- Project key: `lean-model-lab:LM-W08-T01`; feature area: training baseline; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Pin data provenance, permitted uses, split digests and transformations.

- Dependencies: LM-W02-T08, LM-W04-T08.

- Acceptance: Pin data provenance, permitted uses, split digests and transformations; overlap or ambiguous terms block training admission.

- Origin: expanded source requirement; references: lean-model-lab:LM-005, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W08-T02 — Define exposure and token accounting

- Project key: `lean-model-lab:LM-W08-T02`; feature area: training baseline; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Separate raw, nonpadding and loss-bearing tokens, steps and accumulation.

- Dependencies: LM-W08-T01.

- Acceptance: Separate raw, nonpadding and loss-bearing tokens, steps and accumulation; equivalent data exposure can be verified from run records.

- Origin: expanded source requirement; references: lean-model-lab:LM-005, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W08-T03 — Pin initialization and seed schedule

- Project key: `lean-model-lab:LM-W08-T03`; feature area: training baseline; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Record model initialization, seed list and nondeterminism scope.

- Dependencies: LM-W08-T02.

- Acceptance: Record model initialization, seed list and nondeterminism scope; replay reproduces supported control behavior within declared tolerance.

- Origin: expanded source requirement; references: lean-model-lab:LM-005, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W08-T04 — Freeze optimizer and data order

- Project key: `lean-model-lab:LM-W08-T04`; feature area: training baseline; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Record optimizer state, hyperparameters, shuffling and batching.

- Dependencies: LM-W08-T03.

- Acceptance: Record optimizer state, hyperparameters, shuffling and batching; a hidden schedule change invalidates comparison.

- Origin: expanded source requirement; references: lean-model-lab:LM-005, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W08-T05 — Define held-out target and evaluation cadence

- Project key: `lean-model-lab:LM-W08-T05`; feature area: training baseline; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Set quality target, evaluation intervals and checkpoint-selection rule before execution.

- Dependencies: LM-W08-T04.

- Acceptance: Set quality target, evaluation intervals and checkpoint-selection rule before execution; post-hoc target changes create a new family.

- Origin: expanded source requirement; references: lean-model-lab:LM-005, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W08-T06 — Execute a bounded tiny training control

- Project key: `lean-model-lab:LM-W08-T06`; feature area: training baseline; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Real training reaches or fails the declared target across the fixed seeds with time, memory and all failed work retained..

- Dependencies: LM-W08-T05.

- Acceptance: Real training reaches or fails the declared target across the fixed seeds with time, memory and all failed work retained.

- Origin: expanded source requirement; references: lean-model-lab:LM-005, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W08-T07 — Recover training without exposure ambiguity

- Project key: `lean-model-lab:LM-W08-T07`; feature area: training baseline; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Checkpoint continuation reconciles RNG, optimizer and consumed tokens.

- Dependencies: LM-W08-T06.

- Acceptance: Checkpoint continuation reconciles RNG, optimizer and consumed tokens; incompatible state triggers an accounted restart.

- Origin: expanded source requirement; references: lean-model-lab:LM-005, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W08-T08 — Publish baseline convergence evidence

- Project key: `lean-model-lab:LM-W08-T08`; feature area: training baseline; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Held-out loss, time-to-quality and seed variation regenerate from raw records.

- Dependencies: LM-W08-T01, LM-W08-T02, LM-W08-T03, LM-W08-T04, LM-W08-T05, LM-W08-T06, LM-W08-T07.

- Acceptance: Held-out loss, time-to-quality and seed variation regenerate from raw records; nonconvergence remains visible.

- Origin: expanded source requirement; references: lean-model-lab:LM-005, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 9: Analytical models disclose their calibrated limits

Horizon: later 0.x. Exit evidence: Every simulated result references a model version and calibration envelope with separate measured evidence and invalid extrapolation labels.

### LM-W09-T01 — Version analytical model assumptions

- Project key: `lean-model-lab:LM-W09-T01`; feature area: simulation; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Declare modeled compute, bandwidth, memory and queueing terms with units and applicability.

- Dependencies: LM-W04-T08, LM-W08-T08.

- Acceptance: Declare modeled compute, bandwidth, memory and queueing terms with units and applicability; assumptions are not labeled measurements.

- Origin: expanded source requirement; references: lean-model-lab:LM-006, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W09-T02 — Separate calibration and test evidence

- Project key: `lean-model-lab:LM-W09-T02`; feature area: simulation; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Freeze calibration and held-out workload/device sets.

- Dependencies: LM-W09-T01.

- Acceptance: Freeze calibration and held-out workload/device sets; fitting code cannot consume held-out outcomes.

- Origin: expanded source requirement; references: lean-model-lab:LM-006, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W09-T03 — Calibrate a compute and bandwidth ceiling

- Project key: `lean-model-lab:LM-W09-T03`; feature area: simulation; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Fit roofline parameters to documented measurements with overhead boundaries and residuals, avoiding impossible application-speed claims..

- Dependencies: LM-W09-T02.

- Acceptance: Fit roofline parameters to documented measurements with overhead boundaries and residuals, avoiding impossible application-speed claims.

- Origin: expanded source requirement; references: lean-model-lab:LM-006, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W09-T04 — Model memory capacity and cache demand

- Project key: `lean-model-lab:LM-W09-T04`; feature area: simulation; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Predict weights, activation/cache and overhead memory with explicit unmodeled allocations.

- Dependencies: LM-W09-T03.

- Acceptance: Predict weights, activation/cache and overhead memory with explicit unmodeled allocations; held-out OOM cases test capacity limits.

- Origin: expanded source requirement; references: lean-model-lab:LM-006, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W09-T05 — Calibrate a request queue model

- Project key: `lean-model-lab:LM-W09-T05`; feature area: simulation; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Fit arrival/service assumptions to admitted traces and report where burst or contention behavior violates them..

- Dependencies: LM-W09-T04.

- Acceptance: Fit arrival/service assumptions to admitted traces and report where burst or contention behavior violates them.

- Origin: expanded source requirement; references: lean-model-lab:LM-006, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W09-T06 — Quantify held-out prediction error

- Project key: `lean-model-lab:LM-W09-T06`; feature area: simulation; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Report absolute/relative error by workload and interval coverage, retaining worst cases and failed predictions..

- Dependencies: LM-W09-T05.

- Acceptance: Report absolute/relative error by workload and interval coverage, retaining worst cases and failed predictions.

- Origin: expanded source requirement; references: lean-model-lab:LM-006, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W09-T07 — Propagate parameter uncertainty

- Project key: `lean-model-lab:LM-W09-T07`; feature area: simulation; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Sensitivity/uncertainty analysis identifies predictions unstable under calibration error.

- Dependencies: LM-W09-T06.

- Acceptance: Sensitivity/uncertainty analysis identifies predictions unstable under calibration error; point estimates cannot hide this instability.

- Origin: expanded source requirement; references: lean-model-lab:LM-006, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W09-T08 — Publish simulation-to-measurement correspondence

- Project key: `lean-model-lab:LM-W09-T08`; feature area: simulation; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Every simulated result references a model version and calibration envelope with separate measured evidence and invalid extrapolation labels..

- Dependencies: LM-W09-T01, LM-W09-T02, LM-W09-T03, LM-W09-T04, LM-W09-T05, LM-W09-T06, LM-W09-T07.

- Acceptance: Every simulated result references a model version and calibration envelope with separate measured evidence and invalid extrapolation labels.

- Origin: expanded source requirement; references: lean-model-lab:LM-006, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 10: Packing and checkpointing preserve time to quality

Horizon: later 0.x. Exit evidence: A report identifies lengths, batches and memory limits where each technique helps or regresses with exact supporting evidence.

### LM-W10-T01 — Freeze equivalent training comparisons

- Project key: `lean-model-lab:LM-W10-T01`; feature area: training efficiency; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Bind data exposure, quality target, seeds and evaluation cadence for packing/checkpointing candidates before measurements..

- Dependencies: LM-W08-T08, LM-W09-T08.

- Acceptance: Bind data exposure, quality target, seeds and evaluation cadence for packing/checkpointing candidates before measurements.

- Origin: expanded source requirement; references: lean-model-lab:LM-008, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W10-T02 — Implement sequence packing with semantic masks

- Project key: `lean-model-lab:LM-W10-T02`; feature area: training efficiency; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Packed inputs preserve document boundaries and loss masks.

- Dependencies: LM-W10-T01.

- Acceptance: Packed inputs preserve document boundaries and loss masks; cross-document leakage and missing-token fixtures fail.

- Origin: expanded source requirement; references: lean-model-lab:LM-008, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W10-T03 — Measure packing preparation and waste

- Project key: `lean-model-lab:LM-W10-T03`; feature area: training efficiency; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Account preprocessing, padding saved and loss-bearing tokens without excluding packing setup from full-wall time..

- Dependencies: LM-W10-T02.

- Acceptance: Account preprocessing, padding saved and loss-bearing tokens without excluding packing setup from full-wall time.

- Origin: expanded source requirement; references: lean-model-lab:LM-008, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W10-T04 — Validate checkpoint recomputation correctness

- Project key: `lean-model-lab:LM-W10-T04`; feature area: training efficiency; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Forward/gradient controls compare checkpointed and baseline paths under declared tolerances.

- Dependencies: LM-W10-T03.

- Acceptance: Forward/gradient controls compare checkpointed and baseline paths under declared tolerances; silent state mutation is rejected.

- Origin: expanded source requirement; references: lean-model-lab:LM-008, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W10-T05 — Measure checkpoint memory/time tradeoffs

- Project key: `lean-model-lab:LM-W10-T05`; feature area: training efficiency; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Peak supported memory and recomputation overhead are reported jointly across fixed workloads, including OOM outcomes..

- Dependencies: LM-W10-T04.

- Acceptance: Peak supported memory and recomputation overhead are reported jointly across fixed workloads, including OOM outcomes.

- Origin: expanded source requirement; references: lean-model-lab:LM-008, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W10-T06 — Test interactions with accumulation and RNG

- Project key: `lean-model-lab:LM-W10-T06`; feature area: training efficiency; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Packing/checkpointing preserves effective batch exposure and supported stochastic behavior under gradient accumulation..

- Dependencies: LM-W10-T05.

- Acceptance: Packing/checkpointing preserves effective batch exposure and supported stochastic behavior under gradient accumulation.

- Origin: expanded source requirement; references: lean-model-lab:LM-008, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W10-T07 — Evaluate paired time-to-quality outcomes

- Project key: `lean-model-lab:LM-W10-T07`; feature area: training efficiency; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Compare all seeds at the same frozen quality target including nonconvergence and failed attempts.

- Dependencies: LM-W10-T06.

- Acceptance: Compare all seeds at the same frozen quality target including nonconvergence and failed attempts; fastest-seed selection is rejected.

- Origin: expanded source requirement; references: lean-model-lab:LM-008, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W10-T08 — Publish training efficiency failure boundaries

- Project key: `lean-model-lab:LM-W10-T08`; feature area: training efficiency; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: A report identifies lengths, batches and memory limits where each technique helps or regresses with exact supporting evidence..

- Dependencies: LM-W10-T01, LM-W10-T02, LM-W10-T03, LM-W10-T04, LM-W10-T05, LM-W10-T06, LM-W10-T07.

- Acceptance: A report identifies lengths, batches and memory limits where each technique helps or regresses with exact supporting evidence.

- Origin: expanded source requirement; references: lean-model-lab:LM-008, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 11: Evaluator immutability survives adversarial controls

Horizon: later 0.x. Exit evidence: Version representative gaming/failure fixtures with expected evaluator decisions and demonstrated defect detection coverage.

### LM-W11-T01 — Authenticate complete comparison provenance

- Project key: `lean-model-lab:LM-W11-T01`; feature area: integrity; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Every derived result binds immutable input/evaluator digests.

- Dependencies: LM-W04-T08, LM-W10-T08.

- Acceptance: Every derived result binds immutable input/evaluator digests; substituted files or mismatched parents invalidate evaluation.

- Origin: expanded source requirement; references: lean-model-lab:LM-010, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W11-T02 — Detect tokenizer and template substitutions

- Project key: `lean-model-lab:LM-W11-T02`; feature area: integrity; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Negative controls alter vocabulary, normalization or chat templates and reliably fail equivalent-family admission..

- Dependencies: LM-W11-T01.

- Acceptance: Negative controls alter vocabulary, normalization or chat templates and reliably fail equivalent-family admission.

- Origin: expanded source requirement; references: lean-model-lab:LM-010, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W11-T03 — Detect truncated and selectively omitted outputs

- Project key: `lean-model-lab:LM-W11-T03`; feature area: integrity; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Controls shorten generations or remove hard cases.

- Dependencies: LM-W11-T02.

- Acceptance: Controls shorten generations or remove hard cases; evaluator reports violations and retains the full intended population.

- Origin: expanded source requirement; references: lean-model-lab:LM-010, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W11-T04 — Protect frozen quality thresholds

- Project key: `lean-model-lab:LM-W11-T04`; feature area: integrity; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Changing target, tolerance or evaluation schedule after candidates exist creates a different contract and cannot inherit prior eligibility..

- Dependencies: LM-W11-T03.

- Acceptance: Changing target, tolerance or evaluation schedule after candidates exist creates a different contract and cannot inherit prior eligibility.

- Origin: expanded source requirement; references: lean-model-lab:LM-010, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W11-T05 — Separate candidate and evaluator capabilities

- Project key: `lean-model-lab:LM-W11-T05`; feature area: integrity; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Enforced OS/container/VM tests deny candidates evaluator mutation, credential access and unauthorized network/filesystem access..

- Dependencies: LM-W11-T04.

- Acceptance: Enforced OS/container/VM tests deny candidates evaluator mutation, credential access and unauthorized network/filesystem access.

- Origin: expanded source requirement; references: lean-model-lab:LM-010, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W11-T06 — Validate training data and loss-mask integrity

- Project key: `lean-model-lab:LM-W11-T06`; feature area: integrity; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Controls change exposure, masks or confirmation membership and fail despite improved reported training speed..

- Dependencies: LM-W11-T05.

- Acceptance: Controls change exposure, masks or confirmation membership and fail despite improved reported training speed.

- Origin: expanded source requirement; references: lean-model-lab:LM-010, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W11-T07 — Quarantine invalid imported evidence

- Project key: `lean-model-lab:LM-W11-T07`; feature area: integrity; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Untrusted bundles undergo size, schema, path and provenance checks before parsing/aggregation.

- Dependencies: LM-W11-T06.

- Acceptance: Untrusted bundles undergo size, schema, path and provenance checks before parsing/aggregation; failures remain diagnosable.

- Origin: expanded source requirement; references: lean-model-lab:LM-010, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W11-T08 — Publish an integrity regression corpus

- Project key: `lean-model-lab:LM-W11-T08`; feature area: integrity; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Version representative gaming/failure fixtures with expected evaluator decisions and demonstrated defect detection coverage..

- Dependencies: LM-W11-T01, LM-W11-T02, LM-W11-T03, LM-W11-T04, LM-W11-T05, LM-W11-T06, LM-W11-T07.

- Acceptance: Version representative gaming/failure fixtures with expected evaluator decisions and demonstrated defect detection coverage.

- Origin: expanded source requirement; references: lean-model-lab:LM-010, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 12: Variance and tails determine conclusions

Horizon: later 0.x. Exit evidence: Independent recomputation reproduces intervals and decision labels, including null findings and disagreement among supported estimands.

### LM-W12-T01 — Freeze estimands and experimental units

- Project key: `lean-model-lab:LM-W12-T01`; feature area: statistics; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Specify request-,run- and campaign-level metrics and avoid treating correlated tokens/requests as independent experiments..

- Dependencies: LM-W06-T08, LM-W10-T08, LM-W11-T08.

- Acceptance: Specify request-,run- and campaign-level metrics and avoid treating correlated tokens/requests as independent experiments.

- Origin: expanded source requirement; references: lean-model-lab:LM-011, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W12-T02 — Balance order and cache carryover

- Project key: `lean-model-lab:LM-W12-T02`; feature area: statistics; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Counterbalanced schedules expose arm order and carryover.

- Dependencies: LM-W12-T01.

- Acceptance: Counterbalanced schedules expose arm order and carryover; simulations/controls demonstrate bias detection under injected drift.

- Origin: expanded source requirement; references: lean-model-lab:LM-011, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W12-T03 — Predeclare missingness and outlier treatment

- Project key: `lean-model-lab:LM-W12-T03`; feature area: statistics; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Run exclusions require frozen criteria and remain reported.

- Dependencies: LM-W12-T02.

- Acceptance: Run exclusions require frozen criteria and remain reported; unfavorable samples cannot be removed after inspection.

- Origin: expanded source requirement; references: lean-model-lab:LM-011, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W12-T04 — Estimate paired effects robustly

- Project key: `lean-model-lab:LM-W12-T04`; feature area: statistics; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Paired intervals respect run grouping and report sample count, method and uncertainty when small samples defeat precision..

- Dependencies: LM-W12-T03.

- Acceptance: Paired intervals respect run grouping and report sample count, method and uncertainty when small samples defeat precision.

- Origin: expanded source requirement; references: lean-model-lab:LM-011, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W12-T05 — Quantify tail resolution and instability

- Project key: `lean-model-lab:LM-W12-T05`; feature area: statistics; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: p95/p99 estimates disclose effective sample resolution and uncertainty by stratum instead of unsupported precise tail claims..

- Dependencies: LM-W12-T04.

- Acceptance: p95/p99 estimates disclose effective sample resolution and uncertainty by stratum instead of unsupported precise tail claims.

- Origin: expanded source requirement; references: lean-model-lab:LM-011, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W12-T06 — Control repeated and multiple comparisons

- Project key: `lean-model-lab:LM-W12-T06`; feature area: statistics; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Predeclared stopping and multiplicity rules retain query counts and distinguish exploratory findings from confirmation..

- Dependencies: LM-W12-T05.

- Acceptance: Predeclared stopping and multiplicity rules retain query counts and distinguish exploratory findings from confirmation.

- Origin: expanded source requirement; references: lean-model-lab:LM-011, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W12-T07 — Diagnose thermal/load-driven variation

- Project key: `lean-model-lab:LM-W12-T07`; feature area: statistics; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Link observed load/thermal changes to uncertainty without deleting contaminated runs.

- Dependencies: LM-W12-T06.

- Acceptance: Link observed load/thermal changes to uncertainty without deleting contaminated runs; sensitivity analyses retain all original records.

- Origin: expanded source requirement; references: lean-model-lab:LM-011, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W12-T08 — Publish statistical limitations with findings

- Project key: `lean-model-lab:LM-W12-T08`; feature area: statistics; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Independent recomputation reproduces intervals and decision labels, including null findings and disagreement among supported estimands..

- Dependencies: LM-W12-T01, LM-W12-T02, LM-W12-T03, LM-W12-T04, LM-W12-T05, LM-W12-T06, LM-W12-T07.

- Acceptance: Independent recomputation reproduces intervals and decision labels, including null findings and disagreement among supported estimands.

- Origin: expanded source requirement; references: lean-model-lab:LM-011, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 13: Untouched workloads govern confirmation

Horizon: later 0.x. Exit evidence: Publish access counts, controls, quality decision and applicability without exposing protected/private inputs or claiming universal transfer.

### LM-W13-T01 — Define search and confirmation partitions

- Project key: `lean-model-lab:LM-W13-T01`; feature area: confirmation; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Record lawful split generation, digests and leakage checks.

- Dependencies: LM-W11-T08, LM-W12-T08.

- Acceptance: Record lawful split generation, digests and leakage checks; selected candidates never access confirmation inputs during search.

- Origin: expanded source requirement; references: lean-model-lab:LM-012, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W13-T02 — Enforce protected confirmation execution

- Project key: `lean-model-lab:LM-W13-T02`; feature area: confirmation; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: OS/container/VM probes deny candidate access to hidden evaluator material and credentials.

- Dependencies: LM-W13-T01.

- Acceptance: OS/container/VM probes deny candidate access to hidden evaluator material and credentials; a shared directory alone fails admission.

- Origin: expanded source requirement; references: lean-model-lab:LM-012, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W13-T03 — Reserve a finite confirmation budget

- Project key: `lean-model-lab:LM-W13-T03`; feature area: confirmation; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Account protected accesses, runtime and retries separately within total campaign costs.

- Dependencies: LM-W13-T02.

- Acceptance: Account protected accesses, runtime and retries separately within total campaign costs; exhausted allocation stops evaluation.

- Origin: expanded source requirement; references: lean-model-lab:LM-012, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W13-T04 — Lock candidate and selection rules

- Project key: `lean-model-lab:LM-W13-T04`; feature area: confirmation; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Freeze candidate artifact and selection procedure before confirmation.

- Dependencies: LM-W13-T03.

- Acceptance: Freeze candidate artifact and selection procedure before confirmation; later edits invalidate the confirmation association.

- Origin: expanded source requirement; references: lean-model-lab:LM-012, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W13-T05 — Control checkpoint confirmation access

- Project key: `lean-model-lab:LM-W13-T05`; feature area: confirmation; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Training evaluates a preselected checkpoint or approved sequential rule without feeding intermediate confirmation results back to training..

- Dependencies: LM-W13-T04.

- Acceptance: Training evaluates a preselected checkpoint or approved sequential rule without feeding intermediate confirmation results back to training.

- Origin: expanded source requirement; references: lean-model-lab:LM-012, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W13-T06 — Run untouched workload confirmation

- Project key: `lean-model-lab:LM-W13-T06`; feature area: confirmation; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: A fresh protected attempt evaluates the locked candidate and retains failures, no-gain and reversal outcomes..

- Dependencies: LM-W13-T05.

- Acceptance: A fresh protected attempt evaluates the locked candidate and retains failures, no-gain and reversal outcomes.

- Origin: expanded source requirement; references: lean-model-lab:LM-012, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W13-T07 — Handle confirmation leakage or compromise

- Project key: `lean-model-lab:LM-W13-T07`; feature area: confirmation; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: A tested response invalidates contaminated evidence and identifies a new lawful holdout requirement without recycling exposed material..

- Dependencies: LM-W13-T06.

- Acceptance: A tested response invalidates contaminated evidence and identifies a new lawful holdout requirement without recycling exposed material.

- Origin: expanded source requirement; references: lean-model-lab:LM-012, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W13-T08 — Release scoped confirmation findings

- Project key: `lean-model-lab:LM-W13-T08`; feature area: confirmation; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Publish access counts, controls, quality decision and applicability without exposing protected/private inputs or claiming universal transfer..

- Dependencies: LM-W13-T01, LM-W13-T02, LM-W13-T03, LM-W13-T04, LM-W13-T05, LM-W13-T06, LM-W13-T07.

- Acceptance: Publish access counts, controls, quality decision and applicability without exposing protected/private inputs or claiming universal transfer.

- Origin: expanded source requirement; references: lean-model-lab:LM-012, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 14: Hardware observations have explicit provenance

Horizon: later 0.x. Exit evidence: Each supported environment has actual probe evidence and limitations rather than upstream capability claims masquerading as qualification.

### LM-W14-T01 — Inventory stable device and runtime identity

- Project key: `lean-model-lab:LM-W14-T01`; feature area: hardware measurement; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Record CPU topology, OS, relevant firmware/runtime and numerical settings without publishing secrets or personal machine identifiers..

- Dependencies: LM-W04-T08.

- Acceptance: Record CPU topology, OS, relevant firmware/runtime and numerical settings without publishing secrets or personal machine identifiers.

- Origin: expanded source requirement; references: lean-model-lab:LM-002, lean-model-lab:LM-011, lean-model-lab:LM-012, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W14-T02 — Calibrate timer resolution and overhead

- Project key: `lean-model-lab:LM-W14-T02`; feature area: hardware measurement; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: A probe characterizes monotonic clock resolution and instrumentation cost.

- Dependencies: LM-W14-T01.

- Acceptance: A probe characterizes monotonic clock resolution and instrumentation cost; unsupported sub-resolution intervals are flagged.

- Origin: expanded source requirement; references: lean-model-lab:LM-002, lean-model-lab:LM-011, lean-model-lab:LM-012, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W14-T03 — Verify asynchronous synchronization boundaries

- Project key: `lean-model-lab:LM-W14-T03`; feature area: hardware measurement; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Device/host timing controls show which operations require synchronization and reject mixing unsynchronized event intervals..

- Dependencies: LM-W14-T02.

- Acceptance: Device/host timing controls show which operations require synchronization and reject mixing unsynchronized event intervals.

- Origin: expanded source requirement; references: lean-model-lab:LM-002, lean-model-lab:LM-011, lean-model-lab:LM-012, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W14-T04 — Record concurrent host pressure

- Project key: `lean-model-lab:LM-W14-T04`; feature area: hardware measurement; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Capture bounded load/memory-pressure snapshots for each measured pair while excluding unrelated process secrets and private arguments..

- Dependencies: LM-W14-T03.

- Acceptance: Capture bounded load/memory-pressure snapshots for each measured pair while excluding unrelated process secrets and private arguments.

- Origin: expanded source requirement; references: lean-model-lab:LM-002, lean-model-lab:LM-011, lean-model-lab:LM-012, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W14-T05 — Record thermal and clock capabilities

- Project key: `lean-model-lab:LM-W14-T05`; feature area: hardware measurement; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Probe actual temperature, frequency and throttling support with units/scope.

- Dependencies: LM-W14-T04.

- Acceptance: Probe actual temperature, frequency and throttling support with units/scope; unavailable sensors remain explicit.

- Origin: expanded source requirement; references: lean-model-lab:LM-002, lean-model-lab:LM-011, lean-model-lab:LM-012, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W14-T06 — Measure scoped peak memory

- Project key: `lean-model-lab:LM-W14-T06`; feature area: hardware measurement; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Distinguish process RSS, allocator reservation and device allocation.

- Dependencies: LM-W14-T05.

- Acceptance: Distinguish process RSS, allocator reservation and device allocation; controlled allocations test units and known sampling blind spots.

- Origin: expanded source requirement; references: lean-model-lab:LM-002, lean-model-lab:LM-011, lean-model-lab:LM-012, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W14-T07 — Validate probe failure and permissions

- Project key: `lean-model-lab:LM-W14-T07`; feature area: hardware measurement; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Unsupported devices or denied permissions yield scoped unavailable data without aborting valid unrelated metrics or changing host settings..

- Dependencies: LM-W14-T06.

- Acceptance: Unsupported devices or denied permissions yield scoped unavailable data without aborting valid unrelated metrics or changing host settings.

- Origin: expanded source requirement; references: lean-model-lab:LM-002, lean-model-lab:LM-011, lean-model-lab:LM-012, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W14-T08 — Publish measurement capability matrices

- Project key: `lean-model-lab:LM-W14-T08`; feature area: hardware measurement; target: later 0.x; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Each supported environment has actual probe evidence and limitations rather than upstream capability claims masquerading as qualification..

- Dependencies: LM-W14-T01, LM-W14-T02, LM-W14-T03, LM-W14-T04, LM-W14-T05, LM-W14-T06, LM-W14-T07.

- Acceptance: Each supported environment has actual probe evidence and limitations rather than upstream capability claims masquerading as qualification.

- Origin: expanded source requirement; references: lean-model-lab:LM-002, lean-model-lab:LM-011, lean-model-lab:LM-012, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 15: Energy is measured inside a known boundary

Horizon: long-term. Exit evidence: Raw sensor evidence, method, uncertainty and boundary accompany findings; TDP-based estimates cannot enter the measured-energy column.

### LM-W15-T01 — Admit a sensor with documented scope

- Project key: `lean-model-lab:LM-W15-T01`; feature area: energy; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Review sensor/API permissions, units, counter behavior and sampled-power semantics on authorized hardware before calling readings energy..

- Dependencies: LM-W14-T08.

- Acceptance: Review sensor/API permissions, units, counter behavior and sampled-power semantics on authorized hardware before calling readings energy.

- Origin: expanded source requirement; references: lean-model-lab:LM-002, lean-model-lab:LM-009, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W15-T02 — Validate counter rollover and resets

- Project key: `lean-model-lab:LM-W15-T02`; feature area: energy; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Known wrap/reset cases cannot create negative or implausible integrated energy.

- Dependencies: LM-W15-T01.

- Acceptance: Known wrap/reset cases cannot create negative or implausible integrated energy; discontinuities invalidate affected intervals.

- Origin: expanded source requirement; references: lean-model-lab:LM-002, lean-model-lab:LM-009, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W15-T03 — Synchronize sampling with run envelopes

- Project key: `lean-model-lab:LM-W15-T03`; feature area: energy; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Associate readings to startup, service and evaluation boundaries with timestamp uncertainty and no omitted preparation window..

- Dependencies: LM-W15-T02.

- Acceptance: Associate readings to startup, service and evaluation boundaries with timestamp uncertainty and no omitted preparation window.

- Origin: expanded source requirement; references: lean-model-lab:LM-002, lean-model-lab:LM-009, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W15-T04 — Integrate sampled power with missingness

- Project key: `lean-model-lab:LM-W15-T04`; feature area: energy; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: A testable integration method reports cadence and missing intervals.

- Dependencies: LM-W15-T03.

- Acceptance: A testable integration method reports cadence and missing intervals; unsupported gaps are not silently interpolated into measured totals.

- Origin: expanded source requirement; references: lean-model-lab:LM-002, lean-model-lab:LM-009, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W15-T05 — Separate host and accelerator energy

- Project key: `lean-model-lab:LM-W15-T05`; feature area: energy; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Results label device/system boundaries and avoid adding overlapping sensors or calling accelerator readings whole-system consumption..

- Dependencies: LM-W15-T04.

- Acceptance: Results label device/system boundaries and avoid adding overlapping sensors or calling accelerator readings whole-system consumption.

- Origin: expanded source requirement; references: lean-model-lab:LM-002, lean-model-lab:LM-009, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W15-T06 — Measure idle and instrumentation effects

- Project key: `lean-model-lab:LM-W15-T06`; feature area: energy; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Declare any idle adjustment and retain gross readings.

- Dependencies: LM-W15-T05.

- Acceptance: Declare any idle adjustment and retain gross readings; sensor/profiler overhead experiments bound interpretation.

- Origin: expanded source requirement; references: lean-model-lab:LM-002, lean-model-lab:LM-009, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W15-T07 — Compare energy at fixed quality and work

- Project key: `lean-model-lab:LM-W15-T07`; feature area: energy; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Paired runs retain full requests/training exposure and report energy jointly with latency and quality rather than isolated favorable ratios..

- Dependencies: LM-W15-T06.

- Acceptance: Paired runs retain full requests/training exposure and report energy jointly with latency and quality rather than isolated favorable ratios.

- Origin: expanded source requirement; references: lean-model-lab:LM-002, lean-model-lab:LM-009, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W15-T08 — Publish sensor-qualified energy findings

- Project key: `lean-model-lab:LM-W15-T08`; feature area: energy; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Raw sensor evidence, method, uncertainty and boundary accompany findings.

- Dependencies: LM-W15-T01, LM-W15-T02, LM-W15-T03, LM-W15-T04, LM-W15-T05, LM-W15-T06, LM-W15-T07.

- Acceptance: Raw sensor evidence, method, uncertainty and boundary accompany findings; TDP-based estimates cannot enter the measured-energy column.

- Origin: expanded source requirement; references: lean-model-lab:LM-002, lean-model-lab:LM-009, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 16: Quantization and speculation preserve declared quality

Horizon: long-term. Exit evidence: Independent confirmation reports quality/time/memory tradeoffs and cases where conversion or drafting eliminates any apparent benefit.

### LM-W16-T01 — Freeze quantization comparison semantics

- Project key: `lean-model-lab:LM-W16-T01`; feature area: advanced inference; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Specify baseline/candidate precision, calibration data and quality tolerances as a declared variable rather than an unnoticed identity change..

- Dependencies: LM-W07-T08, LM-W11-T08, LM-W12-T08, LM-W13-T08.

- Acceptance: Specify baseline/candidate precision, calibration data and quality tolerances as a declared variable rather than an unnoticed identity change.

- Origin: expanded source requirement; references: lean-model-lab:LM-013, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W16-T02 — Review quantized artifacts and conversion rights

- Project key: `lean-model-lab:LM-W16-T02`; feature area: advanced inference; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Pin lawful source weights, conversion code/version and generated artifacts with safe-loading and redistribution decisions..

- Dependencies: LM-W16-T01.

- Acceptance: Pin lawful source weights, conversion code/version and generated artifacts with safe-loading and redistribution decisions.

- Origin: expanded source requirement; references: lean-model-lab:LM-013, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W16-T03 — Measure conversion and calibration overhead

- Project key: `lean-model-lab:LM-W16-T03`; feature area: advanced inference; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Account calibration, conversion, load and warmup in full cost and report amortization conditions alongside steady inference..

- Dependencies: LM-W16-T02.

- Acceptance: Account calibration, conversion, load and warmup in full cost and report amortization conditions alongside steady inference.

- Origin: expanded source requirement; references: lean-model-lab:LM-013, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W16-T04 — Evaluate quantized quality by workload stratum

- Project key: `lean-model-lab:LM-W16-T04`; feature area: advanced inference; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Frozen quality tests and numerical controls expose regressions, including long prompts and stop behavior, before performance eligibility..

- Dependencies: LM-W16-T03.

- Acceptance: Frozen quality tests and numerical controls expose regressions, including long prompts and stop behavior, before performance eligibility.

- Origin: expanded source requirement; references: lean-model-lab:LM-013, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W16-T05 — Define speculative decoding equivalence claims

- Project key: `lean-model-lab:LM-W16-T05`; feature area: advanced inference; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Record draft/target models, acceptance algorithm and supported sampling guarantees.

- Dependencies: LM-W16-T04.

- Acceptance: Record draft/target models, acceptance algorithm and supported sampling guarantees; weaker equivalence claims stay explicit.

- Origin: expanded source requirement; references: lean-model-lab:LM-013, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W16-T06 — Account rejected speculation and draft costs

- Project key: `lean-model-lab:LM-W16-T06`; feature area: advanced inference; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Retain draft tokens, rejected work, verification and cache overhead so target-only throughput cannot inflate speedup..

- Dependencies: LM-W16-T05.

- Acceptance: Retain draft tokens, rejected work, verification and cache overhead so target-only throughput cannot inflate speedup.

- Origin: expanded source requirement; references: lean-model-lab:LM-013, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W16-T07 — Stress speculation under variable acceptance

- Project key: `lean-model-lab:LM-W16-T07`; feature area: advanced inference; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Matched traces expose low-acceptance, long-context and concurrency failures with full memory and tail costs..

- Dependencies: LM-W16-T06.

- Acceptance: Matched traces expose low-acceptance, long-context and concurrency failures with full memory and tail costs.

- Origin: expanded source requirement; references: lean-model-lab:LM-013, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W16-T08 — Publish advanced-inference applicability findings

- Project key: `lean-model-lab:LM-W16-T08`; feature area: advanced inference; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Independent confirmation reports quality/time/memory tradeoffs and cases where conversion or drafting eliminates any apparent benefit..

- Dependencies: LM-W16-T01, LM-W16-T02, LM-W16-T03, LM-W16-T04, LM-W16-T05, LM-W16-T06, LM-W16-T07.

- Acceptance: Independent confirmation reports quality/time/memory tradeoffs and cases where conversion or drafting eliminates any apparent benefit.

- Origin: expanded source requirement; references: lean-model-lab:LM-013, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 17: Precision and kernels pass numerical checks

Horizon: long-term. Exit evidence: Report only tested shapes, dtypes and devices with overhead-inclusive results and explicit failure boundaries.

### LM-W17-T01 — Specify numerical reference and tolerance

- Project key: `lean-model-lab:LM-W17-T01`; feature area: numerical methods; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Freeze reference precision, error norms, gradient tolerances and convergence targets before candidate kernel measurements..

- Dependencies: LM-W10-T08, LM-W11-T08, LM-W12-T08, LM-W13-T08.

- Acceptance: Freeze reference precision, error norms, gradient tolerances and convergence targets before candidate kernel measurements.

- Origin: expanded source requirement; references: lean-model-lab:LM-014, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W17-T02 — Review bounded kernel execution admission

- Project key: `lean-model-lab:LM-W17-T02`; feature area: numerical methods; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Pin source/compiler/dependencies and prove required OS/container/VM controls for untrusted kernels without shared-host privilege changes..

- Dependencies: LM-W17-T01.

- Acceptance: Pin source/compiler/dependencies and prove required OS/container/VM controls for untrusted kernels without shared-host privilege changes.

- Origin: expanded source requirement; references: lean-model-lab:LM-014, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W17-T03 — Test forward values on difficult inputs

- Project key: `lean-model-lab:LM-W17-T03`; feature area: numerical methods; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Representative extremes, masking and boundary shapes detect overflow, underflow, NaNs and silently altered semantics..

- Dependencies: LM-W17-T02.

- Acceptance: Representative extremes, masking and boundary shapes detect overflow, underflow, NaNs and silently altered semantics.

- Origin: expanded source requirement; references: lean-model-lab:LM-014, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W17-T04 — Test gradients against trusted controls

- Project key: `lean-model-lab:LM-W17-T04`; feature area: numerical methods; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Finite-difference or reference-gradient checks cover stable cases and expose unsupported nondifferentiable regions explicitly..

- Dependencies: LM-W17-T03.

- Acceptance: Finite-difference or reference-gradient checks cover stable cases and expose unsupported nondifferentiable regions explicitly.

- Origin: expanded source requirement; references: lean-model-lab:LM-014, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W17-T05 — Detect precision and accumulation changes

- Project key: `lean-model-lab:LM-W17-T05`; feature area: numerical methods; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Record operand, accumulator and reduction precision.

- Dependencies: LM-W17-T04.

- Acceptance: Record operand, accumulator and reduction precision; undeclared casts invalidate comparisons even when wall time improves.

- Origin: expanded source requirement; references: lean-model-lab:LM-014, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W17-T06 — Measure compilation and shape specialization

- Project key: `lean-model-lab:LM-W17-T06`; feature area: numerical methods; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Account compile/autotune cost and cache specialization, retaining failures and out-of-envelope shapes..

- Dependencies: LM-W17-T05.

- Acceptance: Account compile/autotune cost and cache specialization, retaining failures and out-of-envelope shapes.

- Origin: expanded source requirement; references: lean-model-lab:LM-014, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W17-T07 — Evaluate numerical stability through training

- Project key: `lean-model-lab:LM-W17-T07`; feature area: numerical methods; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Across fixed seeds, candidate kernels must meet frozen quality targets and retain divergence/nonconvergence evidence..

- Dependencies: LM-W17-T06.

- Acceptance: Across fixed seeds, candidate kernels must meet frozen quality targets and retain divergence/nonconvergence evidence.

- Origin: expanded source requirement; references: lean-model-lab:LM-014, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W17-T08 — Publish kernel speed and correctness envelopes

- Project key: `lean-model-lab:LM-W17-T08`; feature area: numerical methods; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Report only tested shapes, dtypes and devices with overhead-inclusive results and explicit failure boundaries..

- Dependencies: LM-W17-T01, LM-W17-T02, LM-W17-T03, LM-W17-T04, LM-W17-T05, LM-W17-T06, LM-W17-T07.

- Acceptance: Report only tested shapes, dtypes and devices with overhead-inclusive results and explicit failure boundaries.

- Origin: expanded source requirement; references: lean-model-lab:LM-014, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 18: Optimizer comparisons preserve convergence fairness

Horizon: long-term. Exit evidence: Report data/model/precision-specific convergence and cost effects with null and adverse results and exact tuning effort.

### LM-W18-T01 — Freeze optimizer comparison budgets

- Project key: `lean-model-lab:LM-W18-T01`; feature area: optimizers; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Declare fixed-token, fixed-compute or fixed-wall family and quality target.

- Dependencies: LM-W08-T08, LM-W10-T08, LM-W12-T08, LM-W13-T08.

- Acceptance: Declare fixed-token, fixed-compute or fixed-wall family and quality target; switching the budget axis invalidates a paired claim.

- Origin: expanded source requirement; references: lean-model-lab:LM-014, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W18-T02 — Preserve batch exposure and data order

- Project key: `lean-model-lab:LM-W18-T02`; feature area: optimizers; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Optimizer candidates receive equivalent tokens/order/accumulation within declared stochastic controls and recorded exceptions..

- Dependencies: LM-W18-T01.

- Acceptance: Optimizer candidates receive equivalent tokens/order/accumulation within declared stochastic controls and recorded exceptions.

- Origin: expanded source requirement; references: lean-model-lab:LM-014, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W18-T03 — Record optimizer state and memory overhead

- Project key: `lean-model-lab:LM-W18-T03`; feature area: optimizers; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Include state tensors, updates, initialization and serialization cost with supported peak-memory measurements..

- Dependencies: LM-W18-T02.

- Acceptance: Include state tensors, updates, initialization and serialization cost with supported peak-memory measurements.

- Origin: expanded source requirement; references: lean-model-lab:LM-014, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W18-T04 — Define equal tuning allocations

- Project key: `lean-model-lab:LM-W18-T04`; feature area: optimizers; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Baseline and candidates receive the same predeclared search effort.

- Dependencies: LM-W18-T03.

- Acceptance: Baseline and candidates receive the same predeclared search effort; failed hyperparameter trials stay in campaign costs.

- Origin: expanded source requirement; references: lean-model-lab:LM-014, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W18-T05 — Validate update numerics and recovery

- Project key: `lean-model-lab:LM-W18-T05`; feature area: optimizers; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Reference steps and resumed checkpoints detect unstable updates, lost moments or incompatible optimizer state..

- Dependencies: LM-W18-T04.

- Acceptance: Reference steps and resumed checkpoints detect unstable updates, lost moments or incompatible optimizer state.

- Origin: expanded source requirement; references: lean-model-lab:LM-014, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W18-T06 — Measure full time to quality across seeds

- Project key: `lean-model-lab:LM-W18-T06`; feature area: optimizers; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Retain target crossings, evaluation overhead, divergence and nonconvergence rather than comparing selected final checkpoints..

- Dependencies: LM-W18-T05.

- Acceptance: Retain target crossings, evaluation overhead, divergence and nonconvergence rather than comparing selected final checkpoints.

- Origin: expanded source requirement; references: lean-model-lab:LM-014, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W18-T07 — Confirm selected optimizer settings untouched

- Project key: `lean-model-lab:LM-W18-T07`; feature area: optimizers; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Locked settings run against protected confirmation under the same target and budget.

- Dependencies: LM-W18-T06.

- Acceptance: Locked settings run against protected confirmation under the same target and budget; reversals invalidate broad benefit claims.

- Origin: expanded source requirement; references: lean-model-lab:LM-014, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W18-T08 — Publish optimizer applicability boundaries

- Project key: `lean-model-lab:LM-W18-T08`; feature area: optimizers; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Report data/model/precision-specific convergence and cost effects with null and adverse results and exact tuning effort..

- Dependencies: LM-W18-T01, LM-W18-T02, LM-W18-T03, LM-W18-T04, LM-W18-T05, LM-W18-T06, LM-W18-T07.

- Acceptance: Report data/model/precision-specific convergence and cost effects with null and adverse results and exact tuning effort.

- Origin: expanded source requirement; references: lean-model-lab:LM-014, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 19: Distributed models account for communication

Horizon: long-term. Exit evidence: Per-topology evidence compares predictions and authorized runs with uncertainty and no pooled superiority claim.

### LM-W19-T01 — Define simulated distributed topology

- Project key: `lean-model-lab:LM-W19-T01`; feature area: distributed execution; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Version device, link, placement and communication assumptions.

- Dependencies: LM-W09-T08, LM-W11-T08, LM-W14-T08.

- Acceptance: Version device, link, placement and communication assumptions; simulated outputs cannot be labeled real hardware measurements.

- Origin: expanded source requirement; references: lean-model-lab:LM-015, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W19-T02 — Model collective communication costs

- Project key: `lean-model-lab:LM-W19-T02`; feature area: distributed execution; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Calibrated latency/bandwidth terms include message sizes and topology with held-out prediction error..

- Dependencies: LM-W19-T01.

- Acceptance: Calibrated latency/bandwidth terms include message sizes and topology with held-out prediction error.

- Origin: expanded source requirement; references: lean-model-lab:LM-015, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W19-T03 — Model memory partition and replication

- Project key: `lean-model-lab:LM-W19-T03`; feature area: distributed execution; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Explicitly account weights, optimizer, activation/cache and replicated state.

- Dependencies: LM-W19-T02.

- Acceptance: Explicitly account weights, optimizer, activation/cache and replicated state; infeasible per-device memory invalidates a configuration.

- Origin: expanded source requirement; references: lean-model-lab:LM-015, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W19-T04 — Represent stragglers and synchronization

- Project key: `lean-model-lab:LM-W19-T04`; feature area: distributed execution; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Simulated service distributions expose barriers, skew and tail sensitivity instead of assuming identical workers..

- Dependencies: LM-W19-T03.

- Acceptance: Simulated service distributions expose barriers, skew and tail sensitivity instead of assuming identical workers.

- Origin: expanded source requirement; references: lean-model-lab:LM-015, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W19-T05 — Review real distributed resource admission

- Project key: `lean-model-lab:LM-W19-T05`; feature area: distributed execution; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Obtain exact hardware/network/allocation approval and dependency/isolation evidence before any remote or multi-device run..

- Dependencies: LM-W19-T04.

- Acceptance: Obtain exact hardware/network/allocation approval and dependency/isolation evidence before any remote or multi-device run.

- Origin: expanded source requirement; references: lean-model-lab:LM-015, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W19-T06 — Measure approved communication and compute overlap

- Project key: `lean-model-lab:LM-W19-T06`; feature area: distributed execution; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Real events distinguish synchronization, transfer and useful work.

- Dependencies: LM-W19-T05.

- Acceptance: Real events distinguish synchronization, transfer and useful work; unsupported overlap inference remains unavailable.

- Origin: expanded source requirement; references: lean-model-lab:LM-015, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W19-T07 — Reconcile distributed failures and partial work

- Project key: `lean-model-lab:LM-W19-T07`; feature area: distributed execution; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Worker loss, retries and timeout records retain every consumed allocation and prevent duplicate logical completion..

- Dependencies: LM-W19-T06.

- Acceptance: Worker loss, retries and timeout records retain every consumed allocation and prevent duplicate logical completion.

- Origin: expanded source requirement; references: lean-model-lab:LM-015, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W19-T08 — Publish separate simulation and hardware findings

- Project key: `lean-model-lab:LM-W19-T08`; feature area: distributed execution; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Per-topology evidence compares predictions and authorized runs with uncertainty and no pooled superiority claim..

- Dependencies: LM-W19-T01, LM-W19-T02, LM-W19-T03, LM-W19-T04, LM-W19-T05, LM-W19-T06, LM-W19-T07.

- Acceptance: Per-topology evidence compares predictions and authorized runs with uncertainty and no pooled superiority claim.

- Origin: expanded source requirement; references: lean-model-lab:LM-015, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 20: Profiler evidence motivates falsifiable hypotheses

Horizon: long-term. Exit evidence: A searchable record links predictions, experiments and contrary evidence; unsupported causal explanations remain explicitly speculative.

### LM-W20-T01 — Admit a bounded diagnostic profile

- Project key: `lean-model-lab:LM-W20-T01`; feature area: profiling; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Freeze profiler scope, source/runtime identity and overhead limits.

- Dependencies: LM-W16-T08, LM-W17-T08, LM-W19-T08.

- Acceptance: Freeze profiler scope, source/runtime identity and overhead limits; diagnostic timings stay distinct from benchmark timings.

- Origin: expanded source requirement; references: lean-model-lab:LM-016, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W20-T02 — Attribute observed bottlenecks to phases

- Project key: `lean-model-lab:LM-W20-T02`; feature area: profiling; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Raw trace references support named compute, memory, queue or communication constraints and expose unobserved regions..

- Dependencies: LM-W20-T01.

- Acceptance: Raw trace references support named compute, memory, queue or communication constraints and expose unobserved regions.

- Origin: expanded source requirement; references: lean-model-lab:LM-016, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W20-T03 — Measure profiler perturbation

- Project key: `lean-model-lab:LM-W20-T03`; feature area: profiling; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Paired instrumented/uninstrumented controls quantify tracing overhead before using the trace to explain performance..

- Dependencies: LM-W20-T02.

- Acceptance: Paired instrumented/uninstrumented controls quantify tracing overhead before using the trace to explain performance.

- Origin: expanded source requirement; references: lean-model-lab:LM-016, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W20-T04 — Produce a single-change hypothesis contract

- Project key: `lean-model-lab:LM-W20-T04`; feature area: profiling; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Each proposed change names observed bottleneck, expected mechanism, quality risk, predicted effect and a falsifier..

- Dependencies: LM-W20-T03.

- Acceptance: Each proposed change names observed bottleneck, expected mechanism, quality risk, predicted effect and a falsifier.

- Origin: expanded source requirement; references: lean-model-lab:LM-016, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W20-T05 — Check analytical plausibility of predicted effects

- Project key: `lean-model-lab:LM-W20-T05`; feature area: profiling; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Calibrated ceilings and capacity models bound proposed gains without treating predictions as measured results..

- Dependencies: LM-W20-T04.

- Acceptance: Calibrated ceilings and capacity models bound proposed gains without treating predictions as measured results.

- Origin: expanded source requirement; references: lean-model-lab:LM-016, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W20-T06 — Review hypothesis permissions and resource needs

- Project key: `lean-model-lab:LM-W20-T06`; feature area: profiling; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Reject proposals that cross evaluator authority, require unavailable hardware or exceed finite experiment allocations..

- Dependencies: LM-W20-T05.

- Acceptance: Reject proposals that cross evaluator authority, require unavailable hardware or exceed finite experiment allocations.

- Origin: expanded source requirement; references: lean-model-lab:LM-016, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W20-T07 — Prioritize diagnostic experiments by information

- Project key: `lean-model-lab:LM-W20-T07`; feature area: profiling; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Choose bounded experiments that distinguish competing mechanisms with predefined interpretation rather than chasing noisy fastest runs..

- Dependencies: LM-W20-T06.

- Acceptance: Choose bounded experiments that distinguish competing mechanisms with predefined interpretation rather than chasing noisy fastest runs.

- Origin: expanded source requirement; references: lean-model-lab:LM-016, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W20-T08 — Record supported and refuted hypotheses

- Project key: `lean-model-lab:LM-W20-T08`; feature area: profiling; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: A searchable record links predictions, experiments and contrary evidence.

- Dependencies: LM-W20-T01, LM-W20-T02, LM-W20-T03, LM-W20-T04, LM-W20-T05, LM-W20-T06, LM-W20-T07.

- Acceptance: A searchable record links predictions, experiments and contrary evidence; unsupported causal explanations remain explicitly speculative.

- Origin: expanded source requirement; references: lean-model-lab:LM-016, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 21: Search methods share equal experiment budgets

Horizon: exploratory. Exit evidence: Compare fixed/agent search under the frozen budget and publish no-benefit or failure findings without treating exploratory scope as promised delivery.

### LM-W21-T01 — Specify fixed and agent-guided search arms

- Project key: `lean-model-lab:LM-W21-T01`; feature area: discovery; target: exploratory; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Predeclare search spaces, objective/guardrail vector and baseline method.

- Dependencies: LM-W13-T08, LM-W20-T08.

- Acceptance: Predeclare search spaces, objective/guardrail vector and baseline method; agent proposal ability does not establish useful optimization.

- Origin: exploratory proposal; references: lean-model-lab:LM-017, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W21-T02 — Enforce a shared budget ledger

- Project key: `lean-model-lab:LM-W21-T02`; feature area: discovery; target: exploratory; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: All proposals, evaluations, failures and confirmation allocations consume comparable finite compute/attempt resources..

- Dependencies: LM-W21-T01.

- Acceptance: All proposals, evaluations, failures and confirmation allocations consume comparable finite compute/attempt resources.

- Origin: exploratory proposal; references: lean-model-lab:LM-017, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W21-T03 — Isolate search execution and evaluator authority

- Project key: `lean-model-lab:LM-W21-T03`; feature area: discovery; target: exploratory; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: OS/container/VM probes prevent agent/candidate modification of evaluator, holdouts, credentials and resource ceilings..

- Dependencies: LM-W21-T02.

- Acceptance: OS/container/VM probes prevent agent/candidate modification of evaluator, holdouts, credentials and resource ceilings.

- Origin: exploratory proposal; references: lean-model-lab:LM-017, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W21-T04 — Record complete proposal and trial history

- Project key: `lean-model-lab:LM-W21-T04`; feature area: discovery; target: exploratory; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Retain invalid, rejected, failed and worse candidates with cost and provenance rather than publishing only selected winners..

- Dependencies: LM-W21-T03.

- Acceptance: Retain invalid, rejected, failed and worse candidates with cost and provenance rather than publishing only selected winners.

- Origin: exploratory proposal; references: lean-model-lab:LM-017, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W21-T05 — Separate search randomness from benchmark noise

- Project key: `lean-model-lab:LM-W21-T05`; feature area: discovery; target: exploratory; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Repeat search seeds and measured pairs with a design that distinguishes optimizer variance from execution variance..

- Dependencies: LM-W21-T04.

- Acceptance: Repeat search seeds and measured pairs with a design that distinguishes optimizer variance from execution variance.

- Origin: exploratory proposal; references: lean-model-lab:LM-017, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W21-T06 — Compute constrained Pareto sets honestly

- Project key: `lean-model-lab:LM-W21-T06`; feature area: discovery; target: exploratory; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Only comparable quality-valid candidates enter dominance calculations.

- Dependencies: LM-W21-T05.

- Acceptance: Only comparable quality-valid candidates enter dominance calculations; missing metrics cannot silently act as ideal zero costs.

- Origin: exploratory proposal; references: lean-model-lab:LM-017, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W21-T07 — Confirm locked search selections

- Project key: `lean-model-lab:LM-W21-T07`; feature area: discovery; target: exploratory; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Use reserved untouched confirmation once selection is frozen, counting all search and confirmation cost in the final comparison..

- Dependencies: LM-W21-T06.

- Acceptance: Use reserved untouched confirmation once selection is frozen, counting all search and confirmation cost in the final comparison.

- Origin: exploratory proposal; references: lean-model-lab:LM-017, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W21-T08 — Decide whether agent guidance earns continued scope

- Project key: `lean-model-lab:LM-W21-T08`; feature area: discovery; target: exploratory; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Compare fixed/agent search under the frozen budget and publish no-benefit or failure findings without treating exploratory scope as promised delivery..

- Dependencies: LM-W21-T01, LM-W21-T02, LM-W21-T03, LM-W21-T04, LM-W21-T05, LM-W21-T06, LM-W21-T07.

- Acceptance: Compare fixed/agent search under the frozen budget and publish no-benefit or failure findings without treating exploratory scope as promised delivery.

- Origin: exploratory proposal; references: lean-model-lab:LM-017, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 22: Recipes survive independent confirmation

Horizon: long-term. Exit evidence: Package exact settings and contrary evidence with scope-specific confirmation status and actionable reproduction instructions.

### LM-W22-T01 — Define a recipe applicability envelope

- Project key: `lean-model-lab:LM-W22-T01`; feature area: robust recipes; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Bind model/tokenizer/workload/hardware/runtime and failure conditions so a recipe cannot imply universal benefit..

- Dependencies: LM-W13-T08, LM-W16-T08, LM-W18-T08.

- Acceptance: Bind model/tokenizer/workload/hardware/runtime and failure conditions so a recipe cannot imply universal benefit.

- Origin: expanded source requirement; references: lean-model-lab:LM-018, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W22-T02 — Select recipes without confirmation feedback

- Project key: `lean-model-lab:LM-W22-T02`; feature area: robust recipes; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Predeclare quality/performance tradeoff preferences and choose using development evidence with complete selection history..

- Dependencies: LM-W22-T01.

- Acceptance: Predeclare quality/performance tradeoff preferences and choose using development evidence with complete selection history.

- Origin: expanded source requirement; references: lean-model-lab:LM-018, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W22-T03 — Lock recipe configuration and artifact digests

- Project key: `lean-model-lab:LM-W22-T03`; feature area: robust recipes; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Changes after selection create a new recipe revision and cannot retain the old confirmation status..

- Dependencies: LM-W22-T02.

- Acceptance: Changes after selection create a new recipe revision and cannot retain the old confirmation status.

- Origin: expanded source requirement; references: lean-model-lab:LM-018, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W22-T04 — Repeat confirmation in a fresh process

- Project key: `lean-model-lab:LM-W22-T04`; feature area: robust recipes; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: A separately initialized run reproduces supported direction/quality or records reversal while retaining startup and retry costs..

- Dependencies: LM-W22-T03.

- Acceptance: A separately initialized run reproduces supported direction/quality or records reversal while retaining startup and retry costs.

- Origin: expanded source requirement; references: lean-model-lab:LM-018, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W22-T05 — Ablate interactions in combined recipes

- Project key: `lean-model-lab:LM-W22-T05`; feature area: robust recipes; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: When combinations are proposed, compare constituent changes under matched budgets and expose harmful interactions..

- Dependencies: LM-W22-T04.

- Acceptance: When combinations are proposed, compare constituent changes under matched budgets and expose harmful interactions.

- Origin: expanded source requirement; references: lean-model-lab:LM-018, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W22-T06 — Test boundary workloads and resource exhaustion

- Project key: `lean-model-lab:LM-W22-T06`; feature area: robust recipes; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Inputs near supported context/memory/time bounds produce explicit limitations and preserve invalid/failure records..

- Dependencies: LM-W22-T05.

- Acceptance: Inputs near supported context/memory/time bounds produce explicit limitations and preserve invalid/failure records.

- Origin: expanded source requirement; references: lean-model-lab:LM-018, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W22-T07 — Have an independent reviewer assess robustness

- Project key: `lean-model-lab:LM-W22-T07`; feature area: robust recipes; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Record qualified review of raw evidence, quality, costs and applicability without substituting agent opinion for participant evidence..

- Dependencies: LM-W22-T06.

- Acceptance: Record qualified review of raw evidence, quality, costs and applicability without substituting agent opinion for participant evidence.

- Origin: expanded source requirement; references: lean-model-lab:LM-018, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W22-T08 — Publish recipes including non-transferring outcomes

- Project key: `lean-model-lab:LM-W22-T08`; feature area: robust recipes; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Package exact settings and contrary evidence with scope-specific confirmation status and actionable reproduction instructions..

- Dependencies: LM-W22-T01, LM-W22-T02, LM-W22-T03, LM-W22-T04, LM-W22-T05, LM-W22-T06, LM-W22-T07.

- Acceptance: Package exact settings and contrary evidence with scope-specific confirmation status and actionable reproduction instructions.

- Origin: expanded source requirement; references: lean-model-lab:LM-018, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 23: Researchers inspect tradeoffs accessibly

Horizon: long-term. Exit evidence: Real participants can explain eligibility, limitations and reproduction path; record observed confusion and fixes independently of click tests.

### LM-W23-T01 — Design read-only comparison navigation

- Project key: `lean-model-lab:LM-W23-T01`; feature area: workbench; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Users locate a comparison, its frozen contract, raw evidence and limitations without invoking computation or changing scientific state..

- Dependencies: LM-W12-T08, LM-W22-T08.

- Acceptance: Users locate a comparison, its frozen contract, raw evidence and limitations without invoking computation or changing scientific state.

- Origin: expanded source requirement; references: lean-model-lab:LM-019, owner-launch:2026-09-07:section-5, lean-model-lab:LM-009.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W23-T02 — Present quality before performance eligibility

- Project key: `lean-model-lab:LM-W23-T02`; feature area: workbench; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: The interface explains each valid/invalid quality decision and prevents failed candidates appearing as unqualified winners..

- Dependencies: LM-W23-T01.

- Acceptance: The interface explains each valid/invalid quality decision and prevents failed candidates appearing as unqualified winners.

- Origin: expanded source requirement; references: lean-model-lab:LM-019, owner-launch:2026-09-07:section-5, lean-model-lab:LM-009.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W23-T03 — Compare complete metric vectors

- Project key: `lean-model-lab:LM-W23-T03`; feature area: workbench; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Accessible tables show quality, time, tails, memory, energy availability and full costs with units and denominators..

- Dependencies: LM-W23-T02.

- Acceptance: Accessible tables show quality, time, tails, memory, energy availability and full costs with units and denominators.

- Origin: expanded source requirement; references: lean-model-lab:LM-019, owner-launch:2026-09-07:section-5, lean-model-lab:LM-009.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W23-T04 — Trace rendered values back to artifacts

- Project key: `lean-model-lab:LM-W23-T04`; feature area: workbench; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Every plotted/table value resolves to raw run/attempt IDs and aggregation identity, including failed and excluded samples..

- Dependencies: LM-W23-T03.

- Acceptance: Every plotted/table value resolves to raw run/attempt IDs and aggregation identity, including failed and excluded samples.

- Origin: expanded source requirement; references: lean-model-lab:LM-019, owner-launch:2026-09-07:section-5, lean-model-lab:LM-009.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W23-T05 — Separate simulated, estimated and measured views

- Project key: `lean-model-lab:LM-W23-T05`; feature area: workbench; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Textual labels and filters preserve result classes without relying on color or silently combining incompatible numbers..

- Dependencies: LM-W23-T04.

- Acceptance: Textual labels and filters preserve result classes without relying on color or silently combining incompatible numbers.

- Origin: expanded source requirement; references: lean-model-lab:LM-019, owner-launch:2026-09-07:section-5, lean-model-lab:LM-009.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W23-T06 — Support keyboard and narrow-screen inspection

- Project key: `lean-model-lab:LM-W23-T06`; feature area: workbench; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Focus order, labels, zoom, horizontal table handling and error states pass automated checks and recorded manual review..

- Dependencies: LM-W23-T05.

- Acceptance: Focus order, labels, zoom, horizontal table handling and error states pass automated checks and recorded manual review.

- Origin: expanded source requirement; references: lean-model-lab:LM-019, owner-launch:2026-09-07:section-5, lean-model-lab:LM-009.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W23-T07 — Inspect uncertainty and device-specific tradeoffs

- Project key: `lean-model-lab:LM-W23-T07`; feature area: workbench; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Users can compare strata/devices without pooling away regressions and can see sample sizes and uncertainty on each claim..

- Dependencies: LM-W23-T06.

- Acceptance: Users can compare strata/devices without pooling away regressions and can see sample sizes and uncertainty on each claim.

- Origin: expanded source requirement; references: lean-model-lab:LM-019, owner-launch:2026-09-07:section-5, lean-model-lab:LM-009.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W23-T08 — Validate the researcher interpretation workflow

- Project key: `lean-model-lab:LM-W23-T08`; feature area: workbench; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Real participants can explain eligibility, limitations and reproduction path.

- Dependencies: LM-W23-T01, LM-W23-T02, LM-W23-T03, LM-W23-T04, LM-W23-T05, LM-W23-T06, LM-W23-T07.

- Acceptance: Real participants can explain eligibility, limitations and reproduction path; record observed confusion and fixes independently of click tests.

- Origin: expanded source requirement; references: lean-model-lab:LM-019, owner-launch:2026-09-07:section-5, lean-model-lab:LM-009.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 24: Workers enforce bounded resources and recovery

Horizon: long-term. Exit evidence: Worker loss, network loss and coordinator restart preserve monotonic budgets and clear continuation-versus-restart semantics.

### LM-W24-T01 — Define worker leases and admission capabilities

- Project key: `lean-model-lab:LM-W24-T01`; feature area: workers; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Jobs bind exact approved device/input identities, expiry and finite resource reservations.

- Dependencies: LM-W11-T08, LM-W14-T08, LM-W19-T08.

- Acceptance: Jobs bind exact approved device/input identities, expiry and finite resource reservations; incompatible workers cannot accept them.

- Origin: expanded source requirement; references: lean-model-lab:LM-020, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W24-T02 — Enforce OS-level process and memory limits

- Project key: `lean-model-lab:LM-W24-T02`; feature area: workers; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Representative runaway processes cannot exceed admitted limits or raise their own quotas.

- Dependencies: LM-W24-T01.

- Acceptance: Representative runaway processes cannot exceed admitted limits or raise their own quotas; best-effort app checks are insufficient.

- Origin: expanded source requirement; references: lean-model-lab:LM-020, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W24-T03 — Enforce storage and wall-time ceilings

- Project key: `lean-model-lab:LM-W24-T03`; feature area: workers; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Disk-filling and stalled jobs stop within declared policy while retaining diagnostics and consumed cost without affecting siblings..

- Dependencies: LM-W24-T02.

- Acceptance: Disk-filling and stalled jobs stop within declared policy while retaining diagnostics and consumed cost without affecting siblings.

- Origin: expanded source requirement; references: lean-model-lab:LM-020, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W24-T04 — Deny undeclared network and credential access

- Project key: `lean-model-lab:LM-W24-T04`; feature area: workers; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Isolation probes show approved read-only inputs and bounded outputs with no inherited provider/release credentials..

- Dependencies: LM-W24-T03.

- Acceptance: Isolation probes show approved read-only inputs and bounded outputs with no inherited provider/release credentials.

- Origin: expanded source requirement; references: lean-model-lab:LM-020, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W24-T05 — Make cancellation durable across process failure

- Project key: `lean-model-lab:LM-W24-T05`; feature area: workers; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Persist stop intent, terminate only the owned group and reconcile terminal state after coordinator or worker interruption..

- Dependencies: LM-W24-T04.

- Acceptance: Persist stop intent, terminate only the owned group and reconcile terminal state after coordinator or worker interruption.

- Origin: expanded source requirement; references: lean-model-lab:LM-020, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W24-T06 — Prevent duplicate execution publication

- Project key: `lean-model-lab:LM-W24-T06`; feature area: workers; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Idempotent submission/lease tests ensure retries cannot publish two terminal results for one logical attempt..

- Dependencies: LM-W24-T05.

- Acceptance: Idempotent submission/lease tests ensure retries cannot publish two terminal results for one logical attempt.

- Origin: expanded source requirement; references: lean-model-lab:LM-020, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W24-T07 — Quarantine and validate remote output

- Project key: `lean-model-lab:LM-W24-T07`; feature area: workers; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Schema, path, size, provenance and evaluator checks reject corrupted worker artifacts before entering accepted evidence..

- Dependencies: LM-W24-T06.

- Acceptance: Schema, path, size, provenance and evaluator checks reject corrupted worker artifacts before entering accepted evidence.

- Origin: expanded source requirement; references: lean-model-lab:LM-020, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W24-T08 — Demonstrate bounded recovery under injected faults

- Project key: `lean-model-lab:LM-W24-T08`; feature area: workers; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Worker loss, network loss and coordinator restart preserve monotonic budgets and clear continuation-versus-restart semantics..

- Dependencies: LM-W24-T01, LM-W24-T02, LM-W24-T03, LM-W24-T04, LM-W24-T05, LM-W24-T06, LM-W24-T07.

- Acceptance: Worker loss, network loss and coordinator restart preserve monotonic budgets and clear continuation-versus-restart semantics.

- Origin: expanded source requirement; references: lean-model-lab:LM-020, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 25: Portable bundles retain exact lawful conditions

Horizon: long-term. Exit evidence: Record tested OS/runtime combinations and recovery/inspection limitations from actual artifacts rather than upstream support lists.

### LM-W25-T01 — Version the portable recipe schema

- Project key: `lean-model-lab:LM-W25-T01`; feature area: portable artifacts; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Define compatible manifests for inputs, evaluator, environment and attempts with clear migrations and unsupported-version errors..

- Dependencies: LM-W22-T08, LM-W24-T08.

- Acceptance: Define compatible manifests for inputs, evaluator, environment and attempts with clear migrations and unsupported-version errors.

- Origin: expanded source requirement; references: lean-model-lab:LM-021, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W25-T02 — Resolve lawful artifact retrieval separately from bundling

- Project key: `lean-model-lab:LM-W25-T02`; feature area: portable artifacts; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Every nonredistributable model/data asset has a tested exact public acquisition route and rights notice instead of unlawful inclusion..

- Dependencies: LM-W25-T01.

- Acceptance: Every nonredistributable model/data asset has a tested exact public acquisition route and rights notice instead of unlawful inclusion.

- Origin: expanded source requirement; references: lean-model-lab:LM-021, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W25-T03 — Bundle complete provenance and negative evidence

- Project key: `lean-model-lab:LM-W25-T03`; feature area: portable artifacts; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Include configuration digests, raw traces, evaluation and failures while sanitizing secrets, private prompts and local identifying paths..

- Dependencies: LM-W25-T02.

- Acceptance: Include configuration digests, raw traces, evaluation and failures while sanitizing secrets, private prompts and local identifying paths.

- Origin: expanded source requirement; references: lean-model-lab:LM-021, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W25-T04 — Verify bundle integrity and atomic construction

- Project key: `lean-model-lab:LM-W25-T04`; feature area: portable artifacts; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Checksums, parent links and atomic writes detect corruption and partial exports.

- Dependencies: LM-W25-T03.

- Acceptance: Checksums, parent links and atomic writes detect corruption and partial exports; unknown executable content cannot auto-run.

- Origin: expanded source requirement; references: lean-model-lab:LM-021, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W25-T05 — Inspect bundles without credentials or backend

- Project key: `lean-model-lab:LM-W25-T05`; feature area: portable artifacts; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: A clean reader validates and explains evidence and limitations without model downloads or private accounts..

- Dependencies: LM-W25-T04.

- Acceptance: A clean reader validates and explains evidence and limitations without model downloads or private accounts.

- Origin: expanded source requirement; references: lean-model-lab:LM-021, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W25-T06 — Replay supported computations in a fresh environment

- Project key: `lean-model-lab:LM-W25-T06`; feature area: portable artifacts; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Exact runtime prerequisites and lawful inputs reproduce supported calculations while device-specific timings remain separate..

- Dependencies: LM-W25-T05.

- Acceptance: Exact runtime prerequisites and lawful inputs reproduce supported calculations while device-specific timings remain separate.

- Origin: expanded source requirement; references: lean-model-lab:LM-021, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W25-T07 — Preserve evidence through schema migration

- Project key: `lean-model-lab:LM-W25-T07`; feature area: portable artifacts; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Migration creates a derived artifact with original bytes/hashes retained.

- Dependencies: LM-W25-T06.

- Acceptance: Migration creates a derived artifact with original bytes/hashes retained; it cannot revise historical acceptance or raw measurements.

- Origin: expanded source requirement; references: lean-model-lab:LM-021, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W25-T08 — Publish cross-environment bundle compatibility evidence

- Project key: `lean-model-lab:LM-W25-T08`; feature area: portable artifacts; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Record tested OS/runtime combinations and recovery/inspection limitations from actual artifacts rather than upstream support lists..

- Dependencies: LM-W25-T01, LM-W25-T02, LM-W25-T03, LM-W25-T04, LM-W25-T05, LM-W25-T06, LM-W25-T07.

- Acceptance: Record tested OS/runtime combinations and recovery/inspection limitations from actual artifacts rather than upstream support lists.

- Origin: expanded source requirement; references: lean-model-lab:LM-021, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 26: Cross-device comparisons preserve regressions

Horizon: long-term. Exit evidence: State which recipes transfer, fail or remain inconclusive within tested environments and retain contrary evidence and capability limits.

### LM-W26-T01 — Define an eligible replication family

- Project key: `lean-model-lab:LM-W26-T01`; feature area: replication; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Record which model/tokenizer/workload semantics must match and which hardware/backend differences create distinct result groups..

- Dependencies: LM-W14-T08, LM-W25-T08.

- Acceptance: Record which model/tokenizer/workload semantics must match and which hardware/backend differences create distinct result groups.

- Origin: expanded source requirement; references: lean-model-lab:LM-022, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W26-T02 — Admit the second environment explicitly

- Project key: `lean-model-lab:LM-W26-T02`; feature area: replication; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Review actual hardware capability, backend rights/dependencies and finite resource allocation before claiming supported replication..

- Dependencies: LM-W26-T01.

- Acceptance: Review actual hardware capability, backend rights/dependencies and finite resource allocation before claiming supported replication.

- Origin: expanded source requirement; references: lean-model-lab:LM-022, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W26-T03 — Probe cross-backend output and stop semantics

- Project key: `lean-model-lab:LM-W26-T03`; feature area: replication; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Equivalent sampling, token accounting and output constraints pass controls or comparisons are labeled nonequivalent..

- Dependencies: LM-W26-T02.

- Acceptance: Equivalent sampling, token accounting and output constraints pass controls or comparisons are labeled nonequivalent.

- Origin: expanded source requirement; references: lean-model-lab:LM-022, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W26-T04 — Execute matched real replication attempts

- Project key: `lean-model-lab:LM-W26-T04`; feature area: replication; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: The second device/backend runs the fixed quality-constrained recipe with all requests, failures and full overhead retained..

- Dependencies: LM-W26-T03.

- Acceptance: The second device/backend runs the fixed quality-constrained recipe with all requests, failures and full overhead retained.

- Origin: expanded source requirement; references: lean-model-lab:LM-022, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W26-T05 — Compare per-device quality and performance separately

- Project key: `lean-model-lab:LM-W26-T05`; feature area: replication; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Reports expose each environment's paired effects and uncertainty without averaging away a regression..

- Dependencies: LM-W26-T04.

- Acceptance: Reports expose each environment's paired effects and uncertainty without averaging away a regression.

- Origin: expanded source requirement; references: lean-model-lab:LM-022, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W26-T06 — Diagnose non-transfer using observed evidence

- Project key: `lean-model-lab:LM-W26-T06`; feature area: replication; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Tie differences to supported runtime/cache/measurement observations and distinguish causal hypotheses from demonstrated mechanisms..

- Dependencies: LM-W26-T05.

- Acceptance: Tie differences to supported runtime/cache/measurement observations and distinguish causal hypotheses from demonstrated mechanisms.

- Origin: expanded source requirement; references: lean-model-lab:LM-022, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W26-T07 — Reproduce packaging and recovery on the second device

- Project key: `lean-model-lab:LM-W26-T07`; feature area: replication; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: A fresh public-artifact workflow including interruption validates supported operation independently of identical speed..

- Dependencies: LM-W26-T06.

- Acceptance: A fresh public-artifact workflow including interruption validates supported operation independently of identical speed.

- Origin: expanded source requirement; references: lean-model-lab:LM-022, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W26-T08 — Publish honest transfer and failure findings

- Project key: `lean-model-lab:LM-W26-T08`; feature area: replication; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: State which recipes transfer, fail or remain inconclusive within tested environments and retain contrary evidence and capability limits..

- Dependencies: LM-W26-T01, LM-W26-T02, LM-W26-T03, LM-W26-T04, LM-W26-T05, LM-W26-T06, LM-W26-T07.

- Acceptance: State which recipes transfer, fail or remain inconclusive within tested environments and retain contrary evidence and capability limits.

- Origin: expanded source requirement; references: lean-model-lab:LM-022, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 27: Measurement review governs supported releases

Horizon: long-term. Exit evidence: Use review findings, reproduction gaps and resource evidence to choose the next outcome; postpone unsupported scale and exploratory promises.

### LM-W27-T01 — Establish qualified measurement review criteria

- Project key: `lean-model-lab:LM-W27-T01`; feature area: governance; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Reviewers assess quality, request/exposure completeness, overhead, uncertainty and reproducibility against a fixed rubric with conflicts disclosed..

- Dependencies: LM-W23-T08, LM-W26-T08.

- Acceptance: Reviewers assess quality, request/exposure completeness, overhead, uncertainty and reproducibility against a fixed rubric with conflicts disclosed.

- Origin: expanded source requirement; references: lean-model-lab:LM-023, lean-model-lab:LM-024, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W27-T02 — Audit representative raw-to-report claims

- Project key: `lean-model-lab:LM-W27-T02`; feature area: governance; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: An independent reviewer recomputes selected positive and adverse results and records concrete discrepancies and dispositions..

- Dependencies: LM-W27-T01.

- Acceptance: An independent reviewer recomputes selected positive and adverse results and records concrete discrepancies and dispositions.

- Origin: expanded source requirement; references: lean-model-lab:LM-023, lean-model-lab:LM-024, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W27-T03 — Review lawful distribution and notices

- Project key: `lean-model-lab:LM-W27-T03`; feature area: governance; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Audit source, dependency, model, dataset and fixture rights separately and block artifacts with unresolved redistribution conditions..

- Dependencies: LM-W27-T02.

- Acceptance: Audit source, dependency, model, dataset and fixture rights separately and block artifacts with unresolved redistribution conditions.

- Origin: expanded source requirement; references: lean-model-lab:LM-023, lean-model-lab:LM-024, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W27-T04 — Record supported environment release evidence

- Project key: `lean-model-lab:LM-W27-T04`; feature area: governance; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Every claimed environment links to packaged real execution, recovery, limitations and actual participant observations where required..

- Dependencies: LM-W27-T03.

- Acceptance: Every claimed environment links to packaged real execution, recovery, limitations and actual participant observations where required.

- Origin: expanded source requirement; references: lean-model-lab:LM-023, lean-model-lab:LM-024, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W27-T05 — Maintain correction and retraction provenance

- Project key: `lean-model-lab:LM-W27-T05`; feature area: governance; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: A tested correction workflow preserves original artifacts and links superseding findings without erasing failed or invalidated claims..

- Dependencies: LM-W27-T04.

- Acceptance: A tested correction workflow preserves original artifacts and links superseding findings without erasing failed or invalidated claims.

- Origin: expanded source requirement; references: lean-model-lab:LM-023, lean-model-lab:LM-024, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W27-T06 — Reconcile native plan and repository status

- Project key: `lean-model-lab:LM-W27-T06`; feature area: governance; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Read back platform IDs, dependency order, wave counts and evidence statuses.

- Dependencies: LM-W27-T05.

- Acceptance: Read back platform IDs, dependency order, wave counts and evidence statuses; partial publication is resumed idempotently after reconciliation.

- Origin: expanded source requirement; references: lean-model-lab:LM-023, lean-model-lab:LM-024, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W27-T07 — Publish a maintainer-approved bounded preview

- Project key: `lean-model-lab:LM-W27-T07`; feature area: governance; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Release exact reviewed artifacts and limitations through authorized destinations with public access verified from a fresh environment..

- Dependencies: LM-W27-T06.

- Acceptance: Release exact reviewed artifacts and limitations through authorized destinations with public access verified from a fresh environment.

- Origin: expanded source requirement; references: lean-model-lab:LM-023, lean-model-lab:LM-024, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

### LM-W27-T08 — Decide the next evidence-driven scope increment

- Project key: `lean-model-lab:LM-W27-T08`; feature area: governance; target: long-term; status: **PLANNED**; evidence: **NOT TESTED**.

- Outcome: Use review findings, reproduction gaps and resource evidence to choose the next outcome.

- Dependencies: LM-W27-T01, LM-W27-T02, LM-W27-T03, LM-W27-T04, LM-W27-T05, LM-W27-T06, LM-W27-T07.

- Acceptance: Use review findings, reproduction gaps and resource evidence to choose the next outcome; postpone unsupported scale and exploratory promises.

- Origin: expanded source requirement; references: lean-model-lab:LM-023, lean-model-lab:LM-024, owner-launch:2026-09-07:section-5.

- Risk/evidence needs: Wave exit needs retained raw evidence, falsifiers, exact applicability and required qualified review; resource/dependency adoption remains gated.

## Wave 28: Reviewed recipes become reproducible local experiments

Horizon: 0.2. Exit evidence: Package exact recipe, source/runtime identities, full offered population, actual model observations, adverse attempts, replay checks and runbook; report a scoped gain/null/failure according to the frozen rules and label the artifact local until public and external gates are independently satisfied.

### LM-W28-T01 — Freeze a selected CPU recipe independently of legacy constants

- Project key: `lean-model-lab:LM-W28-T01`; feature area: configurable CPU recipes; target: 0.2; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: An accepted v2 manifest binds a reviewed multi-file model profile, tokenizer/template, runtime settings, evaluation plan and one finite allocation.

- Dependencies: LM-W01-T08, LM-W02-T08, LM-W03-T08.

- Acceptance: Reject unreviewed artifacts, missing shard identities, incompatible tokenizer/template settings and resource values beyond the specific owner allocation; a model name or version label cannot authorize execution.

- Origin: owner-authorized bounded successor; references: lean-model-lab:LM-001, lean-model-lab:LM-002, owner-launch:2026-09-07:section-5, lean-model-lab:LM-004, lean-model-lab:LM-007, lean-model-lab:LM-010, lean-model-lab:LM-020, owner-scope:2026-09-08:0.4.

- Risk/evidence needs: Bounded inference-only successor. Generalizes reviewed local CPU recipe identity only; does not reopen the original 0.1 comparison or admit arbitrary backends, remote model code or training. Software tests, real model observations, human interpretation and public/external access are separate evidence levels. See docs/decisions/0.4-scope.md.

- Recorded evidence: docs/results/14b-development-20260908.md (2026-09-08 local 0.4 progress: All eight reviewed FP16 shards and the actual backend were verified; the v2 development archive executed 32 requests under the original finite allocation. Profile/config rejection controls passed. Measurement campaign and prerequisite exits remain open.).

### LM-W28-T02 — Regenerate bounded v2 synthetic recipe populations

- Project key: `lean-model-lab:LM-W28-T02`; feature area: configurable CPU recipes; target: 0.2; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: A strict generator reproduces the complete key-copy population, relative arrivals, output limit and concurrency modes from an inert versioned recipe.

- Dependencies: LM-W28-T01.

- Acceptance: Validate 4..1024 requests in multiples of four, the original four filler strata and exact-answer rule, 32..128 output tokens, bounded seed, simultaneous/paced/burst offsets, resolved queue/deadline controls and sorted unique concurrency modes; canonical regeneration rejects changed prompts, answers, fields and numeric types while default request bytes match v1.

- Origin: owner-authorized bounded successor; references: lean-model-lab:LM-001, lean-model-lab:LM-002, owner-launch:2026-09-07:section-5, lean-model-lab:LM-003, lean-model-lab:LM-010, owner-scope:2026-09-08:0.4.

- Risk/evidence needs: Bounded inference-only successor. Only the reviewed synthetic family is configurable; no arbitrary private prompts, held-out data protection or relaxed historical quality thresholds are introduced. Software tests, real model observations, human interpretation and public/external access are separate evidence levels. See docs/decisions/0.4-scope.md.

- Recorded evidence: tests/test_workloads.py (2026-09-08 bounded leaf execution: 9 workload-module tests passed with PYTHONPATH=src python3 -m unittest discover -s tests -p test_workloads.py -v. Determinism, population/arrival controls and rejection cases only; no v2 integration, scheduling, inference or release proof. Three original test_contracts.py tests also passed.); docs/evidence/automated-tests-0.4.json (2026-09-08 local 0.4 progress: Nine generator controls passed in the integrated 200-test measurement freeze; actual v2 development regenerated and executed its 8-request population in each of four arms. This does not establish the complete measurement population or broad workload quality.).

### LM-W28-T03 — Dispatch recipe versions without weakening historical validation

- Project key: `lean-model-lab:LM-W28-T03`; feature area: configurable CPU recipes; target: 0.2; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: CLI and validators select an explicit workload/config schema and continue to interpret frozen v1 evidence under its original contract.

- Dependencies: LM-W28-T02.

- Acceptance: Unknown versions and mixed config/workload identities fail closed; old immutable config, workload and attempt bytes regenerate identical v1 report outcomes; v2 changes require a new accepted manifest rather than mutation of a running study.

- Origin: owner-authorized bounded successor; references: lean-model-lab:LM-003, lean-model-lab:LM-010, owner-launch:2026-09-07:section-5, owner-scope:2026-09-08:0.4.

- Risk/evidence needs: Bounded inference-only successor. Compatibility covers the admitted local v1/v2 inference formats; general portable-schema migration and external environment support remain broad future tasks. Software tests, real model observations, human interpretation and public/external access are separate evidence levels. See docs/decisions/0.4-scope.md.

- Recorded evidence: docs/results/14b-development-20260908.md (2026-09-08 local 0.4 progress: Three retained v1 canonical reports re-evaluate to their original digests. Actual v2 development/recovery used explicit schemas; unknown/mixed identity controls passed. Historical bytes remain retained.).

### LM-W28-T04 — Use one frozen paired schedule across run and resume

- Project key: `lean-model-lab:LM-W28-T04`; feature area: configurable CPU recipes; target: 0.2; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: Execution, reservation, evaluation and recovery share configurable concurrency and an even 2..8-pair AB/BA schedule from the same accepted contract.

- Dependencies: LM-W28-T03.

- Acceptance: Reject incompatible modes, pair counts, token limits and arm order before launch; interruption resumes missing cells with fresh attempt IDs and retains every predecessor charge without resetting the allocation.

- Origin: owner-authorized bounded successor; references: lean-model-lab:LM-004, lean-model-lab:LM-007, owner-launch:2026-09-07:section-5, lean-model-lab:LM-010, lean-model-lab:LM-020, lean-model-lab:LM-009, lean-model-lab:LM-011, lean-model-lab:LM-021, owner-scope:2026-09-08:0.4.

- Risk/evidence needs: Bounded inference-only successor. A single reviewed CPU coordinator remains authoritative; no parallel heavy jobs, distributed leases or unrestricted candidate execution. Software tests, real model observations, human interpretation and public/external access are separate evidence levels. See docs/decisions/0.4-scope.md.

- Recorded evidence: docs/evidence/14b-recovery-verification.json (2026-09-08 local 0.4 progress: Real v2 AB/BA development and kill/reconcile/resume control completed; replacement attempts have new IDs, predecessor observations persist and allocation costs continue. Full measurement schedule is still running.).

### LM-W28-T05 — Reconcile selected profile settings with native observations

- Project key: `lean-model-lab:LM-W28-T05`; feature area: configurable CPU recipes; target: 0.2; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: The admitted runtime recipe resolves to actual native arguments, tokenizer IDs, slot inventory and terminal generation settings.

- Dependencies: LM-W28-T04.

- Acceptance: Probe the exact model/backend/profile combination; reject unexpected actual settings or slots, preserve valid nonterminal sentinels and EOS IDs, exclude only validated progress placeholders, and record unsupported engine telemetry as unavailable.

- Origin: owner-authorized bounded successor; references: lean-model-lab:LM-004, lean-model-lab:LM-007, owner-launch:2026-09-07:section-5, lean-model-lab:LM-010, lean-model-lab:LM-020, owner-scope:2026-09-08:0.4.

- Risk/evidence needs: Bounded inference-only successor. This is model-specific native protocol verification, not a claim of cross-backend equivalence or engine-internal timestamps. Software tests, real model observations, human interpretation and public/external access are separate evidence levels. See docs/decisions/0.4-scope.md.

- Recorded evidence: docs/results/14b-development-20260908.md (2026-09-08 local 0.4 progress: 32 actual development responses passed native readback and raw replay; first-shard inventory records 57 shard tensors and 579 total tensors. Unsupported engine admission and token-emission clocks remain unavailable.).

### LM-W28-T06 — Separate development feasibility from frozen v2 measurement

- Project key: `lean-model-lab:LM-W28-T06`; feature area: configurable CPU recipes; target: 0.2; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: Model-specific feasibility observations inform a declared recipe before the paired campaign is frozen, with all prior work retained.

- Dependencies: LM-W28-T05.

- Acceptance: Keep development outcomes and costs identifiable; freeze the selected 14B FP16 recipe and quality/output rules before paired execution; preserve failed quality or parity and do not select a favorable rerun as confirmation.

- Origin: owner-authorized bounded successor; references: lean-model-lab:LM-001, lean-model-lab:LM-002, owner-launch:2026-09-07:section-5, lean-model-lab:LM-009, lean-model-lab:LM-010, lean-model-lab:LM-011, lean-model-lab:LM-020, lean-model-lab:LM-004, lean-model-lab:LM-007, lean-model-lab:LM-021, owner-scope:2026-09-08:0.4.

- Risk/evidence needs: Bounded inference-only successor. A development/control versus measured-campaign boundary is not protected holdout confirmation, a general language benchmark or an efficiency guarantee. Software tests, real model observations, human interpretation and public/external access are separate evidence levels. See docs/decisions/0.4-scope.md.

- Recorded evidence: docs/decisions/14b-measurement-recipes-01.md (2026-09-08 local 0.4 progress: Development is always ineligible; three prospective measurement recipes and the producer archive were frozen before measurement. Same-recipe prior measurement, including changed implementations, blocks a favorable rerun; automatic local predecessor discovery and cost union controls passed. Final campaign findings remain pending.).

### LM-W28-T07 — Prove new-recipe interruption and legacy readback together

- Project key: `lean-model-lab:LM-W28-T07`; feature area: configurable CPU recipes; target: 0.2; status: **IN PROGRESS**; evidence: **RUNTIME VERIFIED**.

- Outcome: The packaged v2 runtime survives an owned-process interruption while the frozen v1 artifacts remain independently readable.

- Dependencies: LM-W28-T06.

- Acceptance: Under the new allocation, exercise real interruption, cleanup, reconciliation and restart using the frozen v2 package; verify distinct attempt IDs, unchanged predecessor observations and monotonic costs, and independently re-evaluate retained v1 evidence without loading either model.

- Origin: owner-authorized bounded successor; references: lean-model-lab:LM-004, lean-model-lab:LM-007, owner-launch:2026-09-07:section-5, lean-model-lab:LM-010, lean-model-lab:LM-020, lean-model-lab:LM-019, lean-model-lab:LM-021, lean-model-lab:LM-022, lean-model-lab:LM-023, lean-model-lab:LM-024, lean-model-lab:LM-003, owner-scope:2026-09-08:0.4.

- Risk/evidence needs: Bounded inference-only successor. Local same-boot recovery is verified separately from public distribution, cross-boot recovery and external reproduction. Software tests, real model observations, human interpretation and public/external access are separate evidence levels. See docs/decisions/0.4-scope.md.

- Recorded evidence: docs/evidence/14b-recovery-verification.json (2026-09-08 local 0.4 progress: Actual SIGKILL retained 2 requests, guarded backend cleanup succeeded, an intentional torn journal was retained/rebuilt, and a new attempt completed 8 requests before final cancellation/reconciliation. Original attempt digest and v1 canonical readback were preserved. This is local runtime evidence; prerequisite and qualified gates remain open.).

### LM-W28-T08 — Assemble a useful local 0.2 recipe result

- Project key: `lean-model-lab:LM-W28-T08`; feature area: configurable CPU recipes; target: 0.2; status: **IN PROGRESS**; evidence: **IMPLEMENTED**.

- Outcome: A local researcher can choose a reviewed recipe, validate it, execute the admitted pair schedule, inspect quality-first results and resume interrupted work.

- Dependencies: LM-W28-T07, LM-W28-T01, LM-W28-T02, LM-W28-T03, LM-W28-T04, LM-W28-T05, LM-W28-T06.

- Acceptance: Package exact recipe, source/runtime identities, full offered population, actual model observations, adverse attempts, replay checks and runbook; report a scoped gain/null/failure according to the frozen rules and label the artifact local until public and external gates are independently satisfied.

- Origin: owner-authorized bounded successor; references: lean-model-lab:LM-001, lean-model-lab:LM-002, owner-launch:2026-09-07:section-5, lean-model-lab:LM-004, lean-model-lab:LM-007, lean-model-lab:LM-010, lean-model-lab:LM-020, lean-model-lab:LM-009, lean-model-lab:LM-011, lean-model-lab:LM-021, lean-model-lab:LM-019, lean-model-lab:LM-022, lean-model-lab:LM-023, lean-model-lab:LM-024, owner-scope:2026-09-08:0.4.

- Risk/evidence needs: Bounded inference-only successor. This bounded local 0.2 exit does not complete public 0.1 publication, human validation, the native Tanduna programme or broader recipe confirmation. Software tests, real model observations, human interpretation and public/external access are separate evidence levels. See docs/decisions/0.4-scope.md.

- Recorded evidence: docs/RUNBOOK-0.4.md (2026-09-08 local 0.4 progress: The packaged recipe-to-report workflow and 12 isolated archive checks are available; development and recovery are observed. Complete prespecified measurements, final evidence package and local integrated exit are pending.).

## Wave 29: Researchers audit compatible CPU evidence without running models

Horizon: 0.4. Exit evidence: Demonstrate the integrated 0.2 to 0.3 to 0.4 workflow using exact local artifacts and actual observations; preserve original v1/v2 evidence, quality failures and complete costs; list unresolved public, qualified-human and external-reproduction gates instead of marking a public release complete.

### LM-W29-T01 — Validate finalized CPU bundles before offline inspection

- Project key: `lean-model-lab:LM-W29-T01`; feature area: offline evidence workbench; target: 0.4; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: An inert local import boundary checks inventory, version and derivative provenance before any bundle contributes to a comparison view.

- Dependencies: LM-W28-T08, LM-W06-T08.

- Acceptance: Reject incomplete, modified, oversized, symlinked, traversal-bearing or unsupported bundles without executing content or loading models; distinguish verified byte consistency from independently authenticated observations.

- Origin: owner-authorized bounded successor; references: lean-model-lab:LM-019, owner-launch:2026-09-07:section-5, lean-model-lab:LM-009, lean-model-lab:LM-021, owner-scope:2026-09-08:0.4.

- Risk/evidence needs: Bounded inference-only successor. Read-only support for reviewed local CPU v1/v2 bundles only; broad portable recipes, remote worker quarantine and external authenticity are not claimed. Software tests, real model observations, human interpretation and public/external access are separate evidence levels. See docs/decisions/0.4-scope.md.

- Recorded evidence: docs/evidence/automated-tests-0.4.json (2026-09-08 local 0.4 progress: Sixteen workbench controls cover inert validated imports, corrupt/incomplete/oversized identities, symlinks and raw consistency. Final multi-study v2 catalog verification remains pending.).

### LM-W29-T02 — Group offline comparisons by compatible recipe family

- Project key: `lean-model-lab:LM-W29-T02`; feature area: offline evidence workbench; target: 0.4; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: Catalog navigation keeps model/tokenizer/workload/evaluator and device applicability visible before presenting paired results.

- Dependencies: LM-W29-T01.

- Acceptance: Compatible-family checks separate changed models, templates, arrivals, quality rules and hardware; users can inspect unlike families side by side without pooled speedup, implicit ranking or erased negative outcomes.

- Origin: owner-authorized bounded successor; references: lean-model-lab:LM-019, owner-launch:2026-09-07:section-5, lean-model-lab:LM-009, owner-scope:2026-09-08:0.4.

- Risk/evidence needs: Bounded inference-only successor. This is read-only comparison of recorded local evidence, not protected recipe selection, cross-device synthesis or constrained search. Software tests, real model observations, human interpretation and public/external access are separate evidence levels. See docs/decisions/0.4-scope.md.

- Recorded evidence: docs/evidence/automated-tests-0.4.json (2026-09-08 local 0.4 progress: Strict family identity and no-pooled-ratio controls passed; actual legacy catalog preserves unlike and adverse studies. Complete 14B plus legacy catalog remains pending.).

### LM-W29-T03 — Explain request-level disagreement from retained records

- Project key: `lean-model-lab:LM-W29-T03`; feature area: offline evidence workbench; target: 0.4; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: A researcher can trace an eligibility failure to exact request IDs, expected/output text, token identities, stop conditions and relevant timing records.

- Dependencies: LM-W29-T02.

- Acceptance: Injected and actual quality, prompt/token parity, truncation, missing-request and admission failures resolve to their source attempt/request records; excluded progress placeholders and real empty-content EOS tokens remain correctly distinguished.

- Origin: owner-authorized bounded successor; references: lean-model-lab:LM-019, owner-launch:2026-09-07:section-5, lean-model-lab:LM-009, lean-model-lab:LM-021, owner-scope:2026-09-08:0.4.

- Risk/evidence needs: Bounded inference-only successor. Explanations show observable discrepancies; they do not invent a numerical, cache or scheduling cause or disclose undeclared private prompts. Software tests, real model observations, human interpretation and public/external access are separate evidence levels. See docs/decisions/0.4-scope.md.

- Recorded evidence: docs/evidence/automated-tests-0.4.json (2026-09-08 local 0.4 progress: Fixtures and actual retained legacy evidence resolve quality/token disagreement to request details. Final v2 admission/serving rows and integrated browser review remain pending.).

### LM-W29-T04 — Keep queued-batch and paced-serving interpretations distinct

- Project key: `lean-model-lab:LM-W29-T04`; feature area: offline evidence workbench; target: 0.4; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: Offline reports expose offered, accepted and completed populations with quality and latency-qualified goodput only where the recipe declares the necessary SLOs.

- Dependencies: LM-W29-T03.

- Acceptance: Render historical finite batches and v2 paced/burst workloads with their own denominators and timing boundaries; unknown engine times and ineligible ratios remain unavailable; every displayed value links to its aggregation and source records.

- Origin: owner-authorized bounded successor; references: lean-model-lab:LM-007, lean-model-lab:LM-011, owner-launch:2026-09-07:section-5, lean-model-lab:LM-019, lean-model-lab:LM-009, owner-scope:2026-09-08:0.4.

- Risk/evidence needs: Bounded inference-only successor. No inferred engine queue, per-token emission clock, unmeasured online-service claim or pooled denominator is introduced by presentation. Software tests, real model observations, human interpretation and public/external access are separate evidence levels. See docs/decisions/0.4-scope.md.

- Recorded evidence: docs/evidence/automated-tests-0.4.json (2026-09-08 local 0.4 progress: Fixture rendering and v2 report controls preserve serving denominators, unavailable times and ineligible ratios. Final actual paced/burst catalog remains pending.).

### LM-W29-T05 — Expose inherited costs and scoped probe evidence in the reader

- Project key: `lean-model-lab:LM-W29-T05`; feature area: offline evidence workbench; target: 0.4; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: The inspector separates attempt costs, inherited allocation history, idle wall and measured or unavailable device probes without double charging shared ancestors.

- Dependencies: LM-W29-T04.

- Acceptance: Show each cost/probe scope and provenance; distinguish process high-water RSS from sampled aggregate memory and unavailable energy/thermal telemetry; comparisons retain failed/recovery work and private operational identifiers do not enter public-review output.

- Origin: owner-authorized bounded successor; references: lean-model-lab:LM-002, lean-model-lab:LM-011, lean-model-lab:LM-012, owner-launch:2026-09-07:section-5, lean-model-lab:LM-019, lean-model-lab:LM-009, owner-scope:2026-09-08:0.4.

- Risk/evidence needs: Bounded inference-only successor. Consumes recorded CPU probe evidence only; it does not complete hardware calibration, asynchronous device measurement, sensor admission or energy measurement. Software tests, real model observations, human interpretation and public/external access are separate evidence levels. See docs/decisions/0.4-scope.md.

- Recorded evidence: docs/evidence/automated-tests-0.4.json (2026-09-08 local 0.4 progress: Costs, failed attempts, shared ancestors and unavailable probe scopes are preserved in workbench controls and retained legacy catalog. Final actual catalog/export privacy review remains pending.).

### LM-W29-T06 — Produce portable inert inspection artifacts from the catalog

- Project key: `lean-model-lab:LM-W29-T06`; feature area: offline evidence workbench; target: 0.4; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: A model-free export contains navigable HTML and machine-readable findings linked to exact local bundle identities and any documented redaction derivation.

- Dependencies: LM-W29-T05.

- Acceptance: Inspection needs no credentials, server or model download; generated content escapes untrusted text, performs no executable import, preserves scientific values and labels changed metadata/hash chains as derived evidence with originals retained.

- Origin: owner-authorized bounded successor; references: lean-model-lab:LM-019, owner-launch:2026-09-07:section-5, lean-model-lab:LM-009, lean-model-lab:LM-021, owner-scope:2026-09-08:0.4.

- Risk/evidence needs: Bounded inference-only successor. Local export is not publication or broad cross-environment migration; no weights or native backend binaries are redistributed. Software tests, real model observations, human interpretation and public/external access are separate evidence levels. See docs/decisions/0.4-scope.md.

- Recorded evidence: docs/evidence/automated-tests-0.4.json (2026-09-08 local 0.4 progress: Standalone escaped HTML/JSON exports and original scientific report preservation passed controls; fresh development, recovery and three legacy derivatives were generated. Final all-study package remains pending.).

### LM-W29-T07 — Verify offline navigation and rejection paths on actual artifacts

- Project key: `lean-model-lab:LM-W29-T07`; feature area: offline evidence workbench; target: 0.4; status: **IN PROGRESS**; evidence: **AUTOMATED PASS**.

- Outcome: The local workbench has reproducible import controls and recorded browser interaction evidence for supported inspection paths.

- Dependencies: LM-W29-T06.

- Acceptance: Run corruption/incompatibility and raw-to-render controls; verify keyboard navigation, focus, zoom and narrow layouts on actual generated artifacts; retain failures and report unavailable human/external observations separately from software checks.

- Origin: owner-authorized bounded successor; references: lean-model-lab:LM-019, owner-launch:2026-09-07:section-5, lean-model-lab:LM-009, lean-model-lab:LM-021, owner-scope:2026-09-08:0.4.

- Risk/evidence needs: Bounded inference-only successor. Browser controls establish software usability evidence; they cannot substitute for qualified researcher interpretation or fresh external public-artifact execution. Software tests, real model observations, human interpretation and public/external access are separate evidence levels. See docs/decisions/0.4-scope.md.

- Recorded evidence: docs/review/workbench-accessibility.md (2026-09-08 local 0.4 progress: Actual legacy catalog was checked in a sandboxed browser for keyboard filtering/details/reset/zero state, 375px reflow and separately labelled 200% content enlargement. Native 200% zoom was separately demonstrated on a tiny control page (docs/evidence/browser-0.4-native-zoom.json); its final v2 artifact application remains pending; no human or accessibility certification is claimed.).

### LM-W29-T08 — Assemble the local 0.4 researcher evidence workflow

- Project key: `lean-model-lab:LM-W29-T08`; feature area: offline evidence workbench; target: 0.4; status: **IN PROGRESS**; evidence: **IMPLEMENTED**.

- Outcome: A reviewable local package supports recipe selection, admitted arrival replay and auditable offline comparison with an explicit version and remaining-gates record.

- Dependencies: LM-W29-T07, LM-W29-T01, LM-W29-T02, LM-W29-T03, LM-W29-T04, LM-W29-T05, LM-W29-T06.

- Acceptance: Demonstrate the integrated 0.2 to 0.3 to 0.4 workflow using exact local artifacts and actual observations; preserve original v1/v2 evidence, quality failures and complete costs; list unresolved public, qualified-human and external-reproduction gates instead of marking a public release complete.

- Origin: owner-authorized bounded successor; references: lean-model-lab:LM-019, owner-launch:2026-09-07:section-5, lean-model-lab:LM-009, lean-model-lab:LM-021, lean-model-lab:LM-022, lean-model-lab:LM-023, lean-model-lab:LM-024, owner-scope:2026-09-08:0.4.

- Risk/evidence needs: Bounded inference-only successor. Local integrated usefulness is the bounded exit. Broad training/distributed/confirmation acceptance, native Tanduna publication and public release remain separate. Software tests, real model observations, human interpretation and public/external access are separate evidence levels. See docs/decisions/0.4-scope.md.

- Recorded evidence: docs/RUNBOOK-0.4.md (2026-09-08 local 0.4 progress: Integrated components and reproducible package producer are implemented; the full prespecified run-to-serving-to-final-workbench demonstration is pending. Public, native Tanduna, qualified-human and fresh external gates remain open.).

## Wave 30: Researchers execute a bounded proposal through the real product

Horizon: 1.0. Exit evidence: Actual root-demonstrated usable workflow with admitted resources, immutable identities, numerical/quality gates, all attempts, bounded execution, persistence/recovery and inspection/export/rerun evidence. Acceptance is unmet until retained runtime outputs exist.

### LM-W30-T01 — Catalog research mechanisms with actionable rights and evidence

- Project key: `lean-model-lab:LM-W30-T01`; feature area: research catalog; target: 1.0; status: **AUTOMATED PASS**; evidence: **AUTOMATED PASS**.

- Outcome: An external researcher can find known inference and distinct training mechanisms, primary sources, lawful acquisition details and the limits of reported versus reproduced evidence.

- Dependencies: LM-F03.

- Acceptance: Retain versioned primary-source review, mechanism, applicability, numerical/semantic changes, model/data/dependency rights and exact acquisition instructions; distinguish literature knowledge from locally supported execution. Expose coverage gaps and strongest applicable comparator combinations. Browse current primary sources before novelty or external technical claims; finite catalog coverage cannot certify novelty.

- Origin: owner-directed bounded v1 delivery outcome; references: lean-model-lab:LM-007, lean-model-lab:LM-008, lean-model-lab:LM-013, lean-model-lab:LM-014, owner-mission:2026-09-08:research, owner-v1:2026-09-08:tanduna-v1-research-20260908-lean-model-lab.

- Risk/evidence needs: Current local status and scope are recorded in this row’s evidence; initial PLANNED / NOT TESTED state remains in the dated reconciliation record. Full public/external acceptance is not inferred from local verification. Use existing authorized resources, conservative shared-host scheduling and one heavy job; preserve frozen experiments, quality gates and all costs. Root alone delegates verified gpt-6-astra leaves. Protected evaluator/confirmation access and technical versus conventional isolation must be stated accurately. No human, external, hardware or novelty validation may be inferred from agent/software evidence.

- Recorded evidence: docs/evidence/automated-tests-v1-platform-01.json (2026-09-08 initial v1 platform build: 40 technique families and72primaryURLs; four nearest context-compression/slicing sources added to the initial catalog. Structural/projection/frozen-source checks pass; finite coverage and source assertions are not local reproduction or novelty.); docs/evidence/packaged-v1-platform-02.json (Expanded controller/cache integration and 295 software checks; actual learned training remains under investigation. Archive03 subsequently corrected the model profile size while preserving historical recipe interpretation.); docs/evidence/packaged-v1-platform-05.json (Local 1.0.0 executable deterministic manifest/implementation and twelve isolated CLI checks; native investigations preserve archive04. Final broad suite, distribution and separate reproduction pending.); docs/evidence/automated-tests-v1-platform-06.json (Final archive06 source and strict distribution software suite: 314 tests pass; 96 pre-recorded source/test/tool files remain unchanged. This is software verification, not independent research or external-person evidence.).

### LM-W30-T02 — Admit bounded model workload and candidate capabilities

- Project key: `lean-model-lab:LM-W30-T02`; feature area: research readiness; target: 1.0; status: **RUNTIME VERIFIED**; evidence: **RUNTIME VERIFIED**.

- Outcome: The supported v1 environment has explicit reproducible admission checks for model, workload, candidate and evaluator capabilities.

- Dependencies: LM-W30-T01.

- Acceptance: Document the exact supported runtime/environment and admitted model/workload resources without private credentials. Verify hashes, rights, resource bounds, candidate numerical/semantic contracts and quality evaluator separation before execution. Demonstrate any claimed OS/container isolation with tests; label a workflow convention accurately and do not run untrusted code without applicable technical isolation. Training admission requires an actual implemented/traced training path with exposure, optimizer, RNG and recovery semantics; inference cannot stand in for training.

- Origin: owner-directed bounded v1 delivery outcome; references: lean-model-lab:LM-002, lean-model-lab:LM-004, owner-mission:2026-09-08:research, owner-v1:2026-09-08:tanduna-v1-research-20260908-lean-model-lab.

- Risk/evidence needs: Current local status and scope are recorded in this row’s evidence; initial PLANNED / NOT TESTED state remains in the dated reconciliation record. Full public/external acceptance is not inferred from local verification. Use existing authorized resources, conservative shared-host scheduling and one heavy job; preserve frozen experiments, quality gates and all costs. Root alone delegates verified gpt-6-astra leaves. Protected evaluator/confirmation access and technical versus conventional isolation must be stated accurately. No human, external, hardware or novelty validation may be inferred from agent/software evidence.

- Recorded evidence: docs/evidence/automated-tests-v1-platform-01.json (2026-09-08 initial v1 platform build: Registered v3 model/workload/mechanism/resource/quality admission and existing prepared-artifact reuse path pass software controls. Actual native candidate use of the new archive is pending; no training or OS candidate isolation claimed.); docs/evidence/packaged-v1-platform-02.json (Expanded controller/cache integration and 295 software checks; actual learned training remains under investigation. Archive03 subsequently corrected the model profile size while preserving historical recipe interpretation.); docs/evidence/packaged-v1-platform-05.json (Local 1.0.0 executable deterministic manifest/implementation and twelve isolated CLI checks; native investigations preserve archive04. Final broad suite, distribution and separate reproduction pending.); docs/evidence/automated-tests-v1-platform-06.json (Final archive06 source and strict distribution software suite: 314 tests pass; 96 pre-recorded source/test/tool files remain unchanged. This is software verification, not independent research or external-person evidence.); docs/evidence/v1-first-workflow-02.json (Actual packaged proposal, frozen recipe, native comparison, persistence, report/workbench, crash recovery and verified export. Later research retains the complete model-bound controller training, fixed controls and adverse confirmation; current CLI preserves exact earlier producers.).

### LM-W30-T03 — Check mechanism compositions and strong comparators

- Project key: `lean-model-lab:LM-W30-T03`; feature area: research composition; target: 1.0; status: **RUNTIME VERIFIED**; evidence: **RUNTIME VERIFIED**.

- Outcome: Researchers can identify supported mechanism combinations, reference controls and harmful or unsupported interactions before implementing a candidate.

- Dependencies: LM-W30-T01, LM-W30-T02.

- Acceptance: Expose composition compatibility, shared-state/precision/quality risks, required constituent controls and full construction/verification/fallback costs. Separate catalog suggestions from tested admission and locally reproduced comparator strength. A proposal cannot silently turn on unsupported backend behavior or arbitrary execution.

- Origin: owner-directed bounded v1 delivery outcome; references: lean-model-lab:LM-018, owner-mission:2026-09-08:research, owner-v1:2026-09-08:tanduna-v1-research-20260908-lean-model-lab.

- Risk/evidence needs: Current local status and scope are recorded in this row’s evidence; initial PLANNED / NOT TESTED state remains in the dated reconciliation record. Full public/external acceptance is not inferred from local verification. Use existing authorized resources, conservative shared-host scheduling and one heavy job; preserve frozen experiments, quality gates and all costs. Root alone delegates verified gpt-6-astra leaves. Protected evaluator/confirmation access and technical versus conventional isolation must be stated accurately. No human, external, hardware or novelty validation may be inferred from agent/software evidence.

- Recorded evidence: docs/evidence/automated-tests-v1-platform-01.json (2026-09-08 initial v1 platform build: Catalog composition warnings and explicit full/lexical/dependency/matched-record controls are exposed. Unsupported arbitrary mechanisms are refused. Strong real-model comparator results remain pending.); docs/evidence/packaged-v1-platform-02.json (Expanded controller/cache integration and 295 software checks; actual learned training remains under investigation. Archive03 subsequently corrected the model profile size while preserving historical recipe interpretation.); docs/evidence/packaged-v1-platform-05.json (Local 1.0.0 executable deterministic manifest/implementation and twelve isolated CLI checks; native investigations preserve archive04. Final broad suite, distribution and separate reproduction pending.); docs/evidence/automated-tests-v1-platform-06.json (Final archive06 source and strict distribution software suite: 314 tests pass; 96 pre-recorded source/test/tool files remain unchanged. This is software verification, not independent research or external-person evidence.); docs/evidence/v1-first-workflow-02.json (Actual packaged proposal, frozen recipe, native comparison, persistence, report/workbench, crash recovery and verified export. Later research retains the complete model-bound controller training, fixed controls and adverse confirmation; current CLI preserves exact earlier producers.).

### LM-W30-T04 — Specify a causal candidate study with a decisive falsifier

- Project key: `lean-model-lab:LM-W30-T04`; feature area: research proposals; target: 1.0; status: **RUNTIME VERIFIED**; evidence: **RUNTIME VERIFIED**.

- Outcome: A researcher can create a source-contrasted candidate proposal whose technical delta, causal prediction and falsification criteria compile into a concrete bounded study contract.

- Dependencies: LM-W30-T01, LM-W30-T03.

- Acceptance: Record closest prior work, technical overlap and unresolved novelty, causal hypothesis, executable bounded implementation interface, strongest applicable baselines, equal-budget ablations and the cheapest decisive falsifier. Declare inference or actual training scope, efficiency-at-quality versus quality-at-budget, lawful data and resource envelope. Reject another settings sweep labeled a novel architecture; negative or inconclusive outcomes remain eligible when substantive.

- Origin: owner-directed bounded v1 delivery outcome; references: lean-model-lab:LM-016, lean-model-lab:LM-017, owner-mission:2026-09-08:research, owner-v1:2026-09-08:tanduna-v1-research-20260908-lean-model-lab.

- Risk/evidence needs: Current local status and scope are recorded in this row’s evidence; initial PLANNED / NOT TESTED state remains in the dated reconciliation record. Full public/external acceptance is not inferred from local verification. Use existing authorized resources, conservative shared-host scheduling and one heavy job; preserve frozen experiments, quality gates and all costs. Root alone delegates verified gpt-6-astra leaves. Protected evaluator/confirmation access and technical versus conventional isolation must be stated accurately. No human, external, hardware or novelty validation may be inferred from agent/software evidence.

- Recorded evidence: docs/evidence/automated-tests-v1-platform-01.json (2026-09-08 initial v1 platform build: Source-contrasted proposals and protocols bind causal question, limitations, ablations and falsifiers. Classical slicing is an initial infrastructure control; substantive candidate investigation is still required.); docs/evidence/packaged-v1-platform-02.json (Expanded controller/cache integration and 295 software checks; actual learned training remains under investigation. Archive03 subsequently corrected the model profile size while preserving historical recipe interpretation.); docs/evidence/packaged-v1-platform-05.json (Local 1.0.0 executable deterministic manifest/implementation and twelve isolated CLI checks; native investigations preserve archive04. Final broad suite, distribution and separate reproduction pending.); docs/evidence/automated-tests-v1-platform-06.json (Final archive06 source and strict distribution software suite: 314 tests pass; 96 pre-recorded source/test/tool files remain unchanged. This is software verification, not independent research or external-person evidence.); docs/evidence/v1-first-workflow-02.json (Actual packaged proposal, frozen recipe, native comparison, persistence, report/workbench, crash recovery and verified export. Later research retains the complete model-bound controller training, fixed controls and adverse confirmation; current CLI preserves exact earlier producers.).

### LM-W30-T05 — Freeze independent quality and complete experiment accounting

- Project key: `lean-model-lab:LM-W30-T05`; feature area: research experiment contracts; target: 1.0; status: **RUNTIME VERIFIED**; evidence: **RUNTIME VERIFIED**.

- Outcome: Each executable study has an independently versioned quality contract, all-attempt inventory and finite reproducible evaluation design.

- Dependencies: LM-W30-T04.

- Acceptance: Before confirmation freeze question, comparator, sample/scenario selection, seeds, repetitions, effect/uncertainty method, stopping rule, resource limits and quality thresholds. Separate development from untouched confirmation with access accounting; never weaken earlier frozen parity/quality gates. Retain outputs/differences, latency distribution/tails, throughput, memory and all setup/search/data preparation/failed/invalid/cancelled/retry/recovery/evaluation costs. Distinguish measured costs from estimated energy and missing instrumentation.

- Origin: owner-directed bounded v1 delivery outcome; references: lean-model-lab:LM-011, lean-model-lab:LM-012, owner-mission:2026-09-08:research, owner-v1:2026-09-08:tanduna-v1-research-20260908-lean-model-lab.

- Risk/evidence needs: Current local status and scope are recorded in this row’s evidence; initial PLANNED / NOT TESTED state remains in the dated reconciliation record. Full public/external acceptance is not inferred from local verification. Use existing authorized resources, conservative shared-host scheduling and one heavy job; preserve frozen experiments, quality gates and all costs. Root alone delegates verified gpt-6-astra leaves. Protected evaluator/confirmation access and technical versus conventional isolation must be stated accurately. No human, external, hardware or novelty validation may be inferred from agent/software evidence.

- Recorded evidence: docs/evidence/automated-tests-v1-platform-01.json (2026-09-08 initial v1 platform build: v3 exact task quality>=95%, zero observed pairwise quality loss, same-input parity controls and full-wall primary cost are tested. Raw native evidence is required for measured3 reports; no experimental finding follows from fixtures.); docs/evidence/packaged-v1-platform-02.json (Expanded controller/cache integration and 295 software checks; actual learned training remains under investigation. Archive03 subsequently corrected the model profile size while preserving historical recipe interpretation.); docs/evidence/packaged-v1-platform-05.json (Local 1.0.0 executable deterministic manifest/implementation and twelve isolated CLI checks; native investigations preserve archive04. Final broad suite, distribution and separate reproduction pending.); docs/evidence/automated-tests-v1-platform-06.json (Final archive06 source and strict distribution software suite: 314 tests pass; 96 pre-recorded source/test/tool files remain unchanged. This is software verification, not independent research or external-person evidence.); docs/evidence/v1-first-workflow-02.json (Actual packaged proposal, frozen recipe, native comparison, persistence, report/workbench, crash recovery and verified export. Later research retains the complete model-bound controller training, fixed controls and adverse confirmation; current CLI preserves exact earlier producers.).

### LM-W30-T06 — Freeze and verify candidate study and evaluation artifacts

- Project key: `lean-model-lab:LM-W30-T06`; feature area: research freeze; target: 1.0; status: **RUNTIME VERIFIED**; evidence: **RUNTIME VERIFIED**.

- Outcome: Immutable study identities bind source catalog, candidate/build/runtime, model/workload, evaluator and all required source bytes with reproducible verification.

- Dependencies: LM-W30-T02, LM-W30-T03, LM-W30-T05.

- Acceptance: Freeze exact bytes and hashes needed to recover the meaning and executable identity of a study without silently consulting mutable registry state. Bind candidate, reference/ablation definitions, acquisition rights, quality rules, resource allocation and protected confirmation commitments. Demonstrate mutation and incompatible-resume rejection, evaluator protection and honest isolation claims. New exploratory changes produce a new build/study; keep previous attempts and costs.

- Origin: owner-directed bounded v1 delivery outcome; references: lean-model-lab:LM-018, lean-model-lab:LM-021, owner-mission:2026-09-08:research, owner-v1:2026-09-08:tanduna-v1-research-20260908-lean-model-lab.

- Risk/evidence needs: Current local status and scope are recorded in this row’s evidence; initial PLANNED / NOT TESTED state remains in the dated reconciliation record. Full public/external acceptance is not inferred from local verification. Use existing authorized resources, conservative shared-host scheduling and one heavy job; preserve frozen experiments, quality gates and all costs. Root alone delegates verified gpt-6-astra leaves. Protected evaluator/confirmation access and technical versus conventional isolation must be stated accurately. No human, external, hardware or novelty validation may be inferred from agent/software evidence.

- Recorded evidence: docs/evidence/automated-tests-v1-platform-01.json (2026-09-08 initial v1 platform build: Deterministic1.0.0.dev0 zipapp,12isolated legacy CLI checks,9research CLI checks plus a separate fixture-boot admission rejection; frozen source/recipe mutations and resume identity checked. Same-host processes, not external reproduction.); docs/evidence/packaged-v1-platform-02.json (Expanded controller/cache integration and 295 software checks; actual learned training remains under investigation. Archive03 subsequently corrected the model profile size while preserving historical recipe interpretation.); docs/evidence/packaged-v1-platform-05.json (Local 1.0.0 executable deterministic manifest/implementation and twelve isolated CLI checks; native investigations preserve archive04. Final broad suite, distribution and separate reproduction pending.); docs/evidence/automated-tests-v1-platform-06.json (Final archive06 source and strict distribution software suite: 314 tests pass; 96 pre-recorded source/test/tool files remain unchanged. This is software verification, not independent research or external-person evidence.); docs/evidence/v1-first-workflow-02.json (Actual packaged proposal, frozen recipe, native comparison, persistence, report/workbench, crash recovery and verified export. Later research retains the complete model-bound controller training, fixed controls and adverse confirmation; current CLI preserves exact earlier producers.).

### LM-W30-T07 — Implement and execute an admitted bounded candidate through the platform

- Project key: `lean-model-lab:LM-W30-T07`; feature area: research control compilation; target: 1.0; status: **RUNTIME VERIFIED**; evidence: **RUNTIME VERIFIED**.

- Outcome: The actual product can turn a frozen nontrivial candidate proposal into a bounded implementation and real model experiment with reference and ablation runs.

- Dependencies: LM-W30-T02, LM-W30-T03, LM-W30-T06.

- Acceptance: Provide a documented product CLI/API or UI path from frozen proposal to admitted candidate implementation, real model execution, numerical/reference controls and all-attempt evidence. Preserve earlier registered controls and archived bytes. Bound candidate code/state, verify quality independently, observe finite resource limits and cancellation/recovery, and retain startup/failure/fallback costs. A manifest-only compiler, synthetic illustrative fixture or separate scratch runner does not satisfy this capability. Implemented/traced training is required for any training study or benefit claim; generic training support is not invented by inference controls.

- Origin: owner-directed bounded v1 delivery outcome; references: lean-model-lab:LM-004, lean-model-lab:LM-007, lean-model-lab:LM-021, owner-mission:2026-09-08:research, owner-v1:2026-09-08:tanduna-v1-research-20260908-lean-model-lab.

- Risk/evidence needs: Current local status and scope are recorded in this row’s evidence; initial PLANNED / NOT TESTED state remains in the dated reconciliation record. Full public/external acceptance is not inferred from local verification. Use existing authorized resources, conservative shared-host scheduling and one heavy job; preserve frozen experiments, quality gates and all costs. Root alone delegates verified gpt-6-astra leaves. Protected evaluator/confirmation access and technical versus conventional isolation must be stated accurately. No human, external, hardware or novelty validation may be inferred from agent/software evidence.

- Recorded evidence: docs/evidence/automated-tests-v1-platform-01.json (2026-09-08 initial v1 platform build: Registered prompt transformation executes through actual inert HTTP server and durable Session;3v3coordinator tests include publication-loss reconciliation with retained preparation envelope. Real model execution of candidate pending.); docs/evidence/packaged-v1-platform-02.json (Expanded controller/cache integration and 295 software checks; actual learned training remains under investigation. Archive03 subsequently corrected the model profile size while preserving historical recipe interpretation.); docs/evidence/packaged-v1-platform-05.json (Local 1.0.0 executable deterministic manifest/implementation and twelve isolated CLI checks; native investigations preserve archive04. Final broad suite, distribution and separate reproduction pending.); docs/evidence/automated-tests-v1-platform-06.json (Final archive06 source and strict distribution software suite: 314 tests pass; 96 pre-recorded source/test/tool files remain unchanged. This is software verification, not independent research or external-person evidence.); docs/evidence/v1-first-workflow-02.json (Actual packaged proposal, frozen recipe, native comparison, persistence, report/workbench, crash recovery and verified export. Later research retains the complete model-bound controller training, fixed controls and adverse confirmation; current CLI preserves exact earlier producers.); docs/research/candidate-study/manuscript.md (Eight real study cells with 1,984 native observations, an actual fitted/calibrated controller, causal controls and all three fixed confirmation policies. No arm reaches 95%; actual learned deployment selects full context everywhere. No underlying LLM training or new architecture claim.).

### LM-W30-T08 — Demonstrate the external researcher workflow before investigations

- Project key: `lean-model-lab:LM-W30-T08`; feature area: research workflow; target: 1.0; status: **RUNTIME VERIFIED**; evidence: **RUNTIME VERIFIED**.

- Outcome: Root demonstrates one real product workflow from admitted resources and proposal through candidate execution, inspection, recovery and reproducible export before investigator campaigns start.

- Dependencies: LM-W30-T01, LM-W30-T02, LM-W30-T03, LM-W30-T04, LM-W30-T05, LM-W30-T06, LM-W30-T07.

- Acceptance: Use the actual user-facing product to admit a lawful model/workload, propose/implement a bounded candidate, freeze and run a real experiment, inspect every attempt and quality/cost tradeoffs, exercise supported persistence/failure/recovery and export/rerun it using documented commands. Retain actual build and raw outputs; no private developer credential or undocumented intervention. This demonstrated usable workflow gates root dispatch of the three investigators. Product blocks trigger reproducible expected/actual reports and a minimal acceptance check, followed by root fixes, relevant regression/end-to-end evidence, a revised build and investigator reruns retaining earlier outputs.

- Origin: owner-directed bounded v1 delivery outcome; references: lean-model-lab:LM-019, lean-model-lab:LM-024, owner-mission:2026-09-08:research, owner-v1:2026-09-08:tanduna-v1-research-20260908-lean-model-lab.

- Risk/evidence needs: Current local status and scope are recorded in this row’s evidence; initial PLANNED / NOT TESTED state remains in the dated reconciliation record. Full public/external acceptance is not inferred from local verification. Use existing authorized resources, conservative shared-host scheduling and one heavy job; preserve frozen experiments, quality gates and all costs. Root alone delegates verified gpt-6-astra leaves. Protected evaluator/confirmation access and technical versus conventional isolation must be stated accurately. No human, external, hardware or novelty validation may be inferred from agent/software evidence.

- Recorded evidence: docs/evidence/automated-tests-v1-platform-01.json (2026-09-08 initial v1 platform build: End-to-end software path and documentation are implemented; actual packaged model/candidate/recovery/export demonstration must occur after current heavy job releases its lease. Investigator dispatch gate remains unmet.); docs/evidence/packaged-v1-platform-02.json (Expanded controller/cache integration and 295 software checks; actual learned training remains under investigation. Archive03 subsequently corrected the model profile size while preserving historical recipe interpretation.); docs/evidence/v1-first-workflow-02.json (Actual archive03 proposal/recipe, 32 native requests, independent raw audit, inspect/report/workbench, native crash/reconciliation/eight-request restart and verified export completed before investigator dispatch. Adverse 1/8 per-arm quality remains retained. This verifies product operation, not quality approval or an external person.); docs/evidence/packaged-v1-platform-05.json (Local 1.0.0 executable deterministic manifest/implementation and twelve isolated CLI checks; native investigations preserve archive04. Final broad suite, distribution and separate reproduction pending.); docs/evidence/automated-tests-v1-platform-06.json (Final archive06 source and strict distribution software suite: 314 tests pass; 96 pre-recorded source/test/tool files remain unchanged. This is software verification, not independent research or external-person evidence.); docs/evidence/v1-first-workflow-02.json (Actual packaged proposal, frozen recipe, native comparison, persistence, report/workbench, crash recovery and verified export. Later research retains the complete model-bound controller training, fixed controls and adverse confirmation; current CLI preserves exact earlier producers.).

## Wave 31: Three substantive studies and a reproducible v1 release candidate

Horizon: 1.0. Exit evidence: Three substantive reproducible research packages, independent agent review with discrepancies resolved or exposed, actual clean supported package workflow, rights/notices/first-run/release artifacts and explicit remaining approval/public/external/human gates. No overall public release completion is inferred from local preparation.

### LM-W31-T01 — Produce a substantive quality-constrained efficiency study

- Project key: `lean-model-lab:LM-W31-T01`; feature area: mechanism falsification; target: 1.0; status: **RUNTIME VERIFIED**; evidence: **RUNTIME VERIFIED**.

- Outcome: A distinct investigator produces a reproducible benchmark or negative finding about a justified supported mechanism under held-out quality and full system costs.

- Dependencies: LM-W30-T08.

- Acceptance: Root assigns a verified gpt-6-astra leaf a bounded platform entrypoint, strong baseline, lawful dataset/scenario rights, finite budget, output directory, measurements and falsification rules. Operate the built product to test caching, quantization, batching or a justified supported alternative on held-out workloads with pinned model/runtime. Measure task quality/output differences, latency distribution, throughput and memory including startup/failures. Preserve earlier failed parity/quality evidence and its gate unchanged; do not count one settings slice or tiny illustrative fixture as a substantive result. Freeze confirmation design and retain all attempts, uncertainty, limitations, rights and reproducible claim/report artifacts.

- Origin: owner-directed bounded v1 delivery outcome; references: lean-model-lab:LM-006, lean-model-lab:LM-016, owner-mission:2026-09-08:research, owner-v1:2026-09-08:tanduna-v1-research-20260908-lean-model-lab.

- Risk/evidence needs: Current local status and scope are recorded in this row’s evidence; initial PLANNED / NOT TESTED state remains in the dated reconciliation record. Full public/external acceptance is not inferred from local verification. Use existing authorized resources, conservative shared-host scheduling and one heavy job; preserve frozen experiments, quality gates and all costs. Root alone delegates verified gpt-6-astra leaves. Protected evaluator/confirmation access and technical versus conventional isolation must be stated accurately. No human, external, hardware or novelty validation may be inferred from agent/software evidence.

- Recorded evidence: docs/evidence/v1-investigator-dispatches.json (Verified Astra leaf dispatched after the actual product workflow with a finite budget, disjoint directory, actual CLI, frozen quality criteria and blocker/reproduction protocol. Research acceptance remains pending.); docs/research/quality-study/confirmation-14b/manuscript.md (Fresh 512-observation 14B confirmation retains 127/128 correct per arm/repetition and parity, 4.123x batch service-throughput and 3.912x full-attempt efficiency medians, with zero jointly latency-qualified responses. Earlier 0.5B quality/parity failure remains. Portable reanalysis passes; separate reproduction/public release remain open.); docs/research/reproduction-review/report.md (Separate verified Astra review complete. One retained 512-observation cell per investigation is repeated through its exact original producer; independent reanalysis and raw checks retain actual discrepancies and timing variation. Original populations, criteria, failures, costs and scientific artifacts remain; no external human or fresh confirmation claim.).

### LM-W31-T02 — Investigate a substantive candidate with ablations and confirmation

- Project key: `lean-model-lab:LM-W31-T02`; feature area: inference mechanism research; target: 1.0; status: **RUNTIME VERIFIED**; evidence: **RUNTIME VERIFIED**.

- Outcome: A distinct investigator implements and tests one ambitious evidence-grounded candidate mechanism through the platform and reports its causal support or rigorous failure.

- Dependencies: LM-W30-T08.

- Acceptance: Root assigns a verified gpt-6-astra leaf a bounded question, platform entrypoint, lawful resources, finite budget, disjoint evidence directory and falsifiers. Browse current primary sources for closest prior work and novelty limits; freeze causal prediction, candidate source/build, strongest applicable baselines, equal-budget ablations, numerical/quality checks and untouched confirmation before access. Execute a real implemented candidate through the product, retaining all failed/invalid/cancelled/unfavorable attempts and complete costs. Another settings sweep cannot be called a new architecture. A rigorous negative/inconclusive finding is acceptable when method, coverage and implications are substantive. Keep informative development artifacts separately usable by study three; confirmation results must not leak into its tuning.

- Origin: owner-directed bounded v1 delivery outcome; references: lean-model-lab:LM-013, lean-model-lab:LM-014, lean-model-lab:LM-016, owner-mission:2026-09-08:research, owner-v1:2026-09-08:tanduna-v1-research-20260908-lean-model-lab.

- Risk/evidence needs: Current local status and scope are recorded in this row’s evidence; initial PLANNED / NOT TESTED state remains in the dated reconciliation record. Full public/external acceptance is not inferred from local verification. Use existing authorized resources, conservative shared-host scheduling and one heavy job; preserve frozen experiments, quality gates and all costs. Root alone delegates verified gpt-6-astra leaves. Protected evaluator/confirmation access and technical versus conventional isolation must be stated accurately. No human, external, hardware or novelty validation may be inferred from agent/software evidence.

- Recorded evidence: docs/evidence/v1-investigator-dispatches.json (Verified Astra leaf dispatched after the actual product workflow with a finite budget, disjoint directory, actual CLI, frozen quality criteria and blocker/reproduction protocol. Research acceptance remains pending.); docs/research/candidate-study/manuscript.md (Complete 1,984-observation, 200-original-table negative context-selection study. Full/slice quality 23/128 versus 34/128, 13 harms and conditional fixed-output oracle 47/128; simple and fitted-controller confirmation and all calibration/control evidence retained. Separate reproduction/public release remain open.); docs/research/reproduction-review/report.md (Separate verified Astra review complete. One retained 512-observation cell per investigation is repeated through its exact original producer; independent reanalysis and raw checks retain actual discrepancies and timing variation. Original populations, criteria, failures, costs and scientific artifacts remain; no external human or fresh confirmation claim.).

### LM-W31-T03 — Challenge generalization and the full cost of a mechanism

- Project key: `lean-model-lab:LM-W31-T03`; feature area: training mechanism research; target: 1.0; status: **RUNTIME VERIFIED**; evidence: **RUNTIME VERIFIED**.

- Outcome: A distinct investigator establishes measured conditions where a promising effect or informative failure transfers, reverses or disappears.

- Dependencies: LM-W30-T08, LM-W31-T01.

- Acceptance: Root assigns a verified gpt-6-astra leaf a bounded user-facing entrypoint, baseline, lawful scenarios, finite budget, disjoint directory and falsification rules. Challenge distinct workloads and context/arrival patterns, plus an additional already admitted model or scale when feasible; justify an infeasible axis and report a project-relevant alternative. Study one results or separately identified study two development evidence may select the question; do not wait for or tune on study two confirmation. Freeze this study's own selection, quality, uncertainty, resource and stopping rules before its independent untouched confirmation. Account for quality loss, setup/search, tail latency, memory and retries, separating measured costs from estimated energy. Produce a distinct substantive result with all attempts and failure boundaries, not the same study split into another document.

- Origin: owner-directed bounded v1 delivery outcome; references: lean-model-lab:LM-005, lean-model-lab:LM-008, lean-model-lab:LM-014, owner-mission:2026-09-08:research, owner-v1:2026-09-08:tanduna-v1-research-20260908-lean-model-lab.

- Risk/evidence needs: Current local status and scope are recorded in this row’s evidence; initial PLANNED / NOT TESTED state remains in the dated reconciliation record. Full public/external acceptance is not inferred from local verification. Use existing authorized resources, conservative shared-host scheduling and one heavy job; preserve frozen experiments, quality gates and all costs. Root alone delegates verified gpt-6-astra leaves. Protected evaluator/confirmation access and technical versus conventional isolation must be stated accurately. No human, external, hardware or novelty validation may be inferred from agent/software evidence.

- Recorded evidence: docs/evidence/v1-investigator-dispatches.json (Verified Astra leaf dispatched after the actual product workflow with a finite budget, disjoint directory, actual CLI, frozen quality criteria and blocker/reproduction protocol. Research acceptance remains pending.); docs/research/systems-study/manuscript.md (Five real cells and 1,600 observations across 0.5B/14B, 24/64 records and retained table-prefix reuse; 32 distinct held-out tables. Warm-query input work increases under slicing on every held-out table, and matched 14B accuracy falls from 73/128 to 55/128. All quality gates fail; portable reanalysis passes. Separate reproduction/public release remain open.); docs/research/reproduction-review/report.md (Separate verified Astra review complete. One retained 512-observation cell per investigation is repeated through its exact original producer; independent reanalysis and raw checks retain actual discrepancies and timing variation. Original populations, criteria, failures, costs and scientific artifacts remain; no external human or fresh confirmation claim.).

### LM-W31-T04 — Reproduce and skeptically review all three research packages

- Project key: `lean-model-lab:LM-W31-T04`; feature area: research frontier evidence; target: 1.0; status: **RUNTIME VERIFIED**; evidence: **RUNTIME VERIFIED**.

- Outcome: A separate verified Astra leaf reproduces the three retained result packages and records discrepancies, alternative explanations and claim limits after results exist.

- Dependencies: LM-W31-T01, LM-W31-T02, LM-W31-T03.

- Acceptance: After three results exist, root assigns a separate verified gpt-6-astra reproduction/skeptical-review leaf to the actual product and retained packages with finite resources and disjoint outputs. Recompute selected positive/adverse effects from raw outputs, rerun supported specifications, challenge controls, uncertainty, costs, data rights, novelty and confirmation leakage, and retain discrepancies plus root dispositions and repeat evidence. Independent checking code may inspect product outputs; a scratch implementation cannot substitute for the product investigation. Each accepted result needs a plain-language claim, context, rights/acquisition, exact identities, executable specification/rerun, all attempts, baseline/independent checks, evidence-generated figures, uncertainty/limits, reproduction outcome and cited report/manuscript. A distinct agent provides process separation, not independent human or institutional validation.

- Origin: owner-directed bounded v1 delivery outcome; references: lean-model-lab:LM-009, lean-model-lab:LM-011, lean-model-lab:LM-018, owner-mission:2026-09-08:research, owner-v1:2026-09-08:tanduna-v1-research-20260908-lean-model-lab.

- Risk/evidence needs: Current local status and scope are recorded in this row’s evidence; initial PLANNED / NOT TESTED state remains in the dated reconciliation record. Full public/external acceptance is not inferred from local verification. Use existing authorized resources, conservative shared-host scheduling and one heavy job; preserve frozen experiments, quality gates and all costs. Root alone delegates verified gpt-6-astra leaves. Protected evaluator/confirmation access and technical versus conventional isolation must be stated accurately. No human, external, hardware or novelty validation may be inferred from agent/software evidence.

- Recorded evidence: docs/evidence/v1-separate-review-dispatch.json (A new leaf actual session was verified as gpt-6-astra/high before native execution. Exact three research ZIPs verified and extracted; 1,536-request complete-cell reproduction admitted within original allocation. Outcomes pending.); docs/research/reproduction-review/report.md (Three complete retained-cell repetitions, 1,536 new observations, exact original producers, separate raw/reanalysis checks and per-result verdicts. The failed zero-inference admission and explicit restored-provenance continuation remain charged. Same host and Unix identity; no human/institutional independence.).

### LM-W31-T05 — Verify the prepared v1 package in a clean supported environment

- Project key: `lean-model-lab:LM-W31-T05`; feature area: mechanism scaling and transfer; target: 1.0; status: **RUNTIME VERIFIED**; evidence: **RUNTIME VERIFIED**.

- Outcome: The concrete v1 release candidate and three study packages can be obtained locally, installed and exercised through the documented external first-run workflow in a clean supported environment.

- Dependencies: LM-W30-T08, LM-W31-T04.

- Acceptance: Verify the actual packaged application with documented supported resources and lawful dependency/model/data acquisition, without private developer credentials or undocumented intervention. Exercise the full relevant UI/CLI/runtime path, persistence, quality/cost inspection/export/rerun and supported failure/recovery; retain observed accessibility/performance and authentic screenshots/demo. Distinguish second process, container, separate physical machine and external person. Include licenses/notices, troubleshooting, examples, contribution opportunities, versioned data/API compatibility and study raw-evidence manifests. Report unsupported environments and remaining human/external gates; a source-tree test alone is not clean package verification.

- Origin: owner-directed bounded v1 delivery outcome; references: lean-model-lab:LM-015, lean-model-lab:LM-022, owner-mission:2026-09-08:research, owner-v1:2026-09-08:tanduna-v1-research-20260908-lean-model-lab.

- Risk/evidence needs: Current local status and scope are recorded in this row’s evidence; initial PLANNED / NOT TESTED state remains in the dated reconciliation record. Full public/external acceptance is not inferred from local verification. Use existing authorized resources, conservative shared-host scheduling and one heavy job; preserve frozen experiments, quality gates and all costs. Root alone delegates verified gpt-6-astra leaves. Protected evaluator/confirmation access and technical versus conventional isolation must be stated accurately. No human, external, hardware or novelty validation may be inferred from agent/software evidence.

- Recorded evidence: docs/evidence/v1-clean-preliminary-workflow.json (Preliminary distribution completes native first use and interrupted recovery in a separate same-host worktree and minimal environment. Exact final three-package source/CLI verification remains pending.); docs/evidence/v1-final-workbench-browser.json (Actual archive06 workbenches pass keyboard task segments, focus, native 200% zoom, narrow reflow and a 2,048-row load observation. Final distribution index, human screen-reader and external-person observations remain separate.); docs/evidence/v1-final-clean-workflow.json (Exact candidate03 source ZIP and archive06 in a new same-host detached worktree and fresh Python3.12.14 venv without pip. All19 commands pass;32 native comparison and10 recovery observations retained; original leases/resources and separately admitted dependencies reused. Final index and external human gates remain open.); docs/evidence/v1-final-distribution-index-browser.json (Actual 23-study index and download hashes verified at native100%/200% zoom and narrow width, with keyboard navigation opening all512 quality-study observations and returning to the index. Renderer sandbox/empty network namespace/cleanup retained. Authentic images reviewed; human screen-reader review remains open.).

### LM-W31-T06 — Prepare exact v1 release artifacts and track approval separately

- Project key: `lean-model-lab:LM-W31-T06`; feature area: mechanism confirmation; target: 1.0; status: **AUTOMATED PASS**; evidence: **AUTOMATED PASS**.

- Outcome: Versioned v1 release and research artifacts are ready for exact owner review while local preparation, submission, acceptance, public release and human/external evidence remain distinct states.

- Dependencies: LM-W31-T05.

- Acceptance: Prepare the tested v1 candidate, three substantive research packages, release notes, authentic screenshots/demo, readable findings overview, external first-run guide, contributor opportunities and English launch copy linking the repository and correct Tanduna project. Reconcile canonical evidence/statuses and identify exact artifact hashes, versions and intended destinations for Lucas's approval. Local preparation does not imply owner approval, submitted/accepted native plan, public download/access verification or human/external validation. Do not publish releases, commits/posts, Tanduna updates, contact participants or submit papers without applicable explicit authorization. After exact approval, root performs only authorized publication and verifies actual public downloads/access and Tanduna readback; overall completion still requires all applicable contract gates. Pending approval must not stop independent authorized work or be represented as public v1 completion.

- Origin: owner-directed bounded v1 delivery outcome; references: lean-model-lab:LM-012, lean-model-lab:LM-023, lean-model-lab:LM-024, owner-mission:2026-09-08:research, owner-v1:2026-09-08:tanduna-v1-research-20260908-lean-model-lab.

- Risk/evidence needs: Current local status and scope are recorded in this row’s evidence; initial PLANNED / NOT TESTED state remains in the dated reconciliation record. Full public/external acceptance is not inferred from local verification. Use existing authorized resources, conservative shared-host scheduling and one heavy job; preserve frozen experiments, quality gates and all costs. Root alone delegates verified gpt-6-astra leaves. Protected evaluator/confirmation access and technical versus conventional isolation must be stated accurately. No human, external, hardware or novelty validation may be inferred from agent/software evidence.

- Recorded evidence: docs/release/V1-RELEASE-NOTES.md (Release notes, English launch copy, findings overview, external first-run and reviewer briefs, authentic screenshots and split-package builder are locally prepared. Exact ZIP assembly, separate reproduction and final artifact approval remain pending.); docs/evidence/v1-candidate03-distribution-readback.json (Actual candidate03 source/CLI,18 evidence ZIPs and3 research ZIPs pass file hashes/inventories and local HTML/source Markdown links. Final delivery adds clean/reproduction receipts and2 workflow exports; no publication or approval inferred.); docs/evidence/v1-candidate04-distribution-readback.json (Actual23-study/three-research distribution passes exact ZIP inventories/hashes and local links. Final delivery preserves original reviewed scientific content and browser bytes, adds the index evidence and provides external source-commit/complete-ZIP/resource records. Exact public v1.0.0-rc.1 approval remains separate.).

## Source mapping and history

Each row preserves original identity, frozen revision, acceptance, predecessors and history in the canonical mapping; platform IDs remain null until supported creation returns them.

| Original source | Treatment | Successors |
| --- | --- | --- |

| LM-F01 | retained | LM-F01 |

| LM-F02 | retained | LM-F02 |

| LM-F03 | retained | LM-F03 |

| LM-001 | split and expanded | LM-W01-T01, LM-W01-T02, LM-W01-T03, LM-W01-T04, LM-W01-T05, LM-W01-T06, LM-W01-T07, LM-W01-T08, LM-W28-T01, LM-W28-T02, LM-W28-T06, LM-W28-T08 |

| LM-002 | split and expanded | LM-W01-T01, LM-W01-T02, LM-W01-T03, LM-W01-T04, LM-W01-T05, LM-W01-T06, LM-W01-T07, LM-W01-T08, LM-W14-T01, LM-W14-T02, LM-W14-T03, LM-W14-T04, LM-W14-T05, LM-W14-T06, LM-W14-T07, LM-W14-T08, LM-W15-T01, LM-W15-T02, LM-W15-T03, LM-W15-T04, LM-W15-T05, LM-W15-T06, LM-W15-T07, LM-W15-T08, LM-W28-T01, LM-W28-T02, LM-W28-T06, LM-W28-T08, LM-W29-T05, LM-W30-T02 |

| LM-003 | split and expanded | LM-W02-T01, LM-W02-T02, LM-W02-T03, LM-W02-T04, LM-W02-T05, LM-W02-T06, LM-W02-T07, LM-W02-T08, LM-W28-T02, LM-W28-T03, LM-W28-T07 |

| LM-004 | split and expanded | LM-W03-T01, LM-W03-T02, LM-W03-T03, LM-W03-T04, LM-W03-T05, LM-W03-T06, LM-W03-T07, LM-W03-T08, LM-W04-T01, LM-W04-T02, LM-W04-T03, LM-W04-T04, LM-W04-T05, LM-W04-T06, LM-W04-T07, LM-W04-T08, LM-W28-T01, LM-W28-T04, LM-W28-T05, LM-W28-T06, LM-W28-T07, LM-W28-T08, LM-W30-T02, LM-W30-T07 |

| LM-005 | deferred and expanded | LM-W08-T01, LM-W08-T02, LM-W08-T03, LM-W08-T04, LM-W08-T05, LM-W08-T06, LM-W08-T07, LM-W08-T08, LM-W31-T03 |

| LM-006 | deferred and expanded | LM-W09-T01, LM-W09-T02, LM-W09-T03, LM-W09-T04, LM-W09-T05, LM-W09-T06, LM-W09-T07, LM-W09-T08, LM-W31-T01 |

| LM-007 | split and expanded | LM-W03-T01, LM-W03-T02, LM-W03-T03, LM-W03-T04, LM-W03-T05, LM-W03-T06, LM-W03-T07, LM-W03-T08, LM-W06-T01, LM-W06-T02, LM-W06-T03, LM-W06-T04, LM-W06-T05, LM-W06-T06, LM-W06-T07, LM-W06-T08, LM-W07-T01, LM-W07-T02, LM-W07-T03, LM-W07-T04, LM-W07-T05, LM-W07-T06, LM-W07-T07, LM-W07-T08, LM-W04-T01, LM-W04-T02, LM-W04-T03, LM-W04-T04, LM-W04-T05, LM-W04-T06, LM-W04-T07, LM-W04-T08, LM-W28-T01, LM-W28-T04, LM-W28-T05, LM-W28-T06, LM-W28-T07, LM-W28-T08, LM-W29-T04, LM-W30-T01, LM-W30-T07 |

| LM-008 | deferred and expanded | LM-W10-T01, LM-W10-T02, LM-W10-T03, LM-W10-T04, LM-W10-T05, LM-W10-T06, LM-W10-T07, LM-W10-T08, LM-W30-T01, LM-W31-T03 |

| LM-009 | split and expanded | LM-W04-T01, LM-W04-T02, LM-W04-T03, LM-W04-T04, LM-W04-T05, LM-W04-T06, LM-W04-T07, LM-W04-T08, LM-W15-T01, LM-W15-T02, LM-W15-T03, LM-W15-T04, LM-W15-T05, LM-W15-T06, LM-W15-T07, LM-W15-T08, LM-W23-T01, LM-W23-T02, LM-W23-T03, LM-W23-T04, LM-W23-T05, LM-W23-T06, LM-W23-T07, LM-W23-T08, LM-W28-T04, LM-W28-T06, LM-W28-T08, LM-W29-T01, LM-W29-T02, LM-W29-T03, LM-W29-T04, LM-W29-T05, LM-W29-T06, LM-W29-T07, LM-W29-T08, LM-W31-T04 |

| LM-010 | split and expanded | LM-W02-T01, LM-W02-T02, LM-W02-T03, LM-W02-T04, LM-W02-T05, LM-W02-T06, LM-W02-T07, LM-W02-T08, LM-W04-T01, LM-W04-T02, LM-W04-T03, LM-W04-T04, LM-W04-T05, LM-W04-T06, LM-W04-T07, LM-W04-T08, LM-W11-T01, LM-W11-T02, LM-W11-T03, LM-W11-T04, LM-W11-T05, LM-W11-T06, LM-W11-T07, LM-W11-T08, LM-W03-T01, LM-W03-T02, LM-W03-T03, LM-W03-T04, LM-W03-T05, LM-W03-T06, LM-W03-T07, LM-W03-T08, LM-W28-T01, LM-W28-T02, LM-W28-T03, LM-W28-T04, LM-W28-T05, LM-W28-T06, LM-W28-T07, LM-W28-T08 |

| LM-011 | split and expanded | LM-W04-T01, LM-W04-T02, LM-W04-T03, LM-W04-T04, LM-W04-T05, LM-W04-T06, LM-W04-T07, LM-W04-T08, LM-W06-T01, LM-W06-T02, LM-W06-T03, LM-W06-T04, LM-W06-T05, LM-W06-T06, LM-W06-T07, LM-W06-T08, LM-W12-T01, LM-W12-T02, LM-W12-T03, LM-W12-T04, LM-W12-T05, LM-W12-T06, LM-W12-T07, LM-W12-T08, LM-W14-T01, LM-W14-T02, LM-W14-T03, LM-W14-T04, LM-W14-T05, LM-W14-T06, LM-W14-T07, LM-W14-T08, LM-W28-T04, LM-W28-T06, LM-W28-T08, LM-W29-T04, LM-W29-T05, LM-W30-T05, LM-W31-T04 |

| LM-012 | deferred and expanded | LM-W13-T01, LM-W13-T02, LM-W13-T03, LM-W13-T04, LM-W13-T05, LM-W13-T06, LM-W13-T07, LM-W13-T08, LM-W14-T01, LM-W14-T02, LM-W14-T03, LM-W14-T04, LM-W14-T05, LM-W14-T06, LM-W14-T07, LM-W14-T08, LM-W29-T05, LM-W30-T05, LM-W31-T06 |

| LM-013 | deferred and expanded | LM-W16-T01, LM-W16-T02, LM-W16-T03, LM-W16-T04, LM-W16-T05, LM-W16-T06, LM-W16-T07, LM-W16-T08, LM-W30-T01, LM-W31-T02 |

| LM-014 | deferred and expanded | LM-W17-T01, LM-W17-T02, LM-W17-T03, LM-W17-T04, LM-W17-T05, LM-W17-T06, LM-W17-T07, LM-W17-T08, LM-W18-T01, LM-W18-T02, LM-W18-T03, LM-W18-T04, LM-W18-T05, LM-W18-T06, LM-W18-T07, LM-W18-T08, LM-W30-T01, LM-W31-T02, LM-W31-T03 |

| LM-015 | deferred and expanded | LM-W19-T01, LM-W19-T02, LM-W19-T03, LM-W19-T04, LM-W19-T05, LM-W19-T06, LM-W19-T07, LM-W19-T08, LM-W31-T05 |

| LM-016 | deferred and expanded | LM-W20-T01, LM-W20-T02, LM-W20-T03, LM-W20-T04, LM-W20-T05, LM-W20-T06, LM-W20-T07, LM-W20-T08, LM-W30-T04, LM-W31-T01, LM-W31-T02 |

| LM-017 | deferred and expanded | LM-W21-T01, LM-W21-T02, LM-W21-T03, LM-W21-T04, LM-W21-T05, LM-W21-T06, LM-W21-T07, LM-W21-T08, LM-W30-T04 |

| LM-018 | deferred and expanded | LM-W22-T01, LM-W22-T02, LM-W22-T03, LM-W22-T04, LM-W22-T05, LM-W22-T06, LM-W22-T07, LM-W22-T08, LM-W30-T03, LM-W30-T06, LM-W31-T04 |

| LM-019 | split and expanded | LM-W05-T01, LM-W05-T02, LM-W05-T03, LM-W05-T04, LM-W05-T05, LM-W05-T06, LM-W05-T07, LM-W05-T08, LM-W23-T01, LM-W23-T02, LM-W23-T03, LM-W23-T04, LM-W23-T05, LM-W23-T06, LM-W23-T07, LM-W23-T08, LM-W28-T07, LM-W28-T08, LM-W29-T01, LM-W29-T02, LM-W29-T03, LM-W29-T04, LM-W29-T05, LM-W29-T06, LM-W29-T07, LM-W29-T08, LM-W30-T08 |

| LM-020 | split and expanded | LM-W04-T01, LM-W04-T02, LM-W04-T03, LM-W04-T04, LM-W04-T05, LM-W04-T06, LM-W04-T07, LM-W04-T08, LM-W24-T01, LM-W24-T02, LM-W24-T03, LM-W24-T04, LM-W24-T05, LM-W24-T06, LM-W24-T07, LM-W24-T08, LM-W03-T01, LM-W03-T02, LM-W03-T03, LM-W03-T04, LM-W03-T05, LM-W03-T06, LM-W03-T07, LM-W03-T08, LM-W28-T01, LM-W28-T04, LM-W28-T05, LM-W28-T06, LM-W28-T07, LM-W28-T08 |

| LM-021 | split and expanded | LM-W05-T01, LM-W05-T02, LM-W05-T03, LM-W05-T04, LM-W05-T05, LM-W05-T06, LM-W05-T07, LM-W05-T08, LM-W25-T01, LM-W25-T02, LM-W25-T03, LM-W25-T04, LM-W25-T05, LM-W25-T06, LM-W25-T07, LM-W25-T08, LM-W04-T01, LM-W04-T02, LM-W04-T03, LM-W04-T04, LM-W04-T05, LM-W04-T06, LM-W04-T07, LM-W04-T08, LM-W28-T04, LM-W28-T06, LM-W28-T07, LM-W28-T08, LM-W29-T01, LM-W29-T03, LM-W29-T06, LM-W29-T07, LM-W29-T08, LM-W30-T06, LM-W30-T07 |

| LM-022 | split and expanded | LM-W05-T01, LM-W05-T02, LM-W05-T03, LM-W05-T04, LM-W05-T05, LM-W05-T06, LM-W05-T07, LM-W05-T08, LM-W26-T01, LM-W26-T02, LM-W26-T03, LM-W26-T04, LM-W26-T05, LM-W26-T06, LM-W26-T07, LM-W26-T08, LM-W28-T07, LM-W28-T08, LM-W29-T08, LM-W31-T05 |

| LM-023 | split and expanded | LM-W05-T01, LM-W05-T02, LM-W05-T03, LM-W05-T04, LM-W05-T05, LM-W05-T06, LM-W05-T07, LM-W05-T08, LM-W27-T01, LM-W27-T02, LM-W27-T03, LM-W27-T04, LM-W27-T05, LM-W27-T06, LM-W27-T07, LM-W27-T08, LM-W28-T07, LM-W28-T08, LM-W29-T08, LM-W31-T06 |

| LM-024 | split and expanded | LM-W05-T01, LM-W05-T02, LM-W05-T03, LM-W05-T04, LM-W05-T05, LM-W05-T06, LM-W05-T07, LM-W05-T08, LM-W27-T01, LM-W27-T02, LM-W27-T03, LM-W27-T04, LM-W27-T05, LM-W27-T06, LM-W27-T07, LM-W27-T08, LM-W28-T07, LM-W28-T08, LM-W29-T08, LM-W30-T08, LM-W31-T06 |
