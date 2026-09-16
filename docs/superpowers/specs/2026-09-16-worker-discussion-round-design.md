# Worker-to-worker discussion round design

## Purpose

Add a bounded discussion subflow to `agent-team-work`. Workers may exchange
evidence and challenge proposals when a task contains an unresolved,
cross-role decision, while the Lead remains the only workflow coordinator and
the existing serial dispatch and acceptance rules remain intact.

The discussion round is a decision protocol, not an unrestricted team chat.
It must end in a recorded decision, an explicit block, or an explicit expiry.

## Scope

This change covers:

- worker-side detection of unresolved decisions through a standard triage gate;
- a worker's structured request for a discussion round;
- Lead approval, participant selection, and discussion lifecycle control;
- worker-to-worker proposals, challenges, evidence, and responses within one
  discussion ID;
- a designated `decision_owner` who makes the content decision;
- Lead verification, recording, and handoff of the accepted decision;
- identity, stale-message, timeout, and disagreement handling.

It does not add unrestricted chat, parallel project execution, autonomous
stage dispatch, worker writes to the team/task ledgers, a second Lead, or a
replacement for Lead acceptance.

## Chosen approach

Use a request-then-approval protocol:

1. A worker detects a decision need using the task's `discussion_policy` and
   submits a `discussion_request`.
2. The Lead evaluates whether the request meets the trigger policy, creates a
   discussion record, selects participants, and assigns a `decision_owner`.
3. Participants exchange messages inside the active discussion. Messages are
   routed to the intended worker(s) and are persisted in an append-only
   transcript visible to the Lead.
4. The `decision_owner` publishes the selected option, rationale, evidence,
   rejected alternatives, and affected tasks.
5. The Lead checks protocol identity, evidence, scope, and dependencies,
   records the decision as accepted or returns it for clarification, then
   resumes or dispatches the affected work under the normal gate.

This keeps the worker-to-worker conversation useful without allowing a member
to bypass the single-writer task ledger or start a later stage.

## Trigger policy

### Worker decision triage

Every new or discussion-enabled `work` and `rework` task includes a
`discussion_policy`. The worker runs the triage at task start, before an
irreversible change, after new evidence changes an assumption, and before
finalizing a cross-role decision. Legacy tasks without this field retain the
current workflow and do not acquire discussion behavior implicitly.

The default policy for newly created tasks is:

```text
mode: worker_can_request
soft_trigger_threshold: 2
max_rounds: 2
deadline: Lead-defined
```

The worker asks:

```text
Can I complete this task using the current requirements and accepted inputs?
├─ yes: proceed; record non-blocking assumptions
└─ no:
   ├─ one missing fact, permission, or input: ask the Lead or report blocked
   ├─ multiple viable options with cross-role impact: request discussion
   └─ conflicting worker evidence or accepted outputs: request discussion
```

### Hard triggers

Any one of the following requires a discussion request before the decision
dependent work continues:

- an API, file format, interface, or acceptance contract affecting another
  worker is unresolved;
- two or more viable options have material trade-offs;
- another worker's result conflicts with the current conclusion;
- the decision concerns release, security, permissions, destructive migration,
  or another high-impact external change;
- the requirement has multiple interpretations that produce materially
  different outputs;
- a wrong choice would invalidate substantial downstream work.

### Soft triggers

Two or more of the following also require a discussion request:

- the worker needs context held by another role;
- key evidence or an assumption is unverified;
- the worker lacks authority to decide for another role;
- the choice changes a downstream task or its DoD;
- there is a meaningful quality, cost, speed, or compatibility trade-off.

One soft trigger alone does not open a discussion. The worker documents the
assumption and proceeds, or asks the Lead for a simple clarification.

Missing tools, paths, permissions, or required inputs are `blocked`, not a
discussion trigger, unless resolving them also requires a cross-role decision.

### Lead safety net

The member report includes `decision_status`:

```text
clear | assumption | unresolved
```

During acceptance, the Lead may open a discussion when a report contains an
unresolved decision, conflicting evidence, an unapproved cross-stage change,
or a downstream dependency that was not addressed. This catches a missed
worker-side trigger without making every task a discussion.

## Discussion request

A request is not an invitation to chat. It is a structured decision request
with the following fields:

```text
team_id / ownership_epoch / revision_cycle
stage / task_id / dispatch_key
question
why_now
options
evidence
affected_tasks
suggested_participants
suggested_decision_owner
impact_if_wrong
paused_work
```

The worker may continue work that is independent of the unresolved decision,
but must pause the decision-dependent or irreversible part until the request
is accepted, rejected with guidance, or converted to `blocked`.

## Discussion record and message identity

Each discussion has a stable key bound to the current task:

```text
<team_id>/<ownership_epoch>/r<revision_cycle>/<stage>/<task_id>/d<sequence>
```

The record contains:

- `discussion_id`, team/epoch/revision/stage/task identity;
- `status`, `trigger`, `question`, and `opened_by`;
- participant labels and their roles;
- `decision_owner`;
- `max_rounds` and `deadline`;
- transcript path and final decision path;
- the related dispatch key and affected task IDs.

