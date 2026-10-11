# Unicode: box drawing, blocks, symbols, emoji, CJK

Every non-ASCII character is drawn as a **text glyph** from the browser's
`monospace` font, placed at its own grid cell. Nothing connects to the SVG
strokes, and text glyphs use the **text color** (`#4b4b4b` light, `white`
dark), not the stroke color (`black` / `#ddd`, or whatever `stroke` sets).

## Cell width

svgbob gives a grapheme **2 cells** if its first character is East Asian Wide
or Fullwidth, or if it contains U+FE0F; otherwise **1 cell**.

| Characters | Cells | Note |
|---|---|---|
| ASCII, Latin, Greek, accents (`é ñ ß α θ Σ`) | 1 | combining accents stay in their cell |
| box drawing `─│┌╔═╭╱`, blocks `░▒▓█▀▄■`, arrows `←→⇒`, math `≤≥≠∞∑√` | 1 | |
| CJK `中文`, fullwidth `ｆｕｌｌ` | 2 | |
| emoji `😀 🚀 ✅ ⭐ ⚡ ❌`, skin tones `👍🏽`, ZWJ `👨‍💻` | 2 | |
| text-default emoji with U+FE0F `❤️ ⚠️ ⚙️ ☁️ ✔️ ☑️ 🗄️ 🖥️` | 2 | |
| text-default emoji **without** U+FE0F `❤ ⚠ ⚙ ☁ ✔ ☑ ☎ ♥ ↕ ⤴` | 1 | the browser may still draw them ~2 wide from an emoji font → they overlap the next cell. Add U+FE0F or a space after |
| flags `🇩🇪` | 1 | drawn 2 wide → put a space after |

In a closed box, each 2-cell grapheme needs one space less on its row. Run
`scripts/check.py` – it prints the cell width of every row and flags the
characters above.

## Symbols that render cleanly as 1 cell

`■ □ ▪ ▫ ▲ △ ▼ ▽ ◆ ◇ ○ ● ◎ ◉ ★ ☆ ✓ ✗ • ‣ … · ° ± × ÷`
`← ↑ → ↓ ↔ ⇐ ⇒ ⇔ ⟵ ⟶ ➔ ➜ ➤ ↩ ↪ ↺ ↻`
`≤ ≥ ≠ ≈ ∞ ∑ ∏ √ ∫ ∂ ∆ ∇ ∈ ∉ ⊂ ⊆ ∪ ∩ ∧ ∨ ¬ ∀ ∃`, Greek letters, `① ② ③`,
`▁▂▃▄▅▆▇█`, `░ ▒ ▓`, `▏▎▍▌▋▊▉`, Braille `⣿⣶⣤⣀`.

Use them for **labels and marks**: `✓`/`✗` in tables, `→ ⇒ ≥` inside text
(the ASCII digraphs `-> => >=` would turn into shapes), `◆` milestones,
`▲▼` scroll arrows, `★` ratings.

## Box drawing: when to use it

Box drawing (`┌─┐│└┘├┤┬┴┼`, double `╔═╗║`, heavy `┏━┓┃`, rounded `╭╮╰╯`,
dashed `┄┆`) gives a crisp **terminal / UI look** and joins seamlessly in good
monospace fonts (JetBrains Mono, DejaVu Sans Mono). Limits, all verified:

- Font-dependent. In Courier-like fonts (Windows default) vertical runs show
  faint seams and rounded corners `╭╮╰╯` fall back to another font.
- `╱ ╲ ╳` diagonals leave gaps between rows; use ASCII `/ \` for diagonals.
- Never join ASCII strokes and box drawing in one outline (`+-----+────┐`):
  the joint breaks and the colors differ. An ASCII arrow may **point at** a
  box-drawing box (`├------>│`).
- Box-drawing lines do not follow the `stroke` parameter (they are text). For a
  colored or thicker outline use ASCII.
- Double lines in an ASCII drawing: `=` horizontally, `||` (two columns)
  vertically. `═ ║` only inside box-drawing figures.

Rule of thumb: **ASCII** for diagrams (flowcharts, architecture, circuits,
anything with arrows or diagonals, anything that gets `stroke` styling).
**Box drawing** for UI mockups, windows, menus, tables, tree listings
(`├── └──`) and terminal-style figures. Do not mix them in one outline.

## Blocks and shading

- `░ ▒ ▓` shading and shadows: `┐▒` at the right edge plus a row of `▒` below.
- `█ ▇ #` rows touch vertically and melt into one block: good for **vertical**
  bars, bad for horizontal bars in adjacent rows. Horizontal bars in adjacent
  rows: `■■■■■` or `▄▄▄▄▄` (they keep a gap). Sparklines: `▁▂▃▅▇█▇▅▃`.

## Emoji

Emoji are good icons in architecture and sequence diagrams (`🌐 Browser`,
`🗄️ DB`, `😎 Bob`). They render in color (also in dark mode), take 2 cells,
and arrows can touch them (`😎-->🚀`). Prefer emoji that are Wide by default
(`🔐 📦 🚀 ✅ ❌ ⚡ 🌐`), or add U+FE0F to text-default ones (`⚙️ 🗄️ 🖥️ ☁️`).
Avoid flags next to other content.
