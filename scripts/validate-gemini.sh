#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
gemini_bin="${GEMINI_BIN:-gemini}"
test_root="$(mktemp -d)"
trap 'rm -rf "$test_root"' EXIT

export HOME="$test_root/home"
mkdir -p "$HOME"

"$gemini_bin" skills install "$repo_root/plugins/enonic/skills" \
  --scope user \
  --consent

skill_list="$("$gemini_bin" skills list)"
for skill in enonic-cli xp-app-debugger xp-app-upgrader; do
  if [[ ! -f "$HOME/.gemini/skills/$skill/SKILL.md" ]]; then
    echo "Gemini CLI installation did not discover $skill" >&2
    exit 1
  fi
  if ! grep -q "^$skill \\[Enabled\\]$" <<<"$skill_list"; then
    echo "Gemini CLI did not enable $skill" >&2
    exit 1
  fi
done

installed_count="$(find "$HOME/.gemini/skills" -name SKILL.md | wc -l | tr -d ' ')"
if [[ "$installed_count" != "3" ]]; then
  echo "Expected exactly three Gemini skills, found $installed_count" >&2
  exit 1
fi

echo "Gemini CLI discovered, installed, and enabled all three skills."
