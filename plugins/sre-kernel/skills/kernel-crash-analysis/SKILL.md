---
name: kernel-crash-analysis
description: >-
  Analyzes Linux kernel crashes on RHEL-family and Ubuntu hosts — Oops, panic, BUG/BUG_ON, WARNING, general protection fault, unexpected reboots, kdump vmcore, pstore records, and machine-check/EDAC hardware errors. Extracts structured oops data with a script, triages (first oops, taint, third-party module, hardware, recent upgrade, fleet pattern), symbolizes on a separate analysis host, and recommends mitigation and escalation. TRIGGER when: the user pastes or points to an oops/panic/call trace, reports 内核崩溃、宕机、意外重启、kernel panic、vmcore、kdump, or kernel-triage routes here. DO NOT TRIGGER when: the system is hung but not crashed (kernel-hang-analysis), the issue is slowness or OOM kills (kernel-perf-analysis), or a userspace process segfaults with no kernel trace.
---

# 内核崩溃分析

> 先读 [`../kernel-triage/SKILL.md`](../kernel-triage/SKILL.md)：执行协议、确认门和报告格式以它为准。

## 流程

```
- [ ] 1. 获取 oops 文本
- [ ] 2. 用 extract_oops.py 提取结构化字段（只提取，不下结论）
- [ ] 3. 分诊：第一个 oops、taint、模块、硬件、近期变更、集群范围
- [ ] 4. 需要源码级定位时，在分析机上符号化
- [ ] 5. 给出处置与升级建议，并沉淀文档
```

### 1. 获取 oops 文本

按顺序尝试，拿到即止：

1. 当前启动：`dmesg -T`，或 `journalctl -k -b`
2. 上一次启动：`journalctl -k -b -1`（需要 journal 持久化）；或 `/var/log/messages`（RHEL）、`/var/log/kern.log`（Ubuntu）
3. kdump：先看 `vmcore-dmesg.txt` / `dmesg.*`，体积小，最快
4. pstore：`/sys/fs/pstore`、`/var/lib/systemd/pstore`
5. 以上都没有：参考 [references/capture-when-broken.md](references/capture-when-broken.md)，包括 BMC SEL、串口、netconsole，以及为下次故障做准备

把原文保存到本机后再处理，不要只看截取的片段。

### 2. 提取字段

```bash
python3 scripts/extract_oops.py oops.txt          # 输出 JSON，一个文件里可以有多个 oops
python3 scripts/extract_oops.py --summary oops.txt
```

脚本会去掉 dmesg 时间戳和 syslog 前缀，输出字段包括：类型、标题行、CPU/PID/Comm、内核版本、taint、硬件型号、RIP（`func+off/size [module]`）、CR2、Code、调用栈（标出 `?` 不可靠帧）和已加载模块。

各字段的含义和常见标题行的判断方法见 [references/oops-anatomy.md](references/oops-anatomy.md)。

### 3. 分诊（按顺序回答）

1. **以第一个 oops 为准**：`[#1]` 才是起点，`[#2]` 之后往往是连锁反应。
2. **taint**：
   - O/E/P：第三方模块优先怀疑，看 RIP 和调用栈里是否出现该模块；
   - M：硬件问题，先查 MCE 和 EDAC；
   - B：内存损坏；
   - 用 `../kernel-triage/scripts/decode_taint.py` 解码。
3. **地址特征**：小地址说明是 NULL 指针加字段偏移；毒化值或非规范地址通常意味着 use-after-free 或链表损坏。见 oops-anatomy.md。
4. **近期变更**：内核或驱动升级、新加载的模块、固件更新是否发生在首次崩溃之前（看 baseline 的 `kernel_packages` 部分）。
5. **范围**：
   - 同一内核版本、多台机器、调用栈相同 → 内核或驱动 bug；
   - 只有一台机器、每次调用栈都不一样 → 硬件，尤其是内存。
6. **已知问题**：用函数名加现象检索发行版知识库（Red Hat KB、Ubuntu Launchpad）和 lore.kernel.org；检查新版内核的 changelog：
   - RHEL：`rpm -q --changelog kernel | grep -i <func>`
   - Ubuntu：changelog 位于 `/usr/share/doc/linux-image-*/changelog.Debian.gz`

### 4. 符号化（在分析机上做）

只有在需要定位到源码行时才做。`debuginfo` 必须与 oops 中的内核版本**完全一致**，否则行号是错的。

具体方法见 [references/symbolization.md](references/symbolization.md)：RHEL 和 Ubuntu 的 debuginfo 获取方式、gdb、`decode_stacktrace.sh`、`faddr2line`、`decodecode`。

有 vmcore 时，参考 [references/kdump-vmcore.md](references/kdump-vmcore.md)。从生产机拷出 vmcore 属于确认门操作。

### 5. 处置与升级

| 判断 | 常见处置 | 是否需要确认 |
|---|---|---|
| 第三方模块导致 | 联系模块供应商；临时禁用或回退该模块 | 是 |
| 新内核引入的回归 | 回退到上一个内核（`grubby --set-default`，或 Ubuntu 的 GRUB_DEFAULT） | 是，需要重启 |
| 已知问题且已有修复 | 按 `sre-docs:sre-change-rollout-plan` 推进升级 | 是 |
| 硬件 | 下线该机器，报修；附上 MCE/EDAC 证据 | 是 |
| 原因未知、可复现 | 向发行版厂商提交工单，附 vmcore 和 sosreport / apport；能在上游内核复现时，再用 `scripts/get_maintainer.pl` 找维护者 | — |

未开启 kdump 时，把"开启 kdump"列为行动项（需要预留内存并重启），以便下次能留下证据。

## 参考

- [Linux 内核 bug-hunting 指南（中文）](https://docs.kernel.org/translations/zh_CN/admin-guide/bug-hunting.html)
- [Tainted kernels](https://docs.kernel.org/admin-guide/tainted-kernels.html)
- [intel/linux-kernel-oops](https://github.com/intel/linux-kernel-oops)：借鉴了它把"提取"（primitive）和"推理"（flow）分开的做法
