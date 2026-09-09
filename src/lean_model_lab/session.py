"""Exclusive local study inventory with immutable events and explicit recovery.

The numbered, hash-linked event files are authoritative. ``journal.jsonl`` is a
durable index whose torn or missing suffix can be rebuilt without losing events.
Hashes detect accidental mutation; they are not authentication against an actor
who rewrites this entire directory or deletes every copy of a trailing event.
"""
from __future__ import annotations

import fcntl
import copy
import os
import re
import threading
import uuid
from pathlib import Path
from typing import Any

from .artifacts import append_event, read_journal, write_json_new, write_new
from .config import validate_config
from .contracts import canonical_bytes, digest, file_digest, read_json, validate_workload
from .evidence import REQUEST_KEYS, validate_attempt

_MAX_INT = 2**63 - 1
_SETUP_KEYS = {"phase", "status", "started_ns", "finished_ns", "bytes_acquired", "details"}
_RESERVATION_KEYS = {"attempt_id", "arm", "concurrency", "pair_index", "started_ns"}


class SessionError(ValueError):
    """A study inventory is inconsistent or an explicit recovery step is required."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SessionError(message)


def _keys(value: Any, expected: set | frozenset, label: str) -> None:
    _require(type(value) is dict and set(value) == expected, f"invalid {label} fields")


def _integer(value: Any, label: str, minimum: int = 0, maximum: int = _MAX_INT) -> None:
    _require(type(value) is int and minimum <= value <= maximum, f"invalid {label} integer")


def _identifier(value: Any) -> None:
    _require(type(value) is str and re.fullmatch(r"attempt-[0-9a-f]{32}", value) is not None,
             "invalid attempt identifier")


def _setup(record: Any) -> None:
    _keys(record, _SETUP_KEYS, "setup record")
    for field in ("phase", "details"):
        _require(type(record[field]) is str and bool(record[field].strip()), f"invalid setup {field}")
    _require(record["status"] in ("COMPLETED", "FAILED", "INTERRUPTED"), "invalid setup status")
    _integer(record["started_ns"], "setup started_ns")
    _integer(record["finished_ns"], "setup finished_ns")
    _require(record["finished_ns"] >= record["started_ns"], "setup clock order is inverted")
    if record["bytes_acquired"] is not None:
        _integer(record["bytes_acquired"], "setup bytes_acquired")


def _setup_accounting(records: list[dict]) -> dict:
    for record in records:
        _setup(record)
    ordered = sorted(records, key=lambda record: record["started_ns"])
    _require(all(a["finished_ns"] <= b["started_ns"] for a, b in zip(ordered, ordered[1:])),
             "setup intervals overlap; disjoint phase accounting is required")
    known_bytes = [record["bytes_acquired"] for record in records if record["bytes_acquired"] is not None]
    return {"status": "RECORDED" if records else "UNAVAILABLE", "records": records,
            "record_count": len(records),
            "full_wall_ns": sum(record["finished_ns"] - record["started_ns"] for record in records) if records else None,
            "elapsed_span_ns": ordered[-1]["finished_ns"] - ordered[0]["started_ns"] if ordered else None,
            "bytes_acquired_known": sum(known_bytes) if known_bytes else None,
            "bytes_acquired_unknown_records": sum(record["bytes_acquired"] is None for record in records),
            "failed_records": sum(record["status"] == "FAILED" for record in records),
            "interrupted_records": sum(record["status"] == "INTERRUPTED" for record in records),
            "scope": "Only supplied setup phases; an empty ledger does not mean zero setup cost."}


def validate_setup_records(records: Any) -> list[dict]:
    """Validate the supplied setup ledger; required acquisition phases are an admission policy."""
    _require(type(records) is list, "setup_records must be an explicit list")
    _setup_accounting(records)
    return records


class Session:
    """Use ``with Session.open(root) as session`` to hold the one-writer lease.

    ``create`` returns an unopened descriptor and refuses an existing directory.
    ``publish`` reconciles an identical crash-written file lacking its terminal
    event, but refuses a second terminal publication or any replacement bytes.
    """

    def __init__(self, root: Path | str):
        self.root = Path(root).absolute()
        self._lock_file = None
        self._mutex = threading.RLock()
        self._snapshot_cache = None
        self._inventory_cache = None

    @classmethod
    def create(cls, root: Path | str, config: dict, workload: dict,
               setup_records: list[dict]) -> "Session":
        validate_config(config)
        validate_workload(workload)
        _require(config["workload_sha256"] == digest(workload), "configuration/workload identity mismatch")
        validate_setup_records(setup_records)
        root = Path(root).absolute()
        root.mkdir(parents=True, exist_ok=False)
        for name in ("events", "attempts", "raw", "recovery"):
            (root / name).mkdir()
        write_json_new(root / "config.json", config)
        write_json_new(root / "workload.json", workload)
        write_json_new(root / "setup.json", setup_records)
        write_json_new(root / "session.json", {"schema_version": 1, "session_id": uuid.uuid4().hex,
                       "config_sha256": digest(config), "workload_sha256": digest(workload),
                       "setup_sha256": digest(setup_records)})
        write_new(root / "journal.jsonl", b"")
        write_new(root / ".lock", b"")
        return cls(root)

    @classmethod
    def open(cls, root: Path | str) -> "Session":
        return cls(root)

    def __enter__(self) -> "Session":
        with self._mutex:
            _require(self._lock_file is None, "session lease is already held by this object")
            _require(self.root.is_dir() and not self.root.is_symlink(), "session directory is missing or symlinked")
            path = self.root / ".lock"
            _require(path.is_file() and not path.is_symlink(), "session lock is missing or symlinked")
            handle = path.open("r+b")
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                handle.close()
                raise SessionError("another writer holds the session lock") from exc
            self._lock_file = handle
            try:
                self.inspect()
            except BaseException:
                self.close()
                raise
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        with self._mutex:
            if self._lock_file is not None:
                fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_UN)
                self._lock_file.close()
                self._lock_file = None
                self._snapshot_cache = None
                self._inventory_cache = None

    def _locked(self) -> None:
        _require(self._lock_file is not None, "operation requires `with Session.open(root)`")

    def _read_file(self, path: Path) -> Any:
        _require(path.is_file() and not path.is_symlink(), f"required regular file missing: {path.name}")
        try:
            return read_json(path)
        except (ValueError, OSError) as exc:
            raise SessionError(f"invalid {path.name}: {exc}") from exc

    def _snapshot(self) -> dict:
        self._locked()
        for name in ("events", "attempts", "raw", "recovery"):
            path = self.root / name
            _require(path.is_dir() and not path.is_symlink(), f"session {name} directory missing or symlinked")
        manifest = self._read_file(self.root / "session.json")
        _keys(manifest, {"schema_version", "session_id", "config_sha256", "workload_sha256", "setup_sha256"}, "session manifest")
        _integer(manifest["schema_version"], "session schema_version", 1, 1)
        _require(type(manifest["session_id"]) is str and re.fullmatch(r"[0-9a-f]{32}", manifest["session_id"]) is not None,
                 "invalid session ID")
        config = self._read_file(self.root / "config.json")
        workload = self._read_file(self.root / "workload.json")
        setup_records = self._read_file(self.root / "setup.json")
        validate_config(config)
        validate_workload(workload)
        _require(type(setup_records) is list, "setup sidecar must be a list")
        for name, document in (("config", config), ("workload", workload), ("setup", setup_records)):
            _require(digest(document) == manifest[f"{name}_sha256"], f"{name} sidecar identity changed")
        _require(config["workload_sha256"] == manifest["workload_sha256"], "configuration/workload identity mismatch")
        events = []
        previous = digest(manifest)
        for sequence, path in enumerate(sorted((self.root / "events").iterdir()), start=1):
            _require(path.name == f"{sequence:020d}.json", "immutable event inventory has a gap or foreign file")
            event = self._read_file(path)
            _keys(event, {"schema_version", "sequence", "previous_sha256", "kind", "payload"}, "event")
            _integer(event["schema_version"], "event schema_version", 1, 1)
            _integer(event["sequence"], "event sequence", sequence, sequence)
            _require(event["previous_sha256"] == previous, "immutable event hash chain mismatch")
            previous = digest(event)
            events.append(event)
        journal_path = self.root / "journal.jsonl"
        _require(journal_path.is_file() and not journal_path.is_symlink(), "journal index is missing or symlinked")
        try:
            index, torn = read_journal(journal_path)
        except (ValueError, OSError) as exc:
            raise SessionError(f"corrupt journal index: {exc}") from exc
        _require(len(index) <= len(events), "journal contains an event missing from immutable inventory")
        _require(all(canonical_bytes(a) == canonical_bytes(b) for a, b in zip(index, events)),
                 "journal differs from immutable event inventory")
        snapshot = {"manifest": manifest, "config": config, "workload": workload, "setup_records": setup_records,
                "events": events, "journal_recovery_required": torn or len(index) != len(events),
                "journal_torn_tail": torn, "journal_indexed_events": len(index)}
        self._snapshot_cache = snapshot
        return snapshot

    def _checkpoint(self, reservation: dict, request: Any, observed_ns: Any, workload: dict) -> None:
        _keys(request, REQUEST_KEYS, "checkpoint request")
        _require(type(request["request_id"]) is str and request["request_id"] in
                 {row["request_id"] for row in workload["requests"]}, "checkpoint request identity is foreign")
        _integer(observed_ns, "checkpoint observed_ns")
        _integer(request["completed_ns"], "checkpoint completed_ns")
        _require(reservation["started_ns"] <= request["completed_ns"] <= observed_ns,
                 "checkpoint observation precedes completion or reservation")
        _require(request["status"] in (("SUCCEEDED", "FAILED", "CANCELLED", "REJECTED", "EXPIRED") if workload["schema_version"] in (2,3) else ("SUCCEEDED", "FAILED", "CANCELLED")), "checkpoint must be terminal")
        # Checkpoint payloads must be finite JSON. Full request/timing reconciliation
        # is repeated against the final normalized attempt before publication.
        canonical_bytes(request)

    def _raw_inventory(self, attempt_id: str) -> list[dict]:
        root = self.root / "raw" / attempt_id
        _require(root.is_dir() and not root.is_symlink(), "published raw attempt directory is missing or symlinked")
        records = []
        for path in sorted(root.rglob("*")):
            _require(not path.is_symlink(), "raw evidence contains a symlink")
            if path.is_dir():
                continue
            _require(path.is_file(), "raw evidence contains a nonregular file")
            before = path.stat()
            checksum = file_digest(path)
            after = path.stat()
            _require((before.st_ino, before.st_size, before.st_mtime_ns) ==
                     (after.st_ino, after.st_size, after.st_mtime_ns), "raw evidence changed during hashing")
            records.append({"path": path.relative_to(root).as_posix(), "size_bytes": after.st_size, "sha256": checksum})
        return records

    def inspect(self) -> dict:
        """Read every reservation, checkpoint and terminal; never infer orphan timing."""
        with self._mutex:
            self._inventory_cache = None
            self._snapshot_cache = None
            snapshot = self._snapshot()
            reservations = {}
            checkpoints = {}
            terminals = {}
            setup_records = list(snapshot["setup_records"])
            for event in snapshot["events"]:
                payload = event["payload"]
                kind = event["kind"]
                if kind == "reserved":
                    _keys(payload, _RESERVATION_KEYS, "reservation")
                    _identifier(payload["attempt_id"])
                    identifier = payload["attempt_id"]
                    _require(identifier not in reservations, "duplicate reservation")
                    _require(payload["arm"] in ("baseline", "candidate"), "invalid reservation arm")
                    _integer(payload["concurrency"], "reservation concurrency", 1, max(snapshot["config"]["evaluation"]["concurrency_modes"]))
                    _require(payload["concurrency"] in snapshot["config"]["evaluation"]["concurrency_modes"], "invalid reservation concurrency")
                    _integer(payload["pair_index"], "reservation pair_index", 0, snapshot["config"]["evaluation"]["pairs_per_concurrency"]-1)
                    _integer(payload["started_ns"], "reservation started_ns")
                    reservations[identifier] = payload
                    checkpoints[identifier] = []
                elif kind == "checkpoint":
                    _keys(payload, {"attempt_id", "request", "observed_ns"}, "checkpoint")
                    _identifier(payload["attempt_id"])
                    identifier = payload["attempt_id"]
                    _require(identifier in reservations and identifier not in terminals,
                             "checkpoint has no open reservation")
                    self._checkpoint(reservations[identifier], payload["request"], payload["observed_ns"], snapshot["workload"])
                    _require(payload["request"]["request_id"] not in {row["request"]["request_id"] for row in checkpoints[identifier]},
                             "duplicate checkpoint request")
                    checkpoints[identifier].append(payload)
                elif kind == "terminal":
                    _keys(payload, {"attempt_id", "attempt_sha256", "raw_files"}, "terminal")
                    _identifier(payload["attempt_id"])
                    identifier = payload["attempt_id"]
                    _require(identifier in reservations and identifier not in terminals, "duplicate or unreserved terminal")
                    terminals[identifier] = payload
                elif kind == "setup":
                    _setup(payload)
                    setup_records.append(payload)
                else:
                    raise SessionError("unknown immutable event kind")
            raw_paths = list((self.root / "raw").iterdir())
            _require(all(path.name in reservations and path.is_dir() and not path.is_symlink() for path in raw_paths),
                     "raw directory contains a foreign or symlinked attempt")
            disk_attempts = {}
            for path in (self.root / "attempts").iterdir():
                _require(path.suffix == ".json", "foreign attempt artifact")
                identifier = path.stem
                _identifier(identifier)
                _require(identifier in reservations, "attempt artifact has no reservation")
                attempt = self._read_file(path)
                self._validate_publication(attempt, reservations[identifier], checkpoints[identifier], snapshot)
                disk_attempts[identifier] = attempt
                if identifier in terminals:
                    _require(digest(attempt) == terminals[identifier]["attempt_sha256"], "published attempt bytes changed")
                    _require(canonical_bytes(self._raw_inventory(identifier)) == canonical_bytes(terminals[identifier]["raw_files"]),
                             "published raw artifact inventory changed: missing, extra or modified file")
            _require(set(terminals) <= set(disk_attempts), "published attempt artifact is missing")
            attempts = [disk_attempts[identifier] for identifier in reservations if identifier in terminals]
            unresolved = []
            for identifier, reservation in reservations.items():
                if identifier in terminals:
                    continue
                retained = checkpoints[identifier]
                observed_until = max((row["observed_ns"] for row in retained), default=None)
                unresolved.append({**reservation, "state": "PENDING_PUBLICATION" if identifier in disk_attempts else "UNFINISHED",
                                   "checkpoints": retained, "observed_until_ns": observed_until,
                                   "known_observed_wall_ns_lower_bound": observed_until - reservation["started_ns"] if observed_until is not None else None,
                                   "observed_requests": len(retained), "unaccounted_request_ids": sorted(
                                       {row["request_id"] for row in snapshot["workload"]["requests"]} -
                                       {row["request"]["request_id"] for row in retained}),
                                   "pending_attempt": disk_attempts.get(identifier),
                                   "limitation": "Final duration and unfinished work are unknown until explicitly reconciled; no continuation or retry has occurred."})
            result = {"session_id": snapshot["manifest"]["session_id"], "config": snapshot["config"], "workload": snapshot["workload"],
                    "config_sha256": snapshot["manifest"]["config_sha256"], "workload_sha256": snapshot["manifest"]["workload_sha256"],
                    "attempts": attempts, "reservation_count": len(reservations), "unresolved_attempts": unresolved,
                    "setup_accounting": _setup_accounting(setup_records),
                    "journal_recovery_required": snapshot["journal_recovery_required"],
                    "journal_torn_tail": snapshot["journal_torn_tail"], "event_count": len(snapshot["events"]),
                    "inventory_complete": not unresolved and not snapshot["journal_recovery_required"],
                    "integrity_limit": "Local hashes do not authenticate evidence or prove no complete trailing inventory was deleted."}
            self._inventory_cache = copy.deepcopy(result)
            return copy.deepcopy(result)

    def _validate_publication(self, attempt: Any, reservation: dict, checkpoints: list[dict], snapshot: dict) -> None:
        validate_attempt(attempt, snapshot["workload"], config_sha256=snapshot["manifest"]["config_sha256"],
                         workload_sha256=snapshot["manifest"]["workload_sha256"],config=snapshot["config"])
        _require(attempt["evidence_class"] == snapshot["config"]["evidence_class"], "attempt evidence class differs from session")
        for field in _RESERVATION_KEYS:
            _require(attempt[field] == reservation[field], f"attempt {field} differs from reservation")
        requests = {row["request_id"]: row for row in attempt["requests"]}
        for checkpoint in checkpoints:
            request = checkpoint["request"]
            _require(request["request_id"] in requests and canonical_bytes(requests[request["request_id"]]) == canonical_bytes(request),
                     "published attempt omits or changes a durable checkpoint")
            _require(checkpoint["observed_ns"] <= attempt["finished_ns"], "attempt full wall excludes durable checkpoint observation")

    def _append(self, kind: str, payload: dict) -> None:
        # The exclusive lease permits using our own last reconciled state between
        # checkpoints. Public inspect and terminal publication always reread disk.
        snapshot = self._snapshot_cache if self._snapshot_cache is not None else self._snapshot()
        _require(not snapshot["journal_recovery_required"], "recover the journal index before writing")
        event = {"schema_version": 1, "sequence": len(snapshot["events"]) + 1,
                 "previous_sha256": digest(snapshot["events"][-1]) if snapshot["events"] else digest(snapshot["manifest"]),
                 "kind": kind, "payload": copy.deepcopy(payload)}
        try:
            write_json_new(self.root / "events" / f"{event['sequence']:020d}.json", event)
            append_event(self.root / "journal.jsonl", event)
        except BaseException:
            self._snapshot_cache = None
            self._inventory_cache = None
            raise
        snapshot["events"].append(event)
        snapshot["journal_indexed_events"] = len(snapshot["events"])

    def reserve(self, arm: str, concurrency: int, pair_index: int, started_ns: int) -> dict:
        with self._mutex:
            inventory = self.inspect()
            _require(not inventory["unresolved_attempts"], "reconcile unfinished attempts before reserving another")
            _require(arm in ("baseline", "candidate"), "invalid reservation arm")
            _integer(concurrency, "concurrency", 1, max(inventory["config"]["evaluation"]["concurrency_modes"]))
            _require(concurrency in inventory["config"]["evaluation"]["concurrency_modes"], "invalid concurrency")
            _integer(pair_index, "pair_index", 0, inventory["config"]["evaluation"]["pairs_per_concurrency"]-1)
            _integer(started_ns, "started_ns")
            _require(all(attempt["finished_ns"] <= started_ns for attempt in inventory["attempts"]),
                     "reservation overlaps a prior terminal attempt")
            identifier = "attempt-" + uuid.uuid4().hex
            self._append("reserved", {"attempt_id": identifier, "arm": arm, "concurrency": concurrency,
                                      "pair_index": pair_index, "started_ns": started_ns})
            raw_dir = self.root / "raw" / identifier
            raw_dir.mkdir()
            self.inspect()
            return {"attempt_id": identifier, "raw_dir": raw_dir}

    def checkpoint(self, attempt_id: str, request: dict, observed_ns: int) -> None:
        with self._mutex:
            self._locked()
            inventory = self._inventory_cache if self._inventory_cache is not None else self.inspect()
            _identifier(attempt_id)
            reservation = next((row for row in inventory["unresolved_attempts"] if row["attempt_id"] == attempt_id), None)
            _require(reservation is not None and reservation["state"] == "UNFINISHED", "checkpoint has no unfinished reservation")
            self._checkpoint(reservation, request, observed_ns, inventory["workload"])
            _require(request["request_id"] not in {row["request"]["request_id"] for row in reservation["checkpoints"]},
                     "duplicate checkpoint request")
            self._append("checkpoint", {"attempt_id": attempt_id, "request": request, "observed_ns": observed_ns})
            reservation["checkpoints"].append({"attempt_id": attempt_id, "request": copy.deepcopy(request), "observed_ns": observed_ns})
            reservation["observed_requests"] += 1
            reservation["observed_until_ns"] = max(reservation["observed_until_ns"] or 0, observed_ns)
            reservation["known_observed_wall_ns_lower_bound"] = reservation["observed_until_ns"] - reservation["started_ns"]
            reservation["unaccounted_request_ids"].remove(request["request_id"])
            inventory["event_count"] += 1

    def publish(self, attempt: dict) -> Path:
        with self._mutex:
            inventory = self.inspect()
            _require(type(attempt) is dict, "attempt must be an object")
            _identifier(attempt.get("attempt_id"))
            identifier = attempt["attempt_id"]
            reservation = next((row for row in inventory["unresolved_attempts"] if row["attempt_id"] == identifier), None)
            _require(reservation is not None, "attempt is unreserved or already published")
            _require(not inventory["journal_recovery_required"], "recover the journal index before writing")
            self._validate_publication(attempt, reservation, reservation["checkpoints"], self._snapshot())
            raw_files = self._raw_inventory(identifier)
            path = self.root / "attempts" / f"{identifier}.json"
            if path.exists():
                _require(canonical_bytes(self._read_file(path)) == canonical_bytes(attempt), "cannot replace crash-written attempt")
            else:
                write_json_new(path, attempt)
            self._append("terminal", {"attempt_id": identifier, "attempt_sha256": digest(attempt), "raw_files": raw_files})
            self.inspect()
            return path

    def record_setup(self, record: dict) -> None:
        with self._mutex:
            inventory = self.inspect()
            _setup_accounting(inventory["setup_accounting"]["records"] + [record])
            self._append("setup", record)
            self.inspect()

    def recover_journal(self) -> Path | None:
        """Archive the damaged index verbatim, then regenerate from immutable events."""
        with self._mutex:
            self.inspect()  # Reconcile semantics and artifacts before touching the index.
            snapshot = self._snapshot()
            if not snapshot["journal_recovery_required"]:
                return None
            path = self.root / "journal.jsonl"
            backup = self.root / "recovery" / f"journal-{uuid.uuid4().hex}.jsonl"
            write_new(backup, path.read_bytes())
            replacement = self.root / "recovery" / f"rebuilt-{uuid.uuid4().hex}.jsonl"
            write_new(replacement, b"".join(canonical_bytes(event) + b"\n" for event in snapshot["events"]))
            os.replace(replacement, path)
            directory = os.open(self.root, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
            self.inspect()
            return backup
