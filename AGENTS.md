# Repository guide for coding agents

This repo contains Agent Skills that work in both Claude Code and Codex. Read this before you add or change a skill.

## Layout

```text
.claude-plugin/marketplace.json     Claude Code marketplace
.agents/plugins/marketplace.json    Codex marketplace
plugins/<plugin>/
  plugin.json                       portable manifest (Codex)
  .claude-plugin/plugin.json        Claude Code manifest
  skills/<skill>/
    SKILL.md                        frontmatter (name, description) + instructions
    agents/openai.yaml              Codex display metadata (Claude Code ignores it)
    references/  scripts/  assets/
  evals/<skill>/evals.json          at least 3 scenarios (sre-kernel, tech-docs)
scripts/validate_skills.py          run before every commit
scripts/install.sh                  install standalone skills for Claude Code and/or Codex
```

## Rules for skills

- Keep `SKILL.md` compatible with both agents:
  - frontmatter has only `name` (equal to the directory name) and `description`;
  - `description` is 400 characters or fewer, states what the skill does first, and contains `TRIGGER when:` and `DO NOT TRIGGER when:`. Codex shares a small budget (about 8,000 characters) across all skill descriptions.
- Write agent-neutral instructions. Don't name a specific agent or its tools, and refer to other skills by their bare name (`sre-incident-doc`), not a plugin-prefixed name.
- Write runnable script paths as `SKILL_DIR/scripts/...`. Both agents run commands from the user's working directory, not the skill directory.
- Each plugin has one shared-protocol skill (`sre-doc-standards`, `kernel-triage`, `tech-doc-style`). Other skills in the plugin link to it and don't redefine its rules.
- Keep `SKILL.md` under 500 lines. Move details into `references/`, linked one level deep from `SKILL.md`.
- Put deterministic work in `scripts/`: read-only by default, with timeouts, and portable across RHEL-family and Ubuntu.
- Keep manifest versions in `plugin.json` and `.claude-plugin/plugin.json` identical.

## Before you commit

```bash
python3 scripts/validate_skills.py
```

Fix every reported error. When you add a plugin, add it to both marketplace files and to `README.md`.
