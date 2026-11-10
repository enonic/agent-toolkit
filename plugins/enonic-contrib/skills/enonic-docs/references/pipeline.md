# Publishing pipeline

How a `docs/` directory becomes pages on https://developer.enonic.com, and the files that control it.

## The workflow

Every repository that publishes documentation has `.github/workflows/enonic-docgen.yml`. The canonical template lives in
`enonic/.github` under `workflow-templates/enonic-docgen.yml`:

```yaml
name: Generate Documentation

on:
  push:
    branches:
      - master
    paths:
      - 'docs/**'
  workflow_dispatch:

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: enonic/release-tools/generate-docs@master
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          webhook-secret: ${{ secrets.DEVELOPER_PORTAL_WEBHOOK_SECRET }}
```

- `branches` must list every branch whose documentation is published. A repository that publishes a `5.x` version from a `5.x`
  branch lists both `master` and `5.x`; otherwise a docs fix on `5.x` never triggers a rebuild.
- `paths: docs/**` keeps code pushes in mixed repositories from rebuilding the documentation. Add the workflow file itself to
  the list if changes to it should trigger a run.
- `DEVELOPER_PORTAL_WEBHOOK_SECRET` must be available to the repository (it is normally an organization secret). Without it the
  build still publishes to `gh-pages` but the portal is not notified.

## What `generate-docs` does

1. Checks out the repository's **default branch** and reads `docs/versions.json` from there. Only the default branch's copy
   matters; `versions.json` on other branches is ignored.
2. If `docs/versions.json` is missing, it substitutes a single version labelled `stable` built from the default branch.
3. If no version carries `"latest": true`, the first entry gets it.
4. For each version: resolves `checkout` with `git rev-parse`, checks it out, copies the repository to a build directory and runs
   asciidoctor in `docs/` with:

   ```text
   asciidoctor --backend html5 --failure-level ERROR -a icons=font -a setanchors=true -a sectlinks=true
               -a encoding=utf-8 -a linkattrs=true -a idprefix= -a toc=right -a outfilesuffix=.ahtml '**/*.adoc'
   ```

   `--failure-level ERROR` means an AsciiDoc error (a missing include, an unresolved file in `image::`) fails the build. The
   glob does not match dot-prefixed files, so `.variables.adoc` is never compiled as a page of its own.
5. Copies the resulting `docs/` tree for each version to `<output>/<label>/`.
6. Pushes the output to the `gh-pages` branch, excluding `**/*.adoc` and `*/versions.json`.
7. Posts a webhook to developer.enonic.com naming the repository.

Everything else under `docs/`, including images, PDFs, JSON files and any stray file, is pushed to `gh-pages`.

## `versions.json`

```json
{
  "versions": [
    {
      "label": "next",
      "checkout": "master"
    },
    {
      "label": "stable",
      "checkout": "origin/5.x",
      "displayName": "5.x",
      "latest": true
    },
    {
      "label": "4.x",
      "checkout": "v4.2.0"
    }
  ]
}
```

| Field         | Meaning                                                                                                             |
|---------------|---------------------------------------------------------------------------------------------------------------------|
| `label`       | Used in the URL path and the version dropdown. `stable` is conventional for the current release.                     |
| `checkout`    | Any git ref: a branch (`origin/5.x`), a tag (`v4.2.0`) or a commit. The action runs with full history.               |
| `displayName` | Optional. Shown in the dropdown instead of the label; does not change the URL.                                       |
| `latest`      | Exactly one version must have `true`. It is the default version shown, and the one used in site search.             |

The label `next` is reserved for unreleased work. The portal does not let search engines index it, so use it for the next major
while it is in development.

### Version branches

Released majors are maintained on version branches (`5.x`, `6.x`); unreleased work is on the default branch. When a new major
ships: cut a branch for the outgoing major from the default branch, point `stable` at the new major, keep the outgoing branch
in `versions.json` under its own label, and add the new branch to the workflow's `branches` list.

A repository whose default branch is the current release and whose next major lives on a separate branch can invert this
(`stable` on `master`, `next` on `origin/6.x`); the action does not care, only the default branch's `versions.json` does.

