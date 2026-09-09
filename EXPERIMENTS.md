# Lean Model Lab experiment and evaluation contract

Status: architecture-foundation requirements with an owner-directed research mission update on 8 September 2026. Real CPU cache controls and recovery observations exist; they validate the measurement foundation. General training and novel-mechanism results are not yet established. See [the research mission](docs/RESEARCH-MISSION.md) and [current evidence](STATUS.md).

## Question and comparison family

Each experiment asks whether one declared candidate changes a metric vector for one accepted comparison family while its hard constraints remain satisfied. The family fixes model semantics, tokenizer, data/workload population, evaluator, hardware class, runtime boundary and clock envelope. A result outside that envelope starts another family; it is not silently pooled.

The first implemented family is local decoder-only inference over a deterministic synthetic trace. Its known cache policy is an infrastructure control. Research proposals must separately name whether they reproduce a known method, combine existing mechanisms or test a proposed new mechanism; novelty remains an explicit review question. Training and model-changing hypotheses require appropriate adapters and quality evaluators, rather than inheriting the synthetic key-copy contract.

Research objectives distinguish efficiency at a declared quality level, quality at a fixed resource budget and a shift of the quality/resource frontier. Prior-art comparison, the proposed technical delta, strong baselines, ablations and cheap decisive falsifiers precede expensive measurement. A favorable synthetic or operator result may justify the next stage but does not constitute a general LLM improvement.

## Evidence classes

Every metric value carries one evidence class:

- `MEASURED`: observed from the declared timer, counter or sensor on the recorded system;
- `DERIVED`: deterministically computed from measured values, with formula and inputs retained;
- `MODELED`: produced by an analytical or simulation model with calibration and applicability limits;
- `ESTIMATED`: an explicitly approximate value that is not suitable for a measured-performance claim;
- `UNAVAILABLE`: requested telemetry was absent, unsupported, inaccessible or invalid.

Do not substitute one class for another. A reproducible simulation can still be a wrong model. A backend's reported duration can still omit client, queue, startup or evaluation time. The result names its boundary.

## Accepted specification

Before admission, freeze:

1. `ModelRecord`, `TokenizerRecord`, `DataRecord`, `WorkloadSpec`, `HardwareRecord` requirements, `RuntimeRecord` requirements and source revision;
2. baseline and one candidate delta, including parameters allowed to vary and all fields required to remain equal;
3. primary metric vector, direction, hard constraints, practical-effect threshold and Pareto preference or selection rule;
4. quality metric, target/equivalence rule, development-evaluation schedule, confirmation partition/access rule, evaluator version and forbidden leakage paths;
5. clock envelope, cache/warmup/compile/synchronization protocol, concurrency and repetitions;
6. attempt, wall-time, storage, memory and any monetary/energy budget, plus cancellation and stop rules;
7. invalidity conditions, failure taxonomy, uncertainty method and observation that would falsify the hypothesis.

Unknown execution fields, unresolved artifact identities, missing units or an unavailable hard requirement reject admission. A missing optional sensor marks its metric `UNAVAILABLE` and may continue only if the plan permits that before the run.

## Provenance and comparability

Model provenance includes architecture/config, exact weights and format, parameter-count convention, source/version, license/use terms, precision and loading policy. Tokenizer provenance includes every asset and rule that can alter token identity or count: normalization, pre-tokenization, vocabulary/merges, special tokens, templates, truncation and padding. Dataset provenance includes source snapshot, transformations, partition lineage, deduplication/leakage analysis and rights. Synthetic data includes generator source and seed.

Baseline and candidate must use the same accepted model, tokenizer, request/sequence population, quality evaluator and hardware/runtime envelope unless one is the sole declared independent variable. A tokenizer change changes token counts and comparison semantics; it is its own study. A quantized model can be a candidate only with explicit weight-format identity and quality/equivalence checks.

Hardware/runtime provenance includes OS, architecture, CPU/GPU/accelerator and memory, topology, driver/firmware, power/clock configuration where observable, backend/compiler/library builds, numerical modes, thread/affinity settings, process/container boundary and relevant environment. An upstream support table is not evidence that the current device passed a probe.

## Measurement protocol

### Common controls

- Use a monotonic high-resolution host clock for end-to-end events and a backend-appropriate synchronized timer for asynchronous device-only intervals.
- Declare cold and warm modes. Record model load, compile, allocator/cache preparation and warmup separately; never move them outside full campaign cost after seeing results.
- Record pre-run and run thermal state where exposed, power source, clock/power caps, competing processes, memory pressure and accelerator sharing. Mark unobserved conditions as such.
- Fix request trace and paired seeds where appropriate. Randomize or counterbalance baseline/candidate run order after required cold-start controls.
- Predeclare minimum and maximum repetitions from pilot variance and decision needs. Retain every attempt. Apply no post-hoc outlier deletion.
- Measure instrumentation overhead with a control when profiling can materially perturb the workload. Profiling runs and benchmark runs are distinct unless the plan justifies their equivalence.

