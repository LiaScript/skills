---
name: liascript-templates
description: >
  Use when building, modifying or debugging a LiaScript template — a LiaScript
  course whose header defines reusable macros that other courses `import:` —
  e.g. wrapping a JavaScript library (from a CDN or bundled from npm), writing
  macros with parameters, `@uid`, `@input` and the `send` API, async or
  long-running scripts, widgets connected by events, narrator hooks and avatars
  (`LIA.narrator`), or collaborative templates that share state in a LiaScript
  classroom via `LIA.classroom` (layers per participant, publish/subscribe,
  peers, shared Yjs types) such as drawing together, votes, markers on a map or
  small multiplayer games. German triggers: "Template für LiaScript bauen",
  "Makro-Template", "gemeinsam zeichnen im Klassenraum", "Abstimmung/Daten im
  Classroom teilen", "kollaboratives Template". For course syntax see
  liascript-syntax.
license: CC0-1.0
---

# LiaScript Template Development

A template is a normal LiaScript course (`README.md`) whose **header comment** defines reusable macros. The same file defines the macros (other courses load them with `import:`), demonstrates each macro on its own slide, and is itself a runnable course. Course syntax itself (header fields, quizzes, effects) is in the `liascript-syntax` skill.

## Navigation — read the file that matches the task

| File | Read when... |
|---|---|
| `reference/patterns.md` | Wrapping a library or building a widget: 13 copy-ready patterns (index below) and the event bus in detail |
| `reference/npm-project.md` | The library is only on npm, or must be bundled with its dependencies |
| `reference/classroom.md` | **Before writing any collaborative template**: full `LIA.classroom` API, visibility per mode, backends, complete example |
| `reference/narrator.md` | Following the narration (`lia-narrator` events) or showing an avatar |
| `reference/chat.md` | The template must also work in LiaScript/Chat (`<lia-chat>`) |

## Top pitfalls

1. **Template versions stay below `1.0.0`** (`0.x.y`), a LiaTemplates convention. LiaScript stores no local state (quizzes, classroom layers) for courses below `1.0.0`, so the template's own demo starts empty after a reload. Test persistence in a separate course with `version: 1.0.0` that imports the template.
2. **Never render a fixed `id` from a macro.** A second call on the same slide finds the first element. A public shortcut passes `@uid` to an internal macro: `@Plot.draw: @Plot.draw_(@uid)`, then `id="plot_@0"`.
3. **Async scripts end with `"LIA: wait"`** and call `send.lia("LIA: stop")` when done. Without it the run counts as finished at once and errors in the promise are lost.
4. **Insert user text into JS strings with `@'input` / `@'0`.** Plain `` `@input` `` breaks on a backtick, quote, backslash or `${`.
5. **An npm-bundled template must commit `dist/`.** LiaScript loads `script: dist/index.js` raw from the repository; an ignored `dist/` works locally and breaks for everyone importing it.
6. **The event bus has one listener per name and no buffer.** Put the listening macro before the dispatching one on the slide, and build the event name from a parameter or `@uid`.
7. **`@@` means two things**: in the header, `@@name` comments out a macro definition; in the course body, `@@Macro(args)` shows the expansion as text instead of running it — so nothing is drawn while it is there.
8. **DOM that must survive a slide change** needs `<lia-keep>` around it or `persistent: true` in the header. A template's `persistent: true` applies to every course that imports it, unless the course sets `persistent` itself.
9. **Widgets that use arrow keys** must call `event.preventDefault()` or carry a role like `slider` or `grid`; otherwise the arrow keys switch slides.
10. **Collaborative state goes into a layer, never only into pubsub**, and layer names start with the template name: `LIA.classroom.layer('PinBoard:' + id)` (`reference/classroom.md`).

## Macro syntax

```markdown
<!--
@highlight: <b style="color: @0">@1</b>     ← single line (colon): indented lines are joined
@highlight_red: @highlight(red, @0)       ← macros can call macros

@MyBlock                                  ← block (no colon): keeps whitespace, ends with @end
<div id="container_@0">
  HTML, JS and CSS work here; other @macros too.
</div>
@end

@@disabled: commented out with @@         ← only in the header
@@@DisabledBlock … @end                   ← a block commented out
-->
```

