# AsciiDoc conventions

Writing rules shared by every Enonic documentation set. Product-specific vocabulary and page templates are in each repository's
`AGENTS.md`.

## Page skeleton

```asciidoc
= Page title
include::.variables.adoc[]
:toc: right
:imagesdir: images

One or two sentences saying what this page covers and who it is for.

== First section

Content.
```

- One level-0 title per page. Sections start at `==`.
- `include::.variables.adoc[]` goes directly below the title. From a subdirectory the path is `../.variables.adoc`.
- `:toc: right` on any page long enough to scroll. The build sets it as a default, but stating it keeps IDE previews consistent.
- Set `:imagesdir:` only on pages that have images.

## Links

- Between pages in the same documentation set: `<<path/to/page#,Label>>`. The path is relative to the current file and omits
  `.adoc`. From `docs/concepts/architecture.adoc` to `docs/release.adoc`: `<<../release#,Release notes>>`.
- To an anchor on another page: `<<path/to/page#anchor-id,Label>>`. To an anchor on the same page: `<<anchor-id,Label>>`.
- To another Enonic documentation set or any external site: `https://developer.enonic.com/docs/xp/stable/...[Label]`. Prefer an
  attribute from `.variables.adoc` for the base URL so it can be updated in one place.
- Never append `^` to a link label. Every Enonic documentation set renders on the same portal as sibling navigation, and forcing
  a new tab removes user agency. Readers who want a new tab can middle-click or Cmd-click.

## Underscores

AsciiDoc treats paired underscores as italic markers. A lone `_` opens an italic run that swallows the rest of the line, and
`foo_bar_baz` renders as `foo*bar*baz`. This hits identifiers, paths and URL placeholders constantly.

- Wrap the string in single-plus passthrough: `+text_with_underscores+`.
- For monospace, combine with backticks: `` `+/_/service/+` ``, `` `+last_event_id+` ``, `` `+http_management_port+` ``.
- The rule applies in prose, list items, table cells, link labels and example URL patterns.
- Content inside a fenced source block (`----`) is safe.
- Do not wrap a whole line that also contains `*bold*`, `<<cross-references>>` or `` `monospace` ``: the passthrough disables all
  of them. Wrap only the substring that contains the underscore.

When in doubt, wrap it.

## Images

- Store images in an `images/` directory relative to the referencing page, and set `:imagesdir: images` on the page.
- Reference with the block macro `image::name.png[Alt text]`. Use the inline macro `image:name.svg[Alt,opts=inline]` only for
  badges and icons that belong inside a sentence.
- Give screenshots a display width when the stored image is high resolution; the convention for a given product (for example
  half the stored width) is in that repository's `AGENTS.md`.
- Shared assets used across sections, such as version badges, live in `docs/images/` and are referenced relative to the page's
  `:imagesdir:`. Do not duplicate them into section folders.
- Do not leave empty `images/` directories behind when pages move.

## Version badges

A badge marks the product version that introduced a feature.

- Place it inline at the far left of the paragraph or list item that first introduces the feature, before the explanatory text.
- Never put a badge in a heading.
- Label it with the product and version that introduced the feature: `image:xp-810.svg[XP 8.1.0,opts=inline]`, or
  `image:guillotine-9.svg[Guillotine 9,opts=inline]` for a Guillotine feature even when the page is about XP.
- Badge SVGs are shared assets in `docs/images/`.

## Variables

`docs/.variables.adoc` holds attributes used across the set: product versions, minimum versions, and documentation base URLs.

```asciidoc
// Shared attributes. Dot-prefixed so asciidoctor does not compile it as a page.
:xp-version: 8.1
:guillotine-version: 9
:xp-docs: https://developer.enonic.com/docs/xp/stable
:guillotine-docs: https://developer.enonic.com/docs/guillotine/stable
```

Reference them as `{xp-version}` and `{xp-docs}/...`. Update the file, not the pages, when a version changes.

## Admonitions and callouts

- `NOTE:` for side information, `TIP:` for a shortcut, `WARNING:` for something that loses data or breaks a site, `IMPORTANT:`
  sparingly. One-line admonitions use the paragraph form; multi-paragraph ones use the `[NOTE]` block.
- Source blocks carry a language: `[source,typescript]`, `[source,yaml]`, `[source,json]`, `[source,graphql]`. Give a block a
  caption with a `.Caption` line above it when the page has several.
- Numbered callouts (`<1>`) are the preferred way to explain the lines of a schema or configuration example.

## Diagrams

Flow and architecture diagrams are authored as Mermaid text and rendered to SVG; the rendered SVG is committed and referenced
with a normal `image::` macro.

- Keep the source next to the image it produces, dot-prefixed, for example `docs/web/images/.pipeline.mmd` rendering to
  `docs/web/images/pipeline.svg`. The importer still copies the source as an orphan media item, which is harmless.
- Use the ELK layout (`config: { layout: elk }` in the file's frontmatter). It honours subgraph `direction` and packs tighter
  than the default layout.
- Render without a global install, from the repository root:

  ```sh
  npx -y -p @mermaid-js/mermaid-cli -p @mermaid-js/layout-elk \
    mmdc -i docs/web/images/.pipeline.mmd -o docs/web/images/pipeline.svg -b transparent
  ```

  The first run downloads the CLI and a headless browser into the user's caches; nothing is added to the repository.
- Keep the render command in an AsciiDoc comment directly above the `image::` line so the recipe travels with the page.
- Re-render and commit both files after any edit.

## External references

Reference separately documented products with a one or two sentence summary and a link; do not re-document them. The standard
targets:

| Product                      | Role in the text                                                              | Link to                                        |
|------------------------------|-------------------------------------------------------------------------------|------------------------------------------------|
| Guillotine                   | The primary headless GraphQL API for querying content                         | Guillotine docs for schema, queries, config    |
| Enonic XP CMS                | Content, schemas, media, pages, JSON structures, advanced queries              | CMS docs                                       |
| Enonic XP platform           | Node API, clustering, exports, deployment, low-level platform concerns         | XP docs                                        |
| Enonic application development | Implementations, build tooling, framework APIs, libraries                   | Developer (code) docs                          |
| Content Studio               | The editorial user interface                                                  | Content Studio docs                            |
| Tutorials                    | Step-by-step guides that build on the reference documentation                 | The Learn section of developer.enonic.com      |
| Third-party frameworks       | Next.js, React, GraphQL and similar                                           | Their own documentation; explain only what is Enonic-specific |

Put the base URLs in `.variables.adoc` and reference them as attributes.

## Terminology

- Applications running on Enonic XP are **Enonic applications**, never "XP applications" or "XP apps". After first mention,
  "application" or "app" is fine.
- Say **Content Studio**, **Guillotine**, **Enonic XP** with those capitalizations.
- Code examples for Enonic applications are TypeScript.
- Prefer flowing prose over mechanical term substitution; once a file path is on the page, "the file" is a fine back-reference.
