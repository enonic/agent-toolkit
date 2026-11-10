#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
gh_bin="${GH_BIN:-gh}"
test_root="$(mktemp -d)"
trap 'rm -rf "$test_root"' EXIT

export HOME="$test_root/home"
mkdir -p "$HOME"

if ! "$gh_bin" skill --help >/dev/null 2>&1; then
  echo "GitHub CLI 2.90.0 or newer with gh skill support is required." >&2
  exit 1
fi

expected_count=0
for skill_dir in "$repo_root"/plugins/*/skills/*; do
  skill="$(basename "$skill_dir")"
  "$gh_bin" skill install "$skill_dir" \
    --from-local \
    --all \
    --agent github-copilot \
    --scope user

  if [[ ! -f "$HOME/.copilot/skills/$skill/SKILL.md" ]]; then
    echo "GitHub Copilot installation did not discover $skill" >&2
    exit 1
  fi
  expected_count=$((expected_count + 1))
done

installed_count="$(find "$HOME/.copilot/skills" -name SKILL.md | wc -l | tr -d ' ')"
if [[ "$installed_count" != "$expected_count" ]]; then
  echo "Expected exactly $expected_count Copilot skills, found $installed_count" >&2
  exit 1
fi

echo "GitHub Copilot discovered and installed all $expected_count skills."
