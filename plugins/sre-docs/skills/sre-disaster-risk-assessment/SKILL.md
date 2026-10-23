---
name: sre-disaster-risk-assessment
description: >-
  Drafts or reviews a disaster risk assessment (灾难风险评估/风险矩阵): critical systems, environmental, infrastructure, and security risks scored by probability x impact, outlier review, response mapping. TRIGGER when: the user asks for BCP/DR risk analysis. DO NOT TRIGGER when: an adversary threat model (sre-threat-model) is wanted.
---

# 灾难风险评估

> 先读 [`../sre-doc-standards/SKILL.md`](../sre-doc-standards/SKILL.md)——风险刻度与打分规则见第 3 节。

模板：[`assets/template.md`](assets/template.md)

## 起草方法

1. **识别关键系统**：找出一旦丢失会导致整体中断的业务运行，包括其依赖（网络、应用层）。分三级：
   - 使命必需（mission-essential）
   - 使命重要（mission-important）
   - 非必需（nonessential）
2. **识别响应所需资源**：技术资源（备件、备用站点、离线凭据、带外访问）与人员资源（技能、值班、外包合同）。
3. **列出风险**：按三个主题逐项判断，再补充本组织特有项：
   - **环境**：地震、洪水、火灾、台风/飓风（与站点地理位置相关）；
   - **基础设施可靠性**：断电、互联网连接中断、认证系统故障、高延迟/基础设施变慢、配置错误、接近容量阈值的降级；
   - **安全**：系统被入侵、内部人员窃取知识产权、DoS/DDoS、资源滥用（如挖矿）、网站篡改、钓鱼、软硬件安全漏洞、新出现的严重漏洞（如 Heartbleed、Meltdown/Spectre 级别）、长期未被发现的外部入侵、未授权数据披露。
4. **打分排序**：概率 × 影响（共享约定第 3 节），从高到低排序；用标准化矩阵而非直觉，避免群体思维。
5. **离群复核**：低概率但灾难性影响的项单独讨论，必要时提升为关键风险；邀请外部专家找隐藏因素和依赖。
6. **按站点评估**：多站点组织要整体评估并按站点分别评估。增加冗余（双线路、备用电源）后需重新打分。
7. **映射响应计划**：排名靠前的风险必须对应一份响应计划或 Playbook（`sre-incident-response-plan` / `sre-playbook`），并纳入演练（`sre-dr-exercise`）。
8. **定期复审**：至少每年一次，或在架构、站点、业务发生重大变化时。

## 质量门禁

- [ ] 关键系统已按三级分类，且列出依赖
- [ ] 响应所需技术与人员资源已列出
- [ ] 环境 / 基础设施 / 安全三个主题均已覆盖
- [ ] 每个风险都有概率、影响、风险分、受影响系统和打分依据
- [ ] 已排序并完成离群复核
- [ ] 多站点时有按站点的评估
- [ ] Top N 风险都映射到响应计划/Playbook 和演练
- [ ] 写明下次复审日期

## 出处

- [Ch16 Disaster Planning](https://google.github.io/building-secure-and-reliable-systems/raw/ch16.html)
- [Appendix A: A Disaster Risk Assessment Matrix](https://google.github.io/building-secure-and-reliable-systems/raw/appa.html)
