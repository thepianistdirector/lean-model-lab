# Fresh native dependency-slice confirmation

The complete 128-question dependency-slice confirmation has finished, passed the independent raw audit, and been exported. The other two predeclared policies are still separate execution work. No confirmation outcome has changed their already-frozen recipes or controller.

Both repetitions produce the same classifications. Full context is correct on 23/128 questions (17.96875%), and dependency slicing on 34/128 (26.5625%). The aggregate increase hides 13 harmed questions. All 128 original and sliced programs independently resolve to the same symbolic answer, so the certificate remains valid while native task behavior changes.

| Outcome per complete 128-question pair | AB | BA |
| --- | ---: | ---: |
| Both correct | 10 | 10 |
| Full correct, slice wrong | 13 | 13 |
| Full wrong, slice correct | 24 | 24 |
| Both wrong | 81 | 81 |
| Full correct / offered | 23/128 | 23/128 |
| Slice correct / offered | 34/128 | 34/128 |
| Observed full/slice oracle | 47/128 | 47/128 |
| Full SLO-qualified / offered | 1/128 | 1/128 |
| Slice SLO-qualified / offered | 6/128 | 6/128 |

The per-pair oracle is 47/128 (36.71875%). The conservative rule requiring one arm to be correct in every repetition gives the same 47/128. These ceilings apply only to choosing between the retained native full/slice outputs. They do not bound new outputs, different prompts, other models or all possible controllers. No opportunistic mixing across repetitions is used.

The unchanged 95% absolute floor fails by a large margin. The candidate's larger aggregate correct count does not erase the full-only cases, and descriptive timing does not become an eligible efficiency gain.

## Complete constituent families

Each row is a constituent part of the same mixed population, with the same counts in both repetitions. These are descriptive strata, not independent 128-question experiments.

| Family | Offered per pair | Both correct | Full only | Slice only | Both wrong | Oracle |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct lookup | 43 | 10 | 11 | 12 | 10 | 33/43 |
| Reference chain | 43 | 0 | 1 | 4 | 38 | 5/43 |
| Updates | 42 | 0 | 1 | 8 | 33 | 9/42 |

The generator uses C-prefixed keys and values for confirmation, whereas development uses D-prefixed names. This namespace difference and independently derived random streams are part of the pre-existing frozen generator. Exact table-body group separation is verified, but IID exchangeability and lexical invariance are not assumed.

## Prospectively selected illustrations

The rule frozen before native confirmation selects the first repeated harmful direct lookup, falling back to another family only if none exists. It selects `r009`: the original table contains `VALUE COWPG CGMSA`, and the query is `ASK COWPG`. The valid one-record slice retains exactly that line, original zero-based line index 13. Both programs resolve to `CGMSA`. Full native output is `CGMSA`; sliced output is the key `COWPG`, in both repetitions, each finishing at EOS. Raw SSE shows four generated tokens including EOS in each arm, a 32-token cap, no truncation, and zero reused prompt tokens. This is a fresh confirmation example, separate from the earlier D-prefixed development case.

The first repeated benefit is `r003`: `VALUE COUKW CAMYD` and `ASK COUKW`. Full native output is `COKSW`, while the slice returns the expected `CAMYD`, again in both repetitions at EOS.

Complete prompts, output token IDs independently reconstructed from raw native SSE, every repetition, certificates and exported-file hashes are retained in [the harmful illustration](publication/artifacts/confirmation-illustrations-stage1-v3/harmful-r009.md) and [the beneficial illustration](publication/artifacts/confirmation-illustrations-stage1-v3/beneficial-r003.md), with companion JSON. The complete [request table](publication/tables/confirmation-stage1/requests.csv) and [paired table](publication/tables/confirmation-stage1/paired.csv) retain the entire population; the illustrations do not select the evaluation denominator.

## Actual cost and qualification

| Measure | Full AB | Slice AB | Full BA | Slice BA |
| --- | ---: | ---: | ---: | ---: |
| Full attempt wall, seconds | 259.595 | 131.789 | 264.110 | 131.529 |
| End-to-end p95, seconds | 245.288 | 123.011 | 249.460 | 122.995 |
| Prompt tokens | 35,257 | 13,473 | 35,257 | 13,473 |
| Generated tokens | 545 | 550 | 545 | 550 |

Prompt tokens fall while generated tokens are slightly higher after slicing. These are actual measured quantities, not an output-length-matched experiment or a qualified speedup. Exact-answer-plus-SLO qualification requires TTFT at most 15 seconds and end-to-end completion at most 30 seconds from arrival, with all 128 arrivals simultaneous. Full qualifies one question and slice six per pair; every offered question remains in each fraction.

The four attempt walls total 787.023751611 seconds. Enclosing queue execution takes 800.030817060 seconds; those scopes overlap. The preceding 39.000432789 minutes of shared-queue waiting remains charged to the original allocation clock, and is separate from native execution. Across the two closed diagnoses, three development studies and this first confirmation study, 960 native requests have completed in 1,953.505183883 seconds of enclosing execution. No native or allocation limit is reset.

The six-export portable reanalysis passes, including exact producer hashes, complete request and arm inventories, independently reconstructed dependency prompts, body-group separation, all four classes, symbolic preservation, native correctness and qualified-service counts. All remaining policy recipes and the actual `ALWAYS_FULL` artifact remain unchanged.


Final status: all three frozen policies subsequently completed. This document retains the first-study snapshot; the [final manuscript](manuscript.md) and [eight-export final analysis](publication/tables/final/analysis.json) supersede its interim campaign totals. No policy, seed or threshold changed.
