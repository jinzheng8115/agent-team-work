# Migration guide

## 0.1.x to 0.2.0

This release keeps the existing entrypoint name and strict serial workflow. It adds explicit Codex project/thread bindings, ownership epochs, dispatch keys, report identity fields, a read-only `.team` validator, and portable evidence records.

Existing users should:

1. Keep the current project and member task IDs when continuing a team.
2. Add `team.json.schema_version: 2`, `project_verified`, `ownership_epoch`, and member host/thread bindings when migrating an older ledger.
3. Add `dispatch_key` and `acceptance` to each task; use a new attempt number for rework.
4. Run `python3 scripts/validate_team_state.py .team` before resuming work.

There is no declared breaking workflow change, but old ledgers without identity and project verification fields must remain paused until they are migrated and checked.

## Schema 2 to schema 3 revision ledgers

Schema 2 remains read-compatible only as the initial `revision_cycle: 1`; missing cycle fields and the legacy dispatch key are interpreted that way. Do not write a post-completion revision into a schema-2 ledger.

Before the first user-requested modification after `complete`, the bound Lead must upgrade both `team.json` and `tasks.json` to `schema_version: 3`, set their matching active `revision_cycle`, preserve cycle-1 tasks and reports, and create `.team/revisions/<cycle>.md` before dispatch. Preserved cycle-1 task records may retain their schema-2 shape: they do not need the schema-3-only `team_id`, `ownership_epoch`, `stage`, `dispatch_kind`, `source`, `report_path`, or identity-bound evidence objects, but they must resolve to `revision_cycle: 1` and retain a valid legacy dispatch key and acceptance evidence. Cycle-2-and-later tasks must include the full identity fields, `revision_cycle`, `supersedes`, non-empty `impact_basis`, `report_path`, and identity-bound evidence, and use `<team_id>/<ownership_epoch>/r<revision_cycle>/<stage>/<attempt>/<kind>`. No task or dispatch key may name a cycle later than the ledgers' active cycle.

For a zero-impact revision, increment the active cycle and append the analysis to `.team/revisions/<cycle>.md` as usual, then add the exact standalone marker `impact_result: no_affected_stages`. This append-preserving marker is the only way a schema-3 team may return to `complete` without any task in the active cycle; explanatory prose alone is insufficient. A planned, sending, or dispatched revision task may reserve its future `report_path` before the member creates that file. The file must exist once the task reaches reported, accepted, or rework. Run `python3 scripts/validate_team_state.py .team` after the upgrade and before sending work.

## Optional worker discussion policy

Legacy teams with no `discussion_protocol_version` in either ledger retain the current serial behavior; their tasks may omit `discussion_policy` regardless of dispatch-key format and do not gain worker-to-worker discussion implicitly. New teams set the integer `discussion_protocol_version: 1` in both `team.json` and `tasks.json`. To enable an existing team, first add the exact default policy (`mode: worker_can_request`, `soft_trigger_threshold: 2`, `max_rounds: 2`, `deadline: Lead-defined`) to every active `work`/`rework` task, then add the matching marker to both ledgers in the same Lead-owned update. Do not add the marker to only one ledger. For an enabled round, migrate the operating procedure as well: Lead selects a worker `decision_owner`, fans out identical context and transcript location to every participant, and requires each participant to read the shared transcript and send an identity-bound message to a real peer thread ID. `recipients` must name that peer, each canonical message is appended once, and owner decision/Lead acceptance require the resulting cross-worker exchange; a Lead-only consultation is invalid. Adding the policy or marker does not migrate old task identity, relax the Lead-only `team.json`/`tasks.json` writer rule, allow a discussion decision to bypass normal task acceptance and stage dispatch, or change legacy/no-marker behavior.
