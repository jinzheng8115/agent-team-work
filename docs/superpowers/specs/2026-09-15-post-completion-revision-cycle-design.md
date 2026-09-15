# Post-completion revision cycle design

## Purpose

`agent-team-work` already defines first-round serial delivery and pre-acceptance rework, but it does not define a complete team workflow for a new modification requested after the team has reached `complete`. This change adds a post-completion revision cycle: the bound Lead first performs impact analysis, then dispatches only the affected stages and required downstream stages through the same capability, reporting, acceptance, and gating discipline as the first round.

The design preserves the first round as immutable evidence. A later modification does not rewrite an accepted task into an ordinary rework attempt, and it does not authorize the Lead to make an ad hoc change outside the team workflow.

## Scope

This change covers:

- modification requests received by the bound Lead after the team is `complete`;
- impact analysis against accepted tasks, delivered artifacts, dependencies, and the overall completion criteria;
- creation and serial dispatch of a new revision cycle;
- reuse of the original member sessions;
- invalidation and recovery when the request changes during a revision cycle;
- ledger validation and behavior evaluations for the new state transitions.

It does not add parallel execution, automatic Lead takeover, new member creation, background supervision, or a new gating mode.

## Chosen approach

Represent each post-completion change as a distinct revision cycle. The Lead creates an impact-analysis record before dispatch, selects the affected stages and necessary downstream stages, and runs those stages through the existing serial protocol. Unaffected accepted work remains valid only when the impact analysis records why it remains valid.

This is preferable to appending an unstructured task because dependencies and inherited acceptance remain explicit. It is also preferable to reopening the original accepted task because the first-round record stays intact and post-completion modification remains distinguishable from pre-acceptance rework.

## State model

The team keeps its existing `team_id` and `ownership_epoch`. A revision cycle is not a change of ownership.

### Team state

`team.json` gains `revision_cycle`. The initial delivery uses `revision_cycle: 1`; the first post-completion modification uses `revision_cycle: 2`, and later cycles increment monotonically.

The allowed team states gain `impact_analysis`. A normal post-completion transition is:

```text
complete -> impact_analysis -> running -> complete
```

If analysis finds no affected stage, the Lead records the conclusion and returns directly to `complete` without dispatch. A user decision or unresolved dependency may move the team from `impact_analysis` or `running` to `paused` or `blocked` under the existing rules.

### Task state

Every task gains:

- `revision_cycle`: the delivery or revision cycle that created the task;
- `supersedes`: identifiers of earlier accepted tasks whose output is replaced or revalidated, or an empty list;
- `impact_basis`: the reason this task is required by the current modification.

Accepted tasks from earlier cycles remain unchanged. A post-completion change creates new task records rather than converting an earlier accepted task to `rework`.

Within one revision cycle, `attempt` retains its current meaning: it increments when a dispatched task fails its DoD and is returned to the same member. The revision cycle distinguishes a new user-requested change from ordinary rework inside that change.

### Revision record

The Lead writes `.team/revisions/<cycle>.md` before the first dispatch. It records:

- the user's original modification request;
- affected artifacts and stages;
- required downstream revalidation or rework;
- prior acceptances that remain valid and the evidence for retaining them;
- changed completion criteria and per-stage DoD;
- selected members, ordering, inputs, allowed paths, and deliverables;
- the final cycle-level acceptance result.

The record is append-preserving evidence. Material changes to the request are added as a new analysis decision; they do not silently replace the original request or an already dispatched task.

## Impact analysis

Only the bound Lead may perform and record the authoritative impact analysis. Before analysis, the Lead verifies the current Leader binding and reads both ledgers, the overall goal and completion criteria, accepted task records, relevant artifacts, and the real state of bound member sessions.

The analysis must answer:

1. What changed in the user's requested outcome?
2. Which accepted artifacts or decisions are affected?
3. Which producing stages must run again?
4. Which downstream stages depend on those outputs and require rework or revalidation?
5. Which prior acceptances remain valid, and what evidence supports that conclusion?
6. What are the revised inputs, allowed scope, deliverables, verification steps, and DoD?
7. What is the serial dispatch order?

