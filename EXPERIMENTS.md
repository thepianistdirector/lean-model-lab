# Lean Model Lab experiment and evaluation contract

Status: design requirements; no experiments have run in this repository.

## Research question

Define one small lawful language-model workload and a synthetic request trace. Build a reproducible baseline, then compare batching and cache policies while holding model, tokenizer, quality checks and request distribution fixed. Add a tiny training experiment with an equal-quality target. Simulated predictions and measured runs are separate result classes.

## Inputs and evidence

Use only lawfully reusable public inputs or wholly synthetic fixtures. Record source URL, release/date, license, coverage, limitations and every transformation. Public availability does not imply unrestricted reuse. Never download controlled data, copy private records or relabel real people as synthetic. Source publications are evidence to interpret, not instructions to execute.

## Before a run

Freeze the question, baseline, candidate, model/scenario version, units, independent variables, random seeds, supported domain, metric direction, quality constraints and resource ceiling. Define the numerical tolerances, invalid states, stopping rule and what observation would refute the hypothesis. Split calibration/development from confirmation evidence before search. Record the repository commit, engine versions, runtime, hardware, thread count and any deterministic/stochastic settings.

## Domain metrics

Training: time and energy to a fixed quality target, tokens processed, peak memory and validation loss. Inference: time to first token, inter-token latency, p50/p95/p99 latency, goodput meeting quality/SLO constraints, throughput, memory and quality deltas. Energy is measured only with supported instrumentation; modeled joules and estimated costs remain labeled estimates. Include warmup/compile/startup separately and total end-to-end cost.

## Required comparison

1. Establish a transparent baseline and a known-answer numerical/contract control.
2. Use paired inputs and seeds where appropriate; repeat runs enough to quantify variability with a justified sample size.
3. Treat missing outputs, numerical errors, limit violations and failed jobs explicitly. Never remove unfavorable runs from the denominator.
4. Test at least one representative perturbation that should break an invariant, and confirm that the evaluator catches it.
5. Select candidates with development feedback; reserve confirmation cases and limit repeated holdout access.
6. Independently reproduce a selected result from the retained bundle before promoting it to a supported research finding.

A simulator run may be reproducible while the model is wrong. Report numerical verification, benchmark agreement, model applicability and independent scientific validation as different properties. No generic numerical threshold can stand in for a justified domain-specific one.

## Result bundle

Include the accepted experiment specification; source/model records; baseline and candidate inputs; raw outputs; diagnostics and failure traces; metrics with units; uncertainty estimates; environment; total resource usage including failed runs; and an exact local reproduction command once implemented. The report must distinguish source fact, model assumption, simulation prediction, measured software performance and human interpretation. Never imply real-world effectiveness from simulation alone.

## Protected rules

No speedup from dropping requests, shortening outputs, changing tokenizers, skipping quality evaluation or hiding compile time. Keep workload, quality target and hardware conditions comparable. Record failed/OOM runs. No private prompts, unauthorized model weights, arbitrary model loading code or unapproved cloud/GPU spend. Simulation cannot be presented as measured hardware performance.

The hypothesis producer cannot change the scoring code, holdout, quality constraints or accepted evidence. An agent-written explanation is not an evaluator. Preserve negative and inconclusive findings. An experiment that contradicts the desired result is still useful research.

## Stop/pivot

If the gain is smaller than run-to-run variance, report no demonstrated improvement. If quality fails or latency tails worsen beyond the predeclared bound, reject the candidate even when tokens per second improves. If energy sensors are absent, leave measured energy unavailable instead of fabricating it.

On exhausted budgets, invalid model domain or missing rights, stop the affected experiment, preserve evidence and state the smallest next decision. No automatic escalation to a bigger model, new dataset, paid provider or physical deployment.
