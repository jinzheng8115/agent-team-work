#!/usr/bin/env python3
"""Regression fixtures for revision-aware team ledger validation."""

import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_team_state import validate


_FIXTURES: list[Path] = []


def write_fixture(*, schema_version: int, team_status: str, cycle: int,
                  revision_record: bool = True,
                  revision_tasks: str = "accepted") -> Path:
    """Create and return a temporary .team directory for one validator case."""
    team_dir = Path(tempfile.mkdtemp())
    _FIXTURES.append(team_dir)
    team = {
        "schema_version": schema_version,
        "skill": "agent-team-work",
        "team_id": "team",
        "project_id": "project",
        "project_root": str(team_dir),
        "status": team_status,
        "ownership_epoch": 1,
        "revision_cycle": cycle,
        "leader": {"thread_id": "leader", "host_id": "host", "title": "Leader"},
        "members": [{
            "label": "worker", "role": "worker", "thread_id": "worker",
            "host_id": "host", "checkout_path": str(team_dir), "project_verified": True,
        }],
    }
    tasks = []

    def task(task_id: str, task_cycle: int, status: str, key: str,
             *, supersedes: list[str] | None = None) -> dict:
        value = {
            "task_id": task_id,
            "attempt": 1,
            "revision_cycle": task_cycle,
            "status": status,
            "dispatch_state": "accepted" if status == "accepted" else "stale",
            "dispatch_key": key,
            "supersedes": supersedes or [],
            "impact_basis": "requested revision" if task_cycle > 1 else "initial delivery",
        }
        if status == "accepted":
            value["acceptance"] = {"status": "accepted", "evidence": ["reports/evidence.md"]}
        return value

    current_key = "team/1/stage/1/work" if cycle == 1 else "team/1/r2/stage/1/work"
    if revision_tasks == "old-cycle-accepted":
        tasks.append(task("old", 1, "accepted", "team/1/stage/1/work"))
        tasks.append(task("current", 2, "accepted", "team/1/r2/stage/1/work"))
    elif revision_tasks == "stale-without-superseder":
        tasks.append(task("stale", cycle, "stale", current_key))
    elif revision_tasks == "planned":
        tasks.append(task("current", cycle, "planned", current_key))
    elif revision_tasks == "wrong-cycle-key":
        tasks.append(task("current", cycle, "accepted", "team/1/stage/1/work"))
    else:
        tasks.append(task("current", cycle, "accepted", current_key))

    tasks_payload = {
        "schema_version": schema_version,
        "team_id": "team",
        "revision": 1,
        "revision_cycle": cycle,
        "last_writer_thread_id": "leader",
        "tasks": tasks,
    }
    (team_dir / "team.json").write_text(json.dumps(team), encoding="utf-8")
    (team_dir / "tasks.json").write_text(json.dumps(tasks_payload), encoding="utf-8")
    if revision_record:
        revisions = team_dir / "revisions"
        revisions.mkdir()
        (revisions / f"{cycle}.md").write_text("impact analysis", encoding="utf-8")
    return team_dir


def test_valid_legacy_cycle_one():
    result = validate(write_fixture(schema_version=2, team_status="complete", cycle=1))
    assert result["ok"], result


def test_valid_scoped_revision():
    result = validate(write_fixture(schema_version=3, team_status="complete", cycle=2,
                                   revision_record=True, revision_tasks="accepted"))
    assert result["ok"], result


def test_revision_requires_impact_record():
    result = validate(write_fixture(schema_version=3, team_status="running", cycle=2,
                                   revision_record=False, revision_tasks="planned"))
    assert "revision record" in " ".join(result["failures"])


def test_old_cycle_cannot_advance_current_cycle():
    result = validate(write_fixture(schema_version=3, team_status="complete", cycle=2,
                                   revision_record=True, revision_tasks="old-cycle-accepted"))
    assert "current cycle" in " ".join(result["failures"])


def test_stale_task_needs_accepted_superseder():
    result = validate(write_fixture(schema_version=3, team_status="complete", cycle=2,
                                   revision_record=True, revision_tasks="stale-without-superseder"))
    assert "supersed" in " ".join(result["failures"])


def test_revision_dispatch_key_is_cycle_bound():
    result = validate(write_fixture(schema_version=3, team_status="running", cycle=2,
                                   revision_record=True, revision_tasks="wrong-cycle-key"))
    assert "revision" in " ".join(result["failures"])


def main() -> int:
    tests = [value for name, value in globals().items() if name.startswith("test_")]
    try:
        for test in tests:
            test()
    finally:
        for fixture in _FIXTURES:
            shutil.rmtree(fixture, ignore_errors=True)
    print(f"PASS revision-cycle-state ({len(tests)} tests)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
