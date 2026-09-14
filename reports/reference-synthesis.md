# Reference Synthesis

Skill: `agent-team-work`
- Description: Use when a user explicitly asks to create or continue a Codex project team with one Leader and independent role sessions visible in the project sidebar, then dispatch work strictly by accepted stages. 用于菜单组建团队、创建项目会话团队、阶段派单、汇报、验收和恢复；不用于解释概念、编写或修改 skill、单次会话管理、普通子代理、并行 worker 或 Orca team。
- Intent confidence: `100/100` (`high`)

## Live GitHub Benchmarks

- No live GitHub benchmarks are attached yet.

## Curated World-Class Pattern Tracks

### Official skill anatomy and context discipline
- Type: `official`
- Evidence mode: `curated-pattern-track`
- Why relevant: This track matches: general fit.
- Borrow: Borrow progressive disclosure: keep the entrypoint lean and move depth into references or scripts.
- Avoid: Do not let packaging or platform concerns swallow the core job boundary.

### Hypothesis-test-learn loop
- Type: `research`
- Evidence mode: `curated-pattern-track`
- Why relevant: This track matches: general fit.
- Borrow: Borrow a small hypothesis-test-learn loop so the first revision is evidence-backed.
- Avoid: Do not create experimental overhead that exceeds the skill's real risk tier.

### Outcome-backwards design
- Type: `principles`
- Evidence mode: `curated-pattern-track`
- Why relevant: This track matches: output.
- Borrow: Borrow the habit of designing from the required hand-back output backwards.
- Avoid: Do not start with architecture terms before the deliverable is concrete.

## Borrow Now

- Borrow progressive disclosure: keep the entrypoint lean and move depth into references or scripts.
- Borrow a small hypothesis-test-learn loop so the first revision is evidence-backed.
- Borrow the habit of designing from the required hand-back output backwards.

## Avoid Now

- Do not let packaging or platform concerns swallow the core job boundary.
- Do not create experimental overhead that exceeds the skill's real risk tier.
- Do not start with architecture terms before the deliverable is concrete.

## Pattern Gate

- Summary: 1 accepted, 2 deferred using threshold 4/4.
- Acceptance threshold: `4/4`
- Accepted patterns:
  - **Outcome-backwards design**: 4/4 (recurrence, generativity, distinctiveness, boundary)
- Deferred patterns:
  - **Official skill anatomy and context discipline**: missing distinctiveness
  - **Hypothesis-test-learn loop**: missing distinctiveness

## Default Recommendation

- Summary: Start by borrowing this pattern: Borrow progressive disclosure: keep the entrypoint lean and move depth into references or scripts. Avoid this for the first pass: Do not let packaging or platform concerns swallow the core job boundary.
- Why: Intent is clear enough, so the system should make the first pattern call quietly.
- User decision required: `False`

## Visibility Mode

- Mode: `silent`
- User note: Apply the synthesis quietly unless uncertainty or a real design conflict appears.
- Reviewer note: Keep the full benchmark and synthesis evidence visible for authors and reviewers.

## Conflict Check

- No material design conflict detected. Keep the synthesis silent for the user.

## Quality Lift Thesis

- Use GitHub repositories for concrete package and workflow patterns.
- Use curated official or commercial tracks for entrypoint and operator ergonomics.
- Use research tracks to justify the smallest evaluation loop that still catches regressions.
- Use principle tracks to keep the package small, boundary-aware, and outcome-driven.

## Decision Prompt

Use the recommendation by default. Only surface the underlying benchmark tradeoffs when intent is uncertain or a real design conflict needs a deliberate call.
