# CPU prefix-cache comparison — proposed 0.1 contract

Status: proposed before model acquisition or inference. Exact backend adoption and finite compute allocation require the owner's decision in `docs/decisions/backend-audit.md`. This document replaces the historical quality placeholder for the narrow 0.1 successor; it does not amend the original scientific task contracts.

## Question

Does enabling the admitted backend's existing prompt-prefix cache reduce client-observed latency or improve throughput on one fixed synthetic key-copy workload, while preserving exact output tokens and a real task-quality threshold? No model competence, online service, energy, frontier or cross-device superiority is implied.

## Fixed population and quality

Generate 128 requests, exactly 32 in each of four **filler-word strata** (16, 64, 128, 256). These are words, not token counts; retain the actual tokenizer counts after model admission. Seed: 20260907. Public synthetic filler uses eight neutral vocabulary words and contains no real/private records. Each prompt contains a five-letter ASCII key and asks for that key alone. Expected answers derive directly from the generator before inference, never from baseline output. Exact-key accuracy after outer whitespace stripping must be at least 95% for each arm, each repetition and each concurrency mode. Failure to meet this absolute quality contract is a failed comparison, even if both arms agree.

Greedy decoding (`temperature=0`), at most 32 generated tokens, model-native end-of-sequence allowed, no custom stop strings, no hidden truncation. Baseline and candidate have identical prompt bytes, tokenization, chat template, weights and decoding parameters. Exact per-request output-token sequence parity is an additional constraint, not the definition of task quality. A length-limit completion is retained as truncated and makes the comparison ineligible.

## Arrival, execution and cache semantics

Each arm receives the same stored trace. All 128 arrivals are scheduled at offset zero: this is a finite queued batch, not an online service workload. Concurrency 1 and 4 cap in-flight requests. A deterministic lane assignment gives each request a stable engine slot; each lane processes its ordered requests serially. Each arm starts a fresh backend process, with the same load/warmup protocol. The only candidate difference is `cache_prompt=true` versus baseline `cache_prompt=false`; automatic cross-slot cache reuse must be disabled or recorded as unsupported before admission.

Three complete paired repetitions per concurrency, order AB / BA / AB fixed before results. No pilot-driven threshold tuning, best-run selection, statistical significance claim from request-level pseudoreplication, or deleting busy-host runs. Pair-level ratios and their range expose the small replication count; request p95/p99 use nearest rank and state that 128-request tails are unstable. Within-stratum summaries accompany pooled summaries. A 5% throughput gain is the practical interpretation threshold; eligible smaller gains are reported as no demonstrated practical gain. Tail regressions greater than 10% invalidate a gain recommendation.

## Clocks, costs and failures

Monotonic nanoseconds are the coordinator clock. Retain scheduled arrival, admission, HTTP dispatch, each observed streamed event, first content/token observation and terminal response. Dispatch is **not** an engine execution-start timestamp; engine start and internal queue are UNAVAILABLE unless the admitted adapter actually exposes them. A streamed multi-token chunk has a chunk receipt time; never invent individual token gaps. Server-reported durations remain separately scoped.

Record startup, artifact verification/model load, warmup, service, evaluation, reporting and recovery full-wall costs, plus acquisition/build setup attempts and failed attempts. Host RSS is sampled or recorded via an explicitly named process measurement boundary; accelerator memory and unsupported energy/thermal probes are UNAVAILABLE. Zero paid compute is not zero CPU cost.

Every attempt has a unique ID and append-only events. Interruption retains completed and unfinished requests and all observed usage. Restart creates a new attempt; partial attempts cannot enter successful paired performance statistics and remain in campaign costs. Missing, duplicated, failed, dropped, timed-out, truncated, malformed or identity-mutated records cannot increase comparison eligibility.

## Execution packet

Root owns `src/lean_model_lab/`, `workloads/`, `tests/test_contracts.py`, `tests/test_evidence.py` and `tests/test_cli.py`. Standard-library preparation has no installation or model requirement. Implement deterministic trace generation, immutable identity digests, strict workload/event validation, independent quality scoring, retained failure accounting, report regeneration and representative mutations. Commands will be documented only after those entry points exist. Exit evidence for this packet is model-free automated behavior; actual inference stays NOT TESTED until the dependency/model gate is accepted and the real backend runs.
