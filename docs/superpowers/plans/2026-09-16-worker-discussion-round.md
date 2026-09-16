# Worker-to-worker discussion round Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a bounded, auditable worker-to-worker discussion protocol in which workers can request and conduct a decision round, one worker can decide the content, and the Lead remains responsible for workflow acceptance and progression.

**Architecture:** Extend the prompt/protocol contract with a worker-side decision triage gate and a request-then-approval discussion lifecycle. Store discussion identity and evidence separately from the existing two ledgers, validate optional discussion records read-only, and keep discussion activity inside the current stage without enabling parallel delivery or autonomous dispatch.

**Tech Stack:** Markdown skill/reference files, Python 3 standard library validator and regression fixtures, JSON/JSONL evaluation fixtures, existing dependency-free CI and runtime-package scripts.

## Global Constraints

- Default new-task policy is `mode: worker_can_request`, `soft_trigger_threshold: 2`, `max_rounds: 2`, and a Lead-defined deadline.
- A worker may request a discussion but cannot unilaterally open or close one, write `team.json`/`tasks.json`, accept a task, or dispatch a later stage.
- Discussion is limited to the current active stage and is not parallel project execution; existing serial dispatch, dependency, capability, and Lead-acceptance gates remain authoritative.
- Hard triggers open a request immediately; two soft triggers open a request; one soft trigger becomes a recorded assumption or a Lead clarification.
- Missing tools, paths, permissions, or required inputs are `blocked` unless resolving them requires a cross-role decision.
- Discussion identity is bound to `team_id`, `ownership_epoch`, `revision_cycle`, `stage`, `task_id`, and `dispatch_key`; mismatches are stale and cannot advance work.
- Existing teams and tasks without `discussion_policy` continue the current serial workflow unchanged.
- Preserve the unrelated untracked `dist/agent-team-work/` directory and do not regenerate or commit it unless an explicit packaging step produces a required artifact.

---

## File map

- `SKILL.md`: expose the discussion boundary and route runtime users to the protocol references.
- `references/workflow.md`: document worker triage, request approval, lifecycle, decision ownership, and stage handoff.
- `references/team-protocol.md`: define optional task policy, discussion records, message identity, states, storage paths, and stale/duplicate rules.
- `references/codex-tools.md`: define how peer messages are sent through existing thread tools, including busy/queued/unknown semantics and safe retry rules.
- `references/role-capabilities.md`: add the read-only decision-triage step and required report field.
- `examples/serial-pipeline.md`: show a discussion inside a serial stage without starting the next stage early.
- `README.md`: add the feature to the user-facing scope and limitation summary.
- `docs/migration-v2.md`: state legacy compatibility and the opt-in/default policy for new tasks.
- `scripts/validate_team_state.py`: validate optional discussion records and identity-bound messages without mutating `.team`.
- `evals/discussion_round_state_test.py`: provide isolated temporary-ledger tests for discussion state and evidence rules.
- `scripts/ci_test.py`: run the discussion-state regression target with the existing dependency-free checks.
- `evals/route_contract_test.py`: require the new protocol terms and routing boundaries.
- `evals/trigger_cases.json`: add development examples for discussion-trigger and no-trigger requests.
- `evals/holdout_cases.json`: add unseen positive and negative discussion cases without overlapping development text.
- `evals/evals.json`: add behavior contracts for triage, approval, decision ownership, timeout, and stale messages.
- `evals/output/cases.jsonl`: add expected model-output examples for the new behavior contracts.
- `references/e2e-smoke-checklist.md`: add a manual discussion-round evidence scenario.

## Interfaces between tasks

The runtime contract introduced by the plan uses these exact shapes:

```text
discussion_policy:
  mode: worker_can_request
  soft_trigger_threshold: 2
  max_rounds: 2
  deadline: Lead-defined

discussion_id:
  {team_id}/{ownership_epoch}/r{revision_cycle}/{stage}/{task_id}/d{sequence}

discussion record path:
  .team/discussions/{task_id}/d{sequence}/record.json

message transcript path:
  .team/discussions/{task_id}/d{sequence}/messages.jsonl

decision path:
  .team/discussions/{task_id}/d{sequence}/decision.json
```

