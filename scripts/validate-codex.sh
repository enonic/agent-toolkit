#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
codex_bin="${CODEX_BIN:-codex}"
test_root="$(mktemp -d)"
trap 'rm -rf "$test_root"' EXIT

export CODEX_HOME="$test_root/codex-home"
mkdir -p "$CODEX_HOME"

"$codex_bin" plugin marketplace add "$repo_root" --json

for plugin in enonic enonic-contrib; do
  "$codex_bin" plugin add "$plugin@enonic-agent-toolkit" --json

  for skill_dir in "$repo_root/plugins/$plugin/skills"/*; do
    skill="$(basename "$skill_dir")"
    if ! find "$CODEX_HOME" -path "*/skills/$skill/SKILL.md" -print -quit | grep -q .; then
      echo "Codex installation did not discover $skill from $plugin" >&2
      exit 1
    fi
  done
done

echo "Codex installed both plugins and discovered all four skills."
