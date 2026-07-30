# Enonic Agent Toolkit

Shared [Agent Skills](https://agentskills.io/specification) for Enonic XP. Claude Code and Codex install them through the `xp` plugin;
GitHub Copilot and Gemini CLI install the same canonical skill directories natively.

Version 0.5.0 provides the same three skills to all four supported clients:

| Skill | Purpose |
|---|---|
| [enonic-cli](plugins/xp/skills/enonic-cli/) | Use the `enonic` command for projects, sandboxes, data, apps, cloud deployment, and server administration. |
| [xp-app-debugger](plugins/xp/skills/xp-app-debugger/) | Diagnose Enonic XP build failures and server runtime errors. |
| [xp-app-upgrader](plugins/xp/skills/xp-app-upgrader/) | Upgrade Enonic XP 7 applications to XP 8. |

## Installation

### Claude Code

```text
/plugin marketplace add enonic/agent-toolkit
/plugin install xp@enonic-agent-toolkit
/reload-plugins
```

### Codex

```text
codex plugin marketplace add enonic/agent-toolkit
codex plugin add xp@enonic-agent-toolkit
```

Start a new thread so Codex discovers the plugin's skills.

### GitHub Copilot

GitHub CLI 2.90.0 or newer installs all three skills into Copilot's user scope:

```text
gh skill install enonic/agent-toolkit --all --agent github-copilot --scope user
```

### Gemini CLI

Install all three skills from the repository's canonical skill directory. Review the displayed skills and approve the installation:

```text
gemini skills install https://github.com/enonic/agent-toolkit --path plugins/xp/skills
```

Run `gemini skills list` to verify discovery.

Upgrading Claude Code or Codex from a version before 0.5.0 requires removing the old installation first; follow
[MIGRATION.md](MIGRATION.md) for recoverable, client-specific steps.

## Repository layout

```text
.claude-plugin/marketplace.json       Claude Code marketplace
.agents/plugins/marketplace.json      Codex marketplace
plugins/
  xp/
    .claude-plugin/plugin.json        Claude Code plugin manifest
    .codex-plugin/plugin.json         Codex plugin manifest
    skills/                           Canonical shared skill content
```

The plugin is self-contained because plugin clients may cache only the selected package directory. Both manifests point to the same
`plugins/xp/skills/` directory inside the package.

Developer-facing CMS skills belong in the foundational `xp` plugin. A future `cloud` or other capability-based plugin should be added only
when it has a distinct audience and substantive skills; there are no placeholder plugins or aggregate `all` plugin.

## Development

Install the pinned validation dependencies:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --requirement requirements-dev.txt
npm ci
```

Run repository, Agent Skills, and Claude Code checks, then test installation for every supported client:

```sh
PATH="$PWD/.venv/bin:$PATH" CLAUDE_BIN="$PWD/node_modules/.bin/claude" npm run validate
CODEX_BIN="$PWD/node_modules/.bin/codex" npm run validate:codex
npm run validate:copilot
GEMINI_BIN="$PWD/node_modules/.bin/gemini" npm run validate:gemini
```

Pull requests run all checks in GitHub Actions. The manual release workflow accepts an exact version only on `master`, reruns every
check, verifies all manifest versions and the tag's absence, and then creates the tag and GitHub release.

## License

[Apache License 2.0](LICENSE)
