# Visuals

Three independent visualization mechanisms: **table→chart** (a Markdown table auto-rendered as an interactive ECharts diagram), **ASCII-Art** (a text drawing rendered as a real SVG image), and raw **SVG** (embedded directly, with LiaScript content injectable via `foreignObject`). A fourth section covers the character-based fine-tuning notation shared by the ASCII line-plot flavor of charts.

## Table → Chart Syntax

Any Markdown table is, by default, shown as a plain sortable table. If LiaScript finds a chart type that fits the data, a small toggle icon switches to a chart view. It inspects the table's shape (numeric vs. text columns, the values of the first column, row/column counts, value-range spread) to guess the type (rules below; `data-type` forces one, and only then does a text-heavy table get a chart), and renders it via a `lia-chart` web component (Apache ECharts). Attach settings by placing an HTML comment with `key="value"` pairs directly above the table — the same attribute-comment mechanism used for custom styling elsewhere (see `reference/syntax-core.md`).

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

`data-show` (or `data-show="true"`) displays the chart immediately instead of the table; `data-title`/`data-xlabel`/`data-ylabel` set the chart's title and axis labels (without `data-title`, the first header cell is used as title); `data-xlim="1994,2000"` and `data-ylim="0,12.3"` override the automatically determined axis range — leave one side blank (`data-ylim=",12"`) to auto-determine only that end. An empty `data-xlim=""` counts as unset since LiaScript 2.2.0; up to 2.1.2 it was passed to ECharts as an empty limit, so leave the attribute out instead.

**Accessible name** (since LiaScript 2.3.0) — a chart is announced as an image. Its name is, in this order: an `aria-label` in the attribute comment (`<!-- data-type="bar" aria-label="Education spending 1995–2000, Finland highest" -->`), else the description ECharts generates, else `data-title`. Since 2.3.0 `data-title` also names the table itself, via a hidden caption. The same `aria-label` works for ASCII charts and a raw `<lia-chart>`. Learners can turn on "do not rely on color alone" in the settings, which adds patterns to the chart series; a chart should still not depend on color alone, e.g. label the series directly where it matters.

**Caution:** never put an authoring note (`<!--- ... --->`) directly above the attribute comment without a blank line in between. The two comments merge into one block, and the comment and table then show up as raw text, with no table and no chart. See `reference/syntax-core.md`'s "Ignoreable comments".

**Type list** — what each type renders as, and when it is guessed (details below):

| Type | Guessed for | Renders as |
|---|---|---|
| `LinePlot` | Numeric x values in the first column, strictly increasing or decreasing; dates or times in the first column | Connected multi-series line chart with legend |
| `ScatterPlot` | Numeric x values that are not monotonic | Disconnected dots, no connecting line |
| `BarChart` | Categories in the first column (default case) | Grouped vertical bars, one group per row |
| `Radar` | Categories, 3+ numeric columns whose maxima differ by more than 10× | Multi-axis polygon per row |
| `Parallel` | Categories, 3+ numeric columns and 50+ cells; or maxima differing by more than 10× with fewer than 3 numeric columns | Parallel coordinates: one vertical axis per column, one line per row |
| `PieChart` | Exactly one data row with positive values | Real pie sectors with labels; a non-numeric first cell in that row becomes the title/subtitle |
| `HeatMap` | Numeric header and numeric, unique first column (coordinates); or an adjacency matrix with a filled diagonal | Colored grid with a color-scale legend; `data-title` applies here too |
| `Graph` | Adjacency matrix: header row and first column list the same node names, diagonal empty or `0` | Node/edge diagram; symmetric matrix → undirected graph, asymmetric → directed (edge weight = cell value, may be negative or fractional); no self-loops or multi-edges |
| `BoxPlot` | Never, use `data-type="boxplot"` | Real box-and-whisker plot, one box per column |
| `Funnel` | Never, use `data-type="funnel"` (same table shape as `PieChart`) | Pyramid/funnel shape, one layer per column |
| `Sankey` | Never, use `data-type="sankey"` (same shape as `Graph`) | Directed flows; leave cells without a flow empty |
| `WordCloud` | Never, use `data-type="wordcloud"` (since LiaScript 2.2.0) | One word cloud per data row, see Word clouds below |
| `Map` | `data-src="<geojson-url>"` (with or without `data-type="map"`), feature names must match the first column; only one data column is supported | Choropleth map; give it room with `style="height: 600px"` |
| `None` | Text-heavy tables, truth tables (see below); `data-type="none"` | No chart and no toggle; `data-type="none"` also disables the first-column-fixed-while-scrolling behavior |

**How the type is guessed (since LiaScript 2.2.0)** — `data-transpose` is applied first, then these rules in order:

1. Only the columns after the first count, empty cells are ignored. A column is numeric if more than half of its filled cells are numbers. A number may be followed by a unit (`12 kg`, `5 %`); an ordinal like `5.` is text. **If there are not more numeric than text columns, the table stays a plain table without a chart.**
2. Header names equal to the first-column values (an adjacency matrix) → `Graph` if the diagonal is empty or `0`, else `HeatMap`.
3. Only `0` and `1` in the first column and in all numeric columns (a truth table) → `None`.
4. Exactly one data row → `PieChart` if the table has a header and all values are positive, else `None`. A place-value table with zeros stays a table.
5. Numbers in the whole first column (x values): a numeric header with at least two names and unique x values → `HeatMap`; strictly increasing or decreasing x values → `LinePlot`; otherwise `ScatterPlot`.
6. Categories in the first column: a table without a header stays plain. First cells that all start with a digit (dates and times like `2024-03-01`, `01.05.2024`, `08:00`) → `LinePlot`. 3+ numeric columns and at least 50 cells (rows × header columns) → `Parallel`. Column maxima that differ by more than 10× → `Radar` with 3+ numeric columns, else `Parallel`. Otherwise `BarChart`.

