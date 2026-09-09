# Proposal to a bounded model experiment

This workflow is being verified for the local v1 candidate. A development archive and successful software tests are not a public release or a research finding. Consult [the acceptance contract](V1-CONTRACT.md) and [current state](../STATUS.md).

Run native commands from the supplied source workspace containing `WORKSPACE.json`, using the tested Python 3.12.14 / Linux x86_64 environment. Other Python versions remain unvalidated by this campaign. The pinned reviewed backend and official model are separate lawful dependencies. [The recipe runbook](RUNBOOK-0.4.md) explains model acquisition, resource admission, workspace scope and recovery. Existing operator authorization persists; the CLI records it and cannot grant resources. A researcher's own deployment needs its own finite authorized envelope. Never reset an existing allocation clock to extend a study.

## Discover actual support

```sh
python3 -I lean-model-lab.pyz research catalog
python3 -I lean-model-lab.pyz research templates
python3 -I lean-model-lab.pyz research mechanisms
```

The technique catalog covers inference and training literature. Only explicitly registered local mechanisms execute. LLM training hypotheses remain unimplemented. The bounded v3 lane implements full-context and same-slot cache controls, lexical/dependency/matched-record selection, cache/slice combinations, a predeclared simple gate, and a fitted small acceptance controller. The last mechanism trains a depth-two decision tree on actual development responses; it does not train or fine-tune the underlying LLM. None is claimed to be a new model architecture. The transformation reads only the prompt; all native outputs are evaluated separately.

Supported original synthetic tasks are direct record lookup, transitive reference resolution, final-write record updates, and eight consecutive queries per shared lookup table (`record-reuse`). Contexts contain 8, 24 or 64 records. Every first-use query and table transition stays in the offered population. They are authored by this project under AGPL-3.0-only and contain no external/private dataset. A symbolic interpreter can solve this restricted grammar; it must be reported as a non-LLM floor. These tasks do not establish general language competence.

`record-mixed-v1` provides a declared mixture of lookup, reference-chain and final-write tables for the acceptance-controller study. The separately named `*-explicit-v2` families and `explicit-grammar-v2` mechanism apply one fixed header clarification while retaining original records, values, query and order. This is an instruction intervention with a distinct identity; it is not a compatible replacement for a frozen original population. Its development failure remains reported, and the negative controller study uses the original grammar.

## Prepare and freeze

Use new output paths; existing artifacts are never overwritten. First write a registered starting proposal and protocol:

```sh
python3 -I lean-model-lab.pyz research propose \
  --mechanism dependency-slice-v1 --output proposal.json
python3 -I lean-model-lab.pyz research protocol \
  --proposal proposal.json --output protocol.json
python3 -I lean-model-lab.pyz research freeze proposal.json --output proposal-bundle
python3 -I lean-model-lab.pyz research verify proposal-bundle
```

Review and author a new protocol file before measurement. Record the exact causal question, primary sources, controls/ablations, development evidence, selection and stopping rules, uncertainty and claim limits. The default protocol is a starting design, not evidence that those obligations have been fulfilled. A proposed resource ceiling may narrow an allocation; it never expands one. `research study-create` binds the complete proposal and protocol into the versioned recipe, alongside the exact model, workload, evaluation and original allocation.

Begin with a separately labeled development split:

```sh
python3 -I lean-model-lab.pyz research study-create \
  --proposal proposal.json --protocol protocol.json \
  --allocation allocation.json --model-profile qwen2.5-0.5b-instruct-fp16-v2 \
  --family reference-chain --context-records 24 \
  --split development --purpose DEVELOPMENT --requests 8 --seed 109 \
  --concurrency 1 --pairs 2 --threads 2 --output development-recipe.json
python3 -I lean-model-lab.pyz recipe validate development-recipe.json
```

After development, freeze a distinct confirmation recipe with `--split confirmation --purpose MEASUREMENT --requests 128` or more, a declared seed and the complete intended paired schedule. Do not edit a measured recipe or tune on its results. The development and confirmation generators use different streams and key/value namespaces; this is a declared distribution difference, not cryptographic secrecy. Shared Unix identity means candidate/evaluator separation is a workflow convention and mutation detection, not isolation against a malicious local writer. This proposal runner refuses claims of technically protected confirmation or LLM training. The separately traced controller-training commands below fit only the small acceptance tree.

