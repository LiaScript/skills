# Recipes for `extra_css`

Snippets for the "signature" layer of a theme. Put them into `theme.json → extra_css`
(one JSON string, `\n` between rules); `build_theme.py` appends them last, so they win at
equal specificity. Everything marked **✓** was rendered and checked with LiaScript 2.x in
light and dark mode (textbook; presentation/slides where relevant). Use theme variables
(`rgb(var(--color-highlight))`, `rgba(var(--color-text), .1)`) for anything that must follow
dark mode; literal hex for decoration that should look the same in both — then check it
on the dark background, and add a `:root.lia-variant-dark …` override where needed.

Before writing selectors, know these facts (all verified):

- **Every section title has class `.h1`**, whatever its level (`<h1 class="h1">` …
  `<h6 class="h1">`), because each heading starts its own section. Use
  `.lia-slide__content .h1` for "all section titles", `h1.h1` / `h2.h1` for one level.
- `.lia-slide__content` is **re-created on every section change**; effect fragments
  (`.lia-effect`) are **inserted when they appear** → CSS entry animations replay.
- **Relative `url()` does not work** in theme CSS (resolves against the LiaScript app);
  use `url('embed:file.svg')` (inlined by `build_theme.py`), an absolute URL, or a gradient.
- Gallery tiles (`.lia-gallery .lia-figure__media`) have a black `rgba(0,0,0,.85)` backdrop.

## Layout and structure

Most of this is available as tokens — see `token-mapping.md` (`layout.heading_align`,
`layout.content_width`, `layout.header`, `density`, `shape.border_width`). Prefer them.

**✓ Centered section titles with a centered bar** — token `"layout": {"heading_align": "center"}`
plus a bar recipe below (the token centers `::after` automatically).

**✓ Accent-colored, full-bleed header** — token `"layout": {"header": "accent"}`. Doing it
by hand is fiddly: the icon menu has its own background, the TOC toggle lives in `.lia-toc`
(not in the header), the progress bar is accent-colored, and the open mobile menu needs
dark icons again. The token handles all of it.

**✓ Narrow, centered reading column** — token `"layout": {"content_width": "68ch"}`.

**✓ Airy or compact rhythm** — token `"density": "airy" | "compact"`.

**✓ Heavier strokes** — token `"shape": {"border_width": "2px"}`.

**✓ Red margin line (exercise book)**

```css
:root.lia-variant-light .lia-slide__content { border-left: 2px solid rgba(214, 69, 69, 0.55); padding-left: 3rem; }
```

**✓ Frame around the slide in presentation / slides mode** (here: a wooden board frame)

```css
:root.lia-variant-dark .lia-canvas:is(.lia-mode--presentation, .lia-mode--slides) .lia-slide__container {
  border: 1.2rem solid #6b4a2e; border-radius: 0.6rem;
  box-shadow: inset 0 0 2.4rem rgba(0, 0, 0, 0.45), 0 0.4rem 1.2rem rgba(0, 0, 0, 0.4); }
```

## Section titles

**✓ Accent bar** (gradient along the source palette)

```css
.lia-slide__content .h1::after { content: ''; display: block; width: 6rem; height: 0.4rem; margin-top: 0.8rem;
  border-radius: 1rem; background: linear-gradient(90deg, #2d2364, #a8407f, #e25e94, #f6959d); }
```

**✓ Quartered multicolor bar** — `background: linear-gradient(90deg, #7f59ae 0 25%, #60c4e4 25% 50%, #e54b89 50% 75%, #f8b622 75%)`.

**✓ Hand-drawn underline** (SVG path; one for dark "chalk", one for light "ink")

```css
.lia-slide__content .h1::after { content: ''; display: block; width: 24rem; max-width: 70%; height: 1.8rem;
  margin-top: 0.2rem; background: url('embed:assets/chalk-underline.svg') left center / 100% 100% no-repeat; }
:root.lia-variant-light .lia-slide__content .h1::after { background-image: url('embed:assets/ink-underline.svg'); }
```

**✓ Painted gradient text**

