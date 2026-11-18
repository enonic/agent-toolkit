---
name: enonic-docs
description: >
  Conventions for writing and maintaining Enonic reference documentation and tutorials:
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
For tutorials published in the Learn section, apply the shared language and page conventions together with the tutorial-specific
guidance below. Keep reference pages and tutorial chapters distinct.

## Language and tone

Always write in US English (`en-US`). Preserve exact spelling in code identifiers, API names, UI labels and quoted text.

Write for developers and LLMs. Make behavior, requirements, defaults and limitations explicit. Use consistent terminology,
name the subject clearly and define unfamiliar terms on first use. Identify each section's subject and dependencies so it can
be understood when retrieved independently. Tutorial chapters may build on earlier work; link to prerequisites rather than
repeating their instructions. Lead with what something does and when to use it. Distinguish requirements from recommendations
and optional choices.

Enonic is friendly, informal and serious about technical accuracy. Use everyday language, natural contractions, active voice
and concrete verbs. Be concise without becoming cryptic. Avoid corporate formality, marketing claims, inflated language and
forced enthusiasm. Avoid words such as "simply," "obviously" or "just" that can make difficult tasks sound trivial. Explain
consequences and constraints without dramatizing them. Use prose for concepts, lists for steps or parallel points, and tables
for structured reference information.

Let personality appear sparingly. A playful example or an established character voice, such as Juke calling himself an
"overlord," can make documentation feel like Enonic. Keep humor out of requirements, warnings and statements of API behavior.
The technical meaning must remain clear without understanding the joke.

### Perspective in reference documentation

Make the product, feature or configuration the subject: "The service returns..." or "This setting controls..." Use "you" for
the reader's choices or responsibilities: "You can override the default." Avoid authorial "we," "let's" and walkthrough
instructions such as "now do this" or "next, add..." Describe behavior, requirements and configuration directly, without assuming
that the reader has followed a sequence. Reserve "we" for statements explicitly about Enonic as an organization where that
attribution matters.

| Avoid | Prefer |
|-------|--------|
| Now add the following property to your configuration. | The `timeout` property sets the request timeout in milliseconds. |
| Next, we'll enable authentication. | Authentication requires... |
| Let's look at the available options. | The available options are... |

### Emoji

Emoji can express warmth, celebrate progress, and support Enonic's personality. Use them deliberately:

- **Tutorials:** An occasional emoji is welcome in a milestone acknowledgment or closing celebration. Save the strongest
  celebration for the final chapter.
- **Character voice:** Emoji can support an established character's personality, such as Juke's playful commentary.
- **Reference documentation:** Keep emoji out of technical explanations, API tables, and configuration instructions.
- **Warnings and requirements:** Use standard documentation admonitions. Never rely on emoji to communicate severity, status,
  or required action.
- **Navigation and code:** Keep emoji out of menu labels, identifiers, and copyable commands unless they are part of the actual
  subject being documented.

Keep them sparse—usually one is enough for a celebratory passage. The words must carry the full meaning without the emoji,
so the text remains clear for screen-reader users, developers, and LLMs. Avoid strings of emoji, ambiguous symbols, or emoji
used in place of words.

## Menu labels, page titles, and introductions

Menu labels and page titles serve different purposes:

- **Menu labels** are short and easy to scan. Use a concise topic or task name.
- **Page titles** clearly identify the page's subject or task. They can be more descriptive than the menu label:
  `Setting up Enonic`. Keep chapter numbers in the menu, not in the page title.
- **Keep them aligned.** The wording can differ, but the menu label and page title must clearly refer to the same topic.

Every page must open with a short introduction directly below the title and any AsciiDoc attributes or includes, before the
first section heading. Usually one or two sentences are enough.

- **Reference pages:** Explain what the subject is and what the page covers.
- **Tutorial pages:** Explain what the reader will accomplish. Separately identify required results from earlier chapters and
  link to those chapters when useful.
- **Section landing pages:** Explain the section's scope and what readers can find in its child pages.

Make the introduction informative on its own. Avoid merely repeating the title or using filler such as "This page contains
information about..."

### Menu depth

Prefer at most two menu levels: a top-level page or section and its children. A third level is acceptable when it groups a
large set of related pages and makes navigation easier to scan, as in `Schema system > Form items > TextLine`. Count top-level
entries as level one. Avoid deeper nesting; reorganize sections or use links from landing pages instead. This is an editorial
convention, not a technical limit of `menu.json`.

### Menu and file structure

