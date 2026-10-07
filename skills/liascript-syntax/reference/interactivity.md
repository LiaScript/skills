# Interactivity

LiaScript content becomes interactive through five layers that combine freely: **effects** (animation/narration/playback timing), **executable code blocks** (editable code with an Execute button and a terminal), the **`send`/JS API** every script gets, **macros** (text-substitution shortcuts, usually imported from a template course), and **JS-Components** (raw `<script>` tags embedded directly in the Markdown body). This file covers all five for *using* them in a course. For *building* a reusable macro/template package for the LiaTemplates ecosystem, see the separate `template-development` skill — it documents the 12 implementation patterns and the full `send` object from the author's side; this file only covers calling what already exists.

## Effects

Animations, comments, and playback are all defined with double curly braces `{{...}}` (or single braces `{...}` for inline use) placed above/around a block or span. They are revealed step-by-step with each click in `Presentation`/`Slides` mode; in `Textbook` mode every step is shown at once, each tagged with its step number.

**Block animation** — a `{{start-stop?}}` line directly above a block (indent by 4+ spaces so other Markdown tools show it as code); the block appears at `start` and, if given, disappears at `stop`:

```markdown
     {{1}}
This appears at step 1 and stays.

     {{2-3}}
This appears at step 2 and disappears at step 3.

{{4}} Same-line form: also valid, but harder to spot in other viewers.
```

**Inline animation** — wrap the animation definition and the affected text in two adjacent brace pairs, usable mid-sentence:

```markdown
* no effect here
* but in this line {2}{show ***second***}
* as well as this one {1-2}{show ***first*** remove on __second__}
```

**Multi-block animation** — group several Markdown blocks (paragraphs, tables, ...) under one step by surrounding them with lines of 3+ asterisks, with the animation definition above the opening line. A `<section>...</section>` wrapper in place of the two asterisk lines works the same way. Note `***` has a second, unrelated meaning as the quiz solution-block delimiter — see `reference/quizzes-surveys.md`'s Tweaks section.

```markdown
     {{1-2}}
************************************

This is an example...

| that     | contains |
|----------|----------|
| multiple | blocks.  |

************************************
```

