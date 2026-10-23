# kdump 与 vmcore

## 检查 kdump 是否就绪（只读）

| 检查项 | RHEL 系 | Ubuntu |
|---|---|---|
| 服务状态 | `systemctl is-active kdump`、`kdumpctl status` | `systemctl is-active kdump-tools`、`kdump-config show` |
| 内存预留 | `/proc/cmdline` 中有 `crashkernel=` | 同左 |
| 已加载 | `/sys/kernel/kexec_crash_loaded` 为 1 | 同左 |
| 转储位置 | `/etc/kdump.conf` 中的 `path`，默认 `/var/crash/<ip>-<日期>/` | `/etc/default/kdump-tools`，默认 `/var/crash/<时间戳>/` |
| 文件 | `vmcore`、`vmcore-dmesg.txt` | `dump.<时间戳>`、`dmesg.<时间戳>` |

开启或修改 kdump 需要预留内存并重启，属于确认门操作，应按变更流程推进。

## 处理顺序

1. **先看 dmesg 文件**（`vmcore-dmesg.txt` / `dmesg.*`），里面就是崩溃前的内核日志，直接交给 `extract_oops.py`。多数情况看这一步就够了。
2. 需要查看内存状态（锁的持有者、各任务的状态、内存使用）时，再分析 vmcore：
   - 拷贝到分析机前先确认文件大小和可用带宽（确认门）：
     ```bash
     ls -lh /var/crash/*/
     scp <host>:/var/crash/<dir>/vmcore .
     sha256sum vmcore      # 两端都算一遍，核对是否一致
     ```
   - 在分析机上安装与崩溃内核**版本完全一致**的 debuginfo，见 symbolization.md。

## crash 工具常用命令

```bash
crash /usr/lib/debug/lib/modules/<ver>/vmlinux vmcore    # RHEL
crash /usr/lib/debug/boot/vmlinux-<ver> dump.<ts>         # Ubuntu
```

| 命令 | 用途 |
|---|---|
| `sys` | 内核版本、运行时长、panic 原因 |
| `log \| tail -100` | 内核日志 |
| `bt` | 出错任务的调用栈；`bt -a` 查看所有 CPU，`bt -l` 带上行号 |
| `ps \| grep UN` | D 状态的任务。卡死类问题用 `foreach UN bt` 查看它们各自的栈 |
| `kmem -i` | 内存使用概况；`kmem -s` 查看 slab |
| `dis -rl <addr>` | 反汇编到指定地址，并附上源码行 |
| `mod -s <mod> <path.ko.debug>` | 加载模块的符号 |
| `struct <type> <addr>` | 按结构体解析内存中的数据 |
| `files <pid>`、`net` | 打开的文件、网络状态 |

## 注意

- 在 live 系统上运行 crash（`crash` 不带 vmcore 参数）虽然是只读的，但开销较大，**不要在故障中的生产机上做**。
- vmcore 中可能包含用户数据和密钥。按 `sre-doc-standards` 的密级规则存放，用完即删。
