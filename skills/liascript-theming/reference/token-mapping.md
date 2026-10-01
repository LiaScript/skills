# Design tokens → LiaScript

`scripts/build_theme.py` reads a `theme.json` and emits the header block. Only three
colors are required; everything else has a sensible default or is derived.

## `theme.json` schema

```jsonc
{
  "name": "Paper & Ink",                 // shown in a CSS comment
  "source": "…", "mood": "…",            // free text, for humans (ignored by the script)

  "fonts": {
    "body": "Inter",                     // family name or full stack ("Inter, Arial, sans-serif")
    "heading": "Fraunces",               // h1–h3 (+ quote text unless "quote" is set)
    "mono": "JetBrains Mono",            // code blocks, Ace editor, inline code, kbd
    "subheading": "Inter",               // optional: h4–h6, summary, accordion (default: body)
    "quote": "Fraunces",                 // optional: blockquote text (default: heading)
    "google": ["Fraunces:wght@600;700", "Inter:wght@400;600;700"],  // → one link: line
    "links": ["https://example.org/fonts.css"],                    // optional extra stylesheets
    "heading_weight": 700,               // optional (default 600)
    "heading_letter_spacing": "0.04em",  // optional
    "heading_transform": "uppercase",    // optional
    "line_height": 1.6,                  // optional (default 1.47)
    "size": "1.6rem"                     // optional body size (default 1.5rem; 1rem = 10px)
  },

  "light": {                             // hex colors
    "background": "#fbf7ee",             // required
    "text": "#21253d",                   // required
    "accent": "#b8481a",                 // required — fills: buttons, pagination, active TOC bar, checkboxes, links
    "accent_text": "#a83e12",            // optional — accent used as text on the background (≥ 4.5:1)
    "border": "#e2dac8",                 // optional (default: 12 % text into background)
    "surface": "#f3ecdd",                // optional — alternating table rows, subtle panels
    "surface_strong": "#e9dfca",         // optional — notes, TTS bar, dividers, disabled buttons
    "keep_accent": false                 // optional — true = do not auto-darken a too-light accent
  },

  "dark": "auto",                        // or an object with the same keys as "light"

  "heading_color": { "light": "#2d2364", "dark": "#ffdfde" },  // optional; default = text color

  "shape": {
    "radius": "0.8rem",                  // buttons, inputs, selects, dropdowns, pagination, settings menu
    "radius_small": "0.4rem",            // checkboxes, kbd, tooltips, inline code
    "radius_large": "1.6rem",            // details, quotes, code blocks, tables, cards
    "shadow": "0 0.4rem 1.6rem rgba(45,35,100,.12)",  // on the same "large" surfaces
    "shadow_popup": "…",                 // optional: settings submenu
    "border_width": "2px"                // optional: all 1px UI borders (buttons, inputs, tables, details, header, TOC)
  },

  "layout": {                            // optional, each key only emitted when set
    "heading_align": "center",           // section titles; centers ::after bars too
    "content_width": "68ch",             // centered reading column in textbook mode
    "header": "accent"                   // full-bleed header in the accent color, white icons
  },
  "density": "compact",                  // optional: "compact" | "airy" (line height, paragraph/heading/quote/table spacing)
  "motion": "subtle",                    // optional: "subtle" | "lively" (slide enter, effect pop, button hover, link, TOC);
                                         //   always wrapped in prefers-reduced-motion: no-preference

  "custom": "--color-highlight-menu: 255,255,255;",   // optional: body of @custom (default shown)
  "extra_css": "…"                        // optional: appended last (see recipes.md); url('embed:file') is inlined
}
```

Keys starting with `_` (e.g. `_decor_colors`, `_review` from `pptx_theme.py`) are ignored.
Sizes use `rem` where `1rem = 10px` (LiaScript sets `html { font-size: 62.5% }`).

**`url('embed:path')`** in `extra_css` is replaced by a `data:` URI of that file (path
relative to `theme.json`; SVG URL-encoded, other formats base64). Needed because relative
`url()`s in theme CSS resolve against the LiaScript app, not the course (see
`mechanisms.md`). Keep embedded files small — they load with every page (warning > 150 KB).

Order of the generated CSS: tokens → palettes → adapter → layout/density/motion features →
`extra_css`. Later wins at equal specificity, so `extra_css` can override any feature.

