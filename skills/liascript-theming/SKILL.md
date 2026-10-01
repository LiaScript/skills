---
name: liascript-theming
description: >
  Restyle the look of a LiaScript course — colors, fonts, font sizes, corner radius,
  borders, shadows, surfaces, light and dark mode — by generating a tested header block
  (`link:` + `@style … @end` + `@custom … @end`) for the course's README.md. Works from a
  textual description ("calm, academic, dark blue, rounded"), from a PowerPoint/.potx
  (extracts theme colors, fonts, sizes, shapes and the colors actually used), from an image,
  photo, logo or screenshot (palette + mood), or from a PDF / website / corporate design
  guide. Use when someone wants to change, customize, brand or theme a LiaScript course,
  match a corporate design (CI/CD), recreate the style of slides or a picture, add a dark
  mode, or asks about LiaScript's CSS variables, `custom:` macro, `@style` or theme classes.
  Also triggers on German requests such as "Design des Kurses ändern", "eigenes Theme",
  "Farben und Schriften anpassen", "wie meine PowerPoint aussehen lassen",
  "Stil/Stimmung aus dem Bild übernehmen", "Corporate Design für LiaScript",
  "CSS-Variablen in LiaScript". Ships ready-made designs that can be applied by name
  in one step: paper-ink, sunset-lake, candy, beehive, chalkboard (Tafel & Heft /
  Kreidetafel), watercolor (Aquarell), manuscript (Codex / Mittelalter / alte
  Bibelhandschrift) — e.g. "nimm das Chalkboard-Theme", "apply the manuscript design".
  For general course syntax see liascript-syntax; for shipping a theme as an importable
  template see template-development.
license: CC0-1.0
---

# LiaScript Theming

## Ready-made designs (apply by name)

If the user names one of these (in any language), skip the design step: inject it,
render once, done. `python3 scripts/build_theme.py --list` prints the same table.

| Name | Also known as | Look |
|---|---|---|
| `paper-ink` | Paper & Ink | calm editorial: cream paper, ink text, rust accent, serif titles, sharp corners |
| `sunset-lake` | Sunset Lake | dreamy indigo → violet → pink, rounded, soft shadows, gradient title bars |
| `candy-pptx` | Candy | playful four-color (purple/cyan/pink/amber) on white, pill buttons, gradient rules |
| `beehive-pptx` | Beehive, Bienenwabe | cream with honey-yellow decoration, hexagon gallery, retro title shadow |
| `chalkboard` | Tafel & Heft, Kreidetafel, Schulheft | dark = green chalkboard with chalk dust, light = squared exercise book; handwriting fonts |
| `watercolor` | Aquarell | watercolor blotches, painted gradient titles, drop caps, glass quotes, polaroid photos |
| `manuscript` | Codex, Mittelalter, Bibelhandschrift, illuminated manuscript | parchment, red blackletter rubrics, lapis-and-gold initials, double-ruled frame; dark = leather binding |

```bash
python3 scripts/build_theme.py manuscript --inject path/to/README.md   # name or theme.json path
python3 scripts/build_theme.py manuscript --css codex.css              # as a stylesheet for link:
```

A named design can still be adjusted: copy `examples/<name>.json`, change tokens
(colors, fonts, `extra_css`), rebuild. Details per design in `examples/README.md`.

LiaScript renders every course with the same stylesheet; its look is driven by a handful
of CSS variables plus a lot of compiled values (fonts, radii, spacing) that only direct
CSS reaches. This skill turns *any* design source into one header block that restyles
the whole course, keeps LiaScript's own color themes and dark mode working, and has been
verified by rendering (LiaScript 2.x, local build and liascript.github.io).

The pipeline is: **source → design tokens (`theme.json`) → `build_theme.py` → header block
→ render & check.** You do the design judgement (step 2); the script does the fiddly CSS,
the dark palette and the contrast checks (steps 3–4).

## Navigation

| File | Covers | Read when… |
|---|---|---|
| `reference/mechanisms.md` | `@style`, `custom:`, `link:`, `font:`, `dark:`; injection order, specificity traps, what persists | you need to know *why* the block looks the way it does, or debug a style that does not apply |
| `reference/token-mapping.md` | `theme.json` schema, how each token maps to LiaScript, dark-palette derivation, contrast rules | writing or editing a `theme.json` |
| `reference/design-extraction.md` | turning a description, PPTX, image, PDF or website into tokens; mood → token heuristics; font pairing & Office→Google font map | step 2, always |
| `reference/recipes.md` | tested `extra_css` snippets: layout, section titles (bars, hand-drawn lines, gradient text, chalk glow, offset shadow), drop caps, ornaments, glass, textures (grain, grid, blotches), photo frames, gallery shapes, motion | the theme needs character beyond colors/fonts/shape |
| `reference/css-surface.md` | every CSS variable, root/mode class, component class, hard-coded value, font/size scale | writing custom selectors |
| `reference/known-gaps.md` | limits of the current interpreter and workarounds | something cannot be themed, or reporting upstream |
| `templates/adapter.css` | the fixed CSS layer that maps tokens onto LiaScript | never edit per theme; `build_theme.py` embeds it |
| `templates/theme.template.json` | empty token file | starting a theme by hand |
| `templates/showcase/` | a course that shows every styleable element once | previewing a theme (copy it first) |
| `examples/*.json` + `examples/README.md` | seven finished themes — from text (Paper & Ink, Tafel & Heft, Aquarell, Codex), an image (Sunset Lake) and two PPTX decks (Candy, Beehive) — with design notes and SVG assets | as starting points and for calibration |

