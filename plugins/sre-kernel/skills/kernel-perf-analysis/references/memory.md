# 内存、回收与 OOM killer

## 判断内存是否紧张

- **看 `MemAvailable`，不看 `MemFree`**。free 很小是正常的，因为空闲内存会被用作 page cache。
- 回收压力：`/proc/vmstat` 中以下计数持续增长：
  - `pgscan_direct`、`allocstall_*`：进程自己在回收内存，会**直接增加请求延迟**；
  - `pgscan_kswapd`：后台回收，相对温和。
- `sar -B 1 5` 中 `%vmeff`（回收效率）偏低，说明扫描了大量页面，但回收到的很少。
- PSI `memory full avg10` 大于 0：在这段时间里所有任务都在等内存，影响严重。
- swap：`vmstat` 中 si/so 持续不为 0，比"swap 用了多少"更能说明问题。

## 读懂 OOM killer 日志

可以先用 `python3 SKILL_DIR/../kernel-crash-analysis/scripts/extract_oops.py --summary LOG_FILE` 提取关键字段：constraint、所在 memcg、被杀进程及其各类 RSS、gfp_mask 和 order。

```
<comm> invoked oom-killer: gfp_mask=0x..., order=0, oom_score_adj=0
...
Mem-Info: / Node 0 Normal free:... min:... low:... high:...
...
[ pid ]   uid  tgid total_vm      rss ... oom_score_adj name
...
oom-kill:constraint=CONSTRAINT_NONE,...,task=java,pid=1234,uid=1000
Out of memory: Killed process 1234 (java) total-vm:..kB, anon-rss:..kB, file-rss:..kB, shmem-rss:..kB
```

| 看什么 | 判断 |
|---|---|
| `invoked oom-killer` 前面的进程名 | 触发 OOM 的进程。它不一定是被杀掉的那个 |
| `constraint=CONSTRAINT_MEMCG`，或出现 `Memory cgroup out of memory` | 进程所在 cgroup 的内存超过了限制，**整机内存并不缺**。应该调整该服务的 MemoryMax / memory.max，或者排查它的内存使用 |
| `order=` 大于 0，且日志中还有不少空闲内存 | 内存碎片化，申请不到连续的大块内存。看 `/proc/buddyinfo` 中高阶的空闲块，以及 `compact_stall` 计数 |
| `anon-rss` 很大 | 应用的堆内存。排查应用内存泄漏，或检查配置是否合理（例如 JVM 的 -Xmx 是否设得比容器限制还大） |
| `shmem-rss` 很大，或 Mem-Info 中 shmem 很大 | tmpfs 或 /dev/shm 被写满（`df -h /dev/shm /run`） |
| 进程表中各进程的 RSS 加起来远小于总内存 | 内存被内核占用了：看 slab（`SUnreclaim` 很大说明内核内存泄漏，用 `slabtop -o` 找出是哪个 slab）、hugepages 预留、驱动占用 |
| 被杀的是关键进程 | 检查它的 `oom_score_adj`；考虑保护关键进程，同时**限制真正占内存的进程** |

## 其他

- NUMA：`numastat -m` 看各节点内存是否不均衡。`vm.zone_reclaim_mode=1` 时，即使其他节点还有空闲内存，也会在本节点回收，导致延迟抖动。
- 透明大页：`/sys/kernel/mm/transparent_hugepage/enabled` 设为 always 时，可能出现 `compact_stall` 带来的延迟尖刺。数据库通常建议设为 madvise 或 never（修改属于变更）。
- overcommit：`vm.overcommit_memory` 和 `overcommit_ratio` 决定了申请内存什么时候会直接失败，而不是等到 OOM 时才处理。
- **不要建议 `drop_caches` 作为解决方案**。它只是把 cache 清掉，问题很快就会回来，还会导致 IO 突增。它属于确认门操作，只适合在诊断时用来对比测试。
