#!/usr/bin/env python3
"""Lint Markdown documentation against the tech-doc-style rules
(Google developer documentation style guide + Chinese typography).

Checks only what can be checked mechanically; semantic rules need human review.
Skips front matter, HTML comments, fenced code (except placeholder checks), inline code and URLs.

Usage: lint_style.py [--lang auto|en|zh] [--format text|json] [--min-severity info|warn|error]
                     [--strict] PATH...
"""
import argparse
import json
import re
import sys
from pathlib import Path

SEVERITIES = {"info": 0, "warn": 1, "error": 2}
CJK = "㐀-䶿一-鿿"
RE_CJK = re.compile(f"[{CJK}]")

# (rule, severity, pattern, message). Patterns run on prose with code/URLs blanked out.
EN_RULES = [
    ("en-trivial", "warn", r"\b(simply|just|easy|easily)\b", "makes the task sound trivial; delete it"),
    ("en-please", "warn", r"\b(please note|note that|please)\b", "drop it; state the point or use a direct imperative"),
    ("en-timeless", "warn", r"\b(currently|presently|as of this writing|soon|eventually|in the future|does not yet|latest)\b",
     "time-sensitive wording; remove it or give a version or date"),
    ("en-latin", "warn", r"(?<!\w)(e\.g\.|i\.e\.)", "use 'for example' / 'such as' or 'that is'"),
    ("en-etc", "info", r"(?<!\w)(etc\.|and so on|and so forth)", "list the items or introduce them with 'including'"),
    ("en-directional", "warn", r"\b(above|below|right-hand|left-hand)\b", "directional language; use 'preceding'/'following' or name the element"),
    ("en-click-on", "warn", r"\bclick on\b", "use 'click'"),
    ("en-lets-you", "info", r"\b(allows you to|enables you to)\b", "use 'lets you'"),
    ("en-wordy", "info", r"\b(in order to|utiliz(e|es|ed|ing)|leverag(e|es|ed|ing)|as per)\b", "use 'to', 'use', or 'according to'"),
    ("en-inclusive", "error", r"\b(whitelist\w*|blacklist\w*|slaves?|sanity[- ]checks?|dummy|crazy|crippl\w*)\b",
     "non-inclusive term; see references/word-list.md"),
    ("en-master", "warn", r"\bmaster\b", "consider primary/main/controller (ignore if it is a literal name)"),
    ("en-lets", "warn", r"\blet's\b", "avoid \"let's\"; address the reader as 'you'"),
    ("en-claims", "warn", r"\b(best|fastest|simplest|guarantee[sd]?|seamless(ly)?)\b", "unverifiable claim; describe the mechanism or cite data"),
    ("en-may", "info", r"\bmay\b", "use 'can' (ability/permission) or 'might' (possibility)"),
    ("en-hang", "info", r"\bhang(s|ing)?\b", "use 'stops responding'"),
    ("en-exclaim", "warn", r"\w!(?=\s|$)", "avoid exclamation marks"),
    ("en-ellipsis", "info", "…", "use three periods only where required; avoid the ellipsis character"),
    ("en-ampersand", "warn", r"\s&\s", "write 'and'"),
]
ZH_RULES = [
    ("zh-trivial", "warn", r"(只需|简单地|轻松|很容易|轻而易举|马上就能)", "让任务显得轻松的措辞，删除"),
    ("zh-please-note", "warn", r"(请注意|需要注意的是)", "删除，直接陈述；必要时改用提示框"),
    ("zh-timeless", "warn", r"(目前|现阶段|最新|即将|敬请期待)", "会过时的措辞，删除或写明版本号/日期"),
    ("zh-directional", "warn", r"(如上所示|上面|下面|上方|下方|左侧|右侧)", "方向性措辞，改用“前面的/以下”或写出元素名称"),
    ("zh-inclusive", "error", r"(白名单|黑名单)", "改用“允许名单/拒绝名单”"),
    ("zh-we", "info", r"我们", "用“你/您”称呼读者"),
    ("zh-etc", "info", r"(等等|之类)", "列全，或用“包括……”引出"),
    ("zh-wordy", "info", r"进行(设置|安装|配置|部署|操作|修改|删除|创建)", "去掉“进行”"),
    ("zh-exclaim", "warn", r"！", "不用感叹号"),
    ("zh-claims", "warn", r"(最好的|最快的|保证|绝对安全|无缝)", "无法验证的断言，描述机制或给出数据"),
    ("zh-repeat-punct", "warn", r"[！？。，]{2,}", "不重复使用标点"),
    ("zh-fullwidth-digit", "warn", r"[０-９]", "数字用半角"),
]
LINK_TEXT_BAD = {"here", "click here", "this", "this page", "this link", "link", "read more", "more",
                 "这里", "此处", "点击这里", "点此", "这个链接", "链接", "详情"}
