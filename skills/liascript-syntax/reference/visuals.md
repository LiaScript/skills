# Visuals

Three independent visualization mechanisms: **table→chart** (a Markdown table auto-rendered as an interactive ECharts diagram), **ASCII-Art** (a text drawing rendered as a real SVG image), and raw **SVG** (embedded directly, with LiaScript content injectable via `foreignObject`). A fourth section covers the character-based fine-tuning notation shared by the ASCII line-plot flavor of charts.

## Table → Chart Syntax

Any Markdown table is, by default, shown as a plain sortable table with a small toggle icon that switches to a chart view. LiaScript inspects the table's shape (numeric vs. text columns, duplicate first-column values, row/column counts, value-range spread) to guess which chart type fits, and renders it via a `lia-chart` web component (Apache ECharts). Attach settings by placing an HTML comment with `key="value"` pairs directly above the table — the same attribute-comment mechanism used for custom styling elsewhere (see `reference/syntax-core.md`).

```markdown
<!--
data-show
data-title="Government expenditure on education"
data-xlabel="year"
data-ylabel="% of GDP"
-->
| Year | Finland | USA | Germany |
| ---- | -------:| ---:| -------:|
| 1995 | 6.8     | 3.1 | 4.4     |
| 1996 | 6.9     | 3.3 | 4.5     |
```

`data-show` (or `data-show="true"`) displays the chart immediately instead of the table; `data-title`/`data-xlabel`/`data-ylabel` set the chart's title and axis labels (without `data-title`, the first header cell is used as title); `data-xlim="1994,2000"` and `data-ylim="0,12.3"` override the automatically determined axis range — leave one side blank (`data-ylim=",12"`) to auto-determine only that end.

**Caution:** if you add an authoring note (an ignoreable `<!--- ... --->` comment) near a chart table, never place it directly above the attribute comment with no blank line between them — the Markdown parser merges adjacent raw HTML comments into a single block, which breaks LiaScript's attribute extraction and silently turns the whole comment+table run into literal unrendered text (confirmed live: no table, no chart). Always separate them with a blank line. See `reference/syntax-core.md`'s "Ignoreable comments" subsection for the full rule.

**Type list** — what triggers each type automatically, and what it renders as:

| Type | Triggered by | Renders as |
|---|---|---|
| `LinePlot` | First column all-numeric, no repeated value → treated as a function | Connected multi-series line chart with legend |
| `ScatterPlot` | Like `LinePlot`, but the first column has repeated values (not a function) | Disconnected dots, no connecting line |
| `BoxPlot` | Not auto-detected — force with `data-type="boxplot"` | Real box-and-whisker plot, one box per column |
| `BarChart` | First column has at least one non-numeric entry (a category table), fewer than 50 cells, and column maxima within a factor of 10 | Grouped vertical bars, one group per row |
| `Radar` | A category table (fewer than 50 cells) whose largest column maximum is more than 10× the smallest | Multi-axis polygon per row; needs 3+ numeric columns for a readable shape |
| `PieChart` | Exactly one data row | Real pie sectors with labels; a non-numeric first cell in that row becomes the title/subtitle |
| `Funnel` | Not auto-detected — force with `data-type="funnel"` (same table shape as `PieChart`) | Pyramid/funnel shape, one layer per column |
| `Map` | `data-type="map"` plus `data-src="<geojson-url>"` naming a GeoJSON file whose feature names match the first column; only one data column is supported | Choropleth map; give it room with `style="height: 600px"` |
| `HeatMap` | Header and first column both purely numeric (coordinates); force with `data-type="heatmap"` otherwise | Colored grid with a color-scale legend; `data-title` applies here too |
| `Parallel` | A category table with 50 or more cells (rows × header columns) | Parallel coordinates: one vertical axis per column, one line per row |
| `Graph` | Table is a square matrix: header row and first column list the same node names | Node/edge diagram; symmetric matrix → undirected graph, asymmetric → directed (edge weight = cell value, may be negative or fractional); no self-loops or multi-edges |
| `None` | `data-type="none"` | Absence case — disables charting for that table entirely (also disables the first-column-fixed-while-scrolling behavior); nothing to render |

