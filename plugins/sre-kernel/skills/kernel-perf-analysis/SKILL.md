---
name: kernel-perf-analysis
description: >-
  Analyzes Linux host performance with the 60-second checklist and USE method, then CPU, memory and OOM, disk IO, and network drill-down, with tools tiered by overhead. TRIGGER when: the user reports 机器慢、负载高、OOM、IO 慢、丢包, or asks for a flame graph. DO NOT TRIGGER when: the host crashed, tasks are stuck in D state, or the slowness is inside one app.
---

# 内核与系统性能分析

> 先读 [`../kernel-triage/SKILL.md`](../kernel-triage/SKILL.md)：执行协议、确认门和报告格式以它为准。

## 流程

```
- [ ] 1. 明确问题：什么慢、从什么时候开始、怎么度量、最近有什么变化
- [ ] 2. 60 秒速查：scripts/sixty_seconds.sh
- [ ] 3. USE 检查：scripts/use_snapshot.sh，逐个资源判断使用率、饱和度、错误
- [ ] 4. 对瓶颈所在的子系统深入分析（按工具档位，档位 2 要确认）
- [ ] 5. 给出结论和处置建议，并说明如何验证效果
```

### 1. 先问清楚

性能问题最常见的错误，是在没有定义"慢"的情况下就开始看各种指标。先确认以下几点：
- 用什么指标衡量：延迟、吞吐，还是错误率；
- 是从什么时候开始的；
- 是所有请求都慢，还是只有一部分；
- 最近有没有发布、扩容或流量变化。

### 2. 60 秒速查

```bash
ssh -o BatchMode=yes <host> 'bash -s' < SKILL_DIR/scripts/sixty_seconds.sh
```

脚本按顺序执行 10 条命令，每条都限定了时长：

```
uptime
dmesg | tail
vmstat 1
mpstat -P ALL 1
pidstat 1
iostat -xz 1
free -m
sar -n DEV 1
sar -n TCP,ETCP 1
top
```

缺少 sysstat 时，脚本会说明哪些命令没有执行。**安装 sysstat 属于确认门操作。**

每条命令的输出重点看什么、有哪些容易误判的地方，见 [references/sixty-seconds.md](references/sixty-seconds.md)。

### 3. USE 检查

```bash
ssh -o BatchMode=yes <host> 'bash -s' < SKILL_DIR/scripts/use_snapshot.sh
```

对每种资源回答三个问题：
- 使用率：忙碌的时间或容量占比；
- 饱和度：排队或等待的程度；
- 错误：错误事件计数。

**先看错误，再看饱和度**，因为它们最容易被忽略，又最能说明问题。

各资源对应的指标和命令见 [references/use-checklist.md](references/use-checklist.md)。

### 4. 深入分析

找到瓶颈所在的资源后，只读取对应的 reference：

| 瓶颈 | 参考 |
|---|---|
| CPU、调度延迟、软中断 | [references/cpu-sched.md](references/cpu-sched.md) |
| 内存、回收、OOM killer | [references/memory.md](references/memory.md) |
| 磁盘 IO、文件系统 | [references/disk-io.md](references/disk-io.md) |
| 网络 | [references/network.md](references/network.md) |

工具开销分档：

| 档位 | 工具 | 规则 |
|---|---|---|
| 0 | `/proc`、`/sys`、sysstat、iproute2、`ss`、`nstat` | 可以直接执行 |
| 1 | `perf stat`、`perf top`（不超过 10 秒） | 执行前说明开销 |
| 2 | `perf record`、bcc、bpftrace、ftrace perf-tools、火焰图、`tcpdump` | **确认门**：必须限定时长，输出写到 `/tmp` 并在用完后删除 |

各档位的工具清单、在 RHEL 和 Ubuntu 上的包名与路径差异，以及开销说明，见 [references/tooling.md](references/tooling.md)。

### 5. 结论

结论要说明**因果关系**：哪个资源饱和 → 导致什么现象 → 有什么证据，而不是简单罗列异常指标。

每条处置建议都要附上验证方法：执行后看哪个指标、预期变成什么样。修改 sysctl 或内核参数属于变更，按 `sre-change-rollout-plan` 推进。

## 参考

- [Brendan Gregg: Linux Performance](https://www.brendangregg.com/linuxperf.html)
- [USE Method: Linux Performance Checklist](https://www.brendangregg.com/USEmethod/use-linux.html)
- [Linux Performance Analysis in 60,000 Milliseconds](https://netflixtechblog.com/linux-performance-analysis-in-60-000-milliseconds-accc10403c55)
