# Migrating to v0.5.0

Version 0.5.0 is a pre-1.0 packaging break. The repository changes from `enonic/ai-enonic-marketplace` to
`enonic/agent-toolkit`, the marketplace changes from `enonic-marketplace` to `enonic-agent-toolkit`, and the plugin changes from
`enonic-skills` to `enonic`.

The scope is preserved: `enonic-cli`, `xp-app-debugger`, and `xp-app-upgrader` remain available. The new `enonic` package is shared by Claude
Code and Codex; GitHub Copilot and Gemini CLI can install the same canonical skill content natively.

## Who needs to migrate

- Claude Code users who added the old marketplace or installed its plugin.
- Codex users who installed individual skill directories directly.
- Automated setup that refers to the old repository, marketplace, plugin, or skill paths.

Fresh installations can follow [README.md](README.md#installation) without these removal steps.
GitHub Copilot and Gemini CLI support is new in v0.5.0 and requires no migration.

## Claude Code

Removing `enonic-marketplace` also removes the plugin installed from it:

```text
/plugin marketplace remove enonic-marketplace
/plugin marketplace add enonic/agent-toolkit
/plugin install enonic@enonic-agent-toolkit
/reload-plugins
```

If necessary, explicitly uninstall the old plugin first with `/plugin uninstall enonic-skills@enonic-marketplace`.

To roll back, remove `enonic-agent-toolkit`, add `enonic/ai-enonic-marketplace`, reinstall
`enonic-skills@enonic-marketplace`, and reload plugins.

## Codex

Move any directly installed `enonic-cli`, `xp-app-debugger`, and `xp-app-upgrader` directories to a recoverable backup location outside
the skills search path. Do not delete the backup until the native plugin is verified. Then install:

```text
codex plugin marketplace add enonic/agent-toolkit
codex plugin add enonic@enonic-agent-toolkit
```

Start a new thread so Codex discovers the plugin skills.

To roll back, remove the `enonic` plugin and renamed marketplace, restore the backed-up skill directories, and start another new thread.

## GitHub Copilot and Gemini CLI

Support for both clients is new in v0.5.0. Before v0.5.0 only Claude Code and Codex were supported, so there is no previous installation
to migrate; install directly per [README.md](README.md#installation).

## Verify

In a new session or thread, confirm that `enonic-cli`, `xp-app-debugger`, and `xp-app-upgrader` are discoverable. Claude Code and Codex
should report them from `enonic@enonic-agent-toolkit`; Copilot and Gemini install them as native skills. If one is missing, reload or restart
the client and begin another new session.

No legacy alias or aggregate `all` plugin is retained. v0.5.0 installs only `enonic`.
