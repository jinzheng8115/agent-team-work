# 角色能力门与运行配置

本文件只规定开始当前任务前的最小能力探测。角色画像、模型和工具不预绑定；每个角色的配置都要在菜单中单独确认。

## 能力门

收到 `attempt >= 1` 的 `work`/`rework` 后，角色先记录 `received`，再做只读检查：

1. 核对 working directory、输入路径和必要产物可读；需要写入时核对目标目录权限，不创建探针文件。
2. 用 `command -v`、宿主工具发现或等价只读方式确认完成 DoD 所需命令/工具，不执行高成本或无关动作。
3. 确认本回合能够向真实 Leader 返回结构化结果；不能以发送成功代替回传能力证明。
4. 每项能力记录 `PASS / MISSING / UNKNOWN + evidence`。核心项全部 `PASS` 后记录 `capability_checked`、`started`，两者都随 result/blocked 回传。

核心项 `MISSING` 或 `UNKNOWN` 时不得开始项目工作：回传通道可用则返回 `blocked`；缺失的正是回传通道时，只能在本地会话留下 blocked，Leader 需要在恢复时读取历史或请用户人工核验。非核心能力不足只限制验证范围，不得把未检查写成通过。

能力要求按阶段最小化。纯文档任务不强制数据库或浏览器；未修改前端时不强制截图；研究任务应把来源访问列为核心能力。

## 讨论启用任务的返回契约

带 `discussion_policy` 的每个 result 或 blocked 报告都必须返回 `decision_status: clear | assumption | unresolved`。`clear` 表示没有未决的跨角色决定；`assumption` 必须列出不阻塞工作的非关键假设；`unresolved` 必须引用已有 `discussion_id` 或附上符合 trigger policy 的 `discussion_request`。该字段不能替代原有 `Status`、Issues 或 verification evidence。

讨论请求不会豁免能力门：成员在任何项目修改前仍须完成本文件要求的 `PASS / MISSING / UNKNOWN + evidence` 检查，核心项非 `PASS` 时返回 `blocked`。出现未决决定时只暂停依赖该决定或不可逆的工作，清楚列入 `paused_work`；不受影响的独立工作可以继续，但成员不能因讨论开放而修改其他角色范围、启动后续阶段或把 owner decision 当成 Lead acceptance。

## 运行配置

默认省略 `model` 和 `thinking`，沿用宿主默认。用户明确为某角色选择模型或思考强度时，把该配置逐角色列入最终摘要，并只传入宿主实际支持的值。即使多个角色使用相同模型，也要逐行明确选择；不能默默复制 Leader 配置。

新建成员在 `create_thread` 时传入已确认的配置，不能创建后再偷偷补设。复用角色若用户明确要求修改运行配置，先查询现有配置和 generation，使用宿主支持的版本保护更新，再重新读取核验；失败或不匹配时停止派单。

当前版本只把当前会话作为 Leader。若用户要求创建或接管另一个 Leader，会话所有权、停止原协调器和消息原子性超出本版 Codex 适配范围，应说明限制，不创建第二个隐形协调器。