GERUND_OK = {"billing", "pricing", "logging", "monitoring", "networking", "troubleshooting", "contributing", "breaking"}
PLACEHOLDER_LANGS = {"", "sh", "bash", "shell", "console", "zsh", "text", "none", "yaml", "yml", "json",
                     "ini", "toml", "env", "properties", "powershell", "cmd", "bat"}

RE_FENCE = re.compile(r"^\s*(```+|~~~+)\s*([\w+-]*)")
RE_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
RE_INLINE_CODE = re.compile(r"`+[^`\n]*`+")
RE_LINK = re.compile(r"!?\[([^\]]*)\]\(([^)\s]*)(?:\s+\"[^\"]*\")?\)")
RE_URL = re.compile(r"<?https?://[^\s>)]+>?")
RE_HTML = re.compile(r"</?[a-zA-Z][^>]*>")
RE_ANGLE_PH = re.compile(r"<[a-z][a-z0-9_-]*>")
RE_POSSESSIVE_PH = re.compile(r"\b(YOUR|MY)_[A-Z0-9_]+\b")
RE_XXX = re.compile(r"\b[xX]{3,}\b")
RE_DATE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")
RE_BOLD_UNDERSCORE = re.compile(r"(?<![\w_])__[^_\n]+__(?![\w_])")
RE_ZH_SPACE = re.compile(f"[{CJK}][A-Za-z0-9]|[A-Za-z0-9][{CJK}]")
RE_ZH_HALF_PUNCT = re.compile(f"[{CJK}][,;:!?]|[{CJK}]\\.(?=\\s|$)")


def blank(m):
    return " " * len(m.group(0))


def to_prose(line):
    """Blank inline code, URLs, link targets and HTML tags so word rules never fire on them."""
    line = RE_INLINE_CODE.sub(blank, line)
    line = RE_LINK.sub(lambda m: m.group(0)[: m.start(2) - m.start(0)] + " " * len(m.group(2))
                       + m.group(0)[m.end(2) - m.start(0):], line)
    line = RE_URL.sub(blank, line)
    return RE_HTML.sub(blank, line)


def to_spacing(line):
    """For CJK spacing: treat inline code as Latin text (it needs spaces too), drop URLs and tags."""
    line = RE_INLINE_CODE.sub(lambda m: "X" * len(m.group(0)), line)
    line = RE_LINK.sub(lambda m: m.group(0)[: m.start(2) - m.start(0)] + " " * len(m.group(2))
                       + m.group(0)[m.end(2) - m.start(0):], line)
    line = RE_URL.sub(blank, line)
    return RE_HTML.sub(blank, line)


def detect_lang(text):
    cjk = len(RE_CJK.findall(text))
    latin = len(re.findall(r"[A-Za-z]", text))
    return "zh" if cjk and cjk / (cjk + latin / 5 + 1) > 0.3 else "en"


