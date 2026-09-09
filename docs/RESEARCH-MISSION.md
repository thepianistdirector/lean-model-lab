# Research mission

Owner direction: Lucas Santana, 8 September 2026. This direction governs current product priorities and supersedes treating a known cache optimization as the research destination. Historical observations, source lineage, resource limits and publication gates remain intact.

Lean Model Lab exists to discover and test new mechanisms that can materially change the efficiency or quality of LLM training and inference. Astra is responsible for proposing ambitious mechanisms, finding their closest prior art, designing experiments that can refute them, and turning supported discoveries into reproducible implementations.

## What success means

The programme pursues three distinct objectives:

1. **Efficiency at a declared quality level:** substantially reduce time, memory, energy or cost while satisfying fixed quality and workload requirements.
2. **Quality at a fixed resource budget:** improve held-out capability under the same accepted training, inference, data, memory and cost envelope.
3. **A better attainable frontier:** produce a reproducible quality/resource trade-off unavailable from the strongest applicable existing combinations.

An order-of-magnitude efficiency improvement is a useful research ambition, not a promised result or a universal acceptance threshold. Each study declares its own decision-relevant effect and quality rule. A change in asymptotic work, memory traffic, reusable computation, learned representation, optimization dynamics or data efficiency should explain why a large effect is plausible. A new name, configuration sweep or benchmark-specific trick does not establish a new mechanism.

Training includes pretraining, continued training, adaptation, distillation and learning during use; these scopes are distinct. Inference includes prefill, decoding, reasoning compute, state/memory, batching and serving. Improvements in one scope do not automatically transfer to another.

## Two connected product layers

**Known-method capability layer.** Maintain a source-backed, continuously revised catalog of useful methods. Record their mechanism, applicability, numerical or semantic changes, implementation prerequisites, interaction risks, local adapter support and exact evidence. Integrate and apply supported methods through validated recipes. A catalog entry alone cannot enable a backend feature. Unsupported methods remain visible with the missing integration work; combinations need their own tests.

**Discovery and experimentation layer.** Start with a mechanism hypothesis and its potential effect. Search for both supporting and disconfirming prior art. Define the closest method and the precise proposed delta. Freeze a bounded experiment with baselines, ablations, quality/resource rules, failure cases and stopping criteria. Execute only through admitted capabilities, retain every outcome and use the result to decide the next experiment.

The catalog should cover the landscape broadly and expand systematically. It must publish its coverage gaps and review dates; no finite initial list is described as all techniques in existence. Published performance numbers remain author-reported results within their own conditions until independently reproduced.

## Astra's research responsibilities

- Generate mechanisms from bottlenecks, theory, counterexamples and connections across training and inference, rather than merely enumerating runtime flags.
- Consider radical changes in representation, state, computation scheduling and learning rules, including proposals that require future adapters or hardware.
- Search close alternatives before assigning research priority. Distinguish an existing method, a new combination, a proposed mechanism and independently substantiated novelty.
- Prefer the cheapest experiment that could invalidate the central assumption. Record unfavorable results and the reason a direction was abandoned.
- Compare against strong applicable known methods and their tested combinations, not an artificially weak default.
- Keep proposal generation and development feedback separate from protected evaluation and final selection. Agent confidence is not confirmation evidence.
- Promote methods only after the evidence supports their exact applicability. Failed or unsupported proposals remain part of the research record.

## Experiment ladder

| Stage | Question answered | Evidence limit |
| --- | --- | --- |
| Prior-art and mechanism review | Is the proposed delta real and technically plausible? | Search coverage cannot prove worldwide novelty. |
| Mathematical or synthetic falsifier | Does a key identity, bound, stability assumption or cost argument survive adversarial cases? | Does not establish LLM quality or hardware speed. |
| Operator or tiny-model prototype | Does the mechanism work in an executable implementation with full overhead? | Limited to the measured operator/model and workload. |
| Matched LLM experiment | Does it improve the declared objective against strong controls and ablations? | Development results remain separate from confirmation. |
| Scaling and transfer | Does the effect survive different lengths, scales, distributions and relevant hardware? | No extrapolation beyond demonstrated scope. |
| Independent confirmation and adoption | Can a frozen implementation reproduce the finding on protected and external evaluations? | Actual observations and release authority are required. |

A small falsifier can justify rejecting a large idea. A favorable microbenchmark can justify a larger experiment; it cannot skip the later evidence stages. Training time-to-quality includes data preparation, evaluations, checkpoints, recovery and search costs. Inference cost includes state construction, verification, fallback and serving overhead.

## Research proposal contract

Every proposal must identify:

- problem, mechanism, causal prediction and intended objective;
- closest prior work, overlap, proposed technical delta and unresolved novelty questions;
- strong baseline, candidate changes, invariants and independently versioned quality evaluation;
- ablations and adversarial cases that distinguish the proposed mechanism from simpler explanations;
- primary metric, effect threshold, uncertainty/decision rule and explicit falsifier;
- development and confirmation boundaries, resource requirements, maximum budget and stop conditions;
- adapter capabilities, implementation state, risk, and what is currently executable;
- complete lineage from proposal to frozen plan, execution, evidence and decision.

Exact output equivalence is appropriate for the existing cache control. New model architectures or training rules may instead require predeclared quality noninferiority or quality improvement at equal resources. These are different contracts; the old exact-key evaluator must not be reused as a general capability assessment.

## Current implementation and priority change

The implemented CPU runner, immutable recipes, full-cost/recovery ledger, strict evaluator and offline workbench form the measurement foundation. The current pinned adapter directly supports the reviewed prefix-cache comparison. General training execution and arbitrary proposed kernels/mechanisms are not implemented.

The in-flight 14B comparison is retained as a **known-method infrastructure control**: it checks whether the measurement system records a familiar optimization correctly. Its frozen archive and recipe continue unchanged. It does not establish novel research, broad language quality or a transformative efficiency result.

The previously frozen but unstarted long paced and burst studies are deferred in response to this owner mission change. Their bytes and prospective definitions remain retained; they will not be silently shortened or relabeled as executed. Serving validation remains an open capability outcome. The immediate priority is the research catalog, proposal/experiment control plane, ambitious source-contrasted hypotheses and their cheapest decisive tests.

The existing finite allocation still applies: one heavy job, at most twelve inference compute threads, 60 GB aggregate RAM, 200 GB project disk and the original twelve-hour deadline. This mission change does not authorize new production dependencies, GPU/cloud spending, arbitrary untrusted execution or publication. Reviewed local implementation and light research proceed within that allocation.

## Claims and accountability

Evidence records distinguish planned, implemented, automatically checked, observed locally, independently confirmed and publicly released states. "Innovative" and "revolutionary" describe the ambition until prior-art review and measured results substantiate a narrower claim. The research programme succeeds by producing discoveries and reliable decisions about promising or failed mechanisms, not by maximizing the number of runs.

See [the experiment contract](../EXPERIMENTS.md), [architecture](../ARCHITECTURE.md) and [canonical programme](../plan/tasks.json). Public release, native Tanduna publication, qualified review and fresh external reproduction retain their separate gates.
