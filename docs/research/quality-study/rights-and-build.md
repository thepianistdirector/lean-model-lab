# Rights, producers and source inventory

The manuscript, tables, original generated task data and project analysis code follow the repository's AGPL-3.0-only license. The original task grammar and generated records contain no external private dataset. A symbolic interpreter can solve this restricted task family; this benchmark does not establish general language competence. Model weights and the native backend binary are separately acquired dependencies and are excluded from the research exports.

| Item | Exact source / producer | Rights and scope |
| --- | --- | --- |
| Historical 14B model | `Qwen/Qwen2.5-14B-Instruct-GGUF`, revision `b466e1f8c07172155743e8e1307507d8a4f91fbd`; 8 FP16 shards, 29,547,716,864 artifact bytes | Apache-2.0 declaration in pinned official profile; all shard hashes retained in `summary.json` |
| Both 0.5B observations | `Qwen/Qwen2.5-0.5B-Instruct-GGUF`, revision `9217f5db79a29953eb74d5343926648285ec7e67`; SHA-256 `8e0ae26000627ed62de0e78e41860af70094558b9d2913385c842a6aa06cf3fc` | Apache-2.0 declaration in official pinned profile; unchanged model bytes |
| New 0.5B profile | `qwen2.5-0.5b-instruct-fp16-v2`, profile SHA-256 `13e85926dcbbf56e3004f3c72b8375d1b921355c15579ee92bb8bf141a5396e4` | Correct artifact size 1,266,425,696 bytes; v2 did not exist in historical 0.1 runs |
| Native backend | `ggml-org/llama.cpp` revision `bb4caa7540188872173c44d161602d9271386413` plus local patch SHA-256 `598d10a911e4d9c33926bd2dfd75735d143b84db14ad644a7502f35bec8e0f1c` | MIT upstream; retain the project notices and local GCC8 compatibility patch |
| 0.5B backend binary | `22bb24feddd1b44d0b793d044fd86dad4119b40d5485e58d9a6213d296cf71b2` | Existing prepared CPU build; byte verification before new native execution |
| 14B backend binary | `e6e4555daed18ae36a87276f16bd4c9f859c92787884b726b7967474d8c4681e` | Separate existing prepared CPU build |
| Shared template | SHA-256 `5e72fa95f7f6782b2363d5a3e2f93e181098b914d2994180b050ad8fc67196f7` | Exact tokenizer/template bindings remain in configurations |
| Historical 0.5B comparison producer | Archive `9550fd27836ea280c3fca8b3613c327be618b278bbf94457e2346523d2bc6c3d`; implementation `afa23358b906f0514c9bb74767c7846dd9345a9a3c162e45e5a7ed9770367fc4`; `0.1.0.dev0` | Measured historical producer; do not substitute v1 identity |
| Historical 14B measurement producer | Archive `5ae4372aa38b68dbe4a198e431602b1e98a127727020bcb666b10d1af29d497f`; implementation `a6b3eb37382d4eec4325d1f5ad85c233a15a1b2d252acaa9a2a36fa5586d44fe`; `0.4.0.dev0` | Retained `.cache/packaged-0.4-measurement-20260908-01/lean-model-lab.pyz` |
| New native development and present CLI inspection | Archive `f90c48dd0be36b29c3188c365ba6b8ab2cbe709897cd7f4cce0e4825a147db6f`; implementation `fe572bc610c0bc395672bf8b4e8f681260e2e6bdccf4280d6a7ec0784c30d5fe`; `1.0.0.dev0` | `.cache/packaged-v1-platform-20260908-03/lean-model-lab.pyz` |

The historical source documentation once quoted 1,266,425,774 as 0.5B model bytes. The [versioned correction](../../decisions/0.5b-profile-size-correction.md) explains that it was acquisition-directory growth; the current artifact is 78 bytes smaller. Historical declarations remain unchanged. This is a metadata correction, not changed weights or an explanation for quality differences.

The historical 0.5B source supplied here is an already prepared derivative. Its `original-provenance/` directory, `EXPORT-READY.json`, report and export-provenance manifest in `.cache/public-evidence-0.4-20260908/legacy-comparison/` preserve lineage. The protocol-failure derivative has its own corresponding lineage. The main 14B original is separately retained, with verified derivative `.cache/v1-export-14b-main-20260908-01`. The new verified derivative is `.cache/v1-investigations-20260908/quality/development-export`.

Permitted path redaction changes raw bytes and dependent hashes. Derivative raw streams are not byte-identical originals. Model paths in operational metadata may become filenames; scientific settings, normalized responses, tokens, timings, scores and adverse history must remain equal. The new export changed 36 raw files, retained all 32 offered/observed responses, and was verified by `tools/export_study.py`; its report hash is `c54a9da3961dd095a922e636885b854b45f1b1e0fcab5ab44aaac6f488ae625a` and provenance hash `51f1057095342fffc6889b89c0cefaf3e7df57bcddc2d6449da6a54728f70c75`. All exports remain local and unpublished.

`source-inventory.json` records raw/normalized/settings/source sizes and hashes for the four inspected studies. `package-inventory.json` records this manuscript package, the investigator's receipts, exact available archives and linked provenance metadata; source and backend build recipes remain in the root distribution. Runtime is Linux x86_64, Python 3.12.14 for recorded native producers; analytical plotting uses the existing project-local Matplotlib 3.10.6 environment. See `rerun.md` for repeat commands. No rights conclusion relies on a model display name alone.

Primary-source reading was bounded to [SGLang](https://arxiv.org/abs/2312.07104), [Qwen2.5](https://arxiv.org/abs/2412.15115) and the pinned project/model/backend evidence. An accidentally retrieved unrelated survey was excluded from the protocol's primary-source list and manuscript claims. There is no broad literature-novelty or comprehensive review claim.

