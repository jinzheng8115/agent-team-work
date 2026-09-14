# Benchmark Methodology

## Benchmark Types

The package uses deterministic trigger and output checks, a real project smoke run, and generated blind review materials. Provider-backed model execution and human adjudication are separate evidence tracks and are not inferred from local fixtures.

## Sample Sources

- `evals/trigger_cases.json` and `reports/route_scorecard.json` cover owned, adjacent, and no-route requests.
- `evals/output/cases.jsonl` contains five file-backed, boundary, rework, resume, and near-neighbor cases.
- `evals/history/2026-09-14-real-smoke.json` records the Codex project/thread smoke run without private prompts or credentials.

## Evaluation Dimensions

Trigger evaluation measures route precision, recall, ambiguity, and no-route accuracy. Output evaluation measures assertion coverage, baseline comparison, regressions, file-backed handling, and boundary handling. Runtime evidence measures package integrity, installation, target conformance, trust checks, and explicit permission metadata.

## Weighting Rule

Every case is graded against its declared assertions with equal case weight. A release decision must preserve zero route misroutes and zero output regressions; aggregate scores never override a failed safety or identity assertion.

## Failure Disclosure

Known failures and unverified capabilities remain listed in `evals/failure-cases.md`, `reports/limitations-roadmap.md`, and the governed evidence ledger. A recorded fixture pass is labeled as fixture evidence and does not count as a provider call, native permission proof, or human review.

## Reproduction

Run from the skill directory:

```bash
uv run --with pyyaml python /Users/jinzheng/.skills-manager/skills/yao-meta-skill/scripts/yao.py skill-ir . --output-json reports/skill-ir.json
uv run --with pyyaml python /Users/jinzheng/.skills-manager/skills/yao-meta-skill/scripts/yao.py conformance . --output-json reports/conformance_matrix.json --output-md reports/conformance_matrix.md
uv run --with pyyaml python /Users/jinzheng/.skills-manager/skills/yao-meta-skill/scripts/yao.py package . --platform generic --output-dir dist --zip
uv run --with pyyaml python /Users/jinzheng/.skills-manager/skills/yao-meta-skill/scripts/yao.py install-simulate . --package-dir dist
uv run --with pyyaml python /Users/jinzheng/.skills-manager/skills/yao-meta-skill/scripts/yao.py package-verify . --package-dir dist --require-zip
```

