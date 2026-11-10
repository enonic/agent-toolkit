# Enonic Agent Toolkit

Shared [Agent Skills](https://agentskills.io/specification) for Enonic. Claude Code and Codex install them through plugins;
GitHub Copilot and Gemini CLI install the same canonical skill directories natively.

Version 0.6.0 provides two plugins, each delivering the same skills to all four supported clients.

**`enonic`** — for people building on Enonic XP:

| Skill | Purpose |
|---|---|
| [enonic-cli](plugins/enonic/skills/enonic-cli/) | Use the `enonic` command for projects, sandboxes, data, apps, cloud deployment, and server administration. |
| [xp-app-debugger](plugins/enonic/skills/xp-app-debugger/) | Diagnose Enonic XP build failures and server runtime errors. |
| [xp-app-upgrader](plugins/enonic/skills/xp-app-upgrader/) | Upgrade Enonic applications from XP 7 to XP 8 or between XP 8 releases using version-specific documentation. |

**`enonic-contrib`** — for people contributing to Enonic's own repositories:

| Skill | Purpose |
|---|---|
| [enonic-docs](plugins/enonic-contrib/skills/enonic-docs/) | Write and maintain Enonic reference documentation: AsciiDoc conventions, the docgen pipeline, `menu.json` and `versions.json`, and the library reference pattern. |

## Installation

### Claude Code

```text
/plugin marketplace add enonic/agent-toolkit
/plugin install enonic@enonic-agent-toolkit
/plugin install enonic-contrib@enonic-agent-toolkit
/reload-plugins
```

Install only the plugins you need; `enonic-contrib` is relevant when you work in Enonic's repositories.

### Codex

```text
codex plugin marketplace add enonic/agent-toolkit
codex plugin add enonic@enonic-agent-toolkit
codex plugin add enonic-contrib@enonic-agent-toolkit
```

Start a new thread so Codex discovers the plugin's skills.

### GitHub Copilot

GitHub CLI 2.90.0 or newer installs every skill from both plugins into Copilot's user scope:

```text
gh skill install enonic/agent-toolkit --all --agent github-copilot --scope user
```

Skills are installed by name without a plugin prefix, so the two plugins' skill names never overlap.

### Gemini CLI

Install each plugin's skills from its canonical skill directory. Review the displayed skills and approve the installation:

```text
gemini skills install https://github.com/enonic/agent-toolkit --path plugins/enonic/skills
gemini skills install https://github.com/enonic/agent-toolkit --path plugins/enonic-contrib/skills
```

Run `gemini skills list` to verify discovery.

Upgrading Claude Code or Codex from a version before 0.5.0 requires removing the old installation first; follow
[MIGRATION.md](MIGRATION.md) for recoverable, client-specific steps.

## Repository layout

```text
.claude-plugin/marketplace.json       Claude Code marketplace
.agents/plugins/marketplace.json      Codex marketplace
plugins/
  enonic/
    .claude-plugin/plugin.json        Claude Code plugin manifest
    .codex-plugin/plugin.json         Codex plugin manifest
    skills/                           Canonical shared skill content
  enonic-contrib/
    .claude-plugin/plugin.json        Claude Code plugin manifest
    .codex-plugin/plugin.json         Codex plugin manifest
    skills/                           Canonical shared skill content
```

Each plugin is self-contained because plugin clients may cache only the selected package directory. Both of a plugin's manifests point to
the same `skills/` directory inside its package. All plugins share one version number with the marketplace.

Developer-facing CMS skills belong in the foundational `enonic` plugin. Skills for people working on Enonic's own repositories (documentation,
conventions, release procedures) belong in `enonic-contrib`. A further plugin should be added only when it has a distinct audience and
substantive skills; there are no placeholder plugins or aggregate `all` plugin.

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