The record uses statuses `requested`, `approved`, `open`, `proposing`,
`challenging`, `decision_pending`, `decided`, `lead_accepted`, `closed`,
`rejected`, `blocked`, `expired`, and `cancelled`. Each message uses one of
`proposal`, `challenge`, `evidence`, `response`, or `decision`.

---

### Task 1: Publish the discussion protocol in the runtime skill

**Files:**
- Modify: `SKILL.md`
- Modify: `references/workflow.md`
- Modify: `references/team-protocol.md`
- Modify: `references/codex-tools.md`
- Modify: `references/role-capabilities.md`
- Modify: `examples/serial-pipeline.md`
- Modify: `README.md`
- Modify: `docs/migration-v2.md`

**Interfaces:**
- Consumes: the approved discussion-round design in `docs/superpowers/specs/2026-09-16-worker-discussion-round-design.md` and the existing Lead-only ledger/serial-gating contract.
- Produces: runtime instructions containing `discussion_policy`, `discussion_request`, `decision_status`, `decision_owner`, the state lifecycle, and the exact identity/path contract in the File map.

- [ ] **Step 1: Add the routing boundary to `SKILL.md`.**

  Add worker-to-worker discussion as an in-stage, request-only capability. Keep the existing exclusions for parallel workers, Orca teams, Sub-Leads, and autonomous stage dispatch. Link the new protocol sections from the existing entrypoint references.

- [ ] **Step 2: Add triage and trigger rules to `references/workflow.md`.**

  Add a `Decision triage` subsection after capability-gate guidance with this decision tree and trigger counts:

  ```text
  Can I complete the task with the current requirements and accepted inputs?
  yes -> proceed and record non-blocking assumptions
  no + one missing fact/input/permission -> ask Lead or return blocked
  no + cross-role options/conflict/high-impact choice -> discussion_request
  ```

  State that hard triggers require a request, two soft triggers require a request, one soft trigger is not enough, and triage runs at task start, before irreversible work, after a changed assumption, and before a cross-role decision is finalized.

- [ ] **Step 3: Add the request/approval lifecycle to `references/workflow.md`.**

  Document `requested -> approved -> open -> proposing/challenging -> decision_pending -> decided -> lead_accepted -> closed`, the terminal states, worker/decision-owner/Lead responsibilities, the two-round default, deadline escalation, and the rule that discussion never creates a later delivery stage.

- [ ] **Step 4: Add the record and message contract to `references/team-protocol.md`.**

  Document the optional `discussion_policy`, the slash-delimited `discussion_id`, the three file paths, record fields, message fields, allowed statuses/kinds, identity matching, optional task `discussion_ids`, and stale/duplicate behavior. Preserve the existing two JSON ledgers as Lead-only writers; discussion messages must not mutate them.

- [ ] **Step 5: Add tool and recovery semantics to `references/codex-tools.md`.**

  Explain that peer messages use the existing real worker thread IDs only after the Lead has approved a discussion, carry the discussion identity on every message, and are persisted by the discussion transcript path. Explicitly retain the existing rule that `queued`, `resumed`, or `already-active` proves only host acceptance; before retrying a peer message, query the record and thread history and mark uncertain delivery `unknown`.

- [ ] **Step 6: Add the worker capability/report contract to `references/role-capabilities.md`.**

  Require the worker to return `decision_status: clear | assumption | unresolved` in every discussion-enabled result and to pause only decision-dependent work. Keep the existing `PASS / MISSING / UNKNOWN + evidence` capability gate before project modifications.

- [ ] **Step 7: Update the example, README, and migration notes.**

  Add one serial example in `examples/serial-pipeline.md` where a backend worker requests a frontend/backend API discussion, a designated worker decides, the Lead records acceptance, and only then the next stage is dispatched. Add the feature and its limitations to `README.md`. In `docs/migration-v2.md`, state that legacy tasks without `discussion_policy` retain current behavior and new tasks default to `worker_can_request`.

- [ ] **Step 8: Run the documentation contract checks.**

  Run:

  ```bash
  python3 evals/route_contract_test.py
  ```

  Expected result before Task 3's route assertions are added: the existing checks pass; any new terms should be added to the route test in Task 3 before final integration.

