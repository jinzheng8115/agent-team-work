# 局限与下一步

## 当前已覆盖

- Codex 原生项目/线程工具路由，避免 Cindy Helper 与普通子代理混用。
- 一次最终确认、严格串行阶段、automatic/confirmation 门控。
- `team_id`、`ownership_epoch`、`dispatch_key`、attempt 和状态账本，用于中断后的 best-effort 恢复。
- 最小能力门、验收与 rework 闭环、跨 worktree 产物核验、规模边界和失败恢复。

## 已获得与仍缺少的真实证据

- 已完成一次真实 Codex 项目端到端记录：创建 Leader/成员 → 待命 → 首阶段 → DoD 失败 → 原成员 rework → 报告 → 验收 → 下一阶段 → complete，详见 `.team/reports/smoke-summary.md`。
- 尚无运行时级重复发送、侧边栏可见性、Git worktree 交接和中断恢复回归测试；本次有限 `list_threads` 查询未返回成员条目，因此 UI 可见性仍为 `unknown`。
- `team.json`/`tasks.json` 是 Lead 的恢复索引，不是跨进程原子锁；不能声称 exactly-once、原子 ownership 或后台常驻监督。
- 当前版本默认当前会话为唯一 Leader；已加入 `leader.thread_id` 只写边界和 `revision` 版本栅栏，但跨 Leader takeover、并行阶段、Sub-Lead、Orca worker 和子团队未实现。
- 已完成的包体安装模拟只证明归档路径、元数据、报告和权限策略可读；未证明 Codex 宿主真实创建成员会话、派单或侧边栏显示。

## 下一次真实试跑建议

在用户明确选择的 Git 项目中按 `references/e2e-smoke-checklist.md` 补做一次 worktree 交接和中断恢复，记录队列 cursor、重复派单核验和侧边栏查询结果。根据失败再修改协议，不先添加并行或后台服务。
