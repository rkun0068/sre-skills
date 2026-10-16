#!/usr/bin/env python3
"""Extract structured fields from Linux kernel oops / panic / BUG / WARNING text.

Pure extraction: no conclusions. Handles dmesg timestamps and syslog/journal prefixes.
Usage: extract_oops.py [--summary] [FILE]   (reads stdin when FILE is omitted)
"""
import argparse
import json
import re
import sys

PREFIX = re.compile(
    r"^(?:\w{3}\s+\d+\s+[\d:]+\s+\S+\s+kernel:\s*)?"  # syslog: "Oct 16 10:00:00 host kernel: "
    r"(?:\S+T\S+\s+\S+\s+kernel:\s*)?"                 # journal short-iso
    r"(?:\[\s*[\d.]+\]\s*)?"                           # dmesg: "[ 123.456]"
    r"(?:\[[A-Z][a-z]{2} [A-Z][a-z]{2} [ \d]\d [\d:]{8} \d{4}\]\s*)?"  # dmesg -T: "[Thu Oct 16 10:00:00 2026]"
)

RE_OOM_HEAD = re.compile(r"invoked oom-killer: gfp_mask=(\S+), order=(-?\d+)")

START = [
    ("page_fault", re.compile(r"BUG: (kernel NULL pointer dereference|unable to handle (page fault|kernel paging request|page request))")),
    ("gpf", re.compile(r"general protection fault")),
    ("bug", re.compile(r"kernel BUG at (\S+)")),
    ("bug", re.compile(r"^BUG: (?!soft lockup|unable|kernel NULL)(.+)")),
    ("warning", re.compile(r"^WARNING: CPU: \d+ PID: \d+ at (\S+)")),
    ("soft_lockup", re.compile(r"BUG: soft lockup")),
    ("hard_lockup", re.compile(r"Watchdog detected hard LOCKUP")),
    ("hung_task", re.compile(r"INFO: task \S+ blocked for more than \d+ seconds")),
    ("rcu_stall", re.compile(r"rcu: INFO: \S+ (self-)?detected stalls?")),
    ("oom", RE_OOM_HEAD),
    ("panic", re.compile(r"^Kernel panic - not syncing: (.*)")),
]
END = re.compile(r"---\[ end (trace|Kernel panic)|Killed process \d+")

RE_CTX = re.compile(r"CPU: (\d+) (?:UID: \d+ )?PID: (\d+) Comm: (\S+)")
RE_TAINT = re.compile(r"\b(Not tainted|Tainted: ([A-Z ]+))")
RE_VER = re.compile(r"\s(\d+\.\d+\.\d+\S*) #\d")
RE_OOM_KILL = re.compile(r"oom-kill:constraint=(\w+)(?:.*?oom_memcg=([^,]+))?.*?task=([^,]+),pid=(\d+)")
RE_OOM_KILLED = re.compile(r"Killed process (\d+) \((.+?)\) total-vm:(\d+)kB, anon-rss:(\d+)kB, file-rss:(\d+)kB, shmem-rss:(\d+)kB")
RE_HW = re.compile(r"^Hardware name: (.*)")
RE_OOPS = re.compile(r"^Oops: (\S+) \[#(\d+)\]")
RE_RIP = re.compile(r"^(?:RIP|EIP|pc) ?: ?(?:\S+:)?(?:\[<[0-9a-f]+>\] )?([\w.$]+)\+(0x[0-9a-f]+)/(0x[0-9a-f]+)(?: \[(\S+)\])?")
RE_CR2 = re.compile(r"^CR2: ([0-9a-f]+)")
RE_ADDR = re.compile(r"address: ([0-9a-f]{8,16})|at ([0-9a-f]{8,16})$")
RE_CODE = re.compile(r"^Code: (.*)")
RE_FRAME = re.compile(r"^\s*(\? )?([\w.$]+)\+(0x[0-9a-f]+)/(0x[0-9a-f]+)(?: \[(\S+)\])?")
RE_MODS = re.compile(r"^Modules linked in: (.*)")


def clean(line):
    return PREFIX.sub("", line.rstrip("\n"), count=1)


def split_reports(lines):
    reports, cur = [], None
    for line in lines:
        if cur is None and END.search(line):
            continue
        kind = next(((k, m) for k, rx in START for m in [rx.search(line)] if m), None)
        # "Kernel panic - not syncing: Fatal exception" follows "---[ end trace ]---":
        # it belongs to the preceding oops, not a new report.
        if kind and kind[0] == "panic" and cur is None and reports and "panic" not in reports[-1] \
                and reports[-1]["type"] != "panic":
            reports[-1]["panic"] = kind[1].group(1)
            continue
        if kind and not (cur and kind[0] == "panic" and cur["type"] != "panic"):
            if cur:
                reports.append(cur)
            cur = {"type": kind[0], "headline": line.strip(), "lines": []}
        if cur is None:
            continue
        cur["lines"].append(line)
        if kind and kind[0] == "panic" and cur["type"] != "panic":
            cur["panic"] = kind[1].group(1)
        if END.search(line):
            reports.append(cur)
            cur = None
    if cur:
        reports.append(cur)
    return reports


