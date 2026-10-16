#!/usr/bin/env python3
"""Decode /proc/sys/kernel/tainted. Usage: decode_taint.py <value>  (or value on stdin)"""
import sys

# bit: (letter, meaning, triage hint)
FLAGS = {
    0: ("P", "proprietary module loaded", "third-party module is first suspect"),
    1: ("F", "module force-loaded", "module/kernel mismatch possible"),
    2: ("S", "out-of-spec system", "hardware/firmware suspect"),
    3: ("R", "module force-unloaded", ""),
    4: ("M", "machine check exception", "hardware error: check MCE/EDAC before blaming software"),
    5: ("B", "bad page reference / unexpected page flags", "memory corruption (hw or sw)"),
    6: ("U", "taint requested by userspace", ""),
    7: ("D", "kernel died recently (OOPS/BUG)", "find the FIRST oops; later ones may be fallout"),
    8: ("A", "ACPI table overridden", ""),
    9: ("W", "kernel issued a warning", "check whether the WARNING relates to the symptom"),
    10: ("C", "staging driver loaded", "staging drivers are low quality: suspect"),
    11: ("I", "platform firmware bug workaround applied", "firmware suspect"),
    12: ("O", "out-of-tree module loaded", "third-party module is first suspect"),
    13: ("E", "unsigned module loaded", "third-party module is first suspect"),
    14: ("L", "soft lockup occurred", "see kernel-hang-analysis"),
    15: ("K", "kernel live-patched", "note livepatch version in report"),
    16: ("X", "auxiliary taint (distro-defined)", ""),
    17: ("T", "built with struct randomization plugin", ""),
    18: ("N", "in-kernel test has run", ""),
    19: ("J", "userspace used a mutating fwctl debug op", ""),
}


def decode(value: int):
    rows = []
    for bit, (letter, meaning, hint) in FLAGS.items():
        if value & (1 << bit):
            rows.append((bit, letter, meaning, hint))
    unknown = value & ~sum(1 << b for b in FLAGS)
    return rows, unknown


def main():
    raw = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    try:
        value = int(raw.strip(), 0)
    except ValueError:
        sys.exit(f"not an integer: {raw!r}")
    if value == 0:
        print("0: not tainted")
        return
    rows, unknown = decode(value)
    letters = "".join(r[1] for r in rows)
    print(f"{value}: {letters}")
    for bit, letter, meaning, hint in rows:
        print(f"  bit {bit:2d} {letter}  {meaning}" + (f"  -> {hint}" if hint else ""))
    if unknown:
        print(f"  unknown bits: {unknown:#x} (newer kernel? check docs.kernel.org tainted-kernels)")


if __name__ == "__main__":
    main()
