# Migration guide

## 0.1.x to 0.2.0

This release keeps the existing entrypoint name and strict serial workflow. It adds explicit Codex project/thread bindings, ownership epochs, dispatch keys, report identity fields, a read-only `.team` validator, and portable evidence records.

Existing users should:

1. Keep the current project and member task IDs when continuing a team.
2. Add `team.json.schema_version: 2`, `project_verified`, `ownership_epoch`, and member host/thread bindings when migrating an older ledger.
3. Add `dispatch_key` and `acceptance` to each task; use a new attempt number for rework.
4. Run `python3 scripts/validate_team_state.py .team` before resuming work.

There is no declared breaking workflow change, but old ledgers without identity and project verification fields must remain paused until they are migrated and checked.