**Up to LiaScript 2.1.2** the guess was more eager: every table with at least one number got a chart toggle. A numeric first column without repeated values was a `LinePlot`, with repeats a `ScatterPlot`; exactly one data row was a `PieChart`; a numeric header and first column were a `HeatMap`; a square matrix with matching names a `Graph`. For a category table: 50 or more cells → `Parallel`; otherwise, if the largest column maximum exceeds 10× the smallest → `Radar`; otherwise `BarChart`.

If the heuristic picks the wrong type for your data, force it explicitly; this works the same in every version:

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
- **`data-orientation="horizontal"`** / `"vertical"` — horizontal bars with categories on the y-axis vs. the default vertical bars. Write the value in lowercase: it is matched case-insensitively only since LiaScript 2.2.0.
- **`data-src`** — GeoJSON URL for `data-type="map"`; store the file in your own project rather than on an external host, to avoid CORS issues.
- **`data-sortable`** — every column of the table view is sortable by default. Set `data-sortable="false"` on the table, and override it per column with a comment inside the header cell:

  ```markdown
  <!-- data-sortable="false" -->
  | Header 1 | <!-- data-sortable="true" --> Header 2 |
  | -------- | -------------------------------------- |
  ```

`data-type` accepts (case-insensitive): `bar`/`barchart`, `boxplot`, `funnel`, `graph`, `heatmap`, `line`/`lineplot`, `map`, `none`, `parallel`, `pie`/`piechart`, `radar`, `sankey`, `scatter`/`scatterplot`, and since LiaScript 2.2.0 `wordcloud`. `sankey` draws a directed-flow diagram from the same adjacency-matrix table shape as `Graph` (leave cells without a flow empty).

**Word clouds** (since LiaScript 2.2.0) — `data-type="wordcloud"` turns the header cells into words and every data row into one cloud, sized by its values; the first cell of the row is the cloud's subtitle. Several rows give clouds side by side that share one font scale, so equal values have equal sizes, and every word keeps its color across clouds. A long word list is easier to write one word per row, with `data-transpose`. Effects in cells animate the cloud like any other chart. An older interpreter ignores the unknown type and guesses one.

```markdown
<!-- data-type="wordcloud" data-transpose data-show -->
| Language   | Votes |
| ---------- | ----: |
| Python     |    42 |
| JavaScript |    30 |
| Elm        |     8 |
| Rust       |    17 |
| Haskell    |     5 |
```

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

This section covers the syntax only. For actually drawing diagrams (grid rules, character traps, Unicode/emoji widths, tested templates, a checker and a renderer that shows the result) use the `liascript-asciiart` skill.

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

The result is a real SVG that scales to the slide width: boxes with square or rounded corners, filled arrowheads on `-->`/`<--`/`^`/`V`, and a rounded box for the `.----.`/`'----'` shape.

**Drawing vocabulary**: borders `-`, `_`, `|` (straight) and `\`, `/` (diagonal); corners `+` (square), `.`/`,`/backtick/`'`/`´` (rounded — visually identical in the output, only the ASCII source differs), `(`/`)` (curvy, for rounded/organic shapes like `( 3 )`), and `*`/`#`/`o`/`O` (filled dot / filled square / empty dot, usable as corners or arrow endpoints); arrows use `<`/`>`/`v`/`V`/`^`/`A` for direction plus the same `*`/`#`/`o`/`O` endings (direction-independent); doubled heads (`---->>`, `<<-->>`) work too. A line only attaches cleanly to a box edge through a `+`. Unicode box-drawing characters (`─│┌┐└┘├┤┬┴┼` etc., plus double-line and shading block variants) can be mixed in freely, and full Unicode/emoji is supported directly in the drawing.

**Styling** — an HTML-comment attribute block directly above the fence works the same as any other custom-styling target (see `reference/syntax-core.md`): `style="..."` can center the image, cap its width, or override the SVG's own `fill`/`stroke`, e.g. `style="display: block; margin: auto; max-width: 315px; stroke: green;"`. `fill` only affects filled shapes (`*`, `#`).

**Title** — a one-liner of Markdown/LiaScript placed after the language tag on the opening fence line becomes a caption shown below the image, same mechanism as a multi-file code-project's per-block title:

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

A raw, unfenced `<svg>...</svg>` block placed directly in the document body is rendered as a live SVG image — standard elements (`<circle>`, `<rect>`, `<line>`, `<path>`, `<text>`, `<defs>`/`<marker>`, ...) all work as plain SVG. **Do not wrap it in a fenced code block**: a fenced `` ```svg `` block shows the source code instead of the image. The official tutorial shows both forms side by side (markup, then live render), which is easy to misread as "either form renders"; only the unfenced form does.

```markdown
<svg viewBox="0 0 200 100">
  <circle cx="50" cy="50" r="40" fill="lightblue" stroke="blue" stroke-width="2"/>
  <text x="50" y="55" font-size="10" text-anchor="middle">SVG Circle</text>
  <rect x="110" y="10" width="80" height="80" fill="lightgreen" stroke="green" stroke-width="2"/>
</svg>
```

### `foreignObject`

`<foreignObject>` embeds real Markdown/LiaScript content (math, styled text, even other interactive elements) inside the SVG's coordinate space — `x`, `y`, `width`, and `height` are required and position/size it like any other SVG element. Formulas inside are typeset with KaTeX as usual.

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