For other workload/arrival experiments, declare family, context size, seed, concurrency, paced/burst intervals, queue capacity, admission deadline and SLOs before running. The ordinary recipe runbook defines all arrival denominators. An ablation is a separately frozen registered mechanism with the same population/model/settings and explicit cost budget. The matched-budget ablation matches record counts, not tokenizer counts; report the actual token difference.

## Execute the frozen product

Keep the exact archive used for every run; source changes cannot silently resume an old study. Supply the prepared model/backend/setup paths:

```sh
python3 -I lean-model-lab.pyz run --recipe development-recipe.json \
  --server prepared/build/bin/llama-server \
  --model prepared/qwen2.5-0.5b-instruct-fp16.gguf \
  --setup prepared/setup.json --output development-study
python3 -I lean-model-lab.pyz inspect development-study
python3 -I lean-model-lab.pyz report development-study \
  --output development-result.json --html development-report.html
python3 -I lean-model-lab.pyz workbench --study development-study \
  --output development-workbench.json --html development-workbench.html
```

The project heavy-job lease queues work by refusing simultaneous heavy commands. Preserve the refusal, wait for the active job to finish, then admit the next exact study; do not reset clocks or run a second backend outside the product. Every reserved attempt checks model shards and backend identity and retains native tokenization, SSE, offered arrivals, request checkpoints, context transformation and costs. Interventions execute before offered arrivals: service-only timings exclude preparation, while full-attempt wall includes it. The primary v3 cost criterion uses full-attempt wall, with shared setup/search costs retained in the complete allocation ledger.

Both arms need at least 95% exact task answers with no observed pairwise quality loss. Same-input controls additionally require exact output token parity. Changed-input interventions retain token differences without treating them as an equivalence guarantee. No favorable ratio is exposed for an ineligible campaign. Negative findings still retain all measurements for inspection. A valid dependency certificate only establishes facts about the parsed record language, never model-output correctness.

## Fit and deploy an empirical acceptance controller

Before collecting labels, compile disjoint `dependency-slice-v1` development recipes for fit and calibration, at concurrency one with at least two balanced pairs. Use different seeds/table populations. Each source must be executed exactly once through the same model/template/producer build; failed or missing cells cannot be replaced with favorable labels. Freeze their identities before native execution:

```sh
python3 -I lean-model-lab.pyz research training-protocol \
  --fit-recipe fit-recipe.json --calibration-recipe calibration-recipe.json \
  --output training-protocol.json
```

Repeat either recipe argument to freeze a larger finite population. Then execute every source recipe through `run`, preserving the producer studies. The training command independently replays their retained native protocol before deriving labels:

```sh
python3 -I lean-model-lab.pyz research train-controller \
  --fit-study fit-study --calibration-study calibration-study \
  --protocol training-protocol.json --output fitted-controller
```

The output includes exact fit/calibration label collections, all four paired correctness classes, a deterministic split trace, every calibration threshold, a model/template-bound `controller.json`, and a training cost/failure receipt. All repetitions must be correct for an arm's per-prompt label to be correct. Repeated queries sharing one table stay in the same fit or calibration partition. Calibration uses native dispatch-to-completion cost as a selection proxy; deployment still needs the independent full-attempt and complete allocation cost gates. Zero observed calibration harm is an empirical selection rule, not a population-risk or conformal guarantee. If no threshold is feasible, the fitted artifact explicitly selects `ALWAYS_FULL`.

The learner uses deterministic Gini splits with stable ordering and tie-breaking; it has no stochastic optimizer or training RNG. Workload and model sampling seeds belong to the frozen source studies. Controller fitting has no checkpoint-resume interface. Ordinary handled exceptions retain partial files and a failed receipt; interruption or process death can leave only files already flushed. Preserve that directory and use a new output for a justified restart from the same frozen label sources, retaining its additional costs. Do not repeat native label collection merely to replace a failed fitting command.