Each message contains:

```text
message_id
discussion_id
sender
recipients
sequence
kind: proposal | challenge | evidence | response | decision
in_reply_to
body
created_at
```

Messages whose team, epoch, revision, stage, task, or discussion identity no
longer matches are `stale` and cannot advance the task.

## State model

The normal lifecycle is:

```text
requested -> approved -> open -> proposing/challenging
           -> decision_pending -> decided -> lead_accepted -> closed
```

Alternative terminal states are `rejected`, `blocked`, `expired`, and
`cancelled`.

- `requested`: a worker submitted a triage-backed request.
- `approved`: the Lead accepted the request and selected participants.
- `open`: invitations and the decision question are visible.
- `proposing` / `challenging`: participants submit options, evidence, and
  objections.
- `decision_pending`: the discussion window is closing and the owner must
  decide or escalate.
- `decided`: the owner published a decision.
- `lead_accepted`: the Lead verified the decision and its evidence.
- `closed`: the decision is attached to the task and no more messages may
  advance it.

The discussion state does not create a new delivery stage. Project work stays
under the existing serial stage gate.

## Roles and permissions

### Worker

- run the triage gate;
- request a discussion when the trigger policy is met;
- submit bounded proposals, challenges, and evidence;
- reference the discussion decision in the task report;
- never edit `team.json` or `tasks.json`, accept a task, or dispatch another
  stage.

### Decision owner

- synthesize the discussion;
- choose one option or explicitly escalate;
- provide rationale, evidence, rejected alternatives, and affected tasks;
- cannot silently change the task scope or bypass Lead acceptance.

### Lead

- approve/reject requests;
- choose participants, owner, deadline, and round limit;
- keep the transcript and decision record auditable;
- accept or return the decision;
- update the task ledger and resume normal dispatch.

## Bounded interaction rules

The MVP defaults are:

- two to four participants;
- one concrete decision question per discussion;
- at most two discussion rounds;
- a Lead-set deadline;
- no project file modifications by a participant solely because a discussion is
  open;
- no discussion may open a later stage or supersede an accepted task without a
  new Lead task decision.

If the owner cannot decide by the deadline, the Lead marks the discussion
`blocked` or asks the user one concrete question. It must not remain open
indefinitely.

## Data flow

1. The Lead dispatches a task with a discussion policy.
2. The worker runs triage and either proceeds, asks for clarification,
   reports blocked, or submits a discussion request.
3. The Lead records the request, then opens or rejects it.
4. Participants exchange identity-bound messages and evidence.
5. The decision owner publishes a decision.
6. The Lead verifies the record and accepts or returns it.
7. The worker resumes the task; the next stage can be dispatched only through
   the existing acceptance and dependency gates.

## Failure and recovery

- Duplicate requests for the same active task are coalesced or marked
  `duplicate`.
- A request with no active matching task is rejected as `stale`.
- Messages after `closed`, `expired`, or `cancelled` are retained as history
  but cannot change the task.
- If a participant is unavailable, the Lead may reduce the participant set or
  mark the discussion blocked; the protocol must not silently substitute a
  new role.
- If the user changes the objective while a discussion is active, the Lead
  pauses new messages, marks invalidated work stale, and re-runs impact
  analysis under a new revision record.
- A discussion decision is evidence for Lead acceptance, not acceptance by
  itself.

## Backward compatibility

Teams without a discussion policy continue using the current serial workflow.
The default policy is `worker_can_request`, with the trigger rules in this
document. Existing accepted tasks and reports remain valid; discussion fields
are added only to tasks that opt into the new protocol.

## Test design

### Trigger tests

- a clear, single-option task proceeds without a discussion;
- one missing input becomes a Lead clarification or `blocked` result;
- one hard trigger creates a valid request;
- two soft triggers create a valid request;
- a worker can continue independent work while decision-dependent work is
  paused.

### State and identity tests

- valid lifecycle reaches `closed` only after `decision_owner` and Lead
  evidence are present;
- wrong team, epoch, revision, stage, task, or discussion keys become stale;
- messages after closure cannot advance a task;
- duplicate requests do not create duplicate active discussions;
- a discussion cannot dispatch a later stage.

### Behavior evaluations

1. Two workers resolve an interface contract and the decision is consumed by
   the original task.
2. Conflicting reports produce a discussion, not an automatic overwrite.
3. A high-risk release choice pauses until an owner decision and Lead
   acceptance exist.
4. A timeout produces `blocked` and a concrete escalation rather than an
   infinite conversation.

## Acceptance criteria

The feature design is satisfied when:

- workers have explicit, repeatable rules for recognizing a discussion need;
- workers can request but cannot unilaterally start or close a discussion;
- workers can exchange bounded, identity-bound messages within an approved
  discussion;
- a designated worker can make the content decision;
- Lead acceptance remains required before task or stage progression;
- stale, duplicate, timeout, disagreement, and objective-change cases are
  defined;
- simple tasks continue without discussion overhead;
- the existing serial ledger and dependency guarantees remain intact.
