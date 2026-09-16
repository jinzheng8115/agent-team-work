# 端到端冒烟清单

这份清单用于维护者在一个可修改的 Codex 项目中补齐真实运行证据。它不授权自动建队，也不把静态检查当成运行通过。

## 运行前

1. 选择一个真实项目，记录 `project_id`、`isGitRepository`、项目根目录和当前 Leader `thread_id`。
2. 用菜单填写目标、首要交付物、完成判定、两个成员角色、两阶段顺序、允许路径和门控；保存最终摘要截图或文本。
3. 在第一次 `create_thread`、`set_thread_title` 或工作 `send_message_to_thread` 前记录用户确认。

## 运行中

按顺序保留以下证据，并在每项旁记录真实 ID、时间和结果：

- 每个成员的 `threadId`/`hostId`、标题和项目归属查询；`clientThreadId` 只能标为 pending。
- `team.json` 与 `tasks.json` 的 `team_id`、`ownership_epoch`、`revision`、`dispatch_key` 和任务状态变化。
- 首条 `attempt=0` 待命消息，以及只派发一个首阶段的 `send_message_to_thread` 结果。
- 能力门 `PASS/MISSING/UNKNOWN`、成员阶段报告、Leader 的验收依据和下一阶段派单。
- 一次缺失 DoD 的 `rework`（attempt 递增）或可证明的阻塞；确认旧报告不能推进新 attempt。
- Git worktree 场景下，前序产物在下一成员目录中的可访问性检查。
- 一次中断后恢复：核对真实会话、cursor 和账本，证明没有重复创建或重复发送。
- 一次有范围的完成后修订：首轮 `complete` 后请求只修改一个上游产物，记录 `complete -> impact_analysis -> running -> complete`、`.team/revisions/2.md` 和 cycle 2 任务；证明只复用受影响原成员及必要下游复核者，未联系无关成员，并确认 cycle 1 结果不能推进 cycle 2。

## Worker-to-worker discussion 实跑场景

在当前 `work` 任务中选择一个会影响其他成员交付物的未决合同，完成下列一次真实场景。每项都填写实际 ID、时间戳、工具结果和对应文件路径，不得用预期值代替运行证据。

- Request：记录 worker 提交的 `discussion_request`，包括 team/epoch/revision/stage/task/dispatch identity、trigger、question、options、evidence、affected tasks 和 suggested owner；确认 worker 没有自行创建 discussion record。
- Lead participant/owner：记录 Lead 批准时选定的二至四名 participant，逐个填写 label、role 和真实 `thread_id`；另记录 `decision_owner` 及其 `thread_id`、`max_rounds` 和 deadline。
- Peer message 1：保留第一条 peer message 的 `message_id`、sender/recipients、sequence、kind、body、发送结果及 `messages.jsonl` 行号。
- Peer message 2：保留来自另一 participant 的第二条 peer message，记录 `in_reply_to`、完整身份、发送结果及 transcript 行号。
- Decision：记录 decision owner 发出的 `decision` message 和 `decision.json`，核对选项、rationale、evidence、rejected alternatives 与 affected tasks。
- Lead acceptance：保留 Lead 对身份、证据、范围和依赖的实际检查，以及写入 `lead_accepted` 和 `closed` 的时间戳。
- 未提前派发：对比 `discussion_request`、decision、Lead acceptance 与下一阶段 `send_message_to_thread` 的时间；附上成员历史和账本差异，证明验收前没有后续阶段消息或状态推进。
- Stale 检查：在 `closed` 后使用原 discussion identity 发送一条测试消息；记录它被保留为 `stale` 历史，且 decision、task status 和下一阶段派发均未变化。
- timeout/block 检查：用一个独立演练 discussion 到达 deadline 但不产生 owner decision；确认 Lead 将其标记 `expired`，把依赖工作标记 `blocked` 或只向用户提一个具体问题，并证明没有派发下一阶段。

## 结束判定

只有 Leader 根据整体 DoD、依赖和最终产物完成检查后才能写 `complete`。记录仍未验证的侧边栏可见性、送达、后台存活或 exactly-once 事实为 `unknown`，不要用成员回合结束代替验收。