### Training accounting

Record raw examples, source tokens, non-padding tokens presented, loss-bearing tokens, repeated exposure, optimizer steps, global/micro batch, accumulation, precision, optimizer/schedule and seed/data order. Report model-useful FLOP estimates separately from recomputation, communication and observed device activity. FLOP estimates state their formula and inclusion boundary.

Report cold full-wall time, initialization/compile, data preparation, training, evaluation/checkpoint, recovery and time to the selected quality decision. Predeclare the development-evaluation schedule in steps or non-padding tokens. The default confirmation rule freezes candidate/checkpoint selection, evaluates one selected checkpoint once on untouched confirmation data and reveals no confirmation result until training/search is closed. A sequential time-to-quality study must instead freeze all checkpoints first and predeclare their evaluation order, maximum confirmation accesses and statistically justified sequential/multiple-testing rule; intermediate outcomes cannot return to training or search. A fixed-token run does not establish time-to-quality; a fixed-time run does not establish equal compute; equal nominal FLOPs do not establish equal elapsed time. Preserve the checkpoints and access log needed to audit the decision.

### Inference accounting

For every offered request, retain its arrival, admission/rejection, backend start, first-token, token-gap and completion events; prompt/output token counts; finish reason; and terminal outcome. Report queue delay, TTFT, ITL, TPOT when defined, end-to-end latency, request/output-token/total-token throughput, SLO goodput and request tails by declared length/concurrency stratum. Include dropped, timed-out, rejected, cancelled, malformed and failed requests in denominators required by the plan.

Prefill and decode are separate phases with different load sensitivity. A candidate cannot claim throughput improvement by shortening outputs, changing sampling/stop rules, dropping slow requests or serving a different arrival trace. Offline saturation throughput and online open-loop latency are different workload modes.

### Memory, energy and monetary cost

Record host peak resident memory and backend-exposed allocated/reserved/peak accelerator memory with API semantics. KV-cache estimates and observed occupancy are separate. OOM is a retained terminal outcome.

Measured energy requires a declared sensor or API, measurement scope, units, sampling/counter method, baseline/idle treatment and missing-interval policy. A supported NVIDIA total-energy counter, sampled accelerator power, Apple/host instrumentation and external whole-system meter each have different scopes. Unsupported APIs, denied access or unclear scope produce `UNAVAILABLE`. Modeled joules and electricity/carbon estimates remain separately labeled and state their assumptions.

Monetary cost includes approved provider charges when applicable plus a declared local-cost model if used. Zero provider charge does not mean zero resource cost. Failed attempts, warmup, profiling, search and confirmation remain in campaign accounting.

## Candidate and evaluator isolation

The producer may propose `CandidateSpec` records and read development metrics. It cannot write accepted specs, evaluator source, confirmation cases, budget events or prior results. Evaluation consumes raw outputs through a versioned interface and emits validity, quality and metric records; it never edits the candidate.

Development, ablation and confirmation partitions are assigned before search. Confirmation inputs beyond the public workload contract, labels, expected outputs, evaluator logic and intermediate decisions are inaccessible to candidate and proposing contexts. Every evaluator access is logged. Repeated confirmation access outside the predeclared sequential/multiple-testing rule, benchmark-specific branching, contamination or overlap discovered after the fact invalidates the affected claim and triggers a new split or hold.

Application-level path checks and subprocess separation are insufficient for untrusted code. Before an untrusted candidate, contributed adapter or proposing agent executes—or protected confirmation begins—an OS sandbox, container or VM must enforce: read-only approved inputs; writable bounded scratch/output only; no credentials; network denied by default; hidden evaluator/protected data; and external CPU, accelerator, memory, process, wall-time and storage limits. Protected confirmation runs in a separate evaluator-controlled context. Failure to establish or attest those controls rejects admission. The initial prototype is limited to reviewed built-in code and inert development fixtures until this isolation gate exists.

Evaluator changes create a new version and reopen directly affected results. Thresholds and equivalence rules cannot be relaxed after seeing a candidate. A representative mutation must show the evaluator rejects changed tokenizer identity, missing requests, truncated output, altered quality threshold and a malformed measurement boundary.

## Search, ablation and multi-objective decisions

Start from profiler or trace evidence and a falsifiable mechanism. Evaluate isolated changes before interactions. All proposers—human, scripted search or agent—share the same accepted attempt/compute/time/cost budget. Save the full proposal and outcome sequence, including duplicates, invalid points and regressions.

Quality/correctness/safety constraints gate admission to the Pareto set. For valid candidates, report the vector of quality delta, cold/warm wall time, TTFT/ITL/tails, throughput/goodput, memory, energy availability/value and monetary cost. Do not collapse it to a scalar unless stakeholder weights and normalization were accepted before search. A selected point is “best under these constraints and preferences,” not universally optimal.

