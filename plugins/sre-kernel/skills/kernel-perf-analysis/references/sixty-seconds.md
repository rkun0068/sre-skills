# 60 秒速查：每条命令看什么

| 命令 | 重点关注 | 常见误判 |
|---|---|---|
| `uptime` | 1、5、15 分钟 load 的趋势（在上升还是在回落），以及和 nproc 的比值 | load 包含 D 状态任务，不能直接等同于 CPU 忙 |
| `dmesg \| tail` | OOM killer、TCP 丢包（`nf_conntrack: table full`、`possible SYN flooding`）、IO 错误 | 一定要看时间戳，旧日志可能和当前问题无关 |
| `vmstat 1` | r 超过 nproc 说明 CPU 饱和；b 大于 0 说明有任务在等 IO 或锁；si/so 不为 0 说明在用 swap；还有 us、sy、id、wa、st | wa 只表示 CPU 空闲时恰好有 IO 在等待，不能单独作为 IO 瓶颈的证据；虚拟机上 st 持续大于 5% 说明宿主机资源被争抢 |
| `mpstat -P ALL 1` | CPU 之间是否均衡：只有一个核满载说明是单线程瓶颈，或中断集中在一个核上；`%irq`、`%soft` 偏高说明网络中断压力大 | 只看平均值会漏掉单核瓶颈 |
| `pidstat 1` | 哪个进程占用 CPU，以及 `%usr` 和 `%system` 的比例 | `%CPU` 超过 100% 是多线程，属于正常现象 |
| `iostat -xz 1` | `r_await`/`w_await`（毫秒）、`aqu-sz`（大于 1 说明在排队）、r/s、w/s、rkB/s、wkB/s | `%util` 对 SSD、NVMe 和 RAID 有误导性，因为这些设备能并行处理请求，100% 不代表已经饱和；新版 sysstat 已移除 `svctm` |
| `free -m` | 看 **available**，而不是 free；还有 buff/cache 和 swap 的使用量 | free 很小是正常的，Linux 会把空闲内存用作 page cache |
| `sar -n DEV 1` | rxkB/s 和 txkB/s 与链路速率（`/sys/class/net/<if>/speed`）的比较 | 注意单位：kB/s 乘以 8 再除以 1000 才是 Mbit/s |
| `sar -n TCP,ETCP 1` | active/s（主动建连）、passive/s（被动建连）、retrans/s（重传） | 重传率可以用 retrans/s 除以 oseg/s 估算；超过 1% 就值得关注 |
| `top` | 整体复核，看是否有前面漏掉的进程 | top 本身也会消耗一些 CPU |

## 判断出口

- CPU 饱和（r 持续大于 nproc，id 接近 0）→ cpu-sched.md
- 内存不足（available 低、si/so 不为 0、scan 很高、出现 OOM）→ memory.md
- IO 饱和（await 高、aqu-sz 大于 1、b 大于 0）→ disk-io.md
- 网络问题（重传、丢包、带宽打满）→ network.md
- 什么都正常，但业务仍然慢 → 问题可能在应用内部或下游依赖。如实报告"主机层面未见瓶颈"，不要硬凑结论。
