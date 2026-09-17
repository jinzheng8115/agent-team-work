# Peer-visible discussion round repair plan

## Goal

Repair the worker discussion protocol so an approved round is a genuine,
participant-visible worker-to-worker exchange before a worker decision can be
accepted by the Lead. The existing serial stage gate, Lead-only ledgers, and
bounded discussion lifecycle remain unchanged.

## Constraints

- Keep `team.json` and `tasks.json` Lead-only writable.
- Keep the existing identity key, states, message kinds, two-round default,
  deadlines, stale handling, and serial stage gate.
- `decision_owner` is a worker participant, not the Lead.
- An approved discussion must fan out the same question/context to all
  participants; participant messages must be visible through one transcript.
- A `closed`/`lead_accepted` discussion requires at least one cross-worker
  exchange before its decision message. A Lead-only consultation is invalid.
- Preserve legacy teams without `discussion_protocol_version`.
- Preserve unrelated untracked `dist/agent-team-work/`.

## Task 1: Publish the peer-visible routing contract

Update the runtime skill, workflow/protocol/tool references, example, README,
migration notes, and smoke checklist. Define the round as:

1. Lead approves worker participants and a worker `decision_owner`.
2. Lead sends the same discussion context and transcript location to every
   participant, not a private decision question to only one worker.
3. Each participant reads the shared transcript and sends at least one
   identity-bound message to another participant using the real peer thread
   ID. `recipients` must name the peer(s), and the canonical message is
   appended once to the shared transcript.
4. The owner may publish `decision` only after a peer exchange is present.
5. Lead verifies peer visibility, identity, evidence, and scope before
   `lead_accepted`; no next stage is dispatched during the round.

Add explicit examples and user-visible evidence requirements so a transcript
shows proposal/challenge/response between worker labels, not only replies to
the Lead.

## Task 2: Enforce and test the contract

Extend `scripts/validate_team_state.py` and
`evals/discussion_round_state_test.py` so closed/lead-accepted discussions:

- require a worker participant as `decision_owner`;
- require at least two participants;
- require at least one non-decision message (`proposal`, `challenge`,
  `evidence`, or `response`) whose sender and recipient are different worker
  participants;
- require at least two distinct participant senders before the owner decision;
- reject a transcript where all messages are self-directed or Lead-directed;
- retain the existing identity, sequence, stale, duplicate, and Lead
  acceptance checks.

Add route/eval assertions and a regression fixture that would reject the
Leader-mediated d1 shape observed in the AI Music test. Run the full
dependency-free CI and discussion/revision regressions.

## Verification

```bash
python3 evals/discussion_round_state_test.py
python3 evals/revision_cycle_state_test.py
python3 evals/route_contract_test.py
python3 scripts/ci_test.py
python3 scripts/validate_team_state.py .team
git diff --check
```

## Completion

Task reviewers approve both spec compliance and quality, then a whole-branch
review confirms that the protocol now requires visible worker-to-worker
exchange and that the observed Leader-only flow fails validation.
