#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
codex_bin="${CODEX_BIN:-codex}"
test_root="$(mktemp -d)"
trap 'rm -rf "$test_root"' EXIT

export CODEX_HOME="$test_root/codex-home"
mkdir -p "$CODEX_HOME"

"$codex_bin" plugin marketplace add "$repo_root" --json
"$codex_bin" plugin add enonic@enonic-agent-toolkit --json

for skill in enonic-cli xp-app-debugger xp-app-upgrader; do
  if ! find "$CODEX_HOME" -path "*/skills/$skill/SKILL.md" -print -quit | grep -q .; then
    echo "Codex installation did not discover $skill" >&2
    exit 1
  fi
done

echo "Codex installed enonic and discovered all three skills."
