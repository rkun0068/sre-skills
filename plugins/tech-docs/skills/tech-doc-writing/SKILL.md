---
name: tech-doc-writing
description: >-
  Drafts developer and user docs in Google style: README, quickstart, how-to, tutorial, concept, CLI/API/config reference, troubleshooting, release notes. Picks the doc type, gathers facts from code, fills a template, verifies commands, lints. TRIGGER when: the user asks to write 使用文档、用户手册、README、教程. DO NOT TRIGGER when: only reviewing style, or writing SRE or design docs.
---

# 编写技术文档与用户文档

> 先读 [`../tech-doc-style/SKILL.md`](../tech-doc-style/SKILL.md)：风格规则、lint 用法和评审模式以它为准。

## 流程

```
- [ ] 1. 明确读者、目标和语言
- [ ] 2. 确定文档类型（见下表）
- [ ] 3. 从可靠来源收集事实，不要编造
- [ ] 4. 复制对应的模板，先写大纲，再写正文
- [ ] 5. 验证命令、占位符和链接
- [ ] 6. 运行 lint 并按检查清单自检
- [ ] 7. 输出文件，并列出未完成的 TODO
```

### 1. 明确读者与目标

缺少以下信息时，一次性问清楚，不要一条条地追问：

- **读者是谁**：开发者、运维人员，还是终端用户？读者已经知道什么？
- **读完之后能做什么**：用一句话说明，例如"能在本地运行服务并调用第一个 API"。
- **用什么语言写**：中文还是英文，或者跟随项目已有的文档。写中文时，额外读 `../tech-doc-style/references/chinese-docs.md`。
- **放在哪里，用什么格式**：例如 `docs/` 目录、Wiki、文档站点，Markdown 还是其他格式；项目有没有自己的风格指南和术语表。

### 2. 选择文档类型

一篇文档只服务一种需求。需求混在一起时，拆成多篇，并互相链接。

| 读者的需求 | 类型 | 模板 |
|---|---|---|
| 这个项目是什么，怎么开始用 | README | [assets/readme.md](assets/readme.md) |
| 用最短的路径跑通一次 | Quickstart | [assets/quickstart.md](assets/quickstart.md) |
| 完成某个具体任务 | How-to 指南 | [assets/how-to.md](assets/how-to.md) |
| 边做边学，端到端完成一个场景 | 教程（Tutorial） | [assets/tutorial.md](assets/tutorial.md) |
| 理解原理、架构或术语 | 概念文档（Concept） | [assets/concept.md](assets/concept.md) |
| 查某个命令、参数、配置项或 API | 参考文档（Reference） | [assets/reference.md](assets/reference.md) |
| 出了问题，怎么解决 | 问题排查（Troubleshooting） | [assets/troubleshooting.md](assets/troubleshooting.md) |
| 这个版本改了什么 | 发布说明（Release notes） | [assets/release-notes.md](assets/release-notes.md) |

不属于本 skill 的文档：
- 设计文档 → `sre-design-review`
- 值班手册、应急手册 → `sre-playbook`
- 事故复盘 → `sre-postmortem`

### 3. 收集事实

事实以以下来源为准，按优先级从高到低：

1. 代码本身：入口、参数解析、配置的数据结构、错误信息
2. 命令自带的帮助：`--help`、`man`
3. 测试用例和 CI 配置
4. 已有的文档和 CHANGELOG
5. 向用户提问

规则：
- **不要编造** flag、默认值、输出或版本号。无法确认的地方，写成 `TODO(owner): 待确认 …`，并在最后的回复里汇总。
- 能在安全环境里实际运行的命令，运行一遍，用真实的输出替换示例。不要在生产环境里运行任何有副作用的命令。
- 示例中不要出现真实的密钥、内部主机名或用户数据。使用 `example.com`、`203.0.113.0/24` 和占位符。

### 4. 写作

- 从模板开始，保留模板中的章节结构。模板里的 `<!-- -->` 注释是写作提示，写完后删除。
- 先写大纲，也就是全部标题，确认结构合理后再写正文。
- 页面开头用一两句话说明：这篇文档讲什么、适合谁读、读完能做什么。
- 前提条件放在第一步之前。步骤按照 `../tech-doc-style/references/procedures.md` 来写。
- 代码块、命令和占位符按照 `../tech-doc-style/references/code-and-commands.md` 来写。
- 结尾给出"后续步骤 / What's next"，链接到下一篇最相关的文档。

### 5. 验证

- [ ] 每个可以复制的命令都能直接运行，除了占位符以外没有需要读者修改的地方
- [ ] 每个占位符都有解释，而且在全文中写法一致
- [ ] 展示的输出和当前版本的实际输出一致，或者明确标明"类似于"
- [ ] 相对链接指向的文件存在；外部链接使用 https
- [ ] 文中提到的版本号、默认值和限制条件，都能在代码或配置中找到出处

### 6. Lint 与自检

```bash
python3 SKILL_DIR/../tech-doc-style/scripts/lint_style.py NEW_DOC.md
```

处理所有 error 和 warn。然后按对应文档类型的模板末尾的"自检"清单逐项检查。

### 7. 输出

- 写入用户指定的路径。没有指定时，按项目惯例放置：README 放在仓库根目录，其他文档放在 `docs/TYPE/SLUG.md`。
- 回复中要包含：新建或修改了哪些文件、选择的文档类型及理由、未解决的 TODO、lint 中没有修改的条目及原因。
