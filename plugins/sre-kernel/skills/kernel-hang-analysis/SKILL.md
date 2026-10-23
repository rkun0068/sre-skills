---
name: kernel-hang-analysis
description: >-
  Diagnoses Linux kernel hangs: soft and hard lockups, hung tasks, RCU stalls, D-state pile-ups. Snapshots blocked tasks read-only and maps wait points to IO, NFS, locks, reclaim, or VM steal. TRIGGER when: logs show lockups or 'blocked for more than', or 机器卡死/load 高但 CPU 空闲. DO NOT TRIGGER when: the host crashed or is just CPU-bound.
---

# 内核卡死 / 停顿分析

> 先读 [`../kernel-triage/SKILL.md`](../kernel-triage/SKILL.md)：执行协议、确认门和报告格式以它为准。

## 流程

```
- [ ] 1. 判断停顿类型（见下表）
- [ ] 2. 运行 scripts/hang_snapshot.sh（只读）
- [ ] 3. 根据等待点归类原因
- [ ] 4. 只读证据不够时，申请执行 sysrq（确认门）
- [ ] 5. 给出处置建议
```

### 1. 判断类型

| 类型 | 日志特征 | 含义 |
|---|---|---|
| soft lockup | `watchdog: BUG: soft lockup - CPU#N stuck for 22s!` | 某个 CPU 在内核态连续运行，超过 2×`watchdog_thresh` 都没有调度 |
| hard lockup | `NMI watchdog: Watchdog detected hard LOCKUP on cpu N` | 某个 CPU 关中断的时间超过 `watchdog_thresh` |
| hung task | `INFO: task X:PID blocked for more than 120 seconds.` | 任务处于 D 状态的时间超过 `hung_task_timeout_secs` |
| RCU stall | `rcu: INFO: rcu_sched detected stalls on CPUs/tasks` | RCU 宽限期迟迟无法结束，通常是某个 CPU 长时间不让出 |
| D 状态堆积 | 没有上述日志，但 `ps` 中有大量 `D` 状态进程，load 很高而 CPU 空闲 | Linux 的 load 包含 D 状态任务，所以 **load 高不代表 CPU 忙** |

阈值、常见原因和各类型的区别见 [references/lockup-types.md](references/lockup-types.md)。

### 2. 采集快照

```bash
ssh -o BatchMode=yes <host> 'bash -s' < SKILL_DIR/scripts/hang_snapshot.sh
```

采集内容包括：
- D 状态的线程，及其 wchan 和 `/proc/<pid>/stack`（需要 root）；
- 内核日志中与 lockup、hung、stall 相关的记录；
- watchdog 相关的 sysctl；
- PSI、`vmstat` 中的 b 列和 st 列；
- NFS 挂载情况；
- 卡住的 IO 请求（`inflight`）。

机器已经卡到 SSH 都很慢时：
- 用 `T=5` 缩短每条命令的超时；
- 如果 `ps` 本身也卡住（读 `/proc/<pid>/cmdline` 可能会被锁住），只看日志部分的输出。

### 3. 根据等待点归类

拿到内核栈或 wchan 后，看最靠上的几个有意义的函数：

| 栈中出现的函数 | 指向的原因 | 下一步验证 |
|---|---|---|
| `rpc_wait_bit_killable`、`nfs_*`、`__rpc_execute` | NFS 服务器不可达或响应慢 | `mount -t nfs,nfs4`、`nfsstat -c`、服务器是否可达 |
| `io_schedule`、`blk_mq_get_tag`、`wait_on_page_bit`、`folio_wait_bit` | 块设备 IO 卡住 | `iostat -x` 中 await 是否很高，`inflight` 是否不降，日志中是否有 `I/O error` 或 `timeout`，multipath 路径是否掉线 |
| `jbd2_*`、`ext4_*`、`xfs_log_*`、`xlog_*` | 文件系统日志卡住，通常是下层 IO 出了问题 | 同上，并找出 jbd2 / xfsaild 线程的状态 |
| `mutex_lock`、`rwsem_down_*`、`down_write` | 在等锁 | 找到持锁者（往往是另一个 D 状态任务），一直追到链条末端 |
| `shrink_*`、`try_to_free_pages`、`__alloc_pages_slowpath` | 内存回收导致的停顿 | 转 kernel-perf-analysis 的内存部分 |
| soft lockup 时 RIP 落在 spinlock 或驱动的循环里 | 锁竞争、驱动 bug | 结合 RIP 和调用栈，按 kernel-crash-analysis 的方法处理 |
| 虚拟机上 st（steal）很高，同时出现 soft lockup 或 RCU stall | 宿主机超卖，vCPU 没有被调度 | 查看宿主机或云平台的指标。这种情况**不是来宾系统内核的 bug** |

### 4. 申请执行 sysrq（确认门）

只读快照拿不到内核栈时（不是 root，或者 `/proc/<pid>/stack` 不可用），可以申请执行 `sysrq-w`，把所有阻塞任务的栈打印到内核日志里。

**风险、使用条件，以及绝对禁止使用的键**，见 [references/sysrq.md](references/sysrq.md)。

### 5. 处置建议

| 原因 | 处置 | 是否需要确认 |
|---|---|---|
| NFS 服务器不可达 | 恢复服务器或网络。挂载点卡住时可以用 `umount -f -l`，但应用可能会出错 | 是 |
| 磁盘或路径故障 | 切换路径、更换磁盘，并迁走业务 | 是 |
| 宿主机 steal 高 | 迁移虚拟机，或联系云厂商 | 是 |
| 内核或驱动 bug | 先保留现场：可以用 `sysrq-c` 触发 kdump（单独确认）；然后按 kernel-crash-analysis 处理 | 是 |
| 无法恢复 | 重启前先申请触发 kdump 保留证据，再重启 | 是 |

处于 D 状态的进程**无法被 kill -9 杀掉**。不要建议"kill 掉就好"。
