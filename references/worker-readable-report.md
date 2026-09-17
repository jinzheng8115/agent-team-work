# Worker 可读回报契约

## 目标

Worker 回合同时服务两类读者：Lead 需要可核验的机器身份和证据，用户需要先知道“做了什么、结果是什么”。因此采用双层呈现：

- **摘要优先（Human-readable summary）**：回合正文先给角色、状态、结论、产物和风险。
- **技术详情（Technical details）**：能力门、完整身份、命令输出和原始执行痕迹放在摘要之后；宿主支持折叠时默认折叠。

`team`、`stage`、`attempt`、`dispatch_key` 等 machine metadata 不删除、不改变，也不能从验收证据中省略；它们只应以一行紧凑标记或详情区呈现，避免淹没成果。

## Worker 最终回报顺序

每个 `work`/`rework` 回合的最终回复按以下顺序编排。第一行仍使用协议规定的 ATW 身份标记，随后立即给出摘要，不先倾倒技术日志：

```text
[ATW team=<id> epoch=<n> stage=<label> attempt=<n> kind=result]

Human-readable summary
Role：<角色名>（用自然语言，不只写 stage code）
Status：completed | blocked | failed
Summary：<1–3 句，说明本回合产生的结果>
Completed：<完成内容及其与目标的对应关系>
Artifacts：<绝对路径；没有产物时写“无”>
Verification：<实际执行的检查和结果；未执行的检查及原因>
Issues：<风险、依赖或需要 Lead 决定的事项；没有时写“无”>
Recommendation：<下一步或复验建议>

Technical details
Capability Gate：<PASS/MISSING/UNKNOWN + evidence>
Identity：<完整 team/epoch/revision/stage/attempt/dispatch_key/source>
Evidence：<必要的命令、来源或原始输出；只放摘要未覆盖的细节>
```

### 摘要写作规则

1. `Human-readable summary` 和 `Technical details` 必须作为独立标题行原样出现，紧接在 ATW 标记之后、详情区之前。不能省略，不能改成 `Technical details：` / `Technical details:` 这类带冒号的字段行，也不能用 Markdown 标题级别或加粗来替换这两个固定英文标题。
2. `Role`、`Status`、`Summary`、`Completed`、`Artifacts`、`Verification`、`Issues`、`Recommendation` 不能顶替上述标题。只有字段、缺少任一标题的最终回复视为未完成可读回报，Lead 不得验收，应按同一 `dispatch_key` 记 `rework`。
3. `Summary` 必须先于 `Technical details`，用普通用户能理解的语言；首次出现的内部术语要顺手解释。
4. `Status`、`Completed`、`Artifacts`、`Verification`、`Issues`、`Recommendation` 都要保留，即使值为“无”。不要让读者从 `stage` 或路径猜测结论。
5. 摘要只能引用已执行且可核验的事实。绝对路径保留为证据入口，但不要把命令输出复制到摘要。
6. `dispatch_key` 只出现在第一行 ATW 标记或 `Technical details` 的 `Identity` 中，不得进入 `Human-readable summary` 正文。
7. 能力门仍是开始和验收依据；把结果压缩成 `PASS/MISSING/UNKNOWN + evidence` 放到技术详情，不在摘要中重复每个探测命令。
8. 普通进度只在开始、blocked、关键发现和完成四类 milestone 更新；同一 milestone 不重复发送长篇技术过程。

中间更新只报告当前 milestone 的一句话状态和下一步；不要逐条转述工具调用、路径扫描或内部推理。需要完整过程时，Lead 再读取报告或技术详情。

派单任务单必须把上述标题约束写进 `Return to Leader`：要求 worker 在最终回复中原样输出两个独立标题行。Lead 读取回报时先定位 `Human-readable summary` 标题；找不到标题时不得把字段拼成摘要后验收。

## Lead 汇总

Lead 只有在检查产物和 accepted report 后，才生成面向用户的团队摘要。汇总应按阶段说明：已完成什么、哪些证据已验收、当前风险和下一步；worker 的原始技术详情仍作为可展开的审计入口。`reported` 不等于 `accepted`，摘要不能替代验收。

## 兼容边界

该契约只改变默认阅读顺序和呈现方式，不改变状态流、能力门、报告路径、账本字段或派单身份。若宿主没有摘要卡片或折叠 UI，仍按上述顺序在同一条消息中输出；若宿主支持 UI 折叠，可将 `Technical details` 映射为默认收起的详情面板。
折叠控件由 Codex 宿主提供，本 skill 不实现客户端折叠；没有折叠 UI 时的顺序 fallback 不构成发布阻塞。完整两成员建队仍需用户明确确认创建；本契约不授权自动建队。
