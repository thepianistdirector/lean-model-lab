"""Model-free scientific-integrity mutations; fixture timings are not measurements."""
import copy
import unittest

from lean_model_lab.contracts import digest, make_workload
from lean_model_lab.config import make_config
from lean_model_lab.evidence import (EvidenceError, OVERHEAD_KEYS, evaluate_campaign,
                                     summarize_attempt, validate_attempt)

CONFIG = make_config(server_sha256="a"*64, evidence_class="TEST_FIXTURE", hardware={"platform":"fixture", "cpu":"fixture"})
CONFIG_SHA256 = digest(CONFIG)


def make_attempt(*, arm="baseline", concurrency=1, pair_index=0, started_ns=1_000,
                 duration_ns=100, workload=None):
    workload = make_workload() if workload is None else workload
    service_start = started_ns + 1_000
    records = []
    for index, request in enumerate(workload["requests"]):
        admitted = service_start + (index // concurrency) * duration_ns
        tokens = [ord(letter) for letter in request["expected"]]
        first = admitted + duration_ns // 2
        records.append({"request_id": request["request_id"], "arrival_ns": service_start,
                        "admitted_ns": admitted, "dispatch_ns": admitted + 1,
                        "first_token_ns": first, "completed_ns": admitted + duration_ns,
                        "token_events": [{"observed_ns": first, "token_ids": tokens[:2]},
                                         {"observed_ns": first + 1, "token_ids": tokens[2:]}],
                        "output_token_ids": tokens, "output_text": request["expected"],
                        "finish_reason": "eos", "status": "SUCCEEDED", "prompt_tokens": request["stratum"] + 30,
                        "generated_tokens": len(tokens), "engine_start_ns": None})
    service_ns = max(row["completed_ns"] for row in records) - service_start
    overhead = {key: 0 for key in OVERHEAD_KEYS}
    overhead.update(startup=100, verification=200, load=300, warmup=400,
                    service=service_ns, evaluation=50, reporting=50)
    unavailable = {"status": "UNAVAILABLE", "scope": "no probe in test fixture", "value": None, "unit": "unavailable"}
    return {"schema_version": 1, "evidence_class": "TEST_FIXTURE",
            "attempt_id": f"fixture-{concurrency}-{pair_index}-{arm}-{started_ns}",
            "config_sha256": CONFIG_SHA256, "workload_sha256": digest(workload),
            "arm": arm, "concurrency": concurrency, "pair_index": pair_index,
            "started_ns": started_ns, "service_started_ns": service_start,
            "finished_ns": service_start + service_ns + 100, "status": "COMPLETED",
            "requests": records, "overhead_ns": overhead,
            "environment": {"observer": "unittest", "version": "0.1.0", "platform": "fixture",
                            "cpu": "fixture", **{key: dict(unavailable) for key in ("load", "thermal", "memory", "energy")}}}


def make_campaign(candidate_duration_ns=80):
    attempts = []
    started = 1_000
    for concurrency in (1, 4):
        for pair in range(3):
            for arm in (("baseline", "candidate") if pair != 1 else ("candidate", "baseline")):
                attempt = make_attempt(arm=arm, concurrency=concurrency, pair_index=pair,
                                       started_ns=started, duration_ns=candidate_duration_ns if arm == "candidate" else 100)
                attempts.append(attempt)
                started = attempt["finished_ns"] + 100
    return attempts


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.workload = make_workload()
        self.identity = {"config_sha256": CONFIG_SHA256, "workload_sha256": digest(self.workload)}
        self.attempt = make_attempt()

    def validate(self, attempt=None):
        validate_attempt(self.attempt if attempt is None else attempt, self.workload, **self.identity)

    def summary(self, attempt=None):
        return summarize_attempt(self.attempt if attempt is None else attempt, self.workload, **self.identity)

    def evaluate(self, attempts):
        return evaluate_campaign(attempts, self.workload, config=CONFIG, **self.identity)

    def test_metrics_keep_units_denominators_and_chunk_scope(self):
        result = self.summary()
        self.assertEqual(result["quality_accuracy"], 1)
        self.assertEqual(result["quality_denominator"], 128)
        self.assertEqual(result["output_tokens_observed"], 640)
        self.assertEqual(result["latency"]["client_end_to_end_ns"]["p95"], 12_200)
        self.assertEqual(result["latency"]["client_end_to_end_ns"]["p99"], 12_700)
        self.assertEqual(result["latency"]["client_chunk_gap_ns"]["count"], 128)
        self.assertEqual(result["latency"]["client_chunk_gap_ns"]["mean"], 1)
        self.assertEqual(result["inter_token_latency_ns"]["status"], "UNAVAILABLE")
        self.assertEqual(result["dispatch_to_engine_start_ns"]["status"], "UNAVAILABLE")
        self.assertEqual(result["strata"]["16"]["expected_count"], 32)
        self.assertEqual(result["unattributed_wall_ns"], 0)

    def test_duplicate_missing_extra_and_unknown_fields_fail(self):
        mutations = [lambda a: a["requests"].append(copy.deepcopy(a["requests"][0])),
                     lambda a: a["requests"].pop(),
                     lambda a: a["requests"][0].update(request_id="foreign"),
                     lambda a: a.update(quality_threshold=0),
                     lambda a: a["requests"][0].update(engine_latency=1),
                     lambda a: a["requests"][0].pop("engine_start_ns"),
                     lambda a: a["requests"][0]["token_events"][0].update(invented=1),
                     lambda a: a["overhead_ns"].update(hidden=0)]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                attempt = copy.deepcopy(self.attempt)
                mutation(attempt)
                with self.assertRaises(EvidenceError):
                    self.validate(attempt)

    def test_identity_and_quality_plan_mutations_fail(self):
        for field in ("config_sha256", "workload_sha256"):
            attempt = copy.deepcopy(self.attempt)
            attempt[field] = "b" * 64
            with self.assertRaises(EvidenceError):
                self.validate(attempt)
        self.workload["quality"]["minimum_accuracy"] = 0.5
        self.identity["workload_sha256"] = digest(self.workload)
        self.attempt["workload_sha256"] = digest(self.workload)
        with self.assertRaises(EvidenceError):
            self.validate()

    def test_expected_workload_digest_is_recomputed(self):
        self.identity["workload_sha256"] = "b" * 64
        self.attempt["workload_sha256"] = "b" * 64
        with self.assertRaises(EvidenceError):
            self.validate()

    def test_nonfinite_boolean_negative_and_float_timestamps_fail(self):
        for value in (float("nan"), float("inf"), -1, True, 2000.0, "2000", None):
            with self.subTest(value=value):
                attempt = copy.deepcopy(self.attempt)
                attempt["requests"][0]["dispatch_ns"] = value
                with self.assertRaises(EvidenceError):
                    self.validate(attempt)
        for field, value in (("concurrency", True), ("pair_index", True), ("schema_version", True)):
            attempt = copy.deepcopy(self.attempt)
            attempt[field] = value
            with self.assertRaises(EvidenceError):
                self.validate(attempt)

    def test_clock_inversions_and_changed_arrival_fail(self):
        mutations = [lambda a: a.update(service_started_ns=a["started_ns"] - 1),
                     lambda a: a.update(finished_ns=a["started_ns"]),
                     lambda a: a["requests"][0].update(arrival_ns=a["service_started_ns"] + 1),
                     lambda a: a["requests"][0].update(admitted_ns=a["service_started_ns"] - 1),
                     lambda a: a["requests"][0].update(dispatch_ns=a["finished_ns"]),
                     lambda a: a["requests"][0].update(completed_ns=a["finished_ns"] + 1),
                     lambda a: a["requests"][0].update(engine_start_ns=a["started_ns"]),
                     lambda a: a["requests"][0]["token_events"].reverse()]
        for mutation in mutations:
            attempt = copy.deepcopy(self.attempt)
            mutation(attempt)
            with self.assertRaises(EvidenceError):
                self.validate(attempt)

    def test_plausible_engine_start_is_rejected_when_adapter_cannot_observe_it(self):
        self.attempt["requests"][0]["engine_start_ns"] = self.attempt["requests"][0]["dispatch_ns"]
        with self.assertRaisesRegex(EvidenceError, "fixed adapter has no engine-start probe"):
            self.validate()

    def test_token_constraints_and_invented_first_token_fail(self):
        mutations = [lambda r: r.update(first_token_ns=r["first_token_ns"] - 1),
                     lambda r: r["output_token_ids"].append(42),
                     lambda r: r.update(output_token_ids=[1] * 4097),
                     lambda r: r.update(token_events=[]),
                     lambda r: r["token_events"][0].update(token_ids=[True]),
                     lambda r: r.update(generated_tokens=0),
                     lambda r: r.update(status="FAILED")]
        for mutation in mutations:
            attempt = copy.deepcopy(self.attempt)
            mutation(attempt["requests"][0])
            with self.assertRaises(EvidenceError):
                self.validate(attempt)

    def test_overhead_cannot_hide_service_or_exceed_full_wall(self):
        for key, value in (("service", 1), ("load", 100_000), ("recovery", -1), ("startup", float("nan"))):
            attempt = copy.deepcopy(self.attempt)
            attempt["overhead_ns"][key] = value
            with self.assertRaises(EvidenceError):
                self.validate(attempt)

    def test_unsupported_probes_cannot_smuggle_numbers(self):
        self.attempt["environment"]["energy"]["value"] = 100
        with self.assertRaises(EvidenceError):
            self.validate()
        for value in (float("nan"), float("inf"), True, -1, [], "100", 10**1000):
            self.attempt["environment"]["energy"].update(status="MEASURED", value=value)
            with self.assertRaises(EvidenceError):
                self.validate()

    def test_declared_concurrency_is_enforced(self):
        attempt = make_attempt(concurrency=4)
        attempt["concurrency"] = 1
        with self.assertRaises(EvidenceError):
            self.validate(attempt)

    def test_deterministic_lanes_cannot_be_reordered(self):
        attempt = make_attempt(concurrency=4)
        first, fifth = attempt["requests"][0], attempt["requests"][4]
        first["request_id"], fifth["request_id"] = fifth["request_id"], first["request_id"]
        with self.assertRaises(EvidenceError):
            self.validate(attempt)

    def test_success_text_requires_observed_tokens(self):
        self.attempt["requests"][0].update(output_token_ids=[], token_events=[], first_token_ns=None)
        with self.assertRaises(EvidenceError):
            self.validate()

    def test_quality_gate_is_absolute_and_exact(self):
        for request in self.attempt["requests"][:6]:
            request["output_text"] = "wrong"
        self.assertTrue(self.summary()["quality_pass"])
        self.attempt["requests"][6]["output_text"] += "."
        self.assertFalse(self.summary()["quality_pass"])
        self.assertFalse(self.summary()["eligible"])
        self.attempt["requests"][6]["output_text"] = "  " + self.workload["requests"][6]["expected"] + "\n"
        self.assertTrue(self.summary()["quality_pass"])

    def test_failed_cancelled_and_truncated_requests_are_ineligible(self):
        for status, reason in (("FAILED", "error"), ("CANCELLED", "cancelled"), ("SUCCEEDED", "limit")):
            attempt = copy.deepcopy(self.attempt)
            request = attempt["requests"][0]
            request.update(status=status, finish_reason=reason)
            if reason == "limit":
                request["output_token_ids"] = [1] * 32
                request["generated_tokens"] = 32
                request["token_events"] = [{"observed_ns": request["first_token_ns"], "token_ids": [1] * 32}]
            result = self.summary(attempt)
            self.assertFalse(result["eligible"])
            self.assertEqual(result["observed_requests"], 128)
            self.assertEqual(result["quality_denominator"], 128)

    def test_empty_output_has_no_fabricated_ttft_and_fails_quality(self):
        for request in self.attempt["requests"]:
            request.update(output_token_ids=[], token_events=[], output_text="", first_token_ns=None, generated_tokens=0)
        result = self.summary()
        self.assertEqual(result["latency"]["client_ttft_ns"]["count"], 0)
        self.assertIsNone(result["latency"]["client_ttft_ns"]["p99"])
        self.assertEqual(result["quality_accuracy"], 0)

    def test_interrupted_attempt_retains_missing_denominator_and_cost(self):
        self.attempt["status"] = "INTERRUPTED"
        self.attempt["requests"] = self.attempt["requests"][:64]
        result = self.evaluate([self.attempt])
        summary = result["attempts"][0]
        self.assertEqual(summary["quality_accuracy"], 0.5)
        self.assertEqual(len(summary["missing_request_ids"]), 64)
        self.assertEqual(result["accounting"]["full_wall_ns"], self.attempt["finished_ns"] - self.attempt["started_ns"])
        self.assertEqual(result["accounting"]["expected_requests_across_attempts"], 128)
        self.assertFalse(result["eligible"])

    def test_three_pairs_support_only_descriptive_fixture_result(self):
        result = self.evaluate(make_campaign())
        self.assertTrue(result["eligible"])
        self.assertFalse(result["measured_claim_eligible"])
        self.assertEqual(result["finding"], "TEST_FIXTURE_ONLY")
        for group in result["concurrency_groups"].values():
            self.assertEqual(group["pair_count"], 3)
            self.assertEqual(group["throughput_ratio_range"], [1.25, 1.25])
            self.assertEqual(group["finding"], "PRACTICAL_GAIN_IN_ALL_THREE_PAIRS")

    def test_no_gain_and_regression_are_preserved(self):
        equal = self.evaluate(make_campaign(candidate_duration_ns=100))
        worse = self.evaluate(make_campaign(candidate_duration_ns=120))
        for group in equal["concurrency_groups"].values():
            self.assertEqual(group["finding"], "NO_DEMONSTRATED_PRACTICAL_GAIN")
        for group in worse["concurrency_groups"].values():
            self.assertEqual(group["finding"], "TAIL_REGRESSION")

    def test_token_parity_is_separate_from_absolute_quality(self):
        attempts = make_campaign()
        candidate = attempts[1]["requests"][0]
        candidate["output_token_ids"][0] = 999
        candidate["token_events"][0]["token_ids"][0] = 999
        result = self.evaluate(attempts)
        self.assertTrue(result["attempts"][1]["quality_pass"])
        self.assertFalse(result["eligible"])
        self.assertFalse(result["concurrency_groups"]["1"]["pairs"][0]["token_parity"])

    def test_tokenizer_count_mutation_invalidates_pair(self):
        attempts = make_campaign()
        attempts[1]["requests"][0]["prompt_tokens"] += 1
        result = self.evaluate(attempts)
        self.assertFalse(result["eligible"])

    def test_matching_tokenizer_drift_across_pairs_is_not_hidden(self):
        attempts = make_campaign()
        for attempt in attempts[:2]:
            attempt["requests"][0]["prompt_tokens"] += 1
        result = self.evaluate(attempts)
        self.assertFalse(result["eligible"])
        self.assertIn("prompt_token_counts_changed_across_attempts", result["ineligibility_reasons"])
        for group in result["concurrency_groups"].values():
            self.assertFalse(group["eligible"])
            self.assertEqual(group["finding"], "INELIGIBLE")
            self.assertEqual(group["pair_count"], 0)
            self.assertIsNone(group["throughput_ratio_range"])
            for pair in group["pairs"]:
                self.assertFalse(pair["eligible"])
                self.assertEqual(pair["campaign_prompt_identity_drift_request_ids"], ["r000"])
                self.assertIsNone(pair["throughput_candidate_over_baseline"])

    def test_incomplete_campaign_cannot_recommend_gain_from_complete_subgroup(self):
        result = self.evaluate(make_campaign()[:-1])
        self.assertFalse(result["eligible"])
        complete_group = result["concurrency_groups"]["1"]
        self.assertEqual(complete_group["pair_count"], 3)
        self.assertEqual(complete_group["throughput_ratio_range"], [1.25, 1.25])
        self.assertFalse(complete_group["eligible"])
        self.assertEqual(complete_group["finding"], "INELIGIBLE")
        self.assertIn("fixed_design_requires_exactly_12_attempts", complete_group["ineligibility_reasons"])

    def test_generated_eos_counter_is_separate_from_visible_tokens(self):
        self.attempt["requests"][0]["generated_tokens"] += 1
        result = self.summary()
        self.assertEqual(result["generated_minus_visible_tokens"], 1)
        self.assertEqual(result["output_tokens_observed"], 640)
        self.assertEqual(result["generated_tokens_reported"], 641)
        self.assertTrue(result["eligible"])

    def test_token_overshoot_is_retained_as_adverse_evidence(self):
        request = self.attempt["requests"][0]
        request["output_token_ids"] = [1] * 33
        request["generated_tokens"] = 34
        request["token_events"] = [{"observed_ns": request["first_token_ns"], "token_ids": [1] * 33}]
        result = self.summary()
        self.assertEqual(result["over_token_budget_requests"], 1)
        self.assertEqual(result["observed_requests"], 128)
        self.assertFalse(result["eligible"])

    def test_length_limit_may_have_fewer_visible_tokens_than_counter(self):
        self.attempt["requests"][0].update(finish_reason="limit", generated_tokens=32)
        result = self.summary()
        self.assertEqual(result["truncated_requests"], 1)
        self.assertFalse(result["eligible"])

    def test_generated_count_parity_is_required(self):
        attempts = make_campaign()
        attempts[1]["requests"][0]["generated_tokens"] += 1
        result = self.evaluate(attempts)
        self.assertFalse(result["eligible"])

    def test_failed_unknown_generated_counter_is_not_fabricated(self):
        self.attempt["requests"][0].update(status="FAILED", finish_reason="error", generated_tokens=None)
        result = self.summary()
        self.assertEqual(result["generated_tokens_unknown_requests"], 1)
        self.assertEqual(result["generated_tokens_reported"], 635)
        self.assertEqual(result["output_tokens_observed"], 640)
        self.assertFalse(result["eligible"])

    def test_success_requires_actual_generated_counter(self):
        self.attempt["requests"][0]["generated_tokens"] = None
        with self.assertRaises(EvidenceError):
            self.validate()

    def test_matching_wrong_answers_do_not_pass_quality(self):
        attempts = make_campaign()
        for attempt in attempts:
            for request in attempt["requests"]:
                request["output_text"] = "wrong"
        result = self.evaluate(attempts)
        self.assertFalse(result["eligible"])
        self.assertTrue(result["concurrency_groups"]["1"]["pairs"][0]["token_parity"])

    def test_bad_counterbalanced_order_is_not_relabelled(self):
        attempts = make_campaign()
        # Exchange actual arm labels in the first AB pair; timestamps stay intact.
        attempts[0]["arm"], attempts[1]["arm"] = attempts[1]["arm"], attempts[0]["arm"]
        result = self.evaluate(attempts)
        self.assertFalse(result["eligible"])
        self.assertFalse(result["concurrency_groups"]["1"]["counterbalanced_order_valid"])

    def test_attempt_array_order_is_not_actual_execution_order(self):
        attempts = make_campaign()
        attempts.reverse()
        self.assertTrue(self.evaluate(attempts)["eligible"])

    def test_retries_and_missing_pair_cannot_select_best_results(self):
        attempts = make_campaign()
        retry = make_attempt(started_ns=attempts[-1]["finished_ns"] + 100)
        result = self.evaluate(attempts + [retry])
        self.assertFalse(result["eligible"])
        self.assertEqual(result["accounting"]["attempt_count"], 13)
        self.assertEqual(result["accounting"]["observed_requests"], 13 * 128)
        self.assertFalse(self.evaluate(attempts[:-1])["eligible"])

    def test_duplicate_ids_overlapping_clocks_and_mixed_classes_fail(self):
        attempts = make_campaign()
        attempts[1]["attempt_id"] = attempts[0]["attempt_id"]
        with self.assertRaises(EvidenceError):
            self.evaluate(attempts)
        attempts = make_campaign()
        attempts[1] = make_attempt(arm="candidate", started_ns=attempts[0]["started_ns"])
        with self.assertRaises(EvidenceError):
            self.evaluate(attempts)
        attempts = make_campaign()
        attempts[1]["evidence_class"] = "MEASURED"
        with self.assertRaises(EvidenceError):
            self.evaluate(attempts)


if __name__ == "__main__":
    unittest.main()
