# agent-team-work

`agent-team-work` 用于在 Codex 项目开始时，通过菜单确认目标、角色、阶段和 DoD，建立一个当前会话 Leader 加多个独立项目成员会话的严格串行团队。Leader 逐阶段派单、核对成员报告和实际产物，只有验收通过后才推进下一阶段；返修复用原成员会话并递增 attempt。

新建任务默认可使用 `worker_can_request` 讨论策略：成员遇到未决的跨角色合同、冲突证据或高影响选择时，可请求一个由 Lead 批准、最多两轮、Lead 定期限的有界 worker-to-worker 决策讨论回合。指定的 `decision_owner` 给出结论，Lead 核验并接受后原任务才可消费该决定；讨论始终是当前阶段内的子流程，不改变串行派单和验收门。

## 使用范围

- 适用：创建或继续 Codex 项目会话团队；每个角色拥有独立项目任务；需要阶段派单、汇报、验收和恢复。
- 完成后的修改：团队已 `complete` 时，Lead 先进入 `impact_analysis`，记录新的 `revision_cycle` 和影响范围，再只复用原成员派发受影响阶段及必要下游阶段；确认零影响时记录规范标记后不派单。
- 不适用：概念解释、编写或修改 skill、一次性改名、普通子代理、并行 worker、Orca team、Sub-Lead 或子团队。
- 讨论限制：不是自由聊天，不允许成员自行开放/关闭讨论、修改 Lead-only 账本、替其他角色扩展范围、验收任务或派发后续阶段；缺少工具/输入通常仍是 `blocked`，而不是讨论理由。legacy task 没有 `discussion_policy` 时完全保持原行为。
- 运行依赖：Codex 原生 project/thread 工具和用户已保存的项目。通用 Agent Skills 目标只保留协议和降级说明。

## 安装与运行

1. 将 `dist/agent-team-work.zip` 解压到目标 skill 目录，或按目标平台的 Agent Skills 安装方式复制包体。
2. 在目标项目中显式调用 `$agent-team-work`。
3. 首次建队先完成菜单摘要和一次最终确认；只读查看已有团队时不创建会话或派单。
4. 状态保存在项目根目录 `.team/`，可用 `python3 scripts/validate_team_state.py .team` 做只读账本校验。

维护者可用 `python3 scripts/ci_test.py` 运行路由、Python 语法和包形状检查；`scripts/local_output_eval_runner.py` 只回放固定 fixture。`scripts/import_telemetry_events.py` 校验 metadata-only JSONL 并向 stdout 输出脱敏事件，不联网也不写文件。`evals/output/provider_matrix.json` 与 `holdout_cases.zh-CN.jsonl` 定义真实 provider 留出评测的 40-call 合同，但没有凭证时保持 `external-required`。

## 发布证据

源码仓库的 `reports/`、`evals/`、`scripts/` 和其他审计资产只用于维护与发布验证，不进入 runtime-only 发布包；仅保留两个用于校验归档完整性的便携元数据文件。发布包只保留 Skill 入口、运行时参考、接口元数据、清单和许可证；本地命令执行、模板或待审查记录不会被当作 provider 或人工证据。

## 许可

本包沿用源 skill 的 MIT 许可，详见 [LICENSE](LICENSE)。