**How a category table is classified** (first column not purely numeric), in this order: 50 or more cells → `Parallel`; otherwise, if the largest column maximum exceeds 10× the smallest → `Radar`; otherwise `BarChart`. If the heuristic picks the wrong type for your data, force it explicitly:

```markdown
<!-- data-show data-type="radar" -->
| Animal          | weight in kg | Lifespan years | Mitogen |
| --------------- | ------------:| --------------:| -------:|
| Mouse           |        0.028 |               2 |      95 |
| Flying squirrel |        0.085 |              15 |      50 |
| Brown bat       |        0.020 |              30 |      10 |
```

**Animated charts** — effect fragments inside table cells change the chart per animation step; the chart updates as the user steps forward or back (in Textbook mode all fragments are shown at once, so use this only for presentation-style courses):

```markdown
       {{1}}
| Music-Style {1-2}{1994} {2}{2014} | Classic           | Country           | Reggae |
|:--------------------------------- | -----------------:| -----------------:| ------:|
| Student rating                    | {1-2}{50} {2}{20} | {1-2}{50} {2}{30} |    100 |
```

**Other attributes:**

- **`data-transpose`** (or `="true"`) — mirrors the table so rows and columns swap (e.g. a category-per-row table becomes the same pie chart as the category-per-column form).
- **`data-orientation="horizontal"`** / `"vertical"` — horizontal bars with categories on the y-axis vs. the default vertical bars.
- **`data-src`** — GeoJSON URL for `data-type="map"`; store the file in your own project rather than on an external host, to avoid CORS issues.
- **`data-sortable`** — every column of the table view is sortable by default. Set `data-sortable="false"` on the table, and override it per column with a comment inside the header cell:

  ```markdown
  <!-- data-sortable="false" -->
  | Header 1 | <!-- data-sortable="true" --> Header 2 |
  | -------- | -------------------------------------- |
  ```

`data-type` accepts (case-insensitive): `bar`/`barchart`, `boxplot`, `funnel`, `graph`, `heatmap`, `line`/`lineplot`, `map`, `none`, `parallel`, `pie`/`piechart`, `radar`, `sankey`, `scatter`/`scatterplot`. `sankey` draws a directed-flow diagram from the same adjacency-matrix table shape as `Graph` (leave cells without a flow empty).

### Custom Diagrams with ECharts

For anything the table-driven mechanism can't express, drop to the underlying `lia-chart` web component directly and pass a full [Apache ECharts](https://echarts.apache.org) `option` object in the `option` attribute. The value is parsed as JSON first and otherwise evaluated as a JavaScript object literal, so unquoted keys and even functions work. Optional `renderer="canvas"` switches from the default SVG renderer:

```html
<lia-chart option="{
  title: { text: 'Custom ECharts diagram' },
  xAxis: { type: 'value' },
  yAxis: { type: 'value' },
  series: [{ type: 'line', data: [[0,0],[1,1],[2,4]] }]
}"></lia-chart>
```

`<script>` tags (standalone JS-Components, see `reference/interactivity.md`) can compute the `option` dynamically and inject it via `"HTML: <lia-chart option='...'></lia-chart>"`.

## ASCII-Art

A fenced code block tagged `ascii` or `art` (case-insensitive; with 9+ backticks the tag is optional) is parsed by an embedded SvgBob-derived renderer and turned into a real SVG diagram. **At top level the fence must sit at the left margin** — an indented fence is not recognized and shows as plain text; inside a list item or blockquote, align it with the item's content like any other block.

````markdown
``` ascii
+------+   +-----+   +-----+   +-----+
|      |   |     |   |     |   |     |
| Foo  +-->| Bar +---+ Baz |<--+ Moo |
|      |   |     |   |     |   |     |
+------+   +-----+   +--+--+   +-----+
              ^         |
              |         V
.-------------+-----------------------.
| Hello here and there and everywhere |
'-------------------------------------'
```
````

Rendered and confirmed: real boxes with rounded/square corners, filled arrowheads on every `-->`/`<--`/`^`/`V`, and a rounded speech-bubble-style box for the `.----.`/`'----'` shape — exactly matching the ASCII layout, as an actual SVG (inspectable, scales to full slide width), not a monospace text block.

