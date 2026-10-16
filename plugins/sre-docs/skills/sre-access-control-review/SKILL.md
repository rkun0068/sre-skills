---
name: sre-access-control-review
description: >-
  Draft or review a standardized least-privilege / access-control design document following Google's "Building Secure and Reliable Systems" (Ch5 Design for Least Privilege, Ch3 Safe Proxies) — risk-based access classification, small functional APIs, zero trust / zero touch, authorization policy, multi-party authorization, business justification, temporary access, proxies, breakglass, auditing, and denial diagnostics. TRIGGER when: the user asks for 权限设计, 访问控制方案, 最小权限评审, IAM / RBAC design, 生产访问管控, breakglass / 应急权限设计, or an access review of a system. DO NOT TRIGGER when: the task is a one-off permission request or grant, or a full design doc (sre-design-review links here).
---

# 最小权限 / 访问控制设计

> 先读 [`../sre-doc-standards/SKILL.md`](../sre-doc-standards/SKILL.md)。

模板：[`assets/template.md`](assets/template.md)

## 关键概念

- **最小权限**：人、自动化任务、机器只拿到完成特定任务所需的权限，**没有常驻的环境权限**（如长期 root）。
- **零信任网络**：网络位置不代表任何权限，访问基于用户与设备凭据。
- **零接触（Zero Touch）**：人通过自动化和安全 API 间接操作生产，而不是直接持有生产角色。
- 读权限可能和写权限一样危险——宽泛的读权限可导致大规模数据泄露。

## 起草方法

1. **访问分级**：定义少量、清晰、一致的数据等级（如 公开 / 敏感 / 高度敏感），对每级评估 读 / 写 / 基础设施 三类访问的风险。高度敏感数据**不允许常驻访问**。
2. **角色与访问路径清单**：列出所有主体（人、服务账号、CI、机器），各自的访问路径（API、交互式 shell、控制台、数据库直连）和权限范围。
3. **API 设计**：小而专一的功能性 API，便于细粒度授权、审计和推理。管理 API 与用户 API 同等审视。尽量消除宽泛的交互式会话——它难以约束和审计，会话日志也容易被绕过。如需替代，考虑安全代理（Safe Proxy）：集中鉴权、MPA、限速、审计。
4. **授权决策**：使用成熟的强认证，然后对每个请求按策略授权；输入包括动作、参数、请求来源、角色元数据、服务端上下文。使用共享授权框架和外置策略（改规则不改代码），策略与二进制分开发布。策略语言既不能过于简单也不能过于通用。
5. **高级控制**（按风险选用，写明适用范围）：
   - 多方授权（MPA）：审批人需要足够上下文并且能说"不"；
   - 三因素授权（3FA）：在独立加固设备上批准，防工作站群被攻破；区别于提升认证的 2FA；
   - 业务理由：如关联工单，默认拒绝；
   - 临时访问：限时授权（如值班期间），减少常驻权限；
   - 代理/堡垒机：强制审批、限速、增强日志。
6. **审计**：记录细粒度操作及 谁/什么/何时/为什么；结构化理由（工单号）以便程序化审计；breakglass 使用在团队层面做最佳实践复查、在中心层面做入侵检测。
7. **测试**：在权限变更上线前验证角色"够用且不多"；测试环境和凭据与生产隔离。
8. **拒绝诊断**：对低权限调用方少暴露信息；对高权限调用方给出拒绝 token 和修复提示，并提供支持渠道。
9. **Breakglass**：仅限 SRE、限定物理位置/终端、每次使用都告警和审计、定期演练。
10. **权衡**：细粒度控制增加复杂度——需要工具回答"谁能访问它"和"他能访问什么"；过严会把人推向写通用理由或在生产里测试；提供培训、文档、自助诊断和快速联系安全专家的通道。

## 质量门禁

- [ ] 有数据分级表，覆盖读/写/基础设施三类访问
- [ ] 高度敏感数据无常驻访问
- [ ] 所有主体（人/服务/CI/机器）与访问路径已列出
- [ ] 交互式 shell 访问已最小化，或说明为何保留及补偿控制
- [ ] 授权策略外置且独立发布
- [ ] 高风险操作已明确 MPA / 业务理由 / 临时访问中的哪些控制
- [ ] 审计日志包含谁/什么/何时/为什么，理由可程序化校验
- [ ] Breakglass 有限定、告警、审计和演练周期
- [ ] 能回答"谁能访问 X"和"Y 能访问什么"（工具或方法）
- [ ] 权限变更有上线前测试
- [ ] 对开发效率的影响与缓解已说明

## 出处

- [Ch5 Design for Least Privilege](https://google.github.io/building-secure-and-reliable-systems/raw/ch05.html)
- [Ch3 Case Study: Safe Proxies](https://google.github.io/building-secure-and-reliable-systems/raw/ch03.html)
