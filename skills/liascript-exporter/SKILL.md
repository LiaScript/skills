---
name: liascript-exporter
description: >
  Use when someone wants to export a LiaScript course with the liaex CLI
  (@liascript/exporter), the Exporter web or desktop app or CI: SCORM 1.2/2004,
  IMS, xAPI, H5P, PDF, ePub, DOCX, web, Android, desktop app, JSON/RDF; the
  right settings or preset for Moodle, ILIAS, OPAL, OpenOLAT, Open edX,
  LearnWorlds or SCORM Cloud; exporting from a GitHub or GitLab repository or
  one sub-folder of it; a project website that lists several courses on one
  designed overview page with SCORM/xAPI/PDF/… downloads, tag filter and search;
  GitHub Actions/Pages or GitLab CI/Pages; spelling and style checks for a
  LiaScript repo. German triggers: "Kurs als SCORM für Moodle exportieren",
  "SCORM-Paket für ILIAS/OPAL", "LiaScript-Kurs als PDF",
  "Kursübersicht/Projektseite aus mehreren Kursen bauen", "Projektseite
  gestalten", "GitHub Action für den LiaScript-Export", "Projektseite auf GitLab
  Pages", "nur einen Unterordner packen", "Quizantworten im SCORM speichern",
  "als H5P in Moodle", "Kurs als Desktop-App".
license: CC0-1.0
---

# LiaScript Exporter

`liaex` turns a LiaScript course (a Markdown file) into LMS packages and documents, and builds project websites that present many courses on one page with downloads. Everything below is checked against `@liascript/exporter` 3.6.2 by running it.

## Navigation — read the file that matches the task

| File | Read when… |
|---|---|
| `reference/formats.md` | Choosing options for one format (SCORM, IMS, web, PDF, ePub, DOCX, xAPI, H5P, Android, desktop, RDF, JSON) or an LMS preset |
| `reference/project.md` | Building a project / course-catalog page: `project.yaml`, downloads, caching, **design**, preview, deploy |
| `reference/workflows.md` | GitHub Actions (single course, project, multi-project), GitHub Pages setup, PDF on CI, **GitLab CI and GitLab Pages** |
| `reference/quality.md` | Spelling and style checks (CSpell, write-good, alex, proselint) |
| `examples/project-site/` | A tested, designed project: `project.yaml`, `theme.css` + `themes/` (campus, night, school), `translate-de.sed`, `deploy-project.yml`, `deploy-several-pages.yml` (several pages sharing the downloads; tested on GitHub Actions), `gitlab-ci.yml` (the same for GitLab Pages) — start every project page from here |
| `examples/*.yaml`, `examples/workflow-*.yml` | Minimal and full `project.yaml`, single-course and multi-project workflows |

Ask first what the user needs if it is unclear: one course for one LMS, documents, a catalog page, or automation.

## Install

```bash
npm install -g @liascript/exporter      # CLI: liaex (also liascript-exporter); liaex --version
```

The version reads `<exporter>--<LiaScript>`, e.g. `3.6.2--2.6.1`. PDF, ePub and DOCX use Puppeteer: to use an installed Chromium instead of Puppeteer's download, set `PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium`.

Alternatives: the **web app** <https://liascript.github.io/LiaScript-Exporter/> (in the browser, nothing uploaded; Markdown, a `.zip` of the course folder or a public GitHub or GitLab repo; no Android; very large PDFs may run out of memory) — recommend it to users who just want one file; the **desktop app** from the GitHub releases; `liaex serve [--port 8080] [--no-browser]` for the same UI locally; Docker `liascript/exporter` (needed for Android):

```bash
docker run --rm -v "$(pwd):/work:ro" -v "/tmp/lia-exports:/out" liascript/exporter \
  liaex -f android -i /work/README.md --android-appId io.github.example.course --output /out/android
```

## Core command

