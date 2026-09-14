# agent-team-work

`agent-team-work` 用于在 Codex 项目开始时，通过菜单确认目标、角色、阶段和 DoD，建立一个当前会话 Leader 加多个独立项目成员会话的严格串行团队。Leader 逐阶段派单、核对成员报告和实际产物，只有验收通过后才推进下一阶段；返修复用原成员会话并递增 attempt。

## 使用范围

- 适用：创建或继续 Codex 项目会话团队；每个角色拥有独立项目任务；需要阶段派单、汇报、验收和恢复。
- 不适用：概念解释、编写或修改 skill、一次性改名、普通子代理、并行 worker、Orca team、Sub-Lead 或子团队。
- 运行依赖：Codex 原生 project/thread 工具和用户已保存的项目。通用 Agent Skills 目标只保留协议和降级说明。

## 安装与运行

1. 将 `dist/agent-team-work.zip` 解压到目标 skill 目录，或按目标平台的 Agent Skills 安装方式复制包体。
2. 在目标项目中显式调用 `$agent-team-work`。
3. 首次建队先完成菜单摘要和一次最终确认；只读查看已有团队时不创建会话或派单。
4. 状态保存在项目根目录 `.team/`，可用 `python3 scripts/validate_team_state.py .team` 做只读账本校验。

维护者可用 `python3 scripts/ci_test.py` 运行路由、Python 语法和包形状检查；`scripts/local_output_eval_runner.py` 只回放固定 fixture。`evals/output/provider_matrix.json` 与 `holdout_cases.zh-CN.jsonl` 定义真实 provider 留出评测的 40-call 合同，但没有凭证时保持 `external-required`。

## 发布证据

`reports/` 保存 IR、目标编译、conformance、信任、安装模拟、路线、输出评估和 Review Studio 证据。真实冒烟记录位于 `evals/history/2026-09-14-real-smoke.json`。本包不把本地命令执行、模板或待审查记录当作 provider 或人工证据；公共发布前仍需按 `reports/world_class_evidence_ledger.md` 的待办完成外部和人工证据收集。

## 许可

本包沿用源 skill 的 MIT 许可，详见 [LICENSE](LICENSE)。
