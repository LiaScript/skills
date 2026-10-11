---
name: liascript-exporter
description: >
  Generates LiaScript export workflows, GitHub Actions, and project.yaml files for LiaScript repositories.
  Use when a user wants to: export a LiaScript course to PDF/SCORM/IMS/ePub/DOCX/xAPI/Android/JSON; pick the
  right SCORM settings or LMS preset for Moodle 3/4/5, ILIAS, OPAL, OpenOLAT, Open edX, LearnWorlds or SCORM Cloud;
  export straight from a GitHub repository (--git-url) or only a sub-folder of it; create or update a GitHub
  Actions workflow for LiaScript; build a project website (index page) that aggregates multiple courses, with
  generated PDF/SCORM/ePub/DOCX/xAPI/APK downloads; set up automated deployment to GitHub Pages; add quality
  checks (spell/style) to a LiaScript repo; or asks anything involving the liaex CLI, @liascript/exporter,
  the LiaScript Exporter web app/desktop app, or LiaScript CI/CD. Also triggers on German requests such as
  "Kurs als SCORM für Moodle exportieren", "SCORM-Paket für ILIAS/OPAL erstellen", "LiaScript-Kurs als PDF",
  "Kursübersicht/Projektseite aus mehreren Kursen bauen", "GitHub Action für den LiaScript-Export",
  "nur einen Unterordner des Repos packen".
license: CC0-1.0
---

# LiaScript Exporter & Workflow Skill

> **Reference for AI agents:** Read this entire file before generating any workflow, `project.yaml`, or `liaex` command.

---

## Agent Role

You are a LiaScript Workflow Engineer. Your task is to help users automate the generation, transformation, and publishing of LiaScript courses.

**Core outputs you produce:**
1. `liaex` CLI commands (for local use)
2. GitHub Actions workflow YAML files (`.github/workflows/*.yml`)
3. `project.yaml` files (for course catalog websites)
4. Configuration files (`.cspell.json`, `.alexrc`, `.proselintrc`)

**Before generating anything:**
- Ask what the user's target LMS or output goal is (if not clear)
- Identify whether they want a single-course export or a multi-course project website
- Check if they already have a `project.yaml` or existing workflows

---

## Agent Workflow

### Step 1: Determine the Goal

Ask or infer from context:

| User Goal | What to produce |
|-----------|----------------|
| Export one course to Moodle/ILIAS/OPAL | `liaex` command + optional GitHub Action |
| Export to PDF/ePub/DOCX | `liaex` command + optional GitHub Action |
| Build a course catalog / index page | `project.yaml` + GitHub Actions workflow |
| Automate exports on every push | GitHub Actions workflow |
| Deploy a project website to GitHub Pages | Full GitHub Actions deployment workflow |
| Add quality checks | Quality check workflow |

### Step 2: Choose the Right Format

Use the decision matrix in Section 11 to select format and required flags based on the target LMS or output type.

**Critical LMS-specific rules — always apply:**
- Moodle 3.x → `scorm1.2 --scorm-iframe`
- Moodle 4.x / OPAL / Open edX / OpenOLAT → `scorm1.2 --scorm-embed`
- ILIAS / learnworlds.com / scorm.cloud → `scorm2004 --scorm-iframe`
- State persistence needed → use `scorm2004` (not `scorm1.2`)
- For a quick one-off export, the built-in presets (`liaex -f presets --<id>`, Section 2.2) are an alternative — but see the caveat there.

### Step 3: Generate the Artifact

Use the templates in Sections 4–5 as starting points. Always:
- Use `force_orphan: true` in `peaceiris/actions-gh-pages` steps
- Use `raw.githubusercontent.com` URLs in `project.yaml` (never HTML GitHub URLs)
- Set `--pdf-timeout 50000` (or higher) for large courses
- For large project websites add `--project-generate-cache` and persist the generated `assets/` folder between runs (Section 4.4) — `-p` does **not** set the cache location
- If a course lives in a sub-folder of its repository, restrict packing to it: `-p <folder>` for single exports, `path:` per course in `project.yaml` (Section 4.5)
- Isolate exporter outputs from source files: write to a temp directory outside the repo (e.g., `/tmp/lia-exports-${{ github.run_id }}` or `${{ runner.temp }}` when valid in step scope)
- For Docker-based exports, mount source as read-only and mount a separate output directory (`-v "$GITHUB_WORKSPACE:/work:ro"` and `-v "$EXPORT_DIR:/out"`)
- Stage release assets only after all exports finish (copy final files into `outputs/`), never export directly into `outputs/`

### Step 4: Explain Setup Steps

After generating the workflow:
1. Tell the user where to place the file (e.g., `.github/workflows/deploy.yml`)
2. If deploying to GitHub Pages: remind them to enable Pages on the `gh-pages` branch in repo Settings
3. If PDF is generated: note Puppeteer dependencies may be needed on Ubuntu runners (Section 8)

---

## Output Isolation (Critical)

When generating multiple export formats in one workflow run, do not write output files into the same tree that contains the LiaScript source input (for example the repository root or a checked out subfolder like `project/`).

If outputs are written next to source content, later exports may include previous export artifacts recursively (ZIP inside ZIP behavior), causing package size growth on every run.

