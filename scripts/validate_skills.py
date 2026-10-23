#!/usr/bin/env python3
"""Validate the sre-skills marketplace: manifests, skill frontmatter, links, scripts, evals."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
MAX_SKILL_LINES = 500

DOCS_SHARED = "sre-doc-standards"
DOCS_METADATA = ["文档类型", "标题", "状态", "密级", "Owner", "创建日期", "最后更新"]
# Live/procedural docs track work elsewhere (live task tracker / revision log).
DOCS_NO_ACTION_TABLE = {"sre-incident-doc", "sre-playbook"}

# plugin -> shared-protocol skill every other skill in that plugin must reference
PLUGIN_ENTRY = {"sre-docs": DOCS_SHARED, "sre-kernel": "kernel-triage", "tech-docs": "tech-doc-style"}
# plugins whose skills ship scripts and must have evals/<skill>/evals.json
EVAL_PLUGINS = {"sre-kernel", "tech-docs"}
MIN_EVALS = 3
# fixture -> report types extract_oops.py must find, in order
KERNEL_FIXTURES = {
    "oops-null-deref-oot.txt": ["page_fault"],
    "gpf-list-poison.txt": ["gpf"],
    "hung-task-nfs.txt": ["hung_task"],
    "soft-lockup-vm.txt": ["soft_lockup", "rcu_stall"],
    "oom-memcg.txt": ["oom"],
}

# fixture -> lint rules that must be reported; good-* fixtures must produce no findings
LINT_FIXTURES = {
    "bad-en.md": ["en-inclusive", "heading-case", "en-please", "en-timeless", "en-trivial", "en-directional",
                  "en-click-on", "en-latin", "placeholder-angle", "placeholder-possessive", "link-text",
                  "date-ambiguous", "image-alt", "heading-h1", "en-claims", "code-lang"],
    "bad-zh.md": ["zh-space", "zh-punct", "zh-trivial", "zh-please-note", "zh-timeless", "zh-directional",
                  "zh-inclusive", "zh-exclaim", "placeholder-angle", "link-text", "heading-punct"],
    "good-en.md": [],
    "good-zh.md": [],
}

errors = []


def err(msg):
    errors.append(msg)


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fields, key = {}, None
    for line in m.group(1).splitlines():
        if line.startswith((" ", "\t")) and key:
            fields[key] = (fields[key] + " " + line.strip()).strip()
        elif ":" in line:
            key, v = line.split(":", 1)
            key, v = key.strip(), v.strip()
            fields[key] = "" if v in (">", ">-", "|", "|-") else v
    return fields


def check_manifests():
    mp = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    listed = {p["name"]: p["source"] for p in mp["plugins"]}
    for d in sorted(p for p in PLUGINS.iterdir() if p.is_dir()):
        if d.name not in listed:
            err(f"{d.name}: plugin not listed in marketplace.json")
        elif (ROOT / listed[d.name]).resolve() != d.resolve():
            err(f"{d.name}: marketplace source {listed[d.name]} does not point to {d}")
        pj = d / ".claude-plugin" / "plugin.json"
        if not pj.exists():
            err(f"{d.name}: missing .claude-plugin/plugin.json")
        elif json.loads(pj.read_text()).get("name") != d.name:
            err(f"{d.name}: plugin.json name mismatch")
    for name in listed:
        if not (PLUGINS / name).is_dir():
            err(f"marketplace lists missing plugin {name}")


def check_skill_common(plugin, d, text, readme):
    fm = frontmatter(text)
    if fm is None:
        return err(f"{plugin}/{d.name}: missing frontmatter")
    if fm.get("name") != d.name:
        err(f"{plugin}/{d.name}: frontmatter name {fm.get('name')!r} != directory name")
    desc = fm.get("description", "")
    if not desc:
        err(f"{plugin}/{d.name}: empty description")
    elif len(desc) > 1024:
        err(f"{plugin}/{d.name}: description is {len(desc)} chars (> 1024)")
    for kw in ("TRIGGER when", "DO NOT TRIGGER when"):
        if kw not in desc:
            err(f"{plugin}/{d.name}: description missing '{kw}'")
    if len(text.splitlines()) > MAX_SKILL_LINES:
        err(f"{plugin}/{d.name}: SKILL.md longer than {MAX_SKILL_LINES} lines")
    # every relative markdown link must resolve
    for target in re.findall(r"\]\(((?!https?://|#)[^)]+)\)", text):
        if not (d / target.split("#")[0]).resolve().exists():
            err(f"{plugin}/{d.name}: broken link {target}")
    # every scripts/<file> mentioned must exist (relative to the skill, or a sibling skill)
    for target in set(re.findall(r"(?:\.\./[\w-]+/)?scripts/[\w.-]+\.(?:sh|py)", text)):
        if not (d / target).resolve().exists():
            err(f"{plugin}/{d.name}: mentions missing {target}")
    if f"plugins/{plugin}/skills/{d.name}/SKILL.md" not in readme:
        err(f"{plugin}/{d.name}: not indexed in README.md")


def check_entry_reference(plugin, d, text):
    entry = PLUGIN_ENTRY.get(plugin)
    if entry and d.name != entry and f"../{entry}/SKILL.md" not in text:
        err(f"{plugin}/{d.name}: does not reference ../{entry}/SKILL.md")


def check_docs_skill(d, text):
    if d.name == DOCS_SHARED:
        return
    if "## 质量门禁" not in text or "## 出处" not in text:
        err(f"sre-docs/{d.name}: missing 质量门禁 or 出处 section")
    tpl = d / "assets" / "template.md"
    if not tpl.exists():
        return err(f"sre-docs/{d.name}: missing assets/template.md")
    tpl_text = tpl.read_text(encoding="utf-8")
    for field in DOCS_METADATA:
        if f"| {field}" not in tpl_text:
            err(f"sre-docs/{d.name}: template metadata missing '{field}'")
    if d.name not in DOCS_NO_ACTION_TABLE and "| ID | 行动项 |" not in tpl_text:
        err(f"sre-docs/{d.name}: template missing standard action-item table")


def check_scripts_and_evals(plugin_dir, d):
    plugin = plugin_dir.name
    for script in sorted((d / "scripts").glob("*")):
        if script.suffix == ".sh":
            r = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
        elif script.suffix == ".py":
            r = subprocess.run([sys.executable, "-m", "py_compile", str(script)], capture_output=True, text=True)
        else:
            continue
        if r.returncode:
            err(f"{plugin}/{d.name}: {script.name} syntax error: {r.stderr.strip()}")
        if not script.stat().st_mode & 0o111:
            err(f"{plugin}/{d.name}: {script.name} is not executable")
    ev = plugin_dir / "evals" / d.name / "evals.json"
    if not ev.exists():
        return err(f"{plugin}/{d.name}: missing evals/{d.name}/evals.json")
    data = json.loads(ev.read_text())
    if data.get("skill_name") != d.name:
        err(f"{plugin}/{d.name}: evals.json skill_name mismatch")
    if len(data.get("evals", [])) < MIN_EVALS:
        err(f"{plugin}/{d.name}: fewer than {MIN_EVALS} evals")
    for case in data.get("evals", []):
        for f in case.get("files", []):
            if not (ev.parent / f).exists():
                err(f"{plugin}/{d.name}: eval {case.get('id')} references missing {f}")


def check_kernel_fixtures(plugin_dir):
    extractor = plugin_dir / "skills" / "kernel-crash-analysis" / "scripts" / "extract_oops.py"
    for name, expected in KERNEL_FIXTURES.items():
        fx = plugin_dir / "evals" / "fixtures" / name
        r = subprocess.run([sys.executable, str(extractor), str(fx)], capture_output=True, text=True)
        if r.returncode:
            err(f"extract_oops.py failed on {name}: {r.stderr.strip()}")
            continue
        got = [rep["type"] for rep in json.loads(r.stdout)]
        if got != expected:
            err(f"extract_oops.py on {name}: got {got}, expected {expected}")


def check_lint_fixtures(plugin_dir):
    linter = plugin_dir / "skills" / "tech-doc-style" / "scripts" / "lint_style.py"
    for name, expected in LINT_FIXTURES.items():
        fx = plugin_dir / "evals" / "fixtures" / name
        r = subprocess.run([sys.executable, str(linter), "--format", "json", str(fx)], capture_output=True, text=True)
        if r.returncode:
            err(f"lint_style.py failed on {name}: {r.stderr.strip()}")
            continue
        got = {f["rule"] for f in json.loads(r.stdout)}
        if not expected and got:
            err(f"lint_style.py on {name}: expected no findings, got {sorted(got)}")
        missing = set(expected) - got
        if missing:
            err(f"lint_style.py on {name}: missing rules {sorted(missing)}")


def main():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    check_manifests()
    count = 0
    for plugin_dir in sorted(p for p in PLUGINS.iterdir() if p.is_dir()):
        for d in sorted(p for p in (plugin_dir / "skills").iterdir() if p.is_dir()):
            skill_md = d / "SKILL.md"
            if not skill_md.exists():
                err(f"{plugin_dir.name}/{d.name}: missing SKILL.md")
                continue
            count += 1
            text = skill_md.read_text(encoding="utf-8")
            check_skill_common(plugin_dir.name, d, text, readme)
            check_entry_reference(plugin_dir.name, d, text)
            if plugin_dir.name == "sre-docs":
                check_docs_skill(d, text)
            if plugin_dir.name in EVAL_PLUGINS:
                check_scripts_and_evals(plugin_dir, d)
        if plugin_dir.name == "sre-kernel":
            check_kernel_fixtures(plugin_dir)
        elif plugin_dir.name == "tech-docs":
            check_lint_fixtures(plugin_dir)

    print(f"checked {count} skills")
    if errors:
        print("\n".join(f"  ✗ {e}" for e in errors))
        sys.exit(1)
    print("  ✓ all checks passed")


if __name__ == "__main__":
    main()
