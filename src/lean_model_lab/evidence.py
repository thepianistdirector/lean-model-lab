"""Strict reconciliation for the frozen CPU study; no inference or inferred telemetry.

Times are coordinator monotonic nanoseconds. Request latency includes client queue;
stream observations describe chunk receipts, never inferred per-token engine times.
This validates internal consistency, not authenticity of externally supplied evidence.
"""
from __future__ import annotations

import math
import re
import statistics
from collections import Counter
from typing import Any

from .contracts import ContractError, digest, validate_workload
from .config import validate_config

QUALITY_MINIMUM = 0.95
PRACTICAL_GAIN = 0.05
TAIL_REGRESSION = 0.10
OVERHEAD_KEYS = frozenset({"startup", "verification", "load", "compilation", "warmup",
                           "cache_preparation", "service", "evaluation", "reporting", "recovery"})
ENVIRONMENT_KEYS = frozenset({"observer", "version", "platform", "cpu", "load", "thermal", "memory", "energy"})
ATTEMPT_KEYS = frozenset({"schema_version", "evidence_class", "attempt_id", "config_sha256",
                        "workload_sha256", "arm", "concurrency", "pair_index", "started_ns",
                        "service_started_ns", "finished_ns", "status", "requests",
                        "overhead_ns", "environment"})
REQUEST_KEYS = frozenset({"request_id", "arrival_ns", "admitted_ns", "dispatch_ns",
                        "first_token_ns", "completed_ns", "token_events", "output_token_ids",
                        "output_text", "finish_reason", "status", "prompt_tokens", "generated_tokens", "engine_start_ns"})
_MAX_INT = 2**63 - 1


class EvidenceError(ValueError):
    """Evidence is malformed or inconsistent with its frozen inputs."""


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceError(message)


def _keys(value: Any, expected: frozenset | set, label: str) -> None:
    _check(type(value) is dict, f"{label} must be an object")
    _check(set(value) == expected, f"{label} has missing or unknown fields")


def _integer(value: Any, label: str, minimum: int = 0, maximum: int = _MAX_INT) -> None:
    _check(type(value) is int and minimum <= value <= maximum,
           f"{label} must be an integer in [{minimum}, {maximum}]")


def _text(value: Any, label: str, *, empty: bool = False) -> None:
    _check(type(value) is str and (empty or bool(value.strip())), f"{label} must be a string")


def _choice(value: Any, choices: tuple, label: str) -> None:
    _check(type(value) is type(choices[0]) and value in choices, f"invalid {label}")


def _tokens(value: Any, label: str) -> None:
    _check(type(value) is list and len(value) <= 4096, f"invalid {label} length/type")
    for token in value:
        _integer(token, label, maximum=2**31 - 1)


def _validate_environment(environment: Any) -> None:
    _keys(environment, ENVIRONMENT_KEYS, "environment")
    for key in ("observer", "version", "platform", "cpu"):
        _text(environment[key], f"environment.{key}")
    for key in ("load", "thermal", "memory", "energy"):
        probe = environment[key]
        _keys(probe, {"status", "scope", "value", "unit"}, f"environment.{key}")
        _choice(probe["status"], ("MEASURED", "UNAVAILABLE"), f"{key}.status")
        _text(probe["scope"], f"{key}.scope")
        _text(probe["unit"], f"{key}.unit")
        if probe["status"] == "UNAVAILABLE":
            _check(probe["value"] is None, f"unavailable {key} must have null value")
        else:
            values = probe["value"] if type(probe["value"]) is list else [probe["value"]]
            _check(bool(values), f"empty measured {key}")
            for value in values:
                finite_number = ((type(value) is int and 0 <= value <= _MAX_INT) or
                                 (type(value) is float and math.isfinite(value) and value >= 0))
                _check(finite_number,
                       f"{key} must contain finite nonnegative measurements")


