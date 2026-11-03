# GitHub Actions, GitHub Pages and PDF in CI

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

      # Chromium system libraries for PDF: see §8

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
          if [ -f logo.jpg ]; then cp logo.jpg gh-pages-deploy/; fi
          if [ -f theme.css ]; then cp theme.css gh-pages-deploy/; fi   # stylesheet from link: in project.yaml
          if [ -d site ]; then cp -r site gh-pages-deploy/; fi

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
      # Fixed path outside the repo: liaex writes ./assets/<format>/ into its CWD
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

      # Chromium system libraries for PDF: see §8

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
          if [ -f theme.css ]; then cp theme.css gh-pages-deploy/; fi   # stylesheet from link: in project.yaml
          if [ -d site ]; then cp -r site gh-pages-deploy/; fi
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

Supported `format` values: `scorm1.2`, `scorm2004`, `pdf`, `web`, `ims`, `xapi`, `h5p`, `rdf`, `json`, `project` — for ePub, DOCX or Android install the CLI instead (§5.1 / Docker). Inputs use kebab-case (`scorm-mastery-score`, `pdf-print-background`, …); outputs are `output-file`, `file-size`, `format`, `success`.

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
