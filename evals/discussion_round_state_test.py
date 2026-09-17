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
                  decision_overrides=None, task_status="reported",
                  task_overrides=None, team_protocol_version=1,
                  tasks_protocol_version=1, extra_members=None) -> Path:
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
    if extra_members:
        team["members"].extend(extra_members)
    if team_protocol_version is not None:
        team["discussion_protocol_version"] = team_protocol_version
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
    if task_overrides:
        task.update(task_overrides)
    tasks = {
        "schema_version": 3,
        "team_id": "team",
        "revision": 1,
        "revision_cycle": 1,
        "current_task_id": "task",
        "last_writer_thread_id": "leader-thread",
        "tasks": [task],
    }
    if tasks_protocol_version is not None:
        tasks["discussion_protocol_version"] = tasks_protocol_version
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
            {
                "message_id": f"{discussion_id}/m3",
                "discussion_id": discussion_id,
                "sender": "worker",
                "recipients": ["reviewer"],
                "sequence": 3,
                "kind": "decision",
                "in_reply_to": f"{discussion_id}/m2",
                "body": "Choose option A based on the compatibility evidence.",
                "created_at": "2026-09-17T10:10:00+08:00",
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
    result = validate(write_fixture(
        with_policy=False,
        discussions=[],
        team_protocol_version=None,
        tasks_protocol_version=None,
    ))
    assert result["ok"], result


def test_discussion_key_must_match_task_identity():
    result = validate(write_fixture(record_overrides={"discussion_id": "team/1/r2/other/task/d1"}))
    assert not result["ok"], result
    assert "discussion team/1/r2/other/task/d1 revision_cycle does not match active cycle" in result["failures"]


def test_unknown_participant_is_rejected():
    result = validate(write_fixture(record_overrides={"participants": ["missing"]}))
    assert not result["ok"], result
    assert "discussion team/1/r1/implementation/task/d1 participant 0 must contain label and role" in result["failures"]


def test_decision_owner_must_be_a_participant():
    result = validate(write_fixture(record_overrides={"decision_owner": "missing"}))
    assert not result["ok"], result
    assert "discussion team/1/r1/implementation/task/d1 decision_owner must be a participant" in result["failures"]


def test_closed_discussion_requires_lead_acceptance():
    result = validate(write_fixture(status="closed", decision_overrides={"lead_acceptance": None}))
    assert not result["ok"], result
    assert "discussion team/1/r1/implementation/task/d1 decision missing lead_acceptance identity" in result["failures"]


def test_message_identity_and_sequence_are_checked():
    result = validate(write_fixture(message_overrides=[{"discussion_id": "other", "sequence": 1}]))
    assert not result["ok"], result
    assert "discussion team/1/r1/implementation/task/d1 message line 1 discussion_id does not match record" in result["failures"]


def test_duplicate_active_discussion_is_rejected():
    result = validate(write_fixture(discussions=["d1", "d2"], statuses=["open", "proposing"]))
    assert not result["ok"], result
    assert "duplicate active discussion records for task task: team/1/r1/implementation/task/d1, team/1/r1/implementation/task/d2" in result["failures"]


def test_stale_task_cannot_advance_from_discussion():
    result = validate(write_fixture(task_status="stale", status="lead_accepted"))
    assert not result["ok"], result
    assert "discussion team/1/r1/implementation/task/d1 cannot advance stale or duplicate task task" in result["failures"]


def test_empty_record_is_rejected():
    team_dir = write_fixture()
    (team_dir / "discussions/task/d1/record.json").write_text("{}", encoding="utf-8")
    result = validate(team_dir)
    assert not result["ok"], result
    assert "discussion <missing> missing discussion_id" in result["failures"]


def test_empty_closed_decision_is_rejected():
    team_dir = write_fixture()
    (team_dir / "discussions/task/d1/decision.json").write_text("{}", encoding="utf-8")
    result = validate(team_dir)
    assert not result["ok"], result
    assert "discussion team/1/r1/implementation/task/d1 decision missing chosen_option" in result["failures"]


def test_sparse_lead_accepted_decision_is_rejected():
    team_dir = write_fixture(status="lead_accepted")
    sparse = {"lead_acceptance": {"status": "accepted", "thread_id": "leader-thread"}}
    (team_dir / "discussions/task/d1/decision.json").write_text(json.dumps(sparse), encoding="utf-8")
    result = validate(team_dir)
    assert not result["ok"], result
    assert "discussion team/1/r1/implementation/task/d1 decision missing decision_owner" in result["failures"]


def test_lead_accepted_requires_owner_thread_binding():
    result = validate(write_fixture(
        status="lead_accepted", decision_overrides={"decision_owner_thread_id": None}
    ))
    assert not result["ok"], result
    assert "discussion team/1/r1/implementation/task/d1 decision missing decision_owner_thread_id" in result["failures"]


def test_lead_accepted_requires_owner_authored_decision_message():
    result = validate(write_fixture(
        status="lead_accepted", message_overrides=[{}, {}, {"kind": "response"}]
    ))
    assert not result["ok"], result
    assert "discussion team/1/r1/implementation/task/d1 missing decision message from decision_owner" in result["failures"]


def test_closed_and_lead_accepted_reject_ai_music_d1_leader_mediated_shape():
    for status in ("closed", "lead_accepted"):
        result = validate(write_fixture(
            status=status,
            extra_members=[{
                "label": "leader",
                "role": "leader",
                "thread_id": "leader-thread",
                "host_id": "host",
                "checkout_path": ".",
                "project_verified": True,
            }],
            record_overrides={
                "participants": [
                    {"label": "worker", "role": "implementer", "thread_id": "worker-thread"},
                    {"label": "reviewer", "role": "reviewer", "thread_id": "reviewer-thread"},
                    {"label": "leader", "role": "leader", "thread_id": "leader-thread"},
                ],
            },
            message_overrides=[
                {"recipients": ["leader"]},
                {"recipients": ["leader"]},
                {"recipients": ["leader"]},
            ],
        ))
        assert not result["ok"], result
        assert "discussion team/1/r1/implementation/task/d1 requires a worker-to-worker non-decision message before decision_owner decision" in result["failures"]
        assert "discussion team/1/r1/implementation/task/d1 cannot contain only self-directed or Lead-directed messages" in result["failures"]


def test_closed_discussion_requires_two_participant_senders_before_owner_decision():
    result = validate(write_fixture(message_overrides=[
        {"recipients": ["reviewer"]},
        {"sender": "worker", "recipients": ["reviewer"]},
        {"recipients": ["reviewer"]},
    ]))
    assert not result["ok"], result
    assert "discussion team/1/r1/implementation/task/d1 requires two participant senders before decision_owner decision" in result["failures"]


def test_closed_discussion_rejects_peer_exchange_appended_after_owner_decision():
    team_dir = write_fixture(message_overrides=[
        {"recipients": ["leader"]},
        {"recipients": ["leader"]},
        {"recipients": ["leader"]},
    ], extra_members=[{
        "label": "leader",
        "role": "leader",
        "thread_id": "leader-thread",
        "host_id": "host",
        "checkout_path": ".",
        "project_verified": True,
    }], record_overrides={
        "participants": [
            {"label": "worker", "role": "implementer", "thread_id": "worker-thread"},
            {"label": "reviewer", "role": "reviewer", "thread_id": "reviewer-thread"},
            {"label": "leader", "role": "leader", "thread_id": "leader-thread"},
        ],
    })
    transcript_path = team_dir / "discussions/task/d1/messages.jsonl"
    with transcript_path.open("a", encoding="utf-8") as transcript:
        transcript.write(json.dumps({
            "message_id": "team/1/r1/implementation/task/d1/m4",
            "discussion_id": "team/1/r1/implementation/task/d1",
            "sender": "reviewer",
            "recipients": ["worker"],
            "sequence": 4,
            "kind": "response",
            "in_reply_to": "team/1/r1/implementation/task/d1/m3",
            "body": "This peer exchange arrived after the decision.",
            "created_at": "2026-09-17T10:15:00+08:00",
        }) + "\n")
    result = validate(team_dir)
    assert not result["ok"], result
    assert "discussion team/1/r1/implementation/task/d1 requires a worker-to-worker non-decision message before decision_owner decision" in result["failures"]


_LEADER_MEMBER = {
    "label": "leader",
    "role": "leader",
    "thread_id": "leader-thread",
    "host_id": "host",
    "checkout_path": ".",
    "project_verified": True,
}


def test_closed_and_lead_accepted_reject_leader_as_substitute_peer_sender():
    for status in ("closed", "lead_accepted"):
        result = validate(write_fixture(
            status=status,
            extra_members=[_LEADER_MEMBER],
            record_overrides={
                "participants": [
                    {"label": "worker", "role": "implementer", "thread_id": "worker-thread"},
                    {"label": "reviewer", "role": "reviewer", "thread_id": "reviewer-thread"},
                    {"label": "leader", "role": "leader", "thread_id": "leader-thread"},
                ],
            },
            message_overrides=[
                {"recipients": ["reviewer"]},
                {"sender": "leader", "recipients": ["worker"], "kind": "challenge"},
                {"recipients": ["reviewer"]},
            ],
        ))
        assert not result["ok"], result
        assert (
            "discussion team/1/r1/implementation/task/d1 requires worker participant "
            "reviewer to send a peer message before decision_owner decision"
        ) in result["failures"], result


def test_closed_and_lead_accepted_reject_self_directed_peer_substitute():
    for status in ("closed", "lead_accepted"):
        result = validate(write_fixture(
            status=status,
            message_overrides=[
                {"recipients": ["reviewer"]},
                {"recipients": ["reviewer"]},
                {"recipients": ["reviewer"]},
            ],
        ))
        assert not result["ok"], result
        assert (
            "discussion team/1/r1/implementation/task/d1 requires worker participant "
            "reviewer to send a peer message before decision_owner decision"
        ) in result["failures"], result


def test_closed_discussion_rejects_silent_third_worker_participant():
    result = validate(write_fixture(
        extra_members=[{
            "label": "third",
            "role": "writer",
            "thread_id": "third-thread",
            "host_id": "host",
            "checkout_path": ".",
            "project_verified": True,
        }],
        record_overrides={
            "participants": [
                {"label": "worker", "role": "implementer", "thread_id": "worker-thread"},
                {"label": "reviewer", "role": "reviewer", "thread_id": "reviewer-thread"},
                {"label": "third", "role": "writer", "thread_id": "third-thread"},
            ],
        },
    ))
    assert not result["ok"], result
    assert (
        "discussion team/1/r1/implementation/task/d1 requires worker participant "
        "third to send a peer message before decision_owner decision"
    ) in result["failures"], result


def test_closed_and_lead_accepted_reject_lower_sequence_backfill_after_owner_decision():
    discussion_id = "team/1/r1/implementation/task/d1"
    for status in ("closed", "lead_accepted"):
        result = validate(write_fixture(
            status=status,
            message_overrides=[
                {"recipients": ["worker"]},
                {
                    "message_id": f"{discussion_id}/m3",
                    "sender": "worker",
                    "recipients": ["reviewer"],
                    "kind": "decision",
                    "sequence": 3,
                    "in_reply_to": f"{discussion_id}/m1",
                    "body": "Decide before peer reply.",
                },
                {
                    "message_id": f"{discussion_id}/m2",
                    "sender": "reviewer",
                    "recipients": ["worker"],
                    "kind": "response",
                    "sequence": 2,
                    "in_reply_to": f"{discussion_id}/m3",
                    "body": "Late peer reply.",
                },
            ],
        ))
        assert not result["ok"], result
        assert (
            "discussion team/1/r1/implementation/task/d1 requires a worker-to-worker "
            "non-decision message before decision_owner decision"
        ) in result["failures"], result


def test_closed_discussion_requires_two_participants():
    result = validate(write_fixture(
        record_overrides={
            "participants": [{"label": "worker", "role": "implementer", "thread_id": "worker-thread"}],
        },
        message_overrides=[
            {"recipients": ["worker"]},
            {"sender": "worker", "recipients": ["worker"]},
            {"recipients": ["worker"]},
        ],
    ))
    assert not result["ok"], result
    assert "discussion team/1/r1/implementation/task/d1 requires at least two participants" in result["failures"]


def test_closed_discussion_rejects_leader_as_decision_owner():
    result = validate(write_fixture(
        extra_members=[{
            "label": "leader",
            "role": "leader",
            "thread_id": "leader-thread",
            "host_id": "host",
            "checkout_path": ".",
            "project_verified": True,
        }],
        record_overrides={
            "participants": [
                {"label": "worker", "role": "implementer", "thread_id": "worker-thread"},
                {"label": "reviewer", "role": "reviewer", "thread_id": "reviewer-thread"},
                {"label": "leader", "role": "leader", "thread_id": "leader-thread"},
            ],
            "decision_owner": "leader",
        },
        message_overrides=[{}, {}, {"sender": "leader", "recipients": ["worker"]}],
        decision_overrides={
            "decision_owner": "leader",
            "decision_owner_thread_id": "leader-thread",
        },
    ))
    assert not result["ok"], result
    assert "discussion team/1/r1/implementation/task/d1 decision_owner must be a worker participant" in result["failures"]


def test_lead_acceptance_must_be_affirmative():
    for status in (None, "rejected"):
        result = validate(write_fixture(decision_overrides={
            "lead_acceptance": {"status": status, "thread_id": "leader-thread"}
        }))
        assert not result["ok"], result
        assert "discussion team/1/r1/implementation/task/d1 lead_acceptance status must be accepted" in result["failures"]


def test_present_discussion_policy_must_match_default_contract():
    result = validate(write_fixture(task_overrides={
        "discussion_policy": {"mode": "disabled", "max_rounds": 99}
    }, team_protocol_version=None, tasks_protocol_version=None))
    assert not result["ok"], result
    assert "task task discussion_policy must match the worker_can_request default" in result["failures"]


def test_new_work_task_requires_discussion_policy():
    result = validate(write_fixture(with_policy=False, discussions=[]))
    assert not result["ok"], result
    assert "task task missing discussion_policy for enabled current work/rework task" in result["failures"]


def test_null_task_kind_cannot_bypass_enabled_work_policy():
    result = validate(write_fixture(
        with_policy=False,
        discussions=[],
        task_overrides={"dispatch_kind": None},
    ))
    assert not result["ok"], result
    assert "task task missing discussion_policy for enabled current work/rework task" in result["failures"]


def test_discussion_protocol_marker_must_exist_in_both_ledgers():
    result = validate(write_fixture(tasks_protocol_version=None))
    assert not result["ok"], result
    assert "discussion_protocol_version must be present in both team.json and tasks.json" in result["failures"]


def test_discussion_protocol_markers_must_match():
    result = validate(write_fixture(tasks_protocol_version=2))
    assert not result["ok"], result
    assert "discussion_protocol_version mismatch between team.json and tasks.json" in result["failures"]


def test_discussion_protocol_marker_must_be_integer_one():
    result = validate(write_fixture(team_protocol_version="1", tasks_protocol_version="1"))
    assert not result["ok"], result
    assert "team.json discussion_protocol_version must be integer 1" in result["failures"]
    assert "tasks.json discussion_protocol_version must be integer 1" in result["failures"]


def test_present_discussion_index_must_match_task_identity():
    result = validate(write_fixture(task_overrides={"discussion_ids": ["garbage"]}))
    assert not result["ok"], result
    assert "task task discussion_ids entry garbage is invalid" in result["failures"]


def test_well_formed_discussion_index_must_match_task_identity():
    wrong_id = "team/1/r1/other/task/d1"
    result = validate(write_fixture(task_overrides={"discussion_ids": [wrong_id]}))
    assert not result["ok"], result
    assert f"task task discussion_ids entry {wrong_id} does not match task identity" in result["failures"]


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
