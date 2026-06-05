---
name: xp-app-upgrader
description: >
  Use when upgrading or migrating an Enonic XP 7 application to XP 8 —
  converting descriptors (application.xml, site.xml,
  parts/layouts/pages/content-types, admin tools, APIs, services, webapp) to
  the new YAML `kind:` format, bumping `xpVersion` and the `com.enonic.xp.app`
  Gradle plugin to 4.x, or finishing/fixing partial xp8migrator runs. Also
  triggers on post-upgrade XP 8 deployment errors. Skip for brand-new XP 8
  apps and for upgrades between XP 7.x minor versions.
license: MIT
compatibility: Claude Code, Codex
allowed-tools: Bash(command -v enonic) Bash(enonic:*) Bash(./gradlew:*) Bash(gradle:*) Bash(ls:*) Bash(find:*) Bash(grep:*) Bash(cat:*) Bash(mv:*) Bash(rm:*) Bash(curl:*) Bash(wget:*) Bash(brew:*) Bash(npm:*) Bash(./migrator:*) WebFetch(domain:raw.githubusercontent.com) WebFetch(domain:repo.enonic.com) Read Write Edit
metadata:
  author: enonic
  xp-version: "7.x → 8.x"
---

## What this skill does

Upgrades a single XP application's source tree from XP 7 to XP 8. Out of scope: dumping/loading content data between XP 7 and XP 8
instances (covered briefly at <https://raw.githubusercontent.com/enonic/doc-xp/refs/heads/8.0/docs/release/upgrade.adoc>), and
upgrading 3rd-party market apps (replace those with their XP 8 versions yourself).

The skill leans on the official [`xp8migrator`](https://github.com/enonic/xp8migrator) tool for descriptor conversion (`application.xml`,
the entire `site/` tree, admin tools, APIs, webapp → YAML with `kind:`) and only does the things the migrator doesn't handle by hand:
build-system reorganization (settings plugin, `xplibs.*` catalog, `gradle.properties` flow), TypeScript/bundler config, code-level breaking
changes, `logback.xml`, and post-migration cleanup of the orphaned `site/` directory. See
<https://raw.githubusercontent.com/enonic/doc-code/refs/heads/master/docs/upgrade.adoc> for the upstream
Enonic upgrade guide (source of truth for descriptor shapes and breaking-change lists), `references/manual-schemes-migration.md` for the
full set of transformations the migrator performs, and `references/examples.md` for the full `xplibs.*` alias tables, worked `build.gradle`
examples, and TypeScript wiring.

## The Enonic CLI

> **REQUIRED SUB-SKILL — `enonic-cli`.** Whenever you need to run *any* `enonic` command (`project build`/`deploy`,
> `sandbox create`/`list`/`start`/`stop`, `dump`, …), **invoke the `enonic-cli` skill first** for the authoritative, current command and
> flag reference. Don't reconstruct `enonic` syntax from memory or from this skill alone — the commands and flags shown here are
> illustrative and can drift between CLI versions.

All build and deploy steps in this skill go through the **Enonic CLI** (`enonic project build`, `enonic project deploy`), not direct
`./gradlew` invocations. The CLI wraps the project's Gradle wrapper under the hood, so build failures still surface as Gradle output —
nothing about error diagnosis changes. The one direct `./gradlew` call that remains in this skill is
`./gradlew wrapper --gradle-version <version>` (the Gradle bump itself), which is a one-off configuration task the CLI has no command for.

The CLI is a machine-level developer tool, not a per-project helper — **so don't install it up front.** Checking whether it's present is
part of **Detect** (step 1, read-only); if it's missing, *installing it* is a line item in the **Plan** (step 3) the user approves, and
the install runs in **Execute** (step 4) — never silently before the plan is approved. Once installed it **stays installed** (never
removed during cleanup, unlike `./migrator`). The go-to install is npm — same on every platform:

```sh
npm install -g @enonic/cli
```

Only if npm is unavailable, fall back to a platform-native package manager:

| Platform | Fallback install command                                                                      |
|----------|-----------------------------------------------------------------------------------------------|
| macOS    | `brew tap enonic/cli && brew install --no-quarantine enonic`                                  |
| Linux    | `sudo snap install enonic` (or the shell installer from <https://developer.enonic.com/start>) |
| Windows  | `scoop bucket add enonic https://github.com/enonic/cli-scoop.git && scoop install enonic`     |

Verify with `enonic --version` after installing. See <https://developer.enonic.com/docs/enonic-cli/stable/install> for the full matrix.

### Running the Enonic CLI non-interactively (without deciding for the user)

Every `enonic` command in this skill (`project build`, `project deploy`, `sandbox create`, `sandbox start`) is **interactive by default** —
it prompts on a TTY. The agent shell has no TTY, so an un-flagged command hangs waiting on stdin, and the `--force` / `-f` flag
**silently accepts the default answer to every prompt** — which means the CLI, not you and not the user, picks the sandbox, the distro
version, and whether to boot a server. That is how a deploy ends up on the wrong sandbox, or attached to a long-running foreground XP
server that hangs the whole session.

The rule: **run the CLI non-interactively, but never let `-f` make a choice the user would want to make.** Before any command that would
prompt for a consequential value, work out what it would ask, surface those questions to the user (an `AskUserQuestion`-style choice in
Claude Code), then run it non-interactively with the answers passed as **explicit flags** — using `-f` only to suppress prompts whose
answers you have already pinned. `-f` means "don't ask me"; only reach for it once you (with the user) have answered everything it would
have asked. Per command:

- **`enonic project build -f`** — fine to run with `-f` directly. Its only prompt ("build without a sandbox?") has a harmless default.
- **`enonic sandbox create`** — prompts for distro version and template. Confirm the version with the user (it must match the app's
  `xpVersion`) and pass both explicitly, using the **Essentials** template: `enonic sandbox create <name> -v <xpVersion> -t essentials -f`.
- **`enonic project deploy <sandbox>`** — has two consequential prompts: *which sandbox* and *start it now?*. Always name the sandbox
  explicitly (never let `-f` choose — see step 7). Starting the sandbox launches a **long-running foreground XP server** that will hang the
  agent shell, so settle the start behaviour with the user first: `--skip-start` to only stage the JAR into a sandbox they will start
  themselves, or run the start detached / in the background (`run_in_background` in Claude Code) when they want a live runtime to inspect.

## Workflow (must follow in order)

The upgrade has two strict phases: **inventory & plan** (read-only, presented to the user), then **execute & validate** (only after the user
approves). Never edit files before the user approves the plan — silent edits frustrate users who want to inspect the change set first.
Throughout both phases, **announce before you act**: before each step that runs a command or edits a file, say in one line what you're
about to do and why, so the user always knows what's happening without having to ask.

```
1. Detect      → check the Enonic CLI is present (read-only); read gradle.properties, build.gradle, app descriptor, list directories
2. Inventory   → enumerate every file the upgrade will touch (group by category)
3. Plan        → present a numbered checklist of changes (incl. installing the Enonic CLI if it's missing); ask for approval
                 (descriptor changes are run via xp8migrator, not hand-edited)
4. Execute     → install the CLI if the plan said so; run xp8migrator for descriptors; edit build/code by hand
5. Validate    → run `enonic project build` BEFORE any cleanup (so a failure leaves the originals intact for diagnosis)
6. Cleanup     → only after the build is green AND the user confirms: `rm -rf src/main/resources/site` and delete `application.xml`
7. Deploy      → offer `enonic project deploy` to a sandbox and run it only after the user confirms
```

### 1. Detect

First, **check the Enonic CLI is present** — read-only, install nothing yet:

```sh
command -v enonic && enonic --version
```

If it's absent, note it for the Plan (step 3) — installing it is a plan item, not something you do here (see "The Enonic CLI" above).
Then read these to understand the app:

- `gradle.properties` — current `xpVersion`, `appName`, `appDisplayName`, `vendorName`, `vendorUrl`, `projectName`, `version`
- `settings.gradle` — does it declare `com.enonic.xp.settings`? If absent, the upgrade adds it (this plugin is the central XP 8 plumbing)
- `build.gradle` — current `com.enonic.xp.app` plugin version (pinned in XP 7, versionless in XP 8), the `app{}` block contents (XP 7 wires
  metadata here; XP 8 leaves it empty), how `com.enonic.xp:lib-*` deps are written (XP 7 long-form vs. XP 8 `xplibs.*` aliases)
- `gradle/wrapper/gradle-wrapper.properties` — Gradle version (must be 9.x for plugin 4.x)
- `src/main/resources/application.xml` (XP 7) or `enonic.yaml` (already XP 8)
- `src/main/resources/site/` — if present, this is a site app. The whole tree migrates to `cms/` (see
  `references/manual-schemes-migration.md`).
- `src/main/resources/webapp/` — if present, includes a webapp
- `src/main/resources/admin/tools/`, `admin/widgets/` — admin surface (widgets become `admin/extensions/` in XP 8)
- `src/main/resources/apis/`, `services/`, `tasks/` — HTTP endpoints / background tasks
- `src/main/resources/idprovider/` — ID provider (rare)
- `src/main/resources/cms/` — already partially migrated? If both `site/` and `cms/` are present, the migration is incomplete.
- **Stray descriptors outside the above locations.** Run
  `find src/main/resources -name '*.xml' -not -path '*/site/*' -not -path '*/admin/*' -not -path '*/apis/*' -not -path '*/services/*' -not -path '*/tasks/*' -not -path '*/webapp/*' -not -path '*/idprovider/*' -not -path '*/import/*' -not -name 'application.xml'`.
  Files like `lib/<name>/<name>.xml` (Page descriptors stashed inside `lib/`) are silently skipped by `xp8migrator` and stay as XP 7 XML in
  the upgraded app. Surface any hits to the user during the plan step — choices are: (a) delete if vestigial, (b) move to the appropriate
  standard location and re-run the migrator, (c) hand-convert in place.

Don't assume only one of these. A single app can be all three (site app + admin tool + webapp).

### 2. Inventory

Build a list of every file that needs to change. Group by category — the user will scan this in step 3, and a flat dump of 50 file paths is
unreadable. Categories:

| Category        | What to look for                                                                                                                                                                  |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Settings plugin | `settings.gradle` — needs `com.enonic.xp.settings` plugin in XP 8 (drives every other build-file change)                                                                          |
| Build           | `gradle.properties`, `build.gradle` (plugin pin, `app{}` block, dependency form), `gradle/wrapper/gradle-wrapper.properties` (Gradle version), `package.json` (`@enonic-types/*`) |
| App descriptor  | `src/main/resources/application.xml`                                                                                                                                              |
| Site → CMS      | `src/main/resources/site/**/*.xml` — the entire tree relocates to `cms/` (`site.xml`, `styles.xml`, parts, layouts, pages, content-types, mixins, x-data, macros, form-fragments) |
| Admin tools     | `src/main/resources/admin/tools/*/*.xml`                                                                                                                                          |
| Admin widgets   | `src/main/resources/admin/widgets/*/*.xml` (renamed to `admin/extensions/` in XP 8)                                                                                               |
| Services        | `src/main/resources/services/*/*.xml` (descriptors migrate to YAML; `kind: "Service"`)                                                                                            |
| APIs            | `src/main/resources/apis/*/*.xml` (rare in XP 7)                                                                                                                                  |
| Tasks           | `src/main/resources/tasks/*/*.xml`                                                                                                                                                |
| Webapp          | `src/main/resources/webapp/webapp.xml` (if present)                                                                                                                               |
| ID provider     | `src/main/resources/idprovider/idprovider.xml` (if present)                                                                                                                       |
| Server config   | `logback.xml` anywhere in the project                                                                                                                                             |
| Code            | controllers using removed admin URL helpers, services that should migrate to APIs                                                                                                 |
| Cleanup         | leftover `src/main/resources/site/` after a successful migrator run (it leaves orphan `.js`/`.svg` files behind)                                                                  |

### 3. Plan

Present the plan as a numbered checklist grouped by category. For each item state **what** changes and **why** in one line. Then ask the
user to approve, modify, or skip individual items. Wait for explicit approval before any write.

The user can grant approval up-front in the same turn as the original request (e.g. "show plan then apply", "go ahead and fix it", "do
whatever it takes"). Treat that as approval — show the plan and proceed straight into execution. Pause for a fresh confirmation only when
the request was open-ended ("what do I need to change?", "can you upgrade this?") without an explicit "go ahead".

If Detect found the Enonic CLI missing, make **installing it the first plan item** (`npm install -g @enonic/cli`, or a platform fallback
from "The Enonic CLI" above) — it's needed for the Validate and Deploy steps. Present it for approval like any other change; don't
pre-install it.

Example shape:

```
## XP 7 → XP 8 upgrade plan for <app-name>

Detected: JS site app, xpVersion 7.9.0, plugin 3.6.2, no settings plugin, `app{}` block has explicit name/displayName/vendor wiring, dependencies use long-form `com.enonic.xp:lib-*:${xpVersion}` coordinates, Gradle wrapper 8.5, no admin tools. Enonic CLI not found on PATH.

### Tooling (only if the Enonic CLI is missing)
0. Install the Enonic CLI — `npm install -g @enonic/cli` (or a platform fallback). Required for `enonic project build`/`deploy`; it's a machine-level dev tool that stays installed afterward.

### Build system (settings plugin + catalog)
1. `settings.gradle` — add the XP 8 settings plugin: `id("com.enonic.xp.settings") version "<latest>"`. This is the centerpiece of the XP 8 build; it supplies the `com.enonic.xp.app` plugin version and the `xplibs.*` catalog. Pick the latest released version (alpha/beta releases like `4.0.0-A3` / `4.0.0-B1` are fine — do not use `-SNAPSHOT`).
2. `build.gradle` — drop the `version '3.6.2'` pin from `id 'com.enonic.xp.app'`; in XP 8 the version is supplied by the settings plugin.
3. `build.gradle` — omit the `app { }` block (the verified XP 8 reference apps don't carry it). Keep `app { createDefaultDevTask = false }` only if the project's `dev` task differs from the plugin default (which runs `deploy --continuous -Penv=dev`) — e.g. a real `NpmTask` watch. If the existing `dev` task just reproduces the default, drop it and use the auto-registered one (see "Build files").
4. `build.gradle` — migrate Enonic library dependencies from `"com.enonic.xp:lib-X:${xpVersion}"` to `xplibs.X`. **Pure 1:1 rename — migrate every `include` as-is; never drop one as "unused" (XP `include`s aren't transitive, so app-source greps can't prove a dep unused; pruning is out of scope — see "Build files").**
5. `gradle/libs.versions.toml` (new file) — extract third-party `com.enonic.lib:*` deps (e.g. `lib-thymeleaf`, `lib-xslt`, `lib-asset`, `lib-static`) into a Gradle version catalog, and reference them as `libs.<alias>` in `build.gradle`. Skip if the app has zero or one such dep.
6. `gradle.properties` — bump `xpVersion` to the highest XP 8 version available (prefer stable; fall back to alpha/beta like `8.0.0-A3` / `8.0.0-B1`; `-SNAPSHOT` only as a last resort). Add `projectName` if missing (used by `settings.gradle`); leave `appName`/`version`/`group` in place. Display/vendor metadata moves to `enonic.yaml` (see *Application descriptor*).
7. `gradle/wrapper/gradle-wrapper.properties` — bump Gradle to 9.4.1 (plugin 4.x requires Gradle 9+). Run via `./gradlew wrapper --gradle-version 9.4.1`.

### Descriptors (run xp8migrator)
8. `src/main/resources/application.xml` → `enonic.yaml` (`kind: "Application"`, plus `title`/`vendorName`/`vendorUrl` imported from `gradle.properties`)
9. `src/main/resources/site/` → `src/main/resources/cms/` — the migrator splits `site.xml` between `cms/site.yaml` and `cms/cms.yaml`, moves `styles.xml` to `cms/style/style.yaml`, renames `x-data/` to `mixins/`, and converts every part/layout/page/content-type/macro to YAML with the right `kind:`. ~16 files touched.

### Validation
10. Run `enonic project build -f` — must pass before any file deletion. If it fails, the originals in `site/` and `application.xml` are still in place for diagnosis.

### Cleanup (only after the build is green)
11. Delete the originals: `rm -rf src/main/resources/site`, `rm src/main/resources/application.xml`, `rm ./migrator` (rationale in the Cleanup step).
12. Remove the duplicate `cms/styles/image.yaml` if the migrator emitted one (see the Cleanup step).
13. Optionally deploy — pick the sandbox and run mode *with the user* (see the Deploy step).

OK to proceed? Reply "go" to apply all, or list the numbers to skip.
```

### 4. Execute

If the plan included installing the Enonic CLI (Detect found it missing), do that first — the Validate step needs it:
`npm install -g @enonic/cli` (or the platform fallback from "The Enonic CLI").

Apply the approved changes in two passes — descriptors first via the migrator, then build/code edits by hand.

**Descriptor pass (xp8migrator):**

```sh
# from the app project root
curl -fsSL https://raw.githubusercontent.com/enonic/xp8migrator/main/migrator-install.sh | sh
./migrator -e overwrite         # non-interactive — overwrite any pre-existing target files
```

> ⚠️ **Flag this to the user before running it.** The `curl … | sh` install pipes a remote script straight into a shell, which Claude's
> security constraints block in auto / auto-accept (headless) mode — it only runs when the user is present to approve it. Tell the user up
> front that in auto mode this step will fail, and offer them the choice: run the installer themselves (suggest typing
> `! curl -fsSL https://raw.githubusercontent.com/enonic/xp8migrator/main/migrator-install.sh | sh` in the prompt) or approve it
> interactively. Once `./migrator` exists in the project root, the rest of the descriptor pass proceeds normally.

If the migrator errors out, run `./migrator -h` to inspect the available flags. **Don't run the migrator a second time with `-x`** — its
post-migration step tries to move `cms/style/style.yaml` again and fails with `FileAlreadyExistsException`. Cleanup of the original XML
happens via plain `rm` after the build is green (see the Cleanup step), not via `./migrator -x`.

The migrator leaves the original `site/` tree and `application.xml` in place. Sibling `.js`, `.html`, and `.svg` files are *copied* into the
new `cms/` location during migration. Don't delete anything yet — let `enonic project build` validate the result first. If it fails, the
originals are still there for diagnosis.

On Windows, use `.\migrator.exe` and the PowerShell installer (`migrator-install.ps1`). Useful flags: `-h` (help), `-a <app-name>` (override
`gradle.properties`), `-e ask|overwrite|skip` (conflict policy — use `overwrite` for non-interactive runs).
See <https://github.com/enonic/xp8migrator> for the canonical CLI reference.

If `xp8migrator` is unavailable (offline environment, descriptor not handled by the tool), fall back to hand-edits per
`references/manual-schemes-migration.md`.

**Build / code pass (hand-edits):**

Edit the files in-place (`Edit` tool in Claude Code) for changes to `build.gradle`, `gradle.properties`, and any controller/template
fixes. Keep edits minimal — don't reformat unrelated lines, don't change content the user didn't approve.

### 5. Validate (before any deletion)

Run `enonic project build -f` first — that catches descriptor-syntax errors and
dependency-resolution failures. The CLI drives the project's Gradle wrapper internally, so failures come back as ordinary Gradle output —
report success or paste the first failure with its file/line. If the build fails, the original `site/` tree and `application.xml` are
still in place, so the user can inspect them while you suggest a fix; ask before retrying.

**A green build does NOT prove the dependency set is right.** XP `include`s aren't transitive, so a bundled lib's runtime
`require('/lib/xp/*')` never surfaces at build time (see the *Migrate dependencies* edit under "Build files") — the only evidence that a
declared dep is used, or that a candidate for removal is truly dead, is a **JAR-level `require` scan** of the built artifact:

```sh
unzip -o build/libs/<app>.jar -d /tmp/<app>-jar >/dev/null
grep -rhoE "require\(['\"]/lib/[^'\"]+" /tmp/<app>-jar | sed -E "s/require\(['\"]//" | sort -u
```

Every `/lib/xp/<name>` the scan lists must have a matching `xplibs.<name>` `include`. This scan is the *prerequisite* for any dependency
pruning — and pruning itself is post-upgrade work, **out of scope for this skill**. During the upgrade, never remove an `include`.

### 6. Cleanup (only after the build is green AND the user confirms)

Once `enonic project build` passes, **ask the user whether to delete the originals before doing it** — don't remove anything automatically.
A green build with descriptors in both XML and YAML forms is a valid, recoverable state; once the originals are deleted the change is hard
to reverse without git. Phrase the prompt as a yes/no question listing the exact paths, e.g. "Build passed. OK to delete
`src/main/resources/site/`, `src/main/resources/application.xml`, and `./migrator`?"

Only after the user confirms, run:

```sh
rm -rf src/main/resources/site
rm src/main/resources/application.xml
rm ./migrator                   # remove the binary too
```

**Do NOT uninstall the Enonic CLI** during cleanup. Unlike `./migrator` (a single-purpose binary dropped into the project), the CLI is a
machine-level developer tool — if the upgrade installed it, it stays installed.

The migrator already copied sibling `.js`/`.html`/`.svg` files from `site/` into `cms/`, so wiping the entire `site/` directory is safe.
(Use plain `rm`, never `./migrator -x` — see the Descriptor pass under Execute.)

If both `cms/style/style.yaml` and `cms/styles/image.yaml` exist after migration (older migrator versions emitted both), delete
`cms/styles/image.yaml` — `cms/style/style.yaml` is the canonical XP 8 form.

### 7. Deploy (optional)

After cleanup, **ask the user whether to deploy** — don't run it automatically. Deploying mutates state outside the project (the sandbox),
so it warrants explicit confirmation. Phrase it as a yes/no question, e.g. "Build passed. Want me to deploy to a sandbox with
`enonic project deploy`?"

If the user says yes, run the deployment **purely via the Enonic CLI** — no direct gradle invocations — and follow the non-interactive
discipline from "Running the Enonic CLI non-interactively" above: list the candidates, let the *user* pick, then run with everything
pinned as explicit flags.

```sh
enonic sandbox list      # read-only — sandboxes + distro versions; the running one (only one at a time) is marked with a leading "*"
```

1. **Pick the sandbox WITH the user — never let `-f` choose.** From the list, present the sandboxes whose distro matches the app's new
   `xpVersion` (an XP 8 app on a leftover XP 7 sandbox fails to load) and ask which one to use — or whether to create a fresh one. If a new
   sandbox is needed, confirm the version, then create it with the **Essentials** template:
   `enonic sandbox create <name> -v <xpVersion> -t essentials -f`.
2. **Check whether a sandbox is already running before offering to start one.** In the `enonic sandbox list` output the running sandbox is
   marked with a leading **`*`**, and only one sandbox runs at a time. So:
    - **The sandbox you picked is already running** (`*` next to it) → don't start anything; stage the JAR with
      `enonic project deploy <sandbox> --skip-start -f` and the live server hot-loads it.
    - **A *different* sandbox is running** → you can't start the target while it's up. Surface this to the user; they decide whether to stop
      the running one (`enonic sandbox stop <name>`, for a detached sandbox) or just deploy to the one already running.
    - **Nothing is running** → proceed to settle the start mode below.
3. **Settle the start mode (when nothing relevant is already running).** `enonic project deploy <sandbox>` will, by default, start the
   sandbox and **attach to a long-running foreground XP server that hangs the agent shell**. Ask the user which they want:
    - `enonic project deploy <sandbox> --skip-start -f` — builds and stages the JAR into the sandbox without starting it (no live runtime,
      but the shell returns immediately); or
    - `enonic project deploy <sandbox> -f` run **in the background** (`run_in_background` in Claude Code) — when they want a live runtime to
      poke at. Read the command's own output to report startup; do not otherwise probe the server (see below).

Always name the sandbox explicitly. Reach for `-f` only after the sandbox and start behaviour are pinned — it is there to suppress the
prompts you have already answered, not to answer them for you.

**Confirm the sandbox started — do not verify the app installed.** Report only what the deploy/start command itself prints (the sandbox
started, or the first failure with file/line). **Don't check whether the app actually installed** — don't open the Applications list,
don't tail `server.log`, don't grep XP_HOME. Once the sandbox reports started, hand the user a link to view it themselves:

- **Admin console / launcher:** <http://localhost:8080/admin> — default dev port is `8080`; if you passed `--http.port`, use that port.

The user inspects the running app from there. If they hit a runtime/load error and want help, hand off to the `xp-app-debugger` skill.

## What changes between XP 7 and XP 8

This is the canonical change set. Apply only the items that exist in the user's app — don't invent files.

> **Verify the public API of any XP `lib-*` before editing JS/Java that calls it.** This skill's lists of removed/renamed functions are a
> starting point, not the source of truth — they may be incomplete or out of date. Library APIs evolve between XP 8 pre-releases. Before
> recommending a replacement function (`getHomeToolUrl`, `extensionUrl`, etc.), confirm it actually exists by reading the relevant
> `.ts`/`.js` file **at the release tag matching the `xpVersion` you're pinning**, not `master` — `master` can be a major ahead of what you
> install (read it only when you're tracking the very latest or a SNAPSHOT). Browse the libs at
> <https://github.com/enonic/xp/tree/master/modules/lib/> and switch the branch selector to that tag. Don't assume a function survived just
> because it was in XP 7; the same applies to Java APIs — verify before editing controllers that import XP types.

### Build files

> See `references/examples.md` for the full `xplibs.*` alias tables (every `com.enonic.xp:` library and API), worked `build.gradle`
> examples (site app with version catalog; TS app with custom `dev` task), and TypeScript wiring.

The XP 8 build is reorganized around the **`com.enonic.xp.settings` Gradle settings plugin**. Once it's in place, it supplies the
`com.enonic.xp.app` plugin version and the `xplibs.*` dependency catalog — both of which used to be set in the app's `build.gradle`. The
upgrade therefore *adds* lines to `settings.gradle` and *removes* lines from `build.gradle`.

**`settings.gradle`** — declare the settings plugin:

```diff
+plugins {
+    id( "com.enonic.xp.settings" ) version "<latest>"
+}
+
 rootProject.name = projectName
```

Pick the **latest released** 4.x version of the plugin (alpha/beta releases such as `4.0.0-A3` or `4.0.0-B1` are fine; do **not** use a
`-SNAPSHOT` suffix). The settings plugin and `com.enonic.xp.app` plugin ship together (the settings plugin supplies the app-plugin version),
but they do not track the XP runtime version — see the next paragraph.

**Verify the settings plugin version is actually published before pinning it.** The settings plugin's release cadence does NOT track XP's —
its `4.0.x` numbering is independent of `xpVersion=8.0.x`, and not every XP release ships with a matching settings plugin to the Gradle
plugin portal. Picking `4.0.0-B4` because `xpVersion=8.0.0-B4` will fail with
`Plugin [...] was not found ... could not resolve plugin artifact` if only `4.0.0-A3` / `4.0.0-B1` are live on plugins.gradle.org. Check
before committing to a version:

```sh
curl -s 'https://plugins.gradle.org/m2/com/enonic/xp/settings/com.enonic.xp.settings.gradle.plugin/' | grep -oE 'href="[^"]+/"'
```

Use the highest version that listing actually shows; it may lag the XP runtime version by one or more releases.

**`build.gradle`** — independent edits (the first three are driven by the settings plugin; the last by the Gradle 9 bump):

1. **Drop the version pin** on `com.enonic.xp.app`:

   ```diff
    plugins {
   -    id 'com.enonic.xp.app' version '3.6.2'
   +    id 'com.enonic.xp.app'
    }
   ```

   The settings plugin supplies the version. Pinning it at the app level conflicts with the settings plugin and is wrong for XP 8.

2. **Strip the `app { }` block.** XP 7 wired metadata through it; XP 8 reads metadata from `enonic.yaml` (`title`, `description`,
   `vendorName`, `vendorUrl`) — see the "Application descriptor" section below:

   ```diff
    app {
   -    name = "${appName}"
   -    displayName = "${appDisplayName}"
   -    vendorName = "${vendorName}"
   -    vendorUrl = "${vendorUrl}"
   -    systemVersion = "${xpVersion}"
    }
   ```

   **Omit `app { }` entirely by default** (the verified XP 8 reference apps don't carry it). Leaving it empty also works.

   **Only keep `app { createDefaultDevTask = false }` when the project's `dev` task does something the plugin's default `dev` task does
   *not* — not merely because a `dev` task is present.** When `createDefaultDevTask` is left on (its default), the plugin auto-registers a
   `dev` task (`com.enonic.gradle.xp.app.DevTask`) whose whole job is to run the continuous task — by default
   `./gradlew deploy --continuous -Penv=dev` (plus `-PxpHome=…` when set), i.e. redeploy on every source change. So compare the project's
   existing `dev` task against that:
    - **Functionally equivalent** (it just runs `deploy` / the build continuously in dev mode) → it's **redundant**: delete it *and* drop
      `createDefaultDevTask = false`, letting the auto-registered default take over (the `app { }` block is then empty — remove it).
    - **Genuinely different** (e.g. an `NpmTask` running `npm run watch` to drive a TS/bundler build, which the default deploy-continuous
      task can't do) → keep it, and keep `app { createDefaultDevTask = false }` so the two don't collide.

   Read the plugin source to see exactly what the default does before deciding:
   <https://github.com/enonic/xp-gradle-plugin/blob/master/src/main/java/com/enonic/gradle/xp/app/DevTask.java>.

3. **Migrate dependencies** to the `xplibs.*` catalog. The catalog has two namespaces:
    - **APIs** (`com.enonic.xp:*-api`) → `xplibs.api.<name>` (e.g. `portal-api` → `xplibs.api.portal`, `core-api` → `xplibs.api.core`,
      `admin-api` → `xplibs.api.admin`)
    - **Libraries** (`com.enonic.xp:lib-*`) → `xplibs.<name>` (e.g. `lib-content` → `xplibs.content`)

   ```diff
    dependencies {
   -    implementation "com.enonic.xp:portal-api:${xpVersion}"
   -    include "com.enonic.xp:lib-content:${xpVersion}"
   -    include "com.enonic.xp:lib-portal:${xpVersion}"
   +    implementation xplibs.api.portal
   +    include xplibs.content
   +    include xplibs.portal
        include "com.enonic.lib:lib-thymeleaf:3.0.0-B1"
    }
   ```

   Only `com.enonic.xp:` dependencies move to the `xplibs` catalog — third-party libraries (`com.enonic.lib:lib-thymeleaf`,
   `com.enonic.lib:lib-xslt`, `com.enonic.lib:lib-asset`, `com.enonic.lib:lib-static`, etc.) keep their full Maven coordinates **or** move
   to a separate Gradle version catalog (see step 5). See `references/examples.md` for the complete `xplibs` alias tables (6 APIs + 24
   libs).

   **The dependency conversion is a pure 1:1 rename — never drop an `include` as "unused" during the upgrade.** XP `include` dependencies
   are **not transitive**: bundled third-party JS libs can `require('/lib/xp/*')` modules that the app's own source never references (e.g.
   `lib-util`'s `getLocale.js` does `require('/lib/xp/admin')`, so an app that bundles `lib-util` needs `xplibs.admin` even with zero
   `/lib/xp/admin` calls of its own). Grepping app source is therefore **not** sufficient evidence that a dep is unused — the build will
   pass and the app will fail at runtime on the first page render. Convert every `include` line as-is; if the number of `include`s changed
   between XP 7 and XP 8 (other than the API/alias rename), you pruned something — put it back. Dependency pruning is post-upgrade work,
   **out of scope for this skill**, and must only be done after a JAR-level `require` scan (see the validation step).

   **`com.enonic.lib:lib-thymeleaf` requires a version bump for XP 8.** XP 7-era apps typically pin `2.1.1`, which is not compatible with
   XP 8. Bump it to the latest released `3.x` — `3.0.0-B1` at time of writing — which is published to the **public** repo (find the current
   one with the Maven-metadata check below). Surface this in the plan whenever the app declares `lib-thymeleaf:2.1.1` (or any other 2.x). A
   released `3.x` resolves through the plain `xp.enonicRepo()` — no dev channel needed. Only if no released `3.x` exists yet, fall back to
   `3.0.0-SNAPSHOT` (dev channel only): then **replace** the existing `xp.enonicRepo()` in `repositories { … }` with
   `xp.enonicRepo( "dev" )`
   (a superset that includes releases — swap it in, don't add it alongside), and don't hand-roll a raw
   `maven { url 'https://repo.enonic.com/snapshot' }` block. Watch for the same 2.x → 3.x transition across other `com.enonic.lib:*`
   libraries during the XP 8 alpha/beta window.

   **Check released artifacts, not the lib repo's `master` branch.** A lib's `master`-branch `gradle.properties` reflects *unreleased*
   development (e.g. `xpVersion = 8.1.0-SNAPSHOT`) and says nothing about what is installable today. Determine the latest released
   XP 8-compatible version from the published Maven metadata under <https://repo.enonic.com/public/>, or from Enonic Market — never from a
   GitHub branch:

   ```sh
   curl -s 'https://repo.enonic.com/public/com/enonic/lib/<lib-name>/maven-metadata.xml' | grep -oE '<version>[^<]+</version>'
   ```

   Pick the highest version compatible with the target `xpVersion` — during the XP 8 pre-release window that is often a `-Bn` beta
   (e.g. `lib-menu` `4.2.1` → `5.0.0-B1`, `lib-urlredirect` `3.0.1` → `4.0.0-B1`). If you then need to confirm a function or API the app
   calls, read the lib's source **at the matching release tag**, not `master` — master can be one or more XP majors ahead of the newest
   installable release.

4. **Extract third-party libraries into `gradle/libs.versions.toml`** (recommended for apps with two or more `com.enonic.lib:*` deps). The
   XP 8 reference apps centralize non-`com.enonic.xp` libs in a Gradle version catalog so versions are declared once and referenced as
   `libs.<alias>` in `build.gradle`:

   ```toml
   # gradle/libs.versions.toml
   [versions]
   thymeleaf = "3.0.0-B1"
   xslt      = "2.1.1"
   asset     = "2.0.0-RC1"

   [libraries]
   lib-thymeleaf = { module = "com.enonic.lib:lib-thymeleaf", version.ref = "thymeleaf" }
   lib-xslt      = { module = "com.enonic.lib:lib-xslt",      version.ref = "xslt" }
   lib-asset     = { module = "com.enonic.lib:lib-asset",     version.ref = "asset" }
   ```

   Then in `build.gradle`:

   ```diff
    dependencies {
        include xplibs.content
        include xplibs.portal
   -    include "com.enonic.lib:lib-thymeleaf:3.0.0-B1"
   -    include "com.enonic.lib:lib-xslt:2.1.1"
   -    include "com.enonic.lib:lib-asset:2.0.0-RC1"
   +    include libs.lib.thymeleaf
   +    include libs.lib.xslt
   +    include libs.lib.asset
    }
   ```

   The catalog file lives at `gradle/libs.versions.toml` (Gradle's default location — no extra wiring in `settings.gradle` needed). Aliases
   in `[libraries]` map dotted accessors in `build.gradle` (`lib-thymeleaf` → `libs.lib.thymeleaf`). This keeps version bumps in one place
   and is the pattern verified against `app-superhero-blog`.

   For apps with only one third-party dep (or zero), keep the inline coordinate — a catalog file is overkill.

5. **Remove top-level `sourceCompatibility` / `targetCompatibility`.** Older XP 7 build files often include:

   ```diff
   -sourceCompatibility = JavaVersion.VERSION_11
   -targetCompatibility = sourceCompatibility
   ```

   Gradle 9 dropped these as `Project` properties — leaving them in fails the build with
   `Could not set unknown property 'sourceCompatibility' for root project ... of type org.gradle.api.Project`. For JS-only XP apps (no
   `src/main/java`) they're vestigial and safe to delete outright. For apps with Java sources, prefer letting the XP plugin's toolchain
   convention handle it (see next bullet) over hand-rolling a `java { sourceCompatibility = ...; targetCompatibility = ... }` block.

6. **Don't add an explicit Java toolchain block — the XP plugin sets it.** The `com.enonic.xp.base` plugin (applied transitively by
   `com.enonic.xp.app`, and applied directly by XP 8 *libraries* like `lib-react4xp`) sets the Java toolchain to **version 25** as a
   convention default whenever the `java` plugin is applied. So a block like:

   ```groovy
   java {
       toolchain {
           languageVersion = JavaLanguageVersion.of(25)
       }
   }
   ```

   is redundant in XP 8 builds and should be removed during the upgrade. Keep an explicit toolchain block only if you need to *override* the
   convention to a different JDK version. Setting `sourceCompatibility`/`targetCompatibility` is also unnecessary — the toolchain handles
   both.

**`gradle.properties`:** bump `xpVersion` to the highest XP 8 version actually available, preferring **stable** over pre-release over
snapshot:

1. **Stable release** (e.g. `8.0.0`, `8.0.1`) — use this if any final XP 8 release exists. Check
   <https://repo.enonic.com/public/com/enonic/xp/core-api/>.
2. **Pre-release** (alpha / beta, e.g. `8.0.0-A3`, `8.0.0-B1`) — use the highest one published to the release repo if no stable exists.
3. **Snapshot** (e.g. `8.0.0-SNAPSHOT`) — only as a last resort, when nothing else is published. Snapshots resolve only through
   `xp.enonicRepo("dev")` (the same dev-channel swap the *Migrate dependencies* edit covers), so they work but move under your feet between
   rebuilds.

If the user is on the very old `7.x` series (< 7.16), warn that XP recommends going through 7.16.x first (see the
[instance upgrade guide](https://raw.githubusercontent.com/enonic/doc-xp/refs/heads/8.0/docs/release/upgrade.adoc)) — but the source-level
edits are the same. Add `projectName = …` if missing (`settings.gradle` reads it); keep `appName`, `version`, `group` (still consumed by
Gradle). Display/vendor metadata (`appDisplayName`, `vendorName`, `vendorUrl`, and the legacy unprefixed `displayName`) is handled in the
*Application descriptor* section below — it moves into `enonic.yaml`.

**`gradle/wrapper/gradle-wrapper.properties`:** plugin 4.x requires **Gradle 9+**. Pin to a current 9.x via the wrapper task (which also
refreshes `gradle-wrapper.jar`):

```sh
./gradlew wrapper --gradle-version 9.4.1
```

**JUnit Platform launcher (Gradle 9+).** If the app has JUnit 5 tests, Gradle 9 no longer auto-resolves
`org.junit.platform:junit-platform-launcher` onto the test runtime classpath — the test task (run as part of `enonic project build`) fails with
`Failed to load JUnit Platform. Please ensure that all JUnit Platform dependencies are available on the test's runtime classpath, including the JUnit Platform launcher.`
Add the launcher explicitly:

```diff
 dependencies {
     testImplementation 'org.junit.jupiter:junit-jupiter:5.11.4'
+    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
 }
```

The version is supplied transitively by `junit-jupiter`; pinning it is unnecessary.

**`JsonMapGenerator` moved package (test-only).** The concrete `JsonMapGenerator` helper class — commonly used in XP 7 unit tests to drive
`MapSerializable.serialize(MapGenerator)` — moved package and jar in XP 8:

| XP 7                                               | XP 8                                                |
|----------------------------------------------------|-----------------------------------------------------|
| `com.enonic.xp.script.serializer.JsonMapGenerator` | `com.enonic.xp.testing.serializer.JsonMapGenerator` |

Compile error: `cannot find symbol: class JsonMapGenerator ... package com.enonic.xp.script.serializer`. Fix is a one-line import update —
the class is in the `com.enonic.xp:testing` jar (already on the test classpath as `testImplementation`). The interfaces it works with (
`MapGenerator`, `MapSerializable`) stay in `com.enonic.xp.script.serializer` and don't move.

### Application descriptor

`src/main/resources/application.xml` → `enonic.yaml` (handled by `xp8migrator`; XML is no longer recognized in XP 8).
`kind: "Application"` is mandatory — missing it fails deployment with `Invalid kind "null". Expected "Application"`. See
`references/manual-schemes-migration.md` §6.1 for the exact field map and
<https://raw.githubusercontent.com/enonic/doc-code/refs/heads/master/docs/upgrade.adoc> for an XP 7 → XP 8 example.

**Metadata flow.** The migrator pulls `appDisplayName` / `vendorName` / `vendorUrl` from `gradle.properties` and writes them into
`enonic.yaml` (as `title` / `vendorName` / `vendorUrl`). Two pre-migrator fixups in real XP 7 apps:

1. **Unprefixed `displayName`** in `gradle.properties` — rename to `appDisplayName` (the migrator only matches the `app`-prefixed form,
   otherwise `title:` ends up empty).
2. **Vendor info hard-coded in the `app{ }` block** of `build.gradle` — lift the literals into `gradle.properties` (or write them straight
   into `enonic.yaml` post-migration; both end states are valid).

If realized after running the migrator: fix the keys and re-run `./migrator -e overwrite`, or hand-edit `enonic.yaml`. (Don't use `-x`
on the re-run — see the "Descriptor pass" note.)

### Admin tools

> Also handled by `xp8migrator`. The hand-edit shape below matters for review (and for fixes the migrator may not auto-apply, like the
> system-API list).

`src/main/resources/admin/tools/<name>/<name>.xml` → `<name>.yaml`.

```yaml
kind: "AdminTool"
title:
  text: "My Dashboard"
  i18n: "admin.tool.dashboard.title"
description:
  text: "Application dashboard"
  i18n: "admin.tool.dashboard.description"
allow:
  - "role:system.admin"
apis:
  - "admin:extension"   # always include — replaces admin:widget
  - "admin:event"
  - "admin:status"
  # plus any custom APIs this tool calls
```

Two gotchas:

1. **`title` and `description` must be objects** (`{ text, i18n }`). Plain strings cause an NPE in `AdminToolMapper`. (APIs use plain-string
   `title` — that's correct for APIs, wrong for admin tools.)
2. **`apis:` is strictly enforced.** A tool can only call APIs it declares — calls to undeclared APIs fail at runtime with
   `API [<app>:<name>] is not mounted`. List every API the tool talks to, including the system APIs (`admin:extension`, `admin:event`,
   `admin:status`). For APIs contributed by an `include`d lib (e.g. `lib-asset`'s `asset` API), use the **bare name** (`"asset"`) —
   the lib's `apis/` are merged into your JAR at build time and mount under your app's key, not the lib's. Confirm with
   `unzip -l build/libs/<app-name>.jar | grep apis/`.

In XP 8 every admin tool is shown on the launcher menu. If you have a tool that should *not* appear there, convert it to an API instead (
move `admin/tools/<name>/` to `apis/<name>/`).

In admin tool **controllers**:

- `portalLib.assetUrl`, `widgetUrl`, etc. work the same.
- The admin lib lost `getAssetsUri()`, `getBaseUri()`, `getLauncherPath()`. Replace with `extensionUrl({ application, extension })` and
  `getHomeToolUrl()`.
- **Confirm against the source for your pinned version before editing.** On current `master` the only `/lib/xp/admin` exports are
  `getToolUrl`, `getHomeToolUrl`, `getInstallation`, `getVersion`, `widgetUrl` (deprecated), and `extensionUrl` — `getLauncherUrl()` is
  gone, and the launcher script is no longer injected at all. Treat that as illustrative and verify against the `lib-admin` source **at the
  tag matching your `xpVersion`** (`…/modules/lib/lib-admin/src/main/resources/lib/xp/admin.ts`), not `master`. The same applies to other
  libs (`lib-portal`, `lib-content`, etc.) — see <https://github.com/enonic/xp/tree/master/modules/lib/>.
- The default Admin Home path is now `/admin` (was `/admin/home`).

In admin tool **HTML templates** (Mustache/Thymeleaf): the launcher script is no longer injected — replace the old launcher include with a
`widgetUrl()` call, and deliver tool config as inline JSON instead of a service fetch.

### Admin widgets → admin extensions

`admin:widget` is renamed to `admin:extension` in XP 8. Update any reference to `admin:widget` (e.g. in the `apis:` list of an admin tool)
to `admin:extension`. The on-disk descriptor file location may also change — consult the `xp-app-creator` skill for current XP 8
widget/extension layout.

### APIs

> Also handled by `xp8migrator`.

`src/main/resources/apis/<name>/<name>.xml` → `<name>.yaml`.

```yaml
kind: "API"
title: "Content API"
allow:
  - "role:system.authenticated"
mount: true
```

`kind: "API"` is mandatory. Note `title:` is a **plain string** for APIs (not the object form admin tools use).

If the app uses `services/` and you want to migrate to the new API model, move each service to `apis/<name>/`, convert the descriptor to
YAML, and update callers from `serviceUrl({ service })` to `apiUrl({ api })`. Services still work in XP 8 — migration is recommended but not
required for the upgrade itself.

### Site descriptors → `cms/` tree (YAML)

The entire `site/` tree relocates to `cms/`, every descriptor becomes YAML with a kind-specific `kind:`, `site.xml` splits into
`cms/site.yaml` + `cms/cms.yaml`, and `x-data/` is renamed to `mixins/`. **Handled by `xp8migrator`.** See
`references/manual-schemes-migration.md` for the systematic transformations: the path/`kind:` map, field renames (including
`<display-name>` → `title:` and its exceptions), structural patterns (`<form/>` → `form: []`, `<occurrences>`, `<config>` flattening,
`<regions>`), and special cases for `application.xml`, `site.xml` split, `styles.xml`, content-type field moves, and `OptionSet` renames.

Two real-world gotchas worth flagging up front (not in the systematic reference):

- **`title:` and `description:` accept either a plain string or a `{ text, i18n }` object.** Use the object form whenever the XP 7 XML had
  an `i18n="…"` attribute on `<display-name>`/`<description>` — it's the form the migrator emits, and it preserves localization keys. Plain
  strings are fine when there's no i18n key. (Admin tools are special — see "Admin tools" above; their `title:` *must* be the object form
  regardless.)
- **Site mappings can use either `match:` or `pattern:`/`invertPattern:`** — both forms are valid in `cms/site.yaml`. The XP 7
  `<match>type:'…'</match>` becomes `match: "type:'…'"`; XP 7 `<pattern>` becomes `pattern: ".*\\/rss"` with an explicit
  `invertPattern: false/true`.

#### `cms/site.yaml` `apis:` list — gotcha

Like admin tools (see above), a site must explicitly mount any **mounted-API** library it uses — most commonly `lib-asset` (which exposes an
`asset` API). Without the declaration, `assetUrl()`/asset-resolution calls fail at runtime. The migrator does NOT infer this — the
declaration must be added by hand:

```yaml
kind: "Site"
mappings:
  - controller: "/lib/rss/rss.js"
    order: 50
    pattern: ".*\\/rss"
    invertPattern: false
apis:
  - "asset"        # required when the site uses lib-asset
```

App-key qualification follows the same rules as admin tool `apis:` lists — a bare name (`"asset"`) refers to the current app's API
namespace; a fully-qualified key (`"<other-app>:<api>"`) targets a *separately-deployed* app's API.

**Important: a lib bundled into your app is not a "separate app".** When the app `include`s a library that publishes a mounted API
(e.g. `com.enonic.lib:lib-asset` providing the `asset` API), the lib's `apis/<name>/` directory is merged into your app's JAR at
build time, and the API is mounted under **your** app's key — not the lib's. So the reference must be the bare name (`"asset"`),
**never** `"com.enonic.lib.asset:asset"` and **never** `"com.enonic.app.<your-app>:asset"` either (the fully-qualified form is
only for cross-app calls). Verify the mount by inspecting the built JAR: `unzip -l build/libs/<app-name>.jar | grep apis/` should
show `apis/asset/...` regardless of which lib contributed the descriptor.

### Server-side configuration files

If the project repo contains server-config files (most commonly a `logback.xml` — remove `<withJansi>true</withJansi>` to avoid a startup
error), apply the changes documented at
<https://raw.githubusercontent.com/enonic/doc-xp/refs/heads/8.0/docs/release/upgrade.adoc>. That guide also covers data migration
(`dump`/`load`), Management API breaking changes, security (`xp.suPassword`, password hashing), and the default
`com.enonic.cms.default` repo behavior change.

## Tips for the conversation

- **Narrate before you act.** Before each step that runs a command or edits a file, say in one line what you're about to do and why, so the
  user can follow along and step in before it happens — don't open with silent tool calls. For consequential or hard-to-reverse actions
  (the migrator run, file deletions, the build, a deploy, a CLI install), state the intent and, where the workflow calls for it, wait for
  the go.
- **Quote what you found.** When presenting the plan, quote the actual current values (`xpVersion = 7.9.0`, plugin `3.6.2`) so the user can
  tell at a glance you read their files instead of guessing.
- **Use diffs, not prose.** When the change is non-trivial (e.g. multi-line `build.gradle` plugin or dependency edits), show a unified-diff
  snippet in the plan so the user can approve precisely what will land.
- **Don't auto-touch generated/wrapper files.** `gradlew`, `gradlew.bat`, `gradle/wrapper/gradle-wrapper.jar` should not be hand-edited. If
  Gradle needs to be bumped, run the wrapper task: `./gradlew wrapper --gradle-version 9.0.0`.
- **Stop on the first deal-breaker.** If a required file is missing or in an unexpected location, ask before proceeding — don't synthesize a
  guess.
- **Hand off to siblings when relevant.** For enonic CLI usage during the upgrade, consult `enonic-cli`. For build failures, point to
  `xp-app-debugger`.

## See also

- <https://raw.githubusercontent.com/enonic/doc-code/refs/heads/master/docs/upgrade.adoc> — upstream Enonic XP 7 → XP 8 app upgrade guide (
  source of truth)
- `references/examples.md` — full `xplibs.*` alias tables (6 APIs + 24 libs), worked `build.gradle` examples (site app with version catalog;
  TS app with custom `dev` task), TypeScript wiring with `@enonic-types/*`
- `references/manual-schemes-migration.md` — comprehensive set of descriptor transformations (paths, `kind:` map, field renames, special
  cases) — read this when the migrator is unavailable or when reviewing what it produced
- <https://raw.githubusercontent.com/enonic/doc-xp/refs/heads/8.0/docs/release/upgrade.adoc> — full instance-level upgrade guide
  (dump/load, security, management API changes)
- `xp-app-debugger` skill — diagnose build/runtime errors after upgrade
- `enonic-cli` skill — full reference for every `enonic` command this skill uses (`project build`/`deploy`, `sandbox create`/`list`,
  `dump create`/`load` for the data side)
