# AsciiDoc conventions

Writing rules shared by every Enonic documentation set. Product-specific vocabulary and page templates are in each repository's
`AGENTS.md`.

## Page skeleton

```asciidoc
= Page title
include::.variables.adoc[]
:toc: right
:imagesdir: media

One or two informative sentences introducing the subject and scope, or the tutorial outcome.

== First section

Content.
```

- One level-0 title per page. Sections start at `==`.
- Every page has a short introduction after the title and header attributes/includes, before the first section heading.
- `include::.variables.adoc[]` goes directly below the title. From a subdirectory the path is `../.variables.adoc`.
- `:toc: right` on any page long enough to scroll. The build sets it as a default, but stating it keeps IDE previews consistent.
- Set `:imagesdir:` only on pages that have images.

## Links

- Between pages in the same documentation set: `<<path/to/page#,Label>>`. The path is relative to the current file and omits
  `.adoc`. From `docs/concepts/architecture.adoc` to `docs/release.adoc`: `<<../release#,Release notes>>`.
- To an anchor on another page: `<<path/to/page#anchor-id,Label>>`. To an anchor on the same page: `<<anchor-id,Label>>`.
- To another documentation set or an external site, use an absolute URL: `https://developer.enonic.com/docs/code[Code docs]`.
  For portal cross-links, follow the version rules below. Prefer shared URL attributes from `.variables.adoc`.
- Never append `^` to a link label. Every Enonic documentation set renders on the same portal as sibling navigation, and forcing
  a new tab removes user agency. Readers who want a new tab can middle-click or Cmd-click.

### Links between documentation sets

Cross-links lead to other documentation sets, tutorials, or portal pages outside the current set. Links between pages and
anchors within the same set are internal links.

Keep cross-links selective: they create dependencies between separately maintained content.

- Link when the reader needs an external prerequisite, an authoritative reference, or a relevant continuation.
- Briefly explain the concept locally so the current page remains understandable without following the link.
- Avoid linking incidental product mentions, repeating the same destination unnecessarily, or adding broad lists of related
  reading.
- Prefer the destination's landing page or relevant topic page. Link to a section anchor only when that precision materially
  helps. Use descriptive link labels.
- For a documentation package or tutorial as a whole, omit the version segment: `/docs/code`, not `/docs/code/stable`.
  The developer portal redirects the package URL to its stable version.
- For a deep link to a page inside the package, include the version segment: `/docs/code/stable/deep/path`. Select the version
  that matches the product and context being documented; do not omit it from deep links.
- Use shared URL attributes from `.variables.adoc` where applicable, so destinations can be maintained centrally.

This restraint does not apply to internal navigation within a documentation set, including links between its pages, section
anchors, and tutorial chapter transitions.

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

## Asset directories

Store images, diagrams, videos, audio, downloads, and other supporting files in `docs/media/` by default. Create the directory
only when there is an actual asset to store.

- Reuse the shared directory across pages. Do not create asset directories for individual pages or sections by default.
- If `media/` is needed for documentation pages—for example, `docs/media.adoc` with child pages under `docs/media/`—use
  `docs/images/` as the shared asset directory instead. This fallback may contain any supporting file type, despite its name.
- Use descriptive filenames that identify the subject, such as `content-studio-project-wizard.png`. Create subdirectories only
  when the number of assets makes the shared directory difficult to navigate.
- Reference shared assets instead of duplicating them. For images, set `:imagesdir:` to the relative path from the page to the
  shared asset directory.
- Do not create empty placeholder directories, and remove directories left empty after changes.
- Preserve established asset locations when editing existing documentation. Do not move files solely to adopt this convention,
  since their published URLs may be in use.

## Images

Use screenshots when they help the reader locate a control, understand a visual state, or verify a result. Avoid screenshots
that merely repeat the written instructions. Capture the relevant area while retaining enough context to orient the reader,
and keep text legible at the intended display width.

Keep essential instructions and expected results in the text; readers should not need the image to complete the task. When a
UI change makes a screenshot misleading, update or remove it.

- For the default shared directory, use `:imagesdir: media` on a page directly under `docs/`, or `:imagesdir: ../media` on
  `docs/topic/child.adoc`. Adjust the relative path for deeper pages or an established asset directory.
- Reference with the block macro `image::name.png[Alt text]`. Use the inline macro `image:name.svg[Alt,opts=inline]` only for
  badges and icons that belong inside a sentence.
- Keep image alt text to 125 characters or fewer, including spaces and punctuation. Describe the information the image conveys
  in its context. Avoid filenames and phrases such as "image of" or "screenshot of." Put longer explanations in the caption
  or surrounding prose.
- Always set an explicit display width in pixels for screenshots, regardless of their resolution. Capture new screenshots
  at 2× their intended display size and set the AsciiDoc width to half the captured pixel width: 1600 pixels displays at 800;
  800 pixels captured at 2× displays at 400.
- Existing screenshots captured at 1× still need an explicit width: an 800-pixel-wide screenshot intended to display at
  800 pixels uses `width=800`. Do not assume every existing screenshot was captured at 2×.

```asciidoc
// Captured at 1600 pixels wide; displayed at 800 pixels.
image::content-studio-project.png[Content Studio project, width=800]
```

### Screenshot formats and file sizes

Capture screenshots as PNG at 2× their intended display size. Aim for files under 500 KB; files from 500 KB to 1 MB are
acceptable when the detail is useful. Optimize any screenshot over 1 MB before committing.

