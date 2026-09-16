# 项目会话团队

基于 project-session-team-bootstrap 的角色预设和阶段交接流程，使用 Codex 桌面端原生工具组织团队。当前项目会话担任 Leader，每名成员拥有同一项目内的独立会话；不依赖 Cindy Helper。这里的团队是严格串行的普通项目会话集合，不是并行 worker、Orca team 或隐式共享上下文的机制。

## 职责与约束

- Leader 维护目标、任务、依赖和验收记录，派发当前阶段任务，检查交付物后决定返修或下一步，最终核对整体交付。
- 成员按任务边界执行，阶段结束提交结构化报告；不能自行派单、启动下一角色或将自身完成报告视为 Leader 验收。
- 默认严格串行：先创建全部待命会话，再启动一个阶段；角色可以多次接单，返修复用原会话。
- 用真实会话 ID 和项目 ID 绑定角色，不按标题猜目标，不用临时子代理替代项目栏独立会话。使用稳定的 `team_id`、`ownership_epoch` 和 `dispatch_key` 防止旧结果推进当前流水线；它们降低冲突风险，但不提供原子锁或 exactly-once 保证。
- 每个 work/rework 阶段先通过最小只读能力门；角色报告 `PASS / MISSING / UNKNOWN + evidence`。能力不足时不得把任务写成已开始或已完成。
- 本 skill 只规定流程，不是常驻调度服务。Leader 活跃时通过等待工具收取结果；中断后依靠项目状态恢复，不承诺关掉任务后仍自动运行。

### Decision triage

新建或显式启用讨论的 `work`/`rework` 任务携带 `discussion_policy`；默认值必须原样为 `mode: worker_can_request`、`soft_trigger_threshold: 2`、`max_rounds: 2`、`deadline: Lead-defined`。旧任务没有 `discussion_policy` 时保持既有行为，不隐式获得讨论能力。成员在任务开始时、不可逆工作之前、新证据改变假设之后，以及最终确定跨角色决定之前，按以下规则检查：

```text
Can I complete the task with the current requirements and accepted inputs?
yes -> proceed and record non-blocking assumptions
no + one missing fact/input/permission -> ask Lead or return blocked
no + cross-role options/conflict/high-impact choice -> discussion_request
```

以下任一 hard trigger 都必须先提交 `discussion_request`，再继续依赖该决定的工作：影响其他成员的 API、文件格式、接口或验收合同尚未确定；两个以上可行选项存在实质权衡；另一成员的证据或 accepted output 与当前结论冲突；决定涉及发布、安全、权限、破坏性迁移或其他高影响外部变更；需求的多个解释会产生实质不同结果；错误选择会使大量下游工作失效。

以下 soft trigger 达到两个时必须请求讨论：需要另一角色持有的上下文；关键证据或假设未经核验；无权替另一角色决定；选择会改变下游任务或其 DoD；存在有意义的质量、成本、速度或兼容性权衡。一个 soft trigger 不足以开放讨论：记录假设后继续，或向 Lead 做简单澄清。缺少工具、路径、权限或必需输入应报告 `blocked`，除非解决它本身还要求跨角色决定。

验收时若报告含 `decision_status: unresolved`、冲突证据、未经批准的跨阶段变更或未处理的下游依赖，Lead 必须把它作为 safety net 重新执行 trigger 判断；达到门槛时开放讨论，不能用自动覆盖或直接验收替代。

## 1. 预检与恢复

先读 [Codex 工具规则](codex-tools.md)，检查必需工具是否可调用；缺失时报告缺失能力，不假装已建队，也不自动改用其他平台。

读取项目已有要求、计划和 `.team/team.json`、`.team/tasks.json`（若有），核实当前会话和项目归属。已有团队先提供继续、查看状态、调整团队或结束团队菜单，不重复创建。只查看状态时不启动工作。状态文件不是唯一真相：仍需用会话工具核对真实会话、项目归属和最近回合。

若当前会话无法验证属于目标项目，先解决项目绑定；不要把 projectless 会话标成项目 Leader。只有当前会话 ID 等于已绑定 `leader.thread_id` 时才能继续写账本或派单；从其他会话恢复时只读状态，提示用户打开绑定 Leader 后再继续，不能自动 takeover 或创建第二个 Leader。无法可靠识别当前会话时，展示查询到的候选，让用户指定，不凭最新一条或相似标题猜测。

