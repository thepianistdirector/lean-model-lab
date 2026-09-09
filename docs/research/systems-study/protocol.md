# Systems and transfer protocol

This investigation asks when dependency-based context omission loses its apparent benefit against **full-context prefix caching**. It is a bounded CPU interaction study with known prior-art overlap, not a claim that prompt compression or cache-aware compression is new. The immutable initial stage plan is retained at `.cache/v1-investigations-20260908/systems/stage-plan.json`; every executed case also retains its packaged proposal, protocol, recipe and command receipts.

## Scope and prior art

[Cache-Aware Prompt Compression](https://arxiv.org/abs/2607.15516) directly studies the conflict between query-dependent compression and prefix caching. Its author-reported API pricing and cache-tier results motivate the question but do not predict latency on this CPU. [RECOMP](https://arxiv.org/abs/2310.04408) and [LLMLingua-2](https://arxiv.org/abs/2403.12968) establish relevant compression baselines; this study does not reproduce their learned compressors or benchmarks.

The candidate here is a classical deterministic dependency slice for an authored record grammar. An independent symbolic interpreter can solve that grammar without an LLM. A syntax/dependency certificate cannot guarantee model output or unchanged logits. The contribution sought is an informative measured boundary or counterexample, with actual cache histories and complete costs.

## Frozen feasibility stage

The first case uses Qwen2.5 0.5B FP16 profile `qwen2.5-0.5b-instruct-fp16-v2`, two compute threads, one native slot, `record-reuse`, 24 records, development seed `940101`, eight offered requests, and two balanced AB/BA pairs. The `slice-versus-full-cache-v1` mechanism enables the same cache setting in both arms: baseline receives the original table; candidate receives the query-dependent dependency slice. Each arm begins with its own real cold cache. All eight distinct queries per table remain in order; first use and table changes are never dropped as warm-up.

Cold prompt-cache history refers to native prefix/KV reuse. The study does not purge the operating system's file/page cache or claim that every model load begins from cold storage. Verification and loading costs are nevertheless charged in each observed full attempt envelope.

The feasibility gate is at least 95% exact answers in **each** full-context baseline attempt, which requires 8/8 in this small population. A failed small-model baseline is retained and does not trigger an expanded small-model confirmation sweep. A single predeclared 14B alternative may repeat the same generated table/query population with no more than six threads, after coordination with the root. This is model-selection development, not independent confirmation.

D1 failed that gate. Following root coordination, D2 was separately frozen before execution at `.cache/v1-investigations-20260908/systems/d2-large-reuse24/`: the same original `record-reuse` grammar, 24 records, seed `940101`, eight requests, two balanced pairs, concurrency one, six threads, Qwen2.5 14B FP16 profile v1 and `slice-versus-full-cache-v1`. D2 uses immutable archive 04, SHA-256 `5f1aabf84635e33dd166ee656d5bcb5830f25a5f4f5d68433e2fd3e4498fb986`, which preserves the original grammar semantics. It requires **both** arms to reach 8/8 in every repetition before any held-out efficiency matrix. A quality failure stops further model, seed and wording search. Any distinct held-out failure/system-cost challenge needs a separate prospective freeze and root coordination; it is not an automatic continuation of feasibility.

Earlier project observations—1/8 on a small-model reference-chain population and 6/8 on a small-model direct-lookup population—are motivation for this gate. They are different populations and are not results of this repeated-table investigation.

## Conditional confirmation design

No confirmation is authorized merely by this list. After feasibility, a separate finite matrix must be frozen before its first native request and coordinated against the shared queue and remaining clock. Potential cases are:

1. Both-cached full-versus-slice comparisons at 24 and 64 records, on separately seeded confirmation tables.
2. At the longer context, constituent controls: uncached full versus uncached slice, and full without cache versus full with cache.
3. One predeclared paced or burst trace if observed service feasibility justifies it. Arrival timing, queue capacity, deadlines and SLOs must be fixed before execution.
4. One matched 14B strong-cache comparison as the predeclared additional-scale alternative if small-model feasibility fails or a bounded model transfer is informative.

Each measurement case requires at least 128 offered requests per attempt and two balanced AB/BA pairs. The initial ceiling is five 512-request measurements plus at most 64 development requests: 2,624 new native offered requests. The investigator's hard limit is 3,000 new offered requests and 90 minutes of actual native execution. These are maxima, not target counts.

## Frozen held-out negative challenge

After both predeclared feasibility configurations failed quality, the root separately approved a substantive negative/system-cost challenge. All three cells below were frozen together before H1 entered the native queue, with timestamp, archive/implementation identities and every recipe/protocol hash in `.cache/v1-investigations-20260908/systems/heldout-matrix-freeze.json`:

| Case | Configuration | Original family | Records | Confirmation seed | Offered requests per attempt | Pairs | Threads |
|---|---|---|---:|---:|---:|---:|---:|
| H1 | Qwen2.5 0.5B FP16 v2 | record-reuse | 24 | 940129 | 128 | 2 | 2 |
| H2 | Qwen2.5 0.5B FP16 v2 | record-reuse | 64 | 940193 | 128 | 2 | 2 |
| H3 | Qwen2.5 14B FP16 v1 | record-reuse | 24 | 940129 | 128 | 2 | 6 |

Every cell uses archive 04, `slice-versus-full-cache-v1`, concurrency one, simultaneous arrivals and two AB/BA pairs. Each contains 16 new tables with eight changing queries each. H1 and H3 use the same prospective generated population for model transfer; H2 uses the separately seeded longer-context population. Both arms maintain their own actual cache histories. Each arm begins cold, but a later table's first use may still reuse a common instruction prefix; table boundaries do not force an artificial cache flush. The analysis distinguishes first use from subsequent queries without assuming that every table's first request has zero reused tokens. The full matrix offers 1,536 new native requests, for an investigator total of 1,600 including the 64 development requests.

The frozen hypotheses concern (1) first-use versus subsequent-query processed-token decomposition; (2) descriptive timing with output-length changes as an explicit confound and all cache preparation charged; (3) all four observed paired correctness classes, including the descriptive either-answer-correct ceiling, by table and pair; and (4) context/model transfer within the exact admitted configurations. This phase preserves the failed-quality regime to test informative failure conditions; it does not reopen search for a passing model, wording or seed. No cell is selected, replaced or discarded based on quality results, and all original gates remain authoritative. The observed either-answer-correct ceiling uses both outputs and the correct answer; it is not a free or deployable oracle.

Prospective execution estimates were 311.811, 617.713 and 2,361.707 seconds for H1/H2/H3. Their combined 1.5× safety allowance was 4,936.847 seconds, below the then-remaining 5,151.919-second native execution budget. Estimates scale the measured development service to 16 tables while retaining four non-service attempt envelopes; H2 initially uses an uncertain 2× small-model service factor for longer context. Before **each** queue launch, 1.5× the current estimate must fit both the remaining investigator execution allowance and the original allocation deadline. Actual H1 timing updates subsequent projections without changing tasks, hypotheses, settings or quality gates. Each budget admission is retained beside its case. Resource infeasibility stops the remaining cell rather than changing its population or silently extending the clock.

## Scientific gates and accounting

Both arms must achieve at least 95% exact task accuracy, with no observed pair-level aggregate accuracy decrease for the candidate. Report all four paired correctness classes: both correct, baseline-only correct, candidate-only correct and both wrong. A net aggregate result never hides individual harmful omissions. Same-input controls additionally require output-token parity; changed-input comparisons retain their differences without asserting logit equivalence.

The primary cost criterion is the platform's full-attempt wall, including verification, model load, transformation, tokenization and shutdown. Service wall, native new/reused input tokens, output tokens, client queueing, TTFT and completion tails remain separate descriptive measurements. A shorter prompt or a faster service phase alone does not establish a full-cost gain. Report sampled aggregate RSS and server VmHWM with their actual scope; no energy measurement or API-price conversion is available.

The accounting retains every failed, interrupted, adverse and prior study. Shared setup and ancestor costs are deduplicated by retained identities and time intervals. Per-study spans from the same original allocation are not added together. The report distinguishes current-investigation native attempt wall, inherited setup/prior work, and the original-allocation span through the final retained producer observation. Waiting and analysis remain inside the original clock.

Two balanced pairs support descriptive paired ranges, not precise confidence intervals or significance claims. Queries from the same table are dependent. Development and confirmation use distinct generator streams and namespaces; under one Unix identity this is workflow separation, not adversarial isolation. Any transfer applies only to the observed model, grammar, table/query distribution, hardware and cache history.

## Execution and stopping

All native execution uses the exact retained product archive through `tools/run_queued_recipe.py`; no scratch-model runner is permitted. The original allocation deadline is monotonic `310468865220540`, with one heavy job, at most 12 total compute threads, 60 decimal GB RAM and 200 decimal GB project disk. This investigation cannot reset that clock or independently enlarge the allocation.

Run each frozen cell once. Preserve failure, interruption and output-budget exhaustion; do not replace a failed confirmation, relax quality gates, remove cold primers, filter full-model errors, or pool counterfactual cache histories. Stop when the declared request/time cap or the original deadline would be exceeded. Final evidence must pass packaged `inspect`, `report` and `workbench`, the raw auditor, and local export verification. A later skeptical reproduction is a separate unfinished obligation until actually performed.
