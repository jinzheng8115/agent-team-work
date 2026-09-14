# Architecture Maintainability

Generated at: `2026-09-14`

## Summary

- decision: `pass`
- python files: `4`
- scripts: `4`
- tests: `0`
- internal modules: `0`
- CLI scripts: `4`
- Yao CLI command handlers: `0`
- entrypoint command handlers: `0`
- command modules: `0`
- largest file lines: `136`
- early watch threshold lines: `600`
- early watchlist: `0`
- watch threshold lines: `720`
- watchlist: `0`
- hotspots: `0`
- blockers: `0`

This report keeps maintainability risk visible before the Meta Skill grows more gates, renderers, and CLI commands.

## Hotspots

No file-size hotspots found.

## Watchlist

No near-threshold files found.

## Early Watchlist

No early watch files found.

## Largest Files

| File | Lines | Kind | Severity |
| --- | ---: | --- | --- |
| `scripts/import_telemetry_events.py` | `136` | `cli-script` | `pass` |
| `scripts/validate_team_state.py` | `131` | `cli-script` | `pass` |
| `scripts/ci_test.py` | `76` | `cli-script` | `pass` |
| `scripts/local_output_eval_runner.py` | `68` | `cli-script` | `pass` |

## Release Rule

- `block` hotspots should be split before governed release.
- `warn` hotspots can ship only when Review Studio keeps them visible and a reviewer accepts the modularization plan.
- Do not split a file only for line count; split when a stable responsibility boundary is clear.
