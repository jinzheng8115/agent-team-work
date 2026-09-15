# Security Trust Report

- OK: `True`
- Scanned files: `40`
- Scripts: `6`
- Internal script modules: `0`
- Secret findings: `0`
- Network-capable scripts: `0`
- Network policy covered scripts: `0`
- Network policy missing scripts: `0`
- File-write scripts: `2`
- Permission approvals: `2 / 2`
- Permission approval gaps: `0`
- CLI help smoke checked: `6`
- CLI help smoke failures: `0`
- Interactive scripts: `0`
- Package hash scope: `source-contract-without-generated-reports`
- Package hash files: `40`
- Package SHA256: `7fc78ea3f8283a5e98703697d10e7b77d25b2d5993f0caba46bc3fb2049f1bc3`

## Failures

- None

## Warnings

- None

## Dependency Evidence

- Files: `requirements-ci.txt`
- Pinned entries: `0`
- Unpinned entries: `0`

## Network Policy

- Policy file: `security/network_policy.json`
- Present: `False`
- Covered scripts: `0`
- Missing scripts: `none`
- Mismatches: `0`

## Permission Governance

- Policy file: `security/permission_policy.json`
- Present: `True`
- Required capabilities: `file_write, subprocess`
- Approved capabilities: `file_write, subprocess`
- Missing approvals: `none`
- Invalid approvals: `none`
- Expired approvals: `none`

## CLI Help Smoke

- Enabled: `True`
- Timeout seconds: `5.0`
- Checked scripts: `6`
- Passed scripts: `6`
- Failed scripts: `none`

## Script Surface

| Script | Interface | Declared | Argparse | Main Guard | Input | Network | File Write | Subprocess | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scripts/build_runtime_package.py | cli | False | True | True | False | False | True | False | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
| scripts/ci_test.py | cli | True | True | True | False | False | False | True | Runs local, dependency-free route, syntax, and package-shape checks before release. |
| scripts/import_telemetry_events.py | cli | True | True | True | False | False | False | False | Validates local JSONL telemetry and emits sanitized metadata events to stdout; the caller owns any local spool redirect. |
| scripts/local_output_eval_runner.py | cli | True | True | True | False | False | False | False | Runs deterministic fixture output through the output-eval command contract; it never calls a provider. |
| scripts/runtime_package_check.py | cli | False | True | True | False | False | True | False | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
| scripts/validate_team_state.py | cli | True | True | True | False | False | False | False | Validates a file-backed team ledger read-only and returns a machine-readable JSON result. |
