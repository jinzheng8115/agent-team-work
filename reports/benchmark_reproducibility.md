# Benchmark Reproducibility

Generated at: `2026-09-17`
Commit: `5287cb518da352b484cfd5a6c82536e4d2f18224`
Working tree dirty at generation: `true`
Source tree dirty at generation: `false`
Generated evidence dirty at generation: `true`
Evidence bundle SHA256: `ccaf2321e1bf8fb18844282fcf65738ce1055ea90fe24441e6c8b455e9faef1e`

## Summary

- reproducibility ready: `true`
- release lock ready: `true`
- methodology complete: `true`
- required artifacts: `25`
- missing artifacts: `0`
- source contract sha256: `71bbbdd0b320`
- archive sha256: `dbd9243877f9`
- output cases: `13`
- disclosed failure cases: `3`
- reproduction commands: `23`
- provider evidence complete: `false`
- phase-one provider matrix complete: `false`
- phase-one three-reviewer adjudication complete: `false`
- phase-one quality promotion complete: `false`
- human review complete: `false`
- world-class ready: `false`
- world-class source checks: `5` pass / `14` total; `9` blocked
- beta test ready: `false`
- beta test blockers: `1`
- beta deferred evidence: `4`
- public claim ready: `false`
- public claim blockers: `6`
- changed files at generation: `65`
- source changed files at generation: `0`
- generated changed files at generation: `65`

This report proves local benchmark reproducibility only. It keeps external provider and human-review gaps visible instead of counting them as complete. The git commit and dirty samples are generation-time context; the evidence bundle SHA is the durable anchor for the artifacts listed below.

## Beta Test Boundary

- ready: `false`
- scope: beta/public test release without superiority, fully-reviewed, or world-class claims
- policy: Human blind-review, native permission enforcement, real client telemetry, and ledger acceptance may be deferred for beta/public testing, but public claims must remain blocked until those evidence entries are accepted.
- required wording: Use beta, public test, or technical preview wording; do not claim world-class readiness, fully reviewed quality, or proven superiority over baseline.

| Blocker |
| --- |
| provider-backed model holdout source evidence is incomplete |

| Deferred evidence | Reason |
| --- | --- |
| `provider-holdout` | Provider-backed source evidence exists, but formal ledger submission and reviewer acceptance are still pending before public claims. |
| `human-adjudication` | Human adjudication evidence is still pending; deferred for beta/public testing and still required before superiority, fully-reviewed, or world-class claims. |
| `native-permission-enforcement` | Native enforcement proof is still pending; deferred for beta/public testing and still required before world-class claims. |
| `native-client-telemetry` | Real client telemetry is still pending; deferred for beta/public testing and still required before world-class claims. |

## Public Claim Boundary

- ready: `false`
- scope: public benchmark or world-class readiness claim
- policy: Local reproducibility can pass before public claims; public claims require provider evidence, human adjudication, clean release lock, accepted world-class evidence, and complete source checks.

| Blocker |
| --- |
| provider-backed model holdout evidence is incomplete |
| human blind-review adjudication is incomplete |
| phase-one provider matrix is incomplete |
| phase-one three-reviewer adjudication is incomplete |
| world-class evidence is not accepted yet (4 open gaps, 4 ledger pending) |
| world-class source checks are not all accepted (5/14 pass, 9 blocked) |

## Release Lock

- ready: `true`
- reason: only generated evidence artifacts were dirty at generation time
- status scope: generation-time status before this report is written

## Evidence Bundle

- algorithm: `sha256(path,label,exists,artifact_sha256)`
- artifacts: `25` / `25`
- sha256: `ccaf2321e1bf8fb18844282fcf65738ce1055ea90fe24441e6c8b455e9faef1e`

## Methodology Sections

| Section | Status |
| --- | --- |
| `## Benchmark Types` | present |
| `## Sample Sources` | present |
| `## Evaluation Dimensions` | present |
| `## Weighting Rule` | present |
| `## Failure Disclosure` | present |
| `## Reproduction` | present |

## Required Artifacts

