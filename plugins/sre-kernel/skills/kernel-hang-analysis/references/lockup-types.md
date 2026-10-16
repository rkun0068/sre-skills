# Lockup / Stall 类型详解

## 阈值与相关 sysctl

| 类型 | 检测机制 | 默认阈值 | 触发 panic 的开关 |
|---|---|---|---|
| soft lockup | watchdog 线程超时没有运行 | 2 × `kernel.watchdog_thresh`（默认 10 秒），即 20 秒 | `kernel.softlockup_panic` |
| hard lockup | perf NMI 中断检测到计时器中断没有推进 | `watchdog_thresh` | `kernel.hardlockup_panic`；还要求 `kernel.nmi_watchdog=1` |
| hung task | khungtaskd 定期扫描 D 状态任务 | `kernel.hung_task_timeout_secs`（默认 120 秒） | `kernel.hung_task_panic` |
| RCU stall | RCU 宽限期超时 | `rcupdate.rcu_cpu_stall_timeout`（默认 21 秒） | `kernel.panic_on_rcu_stall` |

注意：
- 虚拟机上 NMI watchdog 经常不可用，所以看不到 hard lockup 的告警，**不代表没有发生**。
- 把 hung_task_timeout 调大或设为 0 只会让告警消失，问题本身还在。

## 常见原因

### soft lockup
- 自旋锁竞争或死锁：多个 CPU 的栈都停在 `native_queued_spin_lock_slowpath`。
- 驱动或文件系统中没有调度点的长循环，例如超大目录或超大文件的操作。
- 虚拟机 steal 时间很高：vCPU 长时间没有被调度，等它恢复运行时，看起来就像"卡了 20 秒"。
- 大内存机器执行 `sysrq-t`，或者通过慢速串口输出大量日志。

### hard lockup
- 关中断状态下陷入死循环，或在中断上下文里死锁。
- 硬件或固件问题，例如 SMI 风暴。
- 处理方式：日志中的 NMI backtrace 会给出出事 CPU 的栈。如果开启了 kdump 和 `hardlockup_panic`，会留下 vmcore。

### hung task / D 状态
- IO 路径：
  - 磁盘故障、控制器重置；
  - SAN 或 multipath 路径全部掉线（且设置了 `queue_if_no_path`，IO 会一直挂起）；
  - iSCSI 会话断开。
- NFS 使用 hard mount（默认就是 hard）时，服务器不可达会导致相关进程永久卡住。
- 锁链：A 等 B 持有的 mutex，B 又在等 IO。要一直追到最末端的那个任务。
- 内存回收：直接回收卡在 IO 或 shrinker 上。
- 冻结的 cgroup 或文件系统（`fsfreeze` 之后忘了解冻）。

### RCU stall
- 某个 CPU 长时间关中断或关抢占，常常和 soft lockup 同时出现。
- 虚拟机上 vCPU 被宿主机抢占。
- 日志中有 `rcu_preempt kthread starved` 时，说明 RCU 线程本身得不到 CPU，可能是 RT 任务把 CPU 占满了。

## load 高但 CPU 空闲

Linux 的 load average 包含 R（运行）和 D（不可中断睡眠）两种状态的任务。判断方法：

1. 看 `vmstat` 的 b 列，或 `ps -eLo state | grep -c D`；
2. 如果 D 状态任务很多，同时 `us+sy` 很低，就说明在等 IO 或锁，不是 CPU 不够；
3. 再看 PSI 中的 `io some/full`，进一步确认。
