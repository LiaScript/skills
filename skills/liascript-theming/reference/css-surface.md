# LiaScript's CSS surface (2.x)

Reference for writing selectors in `extra_css`. Paths are in the LiaScript repo under
`src/scss/` (ITCSS layers `00_settings` … `06_utilities`). `1rem = 10px`.

## CSS custom properties

Defined on `:root` in `03_elements/_elements.page.scss`.

| Variable | Default | Format | Drives |
|---|---|---|---|
| `--color-background` | `--lia-white` · dark `--lia-grey-dark` | RGB triple | page, header, TOC, cards, tables, outline buttons (18 uses) |
| `--color-text` | `--lia-anthracite` · dark `--lia-white` | RGB triple | body text, cards, submenu, default focus ring (10) |
| `--color-border` | `--lia-grey-light` · dark `--lia-anthracite` | RGB triple | every `1px solid` border: header, TOC, tables, details, hr, kbd (13 + global border) |
| `--color-highlight` | `--lia-turquoise` (20,115,117); per theme turquoise/red/blue/yellow | RGB triple | **92 uses**: links, buttons, checkbox/radio, range, pagination, active TOC, quiz icons, code frame, effect circles, progress, quote/summary tint, `.bg-/.text-/.border-highlight` |
| `--color-highlight-dark` | `--lia-turquoise-dark` | RGB triple | link hover, list markers, inline code, terminal gradient, summary text, quote text, kbd border |
| `--color-highlight-menu` | accent; `--lia-white` in named themes | RGB triple | active TOC entry on the colored (non-default) TOC only |
| `--lia-<name>` ×21 | see palette | RGB triple | used *directly* by many components (below) |
| `--global-font-family` | `'LiaSourceSansPro'` | full value | body, button, input, select, textarea |
| `--global-font-mono` | `'LiaSourceCodePro'` | full value | only `kbd` |
| `--global-font-headline` | `'LiaSourceSerifPro'` | full value | **unused** |
| `--global-font-size` | `1.5rem` | length | body, Ace editor (headings do *not* scale with it) |
| `--font-size-multiplier` | 1 · 1.25 · 1.5 (`lia-font-scale-2/3`) | number | body, h1–h6, TOC, Ace |
| `--max-editor-line-count` | 16 | number | code editor height |
| `--focus-ring-width/-color/-offset/-style/-radius` | 3px / `rgb(var(--color-text))` / 2px / solid / .8rem | full values | `:focus-visible` |
| `--flow-space` | 1em | length | `.flow > * + *` spacing (settings submenu) |

Palette (`00_settings/_settings.colors.scss`, all RGB triples): anthracite 75,75,75 ·
grey-dark 50,50,50 · grey 174,174,174 · grey-light 240,240,240 · grey-lighter 249,249,249 ·
white · black · turquoise 20,115,117 (+ -dark 16,116,117, -darker) · blue 10,100,136 (+ -dark,
-darker) · red 191,44,26 (+ -dark, -darker) · yellow 134,95,7 (+ -dark, -darker) ·
success 140,201,111 · warning 244,195,67. Utilities `.bg-<name>`, `.text-<name>`,
`.border-<name>` exist for each.

Direct palette uses worth knowing (they ignore the semantic variables):

| Palette var | Where |
|---|---|
| `--lia-white` | button labels, pagination text, checkmark, effect circle digits, colored-TOC text, accordion header |
| `--lia-grey-lighter` | alternating table rows (light) |
| `--lia-grey-light` | notes, TTS bar, TOC separators, `.lia-select` border, disabled buttons, script refresh |
| `--lia-grey` | disabled borders/text, notes counter, dark alternating rows (`.3`) |
| `--lia-anthracite` | dark notes/TTS bar, card subtitle, script output background |
| `--lia-grey-dark` | dark background, dark settings submenu, modal |
| `--lia-black` | code terminal background |
| `--lia-red/yellow/success` | quiz/button status (`--failure`, `--warning`, `--success`) |

## Root and mode classes

- `<html>`: `lia-theme-{default|turquoise|blue|red|yellow|custom}`,
  `lia-variant-{light|dark}`, `lia-font-scale-{1|2|3}`; plus `lang`, `dir="rtl"`.
- `.lia-canvas`: `lia-mode--{textbook|presentation|slides}`, `lia-toc--{visible|hidden}`,
  `lia-support--{visible|hidden}`.
- `html:not([class*='lia-theme-default'])` = any named or custom theme → accent-colored TOC.

## Component classes (selected)