Use this safe pattern:
1. Export all formats into an isolated temporary directory outside source tree (`$EXPORT_DIR` in `/tmp` or runner temp).
2. Run Docker Android export with separate source/output mounts and read-only source.
3. Copy only final files to a clean `outputs/` staging folder.
4. Upload assets from `outputs/`.

`--format project` is a special case: it always writes its generated downloads to `./assets/<format>/` and clones repositories into `./tmp/`, both relative to the **current working directory**. Isolate it by running `liaex` from inside the export directory (Section 4.4).

---

## Quick Start — Example Files

Use these ready-made examples as starting points:

| File | What it shows |
|------|---------------|
| [examples/project-minimal.yaml](examples/project-minimal.yaml) | Minimal course catalog with 3 courses |
| [examples/project-course.yaml](examples/project-course.yaml) | Full single-repo catalog with HTML separators, sub-collections, per-course options |
| [examples/workflow-single-course.yml](examples/workflow-single-course.yml) | Export one course to PDF + SCORM 2004 + IMS, attach to GitHub Release |
| [examples/workflow-project-basic.yml](examples/workflow-project-basic.yml) | Generate project website from `project.yaml` and deploy to GitHub Pages |
| [examples/workflow-multi-project.yml](examples/workflow-multi-project.yml) | Multi-project site: multiple YAML files in `project/`, with PDFs + SCORM + Pages |

---

## 1. Installation

```bash
npm install -g @liascript/exporter
# Linux/macOS may require sudo:
sudo npm install -g @liascript/exporter
```

The CLI command is `liaex` (also available as `liascript-exporter`). The npm version string has the form `<exporter>--<LiaScript>` (e.g. `3.4.3--2.1.2`).

**Alternative: Web App (no installation)**
<https://liascript.github.io/LiaScript-Exporter/> runs entirely in the browser — the course is never uploaded. Accepts Markdown files, a `.zip` of the course folder, or a public GitHub repository, and offers all presets and advanced settings. Limits: no Android export, PDF/ePub/DOCX of very large courses may run out of memory, only public GitHub repos (others: upload as `.zip`), one export at a time while its status page is open. Recommend it to users who just want a file, not automation.

