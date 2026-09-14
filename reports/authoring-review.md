# 编写依据与评审记录

目标：反复执行菜单建队、阶段派单、验收与恢复，输出真实项目角色会话和 `.team/` 状态。命名按用户要求固定为 `agent-team-work`；平台依赖保留在正文，OpenAI/Codex 是唯一提供原生项目会话运行面的目标，其他目标保留中性协议和降级说明。

## 参考与取舍

1. `project-session-team-bootstrap`：复用角色预设、串行闸门与交接字段；移除 Cindy 专用工具绑定。
2. Codex 当前工具 schema：按真实 `create_thread`、`send_message_to_thread`、`wait_threads` 能力编写；不假定自动回传、排队或跨 worktree 共享。
3. 系统 `skill-creator`：采用原生 `agents/openai.yaml`，并保留同步的 `agents/interface.yaml`，不把元数据当作运行时能力。
4. `yao-meta-skill`：采用触发边界、渐进披露、目标锁定和证据分级；包体标为 governed，并保留真实 provider、人工和客户端缺口。

## 复核结果

- 意图与路由：意图 100/100；路线混淆矩阵 8/8 正确，0 misroute、0 ambiguous。
- 运行与质量：Skill IR、五目标编译/conformance、trust、四目标安装模拟和 package verification 均通过；本地输出 runner 10/10 command runs 有 timing。
- 真实冒烟：创建 1 个 Leader 和 2 个独立成员，验证待命、首阶段、DoD 失败、原成员 rework attempt=2、验收后串行推进和最终 `complete`。
- 失败边界：缺少 `verification`、发送结果 unknown、跨项目绑定、解释型 near-neighbor、侧边栏未核验均保持明确的 blocked/unknown 语义。

## 发布边界

Registry 已用 MIT 许可、四目标 adapter 和当前 archive checksum 通过；claim guard 0 violations；source commit `7cfd3ae` 的 clean-lock 已由 benchmark 证明。无条件公共 production 仍需真实 provider 40-call holdout、三名 reviewer 的盲评 adjudication、native permission enforcement 和外部客户端 telemetry。不得把 fixture、模板、waiver 或 metadata fallback 作为这些证据的替代品。
