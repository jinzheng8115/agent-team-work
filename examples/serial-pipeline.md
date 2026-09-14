# 串行流水线示例

这是说明性案例，不执行真实 Codex 工具，也不创建 `.team/`。

用户要在当前项目创建 `product-architect`、`developer`、`reviewer` 三个角色，选择 `confirmation` 门控。

1. 只读收集项目目标、阶段 DoD、角色映射、当前 Leader、每个角色的配置和 worktree。
2. 展示一次最终摘要，取得一次明确确认；确认前不 create、rename 或派 work。
3. 当前会话绑定为 Leader，创建三个只待命的成员会话，核验真实 thread ID、project ID、标题和项目列表；只向 `product-architect` 派 `attempt=1` 的 work。
4. 成员先通过能力门，返回带 ATW 身份标记、交付物和验证证据的 result；Leader 核验后写 `accepted`。
5. 因为是 `confirmation`，展示 accepted 摘要并等待用户确认，再派 developer；最后阶段 accepted 后才能记 `complete`。

如果 work 发送结果不明，先查会话历史和当前账本；不能据此重发。若结果身份字段不匹配，记 stale/duplicate，不推进流水线。
