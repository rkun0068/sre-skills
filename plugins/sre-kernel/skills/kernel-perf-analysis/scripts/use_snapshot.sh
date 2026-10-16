#!/usr/bin/env bash
# USE-method snapshot (Utilization / Saturation / Errors) per resource. Read-only, procfs/sysfs first.
# Usage: ssh -o BatchMode=yes <host> 'bash -s' < use_snapshot.sh
# Env: I=<delta interval seconds for counters> (default 5)
set -u
export LC_ALL=C
I=${I:-5}
T=$((I + 10))

sec() { printf '\n===== %s =====\n' "$1"; }
run() { timeout "$T" bash -c "$1" 2>&1 || echo "[rc=$?] $1"; }

# Print counters from /proc/vmstat or nstat that changed over $I seconds.
vmstat_delta() {
  local keys="$1"
  local a b
  a=$(grep -E "^($keys) " /proc/vmstat); sleep "$I"; b=$(grep -E "^($keys) " /proc/vmstat)
  join <(echo "$a" | sort) <(echo "$b" | sort) | awk -v i="$I" '{d=$3-$2; printf "%-28s %12d  (%.1f/s)\n", $1, d, d/i}'
}

sec "CPU"
echo "# U: non-idle %  S: run queue vs nproc, PSI cpu, steal  E: (perf only)"
run 'echo "nproc=$(nproc)"; cat /proc/loadavg'
run "vmstat -w 1 $I | tail -n +2"
run 'cat /proc/pressure/cpu 2>/dev/null'
run "( dmesg -T 2>/dev/null || journalctl -k -b --no-pager ) | grep -iE 'temperature above threshold|cpu clock throttled|mce:' | tail -5"

sec "MEMORY"
echo "# U: used vs total (MemAvailable)  S: scanning, swapping, PSI memory, OOM  E: EDAC / alloc failures"
run 'grep -E "^(MemTotal|MemFree|MemAvailable|Buffers|Cached|SwapTotal|SwapFree|Dirty|Writeback|Shmem|Slab|SReclaimable|SUnreclaim|AnonHugePages|HugePages_Total|HugePages_Free)" /proc/meminfo'
run 'cat /proc/pressure/memory 2>/dev/null'
run "$(declare -f vmstat_delta); I=$I vmstat_delta 'pgscan_kswapd|pgscan_direct|pgsteal_kswapd|pgsteal_direct|pswpin|pswpout|allocstall_normal|allocstall_movable|oom_kill|compact_stall'"
run "( dmesg -T 2>/dev/null || journalctl -k -b --no-pager ) | grep -E 'invoked oom-killer|Out of memory|Memory cgroup out of memory|oom-kill:' | tail -10"
run 'grep -H . /sys/devices/system/edac/mc/mc*/[cu]e_count 2>/dev/null || true'

sec "STORAGE DEVICE I/O"
echo "# U: %util (misleading on SSD/RAID)  S: aqu-sz, await, PSI io  E: I/O errors, device error counters"
run "command -v iostat >/dev/null && iostat -xz 1 2 | awk '/^avg-cpu/{n++} n==2' || cat /proc/diskstats"
run 'cat /proc/pressure/io 2>/dev/null'
run "( dmesg -T 2>/dev/null || journalctl -k -b --no-pager ) | grep -iE 'I/O error|blk_update_request|medium error|reset|timeout' | tail -10"

sec "STORAGE CAPACITY"
run 'df -hT -x tmpfs -x devtmpfs -x squashfs -x overlay'
run 'df -i -x tmpfs -x devtmpfs -x squashfs -x overlay | awk "NR==1 || \$5+0 >= 80"'
run 'swapon --show 2>/dev/null'

sec "NETWORK INTERFACES"
echo "# U: throughput vs link speed  S: drops/overruns, retransmits, listen overflows  E: rx/tx errors"
run 'ip -s -s link show | grep -vE "link/|alias"'
run 'for i in /sys/class/net/*; do n=${i##*/}; [ "$n" = lo ] && continue; echo "$n speed=$(cat $i/speed 2>/dev/null)Mb/s"; done'
run "nstat -az 2>/dev/null | grep -E 'TcpRetransSegs|TcpOutSegs|TcpExtListenOverflows|TcpExtListenDrops|TcpExtTCPTimeouts|TcpExtTCPSynRetrans|TcpEstabResets|TcpAttemptFails|UdpRcvbufErrors|UdpSndbufErrors'"
# softnet_stat is hex; parse in bash (mawk on Ubuntu has no strtonum). Show CPUs with drops/squeezes only.
run 'cpu=0; while read -r p d s _; do d=$((16#$d)); s=$((16#$s)); [ $((d + s)) -gt 0 ] && echo "cpu$cpu processed=$((16#$p)) dropped=$d time_squeeze=$s"; cpu=$((cpu + 1)); done < /proc/net/softnet_stat; echo "softnet: listed CPUs with drops/time_squeeze only"'
run 'ss -s'

sec "SOFTWARE RESOURCES"
echo "# file descriptors, tasks/threads, PIDs, conntrack, ephemeral ports"
run 'echo "file-nr(alloc free max): $(cat /proc/sys/fs/file-nr)"'
run 'echo "threads=$(ps -eLf --no-headers | wc -l) threads-max=$(cat /proc/sys/kernel/threads-max) pid_max=$(cat /proc/sys/kernel/pid_max)"'
run 'c=/proc/sys/net/netfilter; [ -r $c/nf_conntrack_count ] && echo "conntrack $(cat $c/nf_conntrack_count)/$(cat $c/nf_conntrack_max)" || echo "conntrack not loaded"'
run 'echo "ip_local_port_range: $(cat /proc/sys/net/ipv4/ip_local_port_range)"; ss -tan state time-wait | wc -l | sed "s/^/time-wait: /"'