def parse(report):
    out = {k: v for k, v in report.items() if k != "lines"}
    out["call_trace"] = []
    in_trace = False
    for line in report["lines"]:
        if m := RE_CTX.search(line):
            out.setdefault("cpu", int(m[1]))
            out.setdefault("pid", int(m[2]))
            out.setdefault("comm", m[3])
        if (m := RE_TAINT.search(line)) and "tainted" not in out:
            out["tainted"] = "" if m[1] == "Not tainted" else m[2].replace(" ", "")
        if (m := RE_VER.search(line)) and "kernel" not in out:
            out["kernel"] = m[1]
        if m := RE_OOM_KILL.search(line):
            out["oom"] = {**out.get("oom", {}), "constraint": m[1], "oom_memcg": m[2], "victim": m[3], "victim_pid": int(m[4])}
        elif m := RE_OOM_KILLED.search(line):
            out["oom"] = {**out.get("oom", {}), "killed_pid": int(m[1]), "killed_comm": m[2],
                          "total_vm_kb": int(m[3]), "anon_rss_kb": int(m[4]), "file_rss_kb": int(m[5]), "shmem_rss_kb": int(m[6])}
        if m := RE_HW.search(line):
            out["hardware"] = m[1].strip()
        elif m := RE_OOPS.search(line):
            out.update(oops_code=m[1], oops_seq=int(m[2]))
        elif (m := RE_RIP.search(line)) and "rip" not in out:
            out["rip"] = {"func": m[1], "offset": m[2], "size": m[3], "module": m[4]}
        elif m := RE_CR2.search(line):
            out["cr2"] = m[1]
        elif m := RE_CODE.search(line):
            out["code"] = m[1].strip()
        elif m := RE_MODS.search(line):
            out["modules"] = m[1].split()
        if "Call Trace:" in line or "<TASK>" in line:
            in_trace = True
            continue
        if in_trace:
            if m := RE_FRAME.match(line):
                out["call_trace"].append({"func": m[2], "offset": m[3], "size": m[4],
                                          "module": m[5], "unreliable": bool(m[1])})
            elif "</TASK>" in line or line.startswith(("RIP", "Modules", "---[")):
                in_trace = False
    if "address" not in out and (m := RE_ADDR.search(report["headline"])):
        out["address"] = m[1] or m[2]
    if out["type"] == "bug" and (m := re.search(r"kernel BUG at (\S+)", report["headline"])):
        out["bug_at"] = m[1].rstrip("!")
    if out["type"] == "hung_task" and (m := re.search(r"task (\S+):(\d+) blocked", report["headline"])):
        out.setdefault("comm", m[1])
        out.setdefault("pid", int(m[2]))
    if out["type"] == "oom" and (m := RE_OOM_HEAD.search(report["headline"])):
        out.setdefault("oom", {}).update(gfp_mask=m[1], order=int(m[2]))
    if out["type"] == "warning" and (m := re.search(r" at (\S+)", report["headline"])):
        out["warn_at"] = m[1]
    return out


def summary(r):
    rip = r.get("rip") or {}
    loc = f"{rip.get('func')}+{rip.get('offset')}" + (f" [{rip['module']}]" if rip.get("module") else "") if rip else "-"
    frames = [f["func"] + (f" [{f['module']}]" if f["module"] else "") for f in r["call_trace"] if not f["unreliable"]][:8]
    return (f"#{r.get('oops_seq', '-')} {r['type']}: {r['headline']}\n"
            f"  comm={r.get('comm')} pid={r.get('pid')} cpu={r.get('cpu')} kernel={r.get('kernel')} tainted={r.get('tainted')!r}\n"
            f"  rip={loc} cr2={r.get('cr2', '-')} panic={r.get('panic', '-')}\n"
            f"  trace: {' <- '.join(frames) or '-'}"
            + (f"\n  oom: {r['oom']}" if r.get("oom") else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("file", nargs="?")
    a = ap.parse_args()
    text = open(a.file, encoding="utf-8", errors="replace") if a.file else sys.stdin
    lines = [clean(l) for l in text]
    reports = [parse(r) for r in split_reports(lines)]
    if not reports:
        sys.exit("no oops/panic/BUG/WARNING/lockup signature found")
    if a.summary:
        print("\n".join(summary(r) for r in reports))
    else:
        json.dump(reports, sys.stdout, indent=2)
        print()


if __name__ == "__main__":
    main()