## `menu.json`

```json
{
  "menuItems": [
    { "title": "Introduction", "document": "index" },
    {
      "title": "Concepts",
      "document": "concepts",
      "menuItems": [
        { "title": "Architecture", "document": "concepts/architecture" }
      ]
    },
    { "title": "Release Notes", "document": "release" }
  ]
}
```

- `document` is the page path relative to `docs/` without the `.adoc` extension.
- `menuItems` nests to any depth. A section entry normally points at its landing page (`concepts`) and lists its children.
- The portal builds the navigation only from this file. Pages that are published but not listed are reachable by URL only.
- Keep titles short; they are navigation labels, not page titles.

## From file path to URL

The portal's CMS decides where a documentation set lives (for example `/docs/xp/stable` or `/docs/next.xp/stable`). Below that
root, file paths map directly to URLs:

| File                             | URL below the documentation root |
|----------------------------------|----------------------------------|
| `docs/index.adoc`                | `/`                              |
| `docs/release.adoc`              | `/release`                       |
| `docs/concepts.adoc`             | `/concepts`                      |
| `docs/concepts/architecture.adoc`| `/concepts/architecture`         |

A section landing page is `docs/concepts.adoc` with children in `docs/concepts/`. The importer treats a directory with a
sibling `.ahtml` of the same name as that page's children. It does not support `index.adoc` inside subdirectories; only the root
`docs/index.adoc` is special.

## What the importer does with each file

The portal downloads the `gh-pages` branch as a zip and walks every file in each version directory:

| File                                         | Result                                                      |
|----------------------------------------------|-------------------------------------------------------------|
| `*.ahtml`                                    | A documentation page                                        |
| A directory with a sibling `<name>.ahtml`    | The children of that page                                   |
| Any other directory                          | A folder                                                    |
| `*.adoc`, `*.json`                           | Skipped (`.adoc` never reaches `gh-pages`; `.json` is read for `menu.json` only) |
| Anything else                                | A media item (images, PDFs, and any stray file)             |

Consequences:

- A dot prefix does not exclude a file from import. `.variables.adoc` is skipped because of its extension, not its name.
- Instruction files such as `AGENTS.md` placed under `docs/` are imported as orphan media. Keep them at the repository root, or
  ask for the file to be added to the action's exclusion list.
- Diagram sources and other tooling files under `docs/` become media items. Harmless, but avoidable by keeping them outside
  `docs/` or giving them a `.json` extension where that makes sense.

## Local preview

There is no committed local build. The CI run can be reproduced with the same container the action uses. From the repository
root:

```sh
docker run --rm --volume "$PWD:/documents" --workdir /documents/docs asciidoctor/docker-asciidoctor \
  asciidoctor --backend html5 --failure-level ERROR --trace \
  -a icons=font -a setanchors=true -a sectlinks=true -a encoding=utf-8 -a linkattrs=true \
  -a idprefix= -a toc=right -a outfilesuffix=.html '**/*.adoc'
```

This writes an `.html` file next to every `.adoc` for viewing in a browser, and fails on the same errors CI fails on. Remove the
generated files afterwards; do not commit them. Using `.html` locally instead of `.ahtml` keeps browsers happy and keeps the
output distinguishable from CI output.

Most IDEs also render AsciiDoc inline, which is enough for prose but does not catch include or image errors.

## Setting up documentation in a repository

1. Create `docs/index.adoc`, `docs/menu.json` and, if the set has shared values, `docs/.variables.adoc`.
2. Add `docs/versions.json` on the default branch if more than one version will be published.
3. Add `.github/workflows/enonic-docgen.yml` from the template, listing every published branch.
4. Make sure the webhook secret is available to the repository.
5. Run the workflow manually once (`workflow_dispatch`) and check that `gh-pages` appears.
6. Ask the portal maintainers to create the documentation entry in the CMS pointing at the repository, or to repoint an existing
   entry when documentation moves between repositories.

When documentation moves to a repository that is copied into user projects (a starter scaffolded with `degit`), add a
`degit.json` at the repository root with a `remove` action for `docs` so users do not receive the documentation source.
