#!/usr/bin/env bash
# Read-only snapshot for kernel hangs / D-state pile-ups. Does NOT touch /proc/sysrq-trigger.
# Usage: ssh -o BatchMode=yes <host> 'bash -s' < hang_snapshot.sh
# Env: T=<per-command timeout seconds> (default 8), N=<max D threads to inspect> (default 30)
set -u
export LC_ALL=C
T=${T:-8}
N=${N:-30}

sec() { printf '\n===== %s =====\n' "$1"; }
run() { timeout "$T" bash -c "$1" 2>&1 || echo "[rc=$?] $1"; }

sec host
run 'hostname; date --iso-8601=seconds; uname -r; uptime; echo "nproc=$(nproc)"; id -un'
run 'systemd-detect-virt 2>/dev/null || echo virt=unknown'

sec kernel_log_stalls
run "( dmesg -T 2>/dev/null || journalctl -k -b --no-pager 2>/dev/null ) | grep -E 'soft lockup|hard LOCKUP|blocked for more than|rcu.*stall|hung_task|NMI backtrace|nfs: server .* not responding|I/O error|timeout|task abort' | tail -60"

sec watchdog_sysctls
run 'sysctl -e kernel.watchdog_thresh kernel.softlockup_panic kernel.hardlockup_panic kernel.nmi_watchdog kernel.hung_task_timeout_secs kernel.hung_task_panic kernel.hung_task_warnings kernel.sysrq'

sec load_and_pressure
run 'cat /proc/loadavg'
run 'for r in cpu memory io; do echo "$r: $(cat /proc/pressure/$r 2>/dev/null | tr "\n" " ")"; done'
run 'vmstat 1 3'

sec task_states
run 'ps -eLo state= | sort | uniq -c'

sec d_state_threads
run "ps -eLo state,pid,tid,etimes,wchan:40,comm --no-headers | awk '\$1 ~ /^D/' | head -$N"

sec d_state_wchan_histogram
run "ps -eLo state,wchan:40 --no-headers | awk '\$1 ~ /^D/ {print \$2}' | sort | uniq -c | sort -rn | head -15"

sec d_state_kernel_stacks
run "for tid in \$(ps -eLo state,tid --no-headers | awk '\$1 ~ /^D/ {print \$2}' | head -$N); do
  echo \"--- tid \$tid (\$(cat /proc/\$tid/comm 2>/dev/null))\"
  cat /proc/\$tid/stack 2>/dev/null || echo '(stack unreadable: need root)'
done"

sec block_inflight
run 'for d in /sys/block/*; do n=${d##*/}; case $n in loop*|ram*) continue;; esac; echo "$n inflight(r w): $(cat $d/inflight 2>/dev/null)"; done'

sec nfs_mounts
run 'grep -E " nfs4? " /proc/mounts || echo "no NFS mounts"'

sec multipath
run 'command -v multipath >/dev/null && multipath -ll 2>/dev/null | grep -E "failed|faulty|offline" | head -20 || echo "multipath not in use or no failed paths"'
