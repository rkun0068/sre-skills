---
name: kernel-triage
description: >-
  Entry point and execution protocol for kernel-* skills: read-only SSH triage of a Linux host (RHEL or Ubuntu) covering reboots, taint, kernel log signatures, kdump, hardware errors, pressure, then routing. TRIGGER when: the user reports a Linux host problem (宕机、意外重启、机器卡、内核报错). DO NOT TRIGGER when: the issue is in app code, containers, or only a document is wanted.
---

# 内核问题分诊（入口 + 执行协议）

所有 `kernel-*` skill 先读本文件。下面的执行协议是唯一标准，其他 skill 不得重新定义。

## 执行协议

1. **确认目标**：复述主机、问题现象、开始时间（带时区）。主机名或 IP 不清楚时直接询问，不要猜测。
2. **连接方式**：使用用户本机已有的 SSH 配置和 agent。Agent 不输入、不索要密码。
   ```bash
   ssh -o BatchMode=yes -o ConnectTimeout=10 <host> 'bash -s' < SKILL_DIR/scripts/collect_baseline.sh
   ```
   - 只有在用户确认可以免密 sudo 时，才使用 `'sudo -n bash -s'`。不是 root 时，`dmesg`、`/proc/<pid>/stack` 等输出可能受限，报告里要注明"受权限限制未采集"。
   - 脚本放在本机，通过 stdin 传给远端执行，不往生产机上拷贝文件。
3. **默认只读**：所有命令都有超时，开销低，不写生产磁盘。
4. **确认门**：下列操作每次都要先列出"命令 + 影响 + 回滚方式"，得到用户明确同意后才执行：
   - 档位 2 的追踪工具：`perf record`、bcc、bpftrace、ftrace，以及持续超过 30 秒的采集；
   - 往 `/proc/sysrq-trigger` 写入（其中 `c` 会让机器直接崩溃，必须单独确认）；
   - 安装软件包或 debuginfo、修改 sysctl 或配置、加载或卸载模块、`drop_caches`；
   - kill 进程、重启服务或主机、开启或修改 kdump；
   - 从生产机拷出 vmcore 等大文件（占用带宽）。
5. **转入安全事件**：发现入侵迹象（未知内核模块、被篡改的二进制、可疑外连、日志被清空）时，停止常规排障，提醒用户转到 `sre-incident-doc` 的 OpSec 流程：先保全证据，不要清理现场。
6. **分析位置**：vmcore 分析和 debuginfo 安装放在独立分析机上，不在受影响的生产机上做。
7. **路径约定**：`SKILL_DIR` 指当前 SKILL.md 所在的目录。文中的 `scripts/`、`references/` 都相对于 `SKILL_DIR`。Claude Code 和 Codex 执行命令时，当前目录是用户的工作目录，而不是 skill 目录，所以运行脚本时要把 `SKILL_DIR` 换成该目录的绝对路径。引用同一 plugin 中其他 skill 的脚本时，写成 `SKILL_DIR/../<skill>/scripts/...`。

## 分诊流程

复制这份清单并逐项勾选：

```
- [ ] 1. 确认主机、现象、时间窗口
- [ ] 2. 运行 scripts/collect_baseline.sh
- [ ] 3. 用 scripts/decode_taint.py 解码 tainted 值
- [ ] 4. 按下表分类，转到对应 skill
- [ ] 5. 按"报告格式"输出
```

解码 taint（在本机执行）：`python3 SKILL_DIR/scripts/decode_taint.py TAINTED_VALUE`

## 分流

| 采集到的信号 | 转到 |
|---|---|
| `Oops`、`BUG:`、`kernel BUG at`、`general protection fault`、`Kernel panic`；意外重启（`last -x` 中有 crash 记录或缺少 shutdown 记录）；`/var/crash` 下有新文件；pstore 有记录；taint 含 D | `kernel-crash-analysis` |
| `WARNING: CPU:`（taint W） | `kernel-crash-analysis`，但不一定是故障，先判断是否和现象相关 |
| `soft lockup`、`hard LOCKUP`、`blocked for more than`、`rcu.*stall`；大量 D 状态进程；load 高但 CPU 空闲 | `kernel-hang-analysis` |
| 负载高、变慢、`Out of memory` / `oom-kill`、IO 或网络饱和，但没有上面两类信号 | `kernel-perf-analysis` |
| `Machine check`、`EDAC`、`mce:`、taint 含 M；磁盘或 NIC 硬件报错 | `kernel-crash-analysis`（硬件路径，见其中的 references/oops-anatomy.md） |

同时出现多类信号时，按 crash > hang > perf 的优先级处理。后者常常是前者造成的。

## 报告格式

```markdown
## 结论
- 已确认：…（证据编号）
- 未确认：…（原因：权限 / 日志已轮转 / 未开启 kdump）

## 证据
1. `<命令>` → 关键输出（截取最相关的行）

## 建议操作
| 操作 | 是否需要确认 | 影响 | 回滚 |
|---|---|---|---|

## 沉淀
- 需要事件文档 / playbook / 复盘时，链接到 sre-docs 中对应的 skill
```

## 和 sre-docs 的衔接

- SEV0/1 或安全事件 → `sre-incident-doc`
- 可复用的排查步骤 → `sre-playbook`
- 结束后复盘 → `sre-postmortem`
- 需要升级内核或修改参数 → `sre-change-rollout-plan`
