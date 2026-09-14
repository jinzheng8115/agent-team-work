# 调度与状态协议

## 项目状态

在用户选定的项目根目录维护 `.team/`。如果已有同名目录但不是本 skill 的数据，先选择其他状态目录，不覆盖。所有任务单都带上该目录的绝对路径；不同 worktree 使用同一个 Leader 状态目录，不能各自初始化一套。

- `team.json`：`schema_version`（本版为 2）、`skill`（agent-team-work）、`team_id`、`project_id`、`project_root`、`goal`、`completion_criteria`、`status`、`gate`（`automatic`/`confirmation`）、`ownership_epoch`、`active_stage`、`leader`、`members`。
- `leader`：真实 `thread_id`、可用的 `host_id`、`title`。每个 member：`label`、`role`、`responsibility`、`title`、`thread_id`、`host_id`、`client_thread_id`（仅 pending）、`checkout_path`、`created`、`title_synced`、`project_verified`、`status`。
- `tasks.json`：`schema_version`、`team_id`、`revision`、`last_writer_thread_id`、`current_task_id`、`tasks`。每项任务：`task_id`、`attempt`、`role_label`、`objective`、`inputs`、`allowed_paths`、`deliverables`、`acceptance_criteria`、`dependencies`、`status`、`dispatch_state`、`dispatch_key`、`report_path`、`wait_cursor`、`acceptance`。`dispatch_key` 固定为 `<team_id>/<ownership_epoch>/<stage>/<attempt>/<kind>`。
- `reports/<task_id>-<attempt>.md`：阶段报告。一个任务尝试一份报告，不覆盖旧报告；成员只写自己获派的报告，不能修改团队或任务账本。

维护者可运行 `python3 scripts/validate_team_state.py .team` 做只读账本校验；它不能替代 Leader 对真实会话、产物和报告的验收。

Leader 是两个 JSON 账本的唯一写入者。写入前必须确认当前会话 ID 等于 `team.json.leader.thread_id`，读取两个账本并记下 `revision`；写入时保留已绑定 ID 和未受影响任务，写入 `last_writer_thread_id`，使用临时文件加原子替换并递增 revision。执行会话工具后再次读取账本；若 revision 已变化，停止后续 mutation，记录 `blocked`/`conflict` 并由绑定 Leader 重新核对。`ownership_epoch` 首次绑定为 1；只有明确的用户接管流程才能递增，当前版本不自动执行跨 Leader takeover。跨文件更新中断时，先核对 team_id、current_task_id、epoch、revision 和实际会话再修复，不根据单个文件推断成功。该单写者版本栅栏降低重复派单风险；账本仍不是跨进程原子锁，不能宣称 exactly-once 或后台常驻监督。

角色状态可为 pending、waiting、working、blocked；团队可为 ready、running、paused、blocked、complete。任务状态可为 planned、sending、dispatched、reported、accepted、rework、blocked、stale、duplicate。分别记录创建、标题、项目核验，不能用一个 ready 值代替所有证据。

## 任务单

## 能力门

每个 `work`/`rework` 由目标角色先做最小、只读探测：核对工作目录和输入路径可读；按 DoD 用 `command -v`、工具发现或等价方式确认所需工具；确认回传 Leader 的能力可用。只记录当前阶段真正需要的项目，避免为文档任务强制数据库或浏览器。核心项全部为 `PASS` 才能记录 `started`；`MISSING` 或 `UNKNOWN` 时不执行项目修改，返回 `blocked` 和证据。探测结果应随 `result` 或 `blocked` 回传，Lead 不能由发送成功推断能力门通过。

每次派单包含以下内容，不仅发送一段角色人设：

```text
`[ATW team=<id> epoch=<n> stage=<label> attempt=<n> kind=<standby|work|rework|result|accept|snapshot>]`
Team / Task / Attempt：实际团队编号、任务编号、本次尝试次数
Role：目标成员 label 与职责
Objective：本阶段具体目标
Inputs/Dependencies：项目摘要、已确认决策、前序验收摘要与可读取的产物绝对路径
Capability Gate：本阶段最小能力探测、PASS/MISSING/UNKNOWN 及证据
Workspace/Scope：实际工作目录、可修改范围、状态目录；不得修改的既有工作
Deliverables & DoD：交付物、报告路径、验证方式、完成条件
Return to Leader：按下述格式写报告，并在本回合最终回复中给出报告摘要与路径；完成后等待 Leader 的新任务
```

