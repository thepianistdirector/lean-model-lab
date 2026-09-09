# Candidate investigation blocker: versioned mixed task population

Observed 8 September 2026 using the real packaged v1 archive03, SHA-256 `f90c48dd0be36b29c3188c365ba6b8ab2cbe709897cd7f4cce0e4825a147db6f`. No model is needed to reproduce this admission blocker, and no training labels were collected by the failed command.

The candidate investigation needs one prospectively mixed population of direct lookup, transitive references and last-write updates. It should train one model-bound acceptance controller with varied structural features while retaining component-family subgroup counts. Separate independent scratch runs cannot substitute for the product's frozen workload, training protocol and raw-audit path.

From the project workspace, after producing the retained proposal and protocol, run:

```sh
python3 -I .cache/packaged-v1-platform-20260908-03/lean-model-lab.pyz research study-create \
  --proposal .cache/v1-investigations-20260908/candidate/feasibility-proposal03.json \
  --protocol .cache/v1-investigations-20260908/candidate/feasibility-protocol03.json \
  --allocation .cache/allocation-0.4-20260908.json \
  --model-profile qwen2.5-14b-instruct-fp16-v1 \
  --family record-mixed-v1 --context-records 24 \
  --split development --purpose DEVELOPMENT --requests 32 --seed 920260832 \
  --concurrency 1 --pairs 2 --threads 6 \
  --output .cache/v1-investigations-20260908/candidate/mixed-blocker-recipe03.json
```

Expected: a new versioned deterministic mixed family with original generator meanings unchanged; explicit per-request component identity recoverable from the prompt and component-aware report/training coverage.

Actual: exit code 2 at CLI argument admission. Accepted families are `record-lookup`, `reference-chain`, `record-updates` and `record-reuse`. No recipe was created. Full exact argv, timestamps, exit code and output hashes are retained in `.cache/v1-investigations-20260908/candidate/commands/mixed-family-blocker03.json`; the adjacent stdout/stderr files retain actual product output. `commands/mechanisms03.stdout` independently lists the supported families.

Missing capability: a versioned mixed generator plus CLI admission, deterministic recipe validation, component-aware analysis and compatible training/table-group checks. This is a product capability request, not evidence that the proposed controller works.

Minimum acceptance check: the revised packaged CLI creates and validates mixed 32-request development and 128-request confirmation populations; regeneration is exact; components cycle in a documented order (for lookup/reference/updates that would give 11/11/10 and 43/43/42 respectively); all requests preserve the existing request schema; fit/calibration table groups are disjoint and checked; prompt transformations receive no expected answer; actual native raw auditing, training and reporting recognize the new family. Retain a new immutable archive and identities before label collection. Do not alter old family semantics or fill the gap with a scratch experiment.

Independent progress: the already admitted archive03 14B reference-chain/context8 feasibility cell was frozen before execution and submitted through `tools/run_queued_recipe.py`. The mixed-family blocker does not prevent that bounded existing-capability check.
