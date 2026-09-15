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

## 结束判定

只有 Leader 根据整体 DoD、依赖和最终产物完成检查后才能写 `complete`。记录仍未验证的侧边栏可见性、送达、后台存活或 exactly-once 事实为 `unknown`，不要用成员回合结束代替验收。
