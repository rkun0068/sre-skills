---
name: sre-dr-exercise
description: >-
  Drafts or reviews a DR or incident-response exercise plan and report (演练计划/桌面推演/game day): audits, tabletops, fault injection, failover tests, red team, stage timing, follow-ups. TRIGGER when: the user asks for 容灾演练, tabletop, or 演练报告. DO NOT TRIGGER when: a real incident postmortem or code test plan is wanted.
---

# 演练计划与演练报告

> 先读 [`../sre-doc-standards/SKILL.md`](../sre-doc-standards/SKILL.md)。

模板：[`assets/template.md`](assets/template.md)（上半部分为计划，下半部分为报告）

## 原则

- 测试**自动化系统、流程和人**三者，至少每年一次。
- 没有文档或拿不到的流程，在真实事件中大概率不会被执行——计划的每一层都要测。
- 失败的演练同样有价值：写清哪些有效、哪些要改进。

## 演练类型（选一种或组合）

| 类型 | 适用 | 要点 |
|---|---|---|
| 自动化系统审计 | 季度/年度 | 备份（正确创建、安全存放、保留期、权限、恢复验证）；事件日志（存储与保留足以重建时间线）；补丁（关键漏洞及时修补，自动和手动流程都审计）；告警（每条规则能触发，考虑依赖——网络中断时邮件服务器挂了怎么办）；沟通工具（可用、可切换、保留复盘所需记录） |
| 桌面推演 | 不触碰生产 | 可信（基于真实攻击/漏洞）；细节（主持人提前研究，准备日志、客户报告、告警等素材）；60 分钟约 10–20 个决策点，选择影响后续剧情；参与者含一线工程师、高层、公关、法务；参与者实际执行动作而非口头描述；产出可执行反馈与有 Owner 的行动项 |
| 单系统 / 故障注入 | 生产或准生产 | 用代理注入错误或延迟，验证超时处理；分步加压并能快速取消；也可测内部人员场景（如检测违规 U 盘拷贝） |
| 人员不可用 | 组织韧性 | 关键人物不在时团队能否推进 |
| 多组件故障 | 依赖链 | 同时失效；故障切换时 ACL 是否仍生效、依赖服务是否 fail closed |
| 全系统切换 | 区域/数据中心 | 主备数据中心或云区域切换，检查用户可见影响 |
| 红队演练 | 安全检测与响应 | 由内部安全团队模拟真实攻击，响应者不提前知情（仅高层知情）；覆盖外部、内部和社会工程 |

## 起草方法

1. **目标与假设**：要验证哪份计划/Playbook/控制，期望结果是什么；关联灾难风险评估中的风险编号。
2. **范围与安全护栏**：影响范围、禁止动作、**中止条件与中止命令**、回滚方案、需提前通知的对象（红队除外，但需高层授权书面记录）。
3. **场景与剧本**：桌面推演写出注入点（时间、素材、预期决策）；故障注入写出分步加压计划。
4. **角色**：主持人、观察员/计时员、记录员、参与者、安全官（负责中止）。
5. **度量**：对每个响应阶段计时——发现、上报、分诊、声明、缓解、恢复——找出延迟。
6. **执行后报告**：时间线、度量结果、有效之处、问题、对计划/Playbook/检测规则的修订、行动项。安全演练保留日志供后续分析；把演练产生的痕迹回灌到检测，补上缺口；紫队式回归确认已修复问题不再复现。
7. **无责**：报告聚焦系统、流程和计划的改进。

## 质量门禁

计划：
- [ ] 目标明确，关联到具体计划/Playbook/风险
- [ ] 有中止条件、中止命令与安全官
- [ ] 有回滚方案和影响范围
- [ ] 桌面推演有 10–20 个决策点与素材；参与者跨职能
- [ ] 红队演练有高层书面授权
- [ ] 定义了按阶段的计时度量

报告：
- [ ] 有带时区的时间线和各阶段耗时
- [ ] 写明有效之处与问题
- [ ] 列出需修订的计划/Playbook/告警规则及负责人
- [ ] 检测缺口已回灌
- [ ] 行动项符合共享格式

## 出处

- [Ch16 Disaster Planning — Testing Systems and Response Plans](https://google.github.io/building-secure-and-reliable-systems/raw/ch16.html)
- [Ch8 Design for Resilience — Continuous Validation](https://google.github.io/building-secure-and-reliable-systems/raw/ch08.html)
- [Ch20 Understanding Roles and Responsibilities](https://google.github.io/building-secure-and-reliable-systems/raw/ch20.html)（红队/蓝队）