**Styling and nesting** — a multi-block animation may contain further block and inline animations. An attribute comment above the animation marker styles the revealed block. For entrance effects use [animate.css](https://animate.style). It is **not** bundled with LiaScript: load it with `link:` in the header first, otherwise the classes do nothing. Version 4 needs the `animate__` prefix on every class:

```markdown
<!--
link: https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css
-->

# Slide

<!-- class="animate__animated animate__backInUp" -->
     {{1}}
This block flies in at step 1, with an {2}{inline part}<!-- class="animate__animated animate__flash" --> at step 2.
```

**TTS-sync comments** — a paragraph marked with `--{{n}}--` is read aloud by the text-to-speech engine when animation step `n` is reached. Think of `{{n}}` as a presentation bullet (what appears) and `--{{n}}--` as the speaker notes for that same bullet (what is said). Where the text is visible depends on the mode:

| Mode | `--{{n}}--` text |
|---|---|
| Textbook | shown in place as an ordinary paragraph |
| Presentation | spoken, visually hidden (still in the DOM for screen readers) |
| Slides | spoken and shown as speaker notes: a side panel on wide screens, below the slide on narrower ones |

Place the narration **before** the block it explains. In Textbook mode it then reads as the sentence that introduces the block. The full pattern, including picture sequences with `{{n-m}}`, is in `reference/presentation-pattern.md`.

```markdown
                    --{{1}}--
Plants use the energy of sunlight to turn water and carbon dioxide
into sugar.

                      {{1}}
**Photosynthesis converts light into sugar.**
```

**Common mistake: `--{{n}}--` never makes content appear.** It is only the narration half of the pair. Content that should appear on screen at step `n` needs `{{n}}`; a `--{{n}}--` paragraph alone stays invisible in Presentation mode, and nothing reports an error.

Wrap the comment in an HTML comment (`<!-- --{{n}}-- ... -->`) to keep it out of Textbook mode too: it is spoken but never shown in any mode, and it still counts as an animation step.

Several comments with the same step number are read in document order and combined; only the first one's voice is used.

**Voices** — the voice can be set on three levels:

1. **Course:** `narrator:` in the main header (default if missing: `US English Male`).
2. **Slide:** a `narrator:` in an HTML comment directly below the slide heading overrides it for that slide.
3. **Comment:** `--{{n voice}}--` overrides it for one comment, e.g. `--{{3 Deutsch Female}}--`.

Custom voice aliases are defined as macros and used with `@`:

```markdown
## Slide Title
<!--
narrator: UK English Female
@Tanja:   Russian Female
-->

    --{{1}}--
Spoken with the slide's UK English Female voice.

    --{{2 Deutsch Female}}--
Dieser Kommentar wird mit einer deutschen Stimme gesprochen.

    --{{3 @Tanja}}--
«Для торжества зла достаточно бездействия хороших людей».
```

Voice names follow the ResponsiveVoice naming scheme (`<Language> Female`/`<Language> Male`, e.g. `UK English Female`, `Deutsch Male`, `French Female`, `Arabic Male`); the full list is in the docs' `narrator` section. LiaScript uses the browser/OS speech engine first and picks the best-matching installed voice (with fallbacks to related languages); ResponsiveVoice is the backup engine. Pick a voice whose language matches the course's `language` field.

**Speech rate and pitch** — an attribute comment above a comment or playback element changes how it is spoken: `data-pitch` from `0` to `2`, `data-rate` from `0.1` to `5`:

```markdown
<!-- data-rate="1.5" data-pitch="1.2" -->
    --{{1}}--
This is read faster and slightly higher.
```

**Translation** — users can translate a course with Google Translate from the settings. Code blocks and comments with a non-default voice (foreign-language text) are never translated; LiaScript then looks for a voice matching the new language. To exclude any other block or inline element, attach both attributes (Google uses the class, other tools the attribute):

```markdown
<!-- class="notranslate" translate="no" -->
    --{{2}}--
I will not be translated!
```

**Recorded audio or video instead of TTS (optional)** — a comment that starts or ends with an audio or video link plays that recording instead of speaking the text when the step is reached:

```markdown
    --{{1}}--
?[⏯](recording/audio_1.mp3)
The recording replaces the TTS output for this step.

    --{{2}}--
!?[⏯](recording/video_2.webm#t=4,12)
The video is shown as an overlay the viewer can move and resize.
```

- The link is not rendered as a normal inline player. Audio is only fetched and played when the step is reached; a video appears as a movable overlay.
- `#t=start,end` (in seconds) plays only that part of the file.
- `data-rate` also applies to recordings; `data-pitch` does not.
- If the user translates the course with Google Translate, translated comments are spoken with TTS in the target language instead of playing the recording.

**Playback** — `{{|>}}` (block) or `{|>}{...}` (inline) attaches a visible Play/Pause button that reads the paragraph aloud on click, independent of the animation step machinery and visible in every presentation mode (unlike TTS-sync comments, which never appear inline outside Textbook mode — see above):

```markdown
    {{|>}}
This entire paragraph will be spoken out __LOUD__.

    {{!> Australian Female}}
* But in this case, this can also be combined
* with a couple of
* - different
  - Markdown elements
```

`{{!> voice}}`/`{!> voice}{...}` picks a specific voice for that one playback button. `|>` and `!>` are interchangeable — use `!>` inside tables, where `|` would break the table syntax.

**Playback blocks** — put `{{|>}}` above a `***` fence (or a `<section>`/`<div>`) to read several blocks with one button. For quizzes, prefer one inline playback button per option (see `reference/quizzes-surveys.md`'s Reading quizzes aloud).

**Inline playback** — `{|>}{text}` or `{!> voice}{text}` adds a play button to a word or phrase; ideal for vocabulary tables in language courses:

```markdown
| English      | German                        |
| ------------ | ----------------------------- |
| {!>}{I go}   | {!> Deutsch Male}{ich gehe}   |
| {!>}{you go} | {!> Deutsch Male}{du gehst}   |
```

**Playback combined with animation** — add the step range: `{{1 |>}}` for a block, `{|> 1-2}{...}` inline. The button appears at that step, and what is read depends on which inline parts are currently visible (in Textbook mode everything is shown and read):

```markdown
    {{1 |>}}
This is an example where {|> 1-2}{I go} _{|> 2}{I am going}_ to work.
```

**Play buttons without visible text** — TTS and translation need the text in the DOM, so `display: none` does not work. Shift the text off-screen instead, best via a macro in the slide's header comment:

```markdown
<!--
@play: {!> @0}{<span style="display: inline-block; text-indent: -10000px">@1</span>}
@de: @play(Deutsch Male,@0)
-->

| I | @de(ich gehe) |
```

## Interactive Code Blocks

**Starting simple** — attach a `<script>@input</script>` tag directly below a fenced code block to make it executable: an Execute button and (after the first run) a terminal panel appear below the editor. `@input` is replaced with the block's current (editable) content before the script runs; the script's last expression is the returned/displayed value.

````markdown
``` javascript
var result = 0
for (var i = 0; i < 5; i++) { result += i }
result
```
<script>@input</script>
````

Each run of edited code is saved as a new version; the user can step back and forth between versions (editing an older version appends a new one).

**Multi-file projects** — several fenced code blocks placed back-to-back with *no blank line between them* become one project with one shared `<script>` tag at the end. Give each block a filename after the language (prefix `-` to start hidden/minimized, `+` — the default — to start visible), and reference an individual block from the script with `@input(n)` (0-indexed; `@input` alone is equivalent to `@input(0)`):

````markdown
``` js     -EvalScript.js
let who = data.first_name + " " + data.last_name;
if (data.online) { who + " is online"; } else { who + " is NOT online"; }
```
``` json   +Data.json
{ "first_name": "Sammy", "last_name": "Shark", "online": true }
```
<script>
  let data = @input(1);
  @input(0)
</script>
````

**Default `@output`** — add `@output` as an attribute in the *last* code block's fence header (` ```text @output `) inside a project to designate its content as the default output: it is shown in the terminal as soon as the slide loads and replaced by the real result after the first Execute. It only works as a fence-header attribute of a project's last block, not on a single code block.

````markdown
``` js     -EvalScript.js
let who = data.first_name + " " + data.last_name;
if (data.online) { who + " is online"; } else { who + " is NOT online"; }
```
``` json   +Data.json
{ "first_name": "Sammy", "last_name": "Shark", "online": true }
```
``` text @output
Is Sammy Shark really online?
```
<script>
  let data = @input(1);
  @input(0)
</script>
````

This is useful for a course a student may be running offline (no external interpreter available) or for a plain-Markdown viewer like GitHub, where the code never actually executes.

**Loading external resources** — a library referenced from inside a `<script>` tag must be loaded via the `script:` meta-header field first (`<script>` tags themselves cannot fetch external JS); once loaded it is available globally to every code block on the page:

````markdown
<!--
script: https://cdn.example.com/library.min.js
-->

``` matlab
f = sin(t)^4 - 2*cos(t/2)^3*sin(t)
```
<script> Algebrite.run(`@input`) </script>
````

**Styling** — attributes go in an HTML comment directly above the fence. `data-showGutter="false"` removes the line-number gutter; `data-theme="chaos"` (any Ace theme name) switches the editor's color theme; `data-marker="y1 x1 y2 x2 color type;"` (repeatable, `;`-separated) highlights a row/column range with a color keyword (`error`/`log`/`warn`/`debug`/`info`, or a spaceless `rgba(...)`) and an optional marker type (`text`, `fullLine` default, `screenLine`). Further attributes and their defaults: `data-tabSize="2"`, `data-fontSize="12pt"` (must be given in `pt`), `data-firstLineNumber="0"`. By default, non-executable code blocks show no line numbers (useful for pseudo-code), executable ones do.

**Write attribute names exactly as listed here.** Up to LiaScript 2.1.2 they are matched case-sensitively: `data-showGutter`, `data-tabSize`, `data-fontSize` and `data-firstLineNumber` are camelCase, but `data-readonly` is all lowercase.

- `data-readonly="true"` locks an executable block against editing. Executable blocks are editable by default, non-executable ones are read-only, and `data-readonly="false"` makes them editable.
- `data-rtl="true"` switches the editor to right-to-left, e.g. for Arabic or Hebrew code comments.
- `data-ace-options="spellcheck hardWrap=80, tabSize=8"` (since 2.1.1) passes options straight to the Ace editor. It takes whitespace- or comma-separated `name` or `name=value` pairs; a bare name means `true`, and values are read as JSON. The extensions behind `spellcheck`, `hardWrap`, `useElasticTabstops` and the autocompletion options are loaded on demand. Since 2.1.1, autocompletion and snippets are on in executable blocks.

## The send/JS API

LiaScript runs two kinds of scripts, and they get **different `send` objects**:

- **Code-block and quiz scripts**: the `<script>` attached to a code block (`@input`), a quiz, a survey or a task list.
- **Standalone scripts**: a bare `<script>` in the body, including input widgets. See JS-Components below.

| Function | Code-block / quiz script | Standalone script |
|---|---|---|
| `send.lia(msg, details, ok)` | yes | yes |
| `send.log(type, sep, list)`, `send.handle(...)` | yes | no |
| `send.register(...)`, `send.dispatch(...)` | yes | **no** (`send.register is not a function`) |
| `send.output(msg)`, `send.wait()`, `send.stop()`, `send.clear()` | no | yes |
| `send.html(msg)`, `send.liascript(msg)` | no (use the `HTML:` / `LIASCRIPT:` prefix) | yes |
| `console.*` into the terminal panel | yes | no (the browser's console) |

```js
// Control strings — as the script's last expression, or via send.lia(...)
"LIA: stop"       // finish, no further output shown for this run
"LIA: wait"       // keep the loading/running indicator active (for async work)
"LIA: terminal"   // open an interactive input line below the output (a REPL)
"LIA: clear"      // clear the terminal panel

send.lia("message")           // push output, keep running
send.lia("message", [], true) // push output, mark as success (green)
send.lia("message", [], false)// push output, mark as failure (red)
send.lia("LIA: stop")         // push output and stop in one call

send.lia("LIASCRIPT:\n## Heading\n...")  // parsed as LiaScript markup
send.lia("HTML: <b>bold</b>")            // injected as raw HTML

// Code-block scripts only:
console.debug(...)   // gray debug line
console.warn(...)    // yellow warning
console.log(...)     // plain info line
console.error(...)   // red error line
console.html(str)    // inject raw HTML into the terminal
console.stream(str)  // append without a trailing newline
console.clear()      // shorthand for send.lia("LIA: clear")
console.table(data)  // also: console.assert, console.count/countReset,
                     //       console.time/timeLog/timeEnd (performance measurement)

send.log("warn", "", ["This is a warning", 12, [1,2,3]])
                     // generic form: send.log(type, separator, contentList),
                     // type = "debug" | "info" | "warn" | "error" | "html" | "stream"

// Terminal I/O, once "LIA: terminal" is active
send.handle("input", input => { /* runs on each line the user submits */ })
send.handle("stop",  e     => { /* runs when the user clicks stop */ })

// Pub/sub between code blocks
send.register("event-name", callback)
send.dispatch("event-name", payload)
```

- **Async pattern** — end the run with `"LIA: wait"`, and call `send.lia(...)` once the async work finishes, with `"LIA: stop"` at the end or as a separate call. The Execute button is hidden while waiting.
- **`"LIA: terminal"` + `send.handle`** — after Execute, an input line with a send button appears below the output; each submitted line goes to the `input` handler. <kbd>Shift</kbd>+<kbd>Enter</kbd> inserts a new line, Enter submits.
- **`send.register`/`send.dispatch`** work across slides: a listener registered by a code block on one slide also receives events dispatched from another slide. Listeners are global and are never removed. **There is only one listener per event name**: a later `register` with the same name replaces the earlier one. Output of a listener (`console.log`, `send.lia`) goes to the terminal of the block that registered it, so it is not visible while that slide is not shown. To change something visible from another slide, change shared state instead, e.g. a `window` variable.
- **Error annotations in the editor** — pass line-specific details as the second argument of `send.lia` (one inner list per code block of the project), or throw a `LiaError`:

  ```js
  send.lia("ups, something went wrong",
    [[{ row: 1, column: 1, text: "insert your error info here", type: "error" },
      { row: 2, column: 1, text: "a warning about this line",   type: "warning" }]],
    false)
  "LIA: stop"

  // or, equivalently:
  var error = new LiaError("ups something went wrong", 1)   // 1 = number of code blocks
  error.add_detail(0, "insert your error info here", "error", 1, 1)  // block, text, type, row, column
  throw error
  ```

## Using Macros

A macro is `@Name` or `@Name(args)` anywhere in the document body (or `@Name`/`@Name: ...` in a meta-header block), expanded at parse time from a definition — either written locally in this course's header, or pulled in from another course entirely with `import:`:

````markdown
<!--
import: https://raw.githubusercontent.com/liaTemplates/ABCjs/main/README.md
-->

``` abc  @ABCJS.render
X: 1
T: Test Tune
M: C
L: 1/8
K: F
"F"[A3F3][AF] ([AF][GE][AF])[BG] |
```
````

`import:` (repeatable, one URL per line) loads only the *main header* of the referenced course — its macros, `script:`/`link:` entries, `attribute:` lines, and `@onload` block — not its body content: the imported course's slides never appear. Prefer pinning a specific tag/commit in the `import:` URL over `master`/`main` for a course that needs to keep working unmodified.

**Defining macros** — in the main header or in a slide's header comment (a slide-level definition overrides a main-header macro of the same name, e.g. to change `narrator` or `author` for one section). Macro names are case-sensitive (`@author` ≠ `@Author`); the leading `@` in a definition is optional but recommended.

```markdown
<!--
@smile: ;-)
@Single.line: a single-line macro may continue
  on further lines, as long as they are indented.

@block
Block macros keep whitespace and newlines and may contain
Markdown, HTML, CSS, or JavaScript — and call other macros: @smile
@end

@@commented: a single-line macro commented out with @@
@@@commented-block
a block macro commented out with @@@
@end
-->
```

Two special block macros in the main header: `@onload ... @end` holds JavaScript that runs once before the course is shown (global helper functions, setup), and `@style ... @end` holds CSS that is applied directly while parsing (faster than an external `link:`, and not passed on when the course is imported). To write a literal `@` that must not be expanded, escape it: `\@`.

**Calling a macro with parameters** — parentheses, comma-separated, positional (`@0`, `@1`, ... inside the definition). With `@highlight: <b style="color: @0">@1</b>` in the header, this renders a red bold "simple text":

```markdown
@highlight(red, simple text)
```

A parameter that itself contains commas must be wrapped in backticks, otherwise it is split at the first comma:

```markdown
@highlight(green, `simply, simply, green`)
```

A multi-line parameter can be passed inline by wrapping it in a triple-backtick block inside the parentheses (``@highlight(green, ```...```)``) — this works but reads badly in other Markdown viewers, so prefer a code-block parameter:

**Code-block parameter** — put the macro call in the fence's info string, after the language tag; the block's *content* becomes the macro's **last** parameter (the language tag only drives syntax highlighting in other viewers):

````markdown
``` json @panorama("0",https://pannellum.org/images/cerro-toco-0.jpg)
{ "pitch": 14.1, "yaw": 1.5, "type": "info", "text": "Baltimore Museum of Art" }
```
````

**Link parameter** — `@[MacroName(other, args)](relative/or/absolute/url "optional title")`: the URL is passed as the last parameter, and a relative URL is resolved to an absolute one first. Because the call is shaped like a normal Markdown link, it still renders as a clickable link on GitHub and in other viewers.

**Escaping for use inside a JS string** — prefix with `'`: `@'input`, `@'input(1)`, `@'0`, or `@'MacroName(...)` backslash-escape the substituted value so it's safe to embed inside a JS template literal, per the official docs. Apply it once only; chaining escaped macros can double-escape special characters.

**Debugging a call** without running it — prefix with an extra `@` (`@@MyMacro(args)`) to show its fully expanded output in a gray, read-only code block instead of executing it.

For *authoring* your own macros/templates — the block/single-line macro syntax, `@uid`, the 12 established implementation patterns for wrapping a JS library, `LiaError` for editor annotations, and the full template file layout — see the `template-development` skill; that content is not duplicated here.

## JS-Components

A bare `<script>...</script>` tag placed directly in the document body (no fenced code block, no `@input`, no Execute button) is a **standalone JS-Component**: it runs automatically wherever it appears, as an inline element like `**bold**` or an inline formula, and its final expression's value is displayed in place of the tag. An `undefined` result (e.g. from a bare `alert(...)` or a final `var` assignment) displays nothing, which makes the script invisible.

```markdown
$ \sin(\frac{\pi}{2}) = $ <script>Math.sin(Math.PI / 2)</script>
```

Every script — code-block or standalone — runs in its own local scope; two `<script>` tags cannot see each other's plain `var`/`let` bindings. To share state, attach it to `window` explicitly:

```markdown
<script> window.a = 22 ** 3 </script>
<script> window.a / 2 </script>
```

If a script throws, the error message is displayed as its result.

Scripts combine with animation numbers the same way any block does (`{{1}} <script>...</script>`) to delay execution until that step is reached; in `Textbook` mode all of a slide's scripts run once the slide loads. A script without an animation number runs whenever the slide is opened — again on every visit (use `run-once` to prevent that, see Script attributes below).

**Returning HTML or LiaScript** — a plain string result is shown as text. Prefix it with `HTML:` to render it as HTML, or with `LIASCRIPT:` to have it parsed as LiaScript (tables, formulas, even quizzes). Scripts render inline by default; `style="display: block"` gives them the full line. Quizzes/code generated this way are not persisted — only elements written directly in the Markdown keep their state.

```markdown
<script run-once>"LIASCRIPT: $$\\frac{1}{x} = 0$$"</script>

<script style="display: block" modify="false">
"HTML: <marquee>This text scrolls</marquee>"
</script>
```

**Script attributes:**

| Attribute | Effect |
|---|---|
| `run-once` | Execute only once; the result is kept and shown on every later appearance. |
| `modify="false"` | Disables editing the script by double-click and removes the gray background. |
| `modify="// pattern\n"` | Only the code between two `// pattern` lines is shown/editable on double-click; the rest stays hidden. Combine with `type` (e.g. `type="text/python"`) for highlighting when executing other languages from a string. |
| `worker="true"` | Run in a web worker (for heavy computation) — no DOM access. |
| `update-on-change` / `="false"` | Re-run on every change vs. only on Enter/blur, overriding the input type's default. |
| `input-active` | The input widget is visible on first appearance (normally it appears only after clicking the script), and closes again on blur. |
| `input-always-active` | The input widget stays visible permanently. |
| `style="display: block"` | Render the script result as a block instead of inline. |


**Asynchronous execution & `send.output`** — `send.output(...)` exists only in standalone scripts (see the table in The send/JS API). For a long-running, self-updating script, return `"LIA: wait"` (or call `send.wait()`) so LiaScript knows the process is still active, then call `send.output(...)` on every update. Unlike `send.lia(...)`, this does not reset the run:

```markdown
<script>
setInterval(function(){
  i++
  send.output("counting " + i)
}, 1000)

var i = 0
"LIA: wait"
</script>
```

The text updates in place without an Execute button. The process keeps running while the learner is on another slide: on return the display reattaches to it, and the setup code does not run again. It runs until `send.stop()` or `send.lia("LIA: stop")` is called. Shortcuts: `send.wait()` = `"LIA: wait"`, `send.stop()` = `"LIA: stop"`, `send.clear()` = `"LIA: clear"`.

**Input types** — add `input="<type>"` (plus `value="..."` for the initial value) to a `<script>` tag to turn it into a small interactive widget wired to `@input`; most HTML5 input types are supported: `text` (the default for a bare `input` attribute), `number`, `range`, `checkbox`, `radio`, `select`, `button`, `submit`, `search`, `password`, `email`, `url`, `tel`, `color`, `date`, `datetime-local`, `time`, `month`, `week`, `hidden`, and `textarea` (`file` and `image` are not supported). `text`/`number`/`range`/`radio`/`checkbox` re-run the script on every change, most others once the field loses focus or Enter is pressed — `update-on-change` overrides this. A `checkbox` with `options="Ben|Jerry"` becomes a multi-select returning a JSON list.

```markdown
<script input="text" value="reverse">
let str = "@input"
str.split("").reverse().join("")
</script>

<script input="number" value="1" min="0" max="1000000">
let i = @input
"Square of " + i + " = " + i * i
</script>

<script input="range" value="0" min="0" max="360" step="0.1">
let i = @input
"Sinus of " + i + " = " + Math.sin(i)
</script>

<script input="checkbox" value="true">
"@input"
</script>

<script input="radio" value="1" options="1|2|3|Hello World">
"Selected option: @input"
</script>

<script input="select" value="1" options="1|2|3|Hello World">
"Selected option: @input"
</script>

<script input="button">
"click me"
</script>

<script input="submit" default="click me">
Math.random()
</script>
```

`options` (`radio`/`select`, `|`-separated) and `default` (`submit`/`button` — the value shown before the first click) are LiaScript-specific, not standard HTML attributes. `text`/`number`/`range`/`radio`/`select`/`checkbox` execute immediately on load with their default `value`; `button` also executes on load and again on every click; `submit` does **not** execute on load — it shows its `default` text until clicked, and runs the script on every click.

**Connecting scripts via `output`/`input`** — give a script `output="channel-name"`, then reference its live, currently-displayed value from any other script (same slide) with `` @input(`channel-name`) `` (backticks required around the channel name):

```markdown
<script input="checkbox" value="true" output="P" default="true">
@input
</script>
AND
<script input="checkbox" value="false" output="Q" default="false">
@input
</script>
<script>
@input(`P`) && @input(`Q`)
</script>
```

Toggling either checkbox updates the combining script live. If two scripts reference each other's output (a cycle), give both a `default` value; without it the first calculation has nothing to read and fails with a `TypeError`.

**Internationalization API** — `format="..."` (`number`, `datetime`, `list`, `relativetime`, `pluralrules`) applies a `locale`-aware `Intl.*` formatter to the script's output, for display only (the `@input` value seen by connected scripts is unchanged). `format="number" locale="de-DE"` shows `1234.5` as `1.234,5`. The `Intl` options are passed as attributes and **must be written in lowercase**, e.g. `maximumfractiondigits="2"`, `currencydisplay="name"`. For `Intl.NumberFormat`'s `style` option use `localestyle`, because `style` is reserved for CSS:

```markdown
<script format="number" locale="de-DE" localestyle="currency" currency="EUR">1234.5</script>
```

This shows `1.234,50 €` (verified in 2.1).

**`LIA` global object** — `window.LIA` exposes a few helpers to scripts:

```js
LIA.fetch(url, options)   // like fetch(), but resolves URLs relative to the course
LIA.goto(5)               // jump to the slide with this index
LIA.gotoNext(); LIA.gotoPrevious()
LIA.settings              // read/change the user settings from JavaScript
LIA.debug = true          // log every script error to the browser console
LIA.focusOnMain = false   // don't move the focus to the main content on slide change
LIA.scrollUpOnMain = false// don't scroll to the top on slide change
```

`LIA.classroom` is a publish/subscribe interface for the live-presentation "Classroom" feature (peer-to-peer, active only while a classroom session is connected):

```js
LIA.classroom.connected                 // bool: is a classroom session active
LIA.classroom.on("connect", () => {})
LIA.classroom.on("disconnect", () => {})
LIA.classroom.publish("topic", payload)
const id = LIA.classroom.subscribe("topic", message => {})
LIA.classroom.unsubscribe(id)
```

`LIA.classroom.connected` is `false` outside a classroom session; the object always exists, so checking it never throws.
