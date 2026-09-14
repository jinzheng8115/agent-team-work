#!/usr/bin/env python3
"""Validate and emit metadata-only telemetry events without network or file writes."""

SCRIPT_INTERFACE = "cli"
SCRIPT_INTERFACE_REASON = "Validates local JSONL telemetry and emits sanitized metadata events to stdout; the caller owns any local spool redirect."

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ALLOWED_EVENTS = {"skill_activation", "skill_output", "script_run", "review_event"}
ALLOWED_ACTIVATION_TYPES = {"implicit", "explicit", "manual", "unknown"}
ALLOWED_OUTCOMES = {"accepted", "edited", "rejected", "missed", "failed", "reviewed", "unknown"}
ALLOWED_FAILURE_TYPES = {
    "none",
    "wrong_trigger",
    "under_trigger",
    "bad_output",
    "missing_resource",
    "script_error",
    "review_overdue",
}
ALLOWED_SOURCES = {"manual", "yao_cli", "external", "unknown"}
ALLOWED_FIELDS = {
    "command",
    "event",
    "skill",
    "source",
    "version",
    "activation_type",
    "outcome",
    "failure_type",
    "timestamp",
}
SENSITIVE_FIELDS = {
    "prompt",
    "content",
    "input",
    "inputs",
    "output",
    "outputs",
    "transcript",
    "message",
    "messages",
    "note",
    "text",
    "raw",
}


def normalize(raw: dict[str, Any], line_number: int) -> tuple[dict[str, str] | None, list[str]]:
    label = f"line {line_number}"
    failures: list[str] = []
    sensitive = sorted(set(raw) & SENSITIVE_FIELDS)
    unknown = sorted(set(raw) - ALLOWED_FIELDS - SENSITIVE_FIELDS)
    if sensitive:
        failures.append(f"{label}: raw content fields are blocked: {', '.join(sensitive)}")
    if unknown:
        failures.append(f"{label}: unknown fields are blocked: {', '.join(unknown)}")

    event = {
        "command": str(raw.get("command") or "unknown"),
        "event": str(raw.get("event") or "skill_activation"),
        "skill": str(raw.get("skill") or "agent-team-work"),
        "source": str(raw.get("source") or "external"),
        "version": str(raw.get("version") or "0.2.0"),
        "activation_type": str(raw.get("activation_type") or "unknown"),
        "outcome": str(raw.get("outcome") or "unknown"),
        "failure_type": str(raw.get("failure_type") or "none"),
        "timestamp": str(raw.get("timestamp") or ""),
    }
    if event["event"] not in ALLOWED_EVENTS:
        failures.append(f"{label}: unsupported event {event['event']!r}")
    if event["activation_type"] not in ALLOWED_ACTIVATION_TYPES:
        failures.append(f"{label}: unsupported activation_type {event['activation_type']!r}")
    if event["outcome"] not in ALLOWED_OUTCOMES:
        failures.append(f"{label}: unsupported outcome {event['outcome']!r}")
    if event["failure_type"] not in ALLOWED_FAILURE_TYPES:
        failures.append(f"{label}: unsupported failure_type {event['failure_type']!r}")
    if event["source"] not in ALLOWED_SOURCES:
        failures.append(f"{label}: unsupported source {event['source']!r}")
    command = event["command"]
    if not command.replace("-", "").replace("_", "").isalnum() or len(command) > 64:
        failures.append(f"{label}: command must use letters, numbers, hyphens, or underscores and stay under 64 chars")
    if event["timestamp"]:
        try:
            datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            failures.append(f"{label}: timestamp must be ISO-8601")
    else:
        event["timestamp"] = datetime.now().astimezone().isoformat(timespec="seconds")
    return (event if not failures else None), failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate local JSONL telemetry and emit sanitized metadata-only events to stdout."
    )
    parser.add_argument("--input-jsonl", required=True, help="Input JSONL containing metadata-only event objects.")
    args = parser.parse_args()
    path = Path(args.input_jsonl).expanduser()
    if not path.exists():
        print(json.dumps({"ok": False, "failures": [f"input does not exist: {path}"]}, ensure_ascii=False), file=sys.stderr)
        return 2
    failures: list[str] = []
    events: list[dict[str, str]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            failures.append(f"line {number}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(raw, dict):
            failures.append(f"line {number}: event must be a JSON object")
            continue
        event, event_failures = normalize(raw, number)
        failures.extend(event_failures)
        if event:
            events.append(event)
    if failures:
        print(json.dumps({"ok": False, "accepted_count": len(events), "failures": failures}, ensure_ascii=False), file=sys.stderr)
        return 2
    for event in events:
        print(json.dumps(event, ensure_ascii=False, sort_keys=True))
    print(json.dumps({"ok": True, "accepted_count": len(events), "failures": []}, ensure_ascii=False), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