**Drawing vocabulary** (per docs, consistent with the rendered example above): borders `-`, `_`, `|` (straight) and `\`, `/` (diagonal); corners `+` (square), `.`/`,`/backtick/`'`/`´` (rounded — visually identical in the output, only the ASCII source differs), `(`/`)` (curvy, for rounded/organic shapes like `( 3 )`), and `*`/`#`/`o`/`O` (filled dot / filled square / empty dot, usable as corners or arrow endpoints); arrows use `<`/`>`/`v`/`V`/`^`/`A` for direction plus the same `*`/`#`/`o`/`O` endings (direction-independent); doubled heads (`---->>`, `<<-->>`) work too. A line only attaches cleanly to a box edge through a `+`. Unicode box-drawing characters (`─│┌┐└┘├┤┬┴┼` etc., plus double-line and shading block variants) can be mixed in freely, and full Unicode/emoji is supported directly in the drawing.

**Styling** — an HTML-comment attribute block directly above the fence works the same as any other custom-styling target (see `reference/syntax-core.md`): `style="..."` can center the image, cap its width, or override the SVG's own `fill`/`stroke`. Rendered and confirmed on a small test box with `style="display: block; margin-left: auto; margin-right: auto; max-width: 315px; fill: red; stroke: green;"` above the fence: the resulting SVG was horizontally centered within its container and its border color was overridden to green (`fill: red` had no visible effect on this particular drawing since it only used unfilled border/corner characters — no `*`/`#`-style filled shape was present to show the fill override).

**Title** — a one-liner of Markdown/LiaScript placed after the language tag on the opening fence line becomes a caption shown below the image, same mechanism as a multi-file code-project's per-block title. Rendered and confirmed: `` ``` ascii  Fig.: A simple box with a caption `` produced the literal text "Fig.: A simple box with a caption" in the DOM directly below the generated SVG image:

````markdown
``` ascii  Fig.: Working with branches in git
new feature      .---#---.
                 |       |
development    .-o---o---o----o----o-.
main   *---*-+-*---*---*-------------*----
```
````

**Embedding LiaScript content** — text in double quotes inside the drawing is rendered as real LiaScript (Markdown, math, quizzes, code, animations) in a `foreignObject` over the SVG:

- `"_styled one-liner_"` — a single quoted segment on a line.
- **Block:** consecutive lines whose opening quotes start at the same column form one block; the longest quoted line sets the block's width. Extra consecutive quotes are ignored, so `""...""` can contain a literal `"`.
- **Animations:** inline `"{1}{_How are you?_}"`; for a block, make its first line the marker: `"      {{4}}      "`.
- **TTS:** put hidden comments after the fence, e.g. `<!-- --{{2 UK English Female}}-- Need to do some math. -->`.
- **Quizzes:** add a space before the brackets (`" [[ 24 ]] "`), otherwise a lone text quiz is mistaken for a gap text; `<!-- data-show-partial-solution -->` above the fence highlights each gap separately.
- **Long content** (e.g. image URLs) that would stretch the drawing: define a macro in the header (`@image: ![](long-url)`) and use `"   @image   "` inside the drawing.
- Placement is not pixel-precise; expect to adjust quote positions by hand.

```` markdown
``` ascii
 😀                                           😐
  |             "{1}{_How are you?_}"         |
  +------------------------------------------>|
  | "                {{2}}                  " |
  | "   Now some math: $x = \sqrt[3]{y}$    " |
  +<------------------------------------------+
```
````

## SVG

A raw, unfenced `<svg>...</svg>` block placed directly in the document body is rendered as a live SVG image — standard elements (`<circle>`, `<rect>`, `<line>`, `<path>`, `<text>`, `<defs>`/`<marker>`, ...) all work as plain SVG. **This must NOT be wrapped in a fenced code block** — a fenced `` ```svg `` (or `` ````svg ````) block displays as literal source code instead of rendering (confirmed directly: identical content wrapped in a 4-backtick `svg`-tagged fence rendered as a syntax-highlighted code listing; the same content as a bare `<svg>` tag in the body rendered as the actual image). The docs' own tutorial deliberately shows both forms side by side — a fenced "here's the markup" block followed by the unfenced live render — which is easy to misread as "either form renders"; only the unfenced form does.

```markdown
<svg viewBox="0 0 200 100">
  <circle cx="50" cy="50" r="40" fill="lightblue" stroke="blue" stroke-width="2"/>
  <text x="50" y="55" font-size="10" text-anchor="middle">SVG Circle</text>
  <rect x="110" y="10" width="80" height="80" fill="lightgreen" stroke="green" stroke-width="2"/>
