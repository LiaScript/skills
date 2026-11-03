# Implementation Patterns

Copy-ready patterns from the LiaTemplates ecosystem. Pick the one closest to the library you wrap.

### Pattern 1 — Synchronous interpreter (AlaSQL, BiwaScheme, Skulpt)
```markdown
@MyLang.eval
<script>
try {
  MyInterpreter.run(`@input`)
  "LIA: stop"
} catch(e) {
  let err = new LiaError(e.message, 1);
  err.add_detail(0, e.name + ": " + e.message, "error", lineNum - 1, 0);
  throw err;  // annotates editor with error location
}
</script>
@end
```

### Pattern 2 — Async rendering with unique ID (mermaid, JSXGraph, Chat)
```markdown
@mermaid: @mermaid_(@uid, ```@0```)   ← public shortcut injects a uid

@mermaid_
<script run-once modify="false" style="display:block; background: white">
async function draw() {
    const { svg } = await mermaid.render('graphDiv_@0', `@1`);
    send.lia("HTML: " + svg);
    send.lia("LIA: stop")
}
draw()
"LIA: wait"
</script>
@end
```

### Pattern 3 — Web components (ABCjs, JSXGraph)
The `dist/index.js` below is produced by an npm build — see `npm-project.md`.
```markdown
script: dist/index.js     ← bundles custom HTML element definitions

@MyLib.render: @MyLib.renderWith( , ```@0```)

@MyLib.renderWith
<lia-keep>
<my-element @0>@1</my-element>
</lia-keep>
@end

@MyLib.eval: @MyLib.evalWith( , @0)

@MyLib.evalWith
<script>
console.html(`<my-element @0>@input</my-element>`)
"LIA: stop"
</script>
@end
```
`<lia-keep>` prevents LiaScript from destroying the wrapped element on slide change.

### Pattern 4 — Heavy runtime with global state (Pyodide, SQLite)
```markdown
@onload
window.myRuntime = null
window.myRuntime_running = false

async function initRuntime() {
    window.myRuntime = await loadRuntime()
}
initRuntime()
@end

@Lang.eval: @Lang.eval_(@uid)          ← public, passes uid

@Lang.eval_
<script>
if (window.myRuntime_running) {
    setTimeout(() => console.warn("Another process running..."), 500)
    "LIA: stop"
} else {
    window.myRuntime_running = true
    async function run() {
        const code = "@'input"   // backslash-escaped — safe in template literals
        try {
            const result = await window.myRuntime.exec(code)
            send.lia(String(result))
        } catch(e) {
            console.error(e.message)
        }
        send.lia("LIA: stop")
        window.myRuntime_running = false
    }
    setTimeout(run, 500)
    "LIA: wait"
}
</script>
<div id="target_@0"></div>
@end
```

### Pattern 5 — Shortcut chaining
```markdown
@Lang.eval:        @Lang.eval_(@uid)        ← public, injects uid
@Lang.eval.turtle: @Lang.eval_(skulpt_canvas) ← variant with fixed container
@highlight_green:  @highlight(green, @0)    ← default-param shortcut
@load.java:        @load(java, @0)          ← language-specific shortcut
```

### Pattern 6 — Dynamic content via fetch
```markdown
@load
<script style="display:block" modify="false" run-once>
fetch("@1")
  .then(r => r.ok ? r.text() : Promise.reject("404: @1"))
  .then(t => send.lia("LIASCRIPT:\n```@0\n" + t + "\n```"))
  .catch(e => send.lia("HTML: <span style='color:red'>" + e + "</span>"))
"loading: @1"
</script>
@end

@[load(java)](relative/path/App.java)   ← link syntax auto-resolves relative URLs
```

### Pattern 7 — Multiple code block inputs
```markdown
@SQL.run2(db-name)     ← receives two code blocks:
                           @input(0) = first block
                           @input(1) = second block

```SQL -hidden-setup
CREATE TABLE ...       ← minus = listing starts collapsed (learners can open it)
```
```SQL +visible-query
SELECT * FROM ...      ← plus = listing starts open
```
@SQL.run2(mydb)
```

### Pattern 8 — `LiaError` for editor annotation
```js
let e = new LiaError("Error summary", 1);  // 1 = number of source files
e.add_detail(
    0,            // file index (0-based)
    "message",    // detail shown in console/gutter
    "error",      // or "warning"
    row - 1,      // 0-indexed row (subtract 1 from reported line)
    column        // 0-indexed column
);
throw e;
```