```css
.lia-slide__content :is(h1, .h1) { background: linear-gradient(100deg, #3d6f8f, #b25c7a 55%, #d99a4e);
  -webkit-background-clip: text; background-clip: text; color: transparent; }
:root.lia-variant-dark .lia-slide__content :is(h1, .h1) { background-image: linear-gradient(100deg, #9ccbd9, #e8a0a0 55%, #f3cf8a); }
```

**✓ Chalk glow** (dark board) — soft white `text-shadow`

```css
:root.lia-variant-dark .lia-slide__content :is(h1, h2, h3, .h1) { text-shadow: 0 0 1px rgba(255,255,255,.55), 0 0 0.8rem rgba(255,255,255,.18); }
:root.lia-variant-dark .lia-slide__content :is(p, li, td, th) { text-shadow: 0 0 1px rgba(255,255,255,.28); }
```

**✓ Retro offset shadow** — `.lia-slide__content .h1 { text-shadow: 0.25rem 0.25rem 0 #ffde59; }`
(use a translucent version in dark mode).

**✓ Uppercase, letter-spaced / colored titles** — tokens `heading_transform`,
`heading_letter_spacing`, `heading_color`.

## Text

**✓ Drop cap** on the paragraph right below the section title (the title sits in a `<header>`)

```css
.lia-slide__content > header + .lia-paragraph::first-letter { float: left; font-family: 'Playfair Display', serif;
  font-weight: 700; font-size: 3.4em; line-height: 0.8; margin: 0.08em 0.1em 0 0; color: rgb(var(--color-highlight-dark)); }
```

**✓ Handwritten quotes** — token `fonts.quote` (e.g. `"Caveat"`) plus `.lia-quote__text { font-size: 2.4rem; font-weight: 500; }`.

**✓ Stronger link underline** — `.lia-link { text-decoration-thickness: 0.2rem; text-underline-offset: 0.3rem; }`
(keep the underline: links must not be identified by color alone).

## Surfaces, rules, boxes

**✓ Ornamental divider** (`---` renders as `hr.lia-divider`; keep it scoped to the content, the settings menu uses `hr` too)

```css
.lia-slide__content :is(hr, .lia-divider) { border: 0; height: auto; background: none; text-align: center; overflow: visible; }
.lia-slide__content :is(hr, .lia-divider)::after { content: '\2766'; display: inline-block; font-size: 2.4rem; color: rgba(var(--color-highlight), .7); }
```

**✓ Gradient divider** — `hr, .lia-divider { height: .3rem; border: 0; border-radius: 1rem; background: linear-gradient(90deg, …); }`

**✓ Chalk / dashed lines** — `hr, .lia-divider { height: 0; border: 0; border-top: 2px dashed rgba(var(--color-text), .45); }`

**✓ Sketchy, hand-drawn boxes** — irregular elliptical radii as tokens:
`"radius": "255px 15px 225px 15px / 15px 225px 15px 255px"`,
`"radius_large": "255px 25px 225px 25px / 25px 225px 25px 255px"`; combine with a dashed quote:
`.lia-quote:not([class*='alert']) { background: transparent; border: 2px dashed rgba(var(--color-text), .4); }`

**✓ Frosted-glass quote** (needs something behind it, e.g. blotches or a texture)

```css
.lia-quote:not([class*='alert']) { background: rgba(255,255,255,.45); -webkit-backdrop-filter: blur(.8rem) saturate(1.3);
  backdrop-filter: blur(.8rem) saturate(1.3); border: 1px solid rgba(255,255,255,.7); }
:root.lia-variant-dark .lia-quote:not([class*='alert']) { background: rgba(255,255,255,.06); border-color: rgba(255,255,255,.12); }
```

**✓ Quote as neutral panel with accent stroke** —
`.lia-quote { background-color: rgb(var(--lia-grey-light)); border-left: .4rem solid rgb(var(--color-highlight)); }`
(`:not([class*='alert'])` keeps the colored alert boxes untouched).

## Backgrounds and textures

**✓ Watercolor blotches** (fixed, several soft radial gradients; header/TOC made transparent)

```css
.lia-canvas { background-image: radial-gradient(38rem 26rem at 12% 18%, rgba(232,160,160,.28), transparent 70%),
  radial-gradient(34rem 30rem at 88% 12%, rgba(156,203,217,.32), transparent 70%),
  radial-gradient(40rem 28rem at 78% 88%, rgba(243,207,138,.26), transparent 70%); background-attachment: fixed; }
.lia-header, .lia-toc { background-color: transparent; }
```

