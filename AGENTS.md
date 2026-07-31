# Agent toolkit contribution instructions

This repository publishes shared Agent Skills for Enonic products. Version 0.5.0 contains the self-contained `plugins/enonic/` package for
Claude Code and Codex, with the same skill directories installable by GitHub Copilot and Gemini CLI.

## Plugin structure

- Keep canonical skill content under `plugins/enonic/skills/`; do not duplicate skills per client.
- Keep both plugin manifests inside `plugins/enonic/` and both marketplace registries synchronized.
- The plugin name is `enonic`, the marketplace name is `enonic-agent-toolkit`, and repository links use
  `https://github.com/enonic/agent-toolkit`.
- Bump the Claude marketplace and both plugin manifest versions together.
- Keep licensing in the repository-level `LICENSE` file rather than duplicating license metadata across packaged files.
- Do not add empty future plugins. Group future skills by capability rather than client.

## Portable skill writing

- Follow the [Agent Skills specification](https://agentskills.io/specification).
- Use generic actions such as read, search, edit, run, and ask. Do not name a client-specific tool as an imperative.
- Do not add client compatibility declarations or automatic tool approvals to shared skill frontmatter. Each client retains its normal
  permission prompts.
- Keep every `SKILL.md` entry point below 500 lines. Move detailed material to directly referenced files in the skill's `references/`
  directory.
- Keep relative references within the self-contained skill directory.

## Validation

Install the exact versions in `requirements-dev.txt` and `package-lock.json`, then run:

```sh
PATH="$PWD/.venv/bin:$PATH" CLAUDE_BIN="$PWD/node_modules/.bin/claude" npm run validate
CODEX_BIN="$PWD/node_modules/.bin/codex" npm run validate:codex
npm run validate:copilot
GEMINI_BIN="$PWD/node_modules/.bin/gemini" npm run validate:gemini
```

These checks validate all three skills, the strict Claude marketplace, installation and discovery in Codex, GitHub Copilot, and Gemini
CLI, manifest consistency, relative references, local documentation links, stale naming, entry-point size, and portability and permission
policies.

Releases are created only through the manually dispatched release workflow on `master`. Do not manually tag or publish from a feature
branch.
