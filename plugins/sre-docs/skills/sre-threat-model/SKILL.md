---
name: sre-threat-model
description: >-
  Drafts or reviews a threat model (威胁建模): assets, attacker motives and profiles, insider scenarios, kill-chain controls, supply-chain threats, risk ranking. Based on Building Secure and Reliable Systems. TRIGGER when: the user asks for a threat model, 对手分析, or attack surface review. DO NOT TRIGGER when: a full design doc (sre-design-review) or disaster risk matrix is wanted.
---

# 威胁建模文档

> 先读 [`../sre-doc-standards/SKILL.md`](../sre-doc-standards/SKILL.md)：元数据头、风险打分、行动项格式、写作规范均以其为准。

模板：[`assets/template.md`](assets/template.md)

## 何时写

- 新系统/新功能设计阶段（作为设计文档的输入或附录）。
- 系统暴露面、数据敏感度或用户群显著变化时。
- 至少每年复审一次；重大安全事件后必须复审。

## 起草方法

### 1. 先界定"保护什么"
列出资产及其密级（公开 / 敏感 / 高度敏感），包括容易遗漏的：凭据与签名密钥、日志与元数据、源代码、构建与发布系统、配置分发系统、位置/通信等对国家级攻击者有吸引力的数据。画出信任边界与数据流。

### 2. 攻击者动机（逐条判断是否适用）
好奇/炫技、成名、社会/政治诉求、经济利益、胁迫、操纵（散布虚假数据、改变行为）、间谍（含商业间谍）、破坏（毁数据、使系统下线）。同一攻击者可能有多个动机。

### 3. 攻击者画像（逐条判断，并写出对本系统意味着什么）
| 画像 | 关注点 |
|---|---|
| 爱好者 | 往往是盟友，可通过漏洞披露渠道转化 |
| 漏洞研究员 / 红队 | 有无漏洞奖励与披露流程 |
| 政府 / 执法机构 | 是否持有其感兴趣的数据；防御成本可能超过组织能力，目标是提高攻击成本与风险 |
| 黑客行动主义者 | 产品是否涉及争议话题；重点：补丁、分层控制、抗 DoS、快速从备份恢复 |
| 犯罪分子 | 欺诈、勒索软件、社会工程；目标是持续抬高攻击成本 |
| 自动化 / AI 攻击 | 自动发现与利用漏洞；需要安全默认值与自动化的防御迭代 |
| 内部人员 | 第一方（员工、高管）、第三方（承包商、供应商、开源贡献者）、关联方（家人、室友） |

### 4. 内部人员风险：组合成场景
按 **角色 × 动机 × 动作 × 目标** 生成场景，逐一评估：
- 动机：意外、疏忽、账号被盗、经济、意识形态、报复、虚荣……
- 动作：访问、外传、删除、篡改、注入、泄露……
- 目标：用户数据、源代码、文档、日志、基础设施、服务、财务数据
- 由于意图难以判断，**恶意与意外场景同等设计**。

对应控制：最小权限、零信任/通过代理访问、多方授权（MPA）、业务理由、访问审计与检测、破坏性操作可恢复。

### 5. 攻击链阶段与控制
对每个阶段写出现有控制、检测手段和缺口：
侦察 → 初始进入 → 横向移动 → 持久化 → 达成目标。
具体技术可参照 MITRE ATT&CK 逐项展开。重点放在 TTP（战术、技术、过程），而不是猜测攻击者身份——归因很难，且攻击者会伪装。

### 6. 供应链威胁（有构建/发布流程时必填）
未经评审或有漏洞的代码进入生产、从本地或任意仓库构建、部署带调试开关的配置、篡改二进制或存储 ACL、签名密钥被盗、回滚到含已知漏洞的旧版本、恶意构建脚本或被植入后门的编译器。对每项写出现有缓解与局限。

### 7. 评分与排序
按共享约定第 3 节的 概率 × 影响 打分排序，并做离群复核。注意：
- 你可能在不知情时成为目标，或被当作攻击他人的跳板；
- 攻击复杂度不代表成功率——钓鱼等廉价手段最常见，先补基础（如 2FA）；
- 不要低估资金充足的攻击者，也不要假设攻击者畏惧法律追责。

## 质量门禁

- [ ] 资产清单含密级，且覆盖凭据/密钥、日志、构建发布系统
- [ ] 有信任边界或数据流图（或链接）
- [ ] 8 类动机、7 类画像均已判断"适用/不适用 + 理由"
- [ ] 至少 3 个内部人员场景（含 1 个意外场景）
- [ ] 攻击链 5 个阶段均有"现有控制 / 检测 / 缺口"
- [ ] 有构建发布流程时，供应链威胁表已填
- [ ] 风险已按 概率×影响 排序，并完成离群复核
- [ ] 每个高风险缺口都对应一个有 Owner 和日期的行动项
- [ ] 写明下次复审日期与触发复审的条件

## 出处

- [Ch2 Understanding Adversaries](https://google.github.io/building-secure-and-reliable-systems/raw/ch02.html)
- [Ch5 Design for Least Privilege](https://google.github.io/building-secure-and-reliable-systems/raw/ch05.html)（内部风险控制）
- [Ch8 Design for Resilience](https://google.github.io/building-secure-and-reliable-systems/raw/ch08.html)（纵深防御各阶段）
- [Ch14 Deploying Code](https://google.github.io/building-secure-and-reliable-systems/raw/ch14.html)（供应链威胁模型）
