# agent-team-work

`agent-team-work` 用于在 Codex 项目中建立和运行严格串行的项目会话团队：一个当前 Leader，加上同一项目中的独立角色会话。它帮助团队先确认目标、角色、阶段和完成标准，再按已验收的阶段逐步派单。

## 主要功能

- 通过菜单确认项目、目标、角色、阶段顺序、DoD 和 `automatic` / `confirmation` 门控。
- 绑定真实项目和会话，避免重复创建 Leader 或把普通子代理当作团队成员。
- 只有成员报告、产物和能力门验收通过后，才推进下一阶段。
- 中断后按项目状态恢复；返修复用原成员并递增 `attempt`。
- 首轮完成后的修改先由 Lead 做 `impact_analysis`，记录新的 `revision_cycle`，再只派受影响阶段和必要下游阶段。

不用于概念解释、单次会话管理、普通子代理、并行 worker、Orca team、Sub-Lead 或子团队。

## 安装

下载 [runtime-only 发布包](dist/agent-team-work.zip)，解压到目标 Agent Skills 目录，或按宿主平台的 Skill 安装方式复制包体。

包内运行时文件包括 `SKILL.md`、`manifest.json`、Codex 接口元数据、流程/协议/角色参考和许可证；本仓库的测试、评测、报告与维护脚本不属于运行时依赖。

## 使用示例

在目标 Codex 项目中显式调用 `$agent-team-work`，例如：

```text
请为当前项目建立一个串行项目团队。
目标：实现用户资料导入功能。
角色：后端、前端、验收。
阶段：后端 API → 前端接入 → 集成验收。
完成标准：API、界面和验收报告都通过对应门控后才算完成。
门控：automatic。
```

如果首轮完成后发现需求变化，可以这样发起第二轮：

```text
首轮已经完成，但用户资料字段发生变化。请让 Lead 先做影响分析，记录 revision cycle，
只复用原成员派发受影响阶段和必要下游阶段；不要重新创建团队，也不要直接跳过验收。
```

只想查看状态时，可以这样说：

```text
请只检查当前团队、Leader、成员报告和阶段状态，不要创建会话或派发任务。
```

## 进一步阅读

- [完整工作流程](references/workflow.md)
- [调度与状态协议](references/team-protocol.md)
- [Codex 工具规则](references/codex-tools.md)
- [角色预设](references/role-presets.md)
- [团队规模边界](references/team-scaling.md)

## 许可

MIT，详见 [LICENSE](LICENSE)。
