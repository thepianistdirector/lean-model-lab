# Methodology and evidence map

This is one benchmark/negative-contrast package, not several findings made by splitting a study. The primary measured evidence is the historical 14B within-pair cache experiment. Historical 0.5B and a new development cell expose different quality/validity failure modes. The sources were known before this investigator's prospective protocol, so that protocol does not retroactively preregister the historical studies.

## Inputs and implementation

Run from the Lean Model Lab workspace root. `derive.py` reads only retained native evidence and packaged reports, writes this package's tables/figures, and launches no model. It uses the source-independent normalized request fields to recompute exact task correctness and token-difference lists. Correctness requires `SUCCEEDED`, a finish reason other than `length`, and the expected answer after outer-whitespace stripping. The canonical packaged evaluator additionally enforces its full token budget/protocol/inventory rules; recomputing correctness alone cannot establish eligibility. All observed counts and mismatch lists must equal the packaged report, otherwise derivation aborts.

| Study label | Native evidence | Investigator CLI/audit outputs |
| --- | --- | --- |
| `14b` | `.cache/study-14b-main-20260908-01` | `.cache/v1-investigations-20260908/quality/14b` |
| `legacy-comparison` | `.cache/public-evidence-0.4-20260908/legacy-comparison/study` | `.cache/v1-investigations-20260908/quality/legacy-comparison` |
| `legacy-protocol-failure` | `.cache/public-evidence-0.4-20260908/legacy-protocol-failure/study` | `.cache/v1-investigations-20260908/quality/legacy-protocol-failure` |
| `development` | `.cache/v1-investigations-20260908/quality/development-study` | `.cache/v1-investigations-20260908/quality/development` |

Each output directory contains stdout, stderr and a command/time/exit receipt for `inspect`, `report`, `workbench` and the raw auditor. Per-study workbenches avoid a large combined HTML file. Raw auditor exit zero means it emitted a valid audit, not that an interrupted study passed. Read `status`: the historical protocol failure is `INCOMPLETE_OR_FAILED`.

## Frozen design and stopping

The cache proposal, authored protocol, immutable freeze receipt and development recipe are in `.cache/v1-investigations-20260908/quality/`. The freeze preceded native execution. Selected model profile: `qwen2.5-0.5b-instruct-fp16-v2`; family `record-lookup`; context 8; development seed 830091; two AB/BA pairs; eight requests/arm; concurrency 1; two compute threads. The held-out seed was predeclared as 830129 with 128 requests/arm, but no confirmation recipe was created or executed after feasibility failed. Maximum prospective use was 32+512=544 native requests and 1,200 native seconds, within the original common allocation.

The feasibility selection rule required all four arms to attain 8/8 and exact paired output-token parity before confirmation. This screen is not a substitute for the unchanged 95% measurement gate and cannot certify future performance. Observed 6/8 in each arm caused the promised stop. Root accepted the bounded historical-audit alternative; no further native requests or model/family/seed search occurred.

## Units, denominators and uncertainty

`requests.csv` has one row per observed terminal request: 2,048 14B + 1,536 historical 0.5B comparison + 30 historical failed observations + 32 new development = 3,646. There are 3,744 offered requests across these four inventories, including 98 missing in the interrupted study. Missing requests have no invented timing rows; they remain in report and attempt quality denominators. `attempts.csv` has 33 attempts. `pairs.csv` has eight 14B, six historical 0.5B and two new development pairs; null efficiency fields are intentional for ineligible studies. Pair indexes are zero-based. The manuscript uses C1/C4 as concurrency shorthand, not distinct machines.

Service throughput is successful request count divided by retained service envelope. It is not accuracy-qualified goodput. Full-attempt efficiency compares successful requests per full attempt and, for the fully successful equal-work 14B pairs, reduces to baseline/candidate full-wall time. No ineligible pair ratio is reconstructed for promotion. Setup is shared study history, not assigned independently to both arms. No amortization count, electricity price or FLOP estimate is invented.

End-to-end latency is client completion minus offered arrival; TTFT is first nonempty token receipt minus offered arrival. These include queueing. Dispatch-to-completion is reported separately. A client chunk gap is not an engine token-emission gap. Tails use nearest rank. Pair minima/medians/maxima are descriptive rather than confidence intervals. ECDFs pool four correlated batches per arm/concurrency and are labeled accordingly. Per-stratum native metrics remain in packaged reports; there is no cherry-picked stratum selection.

## Complete costs and unfavorable attempts

`cost-ledger.csv` preserves every setup phase and attempt supplied by the four report ledgers, including repeated inherited views. `deduplicated-cost-ledger.json` groups identical start/end intervals so predecessor attempts are not charged twice. Unioning overlapping supplied intervals is descriptive inventory reconciliation; it does not fill unrecorded work. The frozen report's registered full wall is the correct total all-clock view at its cutoff, with unattributed intervals explicit. It contains the phase and attempt costs rather than supplementing them.

Additional prior workflow evidence is linked, not relabeled as this investigator's experiment: [historical 0.5B failures/recovery](../../results/cpu-20260908.md), [14B development/recovery](../../results/14b-development-20260908.md), [v1 first workflow receipt](../../evidence/v1-first-workflow-02.json), and [0.5B profile correction](../../decisions/0.5b-profile-size-correction.md). The initial v1 adoption/workflow failed before inference because a declared size included 78 bytes of non-model acquisition directory growth. Its artifacts remain `.cache/adopted-0.5b-current-01` and `.cache/v1-first-workflow-20260908-01`; corrected adoption is `-02`. These failures are not new native requests in this study. The inherited current ledger also retains the intentional v1 recovery interruption and successful replacement.

The historical 0.5B first native protocol attempt was interrupted after 30 failed normalization observations, with no candidate arm. Two failed builds remain. The 14B historical and v1 first-workflow recovery interruptions were intentional controls; the replacement attempts did not erase them. Every unsuccessful observation remains in its original classification. There was no failed new native attempt or retry here; the new development is operationally completed and scientifically ineligible. Two harmless exploratory file/schema reads and a JavaScript orchestration syntax error were corrected during analysis; they did not execute inference or alter native evidence, and their wall remains in the common allocation clock.

## Output contract and validation

`summary.json` retains complete configurations, audit identities, eligibility and accounting. `tables.json` mirrors the core table data. `source-inventory.json` hashes every file in each of the four supplied study trees, including raw SSE, normalized attempts, immutable events and setup. Original/derivative provenance trees are separate sources, specified in `rights-and-build.md` and the package inventory.

The three static PNG/SVG figures are rendered from these tables with Matplotlib, in project-local temporary/config directories. Their definitions are in `chart-contracts.json`; the exported PNGs were visually inspected. Labels, units, all groups and tails remained visible after moving the quality-chart legend below the plot. No model-free simulation was used as an experiment. Separate skeptical reproduction and external human review are pending.

