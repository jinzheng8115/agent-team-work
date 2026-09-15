# Post-completion Revision Cycle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `agent-team-work` so a modification received after `complete` first goes through Lead impact analysis and then runs only affected stages through the same serial dispatch, reporting, acceptance, and gating protocol as the initial delivery.

**Architecture:** Keep first-round tasks and reports immutable. Add a monotonic `revision_cycle`, a persisted `.team/revisions/<cycle>.md` impact-analysis record, revision-aware task identity, and validator rules that distinguish historical evidence from the active cycle. Update the skill instructions and fixtures so the runtime behavior is explicit even though the skill itself does not implement a background scheduler.

**Tech Stack:** Markdown skill/reference documents, dependency-free Python 3 validator and contract tests, JSON evaluation fixtures, existing `scripts/ci_test.py` entry point.

## Global Constraints

- The bound Lead must perform and record impact analysis before any post-completion dispatch.
- Unaffected accepted work remains valid only when the analysis records evidence for retaining it.
- Revision work reuses original member sessions and remains strictly serial; no parallel worker, new member, takeover, or background supervisor is added.
- Old accepted tasks and reports are append-preserving evidence and are never rewritten into ordinary rework.
- Only matching `team`, `ownership_epoch`, `revision_cycle`, `stage`, `attempt`, `dispatch_key`, and source evidence can advance the active workflow.
- Existing schema-version-2 ledgers remain readable as initial cycle 1; any ledger carrying revision-cycle state is written as schema version 3.
- Preserve unrelated dirty files and generated evidence; update only files listed by each task.

---

## Task 1: Add revision-aware ledger validation and regression fixtures

**Files:**
- Modify: `scripts/validate_team_state.py`
- Create: `evals/revision_cycle_state_test.py`
- Modify: `scripts/ci_test.py`

**Interfaces:**
- `scripts/validate_team_state.py` continues exposing `validate(team_dir: Path) -> dict` and CLI JSON output.
- Add internal helpers `parse_schema_version(value) -> int`, `task_cycle(task, schema_version) -> int`, and `parse_dispatch_key(key) -> dict | None` so validation and tests share one interpretation of legacy and revision keys.
- `evals/revision_cycle_state_test.py` invokes `validate()` against temporary `.team` fixtures and exits non-zero on assertion failure.
- `scripts/ci_test.py` gains a `revision-state` target that runs the new test script with `sys.executable`.

- [ ] **Step 1: Write failing state fixtures and assertions**

Create the test script with fixture builders for:

```python
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
```

Define the test-only helper with this exact interface before these tests:

```python
def write_fixture(*, schema_version: int, team_status: str, cycle: int,
                  revision_record: bool = True,
                  revision_tasks: str = "accepted") -> Path:
    """Create and return a temporary .team directory for one validator case."""
```

The helper must use `tempfile.mkdtemp()`, write `team.json` and `tasks.json`, create `.team/revisions/2.md` only when `revision_record` is true, and populate the requested task mode. It must use a schema-2 legacy key (`team/1/stage/1/work`) for cycle 1 and a schema-3 revision key (`team/1/r2/stage/1/work`) for cycle 2. The `old-cycle-accepted` mode must add an accepted cycle-1 task while the team cycle is 2; `stale-without-superseder` must add a stale current-cycle task without an accepted task naming it in `supersedes`; `wrong-cycle-key` must attach the cycle-1 key to a cycle-2 task. Each generated team must include one verified member, a bound Leader, a positive ownership epoch, and a matching `tasks.json` revision so failures exercise only the intended rule.

- [ ] **Step 2: Run the new test before implementation**

Run: `python3 evals/revision_cycle_state_test.py`

Expected: FAIL because the current validator rejects `impact_analysis`/revision keys and has no current-cycle or revision-record checks.

- [ ] **Step 3: Implement schema and key parsing**

In `scripts/validate_team_state.py`:

```python
LEGACY_DISPATCH_KEY = re.compile(
    r"^(?P<team>[^/]+)/(?P<epoch>\d+)/(?P<stage>[^/]+)/(?P<attempt>\d+)/(?P<kind>standby|work|rework|result|accept|snapshot)$"
)
REVISION_DISPATCH_KEY = re.compile(
    r"^(?P<team>[^/]+)/(?P<epoch>\d+)/r(?P<cycle>\d+)/(?P<stage>[^/]+)/(?P<attempt>\d+)/(?P<kind>standby|work|rework|result|accept|snapshot)$"
)
SUPPORTED_LEDGER_VERSIONS = {2, 3}

def parse_dispatch_key(key: str) -> dict | None:
    for pattern in (REVISION_DISPATCH_KEY, LEGACY_DISPATCH_KEY):
        match = pattern.match(key)
        if match:
            data = match.groupdict()
            data["cycle"] = int(data["cycle"] or 1)
            data["epoch"] = int(data["epoch"])
            data["attempt"] = int(data["attempt"])
            return data
    return None
```