def validate_attempt(attempt: Any, workload: Any, *, config_sha256: str,
                     workload_sha256: str, config: Any=None) -> None:
    """Reject malformed observations before metrics; expected digests come from sidecars."""
    if type(workload) is dict and workload.get('schema_version') == 3:
        from .evidence_v3 import validate_attempt_v3
        return validate_attempt_v3(attempt,workload,config=config,config_sha256=config_sha256,workload_sha256=workload_sha256)
    if type(workload) is dict and workload.get('schema_version')==2:
        if config is None:raise EvidenceError('v2 attempt validation requires its frozen configuration')
        from .evidence_v2 import validate_attempt_v2
        return validate_attempt_v2(attempt,workload,config=config,config_sha256=config_sha256,workload_sha256=workload_sha256)
    try:
        validate_workload(workload)
        actual_workload_digest = digest(workload)
    except ContractError as exc:
        raise EvidenceError(str(exc)) from exc
    for name, value in (("config_sha256", config_sha256), ("workload_sha256", workload_sha256)):
        _check(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
               f"invalid expected {name}")
    _check(actual_workload_digest == workload_sha256, "workload digest does not match frozen input")
    _keys(attempt, ATTEMPT_KEYS, "attempt")
    _integer(attempt["schema_version"], "schema_version", 1, 1)
    _choice(attempt["evidence_class"], ("MEASURED", "TEST_FIXTURE"), "evidence_class")
    _text(attempt["attempt_id"], "attempt_id")
    _check(attempt["config_sha256"] == config_sha256, "configuration identity mismatch")
    _check(attempt["workload_sha256"] == workload_sha256, "workload identity mismatch")
    _choice(attempt["arm"], ("baseline", "candidate"), "arm")
    _choice(attempt["concurrency"], (1, 4), "concurrency")
    _integer(attempt["pair_index"], "pair_index", 0, 2)
    _choice(attempt["status"], ("COMPLETED", "INTERRUPTED", "FAILED"), "attempt.status")
    for field in ("started_ns", "service_started_ns", "finished_ns"):
        _integer(attempt[field], field)
    _check(attempt["started_ns"] <= attempt["service_started_ns"] <= attempt["finished_ns"],
           "invalid attempt clock order")
    _check(attempt["finished_ns"] > attempt["started_ns"], "attempt duration must be positive")
    _keys(attempt["overhead_ns"], OVERHEAD_KEYS, "overhead_ns")
    for field, value in attempt["overhead_ns"].items():
        _integer(value, f"overhead_ns.{field}")
    _check(sum(attempt["overhead_ns"].values()) <= attempt["finished_ns"] - attempt["started_ns"],
           "overhead phases overlap or exceed full wall")
    _check(attempt["overhead_ns"]["service"] <= attempt["finished_ns"] - attempt["service_started_ns"],
           "service exceeds remaining attempt duration")
    _validate_environment(attempt["environment"])
    expected = {request["request_id"]: request for request in workload["requests"]}
    _check(type(attempt["requests"]) is list, "requests must be a list")
    seen = set()
    for request in attempt["requests"]:
        _keys(request, REQUEST_KEYS, "request")
        identifier = request["request_id"]
        _text(identifier, "request_id")
        _check(identifier in expected, "unexpected request ID")
        _check(identifier not in seen, "duplicate request ID")
        seen.add(identifier)
        for field in ("arrival_ns", "admitted_ns", "dispatch_ns", "completed_ns"):
            _integer(request[field], field)
        _check(request["arrival_ns"] == attempt["service_started_ns"] + expected[identifier]["arrival_offset_ns"],
               "arrival differs from the frozen trace")
        _check(request["arrival_ns"] <= request["admitted_ns"] <= request["dispatch_ns"] <=
               request["completed_ns"] <= attempt["finished_ns"], "invalid request clock order")
        _check(request["completed_ns"] - attempt["service_started_ns"] <= attempt["overhead_ns"]["service"],
               "service accounting excludes request time")
        _integer(request["prompt_tokens"], "prompt_tokens", 1, 2**31 - 1)
        _tokens(request["output_token_ids"], "output_token_ids")
        if request["generated_tokens"] is not None:
            _integer(request["generated_tokens"], "generated_tokens", 0, 4096)
            _check(request["generated_tokens"] >= len(request["output_token_ids"]),
                   "generated token count is smaller than observed output IDs")
        _text(request["output_text"], "output_text", empty=True)
        _choice(request["status"], ("SUCCEEDED", "FAILED", "CANCELLED"), "request.status")
        _check(request["status"] != "SUCCEEDED" or request["generated_tokens"] is not None,
               "successful request requires the actual generated token counter")
        _check(not (request["status"] == "SUCCEEDED" and request["output_text"] and
                    not request["output_token_ids"]), "successful nonempty text has no observed output tokens")
        _choice(request["finish_reason"], ("eos", "limit", "error", "cancelled"), "finish_reason")
        reasons = {"SUCCEEDED": ("eos", "limit"), "FAILED": ("error",), "CANCELLED": ("cancelled",)}
        _check(request["finish_reason"] in reasons[request["status"]], "status/finish reason mismatch")
        events = request["token_events"]
        _check(type(events) is list, "token_events must be a list")
        observed_tokens = []
        first_observed = None
        previous = request["dispatch_ns"]
        for event in events:
            _keys(event, {"observed_ns", "token_ids"}, "token event")
            _integer(event["observed_ns"], "token event observed_ns")
            _tokens(event["token_ids"], "token event token_ids")
            _check(previous <= event["observed_ns"] <= request["completed_ns"], "invalid chunk clock order")
            previous = event["observed_ns"]
            if event["token_ids"] and first_observed is None:
                first_observed = event["observed_ns"]
            observed_tokens.extend(event["token_ids"])
        _check(observed_tokens == request["output_token_ids"], "chunk tokens differ from final tokens")
        if request["first_token_ns"] is not None:
            _integer(request["first_token_ns"], "first_token_ns")
        _check(request["first_token_ns"] == first_observed, "first token must equal first nonempty token chunk")
        _check(request["engine_start_ns"] is None,
               "engine_start_ns must be null: the fixed adapter has no engine-start probe")
    if attempt["status"] == "COMPLETED":
        _check(seen == set(expected), "completed attempt has missing requests")
    # A concurrency label must be backed by the observed admission intervals.
    boundaries = []
    for request in attempt["requests"]:
        if request["admitted_ns"] < request["completed_ns"]:
            boundaries.extend(((request["admitted_ns"], 1), (request["completed_ns"], -1)))
    active = 0
    for _, change in sorted(boundaries):
        active += change
        _check(active <= attempt["concurrency"], "observed in-flight count exceeds declared concurrency")
    by_id = {row["request_id"]: row for row in attempt["requests"]}
    for lane in range(attempt["concurrency"]):
        previous_completion = attempt["service_started_ns"]
        for expected_request in workload["requests"][lane::attempt["concurrency"]]:
            request = by_id.get(expected_request["request_id"])
            if request is not None:
                _check(request["admitted_ns"] >= previous_completion,
                       "request order violates the frozen deterministic lane assignment")
                previous_completion = request["completed_ns"]


