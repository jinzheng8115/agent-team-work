#!/usr/bin/env python3
"""Validate an agent-team-work .team state directory without mutating it."""

SCRIPT_INTERFACE = "cli"
SCRIPT_INTERFACE_REASON = "Validates a file-backed team ledger read-only and returns a machine-readable JSON result."

import argparse
import json
import re
import sys
from pathlib import Path


DISPATCH_KEY = re.compile(r"^(?P<team>[^/]+)/(?P<epoch>\d+)/(?P<stage>[^/]+)/(?P<attempt>\d+)/(?P<kind>standby|work|rework|result|accept|snapshot)$")


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

    require(
        team,
        ["schema_version", "skill", "team_id", "project_id", "project_root", "status", "ownership_epoch", "leader", "members"],
        "team.json",
        failures,
    )
    if team.get("skill") != "agent-team-work":
        failures.append("team.json skill must be agent-team-work")
    if team.get("status") not in {"ready", "running", "paused", "blocked", "complete"}:
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
        thread_id = member.get("thread_id")
        if thread_id:
            member_ids.append(thread_id)
        if member.get("project_verified") is not True:
            failures.append(f"member {member.get('label', index)} project_verified must be true")
    if len(member_ids) != len(set(member_ids)):
        failures.append("member thread_id values must be unique")

    require(tasks_payload, ["schema_version", "team_id", "revision", "last_writer_thread_id", "tasks"], "tasks.json", failures)
    if tasks_payload.get("team_id") != team.get("team_id"):
        failures.append("team_id mismatch between team.json and tasks.json")
    if tasks_payload.get("revision", 0) < 1:
        failures.append("tasks.json revision must be positive")
    if tasks_payload.get("last_writer_thread_id") != leader.get("thread_id"):
        failures.append("last_writer_thread_id must match the bound Leader")

    tasks = tasks_payload.get("tasks", []) if isinstance(tasks_payload.get("tasks"), list) else []
    dispatch_keys: list[str] = []
    accepted_count = 0
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            failures.append(f"task {index} must be an object")
            continue
        require(task, ["task_id", "attempt", "status", "dispatch_state", "dispatch_key"], f"task {index}", failures)
        if task.get("attempt", 0) < 1:
            failures.append(f"task {task.get('task_id', index)} attempt must be positive")
        key = task.get("dispatch_key")
        if key:
            dispatch_keys.append(key)
            match = DISPATCH_KEY.match(key)
            if not match:
                failures.append(f"task {task.get('task_id', index)} dispatch_key format is invalid")
            elif match.group("team") != team.get("team_id") or int(match.group("epoch")) != int(team.get("ownership_epoch", 0)):
                failures.append(f"task {task.get('task_id', index)} dispatch_key is bound to another team or epoch")
        if task.get("status") == "accepted":
            accepted_count += 1
            acceptance = task.get("acceptance", {}) if isinstance(task.get("acceptance"), dict) else {}
            if acceptance.get("status") != "accepted":
                failures.append(f"accepted task {task.get('task_id', index)} lacks accepted acceptance evidence")
            if not acceptance.get("evidence"):
                failures.append(f"accepted task {task.get('task_id', index)} lacks evidence paths")
    if len(dispatch_keys) != len(set(dispatch_keys)):
        failures.append("dispatch_key values must be unique")
    if team.get("status") == "complete" and tasks and accepted_count != len(tasks):
        failures.append("complete team must have every task accepted")

    return {
        "ok": not failures,
        "team_dir": str(team_dir),
        "team_id": team.get("team_id"),
        "status": team.get("status"),
        "revision": tasks_payload.get("revision"),
        "member_count": len(members),
        "task_count": len(tasks),
        "accepted_task_count": accepted_count,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an agent-team-work .team state directory.")
    parser.add_argument("team_dir", nargs="?", default=".team")
    args = parser.parse_args()
    report = validate(Path(args.team_dir).expanduser().resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
