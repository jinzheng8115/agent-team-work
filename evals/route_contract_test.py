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


def must_any(text: str, needles: tuple[str, ...], where: str) -> None:
    if not any(needle in text for needle in needles):
        raise AssertionError(f"{where} missing one of {needles!r}")


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
    for excluded in ("普通子代理", "Orca team"):
        must(body, excluded, "entrypoint boundary")
    must_any(body, ("parallel worker", "并行 worker"), "entrypoint parallel-worker exclusion")
    must_any(
        body,
        ("autonomous stage dispatch", "自主阶段调度"),
        "entrypoint autonomous-stage-dispatch exclusion",
    )
    if "若已有授权覆盖" in body:
        raise AssertionError("entrypoint must not bypass the final team confirmation")
    for term in ("impact_analysis", ".team/revisions/<cycle>.md", "旧 cycle", "impact_result: no_affected_stages"):
        must(body, term, "post-completion entrypoint")

    workflow = (ROOT / "references/workflow.md").read_text(encoding="utf-8")
    for term in ("automatic", "confirmation", "ownership_epoch", "dispatch_key", "stale/duplicate", "attempt=0"):
        must(workflow, term, "workflow")
    for term in ("discussion_policy", "discussion_request", "decision_owner", "decision_status"):
        must(workflow, term, "discussion workflow")
    tools = (ROOT / "references/codex-tools.md").read_text(encoding="utf-8")
    if "request_user_input_async" in tools:
        raise AssertionError("references must not name unavailable request_user_input_async")
    for term in ("create_thread", "send_message_to_thread", "wait_threads", "projectId", "不证明成员已经读取"):
        must(tools, term, "Codex tools")
    for term in ("discussion_id", "messages.jsonl", "queued", "unknown"):
        must(tools, term, "discussion tools")
    protocol = (ROOT / "references/team-protocol.md").read_text(encoding="utf-8")
    for term in ("schema_version", "ownership_epoch", "ATW", "Capability", "reported` 不是 `accepted", "blocked"):
        must(protocol, term, "protocol")
    for term in ("last_writer_thread_id", "revision", "revision 已变化", "leader.thread_id"):
        must(protocol, term, "single-writer fence")
    for term in ("revision_cycle", "supersedes", "complete -> impact_analysis -> running -> complete",
                 "active `revision_cycle`", "impact_result: no_affected_stages"):
        must(protocol, term, "revision protocol")
    must(
        workflow + "\n" + protocol,
        "requested -> approved",
        "discussion protocol sources (state flow is published in workflow.md)",
    )
    for term in ("decision_pending", "lead_accepted", "worker_can_request"):
        must(protocol, term, "discussion protocol")
    migration = (ROOT / "docs/migration-v2.md").read_text(encoding="utf-8")
    must(migration, "impact_result: no_affected_stages", "schema-3 migration")
    capabilities = (ROOT / "references/role-capabilities.md").read_text(encoding="utf-8")
    must(capabilities, "PASS / MISSING / UNKNOWN", "capability gate")
    cases = json.loads((ROOT / "evals/trigger_cases.json").read_text(encoding="utf-8"))
    if sum(len(cases.get(bucket, [])) for bucket in ("should_trigger", "should_not_trigger", "near_neighbor")) < 23:
        raise AssertionError("trigger cases are too small")
    if len(cases.get("holdout", [])) < 19:
        raise AssertionError("holdout trigger cases are too small")
    discussion_development_cases = [
        case for case in cases.get("should_trigger", []) if case.get("family") == "discussion"
    ]
    if len(discussion_development_cases) < 6:
        raise AssertionError("development fixture must contain six discussion positives")
    negative_family_counts = {
        family: sum(case.get("family") == family for case in cases.get("should_not_trigger", []))
        for family in ("implementation", "clarification", "blocked", "status", "one-off-edit")
    }
    required_negative_family_counts = {
        "implementation": 2,
        "clarification": 1,
        "blocked": 1,
        "status": 1,
        "one-off-edit": 1,
    }
    if any(
        negative_family_counts[family] < count
        for family, count in required_negative_family_counts.items()
    ):
        raise AssertionError("development fixture must contain six discussion negative scenarios")
    if any(
        case.get("family") == "discussion"
        for bucket in ("should_not_trigger", "near_neighbor", "holdout")
        for case in cases.get(bucket, [])
    ):
        raise AssertionError("family discussion is reserved for development positives")
    holdout = json.loads((ROOT / "evals/holdout_cases.json").read_text(encoding="utf-8"))
    if len(holdout.get("should_trigger", [])) < 14 or len(holdout.get("should_not_trigger", [])) < 13:
        raise AssertionError("holdout fixture must contain fourteen positives and thirteen negatives")
    if sum(case.get("family") == "discussion" for case in holdout.get("should_trigger", [])) < 4:
        raise AssertionError("holdout fixture must contain four discussion positives")
    if any(case.get("family") == "discussion" for case in holdout.get("should_not_trigger", [])):
        raise AssertionError("family discussion is reserved for positive holdout cases")
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
    required_discussion_ids = {
        "discussion-triage-hard-trigger",
        "discussion-triage-soft-threshold",
        "discussion-clarification-not-discussion",
        "discussion-lead-approval",
        "discussion-decision-owner",
        "discussion-timeout-escalation",
        "discussion-stale-message",
    }
    missing_discussion_ids = required_discussion_ids - eval_ids
    if missing_discussion_ids:
        raise AssertionError("missing discussion eval IDs: " + ", ".join(sorted(missing_discussion_ids)))
    evals_by_id = {case["id"]: case for case in evals.get("evals", [])}
    required_discussion_assertions = {
        "discussion-triage-hard-trigger": {
            "worker_requests_instead_of_opens", "does_not_dispatch_next_stage",
        },
        "discussion-triage-soft-threshold": {
            "counts_soft_triggers", "worker_requests_at_threshold", "does_not_dispatch_next_stage",
        },
        "discussion-clarification-not-discussion": {
            "does_not_request_discussion", "does_not_dispatch_next_stage",
        },
        "discussion-lead-approval": {
            "lead_selects_participants", "lead_assigns_decision_owner", "does_not_dispatch_next_stage",
        },
        "discussion-decision-owner": {
            "requires_peer_visible_worker_exchange", "owner_records_decision",
            "lead_accepts_before_resume", "does_not_dispatch_next_stage",
        },
        "discussion-timeout-escalation": {
            "blocks_or_escalates", "does_not_dispatch_next_stage",
        },
        "discussion-stale-message": {
            "records_post_close_message_as_stale", "does_not_dispatch_next_stage",
        },
    }
    for case_id, required_assertions in required_discussion_assertions.items():
        case = evals_by_id[case_id]
        if not case.get("expected_output"):
            raise AssertionError(f"discussion eval {case_id} missing expected_output")
        missing_assertions = required_assertions - set(case.get("assertions", []))
        if missing_assertions:
            raise AssertionError(
                f"discussion eval {case_id} missing assertions: "
                + ", ".join(sorted(missing_assertions))
            )
    output_cases = {
        case["id"]: case
        for line in (ROOT / "evals/output/cases.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
        for case in (json.loads(line),)
    }
    missing_output_ids = required_discussion_ids - output_cases.keys()
    if missing_output_ids:
        raise AssertionError("missing discussion output IDs: " + ", ".join(sorted(missing_output_ids)))
    required_output_phrases = {
        "discussion-triage-hard-trigger": ("worker submits a discussion_request",),
        "discussion-lead-approval": ("Lead approves", "does not dispatch the next stage"),
        "discussion-decision-owner": (
            "two worker participants exchange peer-visible", "directly with each other",
            "worker decision_owner", "Lead acceptance", "does not dispatch the next stage",
        ),
    }
    for case_id, phrases in required_output_phrases.items():
        for phrase in phrases:
            must(output_cases[case_id].get("with_skill_output", ""), phrase, f"output case {case_id}")
    for case_id in required_discussion_ids:
        output = output_cases[case_id].get("with_skill_output", "")
        for assertion in output_cases[case_id].get("assertions", []):
            for phrase in assertion.get("required", []):
                must(output, phrase, f"output case {case_id} assertion {assertion.get('id')}")
    smoke = (ROOT / "references/e2e-smoke-checklist.md").read_text(encoding="utf-8")
    for term in (
        "discussion_request", "participant", "decision_owner", "Lead acceptance",
        "peer message", "stale", "timeout", "blocked",
    ):
        must(smoke, term, "discussion smoke checklist")
    if not (ROOT / "manifest.json").exists():
        raise AssertionError("manifest.json is required for the production package")
    if not (ROOT / "references" / "e2e-smoke-checklist.md").exists():
        raise AssertionError("e2e smoke checklist is required")
    print("GREEN: agent-team-work route/protocol contract validated")


if __name__ == "__main__":
    main()
