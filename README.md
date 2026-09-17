# agent-team-work

`agent-team-work` 用于在 Codex 项目开始时，通过菜单确认目标、角色、阶段和 DoD，建立一个当前会话 Leader 加多个独立项目成员会话的严格串行团队。Leader 逐阶段派单、核对成员报告和实际产物，只有验收通过后才推进下一阶段；返修复用原成员会话并递增 attempt。

新建任务默认可使用 `worker_can_request` 讨论策略：成员遇到未决的跨角色合同、冲突证据或高影响选择时，可请求一个由 Lead 批准、最多两轮、Lead 定期限的有界 worker-to-worker 决策讨论回合。Lead 从 worker participant 中指定 `decision_owner`，向所有 participant 发送相同 context 和共享 transcript 路径；每人读取 transcript 后以真实 peer thread ID 给另一成员发送身份绑定消息，`recipients` 明确写 peer label，规范消息只追加一次。owner 只能在 cross-worker exchange 后给出结论，Lead 核验 peer 可见性、身份、证据和范围后才可接受；仅回复 Lead 的流程无效。讨论始终是当前阶段内的子流程，不改变串行派单和验收门，且 discussion marker 缺失的 legacy 团队维持原行为。

## 使用范围

- 适用：创建或继续 Codex 项目会话团队；每个角色拥有独立项目任务；需要阶段派单、汇报、验收和恢复。
- 完成后的修改：团队已 `complete` 时，Lead 先进入 `impact_analysis`，记录新的 `revision_cycle` 和影响范围，再只复用原成员派发受影响阶段及必要下游阶段；确认零影响时记录规范标记后不派单。
- 不适用：概念解释、编写或修改 skill、一次性改名、普通子代理、并行 worker、Orca team、Sub-Lead 或子团队。
- 讨论限制：不是自由聊天，不允许成员自行开放/关闭讨论、修改 Lead-only 账本、替其他角色扩展范围、验收任务或派发后续阶段；缺少工具/输入通常仍是 `blocked`，而不是讨论理由。legacy task 没有 `discussion_policy` 时完全保持原行为。
- 运行依赖：Codex 原生 project/thread 工具和用户已保存的项目。通用 Agent Skills 目标只保留协议和降级说明。

## 安装与运行

1. 将 `dist/agent-team-work.zip` 解压到目标 skill 目录，或按目标平台的 Agent Skills 安装方式复制包体。归档已包含四个平台适配器。
2. 在目标项目中显式调用 `$agent-team-work`。
3. 首次建队先完成菜单摘要和一次最终确认；只读查看已有团队时不创建会话或派单。
4. 状态保存在项目根目录 `.team/`，可用 `python3 scripts/validate_team_state.py .team` 做只读账本校验。

维护者可用 `python3 scripts/ci_test.py` 运行路由、Python 语法和包形状检查；`scripts/local_output_eval_runner.py` 只回放固定 fixture。`scripts/import_telemetry_events.py` 校验 metadata-only JSONL 并向 stdout 输出脱敏事件，不联网也不写文件。`evals/output/provider_matrix.json` 与 `holdout_cases.zh-CN.jsonl` 定义真实 provider 留出评测的 40-call 合同，但没有凭证时保持 `external-required`。

## 平台适配器

适配器是统一 Skill 契约与目标平台原生元数据之间的桥接层。它负责平台侧的发现、激活、安装范围、权限说明和能力降级，不复制一套新的团队逻辑，也不会额外创建 worker。平台不支持 Codex 原生项目会话时，适配器会明确保留的通用语义和降级边界。

| 平台 | 归档文件 | 作用 |
| --- | --- | --- |
| OpenAI/Codex | `targets/openai/adapter.json`、`targets/openai/agents/openai.yaml` | 描述 Codex 项目/会话能力及 OpenAI 风格展示元数据 |
| Claude | `targets/claude/adapter.json`、`targets/claude/README.md` | 提供 Claude 侧元数据，并记录 Codex 会话能力的降级说明 |
| Generic Agent Skills | `targets/generic/adapter.json` | 提供平台中立的 Agent Skills 兼容元数据 |
| VS Code | `targets/vscode/adapter.json`、`targets/vscode/README.md` | 说明 VS Code 安装范围、workspace trust 和运行限制 |

适配器由跨平台打包阶段生成；最终归档通过以下命令验证目标文件和适配器元数据均已包含：

```bash
python3 scripts/runtime_package_check.py . --package-dir dist
```

## 发布证据

源码仓库的 `reports/`、`evals/`、`scripts/` 和其他审计资产只用于维护与发布验证，不进入 runtime-only 发布包；仅保留两个用于校验归档完整性的便携元数据文件。发布包保留 Skill 入口、运行时参考、接口元数据、四个目标适配器及其目标说明、清单和许可证；本地命令执行、模板或待审查记录不会被当作 provider 或人工证据。目标适配器由跨平台打包阶段生成，并在最终 zip 内按 allowlist 校验。

## 许可

本包沿用源 skill 的 MIT 许可，详见 [LICENSE](LICENSE)。
