"""Durability and omitted-evidence controls; all request data are test fixtures."""
import copy
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from lean_model_lab.artifacts import write_json_new
from lean_model_lab.contracts import canonical_bytes, make_workload
from lean_model_lab.session import Session, SessionError, validate_setup_records
from test_evidence import CONFIG, make_attempt


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "study"
        self.workload = make_workload()
        Session.create(self.root, CONFIG, self.workload, [])

    def reserve(self, session, *, concurrency=1):
        attempt = make_attempt(concurrency=concurrency)
        reservation = session.reserve(attempt["arm"], attempt["concurrency"], attempt["pair_index"], attempt["started_ns"])
        attempt["attempt_id"] = reservation["attempt_id"]
        self.assertTrue(reservation["raw_dir"].is_dir())
        return attempt

    def test_create_never_overwrites_existing_session(self):
        original = (self.root / "session.json").read_bytes()
        with self.assertRaises(FileExistsError):
            Session.create(self.root, CONFIG, self.workload, [])
        self.assertEqual((self.root / "session.json").read_bytes(), original)

    def test_exclusive_writer_lease_and_release(self):
        with Session.open(self.root):
            with self.assertRaisesRegex(SessionError, "another writer"):
                with Session.open(self.root):
                    self.fail("second writer entered")
        with Session.open(self.root) as session:
            self.assertTrue(session.inspect()["inventory_complete"])
        with self.assertRaisesRegex(SessionError, "operation requires"):
            session.inspect()

    def test_complete_checkpoint_and_terminal_round_trip(self):
        with Session.open(self.root) as session:
            attempt = self.reserve(session)
            request = attempt["requests"][0]
            session.checkpoint(attempt["attempt_id"], request, request["completed_ns"] + 1)
            path = session.publish(attempt)
            self.assertTrue(path.is_file())
            inventory = session.inspect()
            self.assertTrue(inventory["inventory_complete"])
            self.assertEqual(inventory["reservation_count"], 1)
            self.assertEqual(inventory["attempts"], [attempt])
            self.assertEqual(inventory["event_count"], 3)
        with Session.open(self.root) as session:
            self.assertEqual(session.inspect()["attempts"], [attempt])

    def test_duplicate_publication_does_not_replace_file(self):
        with Session.open(self.root) as session:
            attempt = self.reserve(session)
            path = session.publish(attempt)
            before = path.read_bytes()
            with self.assertRaisesRegex(SessionError, "already published"):
                session.publish(attempt)
            self.assertEqual(path.read_bytes(), before)

    def test_checkpoint_identity_and_duplicate_requests_fail(self):
        with Session.open(self.root) as session:
            attempt = self.reserve(session)
            request = attempt["requests"][0]
            with self.assertRaisesRegex(SessionError, "unfinished reservation"):
                session.checkpoint("attempt-" + "0" * 32, request, request["completed_ns"])
            foreign = copy.deepcopy(request)
            foreign["request_id"] = "foreign"
            with self.assertRaisesRegex(SessionError, "identity is foreign"):
                session.checkpoint(attempt["attempt_id"], foreign, request["completed_ns"])
            session.checkpoint(attempt["attempt_id"], request, request["completed_ns"])
            with self.assertRaisesRegex(SessionError, "duplicate checkpoint"):
                session.checkpoint(attempt["attempt_id"], request, request["completed_ns"])

    def test_checkpoint_mutation_and_omission_cannot_disappear_in_publication(self):
        with Session.open(self.root) as session:
            attempt = self.reserve(session)
            request = attempt["requests"][0]
            session.checkpoint(attempt["attempt_id"], request, request["completed_ns"])
            changed = copy.deepcopy(attempt)
            changed["requests"][0]["output_text"] = "changed"
            with self.assertRaisesRegex(SessionError, "omits or changes"):
                session.publish(changed)
            changed = copy.deepcopy(attempt)
            changed["status"] = "INTERRUPTED"
            changed["requests"].pop(0)
            with self.assertRaisesRegex(SessionError, "omits or changes"):
                session.publish(changed)
            self.assertEqual(session.inspect()["unresolved_attempts"][0]["observed_requests"], 1)

    def test_reservation_identity_cannot_be_relabelled(self):
        with Session.open(self.root) as session:
            attempt = self.reserve(session)
            attempt["arm"] = "candidate"
            with self.assertRaisesRegex(SessionError, "arm differs"):
                session.publish(attempt)

    def test_unfinished_recovery_exposes_only_observed_lower_bound(self):
        with Session.open(self.root) as session:
            attempt = self.reserve(session)
            request = attempt["requests"][0]
            session.checkpoint(attempt["attempt_id"], request, request["completed_ns"] + 7)
        with Session.open(self.root) as session:
            inventory = session.inspect()
            self.assertFalse(inventory["inventory_complete"])
            self.assertEqual(inventory["attempts"], [])
            orphan = inventory["unresolved_attempts"][0]
            self.assertEqual(orphan["state"], "UNFINISHED")
            self.assertEqual(orphan["known_observed_wall_ns_lower_bound"], request["completed_ns"] + 7 - attempt["started_ns"])
            self.assertEqual(len(orphan["unaccounted_request_ids"]), 127)
            self.assertNotIn("finished_ns", orphan)
            with self.assertRaisesRegex(SessionError, "reconcile unfinished"):
                session.reserve("candidate", 1, 0, 1_000_000)

    def test_reserved_without_observation_does_not_invent_zero_elapsed(self):
        with Session.open(self.root) as session:
            self.reserve(session)
            orphan = session.inspect()["unresolved_attempts"][0]
            self.assertIsNone(orphan["known_observed_wall_ns_lower_bound"])
            self.assertIsNone(orphan["observed_until_ns"])

    def test_deleted_published_attempt_is_detected(self):
        with Session.open(self.root) as session:
            path = session.publish(self.reserve(session))
            path.unlink()
            with self.assertRaisesRegex(SessionError, "artifact is missing"):
                session.inspect()

    def test_altered_published_attempt_is_detected(self):
        with Session.open(self.root) as session:
            attempt = self.reserve(session)
            path = session.publish(attempt)
            attempt["requests"][0]["output_text"] = "other"
            path.write_bytes(canonical_bytes(attempt))
            with self.assertRaisesRegex(SessionError, "bytes changed"):
                session.inspect()

    def test_foreign_attempt_file_is_detected(self):
        with Session.open(self.root) as session:
            write_json_new(self.root / "attempts" / ("attempt-" + "0" * 32 + ".json"), make_attempt())
            with self.assertRaisesRegex(SessionError, "no reservation"):
                session.inspect()

    def test_raw_missing_extra_and_modified_files_are_rejected(self):
        with Session.open(self.root) as session:
            attempt = self.reserve(session)
            raw = self.root / "raw" / attempt["attempt_id"]
            original = b'{"observed_ns":2100,"data_utf8":"fixture"}\n'
            (raw / "r000.jsonl").write_bytes(original)
            session.publish(attempt)
            (raw / "r000.jsonl").write_bytes(b"changed")
            with self.assertRaisesRegex(SessionError, "raw artifact inventory changed"):
                session.inspect()
            (raw / "r000.jsonl").unlink()
            with self.assertRaisesRegex(SessionError, "raw artifact inventory changed"):
                session.inspect()
            (raw / "r000.jsonl").write_bytes(original)
            (raw / "extra.jsonl").write_bytes(b"extra")
            with self.assertRaisesRegex(SessionError, "raw artifact inventory changed"):
                session.inspect()

    def test_raw_directory_deletion_is_detected(self):
        with Session.open(self.root) as session:
            attempt = self.reserve(session)
            session.publish(attempt)
            (self.root / "raw" / attempt["attempt_id"]).rmdir()
            with self.assertRaisesRegex(SessionError, "raw attempt directory is missing"):
                session.inspect()

    def test_raw_symlink_cannot_be_published(self):
        with Session.open(self.root) as session:
            attempt = self.reserve(session)
            (self.root / "raw" / attempt["attempt_id"] / "foreign").symlink_to(self.root / "config.json")
            with self.assertRaisesRegex(SessionError, "raw evidence contains a symlink"):
                session.publish(attempt)

    def test_deleted_event_is_detected_by_inventory_and_index(self):
        with Session.open(self.root) as session:
            session.publish(self.reserve(session))
            (self.root / "events" / "00000000000000000002.json").unlink()
            with self.assertRaisesRegex(SessionError, "event missing"):
                session.inspect()

    def test_altered_event_hash_chain_is_detected(self):
        with Session.open(self.root) as session:
            session.publish(self.reserve(session))
            first = self.root / "events" / "00000000000000000001.json"
            import json
            event = json.loads(first.read_text())
            event["payload"]["pair_index"] = 1
            first.write_bytes(canonical_bytes(event))
            with self.assertRaisesRegex(SessionError, "hash chain mismatch"):
                session.inspect()

    def test_torn_journal_is_archived_before_recovery_without_losing_checkpoint(self):
        with Session.open(self.root) as session:
            attempt = self.reserve(session)
            request = attempt["requests"][0]
            session.checkpoint(attempt["attempt_id"], request, request["completed_ns"])
            index = self.root / "journal.jsonl"
            index.write_bytes(index.read_bytes() + b'{"schema_version":')
            damaged = index.read_bytes()
            inventory = session.inspect()
            self.assertTrue(inventory["journal_torn_tail"])
            self.assertEqual(inventory["unresolved_attempts"][0]["observed_requests"], 1)
            with self.assertRaisesRegex(SessionError, "recover the journal"):
                session.publish(attempt)
            archive = session.recover_journal()
            self.assertEqual(archive.read_bytes(), damaged)
            self.assertFalse(session.inspect()["journal_recovery_required"])
            session.publish(attempt)

    def test_missing_index_suffix_replays_authoritative_events(self):
        with Session.open(self.root) as session:
            session.publish(self.reserve(session))
            index = self.root / "journal.jsonl"
            index.write_bytes(index.read_bytes().splitlines(keepends=True)[0])
            inventory = session.inspect()
            self.assertTrue(inventory["journal_recovery_required"])
            self.assertEqual(len(inventory["attempts"]), 1)
            session.recover_journal()
            self.assertTrue(session.inspect()["inventory_complete"])

    def test_failed_index_append_keeps_authoritative_checkpoint_for_recovery(self):
        with Session.open(self.root) as session:
            attempt = self.reserve(session)
            request = attempt["requests"][0]
            with patch("lean_model_lab.session.append_event", side_effect=OSError("injected index write failure")):
                with self.assertRaises(OSError):
                    session.checkpoint(attempt["attempt_id"], request, request["completed_ns"])
            inventory = session.inspect()
            self.assertTrue(inventory["journal_recovery_required"])
            self.assertEqual(inventory["unresolved_attempts"][0]["observed_requests"], 1)
            session.recover_journal()
            session.publish(attempt)

    def test_corrupt_complete_journal_line_is_never_a_torn_tail(self):
        with Session.open(self.root) as session:
            self.reserve(session)
            index = self.root / "journal.jsonl"
            index.write_bytes(index.read_bytes() + b'{broken}\n')
            with self.assertRaisesRegex(SessionError, "corrupt journal"):
                session.inspect()
            with self.assertRaisesRegex(SessionError, "corrupt journal"):
                session.recover_journal()

    def test_crash_between_artifact_and_terminal_has_explicit_publication_recovery(self):
        with Session.open(self.root) as session:
            attempt = self.reserve(session)
            path = self.root / "attempts" / (attempt["attempt_id"] + ".json")
            write_json_new(path, attempt)
            inventory = session.inspect()
            self.assertEqual(inventory["attempts"], [])
            self.assertEqual(inventory["unresolved_attempts"][0]["state"], "PENDING_PUBLICATION")
            self.assertEqual(inventory["unresolved_attempts"][0]["pending_attempt"], attempt)
            self.assertEqual(session.publish(attempt), path)
            self.assertTrue(session.inspect()["inventory_complete"])

    def test_setup_absence_is_unknown_and_failure_costs_are_retained(self):
        with Session.open(self.root) as session:
            before = session.inspect()["setup_accounting"]
            self.assertEqual(before["status"], "UNAVAILABLE")
            self.assertIsNone(before["full_wall_ns"])
            session.record_setup({"phase": "source-acquisition", "status": "FAILED", "started_ns": 10,
                                  "finished_ns": 30, "bytes_acquired": 4, "details": "setup/failed.json"})
            session.record_setup({"phase": "source-acquisition", "status": "COMPLETED", "started_ns": 40,
                                  "finished_ns": 90, "bytes_acquired": 100, "details": "setup/retry.json"})
            after = session.inspect()["setup_accounting"]
            self.assertEqual(after["failed_records"], 1)
            self.assertEqual(after["full_wall_ns"], 70)
            self.assertEqual(after["elapsed_span_ns"], 80)
            self.assertEqual(after["bytes_acquired_known"], 104)
            self.assertEqual(after["record_count"], 2)

    def test_setup_overlap_nonfinite_or_unknown_fields_are_rejected(self):
        with Session.open(self.root) as session:
            record = {"phase": "build", "status": "FAILED", "started_ns": 10, "finished_ns": 30,
                      "bytes_acquired": None, "details": "setup/build.json"}
            session.record_setup(record)
            with self.assertRaisesRegex(SessionError, "overlap"):
                session.record_setup(record)
            for field, value in (("started_ns", float("nan")), ("bytes_acquired", -1), ("extra", True)):
                changed = {**record, field: value}
                with self.assertRaises(SessionError):
                    session.record_setup(changed)

    def test_public_setup_validation_requires_explicit_list(self):
        self.assertEqual(validate_setup_records([]), [])
        with self.assertRaises(SessionError):
            validate_setup_records(None)

    def test_sidecar_mutation_is_detected(self):
        with Session.open(self.root) as session:
            changed = copy.deepcopy(CONFIG)
            changed["hardware"]["cpu"] = "other"
            (self.root / "config.json").write_bytes(canonical_bytes(changed))
            with self.assertRaisesRegex(SessionError, "sidecar identity changed"):
                session.inspect()

    def test_parallel_checkpoints_keep_one_durable_sequence(self):
        with Session.open(self.root) as session:
            attempt = self.reserve(session, concurrency=4)
            with ThreadPoolExecutor(max_workers=4) as pool:
                futures = [pool.submit(session.checkpoint, attempt["attempt_id"], request, request["completed_ns"])
                           for request in attempt["requests"]]
                for future in futures:
                    future.result()
            session.publish(attempt)
            self.assertEqual(session.inspect()["event_count"], 130)

    def test_mutating_callers_request_does_not_rewrite_cached_checkpoint(self):
        with Session.open(self.root) as session:
            attempt = self.reserve(session)
            request = copy.deepcopy(attempt["requests"][0])
            session.checkpoint(attempt["attempt_id"], request, request["completed_ns"])
            request["output_text"] = "changed"
            session.publish(attempt)
            self.assertTrue(session.inspect()["inventory_complete"])


if __name__ == "__main__":
    unittest.main()
