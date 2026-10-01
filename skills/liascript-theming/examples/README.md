# Example themes

Each file is a complete `theme.json`; build one with

```bash
cp -r ../templates/showcase /tmp/showcase          # never theme the template itself
python3 ../scripts/build_theme.py paper-ink.json --inject /tmp/showcase/README.md
python3 ../scripts/serve.py /tmp/showcase          # open the printed URL
```

All were rendered with the showcase course in light and dark mode and in textbook
mode; the first four also with presentation mode and the default, custom and red color
themes, the artistic ones (chalkboard, watercolor, beehive) also in slides mode.
`assets/` holds the small SVGs the chalkboard theme embeds via `url('embed:…')`.

| File | Source | What it demonstrates |
|---|---|---|
| `paper-ink.json` | text: "calm, editorial, warm paper with a rust-orange accent, sharp corners" | minimal token set (3 colors), serif headings, radius 0, auto dark palette |
| `sunset-lake.json` | image: flat vector sunset landscape (indigo → violet → pink) | explicit dark palette for a dark-first source, heading colors, rounded shapes + tinted shadow, gradient heading bar from the image's color ramp |
| `candy-pptx.json` | PPTX: LibreOffice "Candy" template, via `pptx_theme.py --draft` | faithful font (Noto Sans), accent from the most used saturated fill, pill buttons, quartered 4-color bar and gradient `hr` from the deck's secondary colors |
| `beehive-pptx.json` | PPTX: LibreOffice "Beehive" template | cream background detected from a full-slide rectangle; honey yellow `#ffde59` too light for white labels → auto-darkened accent `#876c00`, yellow kept as decoration (header rule, heading bar, quote stroke, retro offset shadow); hexagon-cut gallery images |
| `chalkboard.json` | text: "school — dark like a chalkboard, light like a squared exercise book, hand-drawn" | two personalities in one theme: dark = green board with SVG chalk-dust grain, chalk glow, yellow hand-drawn underline, wooden frame in presentation/slides; light = squared paper, red margin line, blue-ink underline; handwriting fonts (Cabin Sketch / Kalam), sketchy irregular box radii, dashed chalk lines |
| `manuscript.json` | text: "medieval — like an old illuminated bible manuscript" | parchment texture with vignette (SVG turbulence), red blackletter rubrics with gold fleurons, lapis initial in a gold-ruled box under each title, double-ruled page frame with inner gold line, marginalia quotes, ornamental `— ❦ —` rules; dark = leather binding with gold lettering |
| `watercolor.json` | text: "watercolor — light, playful, paint bleeding into paper, photos like glued in" | fixed watercolor blotches behind a transparent header/TOC, painted gradient titles, drop caps, ornamental ❦ divider, frosted-glass quote with handwritten text, polaroid photos with tilt, organic gallery shapes blended into the paper |

Design notes:

- **Paper & Ink** — Fraunces (high-contrast serif) for headings evokes print; Inter keeps
  UI text neutral; rust accent on cream; no radius, no shadow = paper.
- **Sunset Lake** — Quicksand/Nunito echo the rounded vector shapes; the dark variant is
  the picture itself (deep indigo ground, sunset pink `#f6959d` as text accent); the light
  variant is a pale lilac derived from it.
- **Candy** — four equal candy colors cannot all be the accent: purple (most used,
  readable with white) does the work, the others appear only in decoration.
- **Beehive** — shows the "decoration vs. function" split that most brand yellows,
  light greens and pastels need.
- **Tafel & Heft** — the dark and light variants tell two related stories (board vs.
  exercise book) instead of being inversions of each other; decoration is scoped with
  `:root.lia-variant-dark` / `-light`. Handwriting body text stays legible at 1.65rem.
- **Codex** — one century-old recipe: parchment ground, black text, red rubrics, blue/gold
  initials. Body text stays a readable Garamond at 1.75rem; only titles use blackletter.
- **Aquarell** — all decoration lives *behind* or *around* the text (background, frames,
  ornaments); the text itself stays a calm serif, so the page reads well despite the art.
