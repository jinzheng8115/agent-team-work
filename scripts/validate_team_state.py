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
DISCUSSION_KEY = re.compile(
    r"^(?P<team>[^/]+)/(?P<epoch>\d+)/r(?P<cycle>\d+)/"
    r"(?P<stage>[^/]+)/(?P<task>[^/]+)/d(?P<sequence>\d+)$"
)
DISCUSSION_STATUSES = {
    "requested", "approved", "open", "proposing", "challenging",
    "decision_pending", "decided", "lead_accepted", "closed",
    "rejected", "blocked", "expired", "cancelled",
}
DISCUSSION_MESSAGE_KINDS = {"proposal", "challenge", "evidence", "response", "decision"}
TERMINAL_DISCUSSION_STATUSES = {"closed", "rejected", "blocked", "expired", "cancelled"}
DEFAULT_DISCUSSION_POLICY = {
    "mode": "worker_can_request",
    "soft_trigger_threshold": 2,
    "max_rounds": 2,
    "deadline": "Lead-defined",
}
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

def parse_discussion_key(key: str) -> dict | None:
    if not isinstance(key, str):
        return None
    match = DISCUSSION_KEY.match(key)
    if not match:
        return None
    data = match.groupdict()
    data["epoch"] = int(data["epoch"])
    data["cycle"] = int(data["cycle"])
    data["sequence"] = int(data["sequence"])
    return data

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

def _require_keys(payload: dict, fields: list[str], label: str, failures: list[str]) -> None:
    for field in fields:
        if field not in payload:
            failures.append(f"{label} missing {field}")

