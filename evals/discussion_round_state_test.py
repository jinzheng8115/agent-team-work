#!/usr/bin/env python3
"""Regression fixtures for worker discussion-round state validation."""

import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_team_state import validate


_FIXTURES: list[Path] = []


def write_fixture(*, status="closed", with_policy=True, discussions=["d1"],
                  statuses=None, record_overrides=None, message_overrides=None,
                  decision_overrides=None, task_status="reported") -> Path:
    """Create a temporary schema-3 team with optional discussion evidence."""
    team_dir = Path(tempfile.mkdtemp())
    _FIXTURES.append(team_dir)
    team = {
        "schema_version": 3,
        "skill": "agent-team-work",
        "team_id": "team",
        "project_id": "project",
        "project_root": str(team_dir),
        "status": "running",
        "ownership_epoch": 1,
        "revision_cycle": 1,
        "active_stage": "implementation",
        "leader": {"thread_id": "leader-thread", "host_id": "host", "title": "Lead"},
        "members": [
            {
                "label": "worker",
                "role": "implementer",
                "thread_id": "worker-thread",
                "host_id": "host",
                "checkout_path": str(team_dir),
                "project_verified": True,
            },
            {
                "label": "reviewer",
                "role": "reviewer",
                "thread_id": "reviewer-thread",
                "host_id": "host",
                "checkout_path": str(team_dir),
                "project_verified": True,
            },
        ],
    }
    task = {
        "task_id": "task",
        "revision_cycle": 1,
        "attempt": 1,
        "team_id": "team",
        "ownership_epoch": 1,
        "stage": "implementation",
        "dispatch_kind": "work",
        "source": "worker",
        "status": task_status,
        "dispatch_state": task_status,
        "dispatch_key": "team/1/r1/implementation/1/work",
        "report_path": "reports/task.md",
        "discussion_ids": [f"team/1/r1/implementation/task/{item}" for item in discussions],
    }
    if with_policy:
        task["discussion_policy"] = {
            "mode": "worker_can_request",
            "soft_trigger_threshold": 2,
            "max_rounds": 2,
            "deadline": "Lead-defined",
        }
    tasks = {
        "schema_version": 3,
        "team_id": "team",
        "revision": 1,
        "revision_cycle": 1,
        "current_task_id": "task",
        "last_writer_thread_id": "leader-thread",
        "tasks": [task],
    }
    (team_dir / "team.json").write_text(json.dumps(team), encoding="utf-8")
    (team_dir / "tasks.json").write_text(json.dumps(tasks), encoding="utf-8")
    reports_dir = team_dir / "reports"
    reports_dir.mkdir()
    (reports_dir / "task.md").write_text("task evidence", encoding="utf-8")

    resolved_statuses = statuses or [status] * len(discussions)
    for index, name in enumerate(discussions):
        sequence = int(name.removeprefix("d"))
        discussion_id = f"team/1/r1/implementation/task/d{sequence}"
        discussion_dir = team_dir / "discussions" / "task" / f"d{sequence}"
        discussion_dir.mkdir(parents=True)
        record = {
            "discussion_id": discussion_id,
            "team_id": "team",
            "ownership_epoch": 1,
            "revision_cycle": 1,
            "stage": "implementation",
            "task_id": "task",
            "dispatch_key": "team/1/r1/implementation/1/work",
            "status": resolved_statuses[index],
            "trigger": "cross-role contract choice",
            "question": "Which compatible option should the task use?",
            "opened_by": "worker",
            "participants": [
                {"label": "worker", "role": "implementer", "thread_id": "worker-thread"},
                {"label": "reviewer", "role": "reviewer", "thread_id": "reviewer-thread"},
            ],
            "decision_owner": "worker",
            "max_rounds": 2,
            "deadline": "2026-09-17T12:00:00+08:00",
            "transcript_path": f"discussions/task/d{sequence}/messages.jsonl",
            "decision_path": f"discussions/task/d{sequence}/decision.json",
            "affected_tasks": ["task"],
        }
        if record_overrides and index == 0:
            record.update(record_overrides)
        (discussion_dir / "record.json").write_text(json.dumps(record), encoding="utf-8")

        messages = [
            {
                "message_id": f"{discussion_id}/m1",
                "discussion_id": discussion_id,
                "sender": "worker",
                "recipients": ["reviewer"],
                "sequence": 1,
                "kind": "proposal",
                "in_reply_to": None,
                "body": "Use option A.",
                "created_at": "2026-09-17T10:00:00+08:00",
            },
            {
                "message_id": f"{discussion_id}/m2",
                "discussion_id": discussion_id,
                "sender": "reviewer",
                "recipients": ["worker"],
                "sequence": 2,
                "kind": "challenge",
                "in_reply_to": f"{discussion_id}/m1",
                "body": "Option A needs compatibility evidence.",
                "created_at": "2026-09-17T10:05:00+08:00",
            },
        ]
        if message_overrides and index == 0:
            for message_index, overrides in enumerate(message_overrides):
                messages[message_index].update(overrides)
        with (discussion_dir / "messages.jsonl").open("w", encoding="utf-8") as transcript:
            for message in messages:
                transcript.write(json.dumps(message) + "\n")

        if resolved_statuses[index] in {"decided", "lead_accepted", "closed"}:
            decision = {
                "discussion_id": discussion_id,
                "chosen_option": "option-a",
                "rationale": "It preserves compatibility.",
                "evidence": ["reports/task.md"],
                "rejected_alternatives": ["option-b"],
                "affected_tasks": ["task"],
                "decision_owner": "worker",
                "decision_owner_thread_id": "worker-thread",
                "lead_acceptance": {
                    "status": "accepted",
                    "thread_id": "leader-thread",
                },
            }
            if decision_overrides and index == 0:
                decision.update(decision_overrides)
            (discussion_dir / "decision.json").write_text(json.dumps(decision), encoding="utf-8")
    return team_dir


