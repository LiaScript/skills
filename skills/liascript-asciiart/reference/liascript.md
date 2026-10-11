# ASCII art in LiaScript

## Block syntax

````markdown
{{1}}
<!-- style="max-width: 480px; display: block; margin: auto" class="my-fig" -->
``` ascii   Fig. 3: Caption with **Markdown** and $x^2$
+-----+     +-----+
| foo |---->| bar |
+-----+     +-----+
```
````

- Fence: ` ``` ascii ` or ` ``` art` (any case). With 9 or more backticks the
  tag is optional. Use a 4-backtick fence if a verbatim part contains ` ``` `.
- Text after the tag on the fence line is the **caption**: one line of inline
  LiaScript (bold, links, math), shown below the figure.
- The `<!-- … -->` comment directly above the fence holds HTML attributes for
  the `<svg>`. No blank line between comment and fence.
- `{{n}}` on the line before (above the comment) reveals the whole figure at
  animation step n.
- Do not indent the fence by 4 spaces (that makes an ordinary code block).

LiaScript fixes the svgbob settings: 8 × 16 px cells, font 14 px, line width
1, arc radius 4, verbatim `"` with multi-line blocks. Colors follow the theme:
light = stroke `black`, text `#4b4b4b`, background `white`; dark = stroke
`#ddd`, text `white`, background `#323232`.

## Parameters (verified in LiaScript)

Each `key="value"` in the comment becomes an attribute of the `<svg>`. svgbob
itself sets `style="background-color:…; fill:…"`, `stroke`, `stroke-width` and
`fill` on that element; a parameter with the same name **replaces** it.

| Parameter | Effect |
|---|---|
| *(none)* | the svg is **as wide as the content column** (≈ 870 px on desktop). A 30-column drawing is scaled up about 3.5×, strokes and text included. Almost always set a width |
| `style="max-width: 400px"` | caps the size, keeps it responsive. Good value: columns × 8 × 1.1 … 1.5 px |
| `style="display: block; margin: auto"` | centers the figure (combine with `max-width`/`width`) |
| `style="width: 50%"` | relative width |
| `width="300"` | fixed width in px |
| `style="…"` (any) | **replaces svgbob's own style**: the background becomes transparent (the page shows through, fine in both themes) and the default `fill` goes back to the `fill` attribute |
| `style="stroke: red"` / `stroke="red"` | color of all lines and arrowheads' outlines |
| `style="stroke-width: 2"` / `stroke-width="2"` | line thickness (also scaled with the figure) |
| `style="fill: blue"` | arrowheads, `*` dots, `#` squares. Text keeps its color, `o` circles stay hollow |
| `fill="blue"` alone | no effect (svgbob's style wins); works only together with any `style` |
| `style="background: #fffbe6"` | background color |
| `style="color: blue; font-…"` | colors / fonts only the **verbatim** HTML (it inherits CSS). Grid text keeps its own font and color |
| `font-size`, `font-family`, `color` as attributes | no effect |
| `class="name"` | hook for CSS from the course header (below) |
| `id="name"` | anchor / CSS hook |

Fixed colors (`stroke: red`) ignore the theme. Pick colors readable on both
white and `#323232`, or keep the defaults.

### Styling text and details with `@style`

Text, arrowheads and dots can be styled per class from the main header
comment of the course:

```markdown
<!--
@style
svg.blue-text text   { fill: royalblue; font-weight: bold; }
svg.accent polygon,
svg.accent circle    { fill: crimson; }     /* arrowheads and dots (also o!) */
svg.thin line,
svg.thin path        { stroke-width: 0.5; }
@end
-->
```

Then `<!-- class="blue-text accent" style="max-width: 400px" -->` above the
fence. Element types: `line` (straight strokes), `path` (curves), `polygon`
(arrowheads), `circle` (`o` `*`), `rect` (`#`), `text`, `foreignObject`
(verbatim). Box-drawing and other Unicode glyphs are `text`.

## Verbatim: LiaScript inside the drawing

Text between double quotes is parsed as **LiaScript Markdown** and laid over
the drawing as HTML (`foreignObject`): math, links, bold, quizzes, animations,
images via macros, even code blocks.

- **One-liner**: `"…"` on one row. Width = the cells between the quotes.
- **Block**: quotes in consecutive rows **starting in the same column** merge
  into one Markdown block, positioned at the first row. Width = the widest row.
- Height is not limited to the quoted rows: the content flows **down to the
  bottom of the drawing** and is clipped there. Leave empty rows below for
  tall content (images, display math, lists).
- The quote characters and every character inside take cells like normal text.
  The **source** length counts: `"$\frac{n(n+1)}{2}$"` needs 20 cells even
  though the rendered math is narrower. Keep each quoted row inside its box.
- Any `"` in the drawing starts verbatim. For a literal quote use `“ ”` or `'`.
- The HTML uses the page font, not monospace, and is placed less precisely
  than grid text; render and adjust.
- Quoting also protects a label from shape detection (`"A"`, `"w/o"`), but
  costs the monospace look. Prefer renaming or Unicode (`ascii.md`, text
  traps); quote only where Markdown is needed.
- Never quote single labels on consecutive rows in the same column (`| "0" |`
  directly above `| "1" |`): they merge into one block.

Examples:

````markdown
<!--
@img: <img src="pic.png" style="width:100%">
-->
``` ascii
+-------------------+      +----------------+
| "$E = mc^2$"      |----->| "**bold** _it_"|
+-------------------+      +----------------+
.--------------------------.
|"* first point           "|
|"* second, $O(1)$        "|
|"                        "|
'--------------------------'
+----------------------+
| "@img              " |
|                      |
|                      |
+----------------------+
```
````

- **Quizzes**: `" [[ 4 ]] "` – keep a space before `[[`, otherwise LiaScript
  makes it a single text quiz. All gaps in one drawing form one quiz; the Check
  button appears below the figure. Selections `" [[ (lens) | disc ]] "` work.
- **Animations**: inline `"{1}{appears at step 1}"`; in a block, `{{2}}` on its
  own quoted row. Narration: `<!-- --{{1}}-- text -->` after the block.
- **Long content** (image URLs, long formulas) goes into a macro so the quoted
  area stays short: define `@img: …` in the header, write `"@img   "`.
- Prefer inline `$…$` (with `\displaystyle` if needed) over `$$…$$` blocks.

## Related

ASCII line plots written **without** a fence (an `|` y-axis, `+----` x-axis,
`*` points) become ECharts charts, not svgbob drawings. Keep diagrams inside
` ```ascii `.