Keep menu and file structure aligned by default. A section normally consists of a landing page (`topic.adoc`) and a directory
containing its child pages (`topic/child.adoc`), grouped beneath that section in the menu.

The menu defines navigation; file paths identify documents. Their hierarchies do not technically have to match. When a
different menu grouping improves navigation or preserves established URLs, keep the existing files and point menu entries to
their actual paths. Do not move files solely to match the menu, since moves can change published URLs.

The two-level preference and optional third level apply to menu nesting, not filesystem depth. The file-layout rules for
section landing pages still apply, including when the menu groups those pages differently.

### Documentation entry point

Every documentation set has a root `docs/index.adoc`. Include it as the first entry in `docs/menu.json`, with the label
`Introduction` and the document path `index`, without a chapter number. Use a descriptive page title such as "Next.js website
tutorial" or "Guillotine reference".

- **Reference docs:** Explain what the product or library does, who the documentation is for, and link to useful starting points.
- **Tutorials:** Explain what the reader will build, the prerequisites, and the expected final result. End with a descriptive
  link to chapter 1. Keep setup tasks in the numbered chapters.

## Tutorial conventions

Tutorials belong in the Learn section, separate from reference documentation. The conventions below apply to tutorial material;
do not bring their walkthrough structure into reference pages.

### Perspective and instructions

Address the reader consistently as "you" and use direct imperatives for steps: "Create a content type." Avoid switching to
"we" or "let's."

Use sequencing language when it helps the reader understand progression. "Next" is useful in a closing transition, but most
individual instructions do not need "now" or "next."

### Sequence and navigation

Tutorials guide the reader through a sequence of chapters, each published as a page and building on earlier work.

- After the unnumbered Introduction, number chapters in the menu with consecutive labels such as `1 - Enonic setup`
  and `2 - GraphQL API`.
- Keep the menu order aligned with the intended learning sequence. Supporting pages outside that sequence do not need numbers.
- When adding, moving, or removing a chapter, update the menu numbering and affected links between chapters.

### Tasks and steps

Chapters contain tasks; tasks contain numbered steps. Chapter numbers and step numbers are separate.

- Give each task one clear outcome and a heading beginning with `Task:` followed by a short action, such as
  `Task: Install the CLI` or `Task: Render rich text`. A chapter may contain several tasks.
- Use `== Task: ...` directly within a chapter, or `=== Task: ...` beneath a topic section. Do not skip heading levels.
- Introduce the relevant concept and task outcome before the steps. Keep this brief when the surrounding text already
  provides the context.
- Use an ordered list, starting at 1 for each task. Begin each step with a **short, bold action label**, such as
  "Create the query" or "Verify the result," followed by instructions. Short instructions can follow a hyphen on the same
  line; longer explanations belong in paragraphs beneath it.
- Keep commands, code, screenshots, and notes attached to the step they support. Identify file paths and working directories
  where needed.
- End the task with an observable result or verification step. Use "Verify the rendering" rather than a numbered item called
  "That's it!"
- Keep the chapter summary and transition outside the task's numbered list.

Use AsciiDoc `.` markers for automatic numbering and a standalone `+` to attach each additional block to its step. This keeps
numbering continuous around code, images, and explanatory paragraphs:

```asciidoc
== Task: Verify the CLI

. *Check the installed version* - Run this command in your terminal:
+
[source,shell]
----
enonic -v
----
+
The output should show the installed CLI version.

. *Inspect the available commands* - Run `enonic` without arguments.
+
The CLI displays its help text and available commands.
```

### Summaries and transitions

End every numbered chapter with a `Summary` section. Briefly describe what the reader has created, configured, or learned. Be
concrete; do not introduce new tasks in the summary.

For every chapter except the final one, close with a transition explaining what the reader will do next and linking to the
following page. Use a descriptive link label, and make sure the destination matches the next chapter in the menu.

```asciidoc
== Summary

You've created a local Enonic environment, deployed an application,
and opened its sample content in Content Studio.

Next, you'll <<graphql-api#,query that content with the GraphQL API>>.
```

A little warmth is welcome, but "Great job!" or "Congrats!" must not replace a useful summary of the result.

### Completion and celebration

End the final tutorial chapter by celebrating what the reader has accomplished. Be warm, specific, and proportionate. Name the
working result and make it clear that the tutorial is complete.

A celebratory emoji is welcome. Avoid exaggerated praise or suggesting that completing the tutorial means the reader has
mastered the entire product.

For example:

> You did it! 🎉 You've built a Next.js site that fetches and renders content from Enonic, with previews working in Content Studio.

