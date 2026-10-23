#!/usr/bin/env bash
# Install or uninstall the skills in this repo for Claude Code and/or Codex as standalone skills.
#
#   Claude Code: ~/.claude/skills/<skill>   (override with CLAUDE_SKILLS_DIR)
#   Codex:       ~/.agents/skills/<skill>   (override with CODEX_SKILLS_DIR)
#
# Usage: scripts/install.sh [--agent claude|codex|all] [--plugin NAME]... [--copy] [--uninstall] [--dry-run]
#   --agent      target agent (default: all)
#   --plugin     install only skills from this plugin (repeatable; default: all plugins)
#   --copy       copy instead of symlink (copies don't follow branch switches or git pull)
#   --uninstall  remove skills that this script installed from this repo
#   --dry-run    print actions without changing anything
#
# Existing entries that this repo didn't install are never touched.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
MARKER=".installed-from-sre-skills"
AGENT=all
PLUGINS=""
MODE=link
ACTION=install
DRY=0

die() { echo "error: $*" >&2; exit 2; }
run() { if [ "$DRY" = 1 ]; then echo "[dry-run] $*"; else "$@"; fi; }

while [ $# -gt 0 ]; do
  case "$1" in
    --agent) AGENT=${2:-}; shift 2 ;;
    --plugin) PLUGINS="$PLUGINS ${2:-}"; shift 2 ;;
    --copy) MODE=copy; shift ;;
    --uninstall) ACTION=uninstall; shift ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

case "$AGENT" in
  claude) TARGETS="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}" ;;
  codex) TARGETS="${CODEX_SKILLS_DIR:-$HOME/.agents/skills}" ;;
  all) TARGETS="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills} ${CODEX_SKILLS_DIR:-$HOME/.agents/skills}" ;;
  *) die "--agent must be claude, codex, or all" ;;
esac

[ -n "$PLUGINS" ] || PLUGINS=$(cd "$ROOT/plugins" && ls -d */ | tr -d /)
SKILLS=""
for p in $PLUGINS; do
  [ -d "$ROOT/plugins/$p/skills" ] || die "no such plugin: $p"
  for d in "$ROOT/plugins/$p/skills"/*/; do
    [ -f "$d/SKILL.md" ] && SKILLS="$SKILLS ${d%/}"
  done
done

# ours: a symlink into this repo, or a copy carrying our marker file
is_ours() {
  local dest=$1
  if [ -L "$dest" ]; then
    case "$(readlink "$dest")" in "$ROOT"/*) return 0 ;; esac
    return 1
  fi
  [ -f "$dest/$MARKER" ]
}

installed=0 skipped=0 removed=0
for target in $TARGETS; do
  [ "$ACTION" = install ] && run mkdir -p "$target"
  for src in $SKILLS; do
    name=$(basename "$src")
    dest="$target/$name"
    if [ "$ACTION" = uninstall ]; then
      if [ -e "$dest" ] || [ -L "$dest" ]; then
        if is_ours "$dest"; then run rm -rf "$dest"; removed=$((removed + 1)); fi
      fi
      continue
    fi
    if [ -e "$dest" ] || [ -L "$dest" ]; then
      if ! is_ours "$dest"; then
        echo "skip: $dest exists and was not installed from this repo" >&2
        skipped=$((skipped + 1)); continue
      fi
      run rm -rf "$dest"
    fi
    if [ "$MODE" = copy ]; then
      run cp -R "$src" "$dest"
      [ "$DRY" = 1 ] || echo "$ROOT" > "$dest/$MARKER"
    else
      run ln -s "$src" "$dest"
    fi
    installed=$((installed + 1))
  done
done

if [ "$ACTION" = uninstall ]; then
  echo "removed $removed skill(s) from: $TARGETS"
else
  echo "installed $installed skill(s) ($MODE) into: $TARGETS; skipped $skipped"
  echo "restart Claude Code / Codex if a running session doesn't pick them up"
fi