Accept team states `impact_analysis`, normalize missing cycle fields to cycle 1 only for schema 2, require schema 3 for `revision_cycle > 1`, require `.team/revisions/<cycle>.md` for every cycle above 1, and validate that each key's team/epoch/cycle agrees with its task and team. Require `supersedes` and non-empty `impact_basis` on cycle-2-or-later tasks.

When `team.status == "complete"`, evaluate only the active cycle: every non-stale task in that cycle must be `accepted`; each stale task must be named in the `supersedes` list of an accepted task in the same or later attempt/cycle. Preserve the existing acceptance evidence checks and dispatch-key uniqueness checks.

- [ ] **Step 4: Run the focused test and CI target**

Run: `python3 evals/revision_cycle_state_test.py`

Expected: PASS for legacy cycle 1, valid scoped revision, and all rejection cases.

Run: `python3 scripts/ci_test.py revision-state`

Expected: `PASS revision-state`.

- [ ] **Step 5: Commit the validator and tests**

```bash
git add scripts/validate_team_state.py evals/revision_cycle_state_test.py scripts/ci_test.py
git commit -m "feat: validate post-completion revision cycles"
```

## Task 2: Document the Lead impact-analysis and revision workflow

**Files:**
- Modify: `SKILL.md`
- Modify: `references/workflow.md`
- Modify: `references/team-protocol.md`
- Modify: `references/codex-tools.md`
- Modify: `references/e2e-smoke-checklist.md`
- Modify: `failures/README.md`
- Modify: `docs/migration-v2.md`
- Modify: `examples/serial-pipeline.md`

**Interfaces:**
- The entry skill and references must use the same state names, revision fields, and dispatch-key grammar as Task 1.
- `docs/migration-v2.md` documents schema-2 read compatibility and schema-3 upgrade before the first post-completion revision.

- [ ] **Step 1: Add the entry-point rule**

In `SKILL.md`, add a concise rule after the existing rework rule:

```text
团队 complete 后收到用户修改请求时，Lead 先进入 impact_analysis，读取首轮验收和真实成员状态，写 `.team/revisions/<cycle>.md`，按影响范围创建新 cycle 的任务；完成影响分析前不得向成员发送修改消息。受影响阶段仍复用原成员，并沿用能力门、报告、验收、gate 和恢复规则。
```

Also state that an analysis with no affected stage returns to `complete` without dispatch, and that old-cycle results cannot advance a new cycle.

- [ ] **Step 2: Extend the workflow and protocol references**

Document the transition `complete -> impact_analysis -> running -> complete`, the seven impact-analysis questions, cycle-level task fields (`revision_cycle`, `supersedes`, `impact_basis`), the revision record path, and the revision-aware key:

```text
<team_id>/<ownership_epoch>/r<revision_cycle>/<stage>/<attempt>/<kind>
```

Clarify that `attempt` still increments for rework within one revision cycle, while `revision_cycle` increments only for a new user-requested modification after completion. Add the active-cycle completion rule and the stale-result rule.

- [ ] **Step 3: Update tool, recovery, smoke, failure, migration, and example guidance**

Add to `codex-tools.md` that `send_message_to_thread` is forbidden until the impact record exists and that planned/active tasks must be queried before retrying. Add one smoke scenario covering a scoped revision and one failure row for “post-completion direct send”. Add the migration note that v2 is read-compatible as cycle 1 but a revision requires schema 3. Extend the serial example with a second cycle in which only the affected member and downstream reviewer are dispatched.

- [ ] **Step 4: Run static contract checks**

Run: `python3 evals/route_contract_test.py`

Expected: PASS, including the new terms `impact_analysis`, `revision_cycle`, `.team/revisions/`, and `r<revision_cycle>`.

Run: `python3 scripts/ci_test.py route-contract`

Expected: `PASS route-contract`.

- [ ] **Step 5: Commit the protocol documentation**

```bash
git add SKILL.md references/workflow.md references/team-protocol.md references/codex-tools.md references/e2e-smoke-checklist.md failures/README.md docs/migration-v2.md examples/serial-pipeline.md
git commit -m "docs: define post-completion revision workflow"
```

## Task 3: Add behavior and trigger evaluation coverage

**Files:**
- Modify: `evals/evals.json`
- Modify: `evals/trigger_cases.json`
- Modify: `evals/holdout_cases.json`
- Modify: `evals/failure-cases.md`
- Modify: `evals/route_contract_test.py`
- Modify: `evals/output/cases.jsonl`

**Interfaces:**
- Evaluation assertions must describe observable Lead behavior, not implementation details unavailable to a model using the skill.
- Existing test IDs and fixture outputs remain unchanged; new cases use unique IDs.