**✓ Noise / chalk-dust grain** — an SVG `feTurbulence` tile (`examples/assets/chalk-noise.svg`):
`:root.lia-variant-dark .lia-canvas { background-image: url('embed:assets/chalk-noise.svg'); }`

**✓ Squared (graph) paper** —
`.lia-canvas { background-image: linear-gradient(rgba(47,85,164,.09) 1px, transparent 1px), linear-gradient(90deg, rgba(47,85,164,.09) 1px, transparent 1px); background-size: 2rem 2rem; }`

**✓ Dot grid** — `.lia-canvas { background-image: radial-gradient(rgba(var(--color-text), .07) 1px, transparent 1px); background-size: 1.6rem 1.6rem; }`

**✓ Tinted TOC** (default theme) — `:root.lia-theme-default .lia-toc { background-color: rgb(var(--lia-grey-lighter)); }`

**✓ Colored header rule** — `.lia-header { border-bottom: .3rem solid #ffde59; }`

## Images and media

**✓ Scrapbook / polaroid photos** (not in galleries)

```css
.lia-slide__content .lia-paragraph > img, .lia-slide__content figure:not(.lia-gallery figure) img {
  background: #fff; padding: .8rem .8rem 2.4rem; box-shadow: 0 .6rem 1.6rem rgba(59,52,64,.18); transform: rotate(-1.5deg); }
.lia-slide__content .lia-paragraph img:nth-of-type(even) { transform: rotate(1.8deg); }
```

**✓ Organic gallery shapes painted into the paper**

```css
.lia-gallery .lia-figure__media { background: transparent; }   /* remove the black tile */
.lia-gallery img { border-radius: 58% 42% 55% 45% / 45% 55% 45% 55%; mix-blend-mode: multiply; }
:root.lia-variant-dark .lia-gallery img { mix-blend-mode: normal; opacity: .9; }
```

**✓ Honeycomb (hexagon) gallery**

```css
.lia-gallery .lia-figure__media { background: transparent; }
.lia-gallery img { clip-path: polygon(25% 5%, 75% 5%, 100% 50%, 75% 95%, 25% 95%, 0% 50%); }
```

`multiply` needs a light, transparent backdrop — on the default black tile images turn black.

## Motion

Use the `"motion": "subtle"` token (slide entry, effect "pop", button lift, link underline,
TOC nudge — all inside `@media (prefers-reduced-motion: no-preference)`). For custom motion:

**✓ Entry animation for each section / each effect fragment**

```css
@media (prefers-reduced-motion: no-preference) {
  .lia-slide__content { animation: theme-enter 0.5s cubic-bezier(0.2, 0.7, 0.2, 1) backwards; }
  .lia-effect { animation: theme-pop 0.45s ease-out backwards; }
}
@keyframes theme-enter { from { opacity: 0; transform: translateY(1.2rem); } }
@keyframes theme-pop { from { opacity: 0; transform: translateY(0.6rem) scale(0.98); } }
```

Use `backwards` (not `both`) so no transform stays on the content after the animation —
a lingering transform would change the containing block of fixed/sticky children.

**✓ Button lift** — `.lia-btn:not(.lia-btn--transparent):hover { transform: translateY(-2px); box-shadow: 0 .4rem 1rem rgba(var(--color-highlight), .35); }` with a 0.15s transition.

Always keep motion short (< 0.7s), never loop it on content, and wrap it in the
reduced-motion media query. Authors can still use animate.css classes per element
(`<!-- class="animated rollIn" -->`, see liascript-syntax); those set their own `animation`.

## Principles

- Pick **one** artistic idea and apply it consistently (every title, every rule, every
  photo) rather than many one-offs.
- Decoration uses the *source's* secondary colors; functional UI stays on `accent`.
- Handwriting fonts work for body text when the size goes up (`"size": "1.65rem"`) and the
  line height to ~1.6 — verify legibility at 100 % zoom.
- Textures stay below ~10 % opacity; text contrast is measured against the base color.
- Never restyle `.icon` elements' `font-family` (icons turn into boxes) and never put
  `border-radius` on every `input` (radio buttons become squares) — the adapter handles both.
