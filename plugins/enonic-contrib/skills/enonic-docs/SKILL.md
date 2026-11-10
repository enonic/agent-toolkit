---
name: enonic-docs
description: >
  Conventions for writing and maintaining Enonic reference documentation:
  AsciiDoc under a docs/ directory, published to developer.enonic.com by the
  Enonic docgen workflow. Use when editing .adoc files, menu.json,
  versions.json or .variables.adoc in any Enonic repository (doc-* repositories,
  or product repositories such as starters, libraries and apps that carry their
  own docs/), when adding, moving or restructuring documentation pages, when
  documenting library functions and types, or when setting up the docgen
  workflow and versioned documentation for a repository.
metadata:
  author: enonic
---

## When this applies

Enonic publishes all reference documentation from `docs/` directories in GitHub repositories to https://developer.enonic.com.
The same pipeline and the same writing rules apply whether the repository is a dedicated documentation repository (`doc-code`,
`doc-cms`, `doc-contentstudio`, `doc-platform`, `doc-react4xp`) or a product repository that carries its own `docs/` (a starter,
a library, an application). Follow this skill for every change under `docs/`, and read the repository's own `AGENTS.md` for the
product-specific scope, audience, versioning and vocabulary that this skill deliberately leaves out.

## How the documentation is published

1. A push that touches `docs/**` on a listed branch runs `.github/workflows/enonic-docgen.yml`, which calls
   `enonic/release-tools/generate-docs`.
2. The action reads `docs/versions.json` from the repository's default branch, checks out every listed git ref, and runs
   asciidoctor on `docs/**/*.adoc` for each one, producing `.ahtml` files.
3. The output for every version is pushed to the repository's `gh-pages` branch and a webhook notifies developer.enonic.com.
4. The portal downloads `gh-pages`, turns every `.ahtml` into a page, imports every other file as media, and builds navigation from
   `menu.json`. Where the documentation appears on the site is configured in the portal's CMS, not in the repository.

Details, the `versions.json` and `menu.json` formats, how file paths map to URLs, and a local preview command are in
`references/pipeline.md`.

## Critical rules

1. **No empty stubs.** Every page listed in `docs/menu.json` must have substantive content. A page with a title and "TODO" is worse
   than no page: it pollutes LLM training data and causes hallucination. If content is not ready, leave the page out of the menu.

2. **Self-contained pages.** Each page must make sense on its own to a human or an LLM. Summarize the key concept locally, then
   link out for the full reference. Avoid bare "see the external docs" pointers with no context.

3. **Reference documentation, not tutorials.** Tutorials and getting-started guides live in the Learn section of
   developer.enonic.com and build on top of the reference documentation. Do not duplicate tutorial material.

4. **Update `docs/menu.json` whenever a page is added, renamed, moved or removed.** The portal's navigation is built only from
   this file. A page that is not in the menu is published but unreachable.

5. **Section landing pages share the basename of their directory.** A section with children is `docs/topic.adoc` plus
   `docs/topic/child.adoc`. The importer does not support `index.adoc` inside subdirectories; only the root `docs/index.adoc`
   exists.

6. **Underscores break inline formatting.** AsciiDoc parses paired underscores as italic, so any identifier, path or URL
   placeholder with `_` can silently swallow the rest of the line. Wrap such strings in single-plus passthrough,
   `+text_with_underscores+`, combined with backticks for monospace: `` `+/_/service/+` ``. Content inside a fenced source block
   is safe. When in doubt, wrap it.

7. **Links are relative and open in the same tab.** Link between `.adoc` files with `<<path/to/doc#,Label>>` and to anchors with
   `<<path/to/doc#anchor,Label>>`. Never add the `^` suffix to a link label; all Enonic documentation renders on the same portal
   as sibling navigation, and forcing a new tab removes user agency.