class Linter:
    def __init__(self, path, lang):
        self.path, self.lang, self.findings = str(path), lang, []

    def add(self, line_no, col, sev, rule, msg, excerpt):
        self.findings.append({"path": self.path, "line": line_no, "col": col + 1, "severity": sev,
                              "rule": rule, "message": msg, "excerpt": excerpt.strip()[:80]})

    def run_rules(self, rules, n, prose, raw):
        for rule, sev, pat, msg in rules:
            for m in re.finditer(pat, prose, re.IGNORECASE):
                self.add(n, m.start(), sev, rule, msg, raw[max(0, m.start() - 20): m.end() + 20])

    def check_placeholders(self, n, text, raw, offset=0):
        for rx, rule, sev, msg in (
            (RE_ANGLE_PH, "placeholder-angle", "warn", "use UPPER_SNAKE_CASE placeholders, not <angle-brackets>"),
            (RE_POSSESSIVE_PH, "placeholder-possessive", "warn", "drop YOUR_/MY_ from placeholder names"),
            (RE_XXX, "placeholder-xxx", "info", "use a descriptive placeholder name instead of xxx"),
        ):
            for m in rx.finditer(text):
                at = offset + m.start()
                self.add(n, at, sev, rule, msg, raw[max(0, at - 20): offset + m.end() + 20])

    def check_heading(self, n, level, text, raw, state):
        if level == 1:
            state["h1"] += 1
            if state["h1"] == 2:
                self.add(n, 0, "warn", "heading-h1", "use only one level-1 heading per page", raw)
        if state["last_level"] and level > state["last_level"] + 1:
            self.add(n, 0, "warn", "heading-skip", f"heading level jumps from h{state['last_level']} to h{level}", raw)
        state["last_level"] = level
        plain = to_prose(text).strip()
        if RE_LINK.search(text):
            self.add(n, 0, "warn", "heading-link", "don't put links in headings", raw)
        if re.search(r"[.:;!。：；！，,]$", plain):
            self.add(n, len(raw) - 1, "warn", "heading-punct", "don't end headings with punctuation", raw)
        if self.lang == "en":
            words = re.findall(r"[A-Za-z][\w'-]*", plain)
            if words and words[0].lower().endswith("ing") and words[0].lower() not in GERUND_OK:
                self.add(n, 0, "info", "heading-gerund", "start task headings with a bare verb, not an -ing word", raw)
            rest = [w for w in words[1:] if len(w) > 3 and not w.isupper()]
            caps = [w for w in rest if w[0].isupper()]
            if len(caps) >= 2 and len(caps) / max(len(rest), 1) >= 0.6:
                self.add(n, 0, "info", "heading-case", "looks like Title Case; use sentence case (keep product names)", raw)

    def lint(self, text):
        lines = text.splitlines()
        state = {"h1": 0, "last_level": 0}
        in_fence, fence_mark, fence_lang = False, "", ""
        in_comment = False
        prev_heading = None  # line number of a heading not yet followed by content
        start = 0
        if lines and lines[0].strip() == "---":  # front matter
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    start = i + 1
                    break
        for idx in range(start, len(lines)):
            n, raw = idx + 1, lines[idx]
            fm = RE_FENCE.match(raw)
            if in_fence:
                if fm and fm.group(1)[0] == fence_mark[0] and len(fm.group(1)) >= len(fence_mark) and not fm.group(2):
                    in_fence = False
                elif fence_lang in PLACEHOLDER_LANGS:
                    self.check_placeholders(n, raw, raw)
                continue
            if fm:
                in_fence, fence_mark, fence_lang = True, fm.group(1), fm.group(2).lower()
                if not fence_lang:
                    self.add(n, 0, "info", "code-lang", "add a language to the code fence", raw)
                prev_heading = None
                continue
            if in_comment or raw.lstrip().startswith("<!--"):
                in_comment = "-->" not in raw
                continue
            if not raw.strip():
                continue

            hm = RE_HEADING.match(raw)
            if hm:
                if prev_heading:
                    self.add(prev_heading[0], 0, "info", "heading-empty", "heading has no content before the next heading", prev_heading[1])
                prev_heading = (n, raw)
                self.check_heading(n, len(hm.group(1)), hm.group(2), raw, state)
            else:
                prev_heading = None

            prose = to_prose(raw)
            for code in RE_INLINE_CODE.finditer(raw):
                self.check_placeholders(n, code.group(0), raw, code.start())
            for m in RE_LINK.finditer(raw):
                label = re.sub(r"[*_`]", "", m.group(1)).strip().lower()
                if not m.group(0).startswith("!") and (label in LINK_TEXT_BAD or RE_URL.fullmatch(label)):
                    self.add(n, m.start(), "warn", "link-text", "use descriptive link text (the page title or a short phrase)", m.group(0))
                if m.group(0).startswith("![") and not m.group(1).strip():
                    self.add(n, m.start(), "warn", "image-alt", "add alt text to the image", m.group(0))
            for m in RE_DATE.finditer(prose):
                self.add(n, m.start(), "warn", "date-ambiguous", "use an unambiguous date such as 2026-10-23", m.group(0))
            for m in RE_BOLD_UNDERSCORE.finditer(prose):
                self.add(n, m.start(), "info", "md-bold", "use ** for bold in Markdown", m.group(0))

            has_cjk = bool(RE_CJK.search(raw))
            if self.lang == "zh" or has_cjk:
                self.run_rules(ZH_RULES, n, prose, raw)
                spacing = to_spacing(raw)
                bad = list(RE_ZH_SPACE.finditer(spacing))
                if bad:
                    self.add(n, bad[0].start(), "info", "zh-space", f"中文与英文/数字之间加空格（本行 {len(bad)} 处）",
                             raw[max(0, bad[0].start() - 10): bad[0].end() + 10])
                for m in RE_ZH_HALF_PUNCT.finditer(prose):
                    self.add(n, m.start() + 1, "warn", "zh-punct", "中文句子中使用全角标点", raw[max(0, m.start() - 10): m.end() + 5])
                # inclusive terms in English still apply inside Chinese docs
                self.run_rules([r for r in EN_RULES if r[0] in ("en-inclusive", "en-latin")], n, prose, raw)
            if self.lang == "en":
                self.run_rules(EN_RULES, n, prose, raw)
                if not hm and not raw.lstrip().startswith("|"):
                    for s in re.split(r"(?<=[.?!])\s+", prose.strip()):
                        words = re.findall(r"[A-Za-z0-9][\w'-]*", s)
                        if len(words) > 26:
                            self.add(n, 0, "info", "sentence-length", f"sentence has {len(words)} words; aim for 26 or fewer", s)
        return self.findings


