#!/usr/bin/env python3
"""Validate an agent-team-work .team state directory without mutating it."""
SCRIPT_INTERFACE = "cli"
SCRIPT_INTERFACE_REASON = "Validates a file-backed team ledger read-only and returns a machine-readable JSON result."
import argparse
import json
import re
import sys
from pathlib import Path

LEGACY_DISPATCH_KEY = re.compile(r"^(?P<team>[^/]+)/(?P<epoch>\d+)/(?P<stage>[^/]+)/(?P<attempt>\d+)/(?P<kind>standby|work|rework|result|accept|snapshot)$")
REVISION_DISPATCH_KEY = re.compile(r"^(?P<team>[^/]+)/(?P<epoch>\d+)/r(?P<cycle>\d+)/(?P<stage>[^/]+)/(?P<attempt>\d+)/(?P<kind>standby|work|rework|result|accept|snapshot)$")
SUPPORTED_LEDGER_VERSIONS = {2, 3}
REPORT_REQUIRED_STATUSES = {"reported", "accepted", "rework"}
NO_IMPACT_MARKER = "impact_result: no_affected_stages"

def parse_schema_version(value) -> int:
    try:
        version = int(value)
    except (TypeError, ValueError):
        return 0
    return version if version in SUPPORTED_LEDGER_VERSIONS else 0

def task_cycle(task: dict, schema_version: int) -> int:
    if schema_version == 2 and not task.get("revision_cycle"):
        return 1
    try:
        return int(task.get("revision_cycle", 0))
    except (TypeError, ValueError):
        return 0

