# 拿不到 oops 时

## 意外重启但日志里什么都没有

逐项检查（只读）：

1. `last -x -F`：重启前有没有 `shutdown` 记录。没有说明是非正常关机。
2. `journalctl --list-boots` 和 `journalctl -b -1 -n 200`：上一次启动的最后几行日志。如果 journal 没有持久化，就看不到：
   - RHEL 7 默认不持久化；
   - 判断方法：`/var/log/journal` 是否存在，或 `journald.conf` 中是否设置了 `Storage=persistent`。
3. `/var/log/messages`（RHEL）、`/var/log/kern.log`（Ubuntu）中最后时刻的内容。
4. pstore：`/sys/fs/pstore`、`/var/lib/systemd/pstore`（由 systemd-pstore 归档），可能保存着 panic 时的日志。
5. `/var/crash`：kdump 是否留下了 vmcore。
6. `kernel.panic` 的值。大于 0 时，panic 后会在 N 秒内自动重启，看起来就像"无故重启"。
7. 物理机：`ipmitool sel elist` 中有没有电源、看门狗、温度或 ECC 相关的事件。
8. 虚拟机：查看宿主机或云平台的事件日志，确认是不是宿主机迁移、宿主机故障或 OOM。

如果日志最后几行一切正常、然后突然中断，且没有 panic 记录：
- 优先怀疑电源、硬件看门狗、宿主机层面的问题，或者故障发生得太快、来不及把日志刷到磁盘；
- 不要直接下结论说是内核 bug。

## 为下次故障做准备（都属于变更，需要确认）

| 手段 | 作用 | 代价 |
|---|---|---|
| 开启 kdump | 保留完整的 vmcore | 预留内存、需要重启、占用磁盘空间 |
| journal 持久化（`Storage=persistent`） | 能查看上一次启动的日志 | 占用磁盘空间 |
| netconsole | 把内核日志通过 UDP 实时发到另一台机器 | 需要一台接收机，同网段 |
| 串口控制台 / IPMI SOL | 在机器完全卡死时也能拿到输出 | 需要配置 `console=ttyS0,115200` 并重启 |
| `kernel.panic_on_oops=1` | oops 后立即 panic，触发 kdump，留下现场 | 原本可能继续运行的机器会直接重启 |

建议把以上内容作为行动项，记录到事件文档或复盘文档中。
