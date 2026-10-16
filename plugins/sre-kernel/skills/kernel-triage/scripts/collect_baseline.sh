#!/usr/bin/env bash
# Read-only kernel baseline for RHEL-family and Ubuntu hosts.
# Usage: ssh -o BatchMode=yes <host> 'bash -s' < collect_baseline.sh
# Env: T=<per-command timeout seconds> (default 10)
set -u
export LC_ALL=C
T=${T:-10}

sec() { printf '\n===== %s =====\n' "$1"; }
run() { timeout "$T" bash -c "$1" 2>&1 || echo "[rc=$?] $1"; }
have() { command -v "$1" >/dev/null 2>&1; }

SIG='Oops|BUG:|kernel BUG at|WARNING: CPU|Kernel panic|general protection fault|soft lockup|hard LOCKUP|blocked for more than|rcu.*stall|Out of memory|oom-kill|Machine check|mce:|EDAC|I/O error|nf_conntrack: table full|segfault'

sec host
run 'hostname; date --iso-8601=seconds; uname -a'
run 'grep -E "^(PRETTY_NAME|VERSION_ID)=" /etc/os-release'
run 'uptime; echo "nproc=$(nproc)"'
run 'id -un'
run 'systemd-detect-virt 2>/dev/null || echo virt=unknown'

sec reboots
run 'last -x -F 2>/dev/null | grep -E "reboot|shutdown|crash" | head -20'
run 'journalctl --list-boots --no-pager 2>/dev/null | tail -5'

sec taint
run 'cat /proc/sys/kernel/tainted'
run 'for f in /sys/module/*/taint; do t=$(cat "$f" 2>/dev/null); [ -n "$t" ] && echo "${f%/taint}: $t"; done; true'

sec cmdline
run 'cat /proc/cmdline'

sec kernel_sysctls
run 'sysctl -e kernel.panic kernel.panic_on_oops kernel.panic_on_warn kernel.softlockup_panic kernel.hardlockup_panic kernel.hung_task_timeout_secs kernel.hung_task_panic kernel.nmi_watchdog kernel.watchdog_thresh kernel.sysrq vm.panic_on_oom'

sec kernel_packages
if have rpm; then
  run 'rpm -q kernel kernel-core 2>/dev/null | grep -v "not installed"'
  run 'rpm -qa --last 2>/dev/null | head -25'
elif have dpkg; then
  run 'dpkg -l "linux-image-*" 2>/dev/null | awk "/^ii/{print \$2, \$3}"'
  run 'grep -hE " (install|upgrade) " /var/log/dpkg.log 2>/dev/null | tail -25'
fi

sec kernel_log_signatures_current_boot
run "dmesg -T 2>/dev/null | grep -cE '$SIG' || true"
run "( dmesg -T 2>/dev/null || journalctl -k -b --no-pager 2>/dev/null ) | grep -E '$SIG' | tail -60"

sec kernel_log_errors_tail
run '( dmesg -T --level=emerg,alert,crit,err,warn 2>/dev/null || journalctl -k -b -p warning --no-pager 2>/dev/null ) | tail -60'

sec kernel_log_previous_boot_tail
run 'journalctl -k -b -1 -n 60 --no-pager 2>/dev/null || echo "no previous boot in journal (journal may not be persistent)"'

sec kdump
run 'grep -o "crashkernel=[^ ]*" /proc/cmdline || echo "crashkernel not set"'
run 'cat /sys/kernel/kexec_crash_loaded 2>/dev/null'
run 'systemctl is-active kdump kdump-tools 2>/dev/null; true'
run 'ls -lt /var/crash 2>/dev/null | head -10'

sec pstore
run 'ls -l /sys/fs/pstore /var/lib/systemd/pstore 2>/dev/null; true'

sec hardware_errors
run 'grep -H . /sys/devices/system/edac/mc/mc*/ce_count /sys/devices/system/edac/mc/mc*/ue_count 2>/dev/null || echo "no EDAC counters"'
run "journalctl -k --no-pager --since '-7 days' 2>/dev/null | grep -iE 'mce:|machine check|hardware error' | tail -10"

sec pressure
run 'cat /proc/loadavg'
run 'for r in cpu memory io; do echo "$r: $(cat /proc/pressure/$r 2>/dev/null | tr "\n" " ")"; done'
run 'grep -E "^(MemTotal|MemAvailable|SwapTotal|SwapFree|Dirty|Writeback|Slab|SUnreclaim)" /proc/meminfo'
run 'ps -eo state= | sort | uniq -c'
