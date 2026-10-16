# 网络

## 只读定位（档位 0）

| 现象 | 查看 | 判断 |
|---|---|---|
| 带宽打满 | `sar -n DEV 1 5` 与 `/sys/class/net/<if>/speed` 比较 | rx 或 tx 接近链路速率；bond 要看每个成员口 |
| 网卡丢包 | `ip -s -s link`、`ethtool -S <if> \| grep -iE 'drop\|miss\|err\|fifo\|no_buf'` | `rx_missed`、`rx_no_buffer`、`fifo` 在增长，说明网卡 ring buffer 不够或 CPU 处理不过来（看 `ethtool -g` 的设置，修改属于变更） |
| 内核收包处理不过来 | `/proc/net/softnet_stat` 中的 dropped 和 time_squeeze；`mpstat` 中的 `%soft`；`/proc/softirqs` 中的 NET_RX | 某个核的 `%soft` 很高 → 中断或 RPS 分布不均（看 `/proc/interrupts`、irqbalance）；time_squeeze 在增长 → `netdev_budget` 不够 |
| TCP 重传 | `nstat -az TcpRetransSegs TcpOutSegs`，计算两者比值；用 `ss -tin` 查看每个连接的 retrans、rtt、cwnd | 重传集中在少数几个对端 → 路径问题；全部都有 → 本机或本地网络问题 |
| 新建连接被丢弃 | `nstat -az TcpExtListenOverflows TcpExtListenDrops`；`ss -ltn` 中 Recv-Q 与 Send-Q 的比较 | accept 队列满：应用 accept 太慢，或 backlog / `net.core.somaxconn` 太小 |
| SYN 相关 | 日志中的 `possible SYN flooding`；`TcpExtTCPReqQFullDrop` | SYN 队列满，看 `tcp_max_syn_backlog` 和 syncookies 设置 |
| conntrack 表满 | 日志中的 `nf_conntrack: table full, dropping packet`；count 与 max 比较 | 调大 `nf_conntrack_max`（变更），或减少不必要的连接跟踪 |
| 临时端口耗尽 | `ss -tan state time-wait \| wc -l`；`EADDRNOTAVAIL` 报错 | 短连接太多。优先改用连接复用，其次再考虑调整 `ip_local_port_range` |
| UDP 丢包 | `nstat -az UdpRcvbufErrors UdpInErrors` | 接收缓冲区不够，或应用读得太慢 |
| DNS 慢 | 用 `dig` 或 `getent hosts` 计时；看 `/etc/resolv.conf` 中的 timeout 和 attempts 设置 | 某个 nameserver 不可达，会让每次解析都多等一个超时时间 |

## 进一步分析（档位 2）

| 目的 | 命令 |
|---|---|
| 重传发生在哪些连接上 | `tcpretrans`（bcc 或 perf-tools 版本均可） |
| 内核在哪里丢的包 | `tcpdrop`；或 `perf record -e skb:kfree_skb -a -g -- sleep 10` |
| 连接的生命周期和耗时 | `tcplife`、`tcpconnect`、`tcpaccept` |
| 抓包 | `tcpdump -i <if> -s 128 -c 10000 -w /tmp/x.pcap host <ip>`：只截取包头，限定包数，并且过滤条件要足够精确 |

注意：
- 在繁忙的网卡上运行 tcpdump，会消耗大量 CPU 和磁盘。
- 抓包文件中可能包含敏感数据，用完立即删除。
