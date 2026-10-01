# From a design source to `theme.json`

The goal is not to copy pixels but to carry the *character* of the source into a
reading-and-learning interface. LiaScript content is mostly text, quizzes and code, so
every choice must stay readable for long stretches. Decide in this order:

1. **Ground** — light or dark, and how warm/cool the paper is (`background`, `text`).
2. **Voice** — the typefaces (`fonts.heading`, `fonts.body`, `fonts.mono`).
3. **Signal** — one functional accent (`accent`, `accent_text`) that works with white labels.
4. **Form** — corners, strokes, depth (`shape`).
5. **Signature** — at most two or three decorative touches (`extra_css`, see `recipes.md`),
   typically the source's secondary colors, gradients or a characteristic stroke.

Always write down *why* each choice follows from the source (`"mood"` / `"source"` in the
JSON) and tell the user.

## A. Textual description

Map adjectives onto the five decisions. Starting points (adjust, don't paste):

| Mood / brief | Ground | Voice (Google Fonts) | Signal | Form | Signature ideas |
|---|---|---|---|---|---|
| academic, calm, serious | warm off-white `#fbf9f4`, ink `#1f2430` | Source Serif 4 / Source Sans 3, or Libre Baskerville / Lato | muted blue `#2f5d8a` or oxblood `#7a2e2e` | radius 0.2–0.4rem, no shadow | thin rule under h1, small caps via letter-spacing |
| editorial, magazine | cream `#fbf7ee` | Fraunces or Playfair Display / Inter | rust `#b8481a`, ink blue | radius 0, hairlines | uppercase letter-spaced h2, heavy quote border |
| playful, children, school | white or pale tint | Fredoka, Baloo 2, Nunito | saturated purple/teal, several secondary colors | radius 1.2–2rem (pills), soft shadow | multicolor heading bar, colored effect circles |
| technical, developer | light grey `#f6f8fa` or dark `#0d1117` | Inter / IBM Plex Sans + JetBrains Mono / IBM Plex Mono | electric blue `#0969da` / green | radius 0.4rem, 1px borders | monospace headings, dot-grid background |
| corporate, neutral | white | brand font or Inter / Open Sans | brand primary | radius 0.4–0.6rem, subtle shadow | colored header rule, brand color in TOC |
| nature, sustainability | `#f6f8f1` | Merriweather / Nunito Sans | forest `#2f6b3a` | radius 0.8–1.2rem | leaf-green heading bar, earthy surfaces |
| retro, vintage | `#f4ecd8` sepia | Abril Fatface or Rye / Courier Prime | burnt orange `#b5541c`, teal | radius 0, 2px borders | double rules, uppercase headings |
| dreamy, calm night | deep indigo `#1d1740` (dark-first) | Quicksand / Nunito | magenta `#a8407f` | radius 1.2–1.6rem, glow shadow | sunset gradient bars |
| minimal, Swiss | pure white, black text | Inter Tight / Inter | one strong red `#d62828` | radius 0, no borders | big uppercase h1, red rule |
| high contrast, accessible | white / black | Atkinson Hyperlegible | `#0050b3` | radius 0.4rem, 2px focus ring | bigger `size`, `line_height` 1.6 |

Font sizes: LiaScript's body is 15 px (`1.5rem`); raise to `1.6–1.7rem` for
"airy/accessible", keep for dense technical content. `line_height` 1.5–1.65 for
long-form reading.

### Translating an artistic style (beyond colors)

When the source has a strong visual language, map it onto the five decisions *and* onto
concrete recipes (`recipes.md`, all tested):

| The source shows… | Translate into |
|---|---|
| handmade, drawn, sketchy | handwriting heading font (Cabin Sketch, Caveat Brush), readable handwriting body (Kalam ≥ 1.6rem) or a calm serif; irregular elliptical radii ("sketchy boxes"); SVG hand-drawn underline; dashed lines |
| chalk, blackboard | dark-first green/slate; chalk glow `text-shadow`; SVG noise grain; wooden frame around the slide in presentation mode |
| paper, notebook, print | cream ground; squared/dotted paper background; margin line; hairline rules; drop caps; ornamental dividers |
| painting, watercolor, gouache | soft radial-gradient blotches (fixed); gradient-painted titles; frosted-glass panels; organic image shapes with `multiply` |
| collage, scrapbook, zine | polaroid photos with tilt; tape/label-like title bars; strong offset shadows |
| retro, risograph, pop | offset `text-shadow` in a second color; thick borders (`border_width`); flat, saturated secondary colors in bars |
| geometric, architectural | radius 0, `border_width` 2px, centered titles (`heading_align`), grid background, hexagon/diagonal `clip-path` on images |
| calm, spacious, luxurious | `density: airy`, narrower `content_width`, thin serif titles, generous letter-spacing |
| dense, technical, dashboard | `density: compact`, mono accents, `header: accent` as a toolbar |
| lively, playful, motion | `motion: subtle` (never more than *lively*; always reduced-motion safe) |

Separate the two variants if the source suggests it: the dark mode does not have to be the
inverse of the light one — it can tell a related story (board ↔ exercise book).

## B. PowerPoint / .potx / Keynote export

```bash
python3 scripts/pptx_theme.py deck.pptx --draft theme.json --render slides/
bash scripts/image_palette.sh slides/slide-01.png          # optional, per slide
```

(.odp/.key: convert first — `soffice --headless --convert-to pptx deck.odp`.)

Read the JSON report together with the rendered PNGs:

| Report field | Use it for | Pitfalls |
|---|---|---|
| `theme_colors` (dk1 lt1 dk2 lt2 accent1–6) | brand palette if the deck uses theme colors | Often the untouched Office/LibreOffice default (e.g. accent1 `#18a303` from LibreOffice) — trust `used_*` more. |
| `used_fill_colors`, `used_text_colors`, `used_line_colors` | what the slides really use, weighted (slides ×3, layouts/masters ×1) | White/black dominate; a very light, heavy fill is usually a full-slide rectangle = the real background. |
| `backgrounds` | slide ground: solid / gradient / image | `image` backgrounds: run `image_palette.sh` on a rendered slide. |
| `title` / `body` fonts, sizes, bold, colors | heading/body fonts, heading weight & color | Map Office fonts to free equivalents (table below). Size ratio title/body tells how dramatic headings are. |
| `geometry`, `round_rect_radii_pt` | corners: mostly `rect` → radius 0; `roundRect` → the median radius in pt ≈ rem/10 of our scale; `ellipse`s → playful, round | Decorative shapes ≠ UI shapes; decide by feel. |
| `line_widths_pt`, `used_line_colors` | a prominent stroke → borders, heading bars, quote border in `extra_css` | |
| `outer_shadows` | > 0 → soft `shadow` | |
| `pictures`, `notes` | warnings: design lives in images (then render + `image_palette.sh`), pictures in masters (background art/texture), default color scheme | Read the notes first. |

The `--draft` output already contains background, text, accent, fonts, radius and a
`_decor_colors` list — **always** check it against the slides: e.g. the "Beehive" deck's
honey yellow `#ffde59` became decoration and the functional accent was darkened to
`#876c00`; the "Candy" deck's four candy colors became a quartered heading bar and a
gradient `hr` (see `examples/`).

Slide size → nothing to do; LiaScript is responsive. Absolute pt sizes do not transfer
1:1: slides are read from far away, a course close up. Keep LiaScript's size scale and
transfer *relations* (bold vs. light headings, uppercase, color of titles).

### Office → Google font equivalents (built into `pptx_theme.py`)

| Office / system | Free, metric- or style-compatible |
|---|---|
| Calibri | Carlito |
| Cambria | Caladea |
| Arial, Helvetica, Liberation Sans | Arimo |
| Helvetica Neue, Aptos | Inter |
| Times New Roman | Tinos |
| Georgia | Gelasio |
| Courier New | Cousine |
| Consolas | Inconsolata |
| Segoe UI, Verdana, Tahoma | Noto Sans |
| Century Gothic | Questrial |
| Gill Sans | Lato |
| Trebuchet MS | Fira Sans |
| Franklin Gothic | Libre Franklin |
| Palatino, Book Antiqua | Domine |
| Rockwell | Roboto Slab |
| Garamond | EB Garamond |

## C. Image, photo, illustration, logo, screenshot

```bash
bash scripts/image_palette.sh picture.jpg 8
```

Prints the dominant colors with share, lightness `L`, saturation `S`, a role hint, and
the image's mean lightness. Then look at the image yourself and decide:

- **Light or dark first?** Mean lightness < 45 % → the image *is* dark: design the dark
  palette explicitly from the image and derive a gentle light variant (pale tint of the
  dominant hue as background, the image's darkest color as text).
- **Ground** from the largest calm area (sky, paper, wall), not from the subject.
- **Accent** from a saturated mid-lightness color (`L` 0.3–0.6, `S` > 0.4) that the eye
  goes to — the sun, a logo mark, a jacket. Check white-label contrast.
- **accent_text** in dark mode from the image's light highlight colors (e.g. the pink
  of a sunset sky).
- **Voice** from the image's style: flat vector/illustration → rounded geometric sans
  (Quicksand, Nunito, Poppins); photography/editorial → serif headings; technical
  drawing/blueprint → mono or condensed sans; hand-drawn → Caveat/Patrick Hand only for
  headings; logos → match the logotype's family.
- **Form** from the image's shapes: soft/organic → large radius + soft tinted shadow;
  hard/geometric → radius 0 and visible strokes.
- **Signature**: gradients along the image's color ramp (`linear-gradient` of 3–4 palette
  colors) for heading bars; a subtle dot grid or paper tone for textured images.

