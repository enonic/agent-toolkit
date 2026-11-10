# Template for a repository's AGENTS.md

Once the shared conventions live in this skill, each documentation repository keeps a short `AGENTS.md` with only what is
specific to that product. Copy the template, delete the sections that do not apply, and keep it under about 60 lines. A
`CLAUDE.md` containing the single line `@AGENTS.md` makes the same file apply to clients that read that name.

Where the documentation lives inside a product repository (a starter, a library, an application) rather than a `doc-*`
repository, put this file at `docs/AGENTS.md` only if the repository already has a root `AGENTS.md` for a different audience,
and remember that the importer copies it as media unless it is excluded (see `references/pipeline.md`). Otherwise keep it at
the repository root.

```markdown
# Agent instructions for <Product> documentation

This repository contains the reference documentation for **<Product>**, written in AsciiDoc and published to
https://developer.enonic.com/docs/<product>.

Shared conventions for Enonic documentation (publishing pipeline, menu and version files, AsciiDoc rules, library reference
tables) are in the `enonic-docs` skill from the `enonic-contrib` plugin of https://github.com/enonic/agent-toolkit. Install it
and follow it for every change under `docs/`. The rules below are the ones specific to this product, plus the few shared rules
that must hold even without the skill.

## Scope and audience

<What this documentation covers, and what it deliberately leaves to other documentation sets.>
<Who reads it, and which secondary audience it should still make sense to.>

## Versioning

<Which product version the documentation follows, how version branches map to `docs/versions.json`, and what `next` means
here.>

### Release checklist

1. <Steps to take in this repository when a new product major ships.>

## Content guidelines

<Product-specific framing, for example "answer what it is, how it is configured, and what the data looks like" for a CMS
concept, or "document majors only, never patch alignment" for a multi-component product.>

### Vocabulary

<Terms to use and terms to avoid, with the reason.>

### Page templates

<Fixed structures for families of pages in this set, such as the chapter order for a form-item page.>

## Key conventions specific to this repository

- **Images:** <Layout and sizing rules that differ from the default, such as a shared `images/` folder per section or display
  widths for screenshots.>
- **External references:** <Product-specific link targets, such as a tutorial that builds on this documentation.>

## Must-know rules even without the skill

- Every page in `docs/menu.json` has real content; add new pages to the menu.
- A section landing page is `docs/topic.adoc` with children in `docs/topic/`; no `index.adoc` in subdirectories.
- Wrap identifiers containing `_` in `+...+` outside source blocks.
- Use relative `<<path#,Label>>` links and never a `^` suffix.
- Only `.adoc` and `.json` files under `docs/` stay out of the published site; everything else becomes a page or a media item.
```

## What to remove from an existing AGENTS.md

When trimming a repository's current file against this skill, these sections are fully covered here and can be deleted:

- "Build, Test, and Lint" (CI build, no local preview, validation in CI)
- "High-Level Architecture" (source directory, format, publishing, location, URL structure, navigation, versioning, variables,
  entry point)
- Generic "LLM-readability" bullets (no empty stubs, self-contained pages, consistent structure)
- Generic "External references" bullets for Guillotine, XP, CMS, Content Studio and application development
- "Key Conventions" bullets for version badges, images, menu updates, links, variables, underscores, Mermaid diagrams and the
  library-function table pattern

Keep anything that names a product, a version, a page family, a vocabulary choice, or a release step.
