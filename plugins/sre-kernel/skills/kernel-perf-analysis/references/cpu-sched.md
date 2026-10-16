# CPU 与调度

## 先用只读手段定位（档位 0）

- `mpstat -P ALL 1 5`：
  - 只有一个核满载 → 单线程瓶颈，或中断亲和性集中在一个核上；
  - `%soft` 高 → 网络软中断压力，看 network.md；
  - `%steal` 高 → 宿主机资源被争抢。
- `pidstat -u 1 5` 找出占用 CPU 的进程，`pidstat -t -p <pid> 1 5` 再看到线程级别。
- `pidstat -w 1 5`：上下文切换。`nvcswch/s`（非自愿切换）高说明线程在争抢 CPU。
- `cat /proc/<pid>/sched`：调度统计，包括 `nr_involuntary_switches` 和等待时间。
- `cat /proc/pressure/cpu`：`some avg10` 是最近 10 秒内有任务在等 CPU 的时间占比。
- cgroup 限流：`cat /sys/fs/cgroup/<path>/cpu.stat`。`nr_throttled` 或 `throttled_usec` 在增长，说明是 CPU quota 限制，不是机器整体 CPU 不够。容器或 systemd 服务上经常遇到这种情况。
- 降频：
  - 日志中有 `temperature above threshold` 或 `clock throttled`；
  - `turbostat`（需要 root）中的 Bzy_MHz 明显低于标称频率。

## 进一步分析（档位 1 和 2）

| 目的 | 命令 | 档位 |
|---|---|---|
| 查看热点函数 | `perf top -g --sort comm,dso,sym`（运行不超过 10 秒） | 1 |
| 统计 IPC 和 cache-miss | `perf stat -a -- sleep 10` | 1 |
| CPU 火焰图 | `perf record -F 99 -a -g -o /tmp/perf.data -- sleep 30`，然后 `perf script -i /tmp/perf.data \| stackcollapse-perf.pl \| flamegraph.pl > cpu.svg` | 2 |
| 调度延迟分布 | `runqlat 10 1` | 2 |
| 每个 CPU 的运行队列长度 | `runqlen 10 1` | 2 |
| off-CPU 分析（线程为什么没在运行） | `offcputime -df -p <pid> 30`，结果可以画成 off-CPU 火焰图 | 2 |
| 短命进程（CPU 高但 top 里看不到是谁） | `execsnoop` | 2 |

注意：
- **调用栈不完整**：
  - Ubuntu 24.04 及以后的版本默认开启 frame pointer，栈通常完整；
  - RHEL 和较旧的 Ubuntu 上，用户态栈可能断开，可以用 `--call-graph dwarf`，但数据量大、开销高，要缩短采样时间。
- **符号缺失**：火焰图中显示为十六进制地址，需要安装应用的调试符号。Java、Node 等需要开启 perf map 支持。
- `perf.data` 写在 `/tmp`，分析完后删除。从生产机拷出火焰图（svg 文件很小）即可。
