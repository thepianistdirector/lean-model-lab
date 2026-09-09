# Prospective 14B measurement and serving recipes

Frozen on 8 September 2026, after the separately labeled development and recovery controls and before any of the three measurement recipes execute. All three use the same approved allocation ending at monotonic `310468865220540`; no new clock or resource budget is created.

## Common contract

Use the reviewed Qwen2.5-14B-Instruct FP16 eight-shard profile and pinned llama.cpp CPU binary with the reviewed GCC 8 patch. Use 128 synthetic key-copy requests, seed 20260908, output ceiling 32 tokens, twelve compute threads, and the same frozen exact-answer threshold of 95%. The only paired policy change is `cache_prompt: false` versus `true`. Native token output, prompt token count and token-ID parity remain required; thresholds and responses will not be adjusted after observing measurement results.

The development control used eight requests and two pairs: 32/32 exact answers and both token-parity checks passed. Its native readback reconciled all 32 streams. It remains ineligible as a development study. The actual recovery control retains the original two checkpoints and eight successfully restarted requests, with original identities, costs and interruption. Neither control supplies protected confirmation or a performance claim.

Main and serving studies automatically retain every locally discoverable producer from this exact allocation, including incomplete or adverse history. Admission refuses damaged/unreconciled producers. Explicit predecessor arguments cannot hide a discovered study. Validated identical originals deduplicate by their event histories, and redacted exports cannot replace original producers. This does not authenticate deleted or external evidence.

## Declared schedules

| Recipe | Arrivals | Concurrency | Pairs | Waiting queue | Pre-dispatch deadline | SHA-256 |
| --- | --- | --- | --- | --- | --- | --- |
| Main finite batch | All 128 offered at the service epoch | 1 and 4 | Four AB/BA pairs per mode, sixteen arm runs | 128 | None | `d7337c983048b83dfab1cf218cb91da24b60f086f783f5a7fa184bddb7dd0a80` |
| Paced low-load probe | One request every 21 seconds | 4 | Two AB/BA pairs, four arm runs | 16 | 30 seconds from offered arrival | `862423ac8ae9984f00702a7d2f5b992da20ca00f7ce40054f339f61b81b33d42` |
| Burst saturation probe | Sixteen requests per burst, one burst per second | 4 | Two AB/BA pairs, four arm runs | 8 | 30 seconds from offered arrival | `a2c699eea6a77ed39bceb570a0858875e5f35dd8de0026e524a23f9d4e3e6e7b` |

The main batch supports a device-specific paired cache comparison if all quality, parity, completeness and cost gates pass. The two shorter serving schedules are exploratory matched-load probes; they do not supply a calibrated capacity frontier or precise confidence intervals. Each recipe is evaluated independently. No gain is pooled across recipes, models or studies.

For every recipe, illustrative SLOs remain the existing 15-second offered-arrival-to-first-token and 30-second offered-arrival-to-completion thresholds. They are not production requirements from a customer or universal latency targets. The finite batch deliberately makes queueing visible and is not described as an online service.

The low-load interval was selected only from baseline development dispatch-to-completion observations: sixteen requests, maximum `16475010280` ns. The rule is `ceil(1.25 × maximum seconds)`, yielding 21 seconds. Candidate answers or measurement outcomes do not enter the rule. The measured offered span will be 127 × 21 seconds = 2667 seconds per arm. Engine dispatch, server processing, output-token receipt and declared arrival remain different clocks/scopes.

The saturation probe intentionally offers substantially more work than the observed baseline pace. Overflow and deadline expiry remain visible zero-dispatch outcomes with all 128 requests in quality and qualified-fraction denominators. Ineligible quality or parity must suppress comparison ratios even if a serving metric looks favorable. Completed scheduler accounting alone is not successful inference.

## Frozen measurement implementation

The verified local measurement archive is `.cache/packaged-0.4-measurement-20260908-01/lean-model-lab.pyz`, SHA-256 `5ae4372aa38b68dbe4a198e431602b1e98a127727020bcb666b10d1af29d497f`, implementation SHA-256 `a6b3eb37382d4eec4325d1f5ad85c233a15a1b2d252acaa9a2a36fa5586d44fe`. It follows 200 passing source tests and twelve isolated archive checks. It adds automatic predecessor discovery and the completed workbench fixes after the earlier development archive. Development/recovery retain their original archive identities and are not relabeled as having executed this later implementation.

## Execution and stop rules

Run the main study, then the paced probe, then the saturation probe, with one heavy job at a time. Retain all prior costs once, automatically and with explicit predecessor references for readability. Every attempt verifies all shard and backend identities; the exact measurement archive and implementation digest are recorded with the execution receipts. Frozen source and recipe identities cannot change during a study or its recovery.

A failed arm, resource breach or original-deadline exhaustion ends that run and remains visible. Do not silently retry a measured cell or replace a failed campaign with a successful same-recipe study. If the remaining original allocation cannot support a later predeclared control, leave it unexecuted with an explicit gap; do not shorten its population or reset the budget. A null or ineligible finding is retained as the result.

Expected work, if all schedules complete: 3072 offered requests across 24 measured arm runs, plus the separately retained 42 development/recovery request observations. Rejected requests count as offered work, not as engine-generated responses. Actual counts and resource observations must be read back from immutable inventories.

The host is shared and its clocks/probes are local. Record observed load and owned-process RSS scopes; do not infer energy, thermal state, isolated-host performance, external authenticity or human validation. Public release, native Tanduna publication and external/human gates remain separate from these local measurements.
