# Output Execution Runs

This report records how output-eval variants were produced and whether timing or token evidence is observed or estimated.

- Cases: `5`
- Variant runs: `10`
- Command executed: `10`
- Model executed: `0`
- Recorded fixtures: `0`
- Timing observed: `10`
- Token observed: `0`
- Token estimated: `10`
- Delta: `100.0`
- Gate pass: `True`

No model-executed runs are recorded yet.

Use `python3 scripts/yao.py output-exec --provider-runner openai --self` or `--runner-command` with a reviewed provider-backed runner to replace recorded fixtures with real model output evidence.

Command runner evidence is present. This proves the eval harness executed an external command, but it is not provider-backed model evidence unless the runner reports model metadata.

## Runs

| Case | Variant | Mode | Model | Duration ms | Tokens | Score | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| team-bootstrap | baseline | command | local-output-eval-runner | 25.97 | 12 | 0.0 | pass |
| team-bootstrap | with_skill | command | local-output-eval-runner | 25.73 | 40 | 100.0 | pass |
| serial-gate | baseline | command | local-output-eval-runner | 24.37 | 10 | 0.0 | pass |
| serial-gate | with_skill | command | local-output-eval-runner | 24.65 | 33 | 100.0 | pass |
| rework-safety | baseline | command | local-output-eval-runner | 24.49 | 9 | 0.0 | pass |
| rework-safety | with_skill | command | local-output-eval-runner | 25.2 | 29 | 100.0 | pass |
| resume-ledger | baseline | command | local-output-eval-runner | 24.28 | 6 | 0.0 | pass |
| resume-ledger | with_skill | command | local-output-eval-runner | 24.77 | 46 | 100.0 | pass |
| near-neighbor-explanation | baseline | command | local-output-eval-runner | 23.95 | 11 | 0.0 | pass |
| near-neighbor-explanation | with_skill | command | local-output-eval-runner | 24.2 | 24 | 100.0 | pass |

## Next Fixes

- Keep recorded fixtures as reproducible baselines, but do not describe them as model-executed evidence.
- Use `scripts/provider_output_eval_runner.py` for provider-backed holdout cases when release confidence depends on real generation behavior.
- Compare timing, token cost, and assertion deltas before promoting a skill to governed reuse.
