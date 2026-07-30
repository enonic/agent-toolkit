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
metadata:
  author: enonic
  xp-version: "7.x → 8.x"
---

# Upgrade an Enonic XP 7 app to XP 8

Read `references/upgrade-workflow.md` completely before taking any action. It is the canonical ordered workflow and contains the safety
gates, inventory and planning requirements, execution sequence, validation rules, cleanup confirmation, deployment choices, and detailed
XP 7-to-8 change reference.

Use these supporting references when the workflow directs you to them:

- `references/examples.md` for dependency aliases, worked Gradle examples, and TypeScript wiring.
- `references/manual-schemes-migration.md` for descriptor transformations when reviewing migrator output or migrating manually.

Do not skip or reorder the workflow's detect, inventory, plan, execute, validate, cleanup, and deploy phases.