After the celebration, offer relevant further reading or optional challenges where useful. Clearly distinguish these from
required steps so the reader can finish with a sense of completion.

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

1. **No empty stubs.** Every page listed in `docs/menu.json` must have substantive content. A title and "TODO" do not help the
   reader. If content is not ready, leave the page out of the menu.

2. **Self-contained pages.** Each page must make sense on its own to a human or an LLM. Summarize the key concept locally and
   link to a full reference when the reader needs more detail. Avoid bare "see the external docs" pointers with no context.

3. **Keep reference documentation and tutorials distinct.** Tutorials and getting-started guides live in the Learn section of
   developer.enonic.com and build on top of the reference documentation. Do not duplicate tutorial material in reference pages.

4. **Update `docs/menu.json` whenever a page is added, renamed, moved or removed.** The portal's navigation is built only from
   this file. A page that is not in the menu is published but absent from navigation.

5. **Section landing pages share the basename of their directory.** A section with children is `docs/topic.adoc` plus
   `docs/topic/child.adoc`. The importer does not support `index.adoc` inside subdirectories; only the root `docs/index.adoc`
   exists.

6. **Underscores break inline formatting.** AsciiDoc parses paired underscores as italic, so any identifier, path or URL
   placeholder with `_` can silently swallow the rest of the line. Wrap such strings in single-plus passthrough,
   `+text_with_underscores+`, combined with backticks for monospace: `` `+/_/service/+` ``. Content inside a fenced source block
   is safe. When in doubt, wrap it.

7. **Internal links are relative; links open in the same tab.** Link between `.adoc` files in the same documentation set with
   `<<path/to/doc#,Label>>` and to anchors with
   `<<path/to/doc#anchor,Label>>`. Never add the `^` suffix to a link label; all Enonic documentation renders on the same portal
   as sibling navigation, and forcing a new tab removes user agency.

8. **Use one shared asset directory by default.** Store all supporting file types in `docs/media/`, creating it only when needed.
   If `media/` is used for documentation pages, use `docs/images/` for all asset types instead. Avoid per-page or per-section
   asset directories and preserve established asset locations. Set `:imagesdir:` to the relative path from the page to the
   asset directory. The full convention and examples are in `references/asciidoc-conventions.md`.

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

12. **Cross-link selectively; do not re-document other products.** Briefly summarize the concept and link to another
    documentation set, tutorial, or portal page only when the reader needs that destination. These cross-links create
    maintenance dependencies; internal links within the current set are not subject to this restraint. The full guidance and
    standard targets are in `references/asciidoc-conventions.md`.

13. **Version badges mark where a feature was introduced.** Place an inline badge image at the far left of the paragraph or list
    item that first introduces the feature, never in a heading, labeled with the product and version that introduced it.

14. **Use callouts for specific lines that need explanation.** Keep markers and explanations matched and consecutive within
    each block. Skip callouts for self-explanatory examples. Follow the pattern in `references/asciidoc-conventions.md`.

## Page checklist

Before finishing a change under `docs/`:

- Prose uses `en-US`, the friendly, informal tone above, and the perspective appropriate to reference documentation or tutorials.
- Every page opens with a short, informative introduction before its first section heading.
- Menu labels are concise and align with descriptive page titles; tutorial chapter numbers appear only in the menu.
- Menus normally have at most two levels; a third level has a clear grouping purpose, and deeper nesting is avoided.
- The root `docs/index.adoc` is the first menu entry, labeled `Introduction` and unnumbered.
- Tutorial tasks have action headings and numbered steps with bold action labels and an observable result.
- Numbered chapters end with a summary and a link to the following chapter; the final chapter celebrates completion.
- The page has a level-0 title (`= Title`), `:toc: right` where the page is long enough to need it, and `:imagesdir:` if it has
  images.
- `include::.variables.adoc[]` sits below the title if the page uses attributes.
- Every new or renamed page is in `docs/menu.json` with the `document` value equal to its path without `.adoc`.
- No identifier, path or placeholder with an underscore sits in prose outside a `+...+` passthrough or a source block.
- No link label ends in `^`.
- Cross-links serve a reader need and match the documented version; internal navigation remains intact.
- Code callouts match their explanations and remain attached to the relevant tutorial step where applicable.
- Images referenced from the page exist at the paths resolved through its `:imagesdir:`.
- Assets reuse the shared directory or established locations; no unnecessary or empty asset directories are introduced.
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
  media/                              Shared assets of all types, only when needed; images/ if media/ holds pages
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
