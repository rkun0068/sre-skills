# USE 方法 Linux 检查表

对每种资源依次检查：使用率（U）、饱和度（S）、错误（E）。表中"档位"指工具开销档位，见 tooling.md。

## 物理资源

| 资源 | 使用率 U | 饱和度 S | 错误 E |
|---|---|---|---|
| CPU | `vmstat` 中的 us+sy+st，以及 `mpstat -P ALL` 看每个核的情况；每个进程的占用看 `pidstat` | `vmstat` 的 r 列持续超过 nproc；PSI `cpu some`；调度延迟用 `runqlat`（档位 2）或 `perf sched`（档位 2） | `perf stat` 的硬件事件（档位 1）；日志中的 MCE 和过热降频 |
| 内存容量 | `free` 的 available 与总量比较；每个进程的 RSS 看 `pidstat -r` | `/proc/vmstat` 中的 pgscan 和 allocstall 增量；si/so；PSI `memory some/full`；日志中的 OOM killer | EDAC 的 ce/ue 计数；内存分配失败（`page allocation failure`） |
| 网络接口 | `sar -n DEV`、`ip -s link` 的吞吐量与链路速率比较 | 丢包和 overrun（`ip -s -s link`、`ethtool -S`）；`softnet_stat` 中的 dropped 和 time_squeeze；TCP 重传 | rx/tx errors；网卡驱动计数（`ethtool -S` 中的 `*_err*`、`rx_missed`、`rx_no_buffer`） |
| 存储设备 IO | `iostat -x` 的 `%util`（SSD 上仅供参考）、IOPS、吞吐 | `aqu-sz` 大于 1、await 升高；PSI `io some/full`；`/sys/block/*/inflight` | 日志中的 `I/O error`、SCSI 超时；`smartctl -H`、`nvme smart-log`（只读，需要 root） |
| 存储容量 | `df -h`、`df -i`、swap 使用量 | 不适用。磁盘满了不会排队，直接返回 ENOSPC | 应用日志中的 ENOSPC；文件系统错误（`EXT4-fs error`、`XFS ... corruption`） |
| 存储控制器 | 各设备吞吐之和与控制器上限比较 | 同存储设备 | 控制器重置、`megaraid`、`mpt3sas` 等驱动日志 |
| CPU 和内存互连 | 用 `perf stat` 看 IPC：IPC 小于 1 且 cache-miss 高，说明受内存带宽或延迟限制（档位 1） | 停顿周期（档位 1） | 依赖具体 CPU 支持的事件 |

## 软件资源

| 资源 | 使用率 U | 饱和度 S | 错误 E |
|---|---|---|---|
| 文件描述符 | `/proc/sys/fs/file-nr` 与 file-max 比较；每个进程用 `ls /proc/<pid>/fd \| wc -l` 和 `ulimit -n` 比较 | 不适用 | 应用日志或 strace 中的 EMFILE、ENFILE（**strace 开销极高，不要在生产机上用**） |
| 任务和线程 | 线程总数与 `kernel.threads-max`、`pid_max` 比较；cgroup 的 `pids.current` 与 `pids.max` 比较 | 不适用 | fork 或 `pthread_create` 失败（EAGAIN） |
| conntrack | `nf_conntrack_count` 与 max 比较 | 接近上限 | 日志中的 `nf_conntrack: table full, dropping packet` |
| 临时端口 | `ss -tan state time-wait` 的数量，与 `ip_local_port_range` 的大小比较 | 客户端建连开始变慢 | `EADDRNOTAVAIL` / `Cannot assign requested address` |
| 内核锁 | 需要 `CONFIG_LOCK_STAT`，生产环境一般没有 | profile 中出现大量 spinlock 自旋（档位 2） | 日志中的 lockup，见 kernel-hang-analysis |

改编自 Brendan Gregg 的 [USE Method: Linux Performance Checklist](https://www.brendangregg.com/USEmethod/use-linux.html)。