def _distribution(values: list[int | float]) -> dict:
    ordered = sorted(values)
    result = {"count": len(ordered), "mean": None, "p50": None, "p95": None, "p99": None,
              "method": "nearest_rank", "unit": "ns"}
    if ordered:
        result["mean"] = statistics.fmean(ordered)
        for key, quantile in (("p50", .5), ("p95", .95), ("p99", .99)):
            result[key] = ordered[math.ceil(quantile * len(ordered)) - 1]
    return result


def _unavailable(scope: str) -> dict:
    return {"status": "UNAVAILABLE", "scope": scope, "value": None}


def _summarize(attempt: dict, workload: dict) -> dict:
    records = attempt["requests"]
    expected = {row["request_id"]: row for row in workload["requests"]}
    missing_ids = sorted(set(expected) - {row["request_id"] for row in records})
    statuses = Counter(row["status"] for row in records)
    correct = sum(row["status"] == "SUCCEEDED" and
                  row["output_text"].strip() == expected[row["request_id"]]["expected"] for row in records)
    truncated = sum(row["finish_reason"] == "limit" for row in records)
    over_budget = sum((row["generated_tokens"] is not None and row["generated_tokens"] > 32) or
                      len(row["output_token_ids"]) > 32 for row in records)
    quality = correct / len(expected)  # Failures and absent requests stay in this denominator.
    tokens = sum(len(row["output_token_ids"]) for row in records)
    successful_tokens = sum(len(row["output_token_ids"]) for row in records if row["status"] == "SUCCEEDED")
    service_ns = attempt["overhead_ns"]["service"]
    full_wall_ns = attempt["finished_ns"] - attempt["started_ns"]
    reasons = []
    if attempt["status"] != "COMPLETED":
        reasons.append("attempt_not_completed")
    if missing_ids:
        reasons.append("missing_requests")
    if statuses["SUCCEEDED"] != len(expected):
        reasons.append("not_all_requests_succeeded")
    if truncated:
        reasons.append("length_limit_completion")
    if over_budget:
        reasons.append("generated_token_budget_exceeded")
    if quality < QUALITY_MINIMUM:
        reasons.append("absolute_quality_below_0.95")
    if not service_ns:
        reasons.append("zero_service_duration")
    latency = {
        "client_queue_ns": _distribution([row["admitted_ns"] - row["arrival_ns"] for row in records]),
        "admission_to_dispatch_ns": _distribution([row["dispatch_ns"] - row["admitted_ns"] for row in records]),
        "client_ttft_ns": _distribution([row["first_token_ns"] - row["arrival_ns"] for row in records
                                          if row["first_token_ns"] is not None]),
        "client_end_to_end_ns": _distribution([row["completed_ns"] - row["arrival_ns"] for row in records]),
        "client_chunk_gap_ns": _distribution([second - first for row in records
                for times in [[event["observed_ns"] for event in row["token_events"] if event["token_ids"]]]
                for first, second in zip(times, times[1:])]),
    }
    strata = {}
    for stratum in sorted({row["stratum"] for row in expected.values()}):
        ids = {key for key, value in expected.items() if value["stratum"] == stratum}
        present = [row for row in records if row["request_id"] in ids]
        stratum_correct = sum(row["status"] == "SUCCEEDED" and row["output_text"].strip() ==
                              expected[row["request_id"]]["expected"] for row in present)
        strata[str(stratum)] = {"expected_count": len(ids), "observed_count": len(present),
                               "quality_accuracy": stratum_correct / len(ids),
                               "client_end_to_end_ns": _distribution([
                                   row["completed_ns"] - row["arrival_ns"] for row in present])}
    return {
        "attempt_id": attempt["attempt_id"], "evidence_class": attempt["evidence_class"],
        "arm": attempt["arm"], "concurrency": attempt["concurrency"], "pair_index": attempt["pair_index"],
        "status": attempt["status"], "eligible": not reasons, "ineligibility_reasons": reasons,
        "expected_requests": len(expected), "observed_requests": len(records), "missing_request_ids": missing_ids,
        "succeeded_requests": statuses["SUCCEEDED"], "failed_requests": statuses["FAILED"],
        "cancelled_requests": statuses["CANCELLED"], "truncated_requests": truncated,
        "over_token_budget_requests": over_budget,
        "quality_correct": correct, "quality_denominator": len(expected), "quality_accuracy": quality,
        "quality_pass": quality >= QUALITY_MINIMUM, "output_tokens_observed": tokens,
        "generated_tokens_reported": sum(row["generated_tokens"] for row in records if row["generated_tokens"] is not None),
        "generated_tokens_unknown_requests": sum(row["generated_tokens"] is None for row in records),
        "generated_minus_visible_tokens": sum(row["generated_tokens"] - len(row["output_token_ids"])
                                               for row in records if row["generated_tokens"] is not None),
        "prompt_tokens_observed": sum(row["prompt_tokens"] for row in records),
        "successful_requests_per_second": statuses["SUCCEEDED"] * 1e9 / service_ns if service_ns else None,
        "successful_output_tokens_per_second": successful_tokens * 1e9 / service_ns if service_ns else None,
        "service_ns": service_ns, "full_wall_ns": full_wall_ns, "overhead_ns": dict(attempt["overhead_ns"]),
        "unattributed_wall_ns": full_wall_ns - sum(attempt["overhead_ns"].values()),
        "latency": latency, "strata": strata, "environment": attempt["environment"],
        "dispatch_to_engine_start_ns": _unavailable("the fixed adapter has no engine-start probe"),
        "inter_token_latency_ns": _unavailable("stream chunks do not establish individual engine token emission times"),
        "accelerator_memory_bytes": _unavailable("CPU adapter has no accelerator probe"),
        "denominator_notes": "Quality uses all 128 expected requests. Latency includes every retained terminal request; "
                             "TTFT includes only requests with an observed nonempty token chunk. Missing counts remain explicit.",
    }


