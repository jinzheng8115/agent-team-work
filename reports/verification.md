# 验证记录

本记录对应 `agent-team-work` 0.2.0 的当前 release candidate；证据在生成后仍需按 [AGENTS.md](../AGENTS.md) 的刷新顺序重跑。

- `validate --require-manifest`、治理检查和资源边界检查：通过；manifest/frontmatter 对齐，governed 得分 90/100，入口估算 870/1000 token。
- `skill-ir`、五目标编译和五目标 conformance：通过；OpenAI 保留 Codex 原生 project/thread 运行面，其他目标明确标为降级源契约。
- 路由评测与混淆矩阵：通过；8/8 路由正确、0 misroute、0 ambiguous，并保留解释、编写 skill、普通子代理、并行 worker 和 Orca 等反例。
- 输出评测：5/5 fixture case，with-skill 100、baseline 0、无回归；10/10 command runs 有 timing，token 仍为 estimated，不代表 provider 模型运行。
- 真实 E2E 冒烟：通过；在 `team-worker` 项目创建 1 个 Leader + 2 个独立成员，完成待命、首阶段派单、DoD 失败、原成员 rework attempt=2、阶段验收、下一阶段派单和最终 `complete`；证据见 `/Volumes/Code/team-worker/.team/reports/smoke-summary.md`。
- Trust：通过；0 secret、3 个本地 CLI script、0 network-capable script、3/3 help smoke 通过、无 required capability。
- 运行时权限探针：四目标全部通过元数据校验，但 native enforcement 为 0，metadata fallback 为 4；该限制已进入 world-class ledger。
- 归档与安装：四目标 adapter、145 个 zip entries、路径安全、单入口、portable evidence index、安装模拟均通过。
- Registry：通过；MIT 许可、四目标兼容性、archive/package checksum 已同步。
- Claim guard：通过；0 overclaim violation，但 ledger 仍有 4 项 pending（provider、human adjudication、native permission、native telemetry）。

## 仍然阻断无条件公共 production release 的证据

- provider holdout 尚未运行：需要真实 provider 40 calls、timing 和非估算 token metadata。
- 五个盲评 pair 尚无真实 reviewer judgments；phase-one 三名 reviewer adjudication 和 promotion 也未完成。
- 四个目标都只有 metadata fallback，尚无目标客户端原生权限执行证明。
- 尚无真实外部客户端 metadata-only telemetry 导入。
- 当前目录已建立本地 Git，但最终 clean-lock 需要在提交全部源码和生成证据后重新生成；未完成前不得把公共 release lock 写成 ready。

这些缺口是 `missing evidence`，不以 waiver、fixture、模板或本地命令回放替代。