def test_valid_closed_discussion():
    result = validate(write_fixture(status="closed"))
    assert result["ok"], result


def test_legacy_team_without_discussion_policy_remains_valid():
    result = validate(write_fixture(with_policy=False, discussions=[]))
    assert result["ok"], result


def test_discussion_key_must_match_task_identity():
    result = validate(write_fixture(record_overrides={"discussion_id": "team/1/r2/other/task/d1"}))
    assert "discussion" in " ".join(result["failures"])


def test_unknown_participant_is_rejected():
    result = validate(write_fixture(record_overrides={"participants": ["missing"]}))
    assert "participant" in " ".join(result["failures"])


def test_decision_owner_must_be_a_participant():
    result = validate(write_fixture(record_overrides={"decision_owner": "missing"}))
    assert "decision_owner" in " ".join(result["failures"])


def test_closed_discussion_requires_lead_acceptance():
    result = validate(write_fixture(status="closed", decision_overrides={"lead_acceptance": None}))
    assert "lead_acceptance" in " ".join(result["failures"])


def test_message_identity_and_sequence_are_checked():
    result = validate(write_fixture(message_overrides=[{"discussion_id": "other", "sequence": 1}]))
    assert "message" in " ".join(result["failures"])


def test_duplicate_active_discussion_is_rejected():
    result = validate(write_fixture(discussions=["d1", "d2"], statuses=["open", "proposing"]))
    assert "duplicate" in " ".join(result["failures"])


def test_stale_task_cannot_advance_from_discussion():
    result = validate(write_fixture(task_status="stale", status="lead_accepted"))
    assert "stale" in " ".join(result["failures"])


def main() -> int:
    tests = [value for name, value in globals().items() if name.startswith("test_")]
    try:
        for test in tests:
            test()
    finally:
        for fixture in _FIXTURES:
            shutil.rmtree(fixture, ignore_errors=True)
    print(f"PASS discussion-round-state ({len(tests)} tests)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
