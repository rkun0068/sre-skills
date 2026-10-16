---
name: sre-doc-standards
description: >-
  CRITICAL — every sre-* document skill depends on this. Shared conventions for SRE / security-reliability documents derived from Google's "Building Secure and Reliable Systems" — metadata header, document status lifecycle, severity (SEV0–4) and priority (P0–4) models, probability×impact risk scoring, action-item format, confirmed-vs-unconfirmed writing rules, sensitivity labels, and IOC defanging. TRIGGER when: any sre-* skill is loaded; the user asks to write, standardize, or review any SRE/security/reliability document (设计文档、威胁建模、事件、复盘、预案、演练、风险评估); or asks what severity/priority/risk scale to use. DO NOT TRIGGER when: the task is general coding with no document output, or the user asks for a non-SRE document such as marketing copy.
---

# SRE 文档共享约定

本 skill 是所有 `sre-*` 文档 skill 的**公共协议**。各文档 skill 只定义自己的结构与检查项，以下约定一律以此为准，不得重新定义。

## 1. 元数据头（所有文档必填）

每份文档第一个区块必须是下面这张表：

```markdown
| 字段 | 值 |
|---|---|
| 文档类型 | <威胁建模 / 设计文档 / 事件文档 / 复盘 / ...> |
| 标题 | <系统或事件名 + 文档类型> |
| 状态 | 草稿 / 评审中 / 已批准 / 已废弃（事件类：进行中 / 已缓解 / 已关闭） |
| 密级 | 公开 / 内部 / 机密 / 严格受限 |
| Owner | <唯一负责人> |
| 参与者 / 评审人 | <名单> |
| 创建日期 | YYYY-MM-DD |
| 最后更新 | YYYY-MM-DD |
| 下次复审 | YYYY-MM-DD（计划类文档必填） |
| 关联文档 | <链接> |
```

规则：
- Owner 只能是一个人；"团队"不是 Owner。
- 计划类文档（风险评估、IR 计划、Playbook、威胁模型）必须写"下次复审"，默认不超过 12 个月——系统、威胁和配置都在变化，过期文档在灾难中等于没有。
- 安全事件、未修复漏洞相关文档默认密级为"严格受限"，并说明存放位置的访问控制。

## 2. 严重度与优先级（两个独立维度）

BSRS 把**严重度**（影响有多大）和**优先级**（要多快响应）分开。两者都用 0–4，0 最高。

| 等级 | 严重度 SEV：对组织的影响 | 优先级 P：响应节奏 |
|---|---|---|
| 0 | 灾难性：核心业务中断、大规模数据泄露、生命安全 | 立即放下一切工作，持续响应直到降级 |
| 1 | 严重：关键功能不可用或敏感数据受损，用户显著可感知 | 当班立即处理，可打断其他工作 |
| 2 | 中等：部分功能降级、有限范围受影响 | 当天内处理 |
| 3 | 轻微：影响小、有临时方案 | 按计划排期（本周/本迭代） |
| 4 | 可忽略：无用户影响 | 常规积压 |

规则：
- 严重度一旦评估清楚通常不变；**优先级可以随进展调整**（例：关键修复上线后从 P0 降到 P2），调整要记录原因和时间。
- 严重度要对照灾难风险评估来校准，避免所有事情都被标成"严重"。
- 组织可以按自身业务细化每级的量化阈值（如影响用户比例、金额），但必须保留 0–4 的刻度与"两维独立"原则，并在 IR 计划中统一发布。

## 3. 风险打分（概率 × 影响）

所有涉及风险排序的文档（威胁模型、风险评估、设计文档的风险表）使用同一套刻度，来自 BSRS 附录 A：

| 一年内发生概率 | 值 | 对组织的影响 | 值 |
|---|---|---|---|
| 几乎不会 | 0.0 | 可忽略 | 0.0 |
| 不太可能 | 0.2 | 轻微 | 0.2 |
| 有点可能 | 0.4 | 中等 | 0.5 |
| 可能 | 0.6 | 严重 | 0.8 |
| 很可能 | 0.8 | 灾难性 | 1.0 |
| 必然 | 1.0 | | |

