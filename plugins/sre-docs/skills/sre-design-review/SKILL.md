---
name: sre-design-review
description: >-
  Draft or review a standardized security & reliability design document following Google's "Building Secure and Reliable Systems" (Part II) — requirements incl. nonfunctional ones, scalability, redundancy, dependencies, data integrity, SLOs, security/privacy, least privilege, understandability, resilience (degradation, blast radius, failure domains), design for recovery, DoS defense, logging/investigability, and tradeoff analysis. TRIGGER when: the user asks for a 设计文档, 技术方案, design doc, architecture review, 生产就绪评审 (PRR), 安全设计评审, or wants to check a design for reliability/security gaps. DO NOT TRIGGER when: only a threat model (sre-threat-model), only an access-control design (sre-access-control-review), or only a rollout plan (sre-change-rollout-plan) is wanted — this skill links to those instead of duplicating them.
---

# 安全与可靠性设计文档

> 先读 [`../sre-doc-standards/SKILL.md`](../sre-doc-standards/SKILL.md)。

模板：[`assets/template.md`](assets/template.md)

## 核心原则

- 安全与可靠性是**系统的涌现属性**，不是某个模块的功能——必须在系统层面评审：服务拆分、依赖可用性、负载均衡与限流、信任边界、语言与框架选择、审计日志与事件响应工具。
- 它们是像"单体 vs 微服务"一样的**基础性选择**，事后补救代价高昂，且后补的测试容易把现有缺陷固化。早期投入换取持续速度。
- **每一个缓解措施都可能引入新风险**：评审时要追问"这个缓解措施本身的风险是什么"（例：为提高可用性加的重试队列持久化了敏感数据）。

## 起草方法（按模板章节）

1. **需求**：功能需求与关键用户旅程；横切需求；非功能需求——谁在什么条件下可以访问哪些数据、SLO（可用性、延迟分位）、超过负载阈值时的行为；开发效率与交付速度。
2. **可扩展性**：数据量/流量增长模型、初始资源、扩容时间与成本、保留余量。
3. **冗余与可靠性**：本地数据丢失与短暂中断如何处理；备份什么、如何备份、如何恢复；丢失到恢复之间的暴露窗口；部分失效时能否继续服务。
4. **依赖**：每个依赖长时间不可用会怎样；启动时必须存活的依赖（含 DNS、时间源等隐式依赖）；是否存在依赖环。
5. **数据完整性**：如何、多快发现损坏或丢失；覆盖的丢失来源（用户误操作、应用 bug、存储 bug、站点灾难）与各自的恢复方案。
6. **SLA/SLO**：如何监控与审计；靠什么机制保障。
7. **安全与隐私**：链接威胁模型（`sre-threat-model`），列出主要攻击、最坏影响、对策、已知漏洞与不安全依赖；**若认为无安全隐私问题，必须明确写出并解释原因**。
8. **最小权限**：链接访问控制设计（`sre-access-control-review`），至少说明数据分级、人员如何接触生产（零接触/代理）、紧急访问。
9. **可理解性**：系统不变量（如"所有访问都经过鉴权"）；清晰的 API 和安全边界；使用强制安全默认值的框架；身份/鉴权/日志等横切关注点集中处理。
10. **韧性**：
    - 纵深防御：每层独立有效；
    - 可控降级：按关键性与成本给功能排序，决定先关什么；负载丢弃、节流、lame-duck；明确每个组件是 **fail open（保可用）还是 fail closed（保安全）**——安全关键操作不得 fail open；
    - 爆炸半径：网络分段、按角色/地点/时间隔离、按地点签发证书和密钥、跨地点默认禁止通信；
    - 故障域与冗余：独立等价副本、金丝雀故障域、不要同时更新所有故障域、本地保留 last-known-good 配置；高容量/高可用/低依赖三档组件；降级路径不可成为日常依赖，也不可因不用而腐化；
    - 自动化响应要有变更预算，大范围变更需人工批准；紧急访问通道不能被自动化或 DoS 关闭。
11. **面向恢复的设计**：变更系统按"策略允许的最快速度"设计，速率由策略控制而非写死；紧急发布 = 常规发布调到最快；减少对墙上时钟的依赖（用版本号/纪元）；回滚策略——允许回滚自身 bug，但通过 deny list 和**最低可接受安全版本号（MASVN）**阻止回滚到已知漏洞版本；签名密钥可轮换；显式撤销机制（本地缓存撤销列表、不 fail open、不能撤销自身凭据）；以字节级明确"期望状态"并持续比对；恢复路径可测试。
12. **抗 DoS**：识别请求路径上最薄弱的依赖；尽早丢弃坏流量（入口优先用路由器 ACL 而非有状态防火墙）；缓存、减少每页请求数、限制出口带宽；缓解系统独立于被保护的生产设施，控制器故障时 fail static；客户端指数退避 + 抖动，防止自我造成的 DoS。
13. **可观测与可调查**：日志不可篡改（远程集中存储、变更有审计）；保留期足以发现潜伏数月的入侵，同时满足隐私法规；需保留的日志源（OS、主机 agent、应用安全事件、云、网络/DNS/代理）；日志预算与分级存储；调试工具（用户模拟、原始数据库访问）的访问控制。
14. **测试、发布与回滚**：链接 `sre-security-test-plan` 和 `sre-change-rollout-plan`；至少说明 CI/CD、分阶段发布、经常演练的回滚、代码与配置解耦发布（feature flag）。
15. **权衡与备选方案**：每个备选方案写收益、成本、可靠性风险、安全风险；追踪缓解链条。
16. **评审结论**：先做早期安全设计评审，再做最终安全评审。

## 质量门禁

- [ ] 非功能需求含访问规则、SLO 和过载行为
- [ ] 可扩展性、冗余、依赖、数据完整性、SLO 五节完整
- [ ] 隐式依赖（DNS、时间、鉴权、配置）已列出，依赖环已检查
- [ ] 安全与隐私节有威胁、影响、对策，或明确"不适用 + 理由"
- [ ] 每个组件的 fail open / fail closed 选择已写明并说明理由
- [ ] 降级顺序（先关哪些功能）已定义
- [ ] 爆炸半径与故障域划分已说明
- [ ] 回滚策略说明了如何防止回滚到含漏洞版本
- [ ] 密钥/凭据轮换与撤销机制已说明
- [ ] 日志源、保留期、不可篡改措施已说明
- [ ] 每个缓解措施都评估过它引入的新风险
- [ ] 至少一个备选方案及放弃理由
- [ ] 测试、发布、回滚策略已定义（或链接）
- [ ] 遗留问题都转成了行动项

## 出处

- [Ch4 Design Tradeoffs](https://google.github.io/building-secure-and-reliable-systems/raw/ch04.html)（设计文档模板的可靠性与安全章节）
- [Ch6 Design for Understandability](https://google.github.io/building-secure-and-reliable-systems/raw/ch06.html)
- [Ch8 Design for Resilience](https://google.github.io/building-secure-and-reliable-systems/raw/ch08.html)
- [Ch9 Design for Recovery](https://google.github.io/building-secure-and-reliable-systems/raw/ch09.html)
- [Ch10 Mitigating Denial-of-Service Attacks](https://google.github.io/building-secure-and-reliable-systems/raw/ch10.html)
- [Ch15 Investigating Systems](https://google.github.io/building-secure-and-reliable-systems/raw/ch15.html)