| Area | Classes | Hard-coded values worth overriding |
|---|---|---|
| Shell | `.lia-canvas`, `.lia-header`, `.lia-toc`, `.lia-toc__search`, `.lia-toc__content`, `.lia-toc__link--is-lvl-1…6`, `.lia-active`, `.lia-support-menu`, `.lia-support-menu__item`, `.lia-support-menu__submenu` | header height 5.6/7.8rem; TOC width 28.5rem; submenu shadow `0 0 1rem rgba(128,128,128,.2)`, radius .8rem |
| Slide | `.lia-slide`, `.lia-slide__container`, `.lia-slide__content`, `.lia-slide__footer`, `.lia-pagination`, `.lia-pagination__content`, `.lia-notes`, `.lia-responsive-voice`, `.lia-progress` | content max-width 144rem, padding 0 3rem; pagination radius .8rem |
| Title card | `.lia-card`, `__icon`, `__title`, `__subtitle`, `__body`, `__footer`, `__author` | border .4rem accent; author `grey` |
| Section title | `<hN class="h1">` inside `.lia-slide__content` — **every** section title has `.h1`, the tag follows the level | styled like h1 at every level |
| Text | `h1–h6` (+ utility classes `.h1–.h5`), `.lia-paragraph`, `.lia-list--ordered/--unordered`, `.lia-link`, `.lia-divider` (hr), `.lia-code--inline`, `kbd` | headings: h1 4rem (textbook 3.7rem), h2 2.9rem, h3 2.3rem, h4–6 1.6rem; strong = 600; line-height 1.47 |
| Tables | `.lia-table-responsive` (`.has-thead-sticky`, `.has-first-col-sticky`), `.lia-table` (`.is-alternating`, `.is-compact`), `__head`, `__header`, `__row`, `__data` | cell padding 1.3rem 3.2rem 1.3rem 1.6rem |
| Quotes | `.lia-quote`, `__text`, `__cite`, `__alert-note/-tip/-important/-warning/-caution`, `__alert-icon` | background accent 15 %, padding 2.4rem; alert borders are fixed hex (`#0b5ebe`, `#126229`, `#6e44ba`, `#805f1d`, `#ba131e`) |
| Details | `details`, `summary` | radius .8rem, summary weight 600, tint 5 % accent |
| Code | `.lia-code`, `.lia-code--block`, `.lia-code__input` (frame), `.ace_editor`, `.lia-code-control`, `.lia-code-terminal` | frame 1px accent; terminal black; editor colors = reader's Ace theme |
| Forms/quiz | `.lia-btn` (`--outline`, `--transparent`, `--success/-warning/-failure`, `--tag`), `.lia-input`, `.lia-checkbox`, `.lia-radio`, `.lia-select`, `.lia-dropdown`, `.lia-label`, `.lia-quiz`, `.lia-quiz__*`, `.lia-survey-matrix` | radius .8rem; check/radio 2.4rem; radio 100 % |
| Effects | `.lia-effect__circle`, `.lia-effect--inline`, `.lia-effect__playback-*` | circle 2rem, white digits |
| Media | `figure`, `img`, `.lia-gallery > .lia-lightbox > figure.lia-figure > .lia-figure__media > img`, `.lia-lightbox__clickarea`, `.lia-modal` | tile `.lia-figure__media` black `rgba(0,0,0,.85)`, 25rem tiles, `object-fit: cover` |
| Header | `header#lia-toolbar-nav.lia-header > .lia-header__left / __middle (logo img.lia_header__logo) / __right (#lia-support-menu.lia-support-menu)`, `.lia-progress`; the TOC toggle `#lia-btn-toc` lives in `.lia-toc` | header `margin: 0 3rem`; support menu has its own `--color-background`; progress bar = accent |
| Misc | `.lia-tooltip`, `.lia-tooltiptext`, `.lia-dropdown__options` | tooltip `black`/`#fff`, radius 6px |

Elements rendered with a class but **no** LiaScript rule (free hooks):
`lia-chart`, `lia-formula`, `lia-bold`, `lia-italic`, `lia-strike`, `lia-underline`,
`lia-embed`, `lia-cite`, `lia-figure__caption`, `lia-table__body`, `lia-accordion__item`.

## Fonts and sizes

- Built-in fonts: LiaSourceSansPro 400/600/700, LiaSourceSerifPro 600/700 (no 400),
  LiaSourceCodePro 400/600; no italic faces.
- Compiled font literals (not variables) — the adapter overrides all of them:
  `h1,h2,h3,.h1,.h2,.h3` serif; `h4,h5,h6,.h4,.h5,summary,.lia-accordion__headline` sans;
  `.lia-quote__text` serif; `.lia-code` mono; `code,kbd,samp,pre` monospace.
- Icons use the `icon` font on `.icon` — never override that family.
- Breakpoints (min-width): xs 30em, sm 48em, md 64em, lg 90em, xl 105em.

## Radius and shadow inventory (compiled)

| Value | Selectors |
|---|---|
| `.8rem` | `button, .lia-btn, input, .lia-input, select, .lia-select, textarea, .lia-textarea, .lia-dropdown`, `.lia-code-terminal__input`, `details`, `.lia-checkbox`, range track, `.lia-pagination__content`, `.lia-script`, `.lia-support-menu__submenu` |
| `100%` | `.lia-radio[type=radio]` |
| `50%` | `.lia-card__icon`, `.lia-effect__circle` |
| `0` | `.lia-btn--tag`, `.lia-btn--small-tag`, voice controls, script inputs |
| `6px` | `kbd`, `.lia-tooltip .lia-tooltiptext`, `.lia-effect--inline`, classroom cards |
| `.3rem` | active TOC entry in named themes |
| shadows | submenu `0 0 1rem #80808033`; card controls hover `0 0 1rem #0003`; range thumb; none on buttons |
