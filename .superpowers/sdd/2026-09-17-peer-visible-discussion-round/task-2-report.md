# Task 2 report: Enforce and test the contract

## Implementation

- Closed and `lead_accepted` discussions now require at least two valid participants and a `decision_owner` who is a worker participant (not the bound Lead).
- Their transcripts now require a non-`decision` `proposal`, `challenge`, `evidence`, or `response` sent directly from one worker participant to another.
- The validator requires two distinct participant senders before the owner decision and rejects transcripts whose messages are only self-directed or Lead-directed.
- Existing identity, sequence, stale/duplicate, owner-decision, and Lead-acceptance checks remain in place.

## Files

- `scripts/validate_team_state.py`
- `evals/discussion_round_state_test.py`
- `evals/evals.json`
- `evals/output/cases.jsonl`
- `evals/route_contract_test.py`

## TDD evidence

### RED

Command:

```bash
python3 evals/discussion_round_state_test.py
```

Observed result before the validator change:

```text
AssertionError: {'ok': True, ..., 'member_count': 3, 'task_count': 1, 'accepted_task_count': 0, 'failures': []}
```

The failing test was `test_closed_discussion_rejects_ai_music_d1_leader_mediated_shape`. Its fixture models the AI Music d1 shape: worker and reviewer messages are addressed only to Lead, while the owner decision is also Lead-directed. It was accepted before this change.

The self-review added a second RED regression for a direct peer response appended after the owner decision:

```text
AssertionError: {'ok': True, ..., 'member_count': 3, 'task_count': 1, 'accepted_task_count': 0, 'failures': []}
```

`test_closed_discussion_rejects_peer_exchange_appended_after_owner_decision` proved that the first implementation incorrectly counted a post-decision peer message. The final implementation now requires the non-decision worker-to-worker exchange before the owner decision.

### GREEN

Command:

```bash
python3 evals/discussion_round_state_test.py
python3 evals/route_contract_test.py
python3 -m py_compile scripts/validate_team_state.py evals/discussion_round_state_test.py
git diff --check
```

Output:

```text
PASS discussion-round-state (28 tests)
GREEN: agent-team-work route/protocol contract validated
```

## Full verification

```text
PASS discussion-round-state (28 tests)
PASS revision-cycle-state (19 tests)
GREEN: agent-team-work route/protocol contract validated
PASS revision-cycle-state (19 tests)
PASS discussion-round-state (28 tests)
PASS route-contract
PASS python-compile
PASS package-shape
PASS runtime-package
PASS revision-state
PASS discussion-state
Completed 6 CI checks.
git diff --check: PASS
```

Commands run:

```bash
python3 evals/discussion_round_state_test.py
python3 evals/revision_cycle_state_test.py
python3 evals/route_contract_test.py
python3 scripts/ci_test.py
python3 scripts/validate_team_state.py .team
git diff --check
```

## Self-review

- The scope is limited to the validator, discussion regression fixtures, and the corresponding route/eval contract assertions.
- The acceptance condition applies only to `closed` and `lead_accepted`; legacy teams and non-acceptance discussion states keep their existing validation behavior.
- The peer-exchange tests use the real file-backed validator, not a mock, and prove that both the formerly accepted Leader-mediated d1 transcript and a post-decision peer-message backfill now fail.
- The route/output fixture requires explicit direct peer-visible worker exchange before the worker owner decision.

## Concerns

`python3 scripts/validate_team_state.py .team` exits nonzero because this worktree has no `.team/team.json` or `.team/tasks.json`. The validator reports both files missing and then the dependent required-field errors. This is pre-existing workspace state, not a Task 2 regression. All dependency-free CI and discussion/revision/route regressions pass.

## Fix round 1 (final-review findings I1/I2)

Final whole-branch review found two Important gaps beyond the first acceptance
predicates:

- I1: the sender predicates counted the bound Leader or self-directed traffic
  toward the two-sender/participant obligation.
- I2: the decision boundary used numeric `sequence`, so a physically later
  JSONL line with a lower sequence could count as pre-decision exchange.

RED evidence (before the fix, one representative run):

```text
python3 evals/discussion_round_state_test.py
AssertionError: {'ok': True, ..., 'member_count': 3, 'task_count': 1, 'accepted_task_count': 0, 'failures': []}
```

Four new regressions were added: Leader-as-second-sender with a silent reviewer
(closed + lead_accepted), reviewer self-directed challenge, silent third worker
participant, and physical-order lower-sequence backfill (closed + lead_accepted).

GREEN evidence (after the fix):

```text
PASS discussion-round-state (32 tests)
PASS revision-cycle-state (19 tests)
GREEN: agent-team-work route/protocol contract validated
Completed 6 CI checks.
git diff --check: PASS
```

Implementation: `owner_decision_line` now uses the first valid owner decision
line in JSONL append order; messages at or after that line cannot satisfy the
exchange/sender predicates. Every worker participant (member thread_id !=
bound Leader and role != leader) must contribute at least one pre-decision
non-decision peer message to a different worker participant; Leader and
self-directed senders never satisfy that obligation. At least two worker
participants are required.