</svg>
```

### `foreignObject`

`<foreignObject>` embeds real Markdown/LiaScript content (math, styled text, even other interactive elements) inside the SVG's coordinate space — `x`, `y`, `width`, and `height` are required and position/size it like any other SVG element. Rendered and confirmed on a labeled-circle diagram with three `foreignObject`s (a $$C = 2\pi r$$ display formula, an inline `$r$` label, and a $$A = \pi r^2$$ display formula): all three rendered as real, correctly-typeset KaTeX at their given positions over the circle/line/dot drawn with plain SVG shapes, no console errors.

```markdown
<svg viewBox="0 0 280 200">
<foreignObject x="130" y="0" width="200" height="80">
Circumference:

$$C = 2 \pi r$$
</foreignObject>
<circle cx="100" cy="100" r="80" fill="lightblue" stroke="blue" stroke-width="2"/>
<line x1="100" y1="100" x2="180" y2="100" stroke="red" stroke-width="2"/>
<foreignObject x="110" y="78" width="100" height="30"> Radius: $r$ </foreignObject>
</svg>
```

A `foreignObject` can hold anything LiaScript can render, including animations (a `{{n}}` line at the start of its content), quizzes, `<script>`s (which can manipulate other SVG elements by `id`), and further nested SVGs. Because dark mode inverts LiaScript's default palette but not an SVG's hard-coded colors, set colors explicitly on the outer element, e.g. `<svg style="background-color: white; color: black;">`.

## Chart Fine-Tuning

A separate, lighter-weight plotting notation — distinct from the table-driven charts above — for quick line/scatter/dot plots written directly as ASCII text (no fence required; LiaScript detects the shape automatically). Indent by 4+ spaces so non-LiaScript Markdown viewers still show it as a preformatted block:

```markdown
    | r          *                                    (* stars)
    |    r                     A   A   A   A   A      (r imaginary course)
    |       r *      *       A   A   A   A   A   A    (A big triangles)
    |        * r       *
    |       *      r      *       *
    |      *            r    *
    |     *                 r
    |   *                          r
    | *                              *    r    *
    +-------------------------------------------
```

This produces a real ECharts line/scatter plot with a legend built from the parenthesized `(char label)` entries — here three series ("stars", "imaginary course", "big triangles").

**Axes, labels, title** — all optional: a title line above the plot; axis limits at the ends of the axes (y max at the top and y min at the `+` corner, x min and x max below the x-axis); the x label between the x limits; the y label written vertically, one letter per row, left of the `|`. Without limits, both axes default to the range 0 to 1:

```markdown
                                      diagram title
    1.5 |           *                     (* stars)
        |
      y |        *      *
      - |      *          *
      a |     *             *       *
      x |    *                 *
      i |   *
      s |  *
        | *                              *        *
      0 +------------------------------------------
         2.0              x-axis                100
```

**How the character encodes appearance** — the same letter used for two-or-more points at a shared x-position becomes a dot cluster (a density/dot-plot) rather than a connected line, and case matters:

- **Color** — the letter picks the color: `x`/`+`/`*`/`#` black, `a` amber, `b` blue, `c` cyan, `d` dark red, `e` ebony (gray-green), `f` forest green, `g` green, `h` heliotrope, `i` indigo, `j` jade, `k` khaki, `l` lime, `m` mint, `n` brown, `o` orange, `p` pink, `q` queen blue, `r` red, `s` silver, `t` teal, `u` ultramarine, `v` violet, `w` white, `y` yellow, `z` zomp.
- **Size** — uppercase renders larger than the lowercase form of the same letter (`R` has twice the radius of `r`).
- **Shape and line style** — also depend on the letter and its case: e.g. `r` gives small round dots with a smoothly interpolated line, `A` large triangles with sharp line segments. There is no compact rule; the docs' Shapes and Line types sections show the full grid of characters.

Custom styling applies the same way as for `ascii` blocks — an HTML comment (`<!-- style="..." -->`) directly above the plot, e.g. to increase its height for a dense multi-character legend.
