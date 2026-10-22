# Styling mechanisms in LiaScript

Everything here was verified by rendering with the LiaScript 2.x interpreter (local build and
liascript.github.io, 2026-09; 2.3/2.4 changes checked against the source and liascript.github.io, 2026-10). Source references point into the LiaScript repo
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

`<html>` gets three classes, plus a fourth when the reader turns on "do not rely on color
alone" (since LiaScript 2.3.0), replaced wholesale on every settings change
(`connectors/Base/settings.ts`):

```
lia-theme-{default|turquoise|blue|red|yellow|custom}  lia-variant-{light|dark}  lia-font-scale-{1|2|3}  [lia-decals]
```

`lia-decals` adds patterns to charts and marks quiz states by border style (correct solid
2px, wrong dashed 2px, a dashed outline around checked wrong boxes). Since 2.3.0 `<html>`
also carries the attribute `data-mouse-focus` after a mouse click (the focus ring of
`.lia-input` then stays hidden) — an attribute, because the class list is overwritten.

Mode and panel state are classes on `.lia-canvas`, not on `<html>`:
`lia-mode--textbook | lia-mode--presentation | lia-mode--slides`,
`lia-toc--visible | lia-toc--hidden`, `lia-support--visible | lia-support--hidden`, and
since 2.3.1 `lia-navigation--visible | lia-navigation--hidden` ("Hide navigation" in the
mode menu; not stored, every load starts visible). With hidden navigation the header is a
narrow column top right and the TOC, prev/next and sound buttons float over the content;
`build_theme.py` scopes `layout.header: accent` with
`:where(.lia-canvas:not(.lia-navigation--hidden))`, which also matches older versions
that have no such class.

Reader settings live in `localStorage.settings` (JSON). Relevant keys for previews:
`theme` (`"default"`, `"custom"`, `"red"` …), `light` (bool), `mode`
(`"Textbook" | "Presentation" | "Slides"`), `font_size` (1–3), `editor` (Ace theme name),
`decals` (bool, 2.3.0+). Set them, then reload, to screenshot every combination:

```js
// Playwright: page is on the course
await page.evaluate(o => { const s = JSON.parse(localStorage.getItem('settings') || '{}');
  Object.assign(s, o); localStorage.setItem('settings', JSON.stringify(s)); },
  { theme: 'default', light: false, mode: 'Presentation', font_size: 1 });
await page.reload();
await page.waitForSelector('.lia-slide__content');
```

If the app writes its own settings back before yours are read, click the buttons
instead, from a script (`el.click()` — they sit in closed menus): `#lia-btn-light-mode`,
`#lia-mode-textbook/-presentation/-slides`, the "Hide navigation" button in the mode menu,
`#lia-btn-toc`.

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
| LiaScript `:root.lia-variant-dark { --color-accent: rgb(from …) }` (2.3.0+) | 0,2,0 | a plain `:root {}`; loses to the generated 0,3,0 block |
| LiaScript `html.lia-variant-dark .lia-btn--outline { color: rgb(from …) }` (and the other multiplied rules) | 0,2,1 | plain `.lia-btn--outline` rules in dark mode |

## Dark mode quirks

LiaScript never changes `--color-highlight` in dark mode. Instead it computes a lighter
color with relative color syntax, e.g.
`rgb(from rgb(var(--color-highlight)) calc(r * 2.5) calc(g * 2.5) calc(b * 2.5))`.

Since LiaScript 2.3.0 most of it is one variable on `:root.lia-variant-dark`:
`--color-accent` = highlight ×2.5 (inside `@supports`; older browsers keep the plain
highlight). It colors links (also on hover), inline code text, the active TOC entry and its
bar, the borders of checkboxes, radios, selects, dropdowns and quiz inputs, TTS buttons and
the pressed support-menu button. `.lia-notes` and `.lia-responsive-voice` set their own
`--color-accent` in dark mode, lifted towards white for the anthracite surface. The
generated block sets `--color-accent` to the theme's dark `accent_text` (0,3,0 beats
LiaScript's 0,2,0) and, for notes and TTS bar, to `accent_text` checked against
`surface_strong` (≥ 3:1). In light mode it is the accent, or `accent_text` when the accent
is below 4.5:1 on the background.

Still multiplied in 2.4.0 (and all of these up to 2.2.2):

```
html.lia-variant-dark .lia-btn--outline           (×2.2 border, ×2.5 text)
html.lia-variant-dark .lia-code--inline           (×2.2 border; text ×2.5 up to 2.2.2, now --color-accent)
html.lia-variant-dark .lia-link                   (×2.2 border; text ×2.5 up to 2.2.2, now --color-accent)
html.lia-variant-dark summary, summary:after      (×2.5 / ×2.2)
html.lia-variant-dark .lia-label                  (×1.8)  – quiz option labels
html.lia-variant-dark .lia-support-menu__item     (×1.8)  – header icons
html.lia-variant-dark .lia-canvas .lia-skip-nav   (×2.5)
html.lia-variant-dark .lia-list--*> li::marker    (×2.5 of highlight-dark)
html.lia-variant-dark .lia-quote__text            (×4.8 of highlight-dark)
```

plus `filter: brightness(1.8) contrast(1.1)` on `.lia-btn--transparent` (and on
`.lia-input` up to 2.2.2). Multiplying RGB turns most hand-picked accents into pastel or
yellow (orange `214,88,33` ×2.5 → `255,220,82`). `templates/adapter.css` overrides all of
these for the course theme with `--color-highlight-dark` (the "accent as text" color),
scoped to `.lia-theme-default/.lia-theme-custom` so the built-in themes keep their
behavior. The adapter rules that only matter up to 2.2.2 are marked in its comments.

Other dark-mode surfaces use palette variables directly: notes/TTS bar
`--lia-anthracite`, settings submenu `--lia-grey-dark`, alternating table rows
`rgba(var(--lia-grey), .15)` (`.3` up to 2.2.2). The generated block redefines `--lia-grey-dark` and
`--lia-anthracite` inside `:root.lia-variant-dark` (and `--lia-grey-lighter/-light` in
light mode) so these surfaces take the theme's tint.

Quiz states (since 2.3.0) use `--color-success` / `--color-failure` (light 63,122,42 /
191,44,26; dark 140,201,111 / 255,135,120). `build_theme.py` keeps them and emits a
darker (light) or lighter (dark) value only where they fall below 4.5:1 on the theme's
background.

LiaScript forces `animation-duration` and `transition-duration` to `0.01ms !important` on
every element under `prefers-reduced-motion: reduce` since 2.3.0 (and turns off smooth
scrolling); the skill's own `no-preference` guard stays as a second layer.

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
