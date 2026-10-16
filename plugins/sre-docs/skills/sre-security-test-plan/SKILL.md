---
name: sre-security-test-plan
description: >-
  Draft or review a standardized security & reliability test plan following Google's "Building Secure and Reliable Systems" (Ch12 Writing Code, Ch13 Testing Code) — secure-by-default frameworks, unit tests with security edge cases, hermetic integration tests without production data, sanitizers, continuous fuzzing, static analysis / linters / abstract interpretation / formal methods, and how each is wired into CI and code review. TRIGGER when: the user asks for 测试计划, 安全测试方案, fuzz 计划, 静态扫描接入方案, test strategy for a security-sensitive component, or a review of test coverage for security/reliability. DO NOT TRIGGER when: the user just wants a specific unit test written, or is planning DR drills / tabletop exercises (sre-dr-exercise).
---

# 安全与可靠性测试计划

> 先读 [`../sre-doc-standards/SKILL.md`](../sre-doc-standards/SKILL.md)。

模板：[`assets/template.md`](assets/template.md)

## 起草方法

1. **先选框架，再写测试**：优先使用"安全默认、按构造安全"的框架（如自动转义的模板、类型安全的 SQL 构造、集中鉴权），从源头消除整类漏洞（XSS、SQL 注入等）。列出组件涉及的常见漏洞类别以及由哪个框架/库消除。简单的代码更安全可靠。
2. **单元测试**：
   - 快速、可靠、密封（hermetic），不稳定测试立即修；
   - 覆盖安全边界：负数、接近类型上限的溢出、畸形/恶意输入；参数化测试；
   - 何时写：与代码同时、TDD、或在缺陷报告和安全评审之后写回归测试；
   - 评审时确认改坏代码后测试会失败（变异测试）；
   - 外部依赖放在接口后用 mock/fake，但避免过度抽象（变成测调用顺序）；
   - 有现成一致性套件时直接用（如密码学测试向量）。
3. **集成测试**：用真实依赖跑完整路径；**禁止把生产敏感数据复制到测试环境**，用非敏感种子数据并对测试环境施行最小权限；指向 QA 端点而非生产；在关键步骤打日志便于排查。
4. **动态分析**：用 ASan / UBSan / TSan / MSan / LSan 等 sanitizer；因为慢，安排在 CI 之外的定期流水线（如每晚）。
5. **模糊测试**：优先覆盖解析器、解码器、协议处理器；配合 sanitizer；种子语料 + 结构化字典 + 多引擎；关注覆盖率平台期；fuzz driver 要确定性、快、无日志与磁盘 IO；绕开攻击者可轻易伪造的完整性校验；持续 fuzz——每天构建、去重崩溃、自动回归与提单。
6. **静态分析**：linter 与代码检查工具前置到编辑器与代码评审，误报率要低；抽象解释类深度分析每晚或对变更代码运行；安全关键或密码学组件考虑形式化方法；在开发者已在用的界面展示告警、尽量提供自动修复、收集"无用"反馈调优规则。
7. **接入点与门禁**：说明每种测试在何时运行（提交前/评审/CI/每晚/持续）、是否阻断合入、失败由谁处理。

## 质量门禁

- [ ] 列出组件相关的漏洞类别及消除它们的框架/库
- [ ] 单元测试覆盖安全边界与恶意输入
- [ ] 有回归测试策略（缺陷/安全评审后补测试）
- [ ] 集成测试不使用生产敏感数据，不访问生产端点
- [ ] 内存不安全语言的组件接入了 sanitizer
- [ ] 解析/解码/协议处理代码有持续 fuzz，并配合 sanitizer
- [ ] 静态分析接入代码评审，并有误报反馈机制
- [ ] 每种测试的运行时机、是否阻断、失败处理人已写明
- [ ] 有覆盖率或效果度量

## 出处

- [Ch12 Writing Code](https://google.github.io/building-secure-and-reliable-systems/raw/ch12.html)
- [Ch13 Testing Code](https://google.github.io/building-secure-and-reliable-systems/raw/ch13.html)