- [ ] **Step 1: Add post-completion behavior prompts and assertions**

Append these cases to `evals/evals.json`:

```json
{
  "id": "revision-impact-analysis",
  "prompt": "第一轮团队已经 complete，用户要求只修改交付物中的数据来源。请由 Lead 先做影响分析，再决定哪些原成员和下游阶段需要重新派发。",
  "expected_output": "先进入 impact_analysis 并写修订记录；只派受影响阶段及必要下游阶段；复用原成员，逐阶段验收。",
  "files": [],
  "assertions": ["analysis_before_dispatch", "scoped_dispatch", "reuses_original_members", "serial_acceptance"]
}
```

Also add cases for a cross-stage modification, a changed request that stales an already-dispatched task, and a no-impact request that performs no dispatch.

- [ ] **Step 2: Add trigger and holdout coverage**

Add should-trigger prompts mentioning “第一轮已完成后修改”, “Lead 影响分析”, “只重跑受影响阶段”, and “复用原成员返修”; add near-neighbor negatives for ordinary one-off edits, explanation-only requests, and creating a new skill. Keep the existing minimum counts in `route_contract_test.py` and increase them by the exact number of added cases.

- [ ] **Step 3: Add deterministic output fixtures**

Add one JSONL output fixture whose with-skill answer contains `impact_analysis`, `revision_cycle`, scoped dispatch, and active-cycle acceptance, while the baseline omits the analysis gate. Assertions must check the phrases as separate requirements so a response cannot pass by mentioning only “rework”.

- [ ] **Step 4: Extend the route contract test**

Require the new entry/protocol terms and assert that the new evaluation IDs are present. Do not add network calls, provider calls, or mutation to this static test.

- [ ] **Step 5: Run evaluation fixture checks**

Run: `python3 evals/route_contract_test.py`

Expected: PASS with the expanded trigger and holdout sets.

Run: `python3 scripts/ci_test.py python-compile`

Expected: `PASS python-compile`.

- [ ] **Step 6: Commit evaluation coverage**

```bash
git add evals/evals.json evals/trigger_cases.json evals/holdout_cases.json evals/failure-cases.md evals/route_contract_test.py evals/output/cases.jsonl
git commit -m "test: cover post-completion revision routing"
```

## Task 4: Refresh package-local verification and release evidence

**Files:**
- Modify only generated files that are produced by an available repository script; do not overwrite the pre-existing dirty files listed by `git status`.
- Verify: `dist/agent-team-work.zip`, `dist/agent-team-work/`, `manifest.json`, and `registry/packages/agent-team-work.json` for source/package drift.

**Interfaces:**
- The source skill remains `agent-team-work` version `0.2.0` unless an available release tool requires a coordinated version bump.
- No generated checksum or registry claim may be updated unless the corresponding source/package verification command succeeds.

- [ ] **Step 1: Run all dependency-free checks**

Run:

```bash
python3 scripts/ci_test.py
python3 evals/route_contract_test.py
python3 evals/revision_cycle_state_test.py
python3 scripts/validate_team_state.py .team
```

Expected: all checks pass. If `.team` is absent, report that the optional live-ledger check was not runnable rather than creating a synthetic project ledger.

- [ ] **Step 2: Discover available package refresh commands**

Run: `rg --files scripts | sort` and inspect only scripts present in this checkout. If the release commands referenced by `AGENTS.md` are absent, do not invent replacements; record the limitation in the final handoff and leave unrelated generated files untouched.

- [ ] **Step 3: Verify final diff and package drift**

Run:

```bash
git diff --check HEAD~3..HEAD
git status --short
git diff --stat HEAD~3..HEAD
```

Expected: only the committed implementation/design changes and intentionally refreshed generated outputs appear; pre-existing dirty artifacts remain unmodified unless a verified generator explicitly updates them.

- [ ] **Step 4: Commit verified generated outputs, if any**

If an available generator reports verified paths, stage only those explicit paths (for example, `dist/agent-team-work.zip`, `dist/agent-team-work/`, and the specific report files named by that generator) and commit them with `chore: refresh revision-cycle package evidence`. Do not use a wildcard or stage the whole repository.

If no generator is available, skip this commit and state exactly which release evidence remains stale.

## Self-review checklist

- [ ] The state validator accepts v2 cycle-1 ledgers and enforces v3 revision invariants.
- [ ] `complete` cannot dispatch directly; `impact_analysis` is documented as the hard gate.
- [ ] Scoped revisions preserve unaffected acceptance with explicit evidence.
- [ ] Stale tasks require accepted superseders before completion.
- [ ] Dispatch keys cannot cross team, epoch, cycle, stage, attempt, or kind.
- [ ] Documentation, examples, failure guidance, and tests use identical field names and key grammar.
- [ ] No placeholder language remains in this plan.
