---
name: sre-postmortem
description: >-
  Drafts or reviews a blameless postmortem (复盘/故障报告): impact, timeline, response timing, contributing factors, detection gaps, short- and long-term action items with owners. TRIGGER when: the user asks for a postmortem, PIR, or 事故总结. DO NOT TRIGGER when: the incident is still active (sre-incident-doc) or for exercise reports.
---

# 无责事后复盘

> 先读 [`../sre-doc-standards/SKILL.md`](../sre-doc-standards/SKILL.md)。

模板：[`assets/template.md`](assets/template.md)

## 原则

- **无责**：关注系统、流程和程序的改进，不追究个人。
- 以事件文档、恢复计划和响应者笔记为原始材料；恢复结束后**尽快**完成，趁记忆清晰、修复尚未被搁置。
- 行动项分为**短期**（低垂果实，如开启 2FA、缩短补丁周期、启动漏洞披露计划）和**长期**（根本性改变，如组建安全团队、骨干网加密、更换操作系统选型），各自有 Owner 和时间。
- 利用两次事件之间的平静期学习、识别威胁、为下一次做准备。

## 起草方法

1. **摘要**：3–5 句话——发生了什么、影响、根本原因类别、最重要的改进。
2. **影响**：用户、数据、业务、合规影响，尽量量化；区分已确认与未确认。
3. **时间线**：从事件文档提炼关键节点（带时区）。
4. **响应各阶段计时**：发现 → 上报 → 分诊 → 声明 → 遏制/缓解 → 恢复 → 关闭，标出延迟及原因。
5. **必答问题**（安全视角，可靠性事件同样适用）：
   - 主要促成因素是什么？其他地方是否存在类似问题？
   - 哪些测试或审计本应更早发现？能否建立？
   - 预期的控制（如入侵检测、告警）是否发现了它？没有的话如何改进检测？
   - 检测和响应是否足够快？
   - 敏感数据保护是否足够？需要哪些新控制？
   - 恢复团队能否有效使用源码管理、部署、测试、备份与恢复工具？
   - 绕过了哪些常规流程（如紧急变更、breakglass）？现在需要什么补救？
   - 临时搭建的基础设施或工具是否需要重构或移除？
   - 事件期间提交了哪些 bug，需要修复？
   - 哪些业界或同行实践可能在某个阶段有帮助？
6. **做得好的地方 / 运气成分**：保留下来的做法和侥幸之处同样重要。
7. **行动项**：符合共享格式；每个促成因素至少对应一个行动项；把发现回流到威胁模型、风险评估、Playbook、检测规则，并标明更新了哪份文档。
8. **确认隔离资产**：恢复期间临时保留的被入侵资产已永久处理。

## 质量门禁

- [ ] 无责措辞，无个人指责
- [ ] 影响已量化，区分已确认/未确认
- [ ] 时间线带时区；各阶段耗时与延迟原因已列出
- [ ] 十个必答问题全部回答（不适用需说明）
- [ ] 每个促成因素都有对应行动项
- [ ] 行动项分短期/长期，均有 Owner、截止日期和跟踪链接
- [ ] 列出被绕过的流程和需移除的临时改动
- [ ] 标明需更新的威胁模型/风险评估/Playbook/检测规则
- [ ] 临时隔离资产已确认永久处理
- [ ] 密级与分发范围适当（安全事件默认严格受限）

## 出处

- [Ch18 Recovery and Aftermath — After the Recovery](https://google.github.io/building-secure-and-reliable-systems/raw/ch18.html)
- [Ch16 Disaster Planning — Evaluating Responses](https://google.github.io/building-secure-and-reliable-systems/raw/ch16.html)
- [Ch21 Building a Culture of Security and Reliability](https://google.github.io/building-secure-and-reliable-systems/raw/ch21.html)（无责文化）
