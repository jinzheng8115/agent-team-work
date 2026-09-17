---
name: agent-team-work
description: "Use when a user explicitly asks to create or continue a Codex project team with one Leader and independent role sessions visible in the project sidebar, then dispatch work strictly by accepted stages. 也用于团队完成后的修改：Lead 先做影响分析、启动修订周期，再只派受影响阶段和必要下游并复用原成员。用于创建/继续项目会话团队、阶段派单、验收和恢复；不用于解释概念、编写或修改 skill、单次会话管理、普通子代理、并行 worker 或 Orca team。"
---

# 项目会话团队

菜单建队，Leader 验收后逐阶段推进，产出独立会话与可恢复的项目状态。基于 project-session-team-bootstrap 改编，使用 Codex 原生会话工具，不依赖 Cindy Helper。

本版本只支持一个当前会话 Leader 加普通独立角色会话的严格串行流水线；不支持并行 worker、Orca team、Sub-Lead 或子团队。

## 执行入口

- 新建团队：读 [工作流程](references/workflow.md)、[工具规则](references/codex-tools.md) 和 [Worker 可读回报契约](references/worker-readable-report.md)，核实项目与当前 Leader；菜单确认目标、角色、阶段、门控及工作目录。新任务需要 worker-to-worker 决策时，按工作流程中的 Decision triage 和讨论生命周期执行。
- 选择角色：按需读 [角色预设](references/role-presets.md) 和 [角色能力门](references/role-capabilities.md)，允许增删修改。
- 继续或查看团队：先读 [状态协议](references/team-protocol.md) 和现有 `.team/` 记录，再核验真实会话、当前 Leader 和 ownership epoch，不重复建队。讨论恢复也必须核对讨论记录、消息身份和真实会话；只查状态时不派单。

## 调度约束

当前项目会话为默认 Leader；它本身就是项目栏中的 Leader 会话，不另建隐形协调器。只有与 `team.json.leader.thread_id` 完全匹配的当前会话可以写账本、派单或验收；其他会话只能读取状态并引导用户回到已绑定 Leader，不创建第二个 Leader，也不代写账本。成员使用同一项目内真实独立会话，禁止用普通子代理或临时子代理替代。全部创建并核验后只启动当前阶段。待命回复不算任务完成；成员报告需匹配 team、epoch、stage、attempt 和 dispatch key，Leader 检查产物后才能验收和派发下一阶段。返修复用原成员。

Worker-to-worker discussion 是当前阶段内、由成员请求且由 Lead 批准的有界决策能力，必须由共享 transcript 中真实可见的 peer 交换支撑；Lead 只用私下征询不能替代，且不得在 `lead_accepted` 前派发下一阶段。完整触发、生命周期、消息身份与恢复规则见 [工作流程](references/workflow.md) 和 [状态协议](references/team-protocol.md)。成员不能自行开放/关闭讨论、修改两个 JSON 账本、验收任务或派发后续阶段；该能力不引入并行 worker、Orca team、Sub-Lead、子团队或自主阶段调度，现有串行 stage gate 和 Lead 验收继续适用；没有讨论 marker 的 legacy 团队仍保持原行为。

默认门控为 `automatic`：阶段 accepted 后继续下一阶段；用户选择 `confirmation` 时，每个 accepted 之后、下一次派单之前再确认。跨 worktree 交接先核验产物可访问。创建或派单结果不明时先查询，不重复执行。Leader 活跃时通过等待工具收取报告；中断后恢复状态，不承诺后台常驻。

团队 `complete` 后收到用户修改请求时，Lead 先进入 `impact_analysis`，读取首轮验收和真实成员状态，递增 cycle 并写 `.team/revisions/<cycle>.md`，按影响范围创建新 cycle 的任务；完成影响分析前不得向成员发送修改消息。受影响阶段仍复用原成员，并沿用能力门、报告、验收、gate 和恢复规则。分析确认没有受影响阶段时，在该追加保留的修订记录中写入独立标记 `impact_result: no_affected_stages`，不派单并直接回到 `complete`；没有此标记的空 active cycle 不能完成。旧 cycle 的结果只能作为历史证据，未来 cycle 的任务或派单键也不能推进当前 cycle。

## 输入与交付契约

每次运行先把以下信息写入菜单摘要和 `.team/team.json`：项目归属与允许的 checkout、目标和首要交付物、完成判定、成员职责与阶段顺序、输入/依赖路径、工作范围，以及 `automatic` 或 `confirmation` 门控。成员回报遵循 [Worker 可读回报契约](references/worker-readable-report.md)：最终回复必须含独立标题行 `Human-readable summary` 和 `Technical details`，字段不能顶替标题；身份和技术日志保留为机器证据，用户默认先看到角色结论、产物、验证、风险和下一步。缺少目标项目、首要交付物或完成判定时停在菜单，不创建会话。

交付必须包含可核验的团队绑定（真实 `project_id`、`thread_id`、标题与项目归属）、逐阶段任务与报告（身份字段、产物绝对路径、验证结果），以及最终状态和下一步；未查询到的创建、送达或验收事实标为 `unknown`。

## 交付

报告团队就绪情况、当前阶段、成员状态、成果和下一步，并按宿主要求附真实创建会话入口。工具不可用或项目归属无法核实时说明缺口，不声称已创建或完成。

Codex 与通用 agent-skills 的元数据差异及运行依赖边界见 [工具规则](references/codex-tools.md)；评测、报告和发布检查属于源码仓库维护资产，不是 Skill 运行依赖。
