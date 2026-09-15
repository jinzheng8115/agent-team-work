# 串行流水线示例

这是说明性案例，不执行真实 Codex 工具，也不创建 `.team/`。

用户要在当前项目创建 `product-architect`、`developer`、`reviewer` 三个角色，选择 `confirmation` 门控。

1. 只读收集项目目标、阶段 DoD、角色映射、当前 Leader、每个角色的配置和 worktree。
2. 展示一次最终摘要，取得一次明确确认；确认前不 create、rename 或派 work。
3. 当前会话绑定为 Leader，创建三个只待命的成员会话，核验真实 thread ID、project ID、标题和项目列表；只向 `product-architect` 派 `attempt=1` 的 work。
4. 成员先通过能力门，返回带 ATW 身份标记、交付物和验证证据的 result；Leader 核验后写 `accepted`。
5. 因为是 `confirmation`，展示 accepted 摘要并等待用户确认，再派 developer；最后阶段 accepted 后才能记 `complete`。

如果 work 发送结果不明，先查会话历史和当前账本；不能据此重发。若结果身份字段不匹配，记 stale/duplicate，不推进流水线。

首轮 `revision_cycle: 1` 已 `complete` 后，用户要求只修改 developer 产出的数据映射，并让 reviewer 重新核验：

1. Lead 先进入 `impact_analysis`，读取首轮验收、产物和三个原成员的真实状态，回答七项影响问题；此时不向任何成员发消息。
2. Lead 写 `.team/revisions/2.md`，说明 architect 产物与验收保持有效，只影响 developer 和依赖其输出的 reviewer；升级/使用 schema 3，并建立带 `revision_cycle: 2`、`supersedes`、`impact_basis` 的两个 planned tasks。
3. Lead 复用原 developer 会话，以 `<team_id>/<ownership_epoch>/r2/developer/1/work` 派单；验收后按 `confirmation` gate 等待用户确认，再复用原 reviewer 会话派复核任务。architect 不接收 cycle 2 消息。
4. cycle 1 的报告只作为影响分析证据，不能推动 cycle 2；两个 cycle 2 任务都 accepted 且整体 DoD 复验通过后，Lead 在修订记录写周期结论并将团队恢复为 `complete`。
