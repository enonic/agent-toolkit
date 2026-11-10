#!/usr/bin/env python3
"""Validate repository invariants shared by local checks and CI."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = ROOT / "plugins"
VERSION = "0.6.0"
REPOSITORY = "https://github.com/enonic/agent-toolkit"
PLUGINS = {
    "enonic": {"enonic-cli", "xp-app-debugger", "xp-app-upgrader"},
    "enonic-contrib": {"enonic-docs"},
}
STALE_NAMES = (
    "ai-enonic-" + "marketplace",
    "enonic-" + "marketplace",
    "enonic-" + "skills",
)
STALE_ALLOWED = {"MIGRATION.md"}
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

if claude_market.get("name") != "enonic-agent-toolkit":
    errors.append("Claude marketplace name must be enonic-agent-toolkit")
if codex_market.get("name") != "enonic-agent-toolkit":
    errors.append("Codex marketplace name must be enonic-agent-toolkit")

actual_plugins = {path.name for path in PLUGINS_DIR.iterdir() if path.is_dir()}
if actual_plugins != set(PLUGINS):
    errors.append(f"Expected plugins {sorted(PLUGINS)}, found {sorted(actual_plugins)}")

claude_entries = {entry.get("name"): entry for entry in claude_market.get("plugins", [])}
if set(claude_entries) != set(PLUGINS):
    errors.append(f"Claude marketplace must list exactly {sorted(PLUGINS)}")
codex_entries = {entry.get("name"): entry for entry in codex_market.get("plugins", [])}
if set(codex_entries) != set(PLUGINS):
    errors.append(f"Codex marketplace must list exactly {sorted(PLUGINS)}")

for plugin_name, skill_names in PLUGINS.items():
    plugin = PLUGINS_DIR / plugin_name
    claude_plugin = load_json(plugin / ".claude-plugin" / "plugin.json")
    codex_plugin = load_json(plugin / ".codex-plugin" / "plugin.json")

    for label, manifest in (("Claude", claude_plugin), ("Codex", codex_plugin)):
        if manifest.get("name") != plugin_name:
            errors.append(f"{label} plugin name must be {plugin_name}")
        if manifest.get("version") != VERSION:
            errors.append(f"{label} plugin {plugin_name} version must be {VERSION}")
        if manifest.get("repository") != REPOSITORY:
            errors.append(f"{label} plugin {plugin_name} repository must be {REPOSITORY}")
        if manifest.get("skills") not in ("./skills", "./skills/"):
            errors.append(f"{label} plugin {plugin_name} must use its packaged ./skills directory")

    entry = claude_entries.get(plugin_name, {})
    expected = {"source": f"./plugins/{plugin_name}", "version": VERSION}
    for key, value in expected.items():
        if entry.get(key) != value:
            errors.append(f"Claude marketplace plugin {plugin_name} {key} must be {value}")

    entry = codex_entries.get(plugin_name, {})
    if entry.get("source") != {"source": "local", "path": f"./plugins/{plugin_name}"}:
        errors.append(f"Codex marketplace source for {plugin_name} must be local ./plugins/{plugin_name}")
    if entry.get("policy") != {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    }:
        errors.append(f"Codex marketplace policy for {plugin_name} must be AVAILABLE/ON_INSTALL")
    if entry.get("category") != "Productivity":
        errors.append(f"Codex marketplace category for {plugin_name} must be Productivity")

    skills = plugin / "skills"
    actual_skills = {path.name for path in skills.iterdir() if path.is_dir()}
    if actual_skills != skill_names:
        errors.append(
            f"{plugin_name}: expected skills {sorted(skill_names)}, found {sorted(actual_skills)}"
        )

    for skill in sorted(skills.iterdir()):
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

all_skill_names = [name for names in PLUGINS.values() for name in names]
if len(all_skill_names) != len(set(all_skill_names)):
    errors.append("Skill names must be unique across plugins; flat installs share one namespace")

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
