# Project websites (`-f project`)

A course catalog page built from a `project.yaml`, with per-course downloads.

## 4. Project Website (`project.yaml`)

**Every `url` must be reachable over `http(s)`.** The exporter hands each URL to LiaScript, which downloads it; a local path (`url: courses/intro/README.md`) aborts the **whole** project export with "Export failed: it stopped without writing any output". Use `raw.githubusercontent.com` URLs (needed for SCORM/IMS/xAPI/H5P/APK anyway) — so the courses must be pushed before the project page can be built.

A project website is a single `index.html` that aggregates multiple LiaScript courses into a searchable, filterable catalog.

### 4.1 Full project.yaml Reference

```yaml
# Page title — supports HTML
title: >
  <span style="background-color: rgba(0,106,179,0.75); padding: 5px; color: white">
    My OER Collection
  </span>

# Subtitle / description — supports HTML
comment: >
  <br>
  <span style="background-color: rgba(0,106,179,0.75); padding: 5px; color: white">
    Interactive courses made with LiaScript
  </span>

# Page header image (local file or URL)
logo: logo.jpg

# Browser tab favicon or social media icon (URL recommended)
icon: https://example.com/icon.svg

# Optional sticky navigation bar
navbar:
  brand: My OER Collection           # text/logo on the left
  background: "#0B6E75"              # optional bar color (default: #0B6E75)
  theme: dark                        # dark (white text) | light (dark text)
  links:
    - label: Home
      url: "#"
    - label: Section 1
      url: "#section-1"

# Footer — supports HTML
footer: >
  Made with LiaScript —
  <a href="https://liascript.github.io" target="_blank">https://LiaScript.github.io</a>

# Social media / OpenGraph metadata
# If omitted, title/comment/logo are used. Disable with --project-no-meta
meta:
  title: My OER Collection
  description: A collection of interactive open educational resources
  # image: https://example.com/og-image.jpg

# Main course collection
collection:
  # Simple course entry — metadata auto-extracted from the LiaScript header
  - url: https://raw.githubusercontent.com/username/repo/main/README.md

  # Course with overridden metadata
  - url: https://raw.githubusercontent.com/username/repo2/main/README.md
    title: Custom Title
    comment: Custom description shown on the card.
    logo: https://example.com/custom-logo.jpg   # leave empty (logo:) to hide image
    tags:
      - Tutorial
      - Beginner

  # Course that lives in a sub-folder of a larger repository:
  # pack only that folder into SCORM/IMS/xAPI/H5P/APK (see §4.5)
  - url: https://raw.githubusercontent.com/username/monorepo/main/courses/intro/README.md
    path: courses/intro

  # Per-course export override (long flag names without --)
  - url: https://raw.githubusercontent.com/username/repo3/main/README.md
    arguments:
      - pdf-format: A3
      - project-generate-scorm2004: true
      - scorm-organization: My Organization
      - project-generate-pdf: false   # disable PDF for this specific course

  # HTML separator / section header between course groups
  - html: >
      <hr>
      <h1>Programming Courses</h1>
      <p>Learn various languages and paradigms.</p>

  # Sub-collection (grouped courses with optional grid layout)
  - title: Python Track
    comment: From beginner to advanced Python
    grid: true     # smaller preview cards in a grid layout
    collection:
      - url: https://raw.githubusercontent.com/username/python-intro/main/README.md
        tags:
          - Beginner
      - url: https://raw.githubusercontent.com/username/python-advanced/main/README.md
        tags:
          - Advanced
```

### 4.2 Tags and the category filter

The filter in the page header lists the tags of all courses. A course's tags come from **either** its `tags:` in `project.yaml` **or**, if that is missing, the `tags:` of its LiaScript header — `tags:` in `project.yaml` replaces the header tags, it does not add to them. Tags at the top level of `project.yaml` or on a group are **ignored**. The filter shows the tags in lower case ("musik"); the cards show them as written. Without any tag the filter is not shown.

Tags in the LiaScript course header:

```markdown
<!--
author:  Your Name
email:   your.email@example.com
version: 1.0.0
language: en
narrator: US English Female
comment: Introduction to Python programming
tags: Python, Programming, Beginner, Computer Science
-->
```

### 4.3 Project Export CLI Options

```bash
# Basic project website
liaex -i project.yaml --format project --output index

# With PDF generation for every course
liaex -i project.yaml --format project --output index --project-generate-pdf

# With SCORM 1.2 for every course
liaex -i project.yaml --format project --output index --project-generate-scorm12

# With SCORM 2004
liaex -i project.yaml --format project --output index --project-generate-scorm2004

# With IMS packages
liaex -i project.yaml --format project --output index --project-generate-ims

# Combined PDF + SCORM
liaex -i project.yaml --format project --output index \
  --project-generate-pdf --project-generate-scorm12

# ePub, DOCX, xAPI or Android APK for every course
liaex -i project.yaml --format project --output index \
  --project-generate-epub --project-generate-docx --project-generate-xapi

# With caching (skip files that already exist in ./assets/<format>/)
liaex -i project.yaml --format project --output index \
  --project-generate-pdf --project-generate-scorm12 --project-generate-cache

# PDF with custom theme
liaex -i project.yaml --format project --output index \
  --project-generate-pdf --pdf-theme blue --pdf-printBackground

# Disable tag/category filtering
liaex -i project.yaml --format project --output index --project-no-categories

# Blur non-matching courses instead of hiding them
liaex -i project.yaml --format project --output index --project-category-blur

# Disable social media meta tags
liaex -i project.yaml --format project --output index --project-no-meta

# Enable full-text fuzzy search (adds search icon to navbar or floating button)
liaex -i project.yaml --format project --output index --project-search
```

