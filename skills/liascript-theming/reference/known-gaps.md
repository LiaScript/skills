# Known gaps in LiaScript theming (2.x) and how the skill works around them

Found while building and testing this skill (2026-09). Each entry: symptom → workaround
used here → suggested fix in the interpreter (`github.com/LiaScript/LiaScript`).

| # | Gap | Workaround in this skill | Suggested core fix |
|---|---|---|---|
| 1 | `custom:` is never active unless the reader clicks the extra swatch; no header key selects a theme. | Put the design into `@style`; `@custom` only offers a variant. | Add `theme: custom\|red\|…` header key, or auto-select `custom` when a course defines it and the reader has not chosen explicitly. |
| 2 | The custom swatch's title is "Default" (`Trans.cDefault`) — two swatches named "Default". | Mention it to users. | Own translation string, e.g. "Course theme". |
| 3 | `custom:` is wrapped as `:root {…}` (0,1,0) and loses to `:root.lia-variant-dark` / `:root.lia-theme-*`; it cannot style dark mode or components. | `@style` with scoped selectors. | Inject custom as its own layer with higher specificity, or accept full CSS. |
| 4 | Heading, code, quote, summary and accordion fonts are compiled literals; `--global-font-headline` is defined but unused; `--global-font-mono` only styles `kbd`. | Adapter sets them with explicit selectors. | Use `var(--global-font-headline)` / `var(--global-font-mono)` in those rules. |
| 5 | `font:` appends the font as a *fallback* — it never replaces LiaScript's fonts. | Fonts via `link:` + tokens. | Prepend instead of append, or document as fallback-only. |
| 6 | Radius (`$global-radius`), border width, spacing, shadows, line-height are SCSS constants. | Adapter re-declares them with `--theme-radius*`/`--theme-shadow`. | Expose `--global-radius`, `--global-border-width`, `--global-shadow`, `--global-line-height`. |
| 7 | Dark mode brightens the accent with `rgb(from … calc(r*2.5))` in ten rules (and `filter: brightness(1.8)`): hand-picked accents turn pastel/yellow; there is no variable for a dark accent. | Adapter maps text-like uses to `--color-highlight-dark` for the course theme. | Introduce `--color-highlight-text` (and dark overrides of `--color-highlight*`) instead of multiplication. |
| 8 | Button, pagination, checkmark and colored-TOC labels are `--lia-white`/`white` — no "on-accent" color, so light brand colors cannot be accents. | Auto-darken the accent; original becomes decoration. | `--color-on-highlight` variable. |
| 9 | Components use palette greys directly (`--lia-grey-light` for notes, TTS, separators; `--lia-anthracite`/`--lia-grey-dark` in dark). | Redefine those palette variables per variant. | Semantic `--color-surface` / `--color-surface-strong`. |
| 10 | Alert quotes (`> [!NOTE]` …) use fixed hex colors; quiz/survey feedback `.text-error` is `#f00`; tooltips are `black/#fff`. | Left as is (they are semantic). | Variables `--color-note/-tip/-warning/…`, `--color-error`. |
| 11 | The code editor's colors come from the reader's Ace theme setting, not from light/dark mode. | None (reader setting). | Optional: follow dark mode by default. |
| 12 | Headings carry `.h1…` classes whose utility rules outrank element selectors — `h1 {}` in `@style` silently loses. | Adapter targets both. | Drop the classes from rendered headings or lower utility specificity. |
| 13 | `.lia-modal` sets `--color-text: white` (a keyword, not a triple) → `rgb(var(--color-text))` is invalid inside modals. | Not touched. | Use `var(--lia-white)`. |
| 14 | `Settings.updateClassName` replaces the whole `<html>` class list, wiping classes set by others (e.g. Google Translate). | — | Toggle only LiaScript's own classes. |
| 15 | Charts (ECharts) take no colors from the theme. | — | Pass `--color-highlight`/palette to the chart options. |
| 16 | `.lia-radio.is-red` uses `--lia-turquoise` (`_elements.input.scss`); `.max-w-50` is defined twice (25 %, then 50 %, `_utilities.width.scss`); `_utilities.disabled.scss` is not imported. | — | Small SCSS fixes. |
| 17 | A block macro with `@end` on the line right after its opening (`@style` ⏎ `@end`) makes the whole header be dropped silently (author, language, macros, links). | Never emit empty blocks; showcase has none. | Accept empty blocks, or report a parse error instead of falling back to defaults. |
| 18 | Relative `url()` in `@style` and in `link:`ed stylesheets (inlined as `blob:`) resolve against the LiaScript app, not the course — local textures, fonts and images 404. | `url('embed:…')` → data URI via `build_theme.py`; absolute URLs. | Rewrite relative `url()`s against the course base when injecting `@style` / link blobs. |
| 19 | Gallery tiles (`.lia-figure__media`) have a hard-coded black `rgba(0,0,0,.85)` backdrop; blend modes and rounded/clipped images show it. | Recipe sets it transparent. | Use `--color-background` or transparent. |
| 20 | All section titles carry class `.h1` regardless of level, and the `.h1` utility outranks `h2`…`h6` rules — per-level styling needs `hN.h1`. | Documented; recipes use `.h1`. | Emit `.h<level>` or a dedicated `.lia-section-title` class. |
