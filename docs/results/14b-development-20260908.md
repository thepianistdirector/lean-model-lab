# 14B development and recovery observations — 8 September 2026

The first real 14B development control completed 32 requests with 32 exact answers, and both paired token-parity checks passed. The native-response audit reconciled all 32 requests. **This remains an ineligible development study, not a measured efficiency gain or confirmation result.** The complete measurement and serving recipes are separately frozen in [the prospective protocol](../decisions/14b-measurement-recipes-01.md).

## Native compatibility and resources

The actual model is official Qwen2.5-14B-Instruct-GGUF FP16, revision `b466e1f8c07172155743e8e1307507d8a4f91fbd`. All eight reviewed shards, totaling 29,547,716,864 bytes, passed exact SHA-256 and size verification. The first-shard GGUF metadata declares Qwen2, eight splits and 579 tensors in total; that first file contains 57 tensors. Its embedded GPT-2 tokenizer has 152064 entries and Qwen ChatML special tokens at 151643–151645. [The metadata inventory](../evidence/14b-first-shard-metadata.json) is a scoped parser observation, not a tensor execution test.

The CPU backend is the pinned llama.cpp source plus reviewed GCC 8 compatibility patch. Its actual binary SHA-256 is `e6e4555daed18ae36a87276f16bd4c9f859c92787884b726b7967474d8c4681e`. The exact development archive SHA-256 is `27cb76d6165df86f608f9e93c695d1bd6ffd9512e32b352bd2802728e2fbbac9`; implementation SHA-256 is `a7224434ec9afb92fddce70483c42801d7b1bae3550bb9a928218439712985f9`. Each invocation verified actual shard/backend bytes, native version, one slot with context 2048 and tokenized input IDs before service.

The backend had CPU affinity restricted to twelve logical CPUs and twelve configured compute threads. Its additional service/I/O threads are distinct from compute-thread count; the process affinity covers all of them. A direct process read also confirmed inheritance of the project heavy-job lease. Maximum **sampled backend-plus-coordinator RSS** across the development arms was 30,171,955,200 bytes. This is not a continuous allocation-wide peak, physical-memory exclusivity, energy measurement or thermal measurement.

## Retained development outcomes

Recipe SHA-256: `28a1de610c82ff42cd01ff0bca24414b2629c3fb91832b0f45eb0173dcaa54a4`. Eight requests, seed 20260908, output ceiling 32, concurrency one, two pairs in AB/BA order.

| Execution order | Arm | Exact answers | Status | Attempt full wall |
| --- | --- | --- | --- | --- |
| Pair 1, first | Baseline | 8/8 | COMPLETED | 96.618 s |
| Pair 1, second | Candidate | 8/8 | COMPLETED | 64.379 s |
| Pair 2, first | Candidate | 8/8 | COMPLETED | 62.980 s |
| Pair 2, second | Baseline | 8/8 | COMPLETED | 96.006 s |

Both pairs have matching output token IDs, reported generated counts and prompt counts. The [native audit](../evidence/14b-development-raw-audit.json) verifies actual tokenizer inputs and cached/new/generated token accounting. Baseline cache reuse is zero; candidate reuse was observed. No ratio is promoted from this feasibility control: its purpose and population force ineligibility.

At the last producer observation, registered full wall was 4130.088 seconds from the original allocation start, including earlier acquisition, build, development, checks and idle work. The dedicated setup/attempt intervals account for 1759.600 seconds; 2370.488 seconds remain attributed to intervening coordinator/development/idle wall. Required setup costs are recorded, not assumed zero. Later report/export and measurement work continue consuming the same original allocation; this historical cutoff is not its closure.

## Actual interruption and restart

The [recovery receipt](../evidence/14b-recovery-verification.json) records the same frozen development archive and recipe. The harness killed only its new coordinator after two durable request checkpoints. The owned backend stopped. An intentionally damaged local journal index was archived byte-for-byte and rebuilt from authoritative events; reconciliation retained both observed requests without alteration.

Resume used a new attempt ID and completed eight native requests successfully. The control stopped at that first replacement cell and retained two terminal attempts with ten observed requests. The original interrupted attempt digest remained unchanged. The original monotonic deadline and allocation start were preserved; no extra comparison or fresh budget was created. SIGINT occurred after the replacement completed and produced coordinator exit `-2`; final reconciliation verified complete inventory before the control reported PASS.

Recovery establishes this local same-boot path. It does not establish cross-boot recovery, external execution, human interpretation or a released artifact. The interrupted study remains scientifically ineligible even though its replacement requests succeeded.

## Legacy readback and prospective use

Current source re-evaluated all three retained 0.1 inventories without loading a model. Their canonical results are unchanged: comparison `4e37092fcbd709110b0802974690501fe6999ec72221c7fb3908986d9f8cf37b`, protocol failure `a5dbae47d1d25086dc31821daa0d487177168413ccc6cd2c5a5dd5df01b90bb9`, and recovery control `51b3513403b51a7dd09cd66d7d1527919063642a0b2fcc9362505ae56927adf2`.

Only the sixteen baseline development dispatch-to-completion observations informed the later 21-second paced-arrival interval. [The calibration receipt](../evidence/14b-serving-calibration.json) records the maximum and fixed rounding rule. The quality rule, token ceiling and illustrative 15/30-second SLOs remain unchanged. All development/recovery observations and costs are carried into subsequent same-allocation studies once. Their presence cannot turn the later work into protected confirmation.
