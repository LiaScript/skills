# Styling mechanisms in LiaScript

Everything here was verified by rendering with the LiaScript 2.x interpreter (local build and
liascript.github.io, 2026-09). Source references point into the LiaScript repo
(`github.com/LiaScript/LiaScript`).

## The header keys that affect the look

| Key | What it does | Carried along on `import:`? |
|---|---|---|
| `@style … @end` (or `style:` one-liner) | Raw CSS, appended as a `<style>` element to `<head>` **after** LiaScript's own stylesheet. | **No** — local to the course. |
| `link: url` | Loads an external stylesheet (`<link rel=stylesheet>`). Repeatable / multi-line. Use for web fonts. | Yes. |
| `@custom … @end` (or `custom:`) | Text is wrapped as `:root { <text> }` in `<style id="lia-custom-style">`, **only while the reader has selected the extra "custom" color swatch**. | — |
| `font: Name` | Appends `Name` to `--global-font-family/-mono/-headline` **as a fallback after** LiaScript's fonts — so it only shows for glyphs the built-in fonts lack. Not a way to switch fonts. | — |
| `dark: true` / `dark: false` | Forces the initial light/dark mode on every load (there is no `light:` key). | — |
| `logo: url` | Image on the course card / title and `og:image`. | — |
| `icon: url` | Course icon (can also be set per section). | — |
| `<!-- style="…" class="…" -->` | Per-element styling in the body (see liascript-syntax, "Custom Styling"). | — |

There is **no `theme:` header key**; a course cannot preselect a color theme.

## `@style` in detail

- Injected once per load, after the main CSS, so a plain `:root { … }` or `h2 { … }` beats
  LiaScript's equal-specificity rules by source order.
- At-rules work: `@import url(…)` (must be the first rule), `@media`, `@keyframes`,
  `@font-face` — tested. Caveat: if the course or an imported template defines a macro with
  the same name (e.g. `@media`), LiaScript would expand it; avoid such macro names.
- Being local is a feature for one-off themes and a limitation for shared ones: for a
  theme used by many courses, publish `build_theme.py --css theme.css` and include it with
  `link:`, or wrap it in a template course that other courses `import:`.

### Three traps found by testing

1. **A block macro whose `@end` directly follows its opening line (`@style` ⏎ `@end`, or any
   `@name` ⏎ `@end`) makes LiaScript silently drop the whole header** — author, language,
   logo, `link:`, macros, `@style`; the course still renders, with defaults. Tested at the
   start and the end of the header. With one blank line in between it parses. Never leave
   an empty block in a header; `build_theme.py --inject` always fills the one it writes.
2. **Relative `url()` in theme CSS resolves against the LiaScript app, not the course.**
   `url('img.png')` in `@style` becomes `https://liascript.github.io/img.png` (404). A
   stylesheet loaded via `link: theme.css` is fetched relative to the course, but LiaScript
   inlines it as a `blob:` — its relative `url()`s break the same way. Use absolute URLs,
   gradients, or `url('embed:file')` in `extra_css` (inlined as a data URI by `build_theme.py`).
3. **Every section title carries class `.h1`**, whatever its level: `# A` → `<h1 class="h1">`,
   `### B` → `<h3 class="h1">`. The utility rules for `.h1` (0,1,0) beat element rules
   (`h3 {}`), so style section titles through `.lia-slide__content .h1`, and target one level
   with `h2.h1`. LiaScript starts a new section at every heading, so the section title is
   usually the only heading inside `.lia-slide__content`.

Also useful: `.lia-slide__content` is re-created on every section change and effect
fragments (`.lia-effect`) are inserted into the DOM when they appear — CSS entry
animations therefore replay on each step.

## `@custom` in detail (the "custom" theme)

Source: `Lia/Script.elm` (`customTheme = Dict.get "custom" definition.macro`),
`Lia/Settings/View.elm` (`viewTheme`), `service/Database.ts` (`lia-custom-style`).

- If a course defines `custom`, the settings panel shows a sixth color swatch
  (class `.lia-radio.is-custom`, a blue→red gradient). Its title is "Default" — the same
  label as the real default swatch (a known bug, see `known-gaps.md`).
- Only when the reader picks it: `<html class="lia-theme-custom …">` and
  `<style id="lia-custom-style">:root {<your text>}</style>` is appended to `<head>`
  (after `@style`, so it wins at equal specificity).
- It is never selected automatically.
- The chosen theme is stored in `localStorage.settings` **for all courses** on that
  origin. A reader who once picked "red" sees red in every course — that is why the
  generated block keeps the course accent for `.lia-theme-custom` too: the custom swatch
  becomes the reader's way back to the course's own design.
- Because the text is wrapped as `:root {…}`, it cannot contain selectors — except by
  closing the brace: `--x: 1; } :root.lia-theme-custom.lia-variant-dark { --x: 2;` works
  (tested) but is a hack that depends on the wrapping; prefer `@style`.
- `:root {}` (specificity 0,1,0) loses to `:root.lia-variant-dark` and
  `:root.lia-theme-red` (0,2,0), so `custom:` cannot override dark-mode colors by itself.