After search, freeze the selected candidate and run a fresh confirmation protocol on untouched cases. Confirmation consumes a separately reserved allocation fixed before access; search and confirmation both count toward total campaign cost. Confirmation must not feed another tuning loop. Outcomes are `PASS`, `NO_DEMONSTRATED_GAIN`, `QUALITY_REJECTED`, `INCONCLUSIVE`, `INVALID`, `HOLD` or `TERMINATE`.

## Run and campaign artifacts

A run attempt bundle contains:

```text
spec.json                 accepted experiment and comparison identities
candidate.json            one candidate delta and hypothesis
environment.json          runtime, hardware and capability probe
events.jsonl              append-only lifecycle and timing events
requests.jsonl            per-request inference events when applicable
training.jsonl            step/evaluation/checkpoint events when applicable
telemetry.jsonl           observations with source, scope and availability
stdout.log / stderr.log   bounded raw process diagnostics
metrics.json              evaluator-produced vector and constraints
result.json               terminal state, evidence classes and limitations
artifacts.json             lineage, sizes and retained output references
```

Write into an attempt-specific temporary directory, validate required files and publish atomically. Partial bundles remain clearly partial. Large/raw artifacts follow a predeclared retention rule; metadata, failures and derived claims never point to silently deleted evidence.

A campaign bundle adds the immutable search policy, ordered attempt ledger, budget ledger, Pareto set, selection decision, confirmation attempts and report. Negative and inconclusive results are first-class outputs because they constrain applicability and prevent repeated dead ends.

## Budget, cancellation and resumption

Admission reserves bounded attempts, elapsed wall time, artifact bytes and any approved monetary allocation. The journal records reservation, start, incremental usage, release and terminal reconciliation. A retry receives a new attempt ID. Budget exhaustion stops new admission and closes running work according to the accepted cancellation policy; it does not trigger automatic paid or larger compute.

Cancellation persists before signaling the process tree, then records grace/forced termination and final resource use. After restart, the coordinator replays the journal and checks worker identity, process liveness, temp artifacts and budget. It may resume only from a compatible declared checkpoint; otherwise it closes the abandoned attempt and starts a separately identified retry if budget remains.

Future remote workers require capability matching, expiring leases, idempotent submission and enforced OS/container/VM isolation. They cannot receive protected evaluator data or credentials. Disconnected work cannot extend its lease. Results are quarantined until provenance and schema validation completes.

## First no-compute harness entry

The first implementation packet validates contracts without installing a backend, downloading a model or running inference/training. It must accept a synthetic 128-request trace contract with four prompt-length strata, maximum 32 requested output tokens, fixed seed, concurrency modes 1 and 4, explicit quality placeholder and zero monetary budget; emit normalized JSON; and reject one trace with a missing tokenizer identity and one with an impossible timestamp/order or negative token count.

That packet also records a local capability inventory and chooses one exact decoder-only model/tokenizer/backend combination that is small enough for the reviewed device. Model weights remain unacquired until source, license, safe-loading and redistribution/use terms pass review. CPU is the required control; Metal is conditional on a probe; CUDA is out of scope until a CUDA host is explicitly available. It executes no untrusted candidate or agent code and uses only reviewed built-in logic plus inert development fixtures.

## Stop and claims

Stop or hold when rights/provenance are missing, the evaluator is compromised, the budget is exhausted, the device falls outside the accepted envelope, required quality cannot be evaluated, results are dominated within the chosen constraints or the practical effect is below noise. Preserve the evidence before replanning.

No run may imply cross-model, cross-tokenizer, cross-backend or cross-device portability without separate evidence. No local plan validator, fixture parser, profiler trace, simulation or agent interpretation is a benchmark result.

## Narrow 0.1 successor contract

`docs/benchmarks/first-workload.md` predeclares a synthetic exact-key task quality rule, output parity as an additional constraint, paired order and measurement boundaries. `workloads/synthetic-key-copy-v1.json` is the generated immutable 128-request trace, with four filler-word strata (actual tokenizer IDs/counts are retained in the 2026-09-08 measured evidence), maximum 32 requested output tokens and concurrency modes 1 and 4. Its model-free validator rejects changes to prompt, answer, quality, sampling and arrival semantics. The historical quality placeholder is preserved only in lineage; it cannot admit a measured 0.1 run.

The historical no-compute entry above is preserved as its original contract. Actual CPU inference and recovery now have separately dated evidence in STATUS.md. The paid-compute budget remains zero; unsupported measurements remain UNAVAILABLE. Public reproduction, qualified-review evidence and native Tanduna publication remain distinct required release gates. The owner-directed research programme builds on these controls and does not rename them as novel techniques.
