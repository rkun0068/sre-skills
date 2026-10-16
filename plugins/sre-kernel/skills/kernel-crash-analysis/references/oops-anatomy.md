# Oops 结构与判读

## 目录
- 类型
- 标题行判读
- 字段
- x86 页错误码
- 硬件路径
- 分诊启发式

## 类型

| 类型 | 典型标题行 | 是否致命 |
|---|---|---|
| 页错误 | `BUG: kernel NULL pointer dereference, address: …` / `BUG: unable to handle page fault for address: …` | 进程被杀；`panic_on_oops=1` 时整机 panic |
| GPF | `general protection fault, probably for non-canonical address 0x…` | 同上 |
| BUG | `kernel BUG at fs/xxx.c:123!`（BUG_ON 断言失败） | 同上 |
| WARNING | `WARNING: CPU: 2 PID: 77 at drivers/x.c:88 func+0x…` | 不致命，会打上 W taint；`panic_on_warn=1` 时会 panic |
| panic | `Kernel panic - not syncing: <原因>` | 致命，按 `kernel.panic` 的设置决定是否自动重启 |
| KASAN/KFENCE | `BUG: KASAN: use-after-free in …` | 调试内核才会出现，直接指明内存错误类型 |

常见的 panic 原因：
- `Fatal exception`：前面有一个 oops，且 `panic_on_oops=1`；
- `Attempted to kill init`：PID 1 崩溃；
- `Out of memory and no killable processes`；
- `softlockup: hung tasks` / `hung_task: blocked tasks`：由对应的 `*_panic` sysctl 触发，转 kernel-hang-analysis；
- `VFS: Unable to mount root fs`：启动问题，通常是 initramfs 或驱动缺失。

## 标题行判读

| 地址特征 | 含义 |
|---|---|
| `0000000000000000`–`0000000000000fff` | NULL 指针加结构体字段偏移。偏移量可以帮助定位是哪个字段 |
| `dead000000000100` / `dead000000000122` | LIST_POISON：访问了已从链表删除的节点，即链表损坏或 use-after-free |
| `6b6b6b6b6b6b6b6b` | slab 释放毒化值（需要开启 slub_debug）：use-after-free |
| `a5a5a5a5…` / `5a5a5a5a…` | slab 毒化或 redzone 被破坏 |
| 非规范地址（GPF） | 指针被覆盖或损坏 |
| 看起来正常的内核地址 | 可能是 use-after-free，也可能是硬件比特翻转。需要结合是否在多台机器上复现来判断 |

## 字段

| 字段 | 含义与用法 |
|---|---|
| `Oops: 0002 [#1] PREEMPT SMP PTI` | 错误码（x86 页错误码见下节）；`[#N]` 是本次启动的第几个 oops，**分析 #1** |
| `CPU: … PID: … Comm: …` | 出事时正在运行的任务。Comm 为 `swapper` 表示 idle 上下文或中断上下文 |
| `Tainted: G OE` | taint 字母，见 decode_taint.py |
| `<内核版本> #1` | 必须与 debuginfo 完全一致 |
| `Hardware name:` | 机型和 BIOS 版本，可用来判断问题是否只出现在某个型号上 |
| `RIP: 0010:func+0x2a/0x90 [mod]` | 出错的指令位置：函数加偏移、函数总长度、所属模块 |
| `CR2:` | 发生页错误的地址 |
| `Code: … <8b> …` | 出错位置附近的机器码，`<>` 标出的是出错的那个字节。可以用 decodecode 反汇编 |
| `Call Trace:` / `<TASK>` | 调用栈，从上往下是从内向外。带 `? ` 前缀的帧不可靠，可能是栈上的残留 |
| `<IRQ>` / `<NMI>` | 出错时处于中断或 NMI 上下文 |
| `Modules linked in: … [last unloaded: x]` | 已加载的模块。带 `(OE)` 等标记的是 taint 来源 |

## x86 页错误码（Oops 后面的数字）

| 位 | 置 1 时的含义 |
|---|---|
| 0 P | 页存在，即保护违例；为 0 时表示页不存在 |
| 1 W | 写操作；为 0 时是读 |
| 2 U | 用户态访问 |
| 3 RSVD | 页表保留位被置位，说明页表损坏 |
| 4 I | 取指令时出错 |

例如 `0002`：页不存在、写操作、内核态。

## 硬件路径

满足以下任一条件时，先排除硬件，再分析软件：
- taint 含 M，或日志中有 `mce:` / `Machine check events logged`；
- EDAC 的 `ue_count` > 0，或 `ce_count` 持续增长；
- 同一台机器反复崩溃，但调用栈各不相同；
- 日志中有磁盘、NIC 硬件报错，或 PCIe AER 报错。

可以查看的证据（只读）：
- `journalctl -k | grep -i mce`、`ras-mc-ctl --errors`（需要 rasdaemon）；
- 物理机上的 `ipmitool sel elist`。

## 分诊启发式

1. 只分析第一个 oops，后面的多半是连锁反应。
2. RIP 或调用栈里出现带 O/E/P taint 的模块时，先怀疑该模块。
3. 同一内核版本、多台机器、调用栈相同：内核或驱动 bug，去查已知问题。
4. 单台机器、调用栈随机：怀疑内存或 CPU 硬件。
5. 首次出现的时间紧跟内核或驱动升级之后：回归，考虑回退。
6. WARNING 本身通常不致命。要说明它和用户看到的现象之间是否有因果关系，不要只因为它出现了就把它当成根因。
