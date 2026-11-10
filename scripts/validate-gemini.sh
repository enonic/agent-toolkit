#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
gemini_bin="${GEMINI_BIN:-gemini}"
test_root="$(mktemp -d)"
trap 'rm -rf "$test_root"' EXIT

export HOME="$test_root/home"
mkdir -p "$HOME"

expected_count=0
for plugin_dir in "$repo_root"/plugins/*; do
  "$gemini_bin" skills install "$plugin_dir/skills" \
    --scope user \
    --consent
  for skill_dir in "$plugin_dir"/skills/*; do
    expected_count=$((expected_count + 1))
  done
done

skill_list="$("$gemini_bin" skills list)"
for skill_dir in "$repo_root"/plugins/*/skills/*; do
  skill="$(basename "$skill_dir")"
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
if [[ "$installed_count" != "$expected_count" ]]; then
  echo "Expected exactly $expected_count Gemini skills, found $installed_count" >&2
  exit 1
fi

echo "Gemini CLI discovered, installed, and enabled all $expected_count skills."
