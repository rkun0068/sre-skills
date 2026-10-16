# 磁盘 IO 与文件系统

## 只读定位（档位 0）

- `iostat -xz 1 5`：
  - `r_await`、`w_await`：从请求发出到完成的平均时间，包括排队；
  - `aqu-sz`：平均队列长度；
  - r/s、w/s、rkB/s、wkB/s；
  - `rareq-sz`、`wareq-sz`：平均请求大小。请求很小但 IOPS 很高，说明是随机 IO。
- 参考值：NVMe 通常在 1 毫秒以内；SATA SSD 在几毫秒；HDD 随机 IO 大约 5–15 毫秒。云盘还要对比它标称的 IOPS 和吞吐上限，**被限速**时，表现为 await 升高，但设备并不忙。
- `pidstat -d 1 5`、`iotop -oPa`（需要 root）：找出是哪个进程在读写。
- PSI `io some/full`：IO 等待对任务造成的影响有多大。
- 写回：`/proc/meminfo` 中 `Dirty` 和 `Writeback` 很高，同时有写入卡顿时，看 `vm.dirty_ratio`、`dirty_background_ratio`，以及 `dirty_bytes` 系列参数的设置。
- 错误：
  - 内核日志中的 `I/O error`、`blk_update_request`、`Medium Error`、`task abort`、`reset`；
  - `smartctl -H -A /dev/sdX`、`nvme smart-log /dev/nvme0`（只读，需要 root）；
  - `multipath -ll` 中路径的状态。

## 进一步分析（档位 2）

| 目的 | 命令 |
|---|---|
| IO 延迟分布（是否有长尾） | `biolatency -D 10 1`（按设备分别统计） |
| 逐个查看 IO 请求（哪个进程、哪个设备、延迟多少） | `biosnoop` 或 `iosnoop`（perf-tools），运行不超过 10 秒 |
| 文件系统层面的慢操作 | `ext4slower 10`、`xfsslower 10`（只显示超过 10 毫秒的操作） |
| 文件访问模式 | `filetop`、`opensnoop` |

## 磁盘空间

- `df -h` 和 `df -i`：除了空间，还要看 inode 是否耗尽。大量小文件时，会出现空间还有剩余、却写不进去的情况。
- `du` 统计出的用量远小于 `df` 显示的用量：通常是文件已被删除，但仍有进程打开着它。用 `lsof +L1` 找出这些进程（需要 root）。处理办法是让该进程重新打开文件或重启它（确认门），不要直接删文件。
- 预留块：ext4 默认为 root 保留 5% 的空间，所以普通用户看到磁盘"满了"，root 还能写入。
