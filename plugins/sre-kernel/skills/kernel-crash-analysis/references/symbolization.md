# 符号化：把 func+off 映射到源码行

全部操作在**独立分析机**上进行。安装 debuginfo 需要几 GB 的磁盘空间和网络访问。

## 前提

- debuginfo 必须与 oops 中的内核版本**完全一致**（例如 `5.14.0-362.8.1.el9_3.x86_64`）。版本不一致时，得到的行号是错的，而且不会有任何报错提示。
- 出错位置在模块里时，还需要该模块对应的 `.ko.debug` 文件。第三方模块要向供应商索取带符号的版本。

## 获取 debuginfo

| 发行版 | 安装命令 | 安装后文件位置 |
|---|---|---|
| RHEL / Rocky / Alma | `dnf debuginfo-install kernel-<ver>`（需要启用 `*-debuginfo` 仓库；RHEL 7 用 `debuginfo-install`） | vmlinux：`/usr/lib/debug/lib/modules/<ver>/vmlinux`；模块：同目录下的 `kernel/**/<mod>.ko.debug` |
| Ubuntu | 先添加 ddebs 仓库（`deb http://ddebs.ubuntu.com <codename>{,-updates} main restricted universe multiverse` 并导入 key），再 `apt install linux-image-<ver>-dbgsym` | vmlinux：`/usr/lib/debug/boot/vmlinux-<ver>`；模块：`/usr/lib/debug/lib/modules/<ver>/kernel/**` |

源码：
- RHEL：kernel 的 SRPM，或 CentOS Stream 的 git 仓库；
- Ubuntu：`apt source linux-image-unsigned-<ver>`，或从 `git.launchpad.net/~ubuntu-kernel` 获取。

`scripts/` 目录下的工具都在内核源码树里。

## 方法（由简到繁）

1. **gdb**：最直接。
   ```bash
   gdb -batch -ex 'list *(acme_xmit+0x2a)' /path/to/vmlinux
   gdb -batch -ex 'list *(acme_xmit+0x2a)' /path/to/acme_nic.ko.debug   # 出错在模块里时
   ```
   内联函数会被展开，报出来的行可能落在被内联的函数里。可以用 `info line *(func+off)` 交叉确认。
2. **faddr2line**：可以直接使用 oops 中 `func+off/size` 的格式，处理内联函数也更准确。
   ```bash
   ./scripts/faddr2line /path/to/vmlinux acme_xmit+0x2a/0x90
   ```
3. **decode_stacktrace.sh**：一次性解码整段调用栈。
   ```bash
   ./scripts/decode_stacktrace.sh /path/to/vmlinux /usr/lib/debug/lib/modules/<ver> < oops.txt
   ```
4. **decodecode**：没有 debuginfo 时，至少能把 `Code:` 那一行反汇编出来，看清出错的指令和用到的寄存器。
   ```bash
   echo 'Code: <整行粘贴>' | ./scripts/decodecode
   ```
5. **objdump**：查看函数的完整反汇编，有源码时可以和源码对照。
   ```bash
   objdump -dS --start-address=0x... --stop-address=0x... vmlinux
   ```

## 解读要点

- 把出错指令里的寄存器和 oops 中的寄存器值对照，就能判断哪个指针是 NULL 或已损坏。
- 再结合 `CR2` 和结构体布局（`pahole -C <struct> vmlinux`）推出具体是哪个字段。
- 报告中给出源码位置时，附上与版本对应的在线链接或 git commit，并注明行号是精确的还是近似的。