Scripts (Python 3 standard library; `image_palette.sh` needs ImageMagick; `--render` needs
LibreOffice + poppler):

| Script | Does |
|---|---|
| `scripts/build_theme.py theme.json [--inject course.md] [--css out.css] [--check]` | tokens → header block, dark palette, WCAG report, layout/density/motion features, `embed:` assets, idempotent injection |
| `scripts/pptx_theme.py deck.pptx [--draft theme.json] [--render dir]` | PPTX/POTX → report of theme + actually used colors, fonts, sizes, shapes; draft tokens; slide PNGs |
| `scripts/image_palette.sh image [n]` | dominant colors with share, lightness, saturation, role hint, mean lightness |
| `scripts/serve.py course-dir [--port N] [--app dist]` | serve a course with CORS and print the preview URL |

## Workflow

1. **Identify the source** and what the user wants: faithful recreation (slides, CI guide)
   or mood transfer (a photo, "make it feel like…"). Ask only if it changes the outcome
   (e.g. "light or dark by default?"). Note the course's existing header — never drop
   existing `@style` content, macros or `link:`s.
2. **Extract tokens** → write a `theme.json` (schema in `reference/token-mapping.md`):
   - Text: use the mood heuristics in `reference/design-extraction.md`.
   - PPTX/POTX: `python3 scripts/pptx_theme.py deck.pptx --draft theme.json --render slides/`,
     then **look at the rendered slides** and correct the draft (theme color schemes are often
     generic; the real design lives in direct formatting).
   - Image/photo/logo/PDF page: `scripts/image_palette.sh img.png` + your own visual reading
     of mood, shapes and typography.
3. **Build**: `python3 scripts/build_theme.py theme.json` prints the block and a WCAG contrast
   report; `--inject course.md` writes it into the header (idempotent, keeps other content);
   `--css theme.css` also writes a plain stylesheet.
4. **Fix contrast failures** (FAIL = must fix; warn = judge). A too-light brand color is
   automatically darkened for functional use — keep the original as decoration in `extra_css`.
5. **Render and look** (strongly recommended). Serve the course with CORS:
   `python3 scripts/serve.py <course-dir>` → open the printed liascript.github.io URL (or,
   with a local LiaScript build, `--app <dist>`). Check light + dark, textbook +
   presentation mode, and the settings panel's color swatches. With a scriptable browser
   (Playwright, Puppeteer, Chrome DevTools) set the reader settings via
   `localStorage.settings` = `{"theme":"default","light":false,"mode":"Presentation",…}`
   and reload — see `reference/mechanisms.md`. Iterate on `theme.json`, not on the output.
6. **Deliver**: the injected header (or block + `theme.json` so the user can rebuild), a
   short description of the design decisions, and any contrast/gap caveats.

## Cheatsheet — the generated block

```markdown
<!--
link:     https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700&family=Inter:wght@400;600;700&display=swap

@style
/* ==== liascript-theming:start ==== */
:root { --theme-font-body: 'Inter', sans-serif; --theme-font-heading: 'Fraunces', serif;
        --theme-radius: 0; --theme-radius-large: 0; --theme-shadow: none; … }
:root.lia-variant-light { --color-background: 251,247,238; --color-text: 33,37,61; … }
:root.lia-variant-dark  { --color-background: 35,25,21;    --color-text: 235,231,229; … }
:root:is(.lia-theme-default, .lia-theme-custom) { --color-highlight: 184,72,26; … }
/* … adapter.css (fonts, radius, dark-mode fixes) … */
/* ==== liascript-theming:end ==== */
@end

@custom
--color-highlight-menu: 255,255,255;
@end
-->
```

Rules that are easy to get wrong (all verified):

- LiaScript colors are **RGB triples without `rgb()`**: `--color-highlight: 184,72,26;`.
- `custom:` alone is *not* a theme: it only applies when the reader picks the extra color
  swatch (labelled "Default" — a known bug) in the settings. The design itself belongs in
  `@style`; `@custom` just offers a variant (here: accent-colored sidebar).
- Accent colors are scoped to `.lia-theme-default`/`.lia-theme-custom` on purpose, so
  readers can still choose LiaScript's turquoise/blue/red/yellow themes.
- LiaScript lightens accents in dark mode by multiplying RGB (×1.8–4.8). The adapter
  replaces that with the theme's own `accent_text` — never rely on the multiplication.
- **Every section title is `<hN class="h1">`** (whatever its level), and `.h1` outranks
  element rules — style titles with `.lia-slide__content .h1`, one level with `h2.h1`.
- Buttons, pagination and the colored TOC always use **white** labels on the accent.
- **Relative `url()` in theme CSS points at the LiaScript app, not the course** — use
  `url('embed:file.svg')` in `extra_css` (inlined by the script) or absolute URLs.
- **Never leave an empty block (`@style` ⏎ `@end`) in a header** — LiaScript then drops the
  whole header silently (macros, language, links).
- `@style` is local; it is **not** carried along when another course `import:`s this one.
  Use `--css` + `link:` (or a template, see template-development) for reusable themes.

Beyond colors, fonts and shape, `theme.json` has verified tokens for **layout**
(`heading_align`, `content_width`, accent `header`), **density** (`compact`/`airy`),
**stroke** (`border_width`) and **motion** (`subtle`/`lively`, reduced-motion safe); the
artistic layer (textures, hand-drawn lines, chalk glow, gradient titles, drop caps,
ornaments, glass panels, polaroid/hexagon/organic images, slide frames) comes from the
tested snippets in `reference/recipes.md` and the "Translating an artistic style" table in
`reference/design-extraction.md`.