首个任务执行前先记录 `dispatch_state = sending`。发送工具返回明确成功时更新为 sent/dispatched；这只表示宿主接受发送，不表示角色已读取、通过能力门或已开始。明确未发送时记 failed，可针对同一任务、目标和 key 安全重试一次。超时或结果不明记 unknown，先查询成员历史与状态；未排除已送达前禁止重发。当前工具若无队列语义，不要把 busy 当作自动入队。

## 成员报告

```text
Task / Attempt：与任务单一致
Identity：team、epoch、stage、attempt、dispatch_key、来源 Leader thread id
Status：completed / blocked / failed
Completed：完成内容及与要求的对应关系
Artifacts：文件绝对路径；如有，提供 checkout、分支和提交
Verification：执行的检查、结果、未执行的检查及原因
Issues：未解决问题、依赖、需要 Leader 的决定
Recommendation：返修或后续工作的建议
```

报告正文不得虚构已执行的检查。成员仅确认待命时不写业务完成报告；无 report 文件但最终回复已包含完整可核实结果时，Leader 可保存该回复并标注来源，不冒充成员生成的文件。

## 验收与交接

任务状态流转：planned → sending → dispatched → reported → accepted；reported 也可转为 rework 或 blocked。只有依赖均 accepted 的任务可派发。attempt 在返修重派时递增；已有旧报告不满足新一次尝试。只有当前 epoch/stage/attempt/key 完全匹配的证据可推进；旧或重复结果仅记 stale/duplicate。

Leader 验收须记录：结论、实际检查证据、接受或退回的原因。检查强度取决于交付物：代码检查实际改动和必要测试，研究检查来源与关键论断，文档检查范围与一致性。不要机械重复全部测试，也不能仅信成员的“完成”。`reported` 不是 `accepted`；验收前不得派下一阶段。`automatic` accepted 后继续，`confirmation` accepted 后先展示摘要并等待确认。

派给下一成员前，明确前序产物如何进入其工作目录，并验证可访问、版本正确；特别是 Git worktree 间的未提交文件不会自动同步。成员是长期角色，不绑定一次性阶段；返修、复核均复用原会话。

## 中断和异常恢复

1. 读取账本，验证 skill、schema_version、team_id、项目和 `ownership_epoch` 匹配，并验证当前会话等于 `leader.thread_id`；不匹配时只读报告并请用户回到绑定 Leader。不识别的版本只报告，不能重置重建。
2. 查询已绑定会话及当前任务，区分正在执行、已报告未验收、发送结果不明和仅待命；只接受身份字段完整的最新证据。
3. 正在执行：恢复等待；已报告：匹配 task_id/attempt/key 后验收；已验收：核对下一阶段尚未送达，再按原 gate 派发。
4. 创建结果不明：核对实际会话和创建证据，不重建已成功角色；缺少可靠关联时报告待用户确认。确实创建失败的角色可重试一次，成功角色保留。
5. 改标题或列表核验失败：保留 ID，只修复失败步骤。有限列表里找不到成员时补充查询，不能直接认定删除。
6. 确认归档、删除或绑定失效后，停止对该成员派单；让用户选择恢复、重新绑定或新建，不自动换人。
7. 用户暂停/取消：保存已发生的操作，不再派单。当前工具集没有通用停止其他会话回合的保证，明确指出仍在执行的成员；必要时请用户在应用中停止，不能声称发送暂停文字就已取消执行。
8. revision 冲突、同一阻塞或同一不确定发送连续返修两次仍无新证据时，向用户说明原因和所需决定，避免无止境地重复派单。

团队完成必须覆盖用户的整体完成条件、全部必要依赖与最终产物；成员会话回合全部结束只是状态证据之一。