Write a `learned-gated-slice-v1` proposal and a prospective confirmation protocol, then supply `--controller fitted-controller/controller.json` to `research study-create`. The complete controller is frozen into the recipe. Native evidence retains each prompt-only routing decision and its measured preparation cost. Model/template mismatches, altered parameters and changed decision receipts are refused. Retain and export the training directory and all label-source studies alongside deployment evidence; one deployment report alone cannot establish amortized training savings.

For multiple researchers on one workspace, `tools/run_queued_recipe.py` accepts `--archive`, `--recipe`, `--server`, `--model`, `--setup` and `--output`, waits for the project queue/heavy leases, and calls the exact product archive once. Its original allocation deadline includes waiting. Separate queue registrations, product logs and completion/failure receipts remain beside each study; no automatic rerun or clock extension occurs.

## Inspect, recover and export

Inspect request disclosures for original and transformed prompts, exact answers and native output tokens, certificate scope, preparation duration, cache reuse, timing and source references. The workbench compares input token IDs within each registered arm and replays raw SSE; the independent raw auditor additionally checks cache accounting. Local hashes establish consistency, not external authenticity.

Use `inspect`, `recover-journal`, `reconcile` and `resume` with the original recipe/archive as documented in [the recovery runbook](RUNBOOK-0.4.md). A resumed cell receives a new attempt ID; earlier failure and costs stay visible. Cross-boot resume is unsupported under an old monotonic allocation. A later supported fresh rerun is a new study under its operator's own resource decision, never replacement evidence.

```sh
python3 tools/audit_raw_study.py development-study --output raw-audit.json
python3 tools/export_study.py development-study --output exported-study \
  --model-path prepared/qwen2.5-0.5b-instruct-fp16.gguf
```

Exports preserve study settings, answers, outputs, token/timing values and adverse history, with explicit provenance for permitted operational-path redaction. No model weights or backend binaries are included. Keep original producer studies and the exact producing archive. Publication requires a separate approval for concrete artifacts and destinations.

## Prepare a portable research distribution

`tools/build_v1_release_bundle.py` accepts the final `--archive`, every retained `--producer`, and repeated `--study NAME=EXPORT_DIRECTORY` arguments. It verifies original/export provenance, complete reports, raw inventories and producer identities before issuing a candidate manifest. The source runtime must match the final CLI exactly. Provide `--asset-manifest` with a JSON mapping from source-relative PNG/PDF figure paths to their reviewed SHA-256 values; changed or unlisted figures are refused. CSV and static SVG figures receive text and format checks.

The output contains source/research manuscripts, exact executable producers, one evidence ZIP and generated HTML/JSON workbench per study, and a small `index.html`. Open the index directly in a browser without a server. Extract an evidence ZIP and use its `evidence/NAME/study` directory for inspection. Each ZIP has its own complete file manifest. A failed build may leave a partial local directory; only a completed `CANDIDATE-MANIFEST.json` describes a review candidate. Binary format checks and local hashes do not establish independent privacy review, scientific validity or public release.

For a complete investigation, add `--research NAME=SPECIFICATION.json`. That JSON declares `title`, `classification`, `source_directory` under `docs/research`, and the exact list of included study names. An optional `entrypoint` identifies the primary Markdown/HTML manuscript within that source directory. Optional `supplementary_files` maps package-relative names to source-workspace-relative text files, for example an `evidence-manifest.json` and `audits/study.json` required by the analysis. These files receive the same text checks and cannot replace reserved package artifacts. The resulting `NAME-research.zip` contains the complete source tree, selected evidence directories, exact required producers, portable workbenches and a `RESEARCH-PACKAGE.json`. Its source is in `lean-model-lab-source/` and its exported studies are in `evidence/NAME/study`; no original developer cache is required. A package classification records the reviewed kind of study and does not automatically establish scientific acceptance.

The source collector refuses unsupported files under `docs/research` rather than silently omitting them. Publish supported UTF-8 text or explicitly reviewed analytical figures, retaining any encoding or filename adaptation map. Reviewed product screenshots use PNG files under `docs/release/screenshots/`; include their exact hashes in the asset manifest too.
