#!/usr/bin/env python3
"""Validate Lean Model Lab's dependency and documentation contract.

This standard-library check validates planning artifacts only. It runs no model,
downloads nothing, and makes no scientific or runtime claim.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
FOUNDATION_IDS = ["LM-F01", "LM-F02", "LM-F03"]
ORIGINAL_IDS = [f"LM-{number:03d}" for number in range(1, 25)]
CORE_IDS = set(FOUNDATION_IDS + ORIGINAL_IDS)
ALLOWED_STATUSES = {
    "PLANNED",
    "IN_PROGRESS",
    "READY_FOR_REVIEW",
    "IMPLEMENTED",
    "AUTOMATED_PASS",
    "RUNTIME_VERIFIED",
    "USER_VALIDATED",
    "RELEASE_VERIFIED",
    "DONE",
    "BLOCKED",
    "FAILED",
    "NOT_TESTED",
}
FOUNDATION_STATES = {"PLANNED", "IN_PROGRESS", "READY_FOR_REVIEW", "DONE", "BLOCKED"}
REQUIRED_ARCHITECTURE_TERMS = [
    "ModelRecord",
    "DataRecord",
    "TokenizerRecord",
    "WorkloadSpec",
    "HardwareRecord",
    "RuntimeRecord",
    "time to first token (TTFT)",
    "inter-token latency (ITL)",
    "BUDGET_EXHAUSTED",
    "OS sandbox, container or VM",
]
REQUIRED_SOURCE_URLS = [
    "github.com/mlcommons/training_policies",
    "github.com/mlcommons/inference",
    "docs.vllm.ai",
    "usenix.org/system/files/osdi24-zhong-yinmin.pdf",
    "docs.nvidia.com/cuda/cuda-runtime-api",
    "docs.nvidia.com/deploy/nvml-api",
    "developer.apple.com/metal/pytorch",
    "arxiv.org/abs/2203.15556",
    "github.com/opencontainers/runtime-spec",
    "csrc.nist.gov/pubs/sp/800/190/final",
]
TASK_HEADING = re.compile(r"^## (?P<id>LM-[A-Z0-9-]+) — (?P<title>.+)$", re.MULTILINE)


def read_text(root: Path, name: str, errors: list[str]) -> str:
    path = root / name
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read {name}: {exc}")
        return ""


def normalize_status(value: str) -> str:
    return re.sub(r"\s+", "_", value.strip().upper())


def parse_task_projection(text: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    """Parse machine-comparable task fields from TASKS.md blocks."""

    matches = list(TASK_HEADING.finditer(text))
    projection: dict[str, dict[str, Any]] = {}
    for index, match in enumerate(matches):
        task_id = match.group("id")
        if task_id in projection:
            errors.append(f"TASKS.md duplicate task heading: {task_id}")
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end() : end]

        wave_line = re.search(
            r"^- Wave: (?P<wave>[^;]+); status: \*\*(?P<status>[^*]+)\*\*; owner: .+$",
            body,
            re.MULTILINE,
        )
        dependency_line = re.search(r"^- Dependencies: (?P<value>.+)\.$", body, re.MULTILINE)
        owned_line = re.search(r"^- Owned scope: (?P<value>.+)\.$", body, re.MULTILINE)
        acceptance_line = re.search(r"^- Acceptance: (?P<value>.+)$", body, re.MULTILINE)

        missing = []
        if wave_line is None:
            missing.append("wave/status/owner")
        if dependency_line is None:
            missing.append("dependencies")
        if owned_line is None:
            missing.append("owned scope")
        if acceptance_line is None:
            missing.append("acceptance")
        if missing:
            errors.append(f"TASKS.md {task_id} missing fields: {', '.join(missing)}")
            continue

        assert wave_line is not None
        assert dependency_line is not None
        assert owned_line is not None
        assert acceptance_line is not None

        wave_text = wave_line.group("wave").strip()
        wave = int(wave_text) if re.fullmatch(r"\d+", wave_text) else wave_text
        dependency_text = dependency_line.group("value").strip()
        dependencies = (
            []
            if dependency_text.lower() == "none"
            else [item.strip() for item in dependency_text.split(",") if item.strip()]
        )
        owned_paths = re.findall(r"`([^`]+)`", owned_line.group("value"))
        projection[task_id] = {
            "id": task_id,
            "title": match.group("title").strip(),
            "wave": wave,
            "status": normalize_status(wave_line.group("status")),
            "dependsOn": dependencies,
            "ownedPaths": owned_paths,
            "acceptance": acceptance_line.group("value").strip(),
        }
    return projection


def validate_dag(tasks: list[dict[str, Any]], errors: list[str]) -> None:
    by_id = {
        task["id"]: task
        for task in tasks
        if isinstance(task.get("id"), str) and task["id"]
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str, trail: list[str]) -> None:
        if task_id in visited:
            return
        if task_id in visiting:
            errors.append("dependency cycle: " + " -> ".join(trail + [task_id]))
            return
        visiting.add(task_id)
        dependencies = by_id[task_id].get("dependsOn", [])
        if not isinstance(dependencies, list):
            dependencies = []
        for dependency in dependencies:
            if isinstance(dependency, str) and dependency in by_id:
                visit(dependency, trail + [task_id])
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in by_id:
        visit(task_id, [])


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    plan_path = root / "plan" / "tasks.json"
    try:
        plan: Any = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot load plan/tasks.json: {exc}"]

    if not isinstance(plan, dict):
        return ["plan top level must be an object"]
    if plan.get("schemaVersion") != 2 or isinstance(plan.get("schemaVersion"), bool):
        errors.append("schemaVersion must be integer 2")
    if plan.get("project") != "lean-model-lab":
        errors.append("project must be lean-model-lab")
    if plan.get("stateAuthority") != "../STATUS.md":
        errors.append("stateAuthority must remain ../STATUS.md")

    raw_tasks = plan.get("tasks")
    if not isinstance(raw_tasks, list) or not raw_tasks:
        errors.append("tasks must be a non-empty list")
        return errors

    tasks: list[dict[str, Any]] = []
    for index, item in enumerate(raw_tasks):
        if not isinstance(item, dict):
            errors.append(f"tasks[{index}] must be an object")
        else:
            tasks.append(item)

    ids: list[str] = []
    for index, task in enumerate(tasks):
        task_id = task.get("id")
        label = task_id if isinstance(task_id, str) and task_id else f"tasks[{index}]"
        if not isinstance(task_id, str) or not task_id.strip():
            errors.append(f"tasks[{index}].id must be a non-empty string")
        else:
            ids.append(task_id)

        wave = task.get("wave")
        if isinstance(wave, bool) or not isinstance(wave, int) or wave < 0:
            errors.append(f"{label}.wave must be a non-negative integer, not boolean")
        title = task.get("title")
        if not isinstance(title, str) or not title.strip():
            errors.append(f"{label}.title must be a non-empty string")
        status = task.get("status")
        if not isinstance(status, str) or not status.strip():
            errors.append(f"{label}.status must be a non-empty string")
        elif status not in ALLOWED_STATUSES:
            errors.append(f"{label}.status is unsupported: {status}")
        acceptance = task.get("acceptance")
        if not isinstance(acceptance, str) or not acceptance.strip():
            errors.append(f"{label}.acceptance must be a non-empty string")

        dependencies = task.get("dependsOn")
        if not isinstance(dependencies, list):
            errors.append(f"{label}.dependsOn must be a list")
        else:
            for dep_index, dependency in enumerate(dependencies):
                if not isinstance(dependency, str) or not dependency.strip():
                    errors.append(f"{label}.dependsOn[{dep_index}] must be a non-empty string")
            string_dependencies = [dep for dep in dependencies if isinstance(dep, str)]
            if len(string_dependencies) != len(set(string_dependencies)):
                errors.append(f"{label}.dependsOn contains a duplicate")

        owned_paths = task.get("ownedPaths")
        if not isinstance(owned_paths, list) or not owned_paths:
            errors.append(f"{label}.ownedPaths must be a non-empty list")
        else:
            for path_index, owned_path in enumerate(owned_paths):
                if not isinstance(owned_path, str) or not owned_path.strip():
                    errors.append(f"{label}.ownedPaths[{path_index}] must be a non-empty string")

    duplicates = sorted(task_id for task_id, count in Counter(ids).items() if count > 1)
    if duplicates:
        errors.append("duplicate task IDs: " + ", ".join(duplicates))
    by_id = {
        task["id"]: task
        for task in tasks
        if isinstance(task.get("id"), str) and task["id"]
    }
    known_ids = set(by_id)
    missing_core = sorted(CORE_IDS - known_ids)
    if missing_core:
        errors.append("missing core task IDs: " + ", ".join(missing_core))

    for task_id, task in by_id.items():
        dependencies = task.get("dependsOn")
        if not isinstance(dependencies, list):
            continue
        for dependency in dependencies:
            if not isinstance(dependency, str):
                continue
            if dependency not in known_ids:
                errors.append(f"{task_id}: unknown dependency {dependency}")
                continue
            if dependency == task_id:
                errors.append(f"{task_id}: self dependency")
            task_wave = task.get("wave")
            dep_wave = by_id[dependency].get("wave")
            valid_task_wave = isinstance(task_wave, int) and not isinstance(task_wave, bool)
            valid_dep_wave = isinstance(dep_wave, int) and not isinstance(dep_wave, bool)
            if valid_task_wave and valid_dep_wave and dep_wave > task_wave:
                errors.append(f"{task_id}: depends on later-wave task {dependency}")

    expected_foundation_edges = {
        "LM-F01": [],
        "LM-F02": ["LM-F01"],
        "LM-F03": ["LM-F02"],
    }
    for task_id, expected in expected_foundation_edges.items():
        if by_id.get(task_id, {}).get("dependsOn") != expected:
            errors.append(f"{task_id}: foundation dependency changed")
    lm001_dependencies = by_id.get("LM-001", {}).get("dependsOn")
    if not isinstance(lm001_dependencies, list) or "LM-F03" not in lm001_dependencies:
        errors.append("LM-001 must remain downstream of the Wave 0 gate LM-F03")

    foundation_values = [by_id.get(task_id, {}).get("status") for task_id in FOUNDATION_IDS]
    foundation_statuses = (
        set(foundation_values) if all(isinstance(value, str) for value in foundation_values) else set()
    )
    if len(foundation_statuses) != 1 or next(iter(foundation_statuses)) not in FOUNDATION_STATES:
        errors.append(
            "foundation tasks must move together in PLANNED, IN_PROGRESS, "
            "READY_FOR_REVIEW, DONE or BLOCKED"
        )
    validate_dag(tasks, errors)

    task_doc = read_text(root, "TASKS.md", errors)
    roadmap = read_text(root, "ROADMAP.md", errors)
    status_doc = read_text(root, "STATUS.md", errors)
    architecture = read_text(root, "ARCHITECTURE.md", errors)
    experiments = read_text(root, "EXPERIMENTS.md", errors)
    sources = read_text(root, "SOURCES.md", errors)
    readme = read_text(root, "README.md", errors)

    projection_errors: list[str] = []
    projection = parse_task_projection(task_doc, projection_errors)
    errors.extend(projection_errors)
    extra_projection_ids = sorted(set(projection) - known_ids)
    if extra_projection_ids:
        errors.append("TASKS.md has tasks absent from plan: " + ", ".join(extra_projection_ids))
    for task_id, task in by_id.items():
        projected = projection.get(task_id)
        if projected is None:
            errors.append(f"TASKS.md missing task block: {task_id}")
            continue
        for field in ("title", "wave", "status", "dependsOn", "ownedPaths", "acceptance"):
            if projected[field] != task.get(field):
                errors.append(
                    f"{task_id}: TASKS {field} differs from plan "
                    f"({projected[field]!r} != {task.get(field)!r})"
                )
        if task_id not in roadmap:
            errors.append(f"ROADMAP.md does not mention {task_id}")

    declared_waves = {
        task["wave"]
        for task in tasks
        if isinstance(task.get("wave"), int) and not isinstance(task.get("wave"), bool)
    }
    for wave in sorted(declared_waves):
        if roadmap.count(f"## Wave {wave}:") != 1:
            errors.append(f"ROADMAP.md must contain exactly one Wave {wave} heading")
    original_gate = (
        "Gate decision: continue when the outcome is reproduced and reviewed at its "
        "appropriate evidence level; otherwise repair, reduce scope or hold. No later "
        "wave may weaken this gate."
    )
    if roadmap.count(original_gate) != 8:
        errors.append("ROADMAP.md must preserve all eight original wave gates verbatim")

    for term in REQUIRED_ARCHITECTURE_TERMS:
        if term not in architecture and term not in experiments:
            errors.append(f"architecture/experiment contract missing term: {term}")
    for url in REQUIRED_SOURCE_URLS:
        if url not in sources:
            errors.append(f"SOURCES.md missing primary/official source: {url}")

    required_next_packet_terms = [
        "128-request",
        "maximum 32 requested output tokens",
        "concurrency modes 1 and 4",
        "CPU is the mandatory control",
        "paid-compute budget",
        "UNAVAILABLE",
    ]
    combined_packet_docs = task_doc + experiments + status_doc
    for term in required_next_packet_terms:
        if term not in combined_packet_docs:
            errors.append(f"next-work packet missing boundary: {term}")

    foundation_state = next(iter(foundation_statuses)) if len(foundation_statuses) == 1 else None
    review_line = next(
        (
            line
            for line in status_doc.splitlines()
            if line.startswith("- Wave 0 review evidence:")
        ),
        "",
    )
    if foundation_state == "DONE":
        if not review_line or "PENDING" in review_line:
            errors.append("foundation DONE requires recorded Wave 0 review evidence in STATUS.md")
    elif foundation_state in FOUNDATION_STATES:
        if "**PENDING**" not in review_line:
            errors.append(f"foundation {foundation_state} requires pending review state in STATUS.md")
    if foundation_state in FOUNDATION_STATES:
        for task_id in FOUNDATION_IDS:
            if f"- {task_id}: **{foundation_state}**" not in status_doc:
                errors.append(f"STATUS.md must mark {task_id} {foundation_state}")

    task_count_match = re.search(r"\[(\d+) contributor tasks\]\(TASKS\.md\)", readme)
    if not task_count_match:
        errors.append("README.md must link TASKS.md with a contributor-task count")
    elif int(task_count_match.group(1)) != len(tasks):
        errors.append("README.md contributor-task count must match plan/tasks.json")

    next_packet = plan.get("nextPacket")
    if not isinstance(next_packet, dict):
        errors.append("plan nextPacket must be an object")
    elif next_packet.get("mode") != "selection-then-no-compute-harness":
        errors.append("plan nextPacket must identify selection followed by the no-compute harness")

    return errors


def copy_fixture(source: Path, destination: Path) -> None:
    (destination / "plan").mkdir(parents=True)
    for name in [
        "README.md",
        "ARCHITECTURE.md",
        "ROADMAP.md",
        "TASKS.md",
        "EXPERIMENTS.md",
        "SOURCES.md",
        "STATUS.md",
    ]:
        shutil.copy2(source / name, destination / name)
    shutil.copy2(source / "plan" / "tasks.json", destination / "plan" / "tasks.json")


def require_errors(errors: list[str], expected_fragments: list[str], case: str) -> None:
    missing = [fragment for fragment in expected_fragments if not any(fragment in error for error in errors)]
    if missing:
        raise AssertionError(f"{case}: missing expected errors {missing}; got {errors}")


def run_self_test(source: Path) -> int:
    baseline_errors = validate_repository(source)
    if baseline_errors:
        print("SELF-TEST FAIL: baseline is invalid")
        for error in baseline_errors:
            print(f"- {error}")
        return 1

    try:
        with tempfile.TemporaryDirectory(prefix="lean-model-lab-plan-") as raw:
            fixture = Path(raw)
            copy_fixture(source, fixture)
            (fixture / "plan" / "tasks.json").write_text("[]\n", encoding="utf-8")
            require_errors(
                validate_repository(fixture),
                ["plan top level must be an object"],
                "non-object top level",
            )

        with tempfile.TemporaryDirectory(prefix="lean-model-lab-plan-") as raw:
            fixture = Path(raw)
            copy_fixture(source, fixture)
            plan_path = fixture / "plan" / "tasks.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["project"] = "wrong-project"
            malformed = plan["tasks"][0]
            malformed.update(
                {
                    "id": 7,
                    "wave": True,
                    "status": [],
                    "dependsOn": [9],
                    "ownedPaths": [],
                }
            )
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            require_errors(
                validate_repository(fixture),
                [
                    ".id must be a non-empty string",
                    "project must be lean-model-lab",
                    ".wave must be a non-negative integer, not boolean",
                    ".status must be a non-empty string",
                    ".dependsOn[0] must be a non-empty string",
                    ".ownedPaths must be a non-empty list",
                ],
                "malformed task fields",
            )

        with tempfile.TemporaryDirectory(prefix="lean-model-lab-plan-") as raw:
            fixture = Path(raw)
            copy_fixture(source, fixture)
            plan_path = fixture / "plan" / "tasks.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["tasks"][0]["wave"] = 9
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            task_path = fixture / "TASKS.md"
            task_path.write_text(
                task_path.read_text(encoding="utf-8").replace(
                    "- Wave: 0; status: **READY FOR REVIEW**; owner:",
                    "- Wave: 9; status: **READY FOR REVIEW**; owner:",
                    1,
                ),
                encoding="utf-8",
            )
            require_errors(
                validate_repository(fixture),
                ["ROADMAP.md must contain exactly one Wave 9 heading"],
                "declared wave without roadmap header",
            )

        with tempfile.TemporaryDirectory(prefix="lean-model-lab-plan-") as raw:
            fixture = Path(raw)
            copy_fixture(source, fixture)
            task_path = fixture / "TASKS.md"
            task_text = task_path.read_text(encoding="utf-8")
            task_text = task_text.replace(
                "## LM-F01 — Establish the architecture and experiment contract",
                "## LM-F01 — Drifted title",
                1,
            )
            task_text = task_text.replace(
                "- Wave: 0; status: **READY FOR REVIEW**; owner:",
                "- Wave: 9; status: **IN PROGRESS**; owner:",
                1,
            )
            task_text = task_text.replace("- Dependencies: none.", "- Dependencies: LM-F03.", 1)
            task_path.write_text(task_text, encoding="utf-8")
            require_errors(
                validate_repository(fixture),
                [
                    "LM-F01: TASKS title differs",
                    "LM-F01: TASKS wave differs",
                    "LM-F01: TASKS status differs",
                    "LM-F01: TASKS dependsOn differs",
                ],
                "task projection drift",
            )

        with tempfile.TemporaryDirectory(prefix="lean-model-lab-plan-") as raw:
            fixture = Path(raw)
            copy_fixture(source, fixture)
            plan_path = fixture / "plan" / "tasks.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            for task in plan["tasks"]:
                if task["id"] in FOUNDATION_IDS:
                    task["status"] = "IN_PROGRESS"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            task_path = fixture / "TASKS.md"
            task_path.write_text(
                re.sub(
                    r"(- Wave: 0; status: \*\*)READY FOR REVIEW(\*\*; owner:)",
                    r"\1IN PROGRESS\2",
                    task_path.read_text(encoding="utf-8"),
                    count=3,
                ),
                encoding="utf-8",
            )
            status_path = fixture / "STATUS.md"
            status_text = status_path.read_text(encoding="utf-8")
            for task_id in FOUNDATION_IDS:
                status_text = status_text.replace(
                    f"- {task_id}: **READY_FOR_REVIEW**",
                    f"- {task_id}: **IN_PROGRESS**",
                )
            status_path.write_text(status_text, encoding="utf-8")
            correction_errors = validate_repository(fixture)
            if correction_errors:
                raise AssertionError(
                    f"coherent IN_PROGRESS correction state should pass: {correction_errors}"
                )

        with tempfile.TemporaryDirectory(prefix="lean-model-lab-plan-") as raw:
            fixture = Path(raw)
            copy_fixture(source, fixture)
            plan_path = fixture / "plan" / "tasks.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            for task in plan["tasks"]:
                if task["id"] in FOUNDATION_IDS:
                    task["status"] = "DONE"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            task_path = fixture / "TASKS.md"
            task_path.write_text(
                re.sub(
                    r"(- Wave: 0; status: \*\*)READY FOR REVIEW(\*\*; owner:)",
                    r"\1DONE\2",
                    task_path.read_text(encoding="utf-8"),
                    count=3,
                ),
                encoding="utf-8",
            )
            require_errors(
                validate_repository(fixture),
                ["foundation DONE requires recorded Wave 0 review evidence"],
                "DONE without evidence",
            )
            status_path = fixture / "STATUS.md"
            status_text = status_path.read_text(encoding="utf-8")
            for task_id in FOUNDATION_IDS:
                status_text = status_text.replace(
                    f"- {task_id}: **READY_FOR_REVIEW**",
                    f"- {task_id}: **DONE**",
                )
            status_text = re.sub(
                r"^- Wave 0 review evidence: \*\*PENDING\*\*.*$",
                "- Wave 0 review evidence: **ACCEPTED 2026-09-07** — isolated self-test evidence.",
                status_text,
                count=1,
                flags=re.MULTILINE,
            )
            status_path.write_text(status_text, encoding="utf-8")
            done_errors = validate_repository(fixture)
            if done_errors:
                raise AssertionError(f"evidence-backed DONE should pass: {done_errors}")
    except AssertionError as exc:
        print(f"SELF-TEST FAIL: {exc}")
        return 1

    print(
        "SELF-TEST PASS: malformed top-level/task fields, missing wave header and task "
        "projection drift rejected; coherent correction state accepted; DONE evidence gate enforced"
    )
    return 0


def print_result(root: Path) -> int:
    errors = validate_repository(root)
    if errors:
        print(f"FAIL: {len(errors)} plan validation error(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    plan = json.loads((root / "plan" / "tasks.json").read_text(encoding="utf-8"))
    tasks = plan["tasks"]
    edge_count = sum(len(task["dependsOn"]) for task in tasks)
    waves = {task["wave"] for task in tasks}
    foundation_state = next(
        task["status"] for task in tasks if task["id"] == FOUNDATION_IDS[0]
    )
    print(
        f"PASS: {len(tasks)} tasks, {len(waves)} waves, {edge_count} dependency edges, "
        f"foundation={foundation_state}, plan/docs consistent"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run isolated negative tests")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    return run_self_test(root) if args.self_test else print_result(root)


if __name__ == "__main__":
    sys.exit(main())