| Label | Path | Status | SHA256 |
| --- | --- | --- | --- |
| methodology | `reports/benchmark_methodology.md` | present | `ce64f2d123bd` |
| failure_disclosure | `evals/failure-cases.md` | present | `fc569fbab194` |
| output_cases | `evals/output/cases.jsonl` | present | `f902853cb360` |
| output_schema | `evals/output/schema.json` | present | `28d35c99d721` |
| output_scorecard | `reports/output_quality_scorecard.json` | present | `41110e6fef36` |
| output_execution | `reports/output_execution_runs.json` | present | `873db2e695d4` |
| blind_review | `reports/output_blind_review_pack.json` | present | `755d8ec5f2be` |
| review_adjudication | `reports/output_review_adjudication.json` | present | `bf6fffcf7e45` |
| trigger_scorecard | `reports/route_scorecard.json` | present | `2bdb98da7159` |
| runtime_conformance | `reports/conformance_matrix.json` | present | `e2c8b725bcb2` |
| trust_report | `reports/security_trust_report.json` | present | `bb69f2f7af6b` |
| python_compatibility | `reports/python_compatibility.json` | present | `91e62411f0a8` |
| registry_audit | `reports/registry_audit.json` | present | `1c02c0e72c31` |
| package_verification | `reports/package_verification.json` | present | `e1d47dcd48a6` |
| install_simulation | `reports/install_simulation.json` | present | `16a30c7362fe` |
| skill_os2_audit | `reports/skill_os2_audit.json` | present | `32a901e50902` |
| world_class_evidence_plan | `reports/world_class_evidence_plan.json` | present | `bcfad535672d` |
| world_class_evidence_ledger | `reports/world_class_evidence_ledger.json` | present | `14f5c0b33881` |
| world_class_evidence_intake | `reports/world_class_evidence_intake.json` | present | `45ab4f056438` |
| world_class_evidence_preflight | `reports/world_class_evidence_preflight.json` | present | `d42ad973695c` |
| world_class_submission_review | `reports/world_class_submission_review.json` | present | `ab5b86f3c351` |
| world_class_operator_runbook | `reports/world_class_operator_runbook.json` | present | `d2f25040ff7d` |
| world_class_operator_runbook_markdown | `reports/world_class_operator_runbook.md` | present | `0854da46c6be` |
| world_class_operator_runbook_html | `reports/world_class_operator_runbook.html` | present | `7af76fe20ee9` |
| world_class_claim_guard | `reports/world_class_claim_guard.json` | present | `cbe5eda3c9d0` |

## Reproduction Commands

- `git rev-parse HEAD`
  - evidence: `git commit hash`
- `make eval-suite`
  - evidence: `reports/eval_suite.json`
- `python3 scripts/yao.py output-eval --self`
  - evidence: `reports/output_quality_scorecard.json`
- `python3 scripts/yao.py output-exec --runner-command '["python3","scripts/local_output_eval_runner.py"]' --self`
  - evidence: `reports/output_execution_runs.json`
- `python3 scripts/yao.py output-review --self`
  - evidence: `reports/output_review_adjudication.json`
- `python3 scripts/yao.py skill-ir . --output-json skill-ir/examples/yao-meta-skill.json --self`
  - evidence: `skill-ir/examples/yao-meta-skill.json`
- `python3 scripts/yao.py conformance . --self`
  - evidence: `reports/conformance_matrix.json`
- `python3 scripts/yao.py trust . --self`
  - evidence: `reports/security_trust_report.json`
- `python3 scripts/yao.py python-compat . --self`
  - evidence: `reports/python_compatibility.json`
- `python3 scripts/yao.py package . --platform openai --platform claude --platform generic --platform vscode --expectations evals/packaging_expectations.json --output-dir dist --zip --self`
  - evidence: `dist/yao-meta-skill.zip`
- `python3 scripts/yao.py package-verify . --package-dir dist --require-zip --self`
  - evidence: `reports/package_verification.json`
- `python3 scripts/yao.py install-simulate . --package-dir dist --self`
  - evidence: `reports/install_simulation.json`
- `python3 scripts/yao.py registry-audit . --self`
  - evidence: `reports/registry_audit.json`
- `python3 scripts/yao.py skill-os2-audit . --self`
  - evidence: `reports/skill_os2_audit.json`
- `python3 scripts/yao.py world-class-evidence . --self`
  - evidence: `reports/world_class_evidence_plan.json`
- `python3 scripts/yao.py world-class-ledger . --submissions-dir evidence/world_class/submissions --self`
  - evidence: `reports/world_class_evidence_ledger.json`
- `python3 scripts/yao.py world-class-intake . --submissions-dir evidence/world_class/submissions --self`
  - evidence: `reports/world_class_evidence_intake.json`
- `python3 scripts/yao.py world-class-preflight . --submissions-dir evidence/world_class/submissions --self`
  - evidence: `reports/world_class_evidence_preflight.json`
- `python3 scripts/yao.py world-class-submission-review . --submissions-dir evidence/world_class/submissions --self`
  - evidence: `reports/world_class_submission_review.json`
- `python3 scripts/yao.py world-class-runbook . --submissions-dir evidence/world_class/submissions --self`
  - evidence: `reports/world_class_operator_runbook.json`
- `python3 scripts/yao.py world-class-claim-guard . --self`
  - evidence: `reports/world_class_claim_guard.json`
- `python3 scripts/yao.py evidence-consistency . --self`
  - evidence: `reports/evidence_consistency.json`
- `make ci-test`
  - evidence: `CI target output`

## Failure Disclosure

- path: `evals/failure-cases.md`
- disclosed cases: `3`
- policy: Keep representative failures visible and tied to regression checks.

## Limits

- The git commit and dirty flags are generation-time context; release lock is blocked by source changes, while generated evidence artifacts are tracked separately.
- Local command-runner evidence is reproducible but does not replace provider-backed model holdout evidence.
- Pending blind-review decisions are visible but do not count as human adjudication.
- World-class readiness remains false until external and human evidence gaps close.
- Beta/public testing may proceed without human blind-review only when wording avoids superiority, fully-reviewed, or world-class claims.
