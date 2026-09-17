# Benchmark Reproducibility

Generated at: `2026-09-17`
Commit: `896c1e018383804eaa606f4f4ad0e3acc38a561b`
Working tree dirty at generation: `true`
Source tree dirty at generation: `true`
Generated evidence dirty at generation: `true`
Evidence bundle SHA256: `ba17758838587c77229a9067b6b2ba429d99d6fe8f14268d7b795a2a5ac8aec7`

## Summary

- reproducibility ready: `true`
- release lock ready: `false`
- methodology complete: `true`
- required artifacts: `25`
- missing artifacts: `0`
- source contract sha256: `b2cb5bbf2289`
- archive sha256: `97a16b203263`
- output cases: `13`
- disclosed failure cases: `3`
- reproduction commands: `23`
- provider evidence complete: `false`
- phase-one provider matrix complete: `false`
- phase-one three-reviewer adjudication complete: `false`
- phase-one quality promotion complete: `false`
- human review complete: `false`
- world-class ready: `false`
- world-class source checks: `6` pass / `14` total; `8` blocked
- beta test ready: `false`
- beta test blockers: `2`
- beta deferred evidence: `4`
- public claim ready: `false`
- public claim blockers: `7`
- changed files at generation: `36`
- source changed files at generation: `7`
- generated changed files at generation: `29`

This report proves local benchmark reproducibility only. It keeps external provider and human-review gaps visible instead of counting them as complete. The git commit and dirty samples are generation-time context; the evidence bundle SHA is the durable anchor for the artifacts listed below.

## Beta Test Boundary

- ready: `false`
- scope: beta/public test release without superiority, fully-reviewed, or world-class claims
- policy: Human blind-review, native permission enforcement, real client telemetry, and ledger acceptance may be deferred for beta/public testing, but public claims must remain blocked until those evidence entries are accepted.
- required wording: Use beta, public test, or technical preview wording; do not claim world-class readiness, fully reviewed quality, or proven superiority over baseline.

| Blocker |
| --- |
| release lock is not clean or commit is unavailable |
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
| release lock is not clean or commit is unavailable |
| provider-backed model holdout evidence is incomplete |
| human blind-review adjudication is incomplete |
| phase-one provider matrix is incomplete |
| phase-one three-reviewer adjudication is incomplete |
| world-class evidence is not accepted yet (4 open gaps, 4 ledger pending) |
| world-class source checks are not all accepted (6/14 pass, 8 blocked) |

## Release Lock

- ready: `false`
- reason: source files were dirty at generation time
- status scope: generation-time status before this report is written

## Evidence Bundle

- algorithm: `sha256(path,label,exists,artifact_sha256)`
- artifacts: `25` / `25`
- sha256: `ba17758838587c77229a9067b6b2ba429d99d6fe8f14268d7b795a2a5ac8aec7`

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
| output_cases | `evals/output/cases.jsonl` | present | `df29164839db` |
| output_schema | `evals/output/schema.json` | present | `28d35c99d721` |
| output_scorecard | `reports/output_quality_scorecard.json` | present | `41110e6fef36` |
| output_execution | `reports/output_execution_runs.json` | present | `873db2e695d4` |
| blind_review | `reports/output_blind_review_pack.json` | present | `755d8ec5f2be` |
| review_adjudication | `reports/output_review_adjudication.json` | present | `bf6fffcf7e45` |
| trigger_scorecard | `reports/route_scorecard.json` | present | `2bdb98da7159` |
| runtime_conformance | `reports/conformance_matrix.json` | present | `e2c8b725bcb2` |
| trust_report | `reports/security_trust_report.json` | present | `aea18c1c82e4` |
| python_compatibility | `reports/python_compatibility.json` | present | `a20ffbb20193` |
| registry_audit | `reports/registry_audit.json` | present | `2513d70c0508` |
| package_verification | `reports/package_verification.json` | present | `7dd9714e343b` |
| install_simulation | `reports/install_simulation.json` | present | `9bb30e02bdc1` |
| skill_os2_audit | `reports/skill_os2_audit.json` | present | `597f988b10b5` |
| world_class_evidence_plan | `reports/world_class_evidence_plan.json` | present | `509a79b8c86f` |
| world_class_evidence_ledger | `reports/world_class_evidence_ledger.json` | present | `e6690b2a0a63` |
| world_class_evidence_intake | `reports/world_class_evidence_intake.json` | present | `3f81fd94e378` |
| world_class_evidence_preflight | `reports/world_class_evidence_preflight.json` | present | `e35e86308bc2` |
| world_class_submission_review | `reports/world_class_submission_review.json` | present | `19b4f81071aa` |
| world_class_operator_runbook | `reports/world_class_operator_runbook.json` | present | `408c9491cacb` |
| world_class_operator_runbook_markdown | `reports/world_class_operator_runbook.md` | present | `a092c2121a84` |
| world_class_operator_runbook_html | `reports/world_class_operator_runbook.html` | present | `26539e126ddc` |
| world_class_claim_guard | `reports/world_class_claim_guard.json` | present | `2f8220a2005f` |

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
