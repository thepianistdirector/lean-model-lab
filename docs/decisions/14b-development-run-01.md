# First 14B feasibility recipe

Recorded before the first 14B inference, 8 September 2026. This is a development control under the already approved 12-hour allocation; it cannot qualify as a measurement claim.

The frozen archive is `.cache/packaged-0.4-dev-20260908-02/lean-model-lab.pyz`, SHA-256 `27cb76d6165df86f608f9e93c695d1bd6ffd9512e32b352bd2802728e2fbbac9`; implementation SHA-256 `a7224434ec9afb92fddce70483c42801d7b1bae3550bb9a928218439712985f9`. The recipe SHA-256 is `28a1de610c82ff42cd01ff0bca24414b2629c3fb91832b0f45eb0173dcaa54a4`.

Run eight generated requests, seed 20260908, output ceiling 32 tokens, concurrency one, two balanced AB/BA pairs, twelve compute threads and the reviewed eight-shard Qwen2.5-14B FP16 profile. The baseline disables prompt caching and the candidate enables it; other settings remain paired. Development sampling remains synthetic exact-key copying, with all four strata represented. The 95% exact-answer criterion and token-parity checks remain visible, while the development purpose always prevents eligibility.

This control establishes native model loading, tokenizer/stream compatibility, observed duration and feasibility within RAM/CPU limits. Its baseline timing may inform a separately frozen serving-arrival recipe before that recipe executes. It does not provide protected confirmation, justify tuning answers/thresholds, or permit dropping failed attempts. All costs and every observed outcome must remain in the predecessor ledger of later studies in this allocation. The original allocation deadline is unchanged.

The first shard's actual GGUF metadata was inspected before execution. It declares the Qwen2 architecture and GPT-2 tokenizer, 152064 vocabulary entries and Qwen ChatML special tokens at 151643–151645. Its template supports the same system/user/assistant envelope used by the reviewed adapter. Exact shard hashes bind the tokenizer bytes; these observations do not imply token ID compatibility with the older 0.5B vocabulary. Cross-profile studies remain separate families.

Required post-run readback: immutable attempt inventory, actual slot/context settings, tokenized input IDs, raw terminal sampling/token/cache values, exact answers, token parity, observed aggregate RSS and all-wall allocation accounting. Any failure is retained and blocks advancing through the affected runtime gate until diagnosed.
