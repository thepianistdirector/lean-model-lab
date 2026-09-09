# Candidate controller investigation: development feasibility

The first native 14B feasibility cell fails the prospectively frozen admission rule. Full context answers 1 of 8 questions correctly in each counterbalanced repetition; dependency slicing answers 2 of 8. The 95% absolute gate requires 8 of 8 in this cell. No main training or confirmation study follows from this result.

The experiment uses the actual packaged product archive `f90c48dd0be36b29c3188c365ba6b8ab2cbe709897cd7f4cce0e4825a147db6f`, Qwen2.5-14B-Instruct FP16 on the admitted CPU adapter, the unchanged `reference-chain` RECORD-LANGUAGE v1 generator, context eight, eight requests, seed 920260801, concurrency one, six compute threads, and two AB/BA pairs. Thirty-two native requests were offered and retained, representing eight unique questions. All four attempts completed; completion does not establish answer correctness. Independent raw reconciliation passed. These are development observations, with no confidence claim over a broader population.

| Pair | Full correct | Slice correct | Both correct | Full only | Slice only | Both wrong |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| AB | 1/8 | 2/8 | 0 | 1 | 2 | 5 |
| BA | 1/8 | 2/8 | 0 | 1 | 2 | 5 |

The aggregate gain of one answer hides a real harmed question. On `r007`, the full prompt produces the expected `DXEDM`, while the semantics-preserving slice produces `J` in both repetitions. On `r003`, the full model stops at a key (`DMDUF`) while the slice correctly returns its assigned value (`DPCYN`). These observations are compatible with an acceptance controller having a useful target, but the five jointly wrong questions and zero jointly correct questions make this cell unsuitable as evidence for a 95% serving-quality system. No baseline failures were excluded or relabeled as safe success.

Some failures suggest instruction interpretation problems. For example, `r000` expects `DZQRB`, but both arms natively emit `B` followed by EOS, with token IDs `[33,151645]`. The incorrect one-letter answer exists in the native stream and is not a report truncation. A full-context `r002` answer adds an explanation and reaches the fixed 32-token cap. This diagnosis motivates one bounded wording test; it does not justify retroactively changing this task, its score or its gate.

| Pair | Full attempt wall (s) | Slice attempt wall (s) | Slice/full descriptive ratio | Full p95 end-to-end (s) | Slice p95 end-to-end (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| AB | 138.180 | 93.112 | 0.674 | 120.929 | 75.915 |
| BA | 139.699 | 93.352 | 0.668 | 122.085 | 75.945 |

The ratios are cost descriptions, not eligible efficiency improvements. Prompt tokens are 1,184 per full attempt and 864 per slice attempt; output tokens differ (54 versus 21), so shortened incorrect outputs contribute to apparent savings. The simultaneous arrival schedule means end-to-end tails include queueing for all eight arrivals, not just isolated request execution. There is no cross-request KV reuse. Full attempt wall includes verification, load, service and shutdown; the four attempts sum to 464.344 seconds, while the queue's enclosing product execution is 468.326 seconds. Those scopes overlap and must not be added.

The already-incurred acquisition/build/setup and prior attempts remain in the product's allocation accounting. The report records the original allocation through its latest retained producer observation, including intervening idle/development time. It also carries historical preparation ancestry separately. These totals overlap the current attempts and are not incremental sums. Energy, thermal and monetary cost were not measured. The planned 1,792-request main campaign at this model's observed context-eight cost would already exceed its 180-minute native budget before the intended larger context; this is an extrapolation, not a measured context-24 result.

The earlier 0.5B product workflow remains adverse evidence: all arms answered 1/8 correctly. One additional 32-request development diagnosis is authorized: on that smaller model and the same eight reference-chain records, compare unchanged full-context v1 against full-context instructions with explicit operand definitions and a fixed unrelated example. Records, questions and expected answers must be identical. The clarified arm must achieve 8/8 in both repetitions and permit the bounded main campaign's remaining cost to advance. A failure ends prompt/seed search within this investigation. It is a wording diagnosis, not a rescued eligible model-compression comparison or evidence of novelty.

Artifacts live under `.cache/v1-investigations-20260908/candidate/`: the original freeze (`00-feasibility-rule.json` and receipt), exact recipe, raw study, queue receipt, packaged inspect/report/workbench command captures, raw audit, relocatable export and `feasibility-14b-analysis03/{analysis.json,requests.csv,attempts.csv,pairs.csv}`. The read-only `analyze_feasibility.py` recomputes all four correctness classes from retained native outputs, checks them against the packaged report's correct counts, and writes descriptive costs without changing product eligibility.

## Closed clarification diagnosis

The32-request archive04 wording diagnosis has completed: unchanged0.5B full v1 is1/8 in both pairs, explicit full v2 is0/8 in both. The frozen positive-advance rule fails and that branch is closed. No further prompt/seed search is authorized by it. Both pairs have0 both-correct,1 full-only,0 explicit-only and7 both-wrong. Full attempt walls are10.191/10.117 seconds; explicit attempt walls15.412/14.398 seconds. Its54.700-second queue interval brings the two branches to64 native requests and523.026 seconds of native product execution.

Actual packaged inspect/report/workbench and export succeed; raw audit passes. `check_clarification.py` independently verifies all16 candidate prompts retain the exact original records/query/order and change only the three fixed instruction lines. No completion hits the token cap. All artifacts use the `clarification-0.5b-*04` prefix, with CSV/JSON/standalone figures in `clarification-0.5b-analysis04/`.

These64 observations do not themselves satisfy a substantive learned-mechanism or publication-readiness requirement. Any new negative-investigation contract must be reviewed separately and cannot reopen this stopped branch.
