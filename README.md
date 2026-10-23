# SRE Skills

一组遵循 Agent Skills 规范的 skill，**同时支持 Claude Code 和 Codex**。仓库本身是一个 plugin marketplace，每个领域是一个 plugin，可以单独安装：

| Plugin | 用途 | 依据 |
|---|---|---|
| [sre-docs](plugins/sre-docs) | 按统一标准起草、补全和评审 SRE / 安全可靠性文档 | Google《[Building Secure and Reliable Systems](https://google.github.io/building-secure-and-reliable-systems/raw/toc.html)》（BSRS） |
| [sre-kernel](plugins/sre-kernel) | 通过 SSH 对 Linux 主机（RHEL 系、Ubuntu）做只读的内核问题排查 | [内核 bug-hunting 指南](https://docs.kernel.org/translations/zh_CN/admin-guide/bug-hunting.html)、[Brendan Gregg Linux Performance](https://www.brendangregg.com/linuxperf.html)，并借鉴了 [intel/linux-kernel-oops](https://github.com/intel/linux-kernel-oops) 的设计 |
| [tech-docs](plugins/tech-docs) | 按 Google 风格编写和评审开发者文档、用户文档（中英文） | [Google developer documentation style guide](https://developers.google.com/style) |

## 安装

### 方式一：作为独立 skill 安装（Claude Code 和 Codex 通用）

```bash
scripts/install.sh                      # 两个 agent 都装，用软链接
scripts/install.sh --agent codex        # 只装到 Codex（~/.agents/skills）
scripts/install.sh --agent claude --plugin sre-kernel --copy
scripts/install.sh --uninstall          # 只删除由本仓库安装的 skill
```

| Agent | 安装位置 | 调用方式 |
|---|---|---|
| Claude Code | `~/.claude/skills/<skill>` | 自动触发，或 `/<skill>` |
| Codex | `~/.agents/skills/<skill>` | 自动触发，或输入 `$<skill>` / `/skills` |

软链接会跟随仓库当前检出的分支，`git pull` 后即可更新；切换到没有这些文件的分支时，对应的 skill 会失效。需要和仓库解耦时，用 `--copy`。

### 方式二：作为 plugin 安装

Claude Code：

```text
/plugin marketplace add /path/to/sre-skills
/plugin install sre-kernel@sre-skills
```

Codex（marketplace 来源由 CLI 管理，在 ChatGPT 桌面应用中安装和启用）：

```bash
codex plugin marketplace add /path/to/sre-skills
```

Codex 读取 `.agents/plugins/marketplace.json` 和每个 plugin 根目录下的 `plugin.json`；Claude Code 读取 `.claude-plugin/` 下的文件。两套清单指向同一份 skill。

## 双 agent 兼容约定

- `SKILL.md` 的 frontmatter 只用 `name` 和 `description` 两个字段，两边通用。
- `description` 不超过 400 字符，并且先写用途：Codex 给所有 skill 描述的总预算大约只有 8,000 字符。
- 正文不写某个 agent 专有的工具或命名空间。引用其他 skill 时写名称，不写 `plugin:skill`。
- 可执行的脚本路径写成 `SKILL_DIR/scripts/...`，因为两个 agent 都在用户的工作目录里执行命令。
- `agents/openai.yaml` 是 Codex 的展示元数据，Claude Code 会忽略它。
- 仓库级的协作说明写在 `AGENTS.md`，`CLAUDE.md` 通过 `@AGENTS.md` 引用它。

## 设计约定

- **渐进式加载**：
  - frontmatter 的 `description` 写清"做什么 + 何时触发 / 何时不触发"；
  - `SKILL.md` 正文只放流程、决策和门禁，不超过 500 行；
  - 细节放在 `references/`，只从 SKILL.md 引用一层；
  - 确定性的工作放在 `scripts/`，直接执行，不读入上下文；
  - 模板放在 `assets/`。
- **每个 plugin 有一个公共协议 skill**，同一 plugin 内的其他 skill 都要先读它，不得重新定义其中的约定：
  - sre-docs：`sre-doc-standards`（元数据头、严重度和优先级、风险打分、行动项、写作规范）；
  - sre-kernel：`kernel-triage`（SSH 执行规则、默认只读、确认门、报告格式）；
  - tech-docs：`tech-doc-style`（风格规则、lint、评审模式）。
- **评估先行**：每个 skill 至少有 3 个评估场景，放在 `plugins/<plugin>/evals/`。

## sre-docs：文档 skill

| 生命周期 | Skill | 产出文档 | BSRS 出处 |
|---|---|---|---|
| 通用 | [sre-doc-standards](plugins/sre-docs/skills/sre-doc-standards/SKILL.md) | 共享约定（不是独立文档） | 全书 |
| 设计 | [sre-threat-model](plugins/sre-docs/skills/sre-threat-model/SKILL.md) | 威胁建模 / 对手分析 | Ch2, Ch5, Ch14 |
| 设计 | [sre-design-review](plugins/sre-docs/skills/sre-design-review/SKILL.md) | 安全与可靠性设计文档 | Ch4, Ch6, Ch8, Ch9, Ch10, Ch15 |
| 设计 | [sre-access-control-review](plugins/sre-docs/skills/sre-access-control-review/SKILL.md) | 最小权限 / 访问控制设计 | Ch3, Ch5 |
| 实施 | [sre-change-rollout-plan](plugins/sre-docs/skills/sre-change-rollout-plan/SKILL.md) | 安全变更与发布计划 | Ch7, Ch14 |
| 实施 | [sre-security-test-plan](plugins/sre-docs/skills/sre-security-test-plan/SKILL.md) | 安全与可靠性测试计划 | Ch12, Ch13 |
| 维护-准备 | [sre-disaster-risk-assessment](plugins/sre-docs/skills/sre-disaster-risk-assessment/SKILL.md) | 灾难风险评估矩阵 | Ch16, 附录 A |
| 维护-准备 | [sre-incident-response-plan](plugins/sre-docs/skills/sre-incident-response-plan/SKILL.md) | 事件响应团队章程与响应计划 | Ch16 |
| 维护-准备 | [sre-playbook](plugins/sre-docs/skills/sre-playbook/SKILL.md) | 操作手册（Playbook / Runbook） | Ch9, Ch16 |
| 维护-准备 | [sre-dr-exercise](plugins/sre-docs/skills/sre-dr-exercise/SKILL.md) | 演练计划与演练报告 | Ch16 |
| 维护-响应 | [sre-incident-doc](plugins/sre-docs/skills/sre-incident-doc/SKILL.md) | 事件指挥工作文档（含会议、交接、通报） | Ch17 |
| 维护-恢复 | [sre-recovery-plan](plugins/sre-docs/skills/sre-recovery-plan/SKILL.md) | 恢复计划与恢复清单 | Ch18 |
| 维护-复盘 | [sre-postmortem](plugins/sre-docs/skills/sre-postmortem/SKILL.md) | 无责事后复盘 | Ch16, Ch18 |

文档之间的关系：

```
威胁建模 ──► 设计文档 ◄── 访问控制设计
                │
                ▼
     测试计划 / 变更发布计划
                │
灾难风险评估 ──► 事件响应计划 ──► Playbook ──► 演练（验证计划与手册）
                                   │
                         ┌─────────┘
                         ▼
                    事件指挥文档 ──► 恢复计划 ──► 事后复盘
                                                   │
                     行动项回流到：威胁模型 / 设计 / 风险评估 / Playbook
```

## sre-kernel：内核排查 skill

| Skill | 覆盖内容 | 脚本（只读） |
|---|---|---|
| [kernel-triage](plugins/sre-kernel/skills/kernel-triage/SKILL.md) | 入口和执行协议：基线采集、taint 解码、分流 | `collect_baseline.sh`、`decode_taint.py` |
| [kernel-crash-analysis](plugins/sre-kernel/skills/kernel-crash-analysis/SKILL.md) | oops、panic、BUG、WARNING、意外重启、kdump/vmcore、硬件错误 | `extract_oops.py` |
| [kernel-hang-analysis](plugins/sre-kernel/skills/kernel-hang-analysis/SKILL.md) | soft/hard lockup、hung task、RCU stall、D 状态堆积 | `hang_snapshot.sh` |
| [kernel-perf-analysis](plugins/sre-kernel/skills/kernel-perf-analysis/SKILL.md) | 60 秒速查、USE 方法、CPU、内存/OOM、IO、网络 | `sixty_seconds.sh`、`use_snapshot.sh` |

执行模型：

```
用户报告主机问题
      │
      ▼
kernel-triage：确认目标 → ssh -o BatchMode=yes <host> 'bash -s' < collect_baseline.sh → 分流
      │
      ├─► kernel-crash-analysis：extract_oops.py → 分诊 → 在分析机上符号化或分析 vmcore
      ├─► kernel-hang-analysis：hang_snapshot.sh → 按等待点归因 →（确认后）sysrq-w
      └─► kernel-perf-analysis：sixty_seconds.sh → use_snapshot.sh → 按子系统深入（档位 2 需确认）
      │
      ▼
沉淀到 sre-docs：事件文档 / Playbook / 复盘 / 变更计划
```

安全边界：
- 默认只读，所有命令都带超时；
- 不在生产机上落地任何文件；
- Claude 不输入密码；
- 写操作和高开销操作必须逐项确认；
- vmcore 和 debuginfo 只在独立分析机上处理。

## tech-docs：技术文档 skill

| Skill | 用途 | 内容 |
|---|---|---|
| [tech-doc-style](plugins/tech-docs/skills/tech-doc-style/SKILL.md) | 风格规则和评审：语气、语法、标题、列表、步骤、代码与占位符、链接、无障碍、包容性语言、不过时的措辞，以及中文排版适配 | `lint_style.py`；references 包括词汇表、格式、步骤、代码与命令、API 参考、无障碍、中文文档 |
| [tech-doc-writing](plugins/tech-docs/skills/tech-doc-writing/SKILL.md) | 根据读者的需求选择文档类型，从代码中收集事实后起草，验证命令，最后运行 lint | 8 个模板：README、quickstart、how-to、tutorial、concept、reference、troubleshooting、release notes |

lint 可以单独使用，也可以接入 CI：

```bash
python3 plugins/tech-docs/skills/tech-doc-style/scripts/lint_style.py --strict docs/
```

它会自动识别中英文，跳过代码块、行内代码和 URL，并在代码块中检查占位符的写法。语义层面的规则（例如语气、条件放在指令之前）仍需人工检查。

## 校验

```bash
python3 scripts/validate_skills.py
```

检查内容包括：
- 两套 marketplace 和 plugin 清单（Claude Code、Codex）是否一致，版本是否相同；
- 双 agent 兼容：描述长度和总预算、`agents/openai.yaml`、正文中没有 agent 专有的写法、脚本路径使用 `SKILL_DIR`；
- frontmatter（名称、长度、触发说明）和 SKILL.md 的行数；
- 相对链接与脚本路径是否有效；
- 文档模板与公共约定的引用；
- 脚本语法与可执行权限；
- evals 的数量和引用的样例文件；
- 用 `extract_oops.py` 对样例日志做回归测试；
- 用 `lint_style.py` 对样例文档做回归测试：bad 样例必须报出指定的规则，good 样例不能有任何发现。

## 版权说明

- sre-docs 是对 BSRS（CC BY-NC-ND 4.0）方法论的**中文转述与工程化整理**，不复制原文。
- sre-kernel 引用的方法论来自上面列出的公开资料，各 skill 的"参考"一节附有原文链接。
- tech-docs 是对 Google developer documentation style guide（CC BY 4.0）的中文转述与精简，不复制原文；词汇表和示例均为改写。
- 样例日志全部为自行编写。
