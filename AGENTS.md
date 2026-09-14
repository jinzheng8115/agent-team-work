# agent-team-work release instructions

This file is contributor guidance for refreshing evidence from a Yao Meta Skill engine checkout. The standalone package does not bundle the engine CLI; use the absolute target path when invoking it. The command forms below remain the canonical release flow.

After source changes that affect scripts, package contents, trust evidence, Review Studio, registry metadata, or generated reports, refresh the release evidence before final sign-off:

```bash
GENERATED_AT="${GENERATED_AT:-$(date +%F)}"
python3 scripts/compile_skill.py . --generated-at "$GENERATED_AT"
python3 scripts/cross_packager.py . --platform openai --platform claude --platform generic --platform vscode --expectations evals/packaging_expectations.json --output-dir dist --zip
python3 scripts/simulate_install.py . --package-dir dist --install-root dist/install-simulation --output-json reports/install_simulation.json --output-md reports/install_simulation.md --generated-at "$GENERATED_AT"
python3 scripts/trust_check.py . --output-json reports/security_trust_report.json --output-md reports/security_trust_report.md
python3 scripts/registry_audit.py . --generated-at "$GENERATED_AT"
python3 scripts/verify_package.py . --package-dir dist --expectations evals/packaging_expectations.json --registry-json reports/registry_audit.json --output-json reports/package_verification.json --output-md reports/package_verification.md --require-zip --generated-at "$GENERATED_AT"
python3 scripts/registry_audit.py . --generated-at "$GENERATED_AT"
python3 scripts/upgrade_check.py . --previous-package-json registry/examples/yao-meta-skill-1.0.0.json --current-package-json reports/registry_audit.json --output-json reports/upgrade_check.json --output-md reports/upgrade_check.md --generated-at "$GENERATED_AT"
python3 scripts/render_adoption_drift_report.py . --generated-at "$GENERATED_AT"
python3 scripts/render_architecture_maintainability.py . --generated-at "$GENERATED_AT"
python3 scripts/python_compat_check.py . --generated-at "$GENERATED_AT"
python3 scripts/probe_runtime_permissions.py . --package-dir dist
python3 scripts/render_review_waivers.py . --generated-at "$GENERATED_AT"
python3 scripts/render_review_annotations.py .
python3 scripts/build_skill_atlas.py --workspace-root . --output-dir skill_atlas --report-html reports/skill_atlas.html --report-json reports/skill_atlas.json --today "$GENERATED_AT"
python3 scripts/render_world_class_evidence_plan.py . --generated-at "$GENERATED_AT"
python3 scripts/render_world_class_evidence_ledger.py . --generated-at "$GENERATED_AT"
python3 scripts/render_world_class_evidence_intake.py . --generated-at "$GENERATED_AT"
python3 scripts/render_world_class_submission_review.py . --generated-at "$GENERATED_AT"
python3 scripts/render_world_class_operator_runbook.py . --generated-at "$GENERATED_AT"
python3 scripts/render_world_class_claim_guard.py . --generated-at "$GENERATED_AT"
python3 scripts/render_daily_skillops_report.py . --generated-at "$GENERATED_AT"
python3 scripts/render_weekly_curator_report.py . --generated-at "$GENERATED_AT"
python3 scripts/render_skill_os2_audit.py . --generated-at "$GENERATED_AT"
python3 scripts/render_skill_os2_coverage.py . --generated-at "$GENERATED_AT"
python3 scripts/render_context_reports.py --generated-at "$GENERATED_AT"
python3 scripts/render_benchmark_reproducibility.py . --generated-at "$GENERATED_AT"
python3 scripts/render_skill_overview.py .
python3 scripts/render_skill_interpretation.py .
python3 scripts/render_review_viewer.py .
python3 scripts/render_world_class_preflight.py . --generated-at "$GENERATED_AT"
python3 scripts/render_review_studio.py . --output-html reports/review-studio.html --output-json reports/review-studio.json
python3 scripts/render_evidence_consistency.py . --generated-at "$GENERATED_AT"
```

`reports/output_execution_runs.json` is the immutable legacy provider baseline. Do not replace it with the local runner during routine report refresh. Phase 1 Provider evidence is generated inside `evidence-build` runs and promoted through the evidence publication protocol.

For final release evidence, commit source and generated package evidence first, then run the clean-lock reports from a clean worktree:

```bash
python3 scripts/render_context_reports.py --generated-at "$GENERATED_AT"
python3 scripts/render_benchmark_reproducibility.py . --generated-at "$GENERATED_AT"
python3 scripts/render_daily_skillops_report.py . --generated-at "$GENERATED_AT"
python3 scripts/render_weekly_curator_report.py . --generated-at "$GENERATED_AT"
python3 scripts/render_skill_overview.py .
python3 scripts/render_skill_interpretation.py .
python3 scripts/render_review_viewer.py .
python3 scripts/render_world_class_preflight.py . --generated-at "$GENERATED_AT"
python3 scripts/render_review_studio.py . --output-html reports/review-studio.html --output-json reports/review-studio.json
python3 scripts/render_evidence_consistency.py . --generated-at "$GENERATED_AT"
```

If `reports/benchmark_reproducibility.json` reports `release_lock_ready: false`, keep the release blocked until the source commit and clean-lock report are reconciled.
