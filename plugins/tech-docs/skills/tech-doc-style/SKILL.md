---
name: tech-doc-style
description: >-
  Shared style rules for tech-docs skills, from the Google developer documentation style guide: tone, voice, headings, lists, procedures, code and placeholders, links, accessibility, inclusive and timeless wording, Chinese typography, plus a Markdown linter. TRIGGER when: writing or reviewing developer or user docs, or 按 Google 风格润色/校对. DO NOT TRIGGER when: writing marketing copy.
---

# 技术文档风格规范

本 skill 是 `tech-doc-writing` 的公共协议。下面的规则是唯一标准，其他 tech-docs skill 不得重新定义。

## 优先级

1. 项目已有的风格指南或术语表
2. 本规范（基于 [Google developer documentation style guide](https://developers.google.com/style)）
3. 第三方参考：拼写看 Merriam-Webster；一般写作风格看 *Chicago Manual of Style*；技术写作风格看 Microsoft Writing Style Guide

规范是指引，不是死规定。偏离可以，但要有理由，并且全文保持一致。

## 核心规则（每篇文档都要满足）

**语气与内容**
1. 像一位懂行的朋友在说话：友好、直接、不卖弄。不用感叹号、玩笑、俚语、流行文化梗或比喻。
2. 不用把任务说得很轻松的词：simply、just、easy、quickly，以及中文的"只需""轻松""简单地"。
3. 不写"please"或"请注意 / please note"，直接说要做什么。
4. 内容要经得起时间：不写 currently、now、new、latest、soon，以及"目前""最新""即将"。确实需要时，写明版本号或日期。release notes 和博客例外。
5. 不预告未来功能。不做无法验证的断言：best、fastest、guarantee、is secure，以及"最好""保证""绝对安全"。
6. 链接文字要说明目标是什么，不写"click here""这里"。

**语言**

7. 用第二人称"you / 你"称呼读者，不用"we / 我们"。中文全文统一用"你"或统一用"您"。
8. 主动语态、现在时，说清楚是谁在做这件事。
9. 条件放在指令之前，目的放在动作之前："To save your work, click **Save**." / "要保存，请点击 **保存**。"
10. 句子要短。英文句子尽量少于 26 个词；用词简单、术语一致，方便翻译和非母语读者阅读。

**格式**

11. 标题用 sentence case（只有首词和专有名词大写），不用 Title Case。
    - 任务类标题以动词原形开头，例如 "Install the CLI"；
    - 概念类标题用名词短语，例如 "Authentication overview"；
    - 标题不以 -ing 开头；
    - 每页只有一个一级标题，不跳级，不在标题里放链接。
12. 有先后顺序的内容用编号列表，其他用项目符号列表。列表前有一句引导语，各项结构平行。
13. 代码、命令、文件名、参数、HTTP 状态码用 `code` 字体；UI 元素用 **粗体**；首次定义的术语用 *斜体*。
14. 占位符写成 `UPPER_SNAKE_CASE`：
    - 不用 `<foo>`、`YOUR_`、`MY_`、`xxx`；
    - 在代码块之后用 "Replace the following:" / "替换以下内容：" 逐个解释。
15. 日期写成不会产生歧义的格式：`2026-10-23` 或 "October 23, 2026"，不写 `10/23/26`。
16. 每张图片都要有 alt text；不用图片代替文字或代码；不用"上面/下面""above/below"指代位置，改用"前面的/以下"或"preceding/following"。
17. 用包容性语言：
    - allowlist / denylist，替代 whitelist / blacklist；
    - primary / replica，替代 master / slave；
    - placeholder，替代 dummy；
    - final check，替代 sanity check。

## 什么时候读哪个 reference

| 正在处理的内容 | 读 |
|---|---|
| 不确定某个词怎么用 | [references/word-list.md](references/word-list.md) |
| 标题、列表、表格、提示框、链接、强调方式 | [references/formatting.md](references/formatting.md) |
| 分步操作（procedure） | [references/procedures.md](references/procedures.md) |
| 代码块、行内代码、占位符、命令行语法 | [references/code-and-commands.md](references/code-and-commands.md) |
| API 参考、代码注释 | [references/api-reference.md](references/api-reference.md) |
| 无障碍与包容性语言 | [references/accessibility-inclusive.md](references/accessibility-inclusive.md) |
| 中文文档 | [references/chinese-docs.md](references/chinese-docs.md) |

## 检查流程

`SKILL_DIR` 指当前 SKILL.md 所在的目录，文中的 `scripts/`、`references/` 都相对于它。Claude Code 和 Codex 执行命令时，当前目录是用户的工作目录，所以运行脚本时要把 `SKILL_DIR` 换成该目录的绝对路径。

```
- [ ] 1. 运行 lint：python3 SKILL_DIR/scripts/lint_style.py FILE.md
- [ ] 2. 逐条处理 error 和 warn；info 级别由你判断是否需要修改
- [ ] 3. 人工检查 lint 覆盖不到的规则：1、5、7–10、12、16（语义类规则）
- [ ] 4. 输出修改结果，或者给出评审意见
```

lint 用法：

```bash
python3 SKILL_DIR/scripts/lint_style.py docs/*.md                    # 自动识别中英文
python3 SKILL_DIR/scripts/lint_style.py --lang zh --format json README.md
python3 SKILL_DIR/scripts/lint_style.py --strict docs/               # 有 error 或 warn 时退出码为 1，可接入 CI
```

lint 只是辅助手段：它会跳过代码块和行内代码，但仍可能误报，例如在描述 `kill` 命令时出现的 "kill"。误报不要硬改，在评审意见中说明即可。

## 评审模式

当用户要求"评审 / 校对 / 检查"一份已有文档时：
- 不直接重写全文；
- 按"阻断（error）→ 建议（warn）→ 可选（info）"的顺序列出问题，每条都附上原文位置、原文、修改建议，以及对应的规则编号；
- 用户同意后再改。

## 参考

- [Google developer documentation style guide](https://developers.google.com/style)：[Highlights](https://developers.google.com/style/highlights)、[Word list](https://developers.google.com/style/word-list)、[Text-formatting summary](https://developers.google.com/style/text-formatting)
