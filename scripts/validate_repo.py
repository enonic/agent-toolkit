#!/usr/bin/env python3
"""Validate repository invariants shared by local checks and CI."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "xp"
SKILLS = PLUGIN / "skills"
VERSION = "0.5.0"
REPOSITORY = "https://github.com/enonic/agent-toolkit"
SKILL_NAMES = {"enonic-cli", "xp-app-debugger", "xp-app-upgrader"}
STALE_NAMES = (
    "ai-enonic-" + "marketplace",
    "enonic-" + "marketplace",
    "enonic-" + "skills",
)
STALE_ALLOWED = {"CHANGELOG.md", "MIGRATION.md"}
CLIENT_WORDING = re.compile(
    r"compatibility:\s*.*(?:Claude|Codex)|"
    r"\b(?:Claude Code|Codex)\b|AskUserQuestion|run_in_background|"
    r"\b(?:Bash|Read|Write|Edit|Grep|Glob|WebFetch) tool\b"
)

errors: list[str] = []


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: {exc}")
        return {}


claude_market = load_json(ROOT / ".claude-plugin" / "marketplace.json")
codex_market = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
claude_plugin = load_json(PLUGIN / ".claude-plugin" / "plugin.json")
codex_plugin = load_json(PLUGIN / ".codex-plugin" / "plugin.json")

if claude_market.get("name") != "enonic-agent-toolkit":
    errors.append("Claude marketplace name must be enonic-agent-toolkit")
if codex_market.get("name") != "enonic-agent-toolkit":
    errors.append("Codex marketplace name must be enonic-agent-toolkit")

for label, manifest in (("Claude", claude_plugin), ("Codex", codex_plugin)):
    if manifest.get("name") != "xp":
        errors.append(f"{label} plugin name must be xp")
    if manifest.get("version") != VERSION:
        errors.append(f"{label} plugin version must be {VERSION}")
    if manifest.get("repository") != REPOSITORY:
        errors.append(f"{label} plugin repository must be {REPOSITORY}")
    if manifest.get("skills") not in ("./skills", "./skills/"):
        errors.append(f"{label} plugin must use its packaged ./skills directory")

claude_entries = claude_market.get("plugins", [])
if len(claude_entries) != 1:
    errors.append("Claude marketplace must contain exactly one plugin")
else:
    entry = claude_entries[0]
    expected = {"name": "xp", "source": "./plugins/xp", "version": VERSION}
    for key, value in expected.items():
        if entry.get(key) != value:
            errors.append(f"Claude marketplace plugin {key} must be {value}")

codex_entries = codex_market.get("plugins", [])
if len(codex_entries) != 1:
    errors.append("Codex marketplace must contain exactly one plugin")
else:
    entry = codex_entries[0]
    if entry.get("name") != "xp":
        errors.append("Codex marketplace plugin name must be xp")
    if entry.get("source") != {"source": "local", "path": "./plugins/xp"}:
        errors.append("Codex marketplace source must be local ./plugins/xp")
    if entry.get("policy") != {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    }:
        errors.append("Codex marketplace policy must be AVAILABLE/ON_INSTALL")
    if entry.get("category") != "Productivity":
        errors.append("Codex marketplace category must be Productivity")

actual_skills = {path.name for path in SKILLS.iterdir() if path.is_dir()}
if actual_skills != SKILL_NAMES:
    errors.append(f"Expected skills {sorted(SKILL_NAMES)}, found {sorted(actual_skills)}")

for skill in sorted(SKILLS.iterdir()):
    if not skill.is_dir():
        continue
    entry_point = skill / "SKILL.md"
    if not entry_point.is_file():
        errors.append(f"{skill.relative_to(ROOT)} has no SKILL.md")
        continue
    line_count = len(entry_point.read_text().splitlines())
    if line_count >= 500:
        errors.append(f"{entry_point.relative_to(ROOT)} has {line_count} lines (must be below 500)")

    for markdown in skill.rglob("*.md"):
        text = markdown.read_text()
        match = CLIENT_WORDING.search(text)
        if match:
            errors.append(
                f"{markdown.relative_to(ROOT)} contains client-specific wording: {match.group(0)!r}"
            )
        for reference in re.findall(r"`(references/[A-Za-z0-9._/-]+\.md)`", text):
            target = skill / reference
            if not target.is_file():
                errors.append(
                    f"{markdown.relative_to(ROOT)} references missing {reference}"
                )

for path in ROOT.rglob("*"):
    if not path.is_file() or any(part in {".git", "node_modules", ".venv"} for part in path.parts):
        continue
    relative = path.relative_to(ROOT)
    if relative.name in STALE_ALLOWED:
        continue
    try:
        text = path.read_text()
    except UnicodeDecodeError:
        continue
    for stale in STALE_NAMES:
        if stale in text:
            errors.append(f"{relative} contains stale name {stale!r}")

for markdown in (ROOT / "README.md", ROOT / "AGENTS.md", ROOT / "MIGRATION.md"):
    if not markdown.exists():
        continue
    text = markdown.read_text()
    for target_text in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        if re.match(r"^(?:https?://|mailto:|#)", target_text):
            continue
        target = target_text.split("#", 1)[0]
        if target and not (markdown.parent / target).resolve().exists():
            errors.append(f"{markdown.relative_to(ROOT)} links to missing {target}")

if errors:
    print("Repository validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print("Repository invariants passed.")