Logos: the logo's primary color is usually the accent; add the logo with `logo:` too.

## D. PDF (brand guide, flyer, slides as PDF)

```bash
pdftoppm -png -r 60 guide.pdf page         # render pages → image_palette.sh / visual reading
pdffonts guide.pdf                          # embedded font names (poppler-utils)
pdftotext -layout guide.pdf - | grep -iE '#[0-9a-f]{6}|rgb|cmyk|pantone'   # documented colors
```

Brand guides often list exact HEX values and fonts — prefer those over sampled pixels.
CMYK/Pantone only: convert to sRGB approximately and say so.

## E. Website

With a scriptable browser, read the computed styles instead of guessing:

```js
() => { const cs = e => getComputedStyle(document.querySelector(e));
  return { bg: cs('body').backgroundColor, text: cs('body').color, font: cs('body').fontFamily,
           h1: cs('h1').fontFamily, link: cs('a').color, btn: cs('button').backgroundColor,
           radius: cs('button').borderRadius }; }
```

Otherwise take a screenshot and treat it like an image. Do not copy logos or proprietary
fonts you have no license for; pick a free equivalent and tell the user.

## Offline and licensing

Google Fonts are fetched at runtime; LiaScript courses are often used offline or
exported (SCORM, PDF, ePub). If that matters, self-host the fonts (put `.woff2` next to
the course and use `@font-face` in `extra_css`, or a `link:` to a local CSS file) or
choose a system-font stack (`"body": "system-ui, sans-serif"`, no `google` entry).