### Pattern 9 — `<script>` tag attributes
| Attribute | Effect |
|---|---|
| `run-once` / `run-once="true"` | Execute only on first render, not on slide revisit |
| `modify="false"` | Disable double-click-to-edit |
| `modify="// marker\n"` | Custom delimiter for the editable code region |
| `style="display: block"` | Show script output as a block element |
| `aria-label="…"` / `aria-labelledby="id"` | Name of an `input=…` widget for screen readers; give every input except `button`/`submit` one, or pass it in as a macro parameter. Groups (`radio`/`checkbox` with `options`) take it too |

### Pattern 10 — Versioned import (for stability in courses)
```markdown
<!-- pinned (stable) -->
import: https://raw.githubusercontent.com/LiaTemplates/Pyodide/0.3.5/README.md

<!-- latest (may break) -->
import: https://raw.githubusercontent.com/LiaTemplates/Pyodide/master/README.md
```
Always offer both options to users.

### Pattern 12 — Special built-in macros
| Macro | Where valid | Effect |
|---|---|---|
| `@uid` | Anywhere except header | Unique DOM id, different on each call: `<slide>_<n>` for the n-th `@uid` on the slide, so it is the same in every browser (usable in classroom layer names) |
| `@input` | Inside `<script>` tags | Current code block / quiz / user input |
| `@input(N)` | Inside `<script>` tags | Nth code block in a multi-file project |
| `@'input` | Inside `<script>` tags | Backslash-escaped input (for JS strings) |
| `@output` | Title of the last listing | That listing is not shown as a file but as the initial terminal output |

### Pattern 13 — Widgets connected by events
`send.register` in one macro, `send.dispatch` in another: the display keeps its state and only updates its own result, nothing is executed again. The parameter becomes part of the event name, so several pairs can live in one course.
```markdown
@meter.display
<script style="display: block">
send.register("meter-@0", value => send.html(`<b>${value}</b> / 10`))
"LIA: wait"
</script>
@end

@meter.input
<script input="range" aria-label="@0" value="0" min="0" max="10" input-always-active>
send.dispatch("meter-@0", @input)
""
</script>
@end
```
Use in a course: `@meter.display(score)` above `@meter.input(score)`. The display must come first, an event without a listener is dropped (see The event bus in detail below). `"LIA: wait"` keeps the listening script alive.

### Pattern 14 — Collaborative widget with a classroom layer
Each participant writes into an own layer, `on` redraws from all visible layers. Works alone and in a classroom; the full vote example with escaping is in `classroom.md`.
```markdown
@dots: @dots_(@uid)

@dots_
<canvas id="dots_@0" width="400" height="200" role="img" aria-label="Shared dots"></canvas>
<script run-once>
const layer = LIA.classroom.layer('dots:@0')
const canvas = document.getElementById('dots_@0'), ctx = canvas.getContext('2d')
canvas.onclick = e => layer.push([e.offsetX, e.offsetY])
layer.on(layers => {
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  for (const l of layers) for (const [x, y] of l.values) {
    ctx.fillStyle = l.color
    ctx.beginPath(); ctx.arc(x, y, 6, 0, 2 * Math.PI); ctx.fill()
  }
})
""
</script>
@end
```
Put `persistent: true` in the header so the canvas survives slide changes.

## The event bus in detail

**Events between code blocks and `<script>` tags** — standalone `<script>` tags have `send.register`/`send.dispatch` too, with the same global event names as code blocks (not in `worker` scripts). A listening script can replace its own result from the handler (`send.lia`, `send.html`, `send.liascript`) without being executed again, so it keeps its state. That makes it easy for a template to chain widgets: one macro renders a listener, another dispatches to it. One listener per name, a later `register` replaces the earlier one, so build the name from `@uid` or a parameter when a macro can appear several times.

**How the event bus behaves** (`LiaEvents` in `Script.ts`):
- **One global table, one listener per name.** `register` overwrites an earlier listener of the same name, on any slide (and in any message of LiaScript/Chat). There is no way to unregister through `send`.
- **No buffering.** `dispatch` to a name nobody has registered yet does nothing. Put the listener before the dispatcher on the slide (scripts start in document order), or let the listener read shared state (`window.…`) when it registers.
- **Independent of the script's run.** `send.register`/`send.dispatch` use one global handler, so a script that has already returned can still dispatch later, e.g. from an `onclick` handler it set up.
- **Synchronous.** `dispatch` calls the listener directly and returns `undefined`; an exception in the listener is thrown in the dispatching script. Wrap risky listener code in `try`/`catch`.
- **Output goes to the registering block.** `console.log`/`send.lia` in a listener write to the terminal or result of the script that registered it, not to the dispatcher. See Pattern 13 for a template built on this.

**Script bodies** — only `</script>` ends a `<script>` in a macro. `</` in a regex or comment, quotes in a regex, nested template strings and unclosed string literals do not cut the script.
