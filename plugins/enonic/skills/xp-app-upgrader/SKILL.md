---
name: xp-app-upgrader
description: >
  Upgrade Enonic applications from XP 7 to XP 8 or between XP 8 releases.
  Use for version-specific upgrade planning, descriptor and build migration,
  API changes, partial xp8migrator runs, and post-upgrade deployment errors.
  Skip brand-new applications and upgrades between XP 7.x minor versions.
metadata:
  author: enonic
  xp-version: "7.x → 8.x; 8.x → later 8.x"
---

# Upgrade an Enonic application

## Find the applicable documentation first

Determine the application's current XP version and requested target from the project and the user's instructions. Before planning edits,
read the main upgrade page in `stable`, then select the relevant guide and release sections. Use `next` only when the developer explicitly
instructs you to use that documentation channel.
Respect an explicit target; if none was given, resolve a published stable XP 8 target before selecting the notes.

| What to look for | Default: stable documentation | Only when explicitly instructed: next documentation |
|---|---|---|
| Upgrade entry point and changes between XP 8 releases | <https://developer.enonic.com/docs/code/stable/upgrade> | <https://developer.enonic.com/docs/code/next/upgrade> |
| XP 7 → XP 8.0 baseline migration | <https://developer.enonic.com/docs/code/stable/upgrade/xp7> | <https://developer.enonic.com/docs/code/next/upgrade/xp7> |

Use `stable` by default. An upcoming target version or missing notes in `stable` does not authorize switching to `next`; report the
documentation gap and continue only with guidance supported by `stable`, unless the developer explicitly instructs you to use `next`.
Check the version headings: these channels move over time. A version shown in `next` is not proof that
its runtime, Gradle plugins, libraries, or type packages have been published; verify those separately before pinning dependencies.
If the selected page is unavailable or lacks notes for the target, report the gap rather than inventing changes or silently using another
release's guidance.

- **XP 7 → XP 8.0:** read the dedicated `/upgrade/xp7` guide.
- **XP 8 → later XP 8:** read the sections after the current version through the target, in version order. Do not run the XP 7 migrator.
- **XP 7 → later XP 8:** read the XP 7 guide and all subsequent release sections through the target before planning. Apply the relevant
  changes together and build directly for the target; no intermediate XP 8.0 deployment is required.

The version-appropriate official documentation is the authority for technical changes. Local references provide workflow and examples;
they do not replace reading the applicable release notes. If they disagree, verify the relevant official API/schema documentation or
source at the target release tag, and explain the discrepancy. Do not resolve it using an unrelated `master` branch.

Classify applicable notes as required changes, requirements conditional on features or runtime choices, and optional modernization.
Check the application's code and dependencies, including Java sources when present. Do not assume every XP 8 upgrade is only a version
bump or that every later-release change is optional. Include required and applicable conditional changes in the plan before execution;
offer optional deprecation clean-ups separately unless already requested.

## Choose the workflow

For an application coming from **XP 7**, read `references/upgrade-workflow.md` completely before executing changes. Follow its detect,
inventory, plan, execute, validate, cleanup, and deploy phases, incorporating the selected release notes during inventory and planning.
Use these supporting references when needed, checking their examples against the target documentation:

- `references/examples.md` for dependency aliases, worked Gradle examples, and TypeScript wiring.
- `references/manual-schemes-migration.md` for descriptor transformations when reviewing migrator output or migrating manually.

For an application already on **XP 8**:

1. Inventory the code, build settings, dependencies, and type packages affected by the applicable release notes. Present the target,
   documentation links, and proposed changes, respecting the user's existing authorization.
2. Update `xpVersion`, compatible dependencies and `@enonic-types/*` packages, and applicable code/configuration. Preserve the existing
   XP 8 descriptors and build structure unless the notes require changes.
3. Consult the `enonic-cli` skill before running any `enonic` command. Build with `enonic project build -f` and run the project's relevant
   checks. Diagnose and fix failures within the agreed scope.
4. If deployment is requested, use an explicitly selected sandbox running the target XP version and settle whether it should start.
   Validate affected behavior there; report build results separately from runtime verification and identify anything not verified.

Application upgrade notes live under `/docs/code/`. Instance configuration and content-data migration are separate work: consult
<https://developer.enonic.com/docs/platform/stable/upgrade/xp7> when that work is requested. Use `xp-app-debugger` for build/runtime error
diagnosis rather than treating every error as another migration step.
