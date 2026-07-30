#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

skills_validator=""
if command -v skills-ref >/dev/null 2>&1; then
  skills_validator="skills-ref"
elif command -v agentskills >/dev/null 2>&1; then
  skills_validator="agentskills"
else
  echo "Install requirements-dev.txt before validating." >&2
  exit 1
fi

for skill in plugins/xp/skills/*; do
  "$skills_validator" validate "$skill"
done

claude_bin="${CLAUDE_BIN:-claude}"
"$claude_bin" plugin validate --strict .
python3 scripts/validate_repo.py
