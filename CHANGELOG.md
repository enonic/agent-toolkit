# Changelog

## 0.5.0

- Renamed `enonic/ai-enonic-marketplace` to `enonic/agent-toolkit`.
- Renamed `enonic-marketplace` to `enonic-agent-toolkit`.
- Replaced `enonic-skills` with one self-contained `xp` plugin for Claude Code and Codex.
- Added native installation and discovery support for GitHub Copilot and Gemini CLI.
- Made all three skills identical and portable across all four supported clients.
- Removed client compatibility metadata and implicit tool approvals.
- Changed the project license from MIT to Apache License 2.0.
- Added cross-client validation, installation smoke tests for Codex, GitHub Copilot, and Gemini CLI, and manual release automation.
- Added [MIGRATION.md](MIGRATION.md) for the breaking installation change.

This version is prepared by the current pull request. It is not tagged or released until the manual release workflow is dispatched after
merge.