def iter_files(paths):
    for p in map(Path, paths):
        if p.is_dir():
            yield from sorted(p.rglob("*.md"))
        else:
            yield p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--lang", choices=["auto", "en", "zh"], default="auto")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--min-severity", choices=list(SEVERITIES), default="info")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any warn or error is found")
    a = ap.parse_args()

    findings = []
    for f in iter_files(a.paths):
        text = f.read_text(encoding="utf-8", errors="replace")
        lang = detect_lang(text) if a.lang == "auto" else a.lang
        findings += Linter(f, lang).lint(text)
    findings = [x for x in findings if SEVERITIES[x["severity"]] >= SEVERITIES[a.min_severity]]
    findings.sort(key=lambda x: (x["path"], x["line"], x["col"]))

    if a.format == "json":
        json.dump(findings, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        for x in findings:
            print(f"{x['path']}:{x['line']}:{x['col']}: {x['severity']}: [{x['rule']}] {x['message']} | {x['excerpt']}")
        counts = {s: sum(1 for x in findings if x["severity"] == s) for s in SEVERITIES}
        print(f"\n{len(findings)} findings: {counts['error']} error, {counts['warn']} warn, {counts['info']} info", file=sys.stderr)
    if a.strict and any(SEVERITIES[x["severity"]] >= 1 for x in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
