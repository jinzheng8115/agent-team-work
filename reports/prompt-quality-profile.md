# Prompt Quality Profile

Skill: `agent-team-work`
Relevance: `prompt-heavy`
Overall quality score: `90.0/100`

## Primary Task Family

**Execution operation**
- Matched keywords: workflow, checklist, 流程, 执行, 清单

## Complexity

- Band: `expert`
- Score: `26`
- Reason: multiple task families plus governance, evaluation, or expert-level constraints

## Need Model

- Explicit Need: 在项目开始时通过菜单组建一个由当前会话担任 Leader、多个独立项目会话担任成员的 Codex 团队，并按阶段派单、收取报告、验收和恢复，直到整体交付完成或明确阻塞。
- Implicit Need: The reusable skill needs a stable role, task, and output contract rather than a one-off prompt.
- Scenario: 用户确认的项目目标、首要交付物和完成判定, 已保存 Codex 项目及其 project_id、Git 或 local 工作目录信息, 成员角色、职责、标题、阶段顺序、输入依赖和允许路径, team.json、tasks.json、成员报告和 Codex 项目/thread 查询结果
- User Level: infer from examples and standards; ask only if it changes output depth
- Success Standard: 阶段严格串行，只有 Leader 验收后才能推进, 任务与报告包含 team、epoch、stage、attempt、dispatch_key 身份字段, 创建、标题、项目归属、送达和验收分别提供证据, 缺失或不确定证据明确标记为 MISSING 或 UNKNOWN，不虚构结果

## RTF To Skill Mapping

- Role: Use an operator role with explicit boundaries, inputs, outputs, and failure handling.
- Task: Convert the job into ordered steps with validation checks and stop conditions.
- Format: Return a runbook-like handoff with commands, checks, owners, and next actions when relevant.

## Quality Matrix

### Completeness — 100/100
- Matched signals: example, 输入, 约束
- Repair: Name missing inputs, outputs, constraints, or success standards before deepening the package.

### Clarity — 85/100
- Matched signals: 明确
- Repair: Replace broad verbs with observable actions and define what done means.

### Consistency — 85/100
- Matched signals: 边界
- Repair: Check that role, task, format, exclusions, and examples do not contradict each other.

### Practicality — 95/100
- Matched signals: use, workflow, 执行, 使用
- Repair: Add runnable steps, examples, or verification cues instead of abstract advice.

### Specificity — 85/100
- Matched signals: 用户
- Repair: Anchor wording in the user's audience, domain nouns, and target outcome.

## Matched Task Families

### Execution operation
- Score: `5`
- Keywords: workflow, checklist, 流程, 执行, 清单
- Role: Use an operator role with explicit boundaries, inputs, outputs, and failure handling.
- Task: Convert the job into ordered steps with validation checks and stop conditions.
- Format: Return a runbook-like handoff with commands, checks, owners, and next actions when relevant.

### Creative generation
- Score: `1`
- Keywords: 标题
- Role: Use a taste-aware creator role with clear audience, tone, and originality boundaries.
- Task: Generate variants, explain selection logic, and preserve the user's distinctive constraints.
- Format: Return options with rationale, selection criteria, and refinement paths.

### Prompt engineering
- Score: `1`
- Keywords: role
- Role: Use a prompt engineer role only when role design materially improves execution.
- Task: Map Role, Task, and Format into skill behavior rather than copying a large prompt template.
- Format: Return a compact prompt contract plus tests, quality matrix, and usage notes.

## Self-Repair Checks

- Check explicit need, implicit need, scenario, user level, and success standard before deepening.
- Map Role, Task, and Format into skill behavior, not decorative prompt labels.
- Ask one focused clarification only when missing information changes the package boundary.
- Add tests or examples for prompt-heavy behavior before treating it as reusable.
- Keep prompt methodology in references and reports instead of bloating SKILL.md.

## Reviewer Note

Use this profile when the package depends on prompt behavior, role design, output contracts, or conversation quality.