- Any non-default theme (including custom) paints the table of contents in
  `--color-highlight` with white text; the default theme keeps a light TOC. The generated
  `@custom` sets `--color-highlight-menu: 255,255,255` so the active TOC entry stays
  readable on that accent-colored sidebar.

## Root classes and reader settings

`<html>` gets exactly three classes, replaced wholesale on every settings change
(`connectors/Base/settings.ts`):

```
lia-theme-{default|turquoise|blue|red|yellow|custom}  lia-variant-{light|dark}  lia-font-scale-{1|2|3}
```

Mode and panel state are classes on `.lia-canvas`, not on `<html>`:
`lia-mode--textbook | lia-mode--presentation | lia-mode--slides`,
`lia-toc--visible | lia-toc--hidden`, `lia-support--visible | lia-support--hidden`.

Reader settings live in `localStorage.settings` (JSON). Relevant keys for previews:
`theme` (`"default"`, `"custom"`, `"red"` …), `light` (bool), `mode`
(`"Textbook" | "Presentation" | "Slides"`), `font_size` (1–3), `editor` (Ace theme name).
Set them, then reload, to screenshot every combination:

```js
// Playwright: page is on the course
await page.evaluate(o => { const s = JSON.parse(localStorage.getItem('settings') || '{}');
  Object.assign(s, o); localStorage.setItem('settings', JSON.stringify(s)); },
  { theme: 'default', light: false, mode: 'Presentation', font_size: 1 });
await page.reload();
await page.waitForSelector('.lia-slide__content');
```

Sections are addressed as `#1`, `#2`, … in the URL. The content of a section scrolls
inside the slide, so prefer a tall viewport over `fullPage` screenshots.

## Specificity and order — what wins (tested)

| Rule | Specificity | Beats |
|---|---|---|
| LiaScript `:root { --color-* }` | 0,1,0 | — |
| `@style` `:root { --color-* }` | 0,1,0, later | base values in light/default |
| LiaScript `:root.lia-variant-dark`, `:root.lia-theme-red` | 0,2,0 | a plain `:root {}` from `@style` or `custom:` |
| `@style` `:root.lia-variant-dark { … }` | 0,2,0, later | LiaScript's dark values |
| `@style` `:root:is(.lia-theme-default,.lia-theme-custom).lia-variant-dark` | 0,3,0 | everything above |
| LiaScript `.h1, .h2, .h3 { font-family }` (every section title carries `.h1`) | 0,1,0 | a bare `h1 { }` / `h3 { }` → target `.h1` |
| LiaScript `html.lia-variant-dark .lia-link { color: rgb(from …) }` | 0,2,1 | plain `.lia-link` rules in dark mode |

## Dark mode quirks

LiaScript never changes `--color-highlight` in dark mode. Instead ten rules recompute a
lighter color with relative color syntax, e.g.
`color: rgb(from rgb(var(--color-highlight)) calc(r * 2.5) calc(g * 2.5) calc(b * 2.5))`:

```
html.lia-variant-dark .lia-btn--outline           (×2.2 border, ×2.5 text)
html.lia-variant-dark .lia-code--inline           (×2.2 / ×2.5)
html.lia-variant-dark .lia-link                   (×2.2 / ×2.5)
html.lia-variant-dark summary, summary:after      (×2.5 / ×2.2)
html.lia-variant-dark .lia-label                  (×1.8)  – quiz option labels
html.lia-variant-dark .lia-support-menu__item     (×1.8)  – header icons
html.lia-variant-dark .lia-canvas .lia-skip-nav   (×2.5)
html.lia-variant-dark .lia-list--*> li::marker    (×2.5 of highlight-dark)
html.lia-variant-dark .lia-quote__text            (×4.8 of highlight-dark)
```

plus `filter: brightness(1.8) contrast(1.1)` on `.lia-btn--transparent` and `.lia-input`.
Multiplying RGB turns most hand-picked accents into pastel or yellow (orange `214,88,33`
×2.5 → `255,220,82`). `templates/adapter.css` overrides all of these for the course theme
with `--color-highlight-dark` (the "accent as text" color), scoped to
`.lia-theme-default/.lia-theme-custom` so the built-in themes keep their behavior.

Other dark-mode surfaces use palette variables directly: notes/TTS bar
`--lia-anthracite`, settings submenu `--lia-grey-dark`, alternating table rows
`rgba(var(--lia-grey), .3)`. The generated block redefines `--lia-grey-dark` and
`--lia-anthracite` inside `:root.lia-variant-dark` (and `--lia-grey-lighter/-light` in
light mode) so these surfaces take the theme's tint.

## Previewing a local course

LiaScript loads a course from any URL that allows CORS:

```bash
python3 scripts/serve.py path/to/course             # prints https://liascript.github.io/course/?http://localhost:8000/README.md
python3 scripts/serve.py path/to/course --app dist  # local LiaScript build at /, course at /course/
```

Chrome may hold a request from the public liascript.github.io page to `localhost` until
the user allows "local network access"; the page then sits at "Loading". Allow it (in
Playwright: `context.grantPermissions(['local-network-access'], {origin: 'https://liascript.github.io'})`
and load again), or use `--app` with a local build, or the LiaScript devserver
(`npm install -g @liascript/devserver`, then `liascript-devserver -l -o`; see liascript-syntax
`reference/tooling.md`).
