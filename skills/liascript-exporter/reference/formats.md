# Export formats and presets

Every format with its options, checked by running the exporter. Presets first, then one section per format.

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

> ⚠️ The preset ID must be exact — there is no bare `--moodle`. Presets set no `masteryScore` except LearnWorlds; add `--scorm-masteryScore 80` yourself if needed. For ILIAS, OPAL and Open edX the presets differ from the tested commands in §3.1 — when generating CI workflows, prefer the explicit flags from §3.1.

---

## 3. Export Formats

### 3.1 SCORM 1.2

```bash
liaex -i README.md --format scorm1.2 --output my-course
```

Produces `my-course.zip`. With the default connector SCORM 1.2 stores only the location, quiz and survey states are lost after a reload — add `--scorm-storage suspend` or use SCORM 2004.

**Key options:**
| Option | Description |
|--------|-------------|
| `--scorm-masteryScore` | 0–100, default **0** (everyone passes). The tested LMS commands below use 80. |
| `--scorm-typicalDuration` | ISO 8601 duration, e.g. `PT1H30M0S`. Default: `PT0H5M0S` |
| `--scorm-organization` | Sets organization in `imsmanifest` |
| `--scorm-iframe` | Fix for ILIAS, OpenOLAT, learnworlds.com that break startingParameter |
| `--scorm-embed` | Embeds Markdown into JS code — use for Moodle 4, OPAL, Open edX |
| `--lia-subfolder` | Places course files in `content/` subfolder (implies `--scorm-embed`) |
| `--scorm-storage suspend` | Keep the whole learner state and report readable answers (see below); default `default` |
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

**`--scorm-storage suspend`** (SCORM 1.2 and 2004): quizzes, surveys, tasks, the code of code blocks, settings and the last slide are kept compressed in `cmi.suspend_data`, also in SCORM 1.2. Every quiz, survey, task list and code project is reported as one interaction named after its question, with answer, correct answer and result (1.2 as readable text like `Python; HTML`, 2004 with typed interactions). Status: `incomplete` from the start, `completed` once all quizzes and surveys are done, `passed`/`failed` only with a mastery score.
- In SCORM 1.2 `passed`/`failed`/`completed` end the attempt (Moodle then opens it for review only), so with a mastery score a 1.2 package reports its score only once everything is done.
- Limits: `cmi.suspend_data` holds 4096 characters in 1.2 (64000 in 2004); if it does not fit, code is dropped first, then tasks, surveys, quizzes (named in the browser console). 1.2 reports at most 255 characters per answer. Code that is edited but never run is not stored. At most 250 elements are reported.
- Moodle shows 1.2 answers in the activity's *Interactions report* (downloadable for all learners), 2004 answers only under *Track details* per attempt.

```bash
liaex -i course/README.md -f scorm1.2 --scorm-storage suspend --scorm-masteryScore 80 --scorm-embed
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
| `--epub-cover` | Path or URL to cover image (default: the course `logo`; a URL that cannot be loaded leaves the book without cover, with a warning) |
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

The package restores the learner's state from the LRS on the next visit (per learner and registration, up to 10000 statements): last slide (`experienced`), quizzes and surveys (`answered`), task lists and code that was run (`interacted`). Every quiz, survey, task list and code project is a `cmi.interaction` activity named after its question, with options, correct answer and a plain-text answer in `result.extensions["http://liascript.github.io/extensions/answer"]`. If a slide's code blocks changed since the learner started, its code starts afresh.

---

### 3.9 Android APK

```bash
liaex -f android \
  -i README.md \
  --android-sdk /home/user/Android/Sdk \
  --android-appId io.github.myorg.mycourse \
  --output output
```

Produces `output.apk` (debug build by default). Uses Capacitor.js. Best done via Docker (see "Install" in `SKILL.md`). Not available in the web app.

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

### 3.9b Desktop app (macOS, Windows, Linux)

Wraps the offline web export into a [Neutralinojs](https://neutralino.js.org/) app that uses the system webview (no bundled browser). Builds on any system in seconds, offline, without Xcode, Wine or Docker:

```bash
liaex -i README.md -f desktop --desktop-appId io.github.example.course -o out/kurs
# → out/kurs-win-x64.exe   out/kurs-mac-universal.zip   out/kurs-linux-x64.zip
```

| Option | Meaning |
|---|---|
| `--desktop-appId` | **required**, reverse-domain id |
| `--desktop-appName` | app name (default: course title) |
| `--desktop-icon` | PNG, 1024×1024 (default: LiaScript logo) |
| `--desktop-platform` | subset of `mac,win,linux` (default: all three) |

The `.exe` carries the course inside; the mac zip holds one universal `.app`, the Linux zip a folder with the binary and `resources.neu`. The apps are unsigned: macOS needs right-click → Open (or `xattr -cr App.app`), Windows SmartScreen → More info → Run anyway; Linux needs `libwebkit2gtk-4.1`. There is no `--project-generate-desktop`.

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

### 3.12 H5P

```bash
liaex -i README.md --format h5p --output course
```

Produces `course.h5p` for Moodle (H5P activity or content bank), ILIAS, WordPress, Drupal, Lumi and other H5P platforms. It carries the LiaScript runtime as its own library `H5P.LiaScript`.

| Option | Description |
|--------|-------------|
| `--h5p-height` | Height in pixels (default 600); the H5P fullscreen button shows it on the whole screen |
| `--h5p-mastery` | Percentage of points needed to pass, e.g. `80` (default: completion only) |

- **The first LiaScript package of a platform must be uploaded by an administrator**: installing a library needs `moodle/h5p:updatelibraries` in Moodle, a switched-on right in WordPress/Drupal. After that teachers add courses like any H5P content. h5p.com accepts no own libraries.
- A platform uses the newest `H5P.LiaScript` it has seen for every LiaScript course, so exporting one course again updates the runtime of all others.
- Grades: once every quiz is answered and every survey submitted, the course reports `completed` with its points (and passed/failed with `--h5p-mastery`). Answers, tasks, code and the slide are kept in H5P's user data (Moodle: activity setting *Save content state*).
- Only images, audio, video, PDFs, office documents and fonts are packed; svg images are embedded as data URLs; HTML and JavaScript files are left out with a warning — a course that loads its own scripts from files must load them from a URL.

---

### 3.13 Project (Index Website)

See `reference/project.md` §4 for the full project workflow.

```bash
liaex -i project.yaml --format project --output index
```