At least one affected stage is required to dispatch work. If none is affected, the Lead explains the conclusion, records it in the revision file, and keeps the team complete.

Impact analysis is a hard dispatch gate. Receiving a modification request does not permit the Lead to send an informal follow-up directly to a member.

## Dispatch and acceptance flow

After impact analysis, the Lead creates all currently known revision tasks as planned records, but dispatches only the first task whose dependencies are accepted or explicitly retained by the analysis.

Revision work reuses the original member session responsible for the selected stage. Each task follows the same workflow as the initial delivery:

1. record dispatch intent and a unique dispatch key;
2. send a complete `work` task to the selected member;
3. require the stage-specific capability gate before modification begins;
4. wait for a structured, identity-bound member report;
5. inspect artifacts and verification evidence;
6. record Lead acceptance or return the task as `rework` with an incremented attempt;
7. apply the existing `automatic` or `confirmation` gate before the next affected stage.

The dispatch key gains a revision component:

```text
<team_id>/<ownership_epoch>/r<revision_cycle>/<stage>/<attempt>/<kind>
```

Only evidence matching team, ownership epoch, revision cycle, stage, attempt, dispatch key, and source may advance the active revision. Results from earlier cycles are historical evidence and cannot satisfy a current task.

After every revision task is accepted, the Lead rechecks the overall completion criteria and final artifacts. The team returns to `complete` only when both the revision tasks and the whole-team outcome pass. The cycle-level result is recorded in the revision file.

## Changes during an active revision

If the user changes the request while a revision cycle is active, the Lead pauses new dispatch and repeats impact analysis against the new request and work already performed.

- Planned but undispatched tasks may be replaced by new planned records.
- Dispatched tasks are not silently rewritten. When their objective or DoD is invalidated, their current result is marked `stale`, and a new task or attempt is created with a new dispatch key.
- Newly affected upstream or downstream stages are inserted according to dependency order.
- A result for an invalidated objective cannot advance the revised workflow, even if the member completed it successfully.
- If the change requires a user decision, the team enters `paused` and the Lead asks one concrete question before further dispatch.

## Validation rules

The ledger validator should reject:

- an invalid or decreasing `revision_cycle`;
- a task without a valid cycle, `supersedes`, or `impact_basis` under the new schema;
- a dispatch key whose revision component does not match its task or team;
- a post-completion revision task created without a corresponding revision record;
- a team marked `complete` while current-cycle tasks are not accepted;
- a current-cycle acceptance based only on an earlier-cycle result;
- duplicate dispatch keys across cycles or attempts.

Schema migration must be explicit. Existing schema-version-2 teams are interpreted as initial cycle 1. Any persisted schema bump and migration behavior will be defined in the implementation plan after checking current compatibility and packaging constraints.

## Test design

### Protocol contract tests

Static tests verify that the entry point, workflow, protocol, examples, and failure guidance define:

- post-completion impact analysis as a dispatch gate;
- `revision_cycle` and revision records;
- retained acceptance with evidence;
- the revision-aware dispatch key;
- full reuse of first-round capability, report, acceptance, and gate rules.

### State validation tests

Fixtures cover valid initial delivery, valid scoped revision, and invalid states including missing analysis, revision mismatch, earlier-cycle evidence advancing the current cycle, and premature completion.

### Behavior evaluations

1. A small post-completion modification reruns only its producing stage and the downstream stages that truly require revalidation.
2. A cross-stage modification dispatches multiple original members in dependency order, never concurrently or ahead of acceptance.
3. A request change during active revision invalidates affected work as stale, updates impact analysis, and avoids duplicate or out-of-order dispatch.
4. A modification with no actual stage impact records the reasoning and keeps the team complete without contacting members.

## Acceptance criteria

The skill improvement is complete when:

- post-completion modifications are explicitly routed through Lead impact analysis;
- affected work follows the same serial team protocol as initial delivery;
- first-round accepted records remain intact;
- revision-aware state and dispatch identities prevent old results from advancing new work;
- validator, protocol tests, and behavior eval fixtures cover the new workflow;
- generated package contents and required release checks are refreshed without overwriting unrelated workspace changes.
