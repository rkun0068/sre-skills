# 工具分档、包名与开销

## 检查哪些工具可用（只读）

```bash
for c in mpstat pidstat iostat sar perf bpftrace trace-cmd ethtool tcpdump numastat turbostat; do
  printf '%-10s %s\n' "$c" "$(command -v $c || echo MISSING)"; done
ls /usr/share/bcc/tools 2>/dev/null | head    # RHEL：bcc 工具所在目录
ls /usr/sbin/*-bpfcc 2>/dev/null | head        # Ubuntu：bcc 工具以 -bpfcc 结尾
```

## 包名对照

安装软件包会写入生产机磁盘，属于确认门操作。

| 用途 | RHEL 系 | Ubuntu |
|---|---|---|
| 基础工具 | `procps-ng`、`util-linux` | `procps`、`util-linux` |
| sysstat（mpstat、iostat、sar、pidstat） | `sysstat` | `sysstat` |
| 网络 | `iproute`、`ethtool`、`tcpdump` | `iproute2`、`ethtool`、`tcpdump` |
| perf | `perf` | `linux-tools-common`、`linux-tools-$(uname -r)` |
| bcc 工具 | `bcc-tools`，命令位于 `/usr/share/bcc/tools/<name>` | `bpfcc-tools`，命令名为 `<name>-bpfcc`，例如 `runqlat-bpfcc` |
| bpftrace | `bpftrace` | `bpftrace` |
| ftrace 前端 | `trace-cmd` | `trace-cmd` |
| NUMA | `numactl` | `numactl` |
| 火焰图脚本 | 在分析机上 clone `brendangregg/FlameGraph` 仓库 | 同左 |

建议事先在基础镜像中预装这些"排障必备工具"（即 Gregg 所说的 crisis tools）。等到出故障时再去安装，往往会因为网络不通或软件源不可用而装不上。

## 开销说明

| 工具 | 开销 | 规则 |
|---|---|---|
| `/proc`、`/sys`、sysstat、`ss`、`nstat` | 可以忽略 | 档位 0，直接执行 |
| `perf stat`、`perf top` | 低 | 档位 1，执行前说明开销，运行不超过 10 秒 |
| `perf record -F 99` | 低到中，会写入 perf.data 文件 | 档位 2，限定 30 秒内，输出写到 `/tmp` |
| bcc / bpftrace 中统计类工具（runqlat、biolatency 等） | 低到中，取决于事件频率 | 档位 2，必须设置时长参数 |
| bcc / bpftrace 中逐事件输出类工具（execsnoop、biosnoop 等） | 事件频率高时，开销也高 | 档位 2，运行不超过 10 秒，必要时加过滤条件 |
| 对高频内核函数设置 kprobe 或 bpftrace 探针 | 可能很高 | 档位 2，先估算事件频率 |
| `strace` | **很高**（基于 ptrace，会让目标进程明显变慢） | 不要在生产机上使用；可以用 `perf trace` 或 bpf 工具代替 |
| `tcpdump` | 繁忙网卡上开销高 | 档位 2，只截取包头，限定包数 |

所有档位 2 的命令都要放在 `timeout` 下运行，或者带上 `-- sleep N` 来限定时长。产生的文件在用完后从生产机上删除。
