#!/usr/bin/env python3
"""Static route and protocol guard; does not call Codex or create sessions."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def must(text: str, needle: str, where: str) -> None:
    if needle not in text:
        raise AssertionError(f"{where} missing {needle!r}")


def main() -> None:
    entry = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    front = entry.split("---", 2)
    if len(front) != 3 or front[0].strip():
        raise AssertionError("SKILL.md must have frontmatter")
    must(front[1], "name: agent-team-work", "frontmatter")
    description = re.search(r"^description:\s*(.+)$", front[1], re.MULTILINE)
    if not description or len(description.group(1)) > 700:
        raise AssertionError("description missing or too broad")
    body = front[2]
    for ref in ("references/workflow.md", "references/codex-tools.md", "references/team-protocol.md", "references/role-presets.md"):
        must(body, ref, "entrypoint")
    for excluded in ("普通子代理", "并行 worker", "Orca team"):
        must(body, excluded, "entrypoint boundary")
    if "若已有授权覆盖" in body:
        raise AssertionError("entrypoint must not bypass the final team confirmation")

    workflow = (ROOT / "references/workflow.md").read_text(encoding="utf-8")
    for term in ("automatic", "confirmation", "ownership_epoch", "dispatch_key", "stale/duplicate", "attempt=0"):
        must(workflow, term, "workflow")
    tools = (ROOT / "references/codex-tools.md").read_text(encoding="utf-8")
    if "request_user_input_async" in tools:
        raise AssertionError("references must not name unavailable request_user_input_async")
    for term in ("create_thread", "send_message_to_thread", "wait_threads", "projectId", "不证明成员已经读取"):
        must(tools, term, "Codex tools")
    protocol = (ROOT / "references/team-protocol.md").read_text(encoding="utf-8")
    for term in ("schema_version", "ownership_epoch", "ATW", "Capability", "reported` 不是 `accepted", "blocked"):
        must(protocol, term, "protocol")
    for term in ("last_writer_thread_id", "revision", "revision 已变化", "leader.thread_id"):
        must(protocol, term, "single-writer fence")
    capabilities = (ROOT / "references/role-capabilities.md").read_text(encoding="utf-8")
    must(capabilities, "PASS / MISSING / UNKNOWN", "capability gate")
    cases = json.loads((ROOT / "evals/trigger_cases.json").read_text(encoding="utf-8"))
    if sum(len(cases.get(bucket, [])) for bucket in ("should_trigger", "should_not_trigger", "near_neighbor")) < 16:
        raise AssertionError("trigger cases are too small")
    if len(cases.get("holdout", [])) < 12:
        raise AssertionError("holdout trigger cases are too small")
    holdout = json.loads((ROOT / "evals/holdout_cases.json").read_text(encoding="utf-8"))
    if len(holdout.get("should_trigger", [])) < 6 or len(holdout.get("should_not_trigger", [])) < 6:
        raise AssertionError("holdout fixture must contain six positives and six negatives")
    if not (ROOT / "manifest.json").exists():
        raise AssertionError("manifest.json is required for the production package")
    if not (ROOT / "references" / "e2e-smoke-checklist.md").exists():
        raise AssertionError("e2e smoke checklist is required")
    print("GREEN: agent-team-work route/protocol contract validated")


if __name__ == "__main__":
    main()
