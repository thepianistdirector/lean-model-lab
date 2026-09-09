# Reinspect and reproduce

These commands run from the Lean Model Lab source workspace. Inspection and derivation require no loaded model or new allocation. Native repetition is a new separately authorized run: retain the original recipe/archive and never reset this campaign's elapsed clock to reuse a spent allocation. All output paths must be new.

```sh
python3 .cache/packaged-v1-platform-20260908-03/lean-model-lab.pyz inspect .cache/study-14b-main-20260908-01
python3 .cache/packaged-v1-platform-20260908-03/lean-model-lab.pyz report .cache/study-14b-main-20260908-01 --output NEW/result.json --html NEW/report.html
python3 .cache/packaged-v1-platform-20260908-03/lean-model-lab.pyz workbench --study .cache/study-14b-main-20260908-01 --output NEW/workbench.json --html NEW/workbench.html
python3 tools/audit_raw_study.py .cache/study-14b-main-20260908-01 --output NEW/raw-audit.json
.cache/research-plot-env/bin/python docs/research/quality-study/derive.py
```

Replace the source study argument with each row in `methodology.md` for the adverse and development sources. Preserve the auditor's status rather than inferring success from process exit. `derive.py` regenerates local derived tables and figures and refreshes `cost-context.json`; it does not mutate native evidence, rerun a model or overwrite producer reports. For an immutable reanalysis copy, first copy this research directory to the chosen review workspace and update its explicit output constant there. Static figures require Matplotlib 3.10.6 and its installed dependencies; they use project-local temporary and configuration directories.

The exact new development command was:

```sh
python3 tools/run_queued_recipe.py \
  --archive .cache/packaged-v1-platform-20260908-03/lean-model-lab.pyz \
  --recipe .cache/v1-investigations-20260908/quality/development-recipe.json \
  --server .cache/prepared-20260908-01/build/bin/llama-server \
  --model .cache/prepared-20260908-01/qwen2.5-0.5b-instruct-fp16.gguf \
  --setup .cache/adopted-0.5b-current-02/setup.json \
  --output .cache/v1-investigations-20260908/quality/development-study
```

This historical command is not an instruction to repeat the stopped screen. Its completed recipe SHA-256 is `1867f2c64e90e172b3e0085262eec69e32ddd1a43ddd532a7f7bae2954ef654f`; generated workload SHA-256 is `c3516b28d2745c9d88c1a46dabdb6210fe07784c683b04dbb33a0490091db77d`. Queue registration, product log and receipt are beside the study in `development-study.queue/`. The screen used 32 native requests once; seed830129 confirmation remains unstarted.

A meaningful skeptical reproduction should first verify all file/provenance hashes and replay the 14B raw audit, then select its own prospectively frozen bounded subset or fresh comparison through the exact admitted package, with distinct declared sampling and full cost retention. Repeating historical 14B execution requires its original producer and original recipe identity; running a new v3 recipe creates a separate experiment rather than upgrading the old one. This package does not authorize that work or prescribe a favorable seed. The root coordinates its finite resources and separate verified investigator.

For export, inspect the source first, retain a new output directory, and use the actual absolute model path recorded in its raw metadata:

```sh
python3 tools/export_study.py SOURCE-STUDY --output NEW-EXPORT --model-path ACTUAL-RECORDED-MODEL-PATH
```

The study export excludes weights and the backend executable. The root distribution must include the source, license/notices, supported runbook, pinned acquisition/build recipes, exact producing archives, frozen protocols, lawful generated workloads, all relevant study/provenance trees and this derived package. A local export alone is not public release, external execution or human validation.

