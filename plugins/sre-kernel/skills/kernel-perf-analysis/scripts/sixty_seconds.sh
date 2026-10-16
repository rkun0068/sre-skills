#!/usr/bin/env bash
# Time-bounded "60-second" Linux performance checklist (Netflix / Brendan Gregg). Read-only.
# Usage: ssh -o BatchMode=yes <host> 'bash -s' < sixty_seconds.sh
# Env: S=<sample count per interval tool> (default 5)
set -u
export LC_ALL=C
S=${S:-5}
T=$((S + 10))

sec() { printf '\n===== %s =====\n' "$1"; }
run() { timeout "$T" bash -c "$1" 2>&1 || echo "[rc=$?] $1"; }
have() { command -v "$1" >/dev/null 2>&1; }

missing=""
for c in mpstat pidstat iostat sar; do have "$c" || missing="$missing $c"; done

sec "uptime"
run 'uptime; echo "nproc=$(nproc)"'

sec "dmesg | tail"
run '( dmesg -T 2>/dev/null || journalctl -k -b --no-pager 2>/dev/null ) | tail -20'

sec "vmstat 1 $S"
run "vmstat -w 1 $S"

sec "mpstat -P ALL 1 $S"
have mpstat && run "mpstat -P ALL 1 $S | tail -n +3" || echo "skipped: sysstat missing"

sec "pidstat 1 $S"
have pidstat && run "pidstat 1 $S | awk 'NR<4 || /Average/'" || echo "skipped: sysstat missing"

sec "iostat -xz 1 $S"
have iostat && run "iostat -xz 1 $S" || echo "skipped: sysstat missing"

sec "free -m"
run 'free -m'

sec "sar -n DEV 1 $S"
have sar && run "sar -n DEV 1 $S | grep -E 'Average|IFACE'" || echo "skipped: sysstat missing"

sec "sar -n TCP,ETCP 1 $S"
have sar && run "sar -n TCP,ETCP 1 $S | grep -E 'Average'" || echo "skipped: sysstat missing"

sec "top"
run 'top -b -n 1 -w 200 | head -25'

if [ -n "$missing" ]; then
  sec "missing tools"
  echo "not installed:$missing (package: sysstat). Installing requires confirmation."
fi
