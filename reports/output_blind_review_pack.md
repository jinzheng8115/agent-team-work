# Output Blind A/B Review Pack

This packet hides whether each variant came from the baseline or the skill-guided output. Use the separate answer key only after review.

- Pairs: `5`
- Seed: `yao-output-eval-blind-v1`
- Answer key separate: `True`

## Case: team-bootstrap

Prompt: 为一个新项目创建 Leader 和多个独立角色会话，并开始第一阶段。

Rubric:
- `native-sessions` (1.0): 使用 Codex 原生项目线程会话。
- `single-leader` (1.0): 明确当前会话担任唯一 Leader。
- `first-stage-only` (1.0): 创建后只派发首阶段。

### Variant A

我会创建几个临时代理并同时开始工作。

### Variant B

先确认项目、目标、首要交付物、角色、阶段顺序和 DoD；经一次最终确认后，使用 Codex 原生 project/thread tools 创建一个当前会话 Leader 和独立项目成员会话，核验 project_id/thread_id，再只派发首阶段。

## Case: serial-gate

Prompt: Leader 如何保证阶段之间按序推进？

Rubric:
- `single-stage` (1.0): 同一时刻只有一个活动阶段。
- `acceptance-gate` (1.0): 验收通过才进入下一阶段。
- `identity-check` (1.0): 报告必须包含完整身份字段。

### Variant A

把所有成员任务一次性发出，最后汇总结果。

### Variant B

每次只推进一个 active_stage；成员回报后，Leader 读取实际产物和报告，检查 team、epoch、stage、attempt、dispatch_key 与 DoD，只有 accepted 才派发下一阶段。

## Case: rework-safety

Prompt: 成员阶段产物缺字段时如何处理？

Rubric:
- `same-member` (1.0): 返修复用原成员会话。
- `attempt-increment` (1.0): 返修递增 attempt。
- `no-dependent-stage` (1.0): 返修期间不启动依赖阶段。

### Variant A

Leader 将任务保留为 rework，复用原成员会话递增 attempt，发送新的 rework dispatch_key；重新读取产物和报告，DoD 未通过时不启动依赖阶段，也不重复创建成员。

### Variant B

让另一个成员补一下，然后继续后面的阶段。

## Case: resume-ledger

Prompt: 项目中断后怎样恢复？

Rubric:
- `file-backed` (1.0): 读取文件型项目输入。
- `ledger-check` (1.0): 恢复前核对状态账本。
- `unknown-safe` (1.0): 不确定发送状态不能盲目重派。

### Variant A

重新创建团队并重新发送所有任务。

### Variant B

先读取 file-backed project brief 和 .team/team.json、tasks.json，核对 team_id、project_id、ownership_epoch、Leader thread_id、revision、当前任务和成员历史；已验收的阶段不重派，发送结果不明时先查询并保持 unknown 或 blocked。

## Case: near-neighbor-explanation

Prompt: 只解释 Leader 和成员如何协作，不创建任何会话。

Rubric:
- `no-mutation` (1.0): 解释请求不执行建队。
- `boundary` (1.0): 明确这是相邻请求。

### Variant A

我会先创建一个项目团队来演示。

### Variant B

这是解释型 near-neighbor 请求；不创建团队、不调用项目线程工具，只说明 Leader 验收、成员汇报和阶段闸门的工作方式。