## 2. 菜单引导

每次只问一个问题，复用已有答案。优先用当前可用的交互问答工具；异步问答发出后可做独立只读预检，但必须收到答案后才能采用该选项。没有菜单工具时用简短文字问题。菜单默认值不等于用户已提交答案。

依次收集：

1. **项目目标**：项目、目标、首要交付物和完成判定。
2. **团队模板**：全栈开发、后端/API、研究与方案或自定义，按需读 [角色预设](role-presets.md)。
3. **成员配置**：唯一 label、显示名称、职责、标题，建议 2–6 名成员；Leader 不计入成员数。预设允许增删修改。
4. **阶段安排**：按序列出负责成员、输入、产物、验收条件和允许修改的范围；返修仍由 Leader 安排。
5. **Lead 路由与运行配置**：默认使用当前会话作为 Leader；已有团队只能由已绑定 Leader 继续。其他会话保持只读，当前版本不执行接管。模型、思考强度沿用宿主默认，只在用户明确要求时设置宿主支持的值，并逐角色列入摘要。
6. **工作目录与门控**：说明实际使用的 checkout/worktree 和交接方式；选择 `automatic`（accepted 后继续）或 `confirmation`（每个阶段 accepted 后再确认）。

最后展示一次具体团队预览：Leader、成员、项目归属、阶段顺序、每个角色的运行配置、门控、工作目录方案，以及新建/复用会话数量。第一次 create、rename 或发送工作消息前必须取得一次明确确认；对象、顺序、门控或 DoD 实质变化时重新确认。用户仅要求设计或预览时不建队。取消时停止尚未执行步骤，如实报告已经发生的操作。

## 3. 建队与绑定

按工具规则将当前会话命名为“项目名 · Leader”，逐个创建成员待命会话，记录真实 ID；需要异步建立 worktree 时先解析为就绪的会话 ID。首条待命通知使用 `attempt=0`，包含项目摘要、角色职责、Leader 标识、等待条件和“只确认待命，不开始项目工作”，不得放入未来阶段的可执行工作。

核验每个会话的标题和项目归属，已有会话仅在用户选定复用时绑定。创建、标题同步、项目列表核验和派单分别记录；有任何绑定未就绪时先修复，不启动首阶段。

建队后按照 [调度与状态协议](team-protocol.md) 保存状态。正式消息首行使用 `[ATW team=<id> epoch=<n> stage=<label> attempt=<n> kind=<standby|work|rework|result|accept|snapshot>]`；将待命回合结束与业务任务完成区分开，未派单的角色始终待启动。

## 4. 阶段调度

1. 为当前阶段生成唯一任务编号与 `dispatch_key`，确认依赖已验收，记录派单意图，再向该成员发送完整任务单。重复发送前先查当前账本、会话历史和可用状态证据。
2. 通过 `wait_threads` 等待该任务回合结束；使用 cursor 收取新事件，不用循环即时快照忙轮询。
3. 匹配 team、epoch、stage、attempt、dispatch key 和来源，检查文件、提交、来源或验证证据。工具显示回合结束不等于任务通过，`queued`/`resumed` 也不等于已开始。
4. 验收通过：记录依据；`automatic` 直接准备下一阶段，`confirmation` 先取得用户确认。返修：递增 attempt，向原角色说明失败 DoD、所需修改和复验方式。阻塞：先解决依赖；需要客户决策时明确问题并暂停派单。
5. 用户中途调整目标时先更新当前阶段与受影响依赖，避免向忙碌成员重复投递；旧 epoch、旧 attempt、错误阶段和重复结果标记为 stale/duplicate，不能通过新版目标验收。

所有计划交付都被验收后，Leader 提供成果位置、验证结果及剩余限制，标记团队 `complete`；不自动归档成员会话。结束/暂停意味着停止新派单，不代表在途回合已经被取消。最后阶段完成只能由 Leader 根据整体 DoD 判断，不能由模板最后一名角色的自述触发。

### 讨论请求与审批生命周期

`discussion_request` 是结构化决策请求，不是聊天邀请，必须包含：

```text
team_id / ownership_epoch / revision_cycle
stage / task_id / dispatch_key
question
why_now
options
evidence
affected_tasks
suggested_participants
suggested_decision_owner
impact_if_wrong
paused_work
```

