---
name: sre-playbook
description: >-
  Draft or review a standardized task-level playbook / runbook following Google's "Building Secure and Reliable Systems" (Ch16 playbooks, Ch9 emergency access, Ch17 OpSec) — trigger and scope, prerequisites and pre-approved access, step-by-step commands with expected output and verification, decision points, security/OpSec cautions, rollback, escalation time limits, low-dependency fallbacks, and offline availability. TRIGGER when: the user asks for a playbook, runbook, SOP, 操作手册, 应急手册, 故障处理手册, 切换手册, breakglass 操作步骤, or wants an alert linked to handling steps. DO NOT TRIGGER when: the user needs the overall IR process (sre-incident-response-plan) or a recovery plan for a specific ongoing compromise (sre-recovery-plan).
---

# 操作手册（Playbook / Runbook）

> 先读 [`../sre-doc-standards/SKILL.md`](../sre-doc-standards/SKILL.md)。

模板：[`assets/template.md`](assets/template.md)

## 定位

Playbook 是**任务级**的分步指令（如授予紧急管理员权限、解析某类日志、故障切换、开启优雅降级），由响应计划引用，按团队维护、频繁修订。它的读者是**压力下、可能刚被叫醒的值班人**。

## 起草方法

1. **一个 Playbook 只做一件事**：标题用"动词 + 对象"，如"切换 X 到备用区域"。
2. **触发条件**：哪个告警/症状触发，链接到告警规则；明确**不适用**的情况。
3. **前置条件**：所需权限（预批准访问还是 breakglass）、工具、网络位置；主依赖不可用时的**低依赖替代路径**（离线凭据、带外访问、电话桥）。
4. **步骤**：编号、每步一个动作；给出**可直接复制的命令**、预期输出、如何验证成功；危险步骤前标注 ⚠️ 并要求"手离键盘"确认（hands-off-keyboard briefing）。不写"检查一下"这类无法执行的指令。
5. **决策点**：用"如果……则跳到步骤 N"表达分支；写明需要谁批准（如需 MPA）。
6. **安全注意事项**（安全类 Playbook 必填）：
   - 在确定范围前不要锁账号、改密码或下线系统，以免惊动攻击者；
   - 不要用可能已泄露的凭据登录被入侵主机，优先用预部署的取证 agent；
   - 不要访问攻击者基础设施（下载样本、扫描、查询域名）；
   - IOC 去武器化书写；
   - 先保全证据（快照、镜像）再修复；
   - 记录自己每一步操作的时间和命令，以便区分自身操作与攻击者痕迹。
7. **回滚**：每个改变状态的步骤都要有对应的回滚步骤。
8. **升级**：单独处理的时间上限（如 15 分钟）、升级给谁、联系方式（含备用）。
9. **日常化**：紧急流程应尽量和日常流程一致，让人在压力下靠习惯操作；能在日常工作中使用的应急工具就日常使用，防止腐化。
10. **可用性**：在公司基础设施外保留可访问副本；与系统变更同步更新；每次演练或实战后修订。

## 质量门禁

- [ ] 标题为"动词 + 对象"，只覆盖一个任务
- [ ] 触发条件与不适用情况已写明，并链接告警
- [ ] 前置权限与工具已列出，含主依赖失效时的替代路径
- [ ] 每步有可执行命令、预期输出和验证方法
- [ ] 危险步骤有 ⚠️ 标记与确认要求
- [ ] 所有改变状态的步骤都有回滚
- [ ] 有升级时限和升级联系人（含备用）
- [ ] 安全类 Playbook 含 OpSec 与证据保全注意事项
- [ ] 有"最近一次演练/使用"记录和离线副本位置

## 出处

- [Ch16 Disaster Planning](https://google.github.io/building-secure-and-reliable-systems/raw/ch16.html)
- [Ch9 Design for Recovery](https://google.github.io/building-secure-and-reliable-systems/raw/ch09.html)（紧急访问与响应者习惯）
- [Ch17 Crisis Management](https://google.github.io/building-secure-and-reliable-systems/raw/ch17.html)（OpSec 常见错误）
- [Ch18 Recovery and Aftermath](https://google.github.io/building-secure-and-reliable-systems/raw/ch18.html)（清单与手离键盘确认）