def validate_discussion_record(team_dir: Path, team: dict, tasks_by_id: dict,
                               record: dict, failures: list[str]) -> None:
    """Validate one discussion and its transcript/decision without mutating state."""
    discussion_id = record.get("discussion_id")
    label = f"discussion {discussion_id or '<missing>'}"
    require(record, [
        "discussion_id", "team_id", "ownership_epoch", "revision_cycle", "stage",
        "task_id", "dispatch_key", "status", "trigger", "question", "opened_by",
        "participants", "decision_owner", "max_rounds", "deadline",
        "transcript_path", "decision_path", "affected_tasks",
    ], label, failures)
    parsed = parse_discussion_key(discussion_id)
    if not parsed:
        failures.append(f"{label} discussion_id format is invalid")
        return

    ownership_epoch = _int_value(team.get("ownership_epoch"))
    active_cycle = _int_value(team.get("revision_cycle", 1))
    expected_record_identity = {
        "team_id": parsed["team"],
        "ownership_epoch": parsed["epoch"],
        "revision_cycle": parsed["cycle"],
        "stage": parsed["stage"],
        "task_id": parsed["task"],
    }
    for field, expected in expected_record_identity.items():
        actual = record.get(field)
        if field in {"ownership_epoch", "revision_cycle"}:
            actual = _int_value(actual, -1)
        if actual != expected:
            failures.append(f"{label} {field} does not match discussion identity")
    if parsed["team"] != team.get("team_id") or parsed["epoch"] != ownership_epoch:
        failures.append(f"{label} is bound to another team or ownership_epoch")
    if parsed["cycle"] != active_cycle:
        failures.append(f"{label} revision_cycle does not match active cycle")
    if parsed["stage"] != team.get("active_stage"):
        failures.append(f"{label} stage does not match team active_stage")

    task = tasks_by_id.get(parsed["task"])
    if not task:
        failures.append(f"{label} has no matching active task")
    else:
        if task.get("status") in {"stale", "duplicate"}:
            failures.append(f"{label} cannot advance stale or duplicate task {parsed['task']}")
        if record.get("dispatch_key") != task.get("dispatch_key"):
            failures.append(f"{label} dispatch_key does not match task identity")
        if task.get("stage") != parsed["stage"]:
            failures.append(f"{label} stage does not match task identity")
        if task_cycle(task, 3) != parsed["cycle"]:
            failures.append(f"{label} revision_cycle does not match task identity")

    if record.get("status") not in DISCUSSION_STATUSES:
        failures.append(f"{label} status is invalid")
    if _int_value(record.get("max_rounds")) < 1:
        failures.append(f"{label} max_rounds must be positive")

    members = team.get("members", []) if isinstance(team.get("members"), list) else []
    members_by_label = {
        member.get("label"): member for member in members
        if isinstance(member, dict) and member.get("label")
    }
    participants = record.get("participants")
    participant_labels: set[str] = set()
    if not isinstance(participants, list) or not participants:
        failures.append(f"{label} participants must be a non-empty list")
    else:
        for index, participant in enumerate(participants):
            if not isinstance(participant, dict):
                failures.append(f"{label} participant {index} must contain label and role")
                continue
            participant_label = participant.get("label")
            if not participant_label or not participant.get("role"):
                failures.append(f"{label} participant {index} missing label or role")
                continue
            member = members_by_label.get(participant_label)
            if not member:
                failures.append(f"{label} participant {participant_label} is not a team member")
                continue
            participant_labels.add(participant_label)
            if participant.get("role") != member.get("role"):
                failures.append(f"{label} participant {participant_label} role does not match member binding")
            if participant.get("thread_id") is not None and participant.get("thread_id") != member.get("thread_id"):
                failures.append(f"{label} participant {participant_label} thread_id does not match member binding")
    decision_owner = record.get("decision_owner")
    if decision_owner not in participant_labels:
        failures.append(f"{label} decision_owner must be a participant")

    status = record.get("status")
    closed_or_lead_accepted = status in {"lead_accepted", "closed"}
    leader_thread_id = (team.get("leader") or {}).get("thread_id")
    worker_participant_labels = {
        participant_label for participant_label in participant_labels
        if (member := members_by_label.get(participant_label))
        and member.get("thread_id") != leader_thread_id
        and str(member.get("role", "")).casefold() != "leader"
    }
    if closed_or_lead_accepted:
        if len(participant_labels) < 2:
            failures.append(f"{label} requires at least two participants")
        if decision_owner not in worker_participant_labels:
            failures.append(f"{label} decision_owner must be a worker participant")

    expected_transcript = f"discussions/{parsed['task']}/d{parsed['sequence']}/messages.jsonl"
    expected_decision = f"discussions/{parsed['task']}/d{parsed['sequence']}/decision.json"
    if record.get("transcript_path") != expected_transcript:
        failures.append(f"{label} transcript_path does not match discussion identity")
    if record.get("decision_path") != expected_decision:
        failures.append(f"{label} decision_path does not match discussion identity")

    transcript_path = team_dir / expected_transcript
    owner_decision_message = False
    worker_to_worker_non_decision_sequences: set[int] = set()
    worker_to_worker_message = False
    participant_senders_before_owner_decision: set[str] = set()
    participant_message_senders: list[tuple[int, str]] = []
    owner_decision_sequence: int | None = None
    if not transcript_path.is_file():
        failures.append(f"{label} missing messages transcript: {transcript_path}")
    else:
        message_sequences: set[int] = set()
        message_ids: set[str] = set()
        try:
            lines = transcript_path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            failures.append(f"{label} cannot read messages transcript: {exc}")
            lines = []
        for line_number, line in enumerate(lines, 1):
            message_label = f"{label} message line {line_number}"
            try:
                message = json.loads(line)
            except json.JSONDecodeError as exc:
                failures.append(f"{message_label} is invalid JSON: {exc}")
                continue
            if not isinstance(message, dict):
                failures.append(f"{message_label} must be an object")
                continue
            _require_keys(message, [
                "message_id", "discussion_id", "sender", "recipients", "sequence",
                "kind", "in_reply_to", "body", "created_at",
            ], message_label, failures)
            if message.get("discussion_id") != discussion_id:
                failures.append(f"{message_label} discussion_id does not match record")
            sequence = _int_value(message.get("sequence"), -1)
            if sequence < 1:
                failures.append(f"{message_label} sequence must be positive")
            elif sequence in message_sequences:
                failures.append(f"{message_label} has duplicate sequence {sequence}")
            else:
                message_sequences.add(sequence)
            message_id = message.get("message_id")
            if message_id in message_ids:
                failures.append(f"{message_label} has duplicate message_id")
            elif isinstance(message_id, str) and message_id:
                message_ids.add(message_id)
            if message.get("sender") not in participant_labels:
                failures.append(f"{message_label} sender is not a known participant")
            recipients = message.get("recipients")
            if (not isinstance(recipients, list) or not recipients
                    or any(recipient not in participant_labels for recipient in recipients)):
                failures.append(f"{message_label} recipients must be known participant labels")
            if message.get("kind") not in DISCUSSION_MESSAGE_KINDS:
                failures.append(f"{message_label} kind is invalid")
            if message.get("kind") == "decision" and message.get("sender") != decision_owner:
                failures.append(f"{message_label} decision sender must match decision_owner")
            if (message.get("kind") == "decision"
                    and message.get("sender") == decision_owner
                    and message.get("discussion_id") == discussion_id):
                owner_decision_message = True
                if sequence > 0 and (owner_decision_sequence is None or sequence < owner_decision_sequence):
                    owner_decision_sequence = sequence
            sender = message.get("sender")
            if sequence > 0 and sender in participant_labels:
                participant_message_senders.append((sequence, sender))
            if sender in worker_participant_labels:
                has_worker_recipient = any(
                    recipient in worker_participant_labels and recipient != sender
                    for recipient in recipients
                ) if isinstance(recipients, list) else False
                if has_worker_recipient:
                    worker_to_worker_message = True
                    if message.get("kind") != "decision":
                        worker_to_worker_non_decision_sequences.add(sequence)
        if owner_decision_sequence is not None:
            participant_senders_before_owner_decision = {
                sender for sequence, sender in participant_message_senders
                if sequence < owner_decision_sequence
            }
        has_peer_exchange_before_owner_decision = (
            owner_decision_sequence is not None
            and any(
                sequence < owner_decision_sequence
                for sequence in worker_to_worker_non_decision_sequences
            )
        )

        if closed_or_lead_accepted:
            if not has_peer_exchange_before_owner_decision:
                failures.append(
                    f"{label} requires a worker-to-worker non-decision message before decision_owner decision"
                )
            if not worker_to_worker_message:
                failures.append(f"{label} cannot contain only self-directed or Lead-directed messages")
            if len(participant_senders_before_owner_decision) < 2:
                failures.append(
                    f"{label} requires two participant senders before decision_owner decision"
                )

    decision_path = team_dir / expected_decision
    decision_required = status in {"decided", "lead_accepted", "closed"}
    if decision_required and not decision_path.is_file():
        failures.append(f"{label} missing decision.json for status {status}")
        return
    if not decision_path.is_file():
        return
    decision = load_json(decision_path, failures)
    if decision.get("discussion_id") not in {None, discussion_id}:
        failures.append(f"{label} decision discussion_id does not match record")
    if status in {"lead_accepted", "closed"}:
        _require_keys(decision, [
            "chosen_option", "rationale", "evidence", "rejected_alternatives",
            "affected_tasks", "decision_owner", "decision_owner_thread_id",
            "lead_acceptance",
        ], f"{label} decision", failures)
        require(decision, [
            "chosen_option", "rationale", "evidence", "affected_tasks",
            "decision_owner", "decision_owner_thread_id",
        ], f"{label} decision", failures)
        if not owner_decision_message:
            failures.append(f"{label} missing decision message from decision_owner")
    if decision.get("decision_owner") is not None and decision.get("decision_owner") != decision_owner:
        failures.append(f"{label} decision_owner does not match record")
    owner_member = members_by_label.get(decision_owner)
    owner_thread_id = decision.get("decision_owner_thread_id")
    if status in {"lead_accepted", "closed"}:
        if not owner_thread_id:
            failures.append(f"{label} decision missing decision_owner_thread_id")
        elif not owner_member or owner_thread_id != owner_member.get("thread_id"):
            failures.append(f"{label} decision owner identity does not match member binding")
        acceptance = decision.get("lead_acceptance")
        if not isinstance(acceptance, dict):
            failures.append(f"{label} decision missing lead_acceptance identity")
        else:
            if acceptance.get("status") != "accepted":
                failures.append(f"{label} lead_acceptance status must be accepted")
            acceptance_thread = acceptance.get("thread_id", acceptance.get("leader_thread_id"))
            if acceptance_thread != (team.get("leader") or {}).get("thread_id"):
                failures.append(f"{label} lead_acceptance identity does not match bound Leader")

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
    if _int_value(tasks_payload.get("revision", 0)) < 1:
        failures.append("tasks.json revision must be positive")
    if tasks_payload.get("last_writer_thread_id") != leader.get("thread_id"):
        failures.append("last_writer_thread_id must match the bound Leader")
    if team_schema == 3 and "revision_cycle" not in tasks_payload:
        failures.append("tasks.json missing revision_cycle for schema_version 3")
    if tasks_payload.get("revision_cycle", active_cycle) != active_cycle:
        failures.append("revision_cycle mismatch between team.json and tasks.json")
    team_has_discussion_protocol = "discussion_protocol_version" in team
    tasks_have_discussion_protocol = "discussion_protocol_version" in tasks_payload
    if team_has_discussion_protocol != tasks_have_discussion_protocol:
        failures.append(
            "discussion_protocol_version must be present in both team.json and tasks.json"
        )
    team_discussion_protocol = team.get("discussion_protocol_version")
    tasks_discussion_protocol = tasks_payload.get("discussion_protocol_version")
    if (team_has_discussion_protocol
            and (type(team_discussion_protocol) is not int or team_discussion_protocol != 1)):
        failures.append("team.json discussion_protocol_version must be integer 1")
    if (tasks_have_discussion_protocol
            and (type(tasks_discussion_protocol) is not int or tasks_discussion_protocol != 1)):
        failures.append("tasks.json discussion_protocol_version must be integer 1")
    if (team_has_discussion_protocol and tasks_have_discussion_protocol
            and team_discussion_protocol != tasks_discussion_protocol):
        failures.append("discussion_protocol_version mismatch between team.json and tasks.json")
    discussion_protocol_enabled = (
        team_has_discussion_protocol
        and tasks_have_discussion_protocol
        and type(team_discussion_protocol) is int
        and type(tasks_discussion_protocol) is int
        and team_discussion_protocol == tasks_discussion_protocol == 1
    )
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
        policy = task.get("discussion_policy")
        if policy is not None and policy != DEFAULT_DISCUSSION_POLICY:
            failures.append(f"{label} discussion_policy must match the worker_can_request default")
        task_kind = parsed["kind"] if parsed else task.get("dispatch_kind")
        is_enabled_current_work = (
            discussion_protocol_enabled
            and cycle == active_cycle
            and task_kind in {"work", "rework"}
        )
        if is_enabled_current_work and policy is None:
            failures.append(f"{label} missing discussion_policy for enabled current work/rework task")
        if "discussion_ids" in task:
            discussion_ids = task.get("discussion_ids")
            if not isinstance(discussion_ids, list):
                failures.append(f"{label} discussion_ids must be a list")
            else:
                for discussion_id in discussion_ids:
                    discussion = parse_discussion_key(discussion_id)
                    if not discussion:
                        failures.append(f"{label} discussion_ids entry {discussion_id} is invalid")
                        continue
                    expected_discussion_identity = {
                        "team": team.get("team_id"),
                        "epoch": ownership_epoch,
                        "cycle": cycle,
                        "stage": task.get("stage", parsed.get("stage") if parsed else None),
                        "task": task.get("task_id"),
                    }
                    if any(
                        discussion[field] != expected
                        for field, expected in expected_discussion_identity.items()
                    ):
                        failures.append(
                            f"{label} discussion_ids entry {discussion_id} does not match task identity"
                        )
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
    tasks_by_id = {
        task.get("task_id"): task for task, _ in parsed_tasks
        if isinstance(task.get("task_id"), str) and task.get("task_id")
    }
    active_discussions_by_task: dict[str, list[str]] = {}
    discussions_dir = team_dir / "discussions"
    if discussions_dir.is_dir():
        for discussion_dir in sorted(path for path in discussions_dir.glob("*/*") if path.is_dir()):
            record_path = discussion_dir / "record.json"
            if not record_path.is_file():
                failures.append(f"discussion directory missing record.json: {discussion_dir}")
                continue
            record = load_json(record_path, failures)
            parsed_discussion = parse_discussion_key(record.get("discussion_id"))
            if parsed_discussion:
                expected_dir = discussions_dir / parsed_discussion["task"] / f"d{parsed_discussion['sequence']}"
                if discussion_dir != expected_dir:
                    failures.append(
                        f"discussion {record.get('discussion_id')} record path does not match discussion identity"
                    )
            validate_discussion_record(team_dir, team, tasks_by_id, record, failures)
            if record.get("status") not in TERMINAL_DISCUSSION_STATUSES:
                task_id = record.get("task_id")
                active_discussions_by_task.setdefault(task_id, []).append(
                    record.get("discussion_id", str(record_path))
                )
        for task_id, discussion_ids in active_discussions_by_task.items():
            if len(discussion_ids) > 1:
                failures.append(
                    f"duplicate active discussion records for task {task_id}: "
                    + ", ".join(discussion_ids)
                )
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