Screenshots containing photographs or other detailed imagery can produce large PNG files. Convert these to WebP when it
meaningfully reduces file size. Prefer lossless WebP for text-heavy interfaces; use lossy compression only when text and UI
details remain clear at the intended display width.

Preserve the 2× pixel dimensions during conversion. Setting a smaller AsciiDoc display width does not reduce download size.
Crop unnecessary content before sacrificing readability. Commit the chosen image format without also adding an unused PNG
duplicate. Files over 2 MB after optimization should be rare and justified by necessary detail.

## Version badges

A badge marks the product version that introduced a feature.

- Place it inline at the far left of the paragraph or list item that first introduces the feature, before the explanatory text.
- Never put a badge in a heading.
- Label it with the product and version that introduced the feature: `image:xp-810.svg[XP 8.1.0,opts=inline]`, or
  `image:guillotine-9.svg[Guillotine 9,opts=inline]` for a Guillotine feature even when the page is about XP.
- Badge SVGs use the shared asset directory, normally `docs/media/`.

## Variables

`docs/.variables.adoc` holds attributes used across the set: product versions, minimum versions, and documentation base URLs.

```asciidoc
// Shared attributes. Dot-prefixed so asciidoctor does not compile it as a page.
:xp-version: 8.1
:guillotine-version: 9
:xp-docs: https://developer.enonic.com/docs/xp
:xp-docs-version: stable
:guillotine-docs: https://developer.enonic.com/docs/guillotine
:guillotine-docs-version: stable
```

Use `{xp-docs}[Enonic XP documentation]` for the package and `{xp-docs}/{xp-docs-version}/deep/path[Relevant topic]` for a deep
link. Keep the base URL unversioned and the documentation version label separate from the product version (`{xp-version}`).
Update the shared attributes, not individual pages, when a URL or version changes.

## Admonitions

- `NOTE:` for side information, `TIP:` for a shortcut, `WARNING:` for something that loses data or breaks a site, `IMPORTANT:`
  sparingly. One-line admonitions use the paragraph form; multi-paragraph ones use the `[NOTE]` block.

## Code examples and callouts

Use lowercase language identifiers in `[source,language]`. Prefer full names such as `typescript` and `javascript` over aliases.
Select the language of the snippet, not the product or tool it belongs to. Use normal product and language capitalization in
prose, such as TypeScript, Java, and Gradle.

| Content | Language identifier |
|---------|---------------------|
| TypeScript | `typescript` |
| JavaScript | `javascript` |
| Java | `java` |
| Gradle Groovy DSL (`build.gradle`) | `groovy` |
| Gradle Kotlin DSL (`build.gradle.kts`) | `kotlin` |
| YAML | `yaml` |
| JSON | `json` |
| GraphQL | `graphql` |
| File trees or plain output | `text` |

Give a block a filename or path as its `.Caption` when relevant; otherwise use a descriptive caption when the page has several
blocks. For example:

```asciidoc
.build.gradle
[source,groovy]
----
dependencies {
    include xplibs.scheduler
}
----
```

Use numbered callouts to connect specific lines in a code, configuration, or file-tree example to explanations below it.
Use them when a few lines need explanation, such as a required setting, a naming constraint, or behavior that is not obvious
from the code. Skip them for self-explanatory examples, short commands explained in surrounding text, or explanations that
apply to the whole block. Do not annotate every line or repeat what the code already says.

- Place each marker at the end of the relevant line. Use a suitable comment prefix where supported: `# <1>` in YAML or
  `// <1>` in TypeScript.
- Start numbering at 1 for each block and keep numbers consecutive.
- Put the matching callout list directly below the block, before unrelated prose. Every marker must have an explanation,
  and every explanation must have a corresponding marker.
- Explain meaning, purpose, or constraints. Keep each explanation short.
- Keep callout numbers separate from tutorial step numbers: steps describe actions; callouts explain the example.

```asciidoc
[source,text]
----
src/main/resources/
  cms/
    cms.yaml                 # <1>
    content-types/
      article/
        article.yaml
        article.svg          # <2>
----
<1> The application's CMS descriptor.
<2> An optional icon displayed in Content Studio.
```

For formats without comments, such as JSON, prefer surrounding prose when the raw example needs to remain directly copyable.
Review rendered examples to confirm that callouts match their explanations. Inside a tutorial step, keep the code block and
its callout list attached to that same step using list continuations.

## Diagrams

Flow and architecture diagrams are authored as Mermaid text and rendered to SVG; the rendered SVG is committed and referenced
with a normal `image::` macro.

- Keep the source next to the image it produces, dot-prefixed, for example `docs/media/.pipeline.mmd` rendering to
  `docs/media/pipeline.svg`. The importer still copies the source as an orphan media item, which is harmless.
- Use the ELK layout (`config: { layout: elk }` in the file's frontmatter). It honors subgraph `direction` and packs tighter
  than the default layout.
- Render without a global install, from the repository root:

  ```sh
  npx -y -p @mermaid-js/mermaid-cli -p @mermaid-js/layout-elk \
    mmdc -i docs/media/.pipeline.mmd -o docs/media/pipeline.svg -b transparent
  ```

  The first run downloads the CLI and a headless browser into the user's caches; nothing is added to the repository.
- Keep the render command in an AsciiDoc comment directly above the `image::` line so the recipe travels with the page.
- Re-render and commit both files after any edit.

## External references

Briefly summarize separately documented products rather than re-documenting them. Add a cross-link when the reader needs more
detail, following the guidance under Links between documentation sets. When a link is useful, use these standard targets:

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