def summarize_attempt(attempt: Any, workload: Any, *, config_sha256: str,
                      workload_sha256: str, config: Any=None) -> dict:
    if type(workload) is dict and workload.get('schema_version') == 3:
        from .evidence_v3 import summarize_attempt_v3
        return summarize_attempt_v3(attempt,workload,config=config,config_sha256=config_sha256,workload_sha256=workload_sha256)
    if type(workload) is dict and workload.get('schema_version')==2:
        if config is None:raise EvidenceError('v2 summary requires its frozen configuration')
        from .evidence_v2 import summarize_attempt_v2
        return summarize_attempt_v2(attempt,workload,config=config,config_sha256=config_sha256,workload_sha256=workload_sha256)
    validate_attempt(attempt, workload, config_sha256=config_sha256, workload_sha256=workload_sha256)
    return _summarize(attempt, workload)


def evaluate_campaign(attempts: Any, workload: Any, *, config: Any, config_sha256: str,
                      workload_sha256: str) -> dict:
    """Account for every supplied attempt; fixed 12-cell design, descriptive pair ranges.

    A retry remains a campaign cost and makes this fixed-design campaign ineligible.
    A new registered campaign may be run; this evaluator never cherry-picks a retry.
    Malformed evidence raises; well-formed adverse evidence returns INELIGIBLE.
    """
    if type(config) is dict and config.get('schema_version') == 3:
        from .evidence_v3 import evaluate_campaign_v3
        return evaluate_campaign_v3(attempts,workload,config=config,config_sha256=config_sha256,workload_sha256=workload_sha256)
    if type(config) is dict and config.get('schema_version')==2:
        from .evidence_v2 import evaluate_campaign_v2
        return evaluate_campaign_v2(attempts,workload,config=config,config_sha256=config_sha256,workload_sha256=workload_sha256)
    try:
        validate_config(config)
    except ContractError as exc:
        raise EvidenceError(str(exc)) from exc
    _check(digest(config) == config_sha256, "configuration digest does not match frozen input")
    _check(type(attempts) is list and bool(attempts), "campaign requires at least one attempt")
    for attempt in attempts:
        validate_attempt(attempt, workload, config_sha256=config_sha256, workload_sha256=workload_sha256)
        _check(attempt["evidence_class"] == config["evidence_class"], "configuration evidence class mismatch")
        _check(attempt["environment"]["platform"] == config["hardware"]["platform"] and
               attempt["environment"]["cpu"] == config["hardware"]["cpu"],
               "hardware identity differs from frozen configuration")
    _check(len({a["attempt_id"] for a in attempts}) == len(attempts), "duplicate attempt ID")
    ordered = sorted(attempts, key=lambda a: a["started_ns"])
    _check(all(a["finished_ns"] <= b["started_ns"] for a, b in zip(ordered, ordered[1:])),
           "attempts overlap; sequential study costs cannot be summed")
    summaries = [_summarize(attempt, workload) for attempt in ordered]
    classes = {a["evidence_class"] for a in attempts}
    _check(len(classes) == 1, "cannot mix measured evidence and test fixtures")
    evidence_class = next(iter(classes))
    reasons = []
    if len(attempts) != 12:
        reasons.append("fixed_design_requires_exactly_12_attempts")
    if any(not row["eligible"] for row in summaries):
        reasons.append("one_or_more_attempts_ineligible")
    cells = {}
    prompt_counts = {}
    for attempt in ordered:
        key = (attempt["concurrency"], attempt["pair_index"], attempt["arm"])
        cells.setdefault(key, []).append(attempt)
        for request in attempt["requests"]:
            prompt_counts.setdefault(request["request_id"], set()).add(request["prompt_tokens"])
    prompt_identity_drift_ids = {identifier for identifier, counts in prompt_counts.items() if len(counts) != 1}
    if prompt_identity_drift_ids:
        reasons.append("prompt_token_counts_changed_across_attempts")
    wanted = {(c, p, arm) for c in (1, 4) for p in range(3) for arm in ("baseline", "candidate")}
    if set(cells) != wanted or any(len(value) != 1 for value in cells.values()):
        reasons.append("missing_or_duplicate_comparison_cells")
    groups = {}
    for concurrency in (1, 4):
        actual_order = [(a["pair_index"], a["arm"]) for a in ordered if a["concurrency"] == concurrency]
        wanted_order = [(p, arm) for p in range(3)
                        for arm in (("baseline", "candidate") if p != 1 else ("candidate", "baseline"))]
        order_ok = actual_order == wanted_order
        if not order_ok:
            reasons.append(f"concurrency_{concurrency}_counterbalanced_order_invalid")
        pairs = []
        for pair in range(3):
            left = cells.get((concurrency, pair, "baseline"), [])
            right = cells.get((concurrency, pair, "candidate"), [])
            if len(left) != 1 or len(right) != 1:
                continue
            baseline, candidate = left[0], right[0]
            left_requests = {r["request_id"]: r for r in baseline["requests"]}
            right_requests = {r["request_id"]: r for r in candidate["requests"]}
            mismatches = sorted(identifier for identifier in set(left_requests) | set(right_requests)
                                if identifier not in left_requests or identifier not in right_requests or
                                left_requests[identifier]["output_token_ids"] != right_requests[identifier]["output_token_ids"] or
                                left_requests[identifier]["generated_tokens"] != right_requests[identifier]["generated_tokens"])
            prompt_mismatches = sorted(identifier for identifier in set(left_requests) & set(right_requests)
                                       if left_requests[identifier]["prompt_tokens"] != right_requests[identifier]["prompt_tokens"])
            prompt_identity_drift = sorted(prompt_identity_drift_ids & (set(left_requests) | set(right_requests)))
            parity = not mismatches and len(left_requests) == len(right_requests) == 128
            if not parity or prompt_mismatches:
                reasons.append(f"concurrency_{concurrency}_pair_{pair}_token_identity_or_parity_failed")
            base = _summarize(baseline, workload)
            cand = _summarize(candidate, workload)
            valid_pair = (base["eligible"] and cand["eligible"] and parity and
                          not prompt_mismatches and not prompt_identity_drift)
            ratio = (cand["successful_requests_per_second"] / base["successful_requests_per_second"]
                     if valid_pair else None)
            tail_ratios = {}
            ttft_tail_ratios = {}
            for percentile in ("p95", "p99"):
                before = base["latency"]["client_end_to_end_ns"][percentile]
                after = cand["latency"]["client_end_to_end_ns"][percentile]
                tail_ratios[percentile] = after / before if valid_pair and before else None
                ttft_before = base["latency"]["client_ttft_ns"][percentile]
                ttft_after = cand["latency"]["client_ttft_ns"][percentile]
                ttft_tail_ratios[percentile] = (ttft_after / ttft_before
                                              if valid_pair and ttft_before and ttft_after is not None else None)
            pairs.append({"pair_index": pair, "baseline_attempt_id": baseline["attempt_id"],
                          "candidate_attempt_id": candidate["attempt_id"], "eligible": bool(valid_pair),
                          "token_parity": parity, "token_mismatch_request_ids": mismatches,
                          "prompt_token_mismatch_request_ids": prompt_mismatches,
                          "campaign_prompt_identity_drift_request_ids": prompt_identity_drift,
                          "throughput_candidate_over_baseline": ratio,
                          "end_to_end_tail_candidate_over_baseline": tail_ratios,
                          "ttft_tail_candidate_over_baseline": ttft_tail_ratios})
        ratios = [p["throughput_candidate_over_baseline"] for p in pairs
                  if p["throughput_candidate_over_baseline"] is not None]
        tails = [v for p in pairs for metric in ("end_to_end_tail_candidate_over_baseline", "ttft_tail_candidate_over_baseline")
                 for v in p[metric].values() if v is not None]
        complete = len(ratios) == 3 and order_ok
        if not complete:
            finding = "INELIGIBLE"
        elif any(value > 1 + TAIL_REGRESSION for value in tails):
            finding = "TAIL_REGRESSION"
        elif min(ratios) >= 1 + PRACTICAL_GAIN:
            finding = "PRACTICAL_GAIN_IN_ALL_THREE_PAIRS"
        else:
            finding = "NO_DEMONSTRATED_PRACTICAL_GAIN"
        groups[str(concurrency)] = {"pairs": pairs, "counterbalanced_order_valid": order_ok,
                                   "pair_count": len(ratios), "throughput_ratio_median": statistics.median(ratios) if ratios else None,
                                   "throughput_ratio_range": [min(ratios), max(ratios)] if ratios else None,
                                   "finding": finding, "eligible": complete}
    eligible = not reasons
    if not eligible:
        # Retain diagnostic pair observations, but a rejected registered campaign
        # cannot yield a gain recommendation through a seemingly healthy subgroup.
        for group in groups.values():
            group["eligible"] = False
            group["finding"] = "INELIGIBLE"
            group["ineligibility_reasons"] = sorted(set(reasons))
    # Fixture findings exercise calculations and can never become measured public claims.
    claim_eligible = False  # Complete inventory and setup must be verified by evaluate_inventory.
    return {"schema_version": 1, "evaluator_version": "0.1.0", "evidence_class": evidence_class,
            "config_sha256": config_sha256, "workload_sha256": workload_sha256,
            "eligible": eligible, "measured_claim_eligible": claim_eligible,
            "finding": "TEST_FIXTURE_ONLY" if evidence_class == "TEST_FIXTURE" else
                       ("PAIRED_DEVICE_SPECIFIC_RESULT" if eligible else "INELIGIBLE"),
            "ineligibility_reasons": sorted(set(reasons)), "attempts": summaries, "concurrency_groups": groups,
            "accounting": {"attempt_count": len(attempts), "expected_requests_across_attempts": 128 * len(attempts),
                           "observed_requests": sum(row["observed_requests"] for row in summaries),
                           "missing_requests": sum(len(row["missing_request_ids"]) for row in summaries),
                           "visible_output_tokens_observed": sum(row["output_tokens_observed"] for row in summaries),
                           "generated_tokens_reported": sum(row["generated_tokens_reported"] for row in summaries),
                           "generated_tokens_unknown_requests": sum(row["generated_tokens_unknown_requests"] for row in summaries),
                           "full_wall_ns": sum(row["full_wall_ns"] for row in summaries),
                           "elapsed_span_ns": ordered[-1]["finished_ns"] - ordered[0]["started_ns"],
                           "overhead_ns": {key: sum(row["overhead_ns"][key] for row in summaries) for key in sorted(OVERHEAD_KEYS)},
                           "unattributed_wall_ns": sum(row["unattributed_wall_ns"] for row in summaries),
                           "setup_acquisition_build_costs": _unavailable("not included in attempt documents; require separate retained setup ledger"),
                           "monetary_cost": _unavailable("no monetary-cost probe or estimate")},
            "thresholds": {"absolute_accuracy": QUALITY_MINIMUM, "practical_throughput_gain": PRACTICAL_GAIN,
                           "maximum_tail_regression": TAIL_REGRESSION},
            "limitations": ["Three independent pairs per concurrency; ranges are descriptive, not confidence intervals or significance tests.",
                            "128-request p95/p99 estimates, and 32-request stratum tails, are unstable.",
                            "Client chunk receipts do not establish individual token emission times or engine-internal latency.",
                            "Synthetic key copying does not establish general language-model competence.",
                            "All supplied attempts are retained; this file alone cannot prove omitted attempts do not exist.",
                            "Digest consistency does not authenticate externally supplied observations.",
                            "Attempt-only evaluation does not verify complete inventory or acquisition/build costs.",
                            "Device-specific finite queued batch; no online serving, energy, or cross-device superiority claim."]}