| Feature token | Verified effect |
|---|---|
| `density: compact` | line height 1.4, paragraphs 0.6rem apart, table cells 0.6rem, quotes 1.4rem padding, blocks 1.4rem |
| `density: airy` | line height 1.7, paragraphs 1.6rem, list items 0.6rem, table cells 1.4rem, quotes 3.2/4rem, blocks 3.2rem |
| `layout.header: accent` | header spans full width in `accent`; icons, TOC toggle, progress bar white; open mobile menu and settings submenu use the accent (dark: `accent_text`) — checked desktop/mobile, open/closed, light/dark |
| `layout.content_width` | narrower centered column; only textbook mode (presentation/slides keep LiaScript's widths) |
| `shape.border_width` | 2px tested; radio/checkbox borders only while unchecked (checked state uses its own thick border) |
| `motion` | `.lia-slide__content` is re-created on every section change and effect fragments are inserted when shown, so the entry animations replay each time; nothing animates under `prefers-reduced-motion: reduce` (tested with emulation) |

## What each token controls

| Token | CSS it becomes | Visible on |
|---|---|---|
| `background` | `--color-background` | page, header, TOC (default theme), cards, tables, outline buttons |
| `text` | `--color-text` | body text, TOC links, headings (unless `heading_color`) |
| `border` | `--color-border` | header rule, TOC dividers, table grid, details, hr |
| `accent` | `--color-highlight` (+ `--color-highlight-menu` in default theme) | buttons (white label!), pagination, links, active TOC bar, header icons, checkbox/radio, quiz icons, code block frame, progress, focus of inputs, quote background (15 %), TOC background in any non-default theme |
| `accent_text` | `--color-highlight-dark` | link hover, list markers, inline code, quote text, `summary`; **in dark mode also** links, header icons, quiz labels, outline buttons (via adapter) |
| `surface` | light: `--lia-grey-lighter` · dark: `--lia-grey-dark` | alternating table rows; dark: settings submenu |
| `surface_strong` | light: `--lia-grey-light` · dark: `--lia-anthracite` | notes, TTS/voice bar, script refresh button, TOC separators, disabled buttons |
| fonts | `--theme-font-*` → `--global-font-*` + explicit selectors | see `templates/adapter.css` |
| shape | `--theme-radius*`, `--theme-shadow` | see table above |

Scoping in the generated CSS:

- `background/text/border/surface*` → `:root.lia-variant-light` / `:root.lia-variant-dark`
  — apply under every color theme.
- `accent/accent_text` → `:root:is(.lia-theme-default, .lia-theme-custom)` (and `.lia-variant-dark`
  for the dark accents) — the built-in turquoise/blue/red/yellow themes stay selectable.

## Contrast rules (checked by `build_theme.py`)

| Pair | Minimum | Why |
|---|---|---|
| text / background (light & dark) | 4.5 **hard** | body text |
| accent_text / background | 4.5 **hard** | links (dark), markers, inline code, quote text |
| text / surface_strong | 4.5 **hard** | notes panel, TTS bar |
| white / accent | 4.5 warn | button, pagination and colored-TOC labels are always white |
| accent / background | 3.0 warn | UI parts: checkbox borders, icons, focus |
| accent / background (light) | 4.5 note | links use the accent in light mode |

If the light `accent` gives less than 4.5:1 with white, the script darkens it until it
reaches 4.5:1 against white *and* the background, and prints a note. Brand yellows,
light greens and pastels therefore become decoration: keep the original hex in
`extra_css` (heading bars, borders, gradients) and let the darker variant do the
functional work. Set `"keep_accent": true` only when the user insists.

## Dark palette derivation (`"dark": "auto"`)

From the light accent's hue `h` and saturation `s`:

| Dark token | Rule |
|---|---|
| background | HSL(h, min(s, .25), 11 %) — a near-black tinted with the accent |
| text | HSL(h, min(s, .15), 91 %) |
| accent (fill) | the light accent (darkened if white labels would fail) |
| accent_text | accent at 62 % lightness, raised until ≥ 5.5:1 on the dark background |
| border / surface / surface_strong | HSL(h, ≤ .2, 24 % / 15 % / 20 %) |

Give an explicit `"dark": {…}` when the source *is* dark (night photo, dark slides) or
when the brand prescribes dark colors; the script then only fills in missing keys.

## Output variants

- `build_theme.py theme.json` — prints `link:` + `@style` + `@custom` for pasting.
- `--inject course.md` — writes into the header comment: replaces a previous block between
  the `liascript-theming:start/end` markers, otherwise prepends it inside an existing
  `@style` (other CSS is kept) or adds a new one; replaces `@custom` (or a one-line
  `custom:`, with a note); adds its font `link:` lines on top and on re-runs removes only
  the links it added itself (they are recorded in a `/* links: … */` comment inside the
  block); leaves every other key, macro and `link:` untouched.
- `--css theme.css` — the same CSS as a file, for `link:`-based reuse across courses.
- `--check` — contrast report only; exit code 1 on hard failures.
