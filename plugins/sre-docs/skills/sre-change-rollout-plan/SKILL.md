---
name: sre-change-rollout-plan
description: >-
  Draft or review a standardized security change & rollout plan following Google's "Building Secure and Reliable Systems" (Ch7 Design for a Changing Landscape, Ch14 Deploying Code) — change type and timeline (zero-day / posture / external demand), incremental-documented-tested-isolated-qualified-staged design, phased rollout with success criteria, audit-only before enforce, acceleration/slowdown/embargo-break contingencies, supply-chain controls (code review, provenance, deployment policy, choke points, breakglass). TRIGGER when: the user asks for 变更方案, 发布计划, 上线方案, rollout plan, 漏洞修复推进计划, 0day 应急补丁计划, 安全基线推广计划, 合规改造计划, or a deployment/supply-chain security review. DO NOT TRIGGER when: the user is executing an already-approved routine deploy, or responding to an active incident (sre-incident-doc).
---

# 安全变更与发布计划

> 先读 [`../sre-doc-standards/SKILL.md`](../sre-doc-standards/SKILL.md)。

模板：[`assets/template.md`](assets/template.md)

## 起草方法

### 1. 定性：变更类型与时间尺度
类型：响应事件或新漏洞 / 产品功能变更 / 内部安全加固 / 外部驱动（法规）/ 依赖变更（第三方代码需满足安全要求）。

| 时间尺度 | 典型场景 | 计划重点 |
|---|---|---|
| 短期（小时-天） | 0day、紧急漏洞 | 分级与影响、验证补丁有效、按小时/天渐进发布；无补丁时先限制对漏洞组件的访问 |
| 中期（周-月） | 提升安全基线 | 按群体分阶段，每阶段有成功标准；先选最容易（建立势头）或最难（尽早暴露问题）的群体；先审计/告警模式再强制；尽量提供 opt-in |
| 长期（季度-年） | 合规、外部要求 | 可度量目标、文档保持可交接、合规检查自动化、自助式度量；持续获得管理层支持；80–90% 覆盖已能显著降低风险 |

### 2. 变更本身的设计（逐条满足）
- **增量**：小而独立，不与重构等无关工作捆绑；
- **有文档**：原因与方法、需求、受影响系统与团队、POC 结论、决策依据、联系人；
- **经过测试**：单元测试、可行时集成测试、同行评审；
- **隔离**：用 feature flag，关闭时行为完全不变；
- **经过验证**：走正常发布流程，逐级通过验证阶段；
- **分阶段**：金丝雀发布，变更前后的行为差异可观测。宁可慢也不要造成中断或数据丢失。

### 3. 供应链控制（每次发布都要说明）
- 强制代码评审（相当于 MPA），由工具强制；
- 构建、测试、部署全部自动化，流水线变更也要评审；
- 验证**制品**而非人：部署环境要求证明自动化步骤已执行；
- 配置即代码，秘密单独保护且不入库；
- 二进制来源证明（provenance）：签名、输出哈希、输入（源码与依赖）、命令、环境、版本；
- 基于 provenance 的部署策略：评审过、来自批准的仓库、官方流水线构建、测试通过、近期扫描过；
- 所有部署经过单一卡点（如准入控制器），禁止绕过；
- 部署后验证：日志足以在策略变化或 breakglass 后重新评估；
- 报错可操作（告诉用户哪里失败、如何修复）；
- breakglass 可用，但每次使用都告警和审计。

### 4. 预案：计划变化时怎么办
- **加速**：出现在野利用 → 先覆盖高风险系统，或对关键系统限流/下线（更快不一定更安全）；
- **减速**：补丁引发错误 → 放慢、回滚、排查、重试；
- **外部延迟**：与漏洞团队协调，准备对受影响用户的沟通；
- **禁运被打破**：为每个阶段预先准备行动方案；
- **暴露有限**：优先修补少数对外服务，其余放慢；
- **依赖厂商**：为厂商补丁或硬件延迟留余量。

### 5. 让系统更易于变更（长期建议，可作为行动项）
依赖保持最新；频繁重建与重新部署；高频小版本发布 + 自动化测试；容器镜像不可变、只在仓库修补镜像并强制只部署近期构建的镜像；微服务独立发布；内部流量默认不信任；共享入口层统一做 DDoS 吸收与证书终结；控制面与数据面分离；定期轮换密钥（Heartbleed 的教训）；自动扫描受影响系统 + 集中跟踪。

## 质量门禁

- [ ] 写明变更类型与时间尺度
- [ ] 六项变更设计原则（增量/文档/测试/隔离/验证/分阶段）逐条说明
- [ ] 有分阶段计划，每阶段有范围、成功标准、观察期、负责人
- [ ] 有回滚方案，且回滚不会重新引入已知漏洞
- [ ] 中长期变更先审计/告警模式再强制
- [ ] 供应链控制已说明（评审、provenance、部署策略、卡点、breakglass）
- [ ] 加速/减速/禁运被打破的预案已写
- [ ] 沟通计划（内部团队与受影响用户）已写
- [ ] 进度度量方式（覆盖率、扫描结果）已定义

## 出处

- [Ch7 Design for a Changing Landscape](https://google.github.io/building-secure-and-reliable-systems/raw/ch07.html)
- [Ch14 Deploying Code](https://google.github.io/building-secure-and-reliable-systems/raw/ch14.html)