```bash
liaex -i <input> -f <format> -o <output-name> [options]
liaex --git-url https://github.com/user/repo [--git-branch main] [--git-subdir docs] [--git-file 01.md] -f web -o course
liaex --git-url https://gitlab.com/group/repo/-/blob/main/docs/01.md -f scorm1.2 -o course   # branch, sub-folder, file from -/blob/, -/raw/ or -/tree/ links; sub-groups, self-hosted, gitlab://host/…
liaex -f presets --moodle4 -i course/README.md -o course      # liaex -f presets lists all presets
```

| Flag | Meaning |
|---|---|
| `-i` / `--input` | Markdown file, or `project.yaml` for `-f project` |
| `-f` / `--format` | `scorm1.2`, `scorm2004`, `ims`, `xapi`, `h5p`, `web`, `pdf`, `epub`, `docx`, `android`, `desktop`, `rdf`, `json`, `fullJson`, `project`, `presets` |
| `-o` / `--output` | output name; the extension follows the format (default `output`) |
| `-p` / `--path` | folder packed into SCORM/IMS/web/xAPI/H5P/Android (default: the input's folder; `-p .` if the course uses `../` files) |
| `-s` / `--style` | extra CSS for the course |

A failed export exits non-zero, so CI steps fail properly.

## Which format for which target

| Target | Command |
|---|---|
| Moodle 3.x | `-f scorm1.2 --scorm-iframe` |
| Moodle 4.x / 5.x, OPAL, Open edX, OpenOLAT | `-f scorm1.2 --scorm-embed` |
| ILIAS, LearnWorlds, SCORM Cloud | `-f scorm2004 --scorm-iframe` |
| LMS must keep quiz answers | add `--scorm-storage suspend` (SCORM 1.2 and 2004); plain SCORM 1.2 keeps only the slide |
| xAPI / LRS | `-f xapi --xapi-endpoint … --xapi-auth …` |
| H5P (Moodle, ILIAS, WordPress, Drupal) | `-f h5p` |
| Print / e-reader / Word | `-f pdf`, `-f epub`, `-f docx` |
| Own web space | `-f web` (needs HTTP, not `file://`; `--web-indexeddb` keeps progress) |
| Android app | `-f android --android-appId …` (Docker) |
| Desktop app (Windows, macOS, Linux) | `-f desktop --desktop-appId …` (no Docker; unsigned) |
| Course catalog with downloads | `-f project`, see below |

Presets (`--moodle3|4|5`, `--ilias`, `--opal`, `--openolat`, `--openedx`, `--learnworlds`, `--scormcloud-1.2`, `--scormcloud-2004`) bundle similar settings; for ILIAS, OPAL and Open edX they differ from this table — prefer the explicit flags in CI. Details and all options: `reference/formats.md`.

## Project website in brief

1. `project.yaml` with `title`, `comment`, `logo` (header image), `navbar`, `link`/`style` for the design, and a `collection` of **raw** course URLs (`raw.githubusercontent.com/…` or GitLab `…/-/raw/<branch>/<file>`) (groups: a `collection` inside the `collection`). Copy `examples/project-site/` and adapt.
2. Design: the page is fixed Bootstrap; restyle it with `link: theme.css` (copied next to the page) and/or inline `style:` — both go into `<head>` after Bootstrap. Start from `examples/project-site/theme.css` (academic) plus, if wanted, one of `themes/campus.css`, `themes/night.css`, `themes/school.css`, and change the variables (colors, fonts, radius), e.g. in `style:`. Selectors: `reference/project.md` §4.6.
3. Look at it before deploying: `liaex -i project.yaml -f project -o index --project-search`, then a desktop and a phone screenshot with headless Chromium (`reference/project.md` §4.7).
4. Final build with downloads: add `--project-generate-scorm12 --project-generate-xapi --project-generate-pdf` (also `-scorm2004`, `-ims`, `-h5p`, `-epub`, `-docx`, `-android`) and `--project-generate-cache`. Run it with `-o` pointing outside the repository; publish that output folder (page, `assets/`, the copied stylesheets) plus images the YAML references relatively — `examples/project-site/deploy-project.yml`.

## Gotchas

1. **One failing download aborts the whole project export** — no page at all. Test new courses and formats locally first.
2. **Project URLs must be `http(s)`.** A local path in `project.yaml` aborts the whole project export ("Export failed: it stopped without writing any output"). Courses must be pushed first.
3. **Project downloads of SCORM/IMS/xAPI/H5P/APK need a GitHub or GitLab file URL** (the exporter clones the repository): `raw.githubusercontent.com/<org>/<repo>/<branch>/<file>`, or GitLab `…/<group>/<repo>/-/raw/<branch>/<file>` (gitlab.com and self-hosted, public repositories; write `https://`, a `gitlab://` link aborts the project export). Other hosts get only PDF/ePub/DOCX, with a warning. Never use GitHub HTML page URLs; for GitLab prefer `-/raw/` links — LiaScript opens them from the card also for projects in sub-groups. A branch name containing `/` is misread — use another branch.
4. **A project's downloads go to `assets/<format>/` next to the output file** (`-o "$SITE_DIR/index"` → `$SITE_DIR/assets/`), named by a hash of the course URL; `-p` does not change that. The folder is created if missing. Deploy `assets/` next to `index.html`.
5. **Design only through `link:`/`style:`** (or raw HTML in `title`, `comment`, `footer`, `html:` entries); many values are Bootstrap utilities or inline styles. A course without `logo` gets no card image — set `logo:` per course in `project.yaml`. Its texts ("All categories", "Download …", search) are English — `examples/project-site/translate-de.sed` translates them.
6. **Tags**: only per-course `tags:` (replacing the header tags) feed the filter; top-level and group `tags:` are ignored; the filter shows them in lower case.
7. **`--project-generate-cache` never refreshes a file** — rotate the CI cache key (e.g. weekly). It saves packaging, not the repository clone, which runs every time.
8. **Never export into the repository source tree** when building several formats or a project in CI: later packages would contain the earlier ones (ZIP in ZIP, growing every run). Export into `/tmp/…` or `$RUNNER_TEMP`, then copy the final files to a staging folder; Docker: mount the source read-only and the output separately.
9. **A folder that gets packed must be clean.** Never commit exports (`assets/`, `*.zip`, `*.h5p`, `*.pdf`, the project page) to the branch the courses are cloned from — deploy them to `gh-pages`; a project export clones that branch and would pack them again. When cloning repositories yourself to export several courses, clone each into its own new empty directory, write the output outside all clones, and delete the clone afterwards; never reuse a working copy that holds earlier exports.
10. **Pack only what belongs to the course**: `-p <folder>`, `--git-subdir`, `course-path` (Action) or `path:` per course in `project.yaml`. Without `path:`, project packages contain the whole repository.
11. **PDF in GitHub Actions** needs `PUPPETEER_ARGS: "--no-sandbox --disable-setuid-sandbox"` and the Chromium libraries — `libasound2t64`, not `libasound2` — on `runs-on: ubuntu-24.04` (`ubuntu-latest` is moving to Ubuntu 26; `reference/workflows.md` §8). Use the Node-24 actions: `checkout@v7`, `setup-node@v7`, `cache@v6`. Raise `--pdf-timeout` (60000) for large courses.
12. **`peaceiris/actions-gh-pages` with `force_orphan: true`**, otherwise the `gh-pages` history grows with every binary.
13. **`[ -f x ] && cp …` as the last line of a `run:` block fails the step** when the file is missing; use `if [ -f x ]; then cp …; fi`.
14. **Per-course overrides** in `project.yaml`: `arguments:` with long flag names without `--` (`- project-generate-pdf: false`).
15. **Web exports need HTTP** (`npx serve`, `python3 -m http.server`); the project page itself opens from `file://`.
16. **GitLab CI / GitLab Pages**: a job named `pages` publishes `public/` (`-o public/index`). The `node:*` images have no Chrome — install Debian's `chromium` and set `PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium`, else PDF/DOCX fail with "Could not find Chrome". Example (run in `node:22-bookworm`): `examples/project-site/gitlab-ci.yml`, details `reference/workflows.md` §10.