**Parameters:**
- `@0`, `@1`, … are positional, comma-separated at the call. A comma inside a value: wrap it in backticks `` `val, ue` ``.
- **Code block as last parameter**: ```` ```lang @Macro(p0) ```` — the block content becomes the last argument.
- **URL as last parameter**: `@[Macro(p0)](url)` — a relative URL is resolved to an absolute one.
- **Escaped for JS strings**: `@'0`, `@'input` escape backslash, both quotes, backticks, newlines, tabs and `${`, so the value fits into `'…'`, `"…"` and `` `…` ``.
- `@10` and higher are parameters of their own. Inserted values are not searched again, so a value containing `@1` stays as it is. An unknown `@name` in an argument (an e-mail address, CSS `@media`) stays as text. A recursive macro inside an argument stops the expansion there.

**Built-in macros:**

| Macro | Where | Effect |
|---|---|---|
| `@uid` | anywhere except the header | unique id per call: `<slide>_<n>` for the n-th `@uid` on the slide, the same in every browser |
| `@input` | inside `<script>` | current code block / quiz / user input |
| `@input(N)` | inside `<script>` | N-th listing of a multi-listing code block |
| `@'input` | inside `<script>` | escaped input for JS strings |

**Debugging**: `@@Macro(args)` in the course body shows the full expansion in a gray box, exactly as text.

## Header: what matters for templates

All header fields are listed in `liascript-syntax` (`reference/syntax-core.md`, Meta-Header). For a template:

```markdown
<!--
version:   0.1.0                       ← always below 1.0.0
script:    https://cdn.example.com/lib.min.js
           ./local.js                  ← one URL per line, indented
link:      https://cdn.example.com/style.css
attribute: [LibName](url) by Author is licensed under [MIT](url)
persistent: true                       ← only if rendered DOM must survive slide changes

@onload
window.myLib = {}                      ← runs once before the course loads
@end

@style
.my-widget { border: 1px solid; }      ← NOT shared with importing courses
@end
-->
```

| Library source | Use when | Header |
|---|---|---|
| **CDN / prebuilt** | a browser build (UMD/IIFE) exists | `script: https://cdn.../lib.min.js` |
| **Local script** | you write the glue yourself | `script: ./local.js` |
| **npm + bundler** | only on npm, or must be bundled | `script: dist/index.js` (`reference/npm-project.md`) |

Scripts run in order once all are loaded. Header scripts run once, also when a versioned course is reloaded from the browser cache; leaving a course for the home screen reloads the page. A loading screen lists the README, every `import:` and every `script:`/`link:` file with its state and warns when one failed. A template that cannot be loaded does not stop the course: its macros then show up unexpanded. Scripts and CSS loaded from raw.githubusercontent.com are cached by the service worker and work offline after the first visit. For widget CSS that importing courses need, put it in a `link:` file or set it inline from JavaScript.

## The `send` object

Every `<script>` gets its own `send`:

```js
// control strings: last statement, or via send.lia()
"LIA: wait"        // still running (async) — required for promises
"LIA: stop"        // finished, no further output
"LIA: terminal"    // interactive terminal
"LIA: clear"       // clear the console

send.lia("text")                       // output
send.lia("text", [], true / false)     // success / failure
send.lia("HTML: <b>bold</b>")          // render HTML
send.liascript("## Heading\n…")        // render LiaScript (also "LIASCRIPT:" prefix)

console.log / warn / error / debug(…)  // terminal output
console.html(str)                      // HTML into the terminal
console.stream(str)                    // text without a trailing newline

send.handle("input", text => {…})      // terminal input
send.handle("stop",  e => {…})         // user pressed stop

send.register("name", payload => {…})  // event bus (also in standalone <script> tags)
send.dispatch("name", payload)
```

A listener can replace its own script result (`send.lia`, `send.html`, `send.liascript`) without running again, so it keeps its state; pattern 13 and the event bus details are in `reference/patterns.md`. Only `</script>` ends a script in a macro; `</` or quotes in a regex, comments and nested template strings are safe. A thrown error in a standalone `<script>` is shown with its kind (`ReferenceError: …`); `LiaError` marks lines in the editor (pattern 8).

## Accessibility and keyboard

- **Arrow keys switch slides** unless the event is `defaultPrevented`, a modifier is held, the focus is in a text input, `textarea`, `select` or `contenteditable`, or inside an element with role `slider`, `spinbutton`, `radiogroup`, `radio`, `listbox`, `combobox`, `tablist`, `grid`, `tree` or `separator`. A swipe that starts in a horizontally scrolling element does not change the slide.
- **Nothing is announced for free**: slides and tables are not `aria-live`. Give a container the template updates (results, counters) `aria-live="polite"` yourself.
- **Name what you render**: inputs, buttons, canvases and SVGs need an accessible name (`aria-label`, or `role="img"` plus `aria-label`). `<script input=…>` passes `aria-label`/`aria-labelledby` to the generated input; `button`/`submit` are named by their text. Let course authors pass the name as a macro parameter.
- The id of the active script input is `lia-focus-<scriptId>`; query `[id^="lia-focus"]` or use your own element.
- **Do not rely on color alone**: the learner setting adds the class `lia-decals` on `<html>` and fires a `lia-decals` event on `window`; switch to patterns or line styles then.
- **Reduce motion** cuts all CSS animations and transitions, template CSS included (`animationend`/`transitionend` still fire). JavaScript, canvas and Web Animations are not stopped: check `matchMedia('(prefers-reduced-motion: reduce)')` there.

## Pattern index (`reference/patterns.md`)

| # | Pattern | Use for |
|---|---|---|
| 1 | Synchronous interpreter | AlaSQL, BiwaScheme, Skulpt: run `@input`, report errors |
| 2 | Async rendering with `@uid` | mermaid, JSXGraph: render into a unique element |
| 3 | Web components + `<lia-keep>` | custom elements from a bundle |
| 4 | Heavy runtime with global state | Pyodide, SQLite: load once, one run at a time |
| 5 | Shortcut chaining | public macros with default parameters |
| 6 | Dynamic content via fetch | load a file into a code block |
| 7 | Multiple code block inputs | `@input(0)`, `@input(1)`, collapsed setup listings |
| 8 | `LiaError` | mark errors at a line in the editor |
| 9 | `<script>` attributes | `run-once`, `modify`, `style`, `aria-label` |
| 10 | Versioned import | pinned tag URL and `master` URL |
| 11 | File structure | skeleton below; npm layout in `reference/npm-project.md` |
| 12 | Special built-in macros | `@uid`, `@input`, `@output` |
| 13 | Widgets connected by events | `send.register` / `send.dispatch` |
| 14 | Collaborative widget | `LIA.classroom.layer` |

## Minimal template skeleton

````markdown
<!--
author:   Your Name
email:    you@example.com
version:  0.0.1
language: en
narrator: US English Female
comment:  One-line description for the course card.

script:   https://cdn.example.com/library.min.js

attribute: [LibraryName](https://lib.example.com)
           by Author is licensed under [MIT](https://opensource.org/licenses/MIT)

@MyLib.eval
<script>
try {
  MyLib.run(`@'input`)
  "LIA: stop"
} catch(e) {
  let err = new LiaError(e.message, 1);
  err.add_detail(0, e.message, "error", 0, 0);
  throw err;
}
</script>
@end
-->

# MyLib - Template

Import via (pinned / latest):
`import: https://raw.githubusercontent.com/LiaTemplates/mylib/0.0.1/README.md`
`import: https://raw.githubusercontent.com/LiaTemplates/mylib/master/README.md`

## `@MyLib.eval`

Add `@MyLib.eval` below any code block:

```mylang
-- your code here --
```
@MyLib.eval

## Implementation

``` html
script: https://cdn.example.com/library.min.js

@MyLib.eval
<script>
...
</script>
@end
```
````

Every macro gets its own slide with a live example; the last slide shows all definitions.
