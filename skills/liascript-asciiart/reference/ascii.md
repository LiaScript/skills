# ASCII shape characters

Every cell is 8 × 16 px. Only the characters below can become shapes, and only
when their neighbours (the 8 surrounding cells) make them part of a drawing.
Everything else is text in `monospace` 14 px. All rules here were verified by
rendering.

## Lines

| Char | Becomes | Condition / note |
|---|---|---|
| `-` | horizontal line through the middle | unless text on both sides (`x-y` stays text). A lone `-` is drawn too: `- item` turns into a dash |
| `_` | horizontal line at the bottom of the cell | joins `|` and `/ \` at the floor: `|___|`, `/____\` |
| `|` | vertical line | unless text on both sides. A lone `|` is drawn |
| `/` `\` | diagonal (about 63°, cells are 1:2) | stays text between two letters (`1/8`, `TCP/IP`), but **not** next to `o v V A . -` or a space: `w/o`, `I/O`, `and/or`, `src/` draw a slash line |
| `~` | dashed horizontal | only if the run touches a line, corner or arrow at one end (`+~~~~>`, `|~~~|`) and no text. `~~strike~~`, `~/path` stay text |
| `:` `!` | dashed vertical | same rule: the run must continue a vertical line, corner or arrow (`+`, `.`, `'`, `|`, `^`, `v`) |
| `=` | double horizontal | same rule: `+=====+`, `+====>`. `a == b`, `x = 1` stay text |
| `||` | double vertical | two `|` columns side by side |
| `- - -` | dashed look | each lone `-` draws a short stroke. An arrowhead needs a `-` directly before it: `- - -->` |

Dashed and double lines need elm-svgbob 5.0.8 (LiaScript after 2.1.2); up to 2.1.2 these characters stay text. There is no vertical form of `=` and no diagonal dashes. A `+` inside a `=`
run breaks the double line into a short single stroke; branch off a double line
with `|` or `!` directly below (or above) a `=` cell instead. A vertical `||`
splits boxes it touches, so run double-line paths horizontally.

## Corners and junctions

| Char | Becomes | Note |
|---|---|---|
| `+` | sharp corner / junction | connects to every neighbouring line, including diagonals. Inner lines need a `+` where they meet a border, otherwise a gap stays |
| `.` `,` | rounded corner opening downwards | `.--`, `--.`, `.-.` |
| `'` `` ` `` `´` | rounded corner opening upwards | `'--'`, `` `--´ `` |
| `(` `)` | arc | only next to `.`/`'` corners or slants: a circle is `.-.` / `( x )` / `'-'`, a stadium is `.----.` / `( ok )` / `'----'`. `(` sits **one column left** of the `.` above it |

Rows of `.` or `'` (dot leaders `.....`, `|  ...  |`) join into a solid line.

Brackets and letters count as text, so `[_]`, `[o]`, `[x]`, `( )` buttons and
checkboxes stay text as long as they do not touch a line.

## Arrowheads and end markers

| Char | Becomes | Condition |
|---|---|---|
| `>` `<` | filled triangle | the line is on the side it points away from: `-->`, `<--`, also after a corner `.->`. `x > y`, `<5k>`, `a<b>c` stay text |
| `^` `A` | up triangle | `|` directly below, or a slant below-left/right |
| `v` `V` | down triangle | `|` directly above (not `+`! write `+`, `|`, `v` on three rows), or a slant above |
| `o` `O` | hollow circle | touches a line and has no letter beside it |
| `*` | filled circle | same |
| `#` | filled square | same; vertically stacked `#` form one bar (`##` bar charts) |

Vertical arrowheads (`v`, `^`) end about half a cell before a border, more
than horizontal ones; that is how the grid works, there is no fix.

Double heads `->>-` work only in the middle of a line; a trailing `-->>` draws
one head and a `>` character.

## Text traps (all verified)

| You write | You get | Write instead |
|---|---|---|
| node `A` above `|` or `/` (`A---B` with a branch below) | `A` becomes an up arrow | another name, or move it off the line column |
| `Volvo`, `foo->`, a `v` or `o` beside a line char | circle / arrowhead inside the word | rename, add a space, or use a different glyph |
| `x >= y`, `a => b`, `<-`, `==>` inside labels | triangles and double lines | Unicode `≥ ⇒ ← ⟹` |
| `- name: String` (UML visibility), `-name` | a dash line | `– name` (en dash U+2013) |
| `...` or `....` | a line | `…` (U+2026) |
| `src/`, `I/O`, `w/o` | a slash stroke | `src`, `I∕O` (U+2215 division slash) |
| `"cat"` | starts a verbatim block in LiaScript | `'cat'`, `“cat”` |
| tab characters | one cell each, misaligned | spaces only |
| `login():` with `:` above/below a `+` or `|` | `:` becomes a dashed line | keep one row between the text and the border, or move the `:` |

## Shapes that work

- Box: `+--+` / `|  |` / `+--+`; rounded `.--.` / `'--'`; mixed corners allowed.
- Stadium / terminal: `.-----.` / `( start )` / `'-----'`.
- Decision diamond: `+` at all four vertices with `/ \` sides (see `patterns.md`).
- Hexagon: `____` / `/    \` / `\____/`.
- Triangle: `/\` / `/  \` / `/____\`.
- Hollow inheritance arrowhead (UML), under a box border `+----+----+`:

  ```
            / \
           +-+-+
             |
  ```
- Database cylinder:

  ```
   .----.
  (      )
  |'----'|
  |  DB  |
  '------'
  ```

## Not available (Rust svgbob features)

Large circle art, `{class}` tags with a `# Legend:` CSS block, `X` crossings,
Unicode box drawing turned into vector lines, and `\"` escapes do **not** exist
in elm-svgbob. Style through the LiaScript parameters instead (`liascript.md`).