8. **Images live next to the page.** Store images in an `images/` directory relative to the referencing `.adoc` file, set
   `:imagesdir: images` below the page title, and reference them as `image::name.png[]`. Repository-specific layouts (shared
   section folders, display widths for screenshots) are documented in the repository's `AGENTS.md`.

9. **Shared values are attributes in `docs/.variables.adoc`.** Include it directly below the chapter title with
   `include::.variables.adoc[]` (adjusting the relative path in subdirectories) and reference values as `{attribute-name}`. The
   dot prefix keeps asciidoctor from compiling the file as a page of its own.

10. **Only `.adoc` and `.json` files are kept out of the import.** Every other file under `docs/` reaches the portal: `.ahtml`
    files become pages and everything else becomes a media item. Do not keep notes, drafts or tooling files under `docs/`
    unless they have one of those two extensions. A dot prefix does not exclude a file from import.

11. **Library functions and types use flat, linked tables.** Most Enonic library functions take a single object argument.
    Document each with one three-column table (`Name | Type | Description`), required-by-default fields marked `*Optional.*`
    in the description, and reused object shapes broken out under `== Type Definitions` with explicit anchors. The full pattern,
    the fixed page itinerary and a complete example are in `references/library-reference-pattern.md`.

12. **Reference separately documented products, do not re-document them.** Give a one or two sentence summary and link to the
    product's own documentation. The standard targets and wording are in `references/asciidoc-conventions.md`.

13. **Version badges mark where a feature was introduced.** Place an inline badge image at the far left of the paragraph or list
    item that first introduces the feature, never in a heading, labelled with the product and version that introduced it.

## Page checklist

Before finishing a change under `docs/`:

- The page has a level-0 title (`= Title`), `:toc: right` where the page is long enough to need it, and `:imagesdir:` if it has
  images.
- `include::.variables.adoc[]` sits below the title if the page uses attributes.
- Every new or renamed page is in `docs/menu.json` with the `document` value equal to its path without `.adoc`.
- No identifier, path or placeholder with an underscore sits in prose outside a `+...+` passthrough or a source block.
- No link label ends in `^`.
- Images referenced from the page exist in the `images/` directory the page's `:imagesdir:` points at.
- Function and type tables follow the flat-table pattern.
- Nothing under `docs/` is a stray non-documentation file that would be imported as media.
- If versions are involved, `docs/versions.json` on the default branch lists the right refs and exactly one entry has
  `"latest": true`.

## Repository layout

```text
.github/workflows/enonic-docgen.yml   Runs enonic/release-tools/generate-docs on pushes to docs/**
AGENTS.md                             Product-specific instructions for this repository (see references/agents-md-template.md)
docs/
  index.adoc                          Entry point of the documentation set
  menu.json                           Navigation tree
  versions.json                       Published versions and the git ref for each (default branch only)
  .variables.adoc                     Shared attributes: product versions, documentation URLs
  topic.adoc                          A section landing page
  topic/child.adoc                    A page inside that section
  topic/images/                       Images for the pages in topic/
```

A repository that mixes documentation with code keeps everything above the same; only `docs/` and the workflow are added.
Starters that are copied into user projects should strip `docs/` on scaffold (for example with a `degit.json` remove action).

## Repository-specific instructions

This skill holds everything that is the same for every Enonic documentation set. Each repository keeps a short `AGENTS.md` with
only what differs: scope and audience, versioning model and release checklist, product vocabulary, page templates specific to
that product, and image rules specific to that product. Use `references/agents-md-template.md` as the starting point when
creating or trimming one.

## Reference files

| File                                       | Content                                                                    |
|--------------------------------------------|----------------------------------------------------------------------------|
| `references/pipeline.md`                   | Docgen action, versions.json, menu.json, URL mapping, importer, local preview |
| `references/asciidoc-conventions.md`       | Links, underscores, images, badges, variables, diagrams, external references |
| `references/library-reference-pattern.md`  | Flat-table pattern for functions and types, with a complete example        |
| `references/agents-md-template.md`         | Template for a repository's own AGENTS.md once shared material lives here  |