def _int_value(value, default=0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def parse_dispatch_key(key: str) -> dict | None:
    for pattern in (REVISION_DISPATCH_KEY, LEGACY_DISPATCH_KEY):
        match = pattern.match(key)
        if match:
            data = match.groupdict()
            data["cycle"] = int(data.get("cycle") or 1)
            data["epoch"] = int(data["epoch"])
            data["attempt"] = int(data["attempt"])
            return data
    return None

def load_json(path: Path, failures: list[str]) -> dict:
    if not path.exists():
        failures.append(f"missing file: {path}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"invalid JSON {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        failures.append(f"JSON root must be an object: {path}")
        return {}
    return value

def require(payload: dict, fields: list[str], label: str, failures: list[str]) -> None:
    for field in fields:
        if not payload.get(field):
            failures.append(f"{label} missing {field}")

def validate(team_dir: Path) -> dict:
    failures: list[str] = []
    team = load_json(team_dir / "team.json", failures)
    tasks_payload = load_json(team_dir / "tasks.json", failures)
    team_schema = parse_schema_version(team.get("schema_version"))
    tasks_schema = parse_schema_version(tasks_payload.get("schema_version"))
    require(team, ["schema_version", "skill", "team_id", "project_id", "project_root", "status", "ownership_epoch", "leader", "members"], "team.json", failures)
    if team_schema == 0:
        failures.append("team.json schema_version is unsupported")
    if team.get("skill") != "agent-team-work":
        failures.append("team.json skill must be agent-team-work")
    if team.get("status") not in {"ready", "running", "paused", "blocked", "impact_analysis", "complete"}:
        failures.append("team.json status is invalid")
    leader = team.get("leader", {}) if isinstance(team.get("leader"), dict) else {}
    require(leader, ["thread_id", "host_id", "title"], "team.json leader", failures)
    members = team.get("members", []) if isinstance(team.get("members"), list) else []
    member_ids = []
    for index, member in enumerate(members):
        if not isinstance(member, dict):
            failures.append(f"member {index} must be an object")
            continue
        require(member, ["label", "role", "thread_id", "host_id", "checkout_path"], f"member {index}", failures)
        if member.get("thread_id"):
            member_ids.append(member["thread_id"])
        if member.get("project_verified") is not True:
            failures.append(f"member {member.get('label', index)} project_verified must be true")
    if len(member_ids) != len(set(member_ids)):
        failures.append("member thread_id values must be unique")
    try:
        ownership_epoch = int(team.get("ownership_epoch", 0))
    except (TypeError, ValueError):
        ownership_epoch = 0
    if ownership_epoch < 1:
        failures.append("team.json ownership_epoch must be positive")
    if team_schema == 3 and "revision_cycle" not in team:
        failures.append("team.json missing revision_cycle for schema_version 3")
    active_cycle = _int_value(team.get("revision_cycle", 1 if team_schema == 2 else 0))
    if active_cycle < 1:
        failures.append("team.json revision_cycle must be positive")
    if active_cycle > 1 and team_schema != 3:
        failures.append("revision_cycle above 1 requires schema_version 3")
    if active_cycle > 1:
        missing_records = [str(cycle) for cycle in range(2, active_cycle + 1)
                           if not (team_dir / "revisions" / f"{cycle}.md").is_file()]
        if missing_records:
            failures.append("missing revision record(s) for cycle(s) " + ", ".join(missing_records))
    require(tasks_payload, ["schema_version", "team_id", "revision", "last_writer_thread_id", "tasks"], "tasks.json", failures)
    if tasks_schema == 0:
        failures.append("tasks.json schema_version is unsupported")
    if team_schema and tasks_schema and team_schema != tasks_schema:
        failures.append("schema_version mismatch between team.json and tasks.json")
    if tasks_payload.get("team_id") != team.get("team_id"):
        failures.append("team_id mismatch between team.json and tasks.json")
    if tasks_payload.get("revision", 0) < 1:
        failures.append("tasks.json revision must be positive")
    if tasks_payload.get("last_writer_thread_id") != leader.get("thread_id"):
        failures.append("last_writer_thread_id must match the bound Leader")
    if team_schema == 3 and "revision_cycle" not in tasks_payload:
        failures.append("tasks.json missing revision_cycle for schema_version 3")
    if tasks_payload.get("revision_cycle", active_cycle) != active_cycle:
        failures.append("revision_cycle mismatch between team.json and tasks.json")
    tasks = tasks_payload.get("tasks", []) if isinstance(tasks_payload.get("tasks"), list) else []
    dispatch_keys = []
    parsed_tasks = []
    accepted_count = 0
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            failures.append(f"task {index} must be an object")
            continue
        label = f"task {task.get('task_id', index)}"
        require(task, ["task_id", "attempt", "status", "dispatch_state", "dispatch_key"], label, failures)
        attempt_value = _int_value(task.get("attempt", 0))
        if attempt_value < 1:
            failures.append(f"{label} attempt must be positive")
        cycle = task_cycle(task, team_schema)
        if cycle < 1:
            failures.append(f"{label} revision_cycle is invalid")
        if team_schema == 2 and cycle != 1:
            failures.append(f"{label} schema_version 2 tasks must resolve to revision_cycle 1")
        if cycle > active_cycle:
            failures.append(
                f"{label} revision_cycle {cycle} exceeds team active revision_cycle {active_cycle}"
            )
        if cycle > 1:
            if not isinstance(task.get("supersedes"), list):
                failures.append(f"{label} missing supersedes list")
            if not isinstance(task.get("impact_basis"), str) or not task.get("impact_basis", "").strip():
                failures.append(f"{label} missing impact_basis")
        if cycle > 1:
            require(task, ["team_id", "ownership_epoch", "stage", "dispatch_kind", "source", "report_path"], label, failures)
            report_path = task.get("report_path")
            if task.get("status") in REPORT_REQUIRED_STATUSES:
                if isinstance(report_path, str) and report_path.strip():
                    if not (team_dir / report_path).is_file():
                        failures.append(f"{label} report_path does not exist")
                elif report_path:
                    failures.append(f"{label} report_path must be a non-empty string")
        key = task.get("dispatch_key")
        parsed = None
        if key:
            dispatch_keys.append(key)
            parsed = parse_dispatch_key(key)
            if not parsed:
                failures.append(f"{label} dispatch_key format is invalid")
            else:
                if parsed["team"] != team.get("team_id") or parsed["epoch"] != ownership_epoch:
                    failures.append(f"{label} dispatch_key is bound to another team or epoch")
                if parsed["cycle"] > active_cycle:
                    failures.append(
                        f"{label} dispatch_key cycle exceeds team active revision_cycle"
                    )
                if parsed["cycle"] != cycle:
                    failures.append(f"{label} revision dispatch_key cycle does not match task revision")
        identity = {
            "team": task.get("team_id", task.get("team")),
            "epoch": task.get("ownership_epoch", task.get("epoch")),
            "stage": task.get("stage", task.get("stage_label")),
            "attempt": task.get("attempt"),
            "kind": task.get("dispatch_kind", task.get("kind")),
        }
        if parsed:
            expected = {"team": identity["team"], "epoch": identity["epoch"],
                        "stage": identity["stage"], "attempt": identity["attempt"],
                        "kind": identity["kind"]}
            for field, expected_value in expected.items():
                if expected_value is None:
                    continue
                if field in {"epoch", "attempt"}:
                    try:
                        expected_value = int(expected_value)
                    except (TypeError, ValueError):
                        failures.append(f"{label} task identity {field} must be numeric")
                        continue
                if parsed[field] != expected_value:
                    failures.append(f"{label} dispatch_key {field} does not match task identity")
        if cycle < active_cycle and task.get("status") == "accepted":
            # Historical accepted tasks are immutable evidence, not current work.
            pass
        parsed_tasks.append((task, cycle))
        if task.get("status") == "accepted":
            accepted_count += 1
            acceptance = task.get("acceptance", {}) if isinstance(task.get("acceptance"), dict) else {}
            if acceptance.get("status") != "accepted":
                failures.append(f"accepted task {task.get('task_id', index)} lacks accepted acceptance evidence")
            if not acceptance.get("evidence"):
                failures.append(f"accepted task {task.get('task_id', index)} lacks evidence paths")
            if cycle > 1:
                evidence = acceptance.get("evidence")
                if not isinstance(evidence, list) or any(not isinstance(item, dict) for item in evidence):
                    failures.append(f"accepted task {task.get('task_id', index)} evidence must bind to task identity")
                else:
                    for item in evidence:
                        if item.get("task_id") != task.get("task_id") or item.get("dispatch_key") != key:
                            failures.append(f"accepted task {task.get('task_id', index)} evidence is not bound to task")
                        if item.get("source") != task.get("source"):
                            failures.append(f"accepted task {task.get('task_id', index)} evidence source does not match task")
                        if item.get("path") != task.get("report_path"):
                            failures.append(f"accepted task {task.get('task_id', index)} evidence path does not match report")
    if len(dispatch_keys) != len(set(dispatch_keys)):
        failures.append("dispatch_key values must be unique")
    if team.get("status") == "complete":
        current = [(task, cycle) for task, cycle in parsed_tasks if cycle == active_cycle]
        accepted = [task for task, _ in current if task.get("status") == "accepted"]
        for task, _ in current:
            if task.get("status") == "stale":
                try:
                    stale_attempt = int(task.get("attempt", 0))
                except (TypeError, ValueError):
                    stale_attempt = 0
                superseded = False
                for candidate in accepted:
                    try:
                        candidate_attempt = int(candidate.get("attempt", 0))
                    except (TypeError, ValueError):
                        candidate_attempt = 0
                    if (task.get("task_id") in (candidate.get("supersedes") or [])
                            and candidate_attempt >= stale_attempt):
                        superseded = True
                        break
                if not superseded:
                    failures.append(f"stale task {task.get('task_id')} requires an accepted superseder")
            elif task.get("status") != "accepted":
                failures.append("complete team must have every current cycle task accepted")
        if not current:
            no_impact_recorded = False
            if team_schema == 3 and active_cycle > 1:
                record_path = team_dir / "revisions" / f"{active_cycle}.md"
                if record_path.is_file():
                    try:
                        no_impact_recorded = any(
                            line.strip() == NO_IMPACT_MARKER
                            for line in record_path.read_text(encoding="utf-8").splitlines()
                        )
                    except OSError:
                        no_impact_recorded = False
            if not no_impact_recorded:
                failures.append(
                    "complete team has no current cycle tasks without explicit "
                    f"{NO_IMPACT_MARKER} analysis"
                )
    return {"ok": not failures, "team_dir": str(team_dir), "team_id": team.get("team_id"), "status": team.get("status"), "revision": tasks_payload.get("revision"), "member_count": len(members), "task_count": len(tasks), "accepted_task_count": accepted_count, "failures": failures}

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an agent-team-work .team state directory.")
    parser.add_argument("team_dir", nargs="?", default=".team")
    args = parser.parse_args()
    report = validate(Path(args.team_dir).expanduser().resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 2

if __name__ == "__main__":
    sys.exit(main())