- [ ] **Step 9: Commit the runtime protocol changes.**

  ```bash
  git add SKILL.md references/workflow.md references/team-protocol.md \
    references/codex-tools.md references/role-capabilities.md \
    examples/serial-pipeline.md README.md docs/migration-v2.md
  git commit -m "docs: define worker discussion protocol"
  ```

### Task 2: Validate discussion records and message evidence

**Files:**
- Modify: `scripts/validate_team_state.py`
- Modify: `scripts/ci_test.py`
- Create: `evals/discussion_round_state_test.py`

**Interfaces:**
- Consumes: optional `.team/discussions/{task_id}/d{sequence}/record.json`, `messages.jsonl`, and `decision.json` records described in Task 1.
- Produces: `parse_discussion_key(key: str) -> dict | None`, `validate_discussion_record(team_dir: Path, team: dict, tasks_by_id: dict, record: dict, failures: list[str]) -> None`, and a `discussion-state` CI target.

- [ ] **Step 1: Write failing discussion fixture tests.**

  In `evals/discussion_round_state_test.py`, create a `write_fixture()` helper using `tempfile.mkdtemp()` and a cleanup list. Give it keyword arguments `status="closed"`, `with_policy=True`, `discussions=["d1"]`, `statuses=None`, `record_overrides=None`, `message_overrides=None`, `decision_overrides=None`, and `task_status="reported"`. Generate a valid schema-3 team, one current task, and discussion files under the exact paths from the Interfaces section. Add these tests before changing the validator:

  ```python
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
  ```

  The valid fixture must include a `record.json` in `closed`, two identity-matching messages, and a `decision.json` with `chosen_option`, `rationale`, `evidence`, `rejected_alternatives`, `affected_tasks`, `decision_owner`, and `lead_acceptance`.

- [ ] **Step 2: Run the new tests to confirm they fail for the missing validator behavior.**

  ```bash
  python3 evals/discussion_round_state_test.py
  ```

  Expected result: the new tests fail because `validate()` does not yet inspect discussion records; existing revision tests remain runnable.

- [ ] **Step 3: Add discussion constants and key parsing.**

  In `scripts/validate_team_state.py`, add:

  ```python
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

  def parse_discussion_key(key: str) -> dict | None:
      match = DISCUSSION_KEY.match(key)
      if not match:
          return None
      data = match.groupdict()
      data["epoch"] = int(data["epoch"])
      data["cycle"] = int(data["cycle"])
      data["sequence"] = int(data["sequence"])
      return data
  ```

  Return numeric `epoch`, `cycle`, and `sequence`, and reject malformed keys without raising.

- [ ] **Step 4: Implement record validation.**

  Add `validate_discussion_record(team_dir, team, tasks_by_id, record, failures)` and call it from `validate()` after tasks are indexed. It must:

  ```text
  - require record identity, status, question, participants, decision_owner,
    max_rounds, deadline, and transcript_path;
  - require the parsed discussion key to match team, epoch, active cycle,
    stage, and task_id/dispatch_key;
  - require every participant label to exist in team.members and decision_owner
    to be one of those labels;
  - validate each messages.jsonl line as an object with unique sequence,
    matching discussion_id, known sender/recipient labels, and allowed kind;
  - require decision.json for decided/lead_accepted/closed records;
  - require chosen_option, rationale, evidence, rejected_alternatives,
    affected_tasks, decision_owner, and lead_acceptance for closed records;
  - reject a closed or lead_accepted record whose decision owner or Lead
    acceptance identity does not match the team/member bindings;
  - mark mismatched or duplicate records as failures with structured messages;
  - allow no discussion files when a legacy task has no discussion_policy.
  ```

  Keep validation read-only and preserve the existing complete-team, revision-cycle, dispatch-key, and single-writer checks.

