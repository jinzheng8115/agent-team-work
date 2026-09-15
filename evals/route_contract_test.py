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


def normalize_case_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


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
    for term in ("impact_analysis", ".team/revisions/<cycle>.md", "旧 cycle"):
        must(body, term, "post-completion entrypoint")

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
    for term in ("revision_cycle", "supersedes", "complete -> impact_analysis -> running -> complete", "active `revision_cycle`"):
        must(protocol, term, "revision protocol")
    capabilities = (ROOT / "references/role-capabilities.md").read_text(encoding="utf-8")
    must(capabilities, "PASS / MISSING / UNKNOWN", "capability gate")
    cases = json.loads((ROOT / "evals/trigger_cases.json").read_text(encoding="utf-8"))
    if sum(len(cases.get(bucket, [])) for bucket in ("should_trigger", "should_not_trigger", "near_neighbor")) < 23:
        raise AssertionError("trigger cases are too small")
    if len(cases.get("holdout", [])) < 19:
        raise AssertionError("holdout trigger cases are too small")
    holdout = json.loads((ROOT / "evals/holdout_cases.json").read_text(encoding="utf-8"))
    if len(holdout.get("should_trigger", [])) < 10 or len(holdout.get("should_not_trigger", [])) < 9:
        raise AssertionError("holdout fixture must contain ten positives and nine negatives")
    development_texts = {
        normalize_case_text(case["text"])
        for bucket in ("should_trigger", "should_not_trigger", "near_neighbor")
        for case in cases.get(bucket, [])
    }
    holdout_texts = {
        normalize_case_text(case["text"])
        for case in cases.get("holdout", [])
    } | {
        normalize_case_text(case["text"])
        for bucket in ("should_trigger", "should_not_trigger", "near_neighbor")
        for case in holdout.get(bucket, [])
    }
    overlapping_texts = development_texts & holdout_texts
    if overlapping_texts:
        raise AssertionError("trigger and holdout texts overlap: " + ", ".join(sorted(overlapping_texts)))
    evals = json.loads((ROOT / "evals/evals.json").read_text(encoding="utf-8"))
    eval_ids = {case.get("id") for case in evals.get("evals", [])}
    required_revision_ids = {
        "revision-impact-analysis",
        "revision-cross-stage-propagation",
        "revision-stales-dispatched-task",
        "revision-no-impact-no-dispatch",
    }
    missing_revision_ids = required_revision_ids - eval_ids
    if missing_revision_ids:
        raise AssertionError("missing revision eval IDs: " + ", ".join(sorted(missing_revision_ids)))
    if not (ROOT / "manifest.json").exists():
        raise AssertionError("manifest.json is required for the production package")
    if not (ROOT / "references" / "e2e-smoke-checklist.md").exists():
        raise AssertionError("e2e smoke checklist is required")
    print("GREEN: agent-team-work route/protocol contract validated")


if __name__ == "__main__":
    main()
