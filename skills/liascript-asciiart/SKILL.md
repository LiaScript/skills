---
name: liascript-asciiart
description: >
  Use when drawing, editing, reviewing or debugging ASCII-art, box-drawing or
  Unicode/emoji diagrams rendered to SVG by elm-svgbob / svgbob, especially
  LiaScript ```ascii or ```art blocks (flowcharts, architecture, sequence,
  state machines, data structures, circuits, timing, git graphs, UI mockups,
  tables, charts), choosing their <!-- style / class / stroke --> parameters,
  or embedding "…" verbatim Markdown, math, quizzes or images in them.
  German - ASCII-Art, Box-Drawing, Rahmenzeichen, Flussdiagramm, Diagramm oder
  Skizze in LiaScript. Not for Mermaid, PlantUML or ASCII art that stays an
  unrendered code block.
license: CC0-1.0
---

# elm-svgbob diagrams (LiaScript ```ascii)

## Core model

The drawing is a grid of **8 × 16 px cells**. A handful of ASCII characters
(`- _ | / \ + . , ' ( ) < > ^ v V A o O * # ~ : ! =`) become SVG strokes,
corners, arrowheads and dots, **depending on their 8 neighbours**. Every other
character, including all box drawing, symbols and emoji, is drawn as a font
glyph in its cell. So the same character is a line in one place and text in
another, and letters next to lines can turn into shapes.

## Workflow

1. Pick the means per element (table below) and a template from
   `reference/patterns.md`.
2. Write the block (syntax and parameters: `reference/liascript.md`).
3. Check the grid: `python3 scripts/check.py FILE.md`
   – prints the cell count per row; rows that share a right border must have
   the same count. Also flags emoji/flag widths, tabs and dot leaders.
   FILE.md can be the course or a scratch file with just the block (a file
   without a fence counts as one drawing).
4. Render and **look at the PNG**:
   `python3 scripts/render.py FILE.md OUT.png [--dark]`
   The script reproduces LiaScript's settings, theme colors and `<!-- -->`
   parameters, using a local elm-svgbob checkout in `$SVGBOB_SRC` (its
   `src/` folder) if set, otherwise the published package. Paths are relative
   to this skill's directory. Needs `elm` and `chromium` on PATH (Pillow
   optional, for cropping).
   `@style` from the course header is applied. Verbatim parts show as yellow
   placeholders; for their real look use the LiaScript preview
   (`liascript-devserver`). Thin 1 px rules can vanish in small renders: add
   `--no-params --scale 2` to zoom past a `max-width` (this also drops
   `stroke`/`class`/`fill`; check colors in a normal render).
5. Fix what looks wrong and repeat 3–4. Even careful drawings have off-by-one
   borders and letters turned into shapes; only the render shows them.

## Which means for what

| Need | Use | Why |
|---|---|---|
| Boxes, arrows, flow, diagonals, anything colored via `stroke` | ASCII (`reference/ascii.md`) | real vector strokes, font independent |
| Window / menu / table mockup, terminal look, `├──` trees | box drawing `┌─┐│╔═╗` (`reference/unicode.md`) | crisp UI look; text glyphs, never joined to ASCII strokes |
| Shading, shadows, bars | `░▒▓`, vertical bars `##`/`█`, horizontal bars `■`/`▄` | `█` rows melt together |
| Marks and labels | `✓ ✗ ★ ◆ → ⇒ ≥ ≤ … ①` | ASCII `-> => >= ...` in labels turn into shapes |
| Icons | emoji `🌐 🗄️ 🔐 😎` | 2 cells each; add U+FE0F to text-style ones (`⚙️`) |
| Math, links, bold, quiz gaps, images, animations | `"…"` verbatim (`reference/liascript.md`) | LiaScript Markdown overlaid as HTML |

## Quick rules

- Connect lines with `+` where they meet borders or each other; `v` needs `|`
  directly above it (not `+`), `^`/`A` need `|` directly below.
- Rounded: `.--.` / `'--'`; circle `.-.` / `( x )` / `'-'` with `(` one column
  left of `.`; decision diamond with `+` at all four vertices.
- Dashed `~` `:` `!` and double `=` only continue a line (`+~~~>`, `+===+`).
  No `+` inside a `=` run: branch off with `|`/`!` directly below a `=` cell.
  Vertical double line is `||` (it splits boxes it touches; prefer horizontal
  double runs).
- One space between labels and line characters; no `"` except for verbatim.
- Set a width: `<!-- style="max-width: Npx" -->` with N ≈ columns × 8 × 1.1 … 1.5,
  or the width the task asks for (`max-width: 600px`, `width: 600px`); without
  it the figure fills the page width. Any `style` also makes the background
  transparent.
- Colors: lines via `stroke`/`stroke-width`, arrowheads and dots via
  `style="fill: …"`, verbatim Markdown via `style="color: …"`. Grid text
  (labels, box drawing, symbols) only via `class` + `@style` in the course
  header: `svg.x text { fill: … }`. "Blue labels" with both kinds of text
  needs both.

## Common mistakes

| Mistake | Effect | Fix |
|---|---|---|
| Not rendering before delivering | broken borders, stray arrows ship | steps 3–4 |
| Emoji/CJK counted as 1 cell | right border jumps | one space less per wide char, `check.py` |
| `⚙ ❤ ⚠ ☁` without U+FE0F, flags | glyph overlaps next cell | `⚙️`, or a space after |
| Node `A` above `|`, `Volvo`, `foo->` | arrowhead / circle in the label | rename, Unicode, or a space |
| `src/`, `I/O`, `w/o` | slash stroke | `src`, `I∕O` (U+2215) |
| `...`, `- item`, `x >= y`, `a ==> b` | line, dash, triangle, double arrow | `…`, `• item`, `≥`, `⟹` |
| `║`, `═` or `──` for a colored/thick path | stays grey text, ignores `stroke` | ASCII `||`, `=`, `-` |
| Mixing `+---` and `────┐` in one outline | gap and two colors | one family per outline |
| `#`/`█` horizontal bars in adjacent rows | bars merge into a block | `■■■■` or `▄▄▄▄` |
| `$$…$$` or long LaTeX in a narrow quote | overflow, misplacement | inline `$…$`, a macro, room below |
| Quoting every label | page font, loose placement | quote only Markdown; rename trap words |
| `style="font-size…"` / `color` for grid text | no effect | `class` + `@style svg.x text {…}` |

## Reference files

- `reference/ascii.md` – every shape character, its neighbour rules, text traps.
- `reference/unicode.md` – widths, box drawing limits, safe symbols, emoji.
- `reference/liascript.md` – fence, caption, parameter table, `@style`, verbatim.
- `reference/patterns.md` – catalogue of technical drawing types with ratings
  and verified templates.