- [ ] **Step 5: Add the CI target.**

  In `scripts/ci_test.py`, add `discussion-state` to `DEFAULT_TARGETS`, define:

  ```python
  def discussion_state() -> None:
      result = subprocess.run(
          [sys.executable, str(ROOT / "evals" / "discussion_round_state_test.py")],
          cwd=ROOT,
          check=False,
      )
      if result.returncode:
          raise AssertionError("discussion-round-state regression tests failed")
  ```

  Register it in `CHECKS` without changing the existing target names.

- [ ] **Step 6: Run focused tests and the existing revision tests.**

  ```bash
  python3 evals/discussion_round_state_test.py
  python3 evals/revision_cycle_state_test.py
  python3 scripts/ci_test.py python-compile discussion-state revision-state
  ```

  Expected result: all focused tests pass and legacy revision fixtures remain unchanged.

- [ ] **Step 7: Commit validator and fixture changes.**

  ```bash
  git add scripts/validate_team_state.py scripts/ci_test.py \
    evals/discussion_round_state_test.py
  git commit -m "feat: validate worker discussion rounds"
  ```

### Task 3: Add routing, trigger, and behavior evaluation coverage

**Files:**
- Modify: `evals/route_contract_test.py`
- Modify: `evals/trigger_cases.json`
- Modify: `evals/holdout_cases.json`
- Modify: `evals/evals.json`
- Modify: `evals/output/cases.jsonl`
- Modify: `references/e2e-smoke-checklist.md`

**Interfaces:**
- Consumes: runtime terms and state names published by Task 1 and the validator contract from Task 2.
- Produces: static routing guards and behavior fixtures proving that discussion requests are bounded, approved, decision-owned, and never mistaken for stage dispatch.

- [ ] **Step 1: Add development trigger cases.**

  Add at least six `should_trigger` cases to `evals/trigger_cases.json` covering an unresolved API contract, conflicting reports, two viable architecture options, a high-risk release decision, a changed assumption with downstream impact, and a worker asking for a discussion. Add at least six `should_not_trigger` cases covering a single-option implementation, a one-fact clarification, missing tool/input blocking, a progress report, a typo fix, and an already-decided implementation. Use a new `family: "discussion"` only for the discussion positives.

- [ ] **Step 2: Add unseen holdout cases without text overlap.**

  Add four positive and four negative Chinese holdout prompts to `evals/holdout_cases.json`. Keep their normalized text distinct from all development cases so the existing overlap guard remains meaningful.

- [ ] **Step 3: Extend route-contract assertions.**

  In `evals/route_contract_test.py`, require these terms in the appropriate files:

  ```python
  for term in ("discussion_policy", "discussion_request", "decision_owner", "decision_status"):
      must(workflow, term, "discussion workflow")
  for term in ("requested -> approved", "decision_pending", "lead_accepted", "worker_can_request"):
      must(protocol, term, "discussion protocol")
  for term in ("discussion_id", "messages.jsonl", "queued", "unknown"):
      must(tools, term, "discussion tools")
  ```

  Also assert that `SKILL.md` retains the exclusions `parallel worker` and `autonomous stage dispatch` after the new routing text is added.

- [ ] **Step 4: Add behavior contracts to `evals/evals.json`.**

  Add these IDs with expected outputs and assertion names:

  ```text
  discussion-triage-hard-trigger
  discussion-triage-soft-threshold
  discussion-clarification-not-discussion
  discussion-lead-approval
  discussion-decision-owner
  discussion-timeout-escalation
  discussion-stale-message
  ```

  Assert that a worker requests rather than opens a discussion, that the Lead chooses participants and owner, that the decision is recorded before resuming work, and that no discussion dispatches a later stage.

- [ ] **Step 5: Add model-output examples.**

  Append matching JSONL cases to `evals/output/cases.jsonl`. Each `with_skill_output` must contain the exact behavioral phrases used by the assertions, including “worker submits a discussion_request”, “Lead approves”, “decision_owner”, “Lead acceptance”, and “does not dispatch the next stage”.

- [ ] **Step 6: Add a manual smoke scenario.**

  Add a section to `references/e2e-smoke-checklist.md` that records one real discussion request, the approved participant thread IDs, two peer messages, the decision-owner result, Lead acceptance, and proof that the next stage was not sent before acceptance. Include checks for a stale post-close message and a timeout/block path.