**Alternative: Desktop App**
Download from [GitHub Releases](https://github.com/LiaScript/LiaScript-Exporter/releases) — same UI, no Node.js required, exports run in a separate process (better than the web app for very large courses).

**Alternative: local Web UI via CLI**
```bash
liaex serve                 # export server with web interface on port 3000
liaex serve --port 8080
liaex serve --no-browser    # don't open the browser automatically
```

**Alternative: Docker (Android exports, or the web UI)**
```bash
docker pull liascript/exporter
docker run --rm \
  -v "$(pwd):/work:ro" \
  -v "/tmp/lia-exports:/out" \
  liascript/exporter \
  liaex -f android -i /work/README.md --android-appId io.github.example.course --output /out/android

# Web UI inside the container
docker run --rm -p 4000:4000 liascript/exporter   # then open http://localhost:4000
```

---

## 2. Core CLI Syntax

```bash
liaex -i <input-file> -f <format> -o <output-name> [options]
```

| Flag | Long form | Description |
|------|-----------|-------------|
| `-i` | `--input` | Input file (Markdown, or YAML for `--format project`) |
| `-f` | `--format` | Output format (see Section 3), or `presets` (Section 2.2). Default: `json` |
| `-o` | `--output` | Output name (extension set by format), default `output` |
| `-p` | `--path` | Folder to pack into the package (default: the input file's directory) |
| `-s` | `--style` | Inject additional CSS |
| `-k` | `--key` | ResponsiveVoice key for TTS |
| `-v` | `--version` | Print version |
| `-h` | `--help` | Show help |
| | `--git-url` | Clone a git/GitHub repository and export from it (instead of `-i`) |
| | `--git-branch` | Branch or tag to check out (default: repository default) |
| | `--git-subdir` | Sub-directory of the clone to use as root |
| | `--git-file` | Markdown file to export (default: `README.md` or first `.md` found) |

**What gets packed (`-p`):** Packaging formats (SCORM, IMS, web, xAPI, Android) copy a whole folder next to the course. Without `-p` that is the directory of the input file, so `liaex -i course/README.md …` packs only `course/`. Set `-p .` when the course references files outside its own folder (e.g. `../img/`), or `-p some/folder` to restrict packing to one folder. Hidden files are skipped.

A failed export exits non-zero, so CI steps fail properly.

### 2.1 Export directly from a Git repository

```bash
# README.md of a repository → SCORM 2004
liaex --git-url https://github.com/LiaScript/LiaScript -f scorm2004 -o course

# A specific file from a branch and sub-directory
liaex --git-url https://github.com/user/repo \
  --git-branch main --git-subdir docs --git-file 01_Intro.md \
  -f web -o course
```

The repo is cloned to a temporary directory that is removed afterwards. `--git-file` is relative to `--git-subdir` (if given). Works together with presets.

### 2.2 Presets (LMS shortcuts)

Presets bundle a format with recommended options for one platform:

```bash
liaex -f presets                                            # list all presets
liaex -f presets --moodle4 -i course/README.md -o course    # export with a preset
liaex -f presets --ilias -i course/README.md -o course --scorm-organization "My Org"   # extra flags override the preset
liaex -f presets --opal --git-url https://github.com/user/repo -o course
```

| Preset flag | Platform | Effective settings (from `presets.yaml`) |
|-------------|----------|------------------------------------------|
| `--moodle3` | Moodle 3.x | scorm1.2 + iframe |
| `--moodle4` | Moodle 4.x | scorm1.2 + embed |
| `--moodle5` | Moodle 5.x | scorm1.2 + embed |
| `--ilias` | ILIAS | scorm1.2 + iframe |
| `--opal` | OPAL | scorm2004, no iframe/embed |
| `--scormcloud-1.2` | SCORM Cloud | scorm1.2 + iframe |
| `--scormcloud-2004` | SCORM Cloud | scorm2004 + iframe |
| `--openolat` | OpenOLAT | scorm1.2 + embed |
| `--openedx` | Open edX | scorm2004 + iframe |
| `--learnworlds` | LearnWorlds | scorm2004 + iframe, masteryScore 80 |

> ⚠️ The preset ID must be exact — there is no bare `--moodle`. Presets set no `masteryScore` except LearnWorlds; add `--scorm-masteryScore 80` yourself if needed. For ILIAS, OPAL and Open edX the presets differ from the tested commands in Section 3.1 — when generating CI workflows, prefer the explicit flags from Section 3.1.

---

## 3. Export Formats

### 3.1 SCORM 1.2

```bash
liaex -i README.md --format scorm1.2 --output my-course
```

Produces `my-course.zip`. SCORM 1.2 stores only location (not quiz/survey states — use SCORM 2004 for state persistence).

**Key options:**
| Option | Description |
|--------|-------------|
| `--scorm-masteryScore` | 0–100, default **0** (everyone passes). The tested LMS commands below use 80. |
| `--scorm-typicalDuration` | ISO 8601 duration, e.g. `PT1H30M0S`. Default: `PT0H5M0S` |
| `--scorm-organization` | Sets organization in `imsmanifest` |
| `--scorm-iframe` | Fix for ILIAS, OpenOLAT, learnworlds.com that break startingParameter |
| `--scorm-embed` | Embeds Markdown into JS code — use for Moodle 4, OPAL, Open edX |
| `--lia-subfolder` | Places course files in `content/` subfolder (implies `--scorm-embed`) |
| `--key` | ResponsiveVoice key for TTS |

**LMS-specific commands:**
```bash
# ILIAS / learnworlds.com
liaex -i course/README.md -f scorm2004 --scorm-masteryScore 80 --scorm-iframe

# Moodle 3.x
liaex -i course/README.md -f scorm1.2 --scorm-masteryScore 80 --scorm-iframe

# Moodle 4.x / OPAL / Open edX / OpenOLAT
liaex -i course/README.md -f scorm1.2 --scorm-masteryScore 80 --scorm-embed

# scorm.cloud
liaex -i course/README.md -f scorm2004 --scorm-masteryScore 80 --scorm-iframe
```

---

### 3.2 SCORM 2004

```bash
liaex -i README.md --format scorm2004 --output my-course
```

Same options as SCORM 1.2. **Supports persistent state** for quizzes, surveys, tasks.

---

### 3.3 IMS Content

```bash
liaex -i README.md --format ims --output course
```

Produces `course.zip`. Simplistic LMS packaging format (IMS v1.1.4).

| Option | Description |
|--------|-------------|
| `--ims-indexeddb` | Persist quiz/coding states in browser's IndexedDB |
| `--lia-subfolder` | Places course files in `content/` subfolder |

---

### 3.4 WEB (Standalone)

```bash
liaex --format web -i README.md -o outputFolder
```

Generates a self-contained web project that can be uploaded to any server.

> ⚠️ Web exports must be served over HTTP — opening `index.html` via `file://` does not work.

**Preview locally:**
```bash
npx serve outputFolder
# or
python3 -m http.server --directory outputFolder
```

| Option | Description |
|--------|-------------|
| `--web-zip` | Bundle into a zip file instead of a folder |
| `--web-iframe` | Hides the course URL (but breaks direct slide linking) |
| `--web-indexeddb [key]` | Persist states in browser IndexedDB |

---

### 3.5 PDF

```bash
liaex --format pdf -i README.md -o output
```

Uses Puppeteer (headless Chrome) to render the entire course as PDF.

**Preview mode:**
```bash
liaex --format pdf --pdf-preview -i https://raw.githubusercontent.com/.../README.md
```

**Key options:**
| Option | Description |
|--------|-------------|
| `--pdf-stylesheet` | Inject custom CSS |
| `--pdf-theme` | `default`, `turquoise`, `blue`, `red`, `yellow` |
| `--pdf-timeout` | Wait time in ms (default: 15000). Increase for large courses. |
| `--pdf-scale` | 0.1–2, default 1 |
| `--pdf-displayHeaderFooter` | Show header/footer (default: false) |
| `--pdf-headerTemplate` | HTML template (classes: `date`, `title`, `url`, `pageNumber`, `totalPages`) |
| `--pdf-footerTemplate` | Same as header template |
| `--pdf-printBackground` | Print background graphics (default: false) |
| `--pdf-landscape` | Landscape orientation (default: false) |
| `--pdf-pageRanges` | e.g. `"1-5, 8, 11-13"` |
| `--pdf-format` | Paper format, e.g. `A4`, `A3`, `Letter` (default: a4) |
| `--pdf-width` / `--pdf-height` | Custom dimensions with units |
| `--pdf-margin-top/right/bottom/left` | Margins with units |
| `--pdf-preferCSSPageSize` | CSS `@page` size takes priority |
| `--pdf-omitBackground` | Transparent background (default: true) |

**Custom CSS example:**
```css
:root {
  --color-highlight: 2, 255, 0;
  --color-background: 122, 122, 122;
  --color-text: 0, 0, 255;
  --global-font-size: 1rem;
  --font-size-multiplier: 2;
}
```

---

### 3.6 ePub

```bash
liaex -i README.md --format epub --epub-title "My Course" --epub-author "Author Name" --output course
```

Title, author, language, description and cover default to the course header (`title`/first heading, `author:`, `language:`, `comment:`, `logo:`), so a plain `liaex -i README.md --format epub` works.

| Option | Description |
|--------|-------------|
| `--epub-title` | Title of the book (default: course title) |
| `--epub-author` | Semicolon-separated for multiple authors (default: `author:` from header) |
| `--epub-publisher` | Publisher name |
| `--epub-cover` | Path or URL to cover image |
| `--epub-description` | Book description |
| `--epub-language` | 2-letter language code (default: `en`) |
| `--epub-version` | EPUB version: `2` or `3` (default: 3) |
| `--epub-stylesheet` | Custom CSS path |
| `--epub-theme` | `default`, `turquoise`, `blue`, `red`, `yellow` |
| `--epub-toc-title` | TOC title (default: `"Table Of Contents"`) |
| `--epub-hide-toc` | Hide TOC (default: false) |
| `--epub-timeout` | Render wait in ms (default: 15000) |
| `--epub-fonts` | Comma-separated custom font paths |
| `--epub-chapter-title` | Main chapter title (default: course title) |
| `--epub-preview` | Open preview browser |

---

### 3.7 DOCX

```bash
liaex -i README.md --format docx --output course
```

Compatible with Word 2007+, LibreOffice Writer, Google Docs.

| Option | Description |
|--------|-------------|
| `--docx-title` | Document title |
| `--docx-author` | Author name |
| `--docx-subject` | Subject |
| `--docx-description` | Description |
| `--docx-language` | Language code for spell checker (default: `en-US`) |
| `--docx-orientation` | `portrait` or `landscape` (default: `portrait`) |
| `--docx-font` | Font name (default: `Arial`) |
| `--docx-font-size` | In half-points/HIP (default: 22 = 11pt) |
| `--docx-header` / `--docx-footer` | Enable header/footer |
| `--docx-header-html` / `--docx-footer-html` | Custom HTML |
| `--docx-page-number` | Add page numbers to footer |
| `--docx-stylesheet` | Custom CSS path |
| `--docx-theme` | `default`, `turquoise`, `blue`, `red`, `yellow` |
| `--docx-timeout` | Render wait in ms (default: 15000) |
| `--docx-preview` | Open preview browser |

---

### 3.8 xAPI

```bash
liaex -i README.md --format xapi --output course
```

Generates a self-contained web package with `tincan.xml` manifest.

| Option | Description |
|--------|-------------|
| `--xapi-endpoint` | LRS endpoint URL |
| `--xapi-auth` | Auth string (e.g., `"Basic dXNlcm5hbWU6cGFzc3dvcmQ="`) |
| `--xapi-actor` | JSON actor string (default: anonymous) |
| `--xapi-course-id` | Custom course identifier |
| `--xapi-course-title` | Custom course title |
| `--xapi-mastery-threshold` | Score threshold (default: 0.8) |
| `--xapi-progress-threshold` | Progress threshold (default: 0.9) |
| `--xapi-debug` | Enable debug logging |
| `--xapi-zip` | Package as zip |
| `--lia-subfolder` | Place course files in `content/` subfolder |

---

### 3.9 Android APK

```bash
liaex -f android \
  -i README.md \
  --android-sdk /home/user/Android/Sdk \
  --android-appId io.github.myorg.mycourse \
  --output output
```

Produces `output.apk` (debug build by default). Uses Capacitor.js. Best done via Docker (see Section 1). Not available in the web app.

| Option | Description |
|--------|-------------|
| `--android-sdk` | Path to Android SDK (not needed in Docker) |
| `--android-appId` | **Required.** Unique reverse-domain app ID |
| `--android-appName` | App name (default: course title) |
| `--android-icon` | App icon (1024×1024 px) |
| `--android-iconBackgroundColor` | Background color of the adaptive icon |
| `--android-iconBackgroundColorDark` | Same for dark mode |
| `--android-release` | Signed release APK (needs keystore) |
| `--android-bundle` | Signed release AAB for the Play Store (needs keystore) |
| `--android-keystore` | Path to keystore file |
| `--android-keystorePassword` | Keystore password (or env `KEYSTORE_PASSWORD`) |
| `--android-keyAlias` | Key alias (default `release`, or env `KEY_ALIAS`) |
| `--android-keyPassword` | Key password (or env `KEY_PASSWORD`) |
| `--android-preview` | Open the project in Android Studio |

In CI, pass signing secrets via the environment variables, never as literal flags in the workflow file. Play Store publishing steps: [PLAYSTORE_GUIDE.md](https://github.com/LiaScript/LiaScript-Exporter/blob/master/PLAYSTORE_GUIDE.md).

> `--android-splash` / `--android-splashDuration` from older docs are no longer read by the exporter.

---

### 3.10 RDF / JSON-LD

```bash
liaex --format rdf --rdf-preview -i README.md
liaex --format rdf --rdf-format n-quads -i README.md -o output
```

Exports LiaScript course metadata as JSON-LD or N-Quads (schema.org `Course`).

| Option | Description |
|--------|-------------|
| `--rdf-preview` | Print to console instead of file |
| `--rdf-format` | `jsonld` (default) or `n-quads` |
| `--rdf-url` | Set remote URL for local file input |
| `--rdf-type` | Default `Course` — can be `EducationalResource`, etc. |
| `--rdf-educationalLevel` | e.g., `beginner`, `intermediate`, `advanced` |
| `--rdf-license` | License URL (auto-detects LICENSE file in root) |
| `--rdf-template` | Base template URL or local JSON file |

---

### 3.11 JSON (parsed course)

```bash
liaex -i README.md --format json -o course       # default format if -f is omitted
liaex -i README.md --format fullJson -o course   # complete parsed course (what the other exporters consume)
```

Writes `course.json` — useful for analyses or custom tooling, not for learners. The format name is case-insensitive.

### 3.12 Project (Index Website)

See Section 4 for the full project workflow.

```bash
liaex -i project.yaml --format project --output index
```

---

## 4. Project Website (`project.yaml`)

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

# Global tags applied to ALL courses
tags:
  - Education
  - Interactive
  - OER

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
  # pack only that folder into SCORM/IMS/xAPI/APK (see Section 4.5)
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
    tags:
      - Python
      - Programming
    collection:
      - url: https://raw.githubusercontent.com/username/python-intro/main/README.md
        tags:
          - Beginner
      - url: https://raw.githubusercontent.com/username/python-advanced/main/README.md
        tags:
          - Advanced
```

### 4.2 Tags in LiaScript Document Headers

Tags in the LiaScript course header are automatically extracted:

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
| `--project-generate-android` | Auto-generate Android APK for every course (needs Android SDK/Docker) |
| `--project-generate-cache` | Skip generation if the file already exists in `./assets/<format>/` |
| `--project-search` | Enable full-text fuzzy search across all courses |

All format-specific flags (`--pdf-*`, `--scorm-*`, `--epub-*`, …) can be passed alongside and apply to every course; per-course `arguments:` override them.

### 4.4 Where generated files go (and how caching works)

Generated downloads are always written relative to the **current working directory**, named by a hash of the course URL, and linked from the page as relative paths:

```
./<output>.html
./assets/pdf/<hash>.pdf          ./assets/epub/<hash>.epub     ./assets/docx/<hash>.docx
./assets/scorm12/<hash>.zip      ./assets/scorm2004/<hash>.zip ./assets/ims/<hash>.zip
./assets/xapi/<hash>.zip         ./assets/android/<hash>.apk
```

Consequences:
- **Deploy `assets/` next to the HTML**, otherwise the download buttons break. Copying the whole folder is enough (it also carries your own images if the repo has an `assets/` folder).
- **`-p` has no effect on this location.** To keep outputs out of the source tree, `cd` into an export directory and pass the YAML by absolute path: `cd "$EXPORT_DIR" && liaex -i "$GITHUB_WORKSPACE/project.yaml" -f project -o index …`. Relative `logo:` paths in the YAML are just copied into the HTML, so copy those image files to the deploy folder too.
- **Caching** = persist `assets/` between runs (e.g. `actions/cache` on `$EXPORT_DIR/assets`) and add `--project-generate-cache`. A cached file is never refreshed, so content changes in a course are only picked up when the cache key changes — rotate it (e.g. weekly) or drop the cache for fresh downloads.
- Several YAML files exported from the same directory share one `assets/` folder; identical courses are generated once.
- SCORM/IMS/xAPI/APK need the full course folder, so the exporter runs `git clone` into **`./tmp/`** and deletes it afterwards (`rm -rf tmp`). Never run a project export in a directory that has its own `tmp/` folder; after a crashed run, delete the leftover `tmp/` or the next clone fails.
- Cloning only works for `raw.githubusercontent.com/<org>/<repo>/<branch>/<file>` URLs. For other hosts, SCORM/IMS/xAPI/APK are silently not generated for that course, while its card still shows a (broken) download link; PDF/ePub/DOCX still work.

### 4.5 Packing only a sub-folder of a repository

For SCORM/IMS/xAPI/APK, a project export packs the **entire cloned repository** by default — including every other course, slides and large media of a monorepo. Restrict it per course with `path:` (relative to the repository root, like `-p` for single exports):

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

## 5. GitHub Actions Workflows

### 5.1 Simple: Transform Single Course to Multiple Formats

**File:** `.github/workflows/generate-outputs.yml`

```yaml
name: Generate LiaScript Outputs

on:
  push:
    branches:
      - main

permissions:
  contents: write

jobs:
  generate:
    runs-on: ubuntu-latest
    env:
      EXPORT_DIR: /tmp/lia-exports-${{ github.run_id }}
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
        with:
          path: project

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Install LiaScript Exporter
        run: npm install -g @liascript/exporter

      - name: Prepare isolated output directory
        run: mkdir -p "$EXPORT_DIR"

      # Chromium system libraries for PDF: see Section 8

      - name: Generate PDF
        env:
          PUPPETEER_ARGS: "--no-sandbox --disable-setuid-sandbox"
        run: liaex -i project/README.md --format pdf --output "$EXPORT_DIR/Documentation" --pdf-timeout 50000

      - name: Generate SCORM 2004
        run: liaex -i project/README.md --format scorm2004 --output "$EXPORT_DIR/SCORM" --scorm-masteryScore 80

      - name: Generate IMS Package
        run: liaex -i project/README.md --format ims --output "$EXPORT_DIR/IMS"

      - name: Publish as release "latest"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Recreate the release so the "latest" tag moves to this commit
          gh release delete latest --cleanup-tag --yes --repo "$GITHUB_REPOSITORY" || true
          gh release create latest --repo "$GITHUB_REPOSITORY" --target "$GITHUB_SHA" \
            --title "Latest LiaScript Documentation" --notes "Built from $GITHUB_SHA" \
            "$EXPORT_DIR/Documentation.pdf" "$EXPORT_DIR/SCORM.zip" "$EXPORT_DIR/IMS.zip"
```

> Do not use `actions/create-release@v1` / `actions/upload-release-asset@v1`: both are archived, and `create-release` fails on every run after the first because the tag already exists.

---

### 5.2 Project Website: Basic Deployment to GitHub Pages

**File:** `.github/workflows/deploy-project.yml`

```yaml
name: Generate and Deploy Project Website

on:
  push:
    branches:
      - main

permissions:
  contents: write

jobs:
  run_exporter:
    runs-on: ubuntu-latest
    steps:
      - name: Install LiaScript Exporter
        run: npm install -g @liascript/exporter

      - name: Check out repository
        uses: actions/checkout@v4

      - name: Generate project website
        run: liaex -i project.yaml --format project --output index

      - name: Prepare deployment directory
        run: |
          mkdir -p gh-pages-deploy
          mv index.html gh-pages-deploy/
          cp logo.jpg gh-pages-deploy/

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_branch: gh-pages
          publish_dir: gh-pages-deploy
          force_orphan: true     # REQUIRED: always overwrite gh-pages history completely
```

> ⚠️ **`force_orphan: true` is required.** This ensures the `gh-pages` branch is always completely replaced, with no accumulated history.

---

### 5.3 Project Website: Full Production Workflow (PDF + SCORM + Cache + Schedule)

**File:** `.github/workflows/deploy-full.yml`

```yaml
name: Generate and Deploy LiaScript Project Website

on:
  push:
    branches:
      - main
  schedule:
    - cron: '0 0 * * 0'   # Every Sunday at midnight UTC

permissions:
  contents: write

jobs:
  run_exporter:
    runs-on: ubuntu-latest
    env:
      # Fixed path outside the repo: liaex writes ./assets/<format>/ and ./tmp/ into its CWD
      SITE_DIR: /tmp/lia-site
    steps:
      - name: Install LiaScript Exporter
        run: npm install -g @liascript/exporter

      - name: Check out repository
        uses: actions/checkout@v4

      - name: Prepare site directory and cache week
        id: week
        run: |
          mkdir -p "$SITE_DIR"
          echo "week=$(date -u +%G-%V)" >> "$GITHUB_OUTPUT"

      - name: Restore generated downloads
        uses: actions/cache@v4
        with:
          path: /tmp/lia-site/assets
          # Cached files are never refreshed by liaex; rotating the key weekly
          # picks up content changes in the courses at least once a week.
          key: lia-assets-${{ hashFiles('project.yaml') }}-${{ steps.week.outputs.week }}

      # Chromium system libraries for PDF: see Section 8

      - name: Generate website with PDFs and SCORM packages
        working-directory: /tmp/lia-site
        env:
          PUPPETEER_ARGS: "--no-sandbox --disable-setuid-sandbox"
        run: |
          liaex -i "$GITHUB_WORKSPACE/project.yaml" --format project --output index \
            --project-generate-pdf \
            --project-generate-scorm12 \
            --project-generate-cache

      - name: Prepare deployment directory
        run: |
          mkdir -p gh-pages-deploy
          cp "$SITE_DIR/index.html" gh-pages-deploy/
          # Generated downloads — must sit next to index.html (links are assets/<format>/<hash>.*)
          cp -r "$SITE_DIR/assets" gh-pages-deploy/
          # Images referenced by project.yaml
          if [ -f logo.jpg ]; then cp logo.jpg gh-pages-deploy/; fi
          if [ -d assets ]; then cp -r assets/. gh-pages-deploy/assets/; fi

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_branch: gh-pages
          publish_dir: gh-pages-deploy
          force_orphan: true
          commit_message: "Deploy: ${{ github.event.head_commit.message || 'Scheduled update' }}"

      - name: Output website URL
        run: |
          echo "Deployed to: https://${{ github.repository_owner }}.github.io/${{ github.event.repository.name }}/"
```

---

### 5.4 Multi-Project Website (multiple YAML files)

Use when one repository contains several distinct subject areas, each with their own catalog page, PDFs, and SCORM packages.

**Repository layout:**
```
project/
  index.yaml           ← top-level navigation page
  topic-a.yaml         ← one section/audience
  topic-b.yaml
assets/                ← shared images referenced by project pages
```

**File:** `.github/workflows/deploy.yml` — see full example at [examples/workflow-multi-project.yml](examples/workflow-multi-project.yml).

Key points:
- Run every `liaex` call with `working-directory` set to one shared export directory outside the repo and pass the YAML files by absolute path (`-i "$GITHUB_WORKSPACE/project/topic-a.yaml"`). All pages then share one `assets/` folder.
- Set `PUPPETEER_ARGS: "--no-sandbox --disable-setuid-sandbox"` env var on the generate step
- Use `force_orphan: true` on `peaceiris/actions-gh-pages@v4`
- Deploy all `*.html` files plus the export directory's `assets/` folder (the generated downloads) side by side, then add the repo's own images

---

### 5.5 Quality Check Workflow

**File:** `.github/workflows/quality-checks.yml`

```yaml
name: Quality Checks

on:
  pull_request:
  push:
    branches: [main, master]

jobs:
  cspell-spellcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install cspell
        run: npm install -g cspell
      - name: Run spell check
        run: npx cspell --locale en-US --show-suggestions "**/*.md"

  write-good:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - name: Install write-good
        run: npm install -g write-good
      - name: Run style check
        run: npx write-good *.md

  alex:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - name: Install alex
        run: npm install -g alex
      - name: Run inclusive language check
        run: npx alex *.md

  proselint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - name: Install proselint
        run: |
          npm install -g proselint
          pip install proselint
      - name: Run proselint
        run: npx proselint *.md
```

---

### 5.6 GitHub Action (LiaScript's own Action)

Use directly in a workflow without installing the exporter:

```yaml
- name: Export to SCORM
  uses: LiaScript/LiaScript-Exporter@master
  with:
    input-file: 'README.md'
    format: 'scorm1.2'
    output-name: 'my-course'
    scorm-organization: 'My Organization'
    # course-path: 'courses/intro'   # folder to pack, like -p (default: folder of input-file)

- name: Upload SCORM
  uses: actions/upload-artifact@v4
  with:
    name: scorm-package
    path: '*.zip'
```

Supported `format` values: `scorm1.2`, `scorm2004`, `pdf`, `web`, `ims`, `xapi`, `rdf`, `json`, `project` — for ePub, DOCX or Android install the CLI instead (Section 5.1 / Docker). Inputs use kebab-case (`scorm-mastery-score`, `pdf-print-background`, …); outputs are `output-file`, `file-size`, `format`, `success`.

Full documentation: [action/README.md](https://github.com/liascript/liascript-exporter/blob/HEAD/action/README.md)

---

### 5.7 Triggering Strategies

```yaml
# Run on push to main only
on:
  push:
    branches: [main]

# Run on push + weekly
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'    # Every Sunday midnight UTC

# Run on push + daily
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * *'    # Every day at midnight UTC

# Run on push AND pull requests
on:
  pull_request:
  push:
    branches: [main, master]
```

---

## 6. Quality Check Tools

### 6.1 CSpell (Spell Checking)

```bash
npm install -g cspell
npx cspell --locale en-US --show-suggestions "**/*.md"

# German support
npm install -g @cspell/dict-de-de
npx cspell --locale en-US,de-DE --show-suggestions "**/*.md"
```

**Config file `.cspell.json`:**
```json
{
  "version": "0.2",
  "language": "en-US",
  "ignoreWords": [
    "LiaScript", "Markdown", "GitHub", "workflow"
  ],
  "dictionaries": ["en_US"]
}
```

**Inline language switching:**
```markdown
<!-- cspell:language de-DE -->
Hier ist ein deutscher Absatz.
<!-- cspell:language en-US -->
Here is an English paragraph.
```

### 6.2 Write-Good (Style Checking)

Flags: passive voice, weasel words, clichés, redundant phrases.

```bash
npm install -g write-good
npx write-good *.md
npx write-good *.md --no-passive    # disable passive voice check
```

Options: `--no-passive`, `--no-illusion`, `--no-so`, `--no-adverb`, `--no-tooWordy`, `--no-cliches`

**German:** `npm install -g schreib-gut && write-good *.md --checks=schreib-gut`

### 6.3 Alex (Inclusive Language)

Flags: gender bias, ableist language, racially insensitive terms.

```bash
npm install -g alex
npx alex *.md
```

**Config `.alexrc`:**
```json
{ "allow": ["special"] }
```

### 6.4 Proselint (Advanced Style)

Flags: redundancy, jargon, typography, consistency.

```bash
npm install -g proselint && pip install proselint
npx proselint *.md
```

**Config `.proselintrc`:**
```json
{
  "checks": {
    "typography.diacritical_marks": false,
    "typography.exclamation": false
  }
}
```

---

## 7. GitHub Pages Setup

After first workflow run:
1. Go to repo → **Settings** → **Pages**
2. Under **Source**, select branch: `gh-pages`
3. Click **Save**

Website URL: `https://<username>.github.io/<repository-name>/`

---

## 8. PDF Generation: Puppeteer on GitHub Actions

Puppeteer (headless Chrome) requires two things on GitHub Actions runners:

**1. The `PUPPETEER_ARGS` environment variable (critical — do not skip this):**
```yaml
- name: Generate PDF
  env:
    PUPPETEER_ARGS: "--no-sandbox --disable-setuid-sandbox"
  run: liaex -i README.md --format pdf --output output --pdf-timeout 60000
```

**2. Chromium system libraries (Ubuntu 24 / `ubuntu-latest`):**
```yaml
- name: Install Chromium system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y \
      libgbm-dev libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
      libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
      libpango-1.0-0 libcairo2 libasound2t64 libnss3 libnspr4 \
      fonts-liberation ca-certificates wget
```

> ⚠️ **Ubuntu 24 uses `libasound2t64`**, not `libasound2`. The old package name causes `apt-get` to fail on `ubuntu-latest` runners.

---

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

---

## 10. Key Rules and Gotchas

1. **`force_orphan: true`** — Always use in `peaceiris/actions-gh-pages` to prevent gh-pages branch history from growing. Required for clean deployments.

2. **`project.yaml` URLs must point to raw Markdown** — Use `raw.githubusercontent.com`, not the GitHub HTML page URL.

3. **Web exports need HTTP** — `liaex --format web` outputs cannot be opened via `file://`. Use `npx serve` or Python HTTP server for local testing.

4. **Project caching lives in `./assets/`, not in `-p`** — `--project-generate-cache` skips files that already exist in `./assets/<format>/` of the working directory. Persist that folder between runs and deploy it next to the HTML (Section 4.4). Cached files are never refreshed.

5. **SCORM state persistence** — SCORM 1.2 stores location only; use SCORM 2004 for quiz/survey state persistence.

6. **LMS-specific SCORM quirks** — Moodle 4, OPAL, Open edX need `--scorm-embed`; ILIAS, learnworlds.com need `--scorm-iframe`.

7. **Per-course argument overrides** — In `project.yaml`, use `arguments:` under a course entry with long flag names (no leading `--`) to override export settings for individual courses.

8. **Tags are auto-extracted** — If the LiaScript document header has `tags:`, they appear automatically. Override or supplement in `project.yaml`.

9. **Navbar is optional** — If `navbar:` is absent from `project.yaml`, no navigation bar is rendered.

10. **`--project-search`** — Adds full-text fuzzy search (Ctrl+K / Cmd+K shortcut). Requires `navbar:` for the search icon, otherwise shows a floating button.

11. **PDF on GitHub Actions needs two things:** (a) set env var `PUPPETEER_ARGS: "--no-sandbox --disable-setuid-sandbox"` on the PDF step, AND (b) install Chromium system libraries. Use `libasound2t64` — not `libasound2` — on `ubuntu-latest` (Ubuntu 24). See Section 8.

12. **Prevent recursive package growth (critical):** never export into the repository source tree when creating multiple formats in one run. Export into an isolated temp directory first, then copy the final artifacts into a clean staging folder for upload. For Docker exports, mount source read-only and outputs on a separate mount.

13. **Pack only what belongs to the course** — `-p <folder>` (single export), `--git-subdir` (git export), `course-path` (Action) or `path:` per course in `project.yaml` (Section 4.5). Without `path:`, project-generated SCORM/IMS/xAPI/APK contain the *whole* repository.

14. **Project export and `./tmp/`** — the project exporter clones into `./tmp/` and runs `rm -rf tmp` afterwards. Never run it in a folder with a `tmp/` directory you need; remove a leftover `tmp/` after a crashed run.

15. **`[ -f x ] && cp …` as the last line of a `run:` block fails the step** when the file is missing (the step's exit code is that of the last command). Use `if [ -f x ]; then cp …; fi`.

16. **Preset IDs are exact** — `--moodle3|4|5`, `--ilias`, `--opal`, `--openolat`, `--openedx`, `--learnworlds`, `--scormcloud-1.2`, `--scormcloud-2004`; `liaex -f presets` lists them.

---

## 11. Quick Reference: Format Decision Matrix

| Goal | Format | Key flag(s) |
|------|--------|-------------|
| Upload to Moodle 3.x | `scorm1.2` | `--scorm-iframe` |
| Upload to Moodle 4.x / 5.x | `scorm1.2` | `--scorm-embed` |
| Upload to ILIAS / scorm.cloud / learnworlds.com | `scorm2004` | `--scorm-iframe` |
| Upload to OPAL / Open edX / OpenOLAT | `scorm1.2` | `--scorm-embed` |
| Printable PDF | `pdf` | `--pdf-theme`, `--pdf-format` |
| E-reader / ePub | `epub` | `--epub-title`, `--epub-author` |
| Word document | `docx` | optional `--docx-*` |
| Self-hosted interactive course | `web` | `--web-indexeddb` for persistence |
| Android app | `android` | `--android-appId` |
| xAPI / LRS tracking | `xapi` | `--xapi-endpoint` |
| Course catalog website | `project` | `project.yaml` input |
| Metadata export | `rdf` | `--rdf-format jsonld` |
| Parsed course data | `json` / `fullJson` | — |
| Just one file, no install | Web app | <https://liascript.github.io/LiaScript-Exporter/> |
| Course in a sub-folder of a repo | any packaging format | `-p` / `--git-subdir` / `path:` |

---

*Sources: [LiaScript-Exporter GitHub](https://github.com/liascript/liascript-exporter) (verified against source of `@liascript/exporter` 3.4.3--2.1.2, October 2026), [Automating LiaScript Transformations](https://liascript.github.io/blog/automating-liascript-transformations-on-github/), [Quality Checks](https://liascript.github.io/blog/quality-checks-on-liascript-with-github-ensuring-document-excellence/), [Creating Project Websites](https://liascript.github.io/blog/creating-project-websites-with-liascript-exporter/)*