- **风险分 = 概率 × 影响**，按分值从高到低排序。
- 排序后必须做一次**离群复核**：低概率但影响为"灾难性"的项（如数据中心整体损毁、签名密钥泄露）不能因为分数低就被忽略，需单独标注并说明处置。
- 概率要结合本组织的地理位置、架构和已有冗余来估计；增加冗余或控制后要重新打分。
- 分数仅用于排序，不代表精确数值——在文档中写清依据，避免拍脑袋和群体思维；必要时请外部专家复核。

## 4. 行动项格式

所有文档中的待办统一用下表，不允许出现没有 Owner 或没有日期的行动项：

```markdown
| ID | 行动项 | 类型 | 优先级 | Owner | 截止日期 | 跟踪链接 | 状态 |
|---|---|---|---|---|---|---|---|
| AI-1 | 动词开头、可验证的描述 | 短期缓解 / 长期改进 / 检测 / 流程 | P0–P4 | 单人 | YYYY-MM-DD | <ticket> | 未开始/进行中/完成 |
```

- "类型"区分**短期**（低垂果实，如开启 2FA、缩短补丁周期）与**长期**（根本性改变，如改造构建流程、组建安全团队）。
- 行动项必须是可验证的结果（"为 X 接入强制 MPA，并有审计日志证明"），而不是"加强 X"。

## 5. 写作规范

1. **区分已确认与未确认**。不要用"可能、大概、应该没事"之类的含糊措辞。写成：
   - 已确认：……（证据：日志/截图/命令输出链接）
   - 未确认：……（原因：例如该环境日志保留不足）
2. **术语先定义**。"已缓解""已修复""已遏制"在不同团队含义不同，首次出现时给出定义。
3. **结论先行**：每节第一句是结论，细节在后。
4. **明确写"不适用"**：模板中某节不适用时，写"不适用"并给出理由，不要删除该节。
5. **时间统一**：时间线使用带时区的 ISO 8601（`2026-10-16T14:05+08:00`），全文同一时区。
6. **IOC 去武器化**：恶意域名、URL、IP 一律写成 `evil[.]example[.]com`、`hxxps://`、`10.0.0[.]1`，防止聊天/文档工具的链接预览向攻击者泄露调查动向。
7. **无责（blameless）**：描述系统、流程与决策背景，不点名指责个人。
8. **可在灾难时访问**：响应类文档（IR 计划、Playbook、联系人）需在公司基础设施之外保留一份可访问副本，并在元数据中注明位置。

## 6. 起草流程（所有文档 skill 共用）

1. **确认文档类型**：根据用户意图选择对应的 `sre-*` skill；若跨多个类型（例如"事故复盘 + 恢复计划"），分别产出并互相链接。
2. **收集输入**：先读用户提供的材料（代码、架构图、日志、聊天记录、旧文档）。缺失的关键信息集中列成问题一次性询问，不要逐条打断。
3. **复制模板**：从对应 skill 的 `assets/template.md` 起草，保留全部章节标题。
4. **填充**：按 skill 中的方法论填写；无法确认的信息标记 `TODO(owner): ...`，不要编造数据、人名、指标或时间。
5. **自检**：逐条执行该 skill 的"质量门禁"清单，以及本文件第 1、4、5 节，把未通过项列给用户。
6. **输出**：默认写入用户仓库中的 Markdown 文件（如 `docs/<type>/<yyyy-mm-dd>-<slug>.md`），并在回复中给出未完成项摘要。

## 7. 评审模式

当用户要求"评审/审查/打分"已有文档时：
- 不重写文档，按对应 skill 的"质量门禁"逐项给出 ✅ / ⚠️ / ❌ 与具体修改建议；
- 先列阻断项（❌），再列建议项；
- 引用文档原文位置（章节名或行号）。

## 出处

- 严重度/优先级模型：[Ch16 Disaster Planning](https://google.github.io/building-secure-and-reliable-systems/raw/ch16.html)
- 风险矩阵：[Appendix A](https://google.github.io/building-secure-and-reliable-systems/raw/appa.html)
- 沟通与 OpSec（含糊措辞、IOC 去武器化）：[Ch17 Crisis Management](https://google.github.io/building-secure-and-reliable-systems/raw/ch17.html)
- 行动项分短期/长期：[Ch18 Recovery and Aftermath](https://google.github.io/building-secure-and-reliable-systems/raw/ch18.html)