- [ ] **Step 7: Run evaluation and route checks.**

  ```bash
  python3 evals/route_contract_test.py
  python3 scripts/ci_test.py route-contract python-compile discussion-state revision-state
  ```

  Expected result: route checks pass, development and holdout trigger texts do not overlap, and all state fixtures remain green.

- [ ] **Step 8: Commit evaluation coverage.**

  ```bash
  git add evals/route_contract_test.py evals/trigger_cases.json \
    evals/holdout_cases.json evals/evals.json evals/output/cases.jsonl \
    references/e2e-smoke-checklist.md
  git commit -m "test: cover worker discussion routing"
  ```

### Task 4: Build the package and complete release verification

**Files:**
- Modify: generated package/evidence files produced by the existing release commands only (`dist/`, `reports/`); do not hand-edit generated outputs.
- Test: `scripts/ci_test.py`, `scripts/validate_team_state.py`, `evals/discussion_round_state_test.py`

**Interfaces:**
- Consumes: all source/docs/tests from Tasks 1–3.
- Produces: a runtime package containing the updated entrypoint and references, passing dependency-free checks, refreshed release evidence, and a clean diff that excludes unrelated workspace artifacts.

- [ ] **Step 1: Run the complete local test set.**

  ```bash
  python3 scripts/ci_test.py
  python3 evals/discussion_round_state_test.py
  python3 evals/revision_cycle_state_test.py
  ```

  Expected result: every named CI check prints `PASS` and both state-test scripts print their test counts with `PASS`.

- [ ] **Step 2: Rebuild and inspect the runtime-only package.**

  ```bash
  python3 scripts/build_runtime_package.py . --package-dir dist --output-json reports/runtime_package.json
  python3 scripts/runtime_package_check.py . --package-dir dist \
    --output-json reports/install_simulation.json \
    --output-md reports/install_simulation.md
  ```

  Verify the archive contains `SKILL.md`, `references/workflow.md`, `references/team-protocol.md`, `references/codex-tools.md`, and `references/role-capabilities.md`, and does not contain `evals/`, `scripts/`, or raw transcripts.

- [ ] **Step 3: Refresh required release evidence.**

  Run the canonical evidence command block in `agent-team-work/AGENTS.md` with:

  ```bash
  YAO_ENGINE="${YAO_ENGINE:-/Users/jinzheng/.skills-manager/skills/yao-meta-skill/scripts}"
  GENERATED_AT="${GENERATED_AT:-$(date +%F)}"
  ```

  Use the listed `compile_skill.py`, `cross_packager.py`, trust, package-verification, registry, compatibility, and report-render commands exactly as documented. Do not substitute `scripts/local_output_eval_runner.py` for the immutable provider baseline.

- [ ] **Step 4: Inspect the final diff and preserved workspace state.**

  ```bash
  git status --short
  git diff --check
  git diff --stat
  ```

  Confirm only the planned source/docs/eval/release changes are staged for the final commit and the pre-existing untracked `dist/agent-team-work/` path remains untouched or is explicitly excluded from the commit.

- [ ] **Step 5: Commit final release evidence if generated changes are required.**

  ```bash
  git status --short reports dist
  ```

  After reviewing that output, stage only the exact generated report and package paths created by this turn, never the whole `reports/` directory and never the pre-existing untracked `dist/agent-team-work/` directory. Commit the reviewed paths with `chore: refresh discussion-round release evidence`. If the clean diff shows no generated changes or the untracked path is not the required package artifact, do not create this commit; record the no-change result in the final verification summary.

## Plan self-review

- Spec coverage: trigger policy is Task 1 and Task 3; request/lifecycle/data identity is Task 1 and Task 2; stale/duplicate/timeout behavior is Task 2 and Task 3; serial/Lead gates are preserved in Tasks 1–4; backward compatibility is Task 1 and Task 2; test and release evidence are Tasks 2–4.
- Placeholder scan: no unfinished markers or unspecified handling steps are used; all commands and paths are concrete.
- Type consistency: `discussion_id`, `discussion_policy`, `decision_status`, `decision_owner`, statuses, message kinds, record paths, parser signature, validator signature, and CI target name are consistent across tasks.
