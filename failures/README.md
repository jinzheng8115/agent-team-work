# 已知失败模式

这里记录会让流水线停止或需要人工恢复的可重复失败；不是运行时状态文件。

- **工具不可用**：未发现必需的 Codex 原生工具时停在预检，不猜 Cindy/Orca 替代工具。
- **项目归属不明**：没有可靠 project ID 或真实 thread ID 时，不创建 projectless 替代会话。
- **发送结果不明**：超时且历史无法证明是否发送时记 `unknown`/`blocked`，不盲目重试；明确未发送的同一动作最多安全重试一次。
- **旧结果**：epoch、stage、attempt 或 dispatch key 不匹配时记 stale/duplicate，不让旧结果通过当前验收。
- **完成后直接发送**：团队 `complete` 后收到修改请求却直接向成员发送消息时停止流程；在 Lead 完成 `impact_analysis`、写入 `.team/revisions/<cycle>.md` 并建立 revision-aware planned task 前，发送不具备有效派单身份且不得验收。
- **验收停等**：`reported` 不是 `accepted`；缺少实际产物、能力证据或 DoD 检查时不启动下一阶段。
- **worktree 隔离**：未提交文件不会自动进入另一 worktree；先交接并验证路径和版本。
- **暂停语义**：停止新派单不等于取消在途回合；说明仍运行的会话，不能声称文字通知已经停止执行。
- **真实证据缺失**：静态评测通过不等于真实菜单、建队、阶段闭环或中断恢复通过；报告中保持 `missing evidence`。
