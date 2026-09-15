---
name: agent-team-work
description: "Use when a user explicitly asks to create or continue a Codex project team with one Leader and independent role sessions visible in the project sidebar, then dispatch work strictly by accepted stages. 用于菜单组建团队、创建项目会话团队、阶段派单、汇报、验收和恢复；不用于解释概念、编写或修改 skill、单次会话管理、普通子代理、并行 worker 或 Orca team。"
---

# 项目会话团队

菜单建队，Leader 验收后逐阶段推进，产出独立会话与可恢复的项目状态。基于 project-session-team-bootstrap 改编，使用 Codex 原生会话工具，不依赖 Cindy Helper。

本版本只支持一个当前会话 Leader 加普通独立角色会话的严格串行流水线；不支持并行 worker、Orca team、Sub-Lead 或子团队。

## 执行入口

- 新建团队：读 [工作流程](references/workflow.md) 和 [工具规则](references/codex-tools.md)，核实项目与当前 Leader；菜单确认目标、角色、阶段、门控及工作目录。
- 选择角色：按需读 [角色预设](references/role-presets.md)，允许增删修改。
- 继续或查看团队：先读 [状态协议](references/team-protocol.md) 和现有 `.team/` 记录，再核验真实会话、当前 Leader 和 ownership epoch，不重复建队。只查状态时不派单。

## 调度约束

当前项目会话为默认 Leader；它本身就是项目栏中的 Leader 会话，不另建隐形协调器。只有与 `team.json.leader.thread_id` 完全匹配的当前会话可以写账本、派单或验收；其他会话只能读取状态并引导用户回到已绑定 Leader，不创建第二个 Leader，也不代写账本。成员使用同一项目内真实独立会话，禁止用普通子代理或临时子代理替代。全部创建并核验后只启动当前阶段。待命回复不算任务完成；成员报告需匹配 team、epoch、stage、attempt 和 dispatch key，Leader 检查产物后才能验收和派发下一阶段。返修复用原成员。

默认门控为 `automatic`：阶段 accepted 后继续下一阶段；用户选择 `confirmation` 时，每个 accepted 之后、下一次派单之前再确认。跨 worktree 交接先核验产物可访问。创建或派单结果不明时先查询，不重复执行。Leader 活跃时通过等待工具收取报告；中断后恢复状态，不承诺后台常驻。

团队 `complete` 后收到用户修改请求时，Lead 先进入 `impact_analysis`，读取首轮验收和真实成员状态，写 `.team/revisions/<cycle>.md`，按影响范围创建新 cycle 的任务；完成影响分析前不得向成员发送修改消息。受影响阶段仍复用原成员，并沿用能力门、报告、验收、gate 和恢复规则。分析确认没有受影响阶段时，不派单并直接回到 `complete`；旧 cycle 的结果只能作为历史证据，不能推进新 cycle。

## 输入与交付契约

每次运行先把以下信息写入菜单摘要和 `.team/team.json`：项目归属与允许的 checkout、目标和首要交付物、完成判定、成员职责与阶段顺序、输入/依赖路径、工作范围，以及 `automatic` 或 `confirmation` 门控。缺少目标项目、首要交付物或完成判定时停在菜单，不创建会话。

交付必须包含可核验的团队绑定（真实 `project_id`、Leader/member `thread_id`、标题和项目归属证据）、逐阶段任务与报告（`task_id`、`attempt`、身份字段、产物绝对路径和验证结果），以及最终 `complete`、`blocked` 或待用户处理状态和下一步。任何未查询到的创建、送达、侧边栏可见性或验收事实都标为 `unknown`，不能写成成功。

维护者可用 `scripts/ci_test.py` 运行无依赖发布检查，`scripts/validate_team_state.py` 校验 `.team/` 账本；`scripts/local_output_eval_runner.py` 只回放固定 fixture 以验证评估管线，不代表 provider 模型运行。

## 交付

报告团队就绪情况、当前阶段、成员状态、成果和下一步，并按宿主要求附真实创建会话入口。工具不可用或项目归属无法核实时说明缺口，不声称已创建或完成。

维护者的触发样例位于 `evals/`，检查证据与验证范围位于 `reports/`；正常建队不必读取。Codex 与通用 agent-skills 元数据的差异见 [工具规则](references/codex-tools.md)。真实试跑按 [端到端冒烟清单](references/e2e-smoke-checklist.md) 留证。需要了解能力门、规模边界、完整串行案例或已知失败时，按需读取 `references/role-capabilities.md`、`references/team-scaling.md`、`examples/serial-pipeline.md` 和 `failures/README.md`。