成员仅暂停依赖未决结论或不可逆的部分，可以继续独立工作。Lead 按 trigger policy 审核请求，选择二至四名既有成员、指定 `decision_owner`、轮次上限和期限，再批准或拒绝；默认最多两轮，期限由 Lead 定义。正常状态流为 `requested -> approved -> open -> proposing/challenging -> decision_pending -> decided -> lead_accepted -> closed`，其中 `proposing` 和 `challenging` 是同一讨论窗口内可交替出现的活动状态；替代终态为 `rejected`、`blocked`、`expired`、`cancelled`。

Worker 负责 triage，并在批准后提交有界的 `proposal`、`challenge`、`evidence` 或 `response`；`decision_owner` 必须选择一个选项或明确升级，并提交 `decision`，说明 rationale、evidence、rejected alternatives 和 affected tasks，不能静默扩大任务范围。Lead 验证完整身份、证据、范围和依赖后，记录 `lead_accepted` 或退回澄清；只有 Lead 可以把 accepted decision 附到原任务并关闭讨论。期限到达时不得继续收取可推进状态的消息；Lead 将讨论标为 `expired`，若 owner 仍无法决定则把依赖工作标为 `blocked`，或只向用户提出一个具体问题。参与者不可用时只能缩减既有 participant set 或标为 `blocked`，不能静默换角色；讨论不能无限保持开放。

讨论是当前任务内的决策子流程，永远不会创建或启动一个后续交付阶段，也不能覆盖 accepted task。`closed` 后原成员按决定恢复工作；后续阶段仍只能在当前任务按正常报告和验收门成为 `accepted` 后，由 Lead 依原 gate 派发。

## 5. 完成后的修改周期

团队已为 `complete` 时，新的用户修改不是原任务的普通返修。绑定 Lead 先将团队置为 `impact_analysis`，核对两个账本、整体完成条件、已接受任务及产物，并查询原成员会话的真实状态。分析必须回答：

1. 用户要求的结果发生了什么变化？
2. 哪些已接受的产物或决策受影响？
3. 哪些产出阶段必须重跑？
4. 哪些下游阶段依赖这些输出，必须返工或复验？
5. 哪些既有验收仍有效，保留它们的证据是什么？
6. 修订后的输入、允许范围、交付物、验证步骤和 DoD 是什么？
7. 串行派单顺序是什么？

Lead 在首次修订派单前写 `.team/revisions/<cycle>.md`，保存原修改请求、上述判断、保留验收的证据、受影响及下游阶段、成员与顺序，以及最终周期验收。已完成首轮是 `revision_cycle: 1`；每次在 `complete` 后收到新的用户修改才单调递增 `revision_cycle`。同一周期内因 DoD 未通过而返修只递增 `attempt`，不增加 cycle。

影响分析完成后，为受影响阶段和必要下游阶段创建带 `revision_cycle`、`supersedes`、`impact_basis` 的新任务记录，并按依赖串行复用原成员。派单键为 `<team_id>/<ownership_epoch>/r<revision_cycle>/<stage>/<attempt>/<kind>`。正常状态流转为 `complete -> impact_analysis -> running -> complete`；若没有任何受影响阶段，在本 cycle 的追加保留记录中写入独立标记 `impact_result: no_affected_stages` 后直接回到 `complete`，不创建或发送成员任务。没有该标记的空 active cycle 不得完成。

只有 active cycle 中每个非 stale 任务都 `accepted`、每个 stale 任务都由同周期或后续 attempt/cycle 的 accepted 任务通过 `supersedes` 指明替代，并且整体完成条件与最终产物复验通过，团队才能重新进入 `complete`。旧 cycle、旧 attempt 或已失效目标的结果只能作为历史证据，不能推进 active cycle。用户在周期进行中再次改变目标时，Lead 暂停新派单、补记影响分析；已派任务不得静默改写，失效结果记为 stale 并以新 key 建立替代任务。

## 6. 输出与恢复

用简短状态说明：团队已就绪/部分完成/待用户处理；当前阶段；成员会话及状态；交付物；下一步。不得把未核验的项目列表可见性、未送达的任务或未验收结果报告为成功。

恢复时先核对真实会话、任务编号、ownership epoch、dispatch key 和最新报告，并先验证当前会话就是绑定 Leader；只续接未完成阶段。创建或发送结果不确定时先查询；明确成功入队的不重发，明确未发送的原目标最多安全重试一次，仍无法判断则 `blocked` 并请求人工核验。详细规则见调度协议。