**All project-specific flags:**
| Flag | Description |
|------|-------------|
| `--project-no-meta` | Disable OpenGraph/Twitter card meta generation |
| `--project-no-rdf` | Disable JSON-LD generation |
| `--project-no-categories` | Disable tag/category filter dropdown |
| `--project-category-blur` | Blur non-matching courses instead of hiding |
| `--project-generate-pdf` | Auto-generate PDF for every course card |
| `--project-generate-scorm12` | Auto-generate SCORM 1.2 for every course |
| `--project-generate-scorm2004` | Auto-generate SCORM 2004 for every course |
| `--project-generate-ims` | Auto-generate IMS package for every course |
| `--project-generate-epub` | Auto-generate ePub for every course |
| `--project-generate-docx` | Auto-generate DOCX for every course |
| `--project-generate-xapi` | Auto-generate xAPI package (zip) for every course |
| `--project-generate-h5p` | Auto-generate H5P package for every course |
| `--project-generate-android` | Auto-generate Android APK for every course (needs Android SDK/Docker) |
| `--project-generate-cache` | Skip generation if the file already exists in `./assets/<format>/` |
| `--project-search` | Enable full-text fuzzy search across all courses |

All format-specific flags (`--pdf-*`, `--scorm-*`, `--epub-*`, …) can be passed alongside and apply to every course; per-course `arguments:` override them.


### 4.4 Where generated files go (and how caching works)

Generated downloads are written to `assets/` **next to the output file** (`-o`), named by a hash of the course URL, and linked from the page as relative paths:

```
./<output>.html
./assets/pdf/<hash>.pdf          ./assets/epub/<hash>.epub     ./assets/docx/<hash>.docx
./assets/scorm12/<hash>.zip      ./assets/scorm2004/<hash>.zip ./assets/ims/<hash>.zip
./assets/xapi/<hash>.zip         ./assets/android/<hash>.apk   ./assets/h5p/<hash>.h5p
```

Consequences:
- **Deploy `assets/` next to the HTML**, otherwise the download buttons break. Copying the whole folder is enough (it also carries your own images if the repo has an `assets/` folder).
- **`-p` has no effect on this location.** To keep outputs out of the source tree, point `-o` into an export directory: `liaex -i project.yaml -f project -o "$SITE_DIR/index" …` (running `liaex` inside that directory with `-o index` works the same). Relative `logo:` paths in the YAML are just copied into the HTML, so copy those image files to the deploy folder too.
- **Caching** = persist `assets/` between runs (e.g. `actions/cache` on `$EXPORT_DIR/assets`) and add `--project-generate-cache`. A cached file is never refreshed, so content changes in a course are only picked up when the cache key changes — rotate it (e.g. weekly) or drop the cache for fresh downloads.
- Several YAML files exported from the same directory share one `assets/` folder; identical courses are generated once.
- SCORM/IMS/xAPI/H5P/APK need the full course folder: for every such course the exporter clones its repository into a fresh system temp directory and removes it afterwards. This happens on every run, **also when all packages are cached** — the cache saves the packaging, not the clone, so a cached run still takes a few seconds per course (more on a slow network).
- The clone is the folder that gets packed, so **the branch must not contain exports**: generated `assets/`, ZIP/H5P/PDF files or the project page committed there end up in every package, which then grows with each run. Deploy the site to `gh-pages`, keep exports out of `main` (`.gitignore`), and restrict packing with `path:`.
- Cloning only works for `raw.githubusercontent.com/<org>/<repo>/<branch>/<file>` URLs. For other hosts SCORM/IMS/xAPI/H5P/APK are skipped with the warning "only generated for courses on raw.githubusercontent.com" and the card has no entry for them; PDF/ePub/DOCX still work.

### 4.5 Packing only a sub-folder of a repository

For SCORM/IMS/xAPI/H5P/APK, a project export packs the **entire cloned repository** by default — including every other course, slides and large media of a monorepo. Restrict it per course with `path:` (relative to the repository root, like `-p` for single exports):

```yaml
collection:
  - url: https://raw.githubusercontent.com/org/lectures/main/week-01/README.md
    path: week-01
  - url: https://raw.githubusercontent.com/org/lectures/main/week-02/README.md
    path: week-02
```

The Markdown file must lie inside `path`. Equivalent options elsewhere:

| Context | Option |
|---------|--------|
| Single CLI export, local file | `-p <folder>` (default: folder of the input file) |
| CLI export from a repo | `--git-url … --git-subdir <folder>` |
| GitHub Action | `course-path: <folder>` |
| `project.yaml` course entry | `path: <folder>` |

---

### 4.6 Design of the overview page

The page is a fixed Bootstrap 5.0.2 layout. Without CSS you can set `title`/`comment` (raw HTML), `logo` (header background image), `navbar` (`background`, `theme`), per-course `logo`, `tags`, groups (`collection` inside `collection`, `grid: true` for smaller cards) and `footer` (raw HTML).

**For a real design use `link:` and `style:`** — like in a LiaScript header. Both go into `<head>` right after Bootstrap, so plain rules override it:

```yaml
link:                       # one URL or a list
  - https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap
  - theme.css               # relative to project.yaml: copied next to the page
style: |                    # inline CSS, after the links
  :root { --accent: #003366; --accent-dark: #001f3f; }
```

A local file in `link:` is copied to the same relative place next to the output (`-o`), so publishing the output folder is enough. A path that leads out of the folder of `project.yaml` (`../x.css`) is linked but not copied (warning). Images or fonts that the stylesheet loads by a relative `url()` are **not** copied — use absolute URLs there, or copy them yourself.

A tested theme to copy and adapt: `examples/project-site/theme.css` — change the CSS variables at its top (accent, header gradient, page and card colors, fonts, radius); the rest follows. It covers the header (gradient over the `logo` image), rounded cards with hover, tag chips, the download button and menu, groups, the search button and the footer.

The stable hooks, if writing CSS from scratch:

| Element | Selector |
|---|---|
| Header with `logo` background, title, comment, filter | `main > .container-fluid`, its `h1`, `.lead`, `#categorySelect`, `#chipsContainer .badge` |
| Card area background | `.album.bg-light` |
| Course card / image / title / text / tags | `.card`, `.card-img-top` (a `div` with background image, 175 px high), `.card-title`, `.card-text`, `.card .badge.bg-light` |
| Download button and menu | `.btn-secondary.dropdown-toggle`, `.dropdown-menu`, `.dropdown-item` |
| Group (sub-collection) box and heading | `.col-12 > .card`, `.col-12 > .card > .card-header` |
| Search button (`--project-search` without navbar) | `#searchFab` |
| Footer | `footer` (has `.text-muted`) |

**Optional post-processing** of the generated `index.html` in the deploy step: the page texts are fixed English ("All categories", "Download ...", "xAPI Package", the search texts, "↑ Top"), `<html>` has no `lang`, the filter shows tags in lower case, `examples/project-site/translate-de.sed` fixes all of that for German (`sed -i -f translate-de.sed index.html`, GNU sed; tested); copy it for another language and change the right-hand sides.

Some values are inline styles or Bootstrap utilities and need `!important` (header text color, `.album` background, card shadow, the search button color). A course without `logo` in its header gets **no** image — give it `logo:` in `project.yaml`, or style image-less cards (`.card:not(:has(.card-img-top))`). Fonts: `@import` Google Fonts at the top of the stylesheet.

### 4.7 Preview locally

The page opens directly from disk (no server needed; Bootstrap and fonts come from CDNs):

```bash
liaex -i project.yaml -f project -o _build/index --project-search      # _build/ git-ignored; fast: no downloads
chromium --headless=new --hide-scrollbars --window-size=1280,1800 \
  --virtual-time-budget=8000 --screenshot=_build/page.png "file://$PWD/_build/index.html"
chromium --headless=new --hide-scrollbars --window-size=390,1500 \
  --virtual-time-budget=8000 --screenshot=_build/mobile.png "file://$PWD/_build/index.html"
```

Look at both screenshots before deploying. Add the `--project-generate-*` flags only for the final build: each course with all formats takes about a minute. Locally, PDF works with the system browser: `PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium liaex …`.

### 4.8 What to deploy

The whole output folder (`index.html`, `assets/`, the stylesheets copied from `link:`) and the **other files `project.yaml` references by a relative path** — a local `logo`, images in `title`/`comment`/`html:`. Keeping those in one folder (e.g. `site/` → `logo: site/header.jpg`) makes that a single copy. `examples/project-site/deploy-project.yml` does this.

## 9. Minimal `project.yaml` Template

For a LiaScript course project (copy and adapt):

```yaml
title: Course Collection Title

comment: Short description of this collection.

logo: logo.jpg

footer: >
  Created with LiaScript —
  <a href="https://liascript.github.io" target="_blank">LiaScript.github.io</a>

meta:
  title: Course Collection
  description: A collection of interactive educational materials

collection:
  - url: https://raw.githubusercontent.com/USERNAME/REPO/main/materials/1-lecture.md
  - url: https://raw.githubusercontent.com/USERNAME/REPO/main/materials/2-lecture.md
  - url: https://raw.githubusercontent.com/USERNAME/REPO/main/materials/3-exercise.md
```
