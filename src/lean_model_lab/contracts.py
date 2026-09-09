"""Immutable workload contracts. No backend, network access or inference here."""
from __future__ import annotations

import hashlib
import json
import random
import string
from pathlib import Path
from typing import Any

SEED = 20260907
STRATA = (16, 64, 128, 256)
QUALITY = {
    "rule": "exact_key_after_outer_whitespace_strip",
    "minimum_accuracy": 0.95,
    "require_token_parity": True,
    "reject_length_limit": True,
}


class ContractError(ValueError):
    """An input violates the frozen comparison contract."""


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ContractError(f"not finite JSON: {exc}") from exc


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_digest(path: Path, *, check=None) -> str:
    if check is not None: check()
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            if check is not None: check()
            chunk = stream.read(1024 * 1024)
            if not chunk: break
            h.update(chunk)
    if check is not None: check()
    return h.hexdigest()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json(text: str | bytes) -> Any:
    def reject_constant(value: str):
        raise ContractError(f"non-finite JSON number: {value}")
    try:
        return json.loads(text, object_pairs_hook=_unique_object, parse_constant=reject_constant)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"invalid JSON: {exc}") from exc


def read_json(path: Path, *, max_bytes: int = 64 * 1024 * 1024) -> Any:
    if path.stat().st_size > max_bytes:
        raise ContractError(f"JSON exceeds {max_bytes} bytes")
    return parse_json(path.read_bytes())


def keys(value: Any, expected: set[str], label: str) -> None:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    if set(value) != expected:
        raise ContractError(f"{label} fields differ: missing={sorted(expected-set(value))}, "
                            f"unknown={sorted(set(value)-expected)}")


def integer(value: Any, minimum: int, maximum: int, label: str) -> None:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ContractError(f"{label} must be an integer in [{minimum}, {maximum}]")


def make_workload() -> dict:
    rng = random.Random(SEED)
    vocabulary = ("river", "stone", "cloud", "field", "tree", "path", "light", "water")
    filler = {size: " ".join(vocabulary[i % len(vocabulary)] for i in range(size))
              for size in STRATA}
    requests = []
    for index in range(128):
        size = STRATA[index % 4]
        answer = "".join(rng.choice(string.ascii_uppercase) for _ in range(5))
        prompt = ("Read the record below. Reply with the value of KEY only, without explanation.\n"
                  f"FILLER: {filler[size]}\nKEY: {answer}\nAnswer:")
        requests.append({"request_id": f"r{index:03d}", "stratum": size,
                         "prompt": prompt, "expected": answer, "arrival_offset_ns": 0})
    return {"schema_version": 1, "workload_id": "synthetic-key-copy-v1",
            "generator_seed": SEED, "stratum_unit": "filler_words",
            "concurrency_modes": [1, 4], "max_output_tokens": 32,
            "sampling": {"temperature": 0, "seed": SEED, "stop": [], "allow_eos": True},
            "arrival_mode": "finite_batch_all_at_zero", "quality": dict(QUALITY),
            "requests": requests}


def validate_workload(value: Any) -> dict:
    if type(value) is dict and type(value.get('schema_version')) is int and value['schema_version'] == 3:
        from .structured_workloads import validate_workload_v3
        return validate_workload_v3(value)
    if type(value) is dict and type(value.get("schema_version")) is int and value["schema_version"] == 2:
        from .workloads import validate_workload_v2
        return validate_workload_v2(value)
    expected = make_workload()
    keys(value, set(expected), "workload")
    integer(value["schema_version"], 1, 1, "schema_version")
    if not isinstance(value["requests"], list) or len(value["requests"]) != 128:
        raise ContractError("workload requires exactly 128 requests")
    for index, request in enumerate(value["requests"]):
        keys(request, {"request_id", "stratum", "prompt", "expected", "arrival_offset_ns"},
             f"requests[{index}]")
        integer(request["stratum"], 1, 256, "stratum")
        integer(request["arrival_offset_ns"], 0, 0, "arrival_offset_ns")
    # The shipped population and all quality/arrival/stop fields are immutable.
    # JSON type identity matters (True must not compare equal to 1).
    if canonical_bytes(value) != canonical_bytes(expected):
        raise ContractError("workload differs from frozen synthetic-key-copy-v1; "
                            "create a reviewed new contract, never mutate this comparison")
    return value
