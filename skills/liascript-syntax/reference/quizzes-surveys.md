# Quizzes & Surveys

LiaScript quizzes and surveys share the same bracket-based syntax: quizzes have a defined correct answer and a "check"/"show solution" UI; surveys are the ungraded, anonymous counterpart — same brackets, but instead of a solution you provide options, and the UI is a single "Submit" button with no right/wrong feedback. Tasks (`- [ ]` check-lists, see `reference/syntax-core.md`) are the third stateful element and share the multi-block rules below.

Where state is stored depends on how the course is delivered: in the **LiaScript PWA** (`https://LiaScript.github.io/course/?...`) quiz/survey/task/code state is kept in the browser's IndexedDB — but only if the course's `version` is `>= 1.0.0`, otherwise (dev mode, default `0.0.1`) every reload clears it; in a **SCORM** export it is stored in the LMS; a plain **web** export ("Base" connector, also used by the devserver and editors) only stores user settings (mode, style, ...), not quiz state. In a live classroom session quizzes and surveys are additionally synced anonymously across connected peers (see Classroom Experience below).

## Quiz Types

Every quiz type is built from `[[ ]]` (checkbox-style) or `[( )]` (radio-style) bracket pairs. A quiz never "fails" — by default users can retry until solved or until they click "show solution"; only the number of trials is tracked. List markers (`- [[X]] ...`, also `+` or `*`) are optional for most types (see per-type notes below); everything also works with 4-space code indentation instead of a paragraph. Single-choice, multiple-choice, and hint options can carry whole Markdown blocks — see Options with Markdown Blocks below.

### Multiple-Choice

Checkboxes: `[[ ]]` unchecked, `[[X]]` or `[[x]]` marks a correct option (upper/lowercase both work). The user's checkboxes always start empty — the `X` only marks the answer key, revealed via "show solution" or matched when they check.

```markdown
- [[ ]] Empty means not checked
- [[X]] Uppercase X means checked
- [[x]] Lowercase x also means checked
```

### Single-Choice

Radio buttons: `[( )]` not selected, `[(X)]`/`[(x)]` marks the correct option. Multiple options may be marked correct — the user only has to select one of them.

```markdown
- [( )] Not selected
- [(X)] This one has to be selected
```

### Options with Markdown Blocks

Since LiaScript 2.0, an option is no longer limited to one line: like a normal Markdown list item, it can carry an **indented block** — further paragraphs, images, code blocks, lists, even a nested task list or quiz. This works for:

- Multiple-choice and single-choice options (`[[X]]`, `[(X)]`)
- Hints (`[[?]]`, see Tweaks)
- Survey vectors (`[[id]]`, `[(id)]`, see Survey Types)
- Tasks (`- [ ]`, see `reference/syntax-core.md`)

It does **not** work for Matrix rows, Text-Quizzes, or Selection-Quizzes — those stay single-line.

**The one rule: indent the block so it lines up with the text right after the marker.** The required indentation is therefore the marker's own width, including the list marker and the trailing space:

| Marker | Indentation of the attached block |
|---|---|
| `- [ ] ` (task) | 6 spaces |
| `- [[X]] ` / `- [(X)] ` / `- [[?]] ` | 8 spaces |
| `[[X]] ` / `[(X)] ` / `[[?]] ` (no list marker) | 6 spaces |
| `- [(good)] ` (survey identifier) | 11 spaces — depends on the identifier's length |

Separate the option line and its block with a blank line; blank lines between options are allowed too.

````markdown
**Which snippet defines a valid single-choice quiz?**

- [(X)] Using dashes together with parentheses

        ``` markdown
        - [(X)] Yes
        - [( )] No
        ```

- [( )] Using square brackets only

        ``` markdown
        - [X] Yes
        - [ ] No
        ```
````

Pitfalls (confirmed by the interpreter's parser tests):

- **Too little indentation ends the quiz.** After a blank line, text indented less than the marker width is *not* part of the option — it ends the option list and becomes an ordinary paragraph (swallowing any following options into it). This is stricter than before 2.0, so older courses with sloppy indentation may need fixing.
- **Every option needs a label on the marker line.** Put at least a short label after the marker and attach the block below it. A bare `[[X]]` alone on its line is not a multiple-choice option — it is parsed as a Text-Quiz whose solution is the literal string `X`.
- The 4-space-indented "code" form works as well: the block then lines up with the text after the marker *including* the 4 leading spaces.

### Matrix-Quiz

Combines multiple- and multiple single-choice "vector" quizzes into one grid. The first line is a header of column labels (brackets `[...]` or parentheses `(...)`, used purely to let you nest the other bracket type as literal text inside a label). Each following row starts with either `[...]`(checkboxes, multiple-choice row) or `(...)` (radio buttons, single-choice row), followed by the row's label text.

```markdown
- [[male (der)] (female [die]) [neuter (das)]]
- [    [X]           [ ]             [ ]     ]  Mann - German for man
- [    ( )           (X)             ( )     ]  Frau - German for woman
```

The column widths in the header and body rows don't have to line up character-for-character — extra spacing is cosmetic only.

**Header brackets are literal text, not per-column type selectors.** Checkbox-vs-radio is controlled entirely per data row: each row's own *leading* bracket sets the input type for that whole row (`[` = checkboxes, `(` = radio buttons), and every cell within a single data row must use the same bracket style — a row cannot mix `[ ]` and `( )` cells. There is no way to make one column checkboxes and another column radio buttons; the grid is always uniform-per-row. Mixing bracket styles in the header row, expecting it to assign a type per column, does not work — the header always renders as plain text labels, ignored for typing purposes:

```markdown
- [[checkbox col] (radio col) [another checkbox col]]
- [    [X]           [ ]             [ ]     ]  Row A
- [    ( )           (X)             ( )     ]  Row B
```

This renders exactly the same as a uniform `[[checkbox col] [radio col] [another checkbox col]]` header would: three plain-text column labels, Row A as three checkboxes (its leading bracket is `[`), Row B as three radio buttons (its leading bracket is `(`). The mixed bracket styles in the header have no effect on input type at all.

### Text-Quiz

A free-text input compared against a solution string. Does not support a starting dash; indentation is optional.

```markdown
What did the fish say when he swam into the wall?

    [[dam]]
```

### Selection-Quiz

A dropdown built from `|`-separated options; the correct option(s) are wrapped in parentheses. Options can contain inline Markdown/LaTeX. Does not support a starting dash.

```markdown
What is the derivative function of $f(x) = x^6$?

[[ $f'(x) = 6$ | ( $f'(x) = 6x^5$ ) | $f'(x) = 5x^6$ ]]
```

### Gap-Text Extreme

Embed Text-Quiz (`[[solution]]`) or Selection-Quiz (`[[a|(b)|c]]`) patterns directly inline inside any Markdown block — the input becomes a normal inline element, so it can be wrapped in `**bold**`, `_italic_`, `~strike~`, etc., and its width matches the length of the placeholder text.

```markdown
__I (learn) [[  have been learning  ]] English for seven years now.__
```

**Text outside `[[...]]` is ordinary literal prose — it has no special meaning.** The `(learn)` above is not a hint, base-form marker, or any other recognized annotation; it just renders as plain parenthesized text sitting next to the blank. LiaScript has no syntax for attaching a hint or base-form directly next to a `[[...]]` blank this way. (Real hints are a separate mechanism — see Tweaks → Hints below — written as `[[?]] hint text` lines attached to the quiz, not as inline parentheses next to the blank.)

To accept more than one correct answer for a blank, use Selection-Quiz syntax and wrap **every** acceptable option in parentheses (not just one) — this turns the blank into a dropdown rather than free text, but any of the parenthesized options is then marked correct:

```markdown
__I [[ (have been learning) | ('ve been learning) ]] English for seven years now.__
```

### Drag & Drop

Same as a Selection-Quiz, but written `[->[ ... ]]`: instead of a dropdown, the options are dragged into the blank. The correct option is wrapped in parentheses. Works as a standalone line and inline inside a gap text.

```markdown
The capital of France is [->[ Berlin | (Paris) | Madrid ]].
```

### Escaping inside `[[...]]`

Characters that are syntax inside a quiz can be escaped with a backslash: `\|` (not an option separator), `\(` `\)` (not a solution marker), `\[` `\]`, and `\@` (not a macro). E.g. `[[a\|b]]` is a Text-Quiz whose solution is `a|b`.

### Generic Quizzes

`[[!]]` (or `- [[!]]`) plus an associated `<script>` — for quiz logic that doesn't fit any built-in type. The script's last expression must evaluate to `true` to mark the quiz solved; any other value counts as unsolved. There's no visible input element unless your script/Markdown adds one. Inside the script, `@input` is `"true"` only when the user clicks the resolve/show-solution button — check for it if the script should behave differently in that case.

```markdown
[[!]]
<script>
  const random = Math.random()
  random < 0.2
</script>
```

## Tweaks (apply to every quiz type)

Order after the quiz itself: hints → `<script>` → `***` solution block. All three are optional.

- **Hints** — any number of `[[?]] hint text` lines (or `- [[?]] hint text` with dashes), revealed one at a time by the "show hint" button. A hint can span several blocks, indented like any other option (6 spaces after `[[?]] `, 8 after `- [[?]] ` — see Options with Markdown Blocks). A blank line between the last answer option and the first hint is tolerated.
- **Solution** — a block of arbitrary Markdown wrapped between two lines of `***` (3+ asterisks), shown after the quiz is solved or resolved. Any Markdown/media/code is allowed inside. Note `***` has a second, unrelated meaning as the animation/fragment-grouping marker — see `reference/interactivity.md`'s Multi-block animation and `reference/syntax-core.md`'s Horizontal rule note. **There must be zero blank lines between the quiz's last element (the `<script>` block, a `[[?]]` hint, or the answer brackets) and the opening `***`** — a blank line there breaks the parser's ability to recognize the delimiter: the `***` renders as a literal horizontal rule/text instead of being consumed as the solution-block marker, and the "solution" content displays unconditionally instead of being gated behind Check/Show-Solution. A blank line before the *closing* `***` is fine.
- **Associated script** — a `<script>` block placed directly after the quiz. Its last statement must evaluate to `true`/`false` to mark the quiz solved/unsolved. `@input` is substituted as raw text before the script runs, so how you quote it changes what you get:
  - **Text-Quiz** (a single `[[solution]]` block): wrap it in backticks/quotes (`` `@input` ``) to force it into a JS string — the user's raw unquoted text isn't valid JS on its own.
  - **Gap-Text** (several `[[...]]` inside one paragraph): leave it **unquoted**. LiaScript already substitutes a JS array literal, with text gaps quoted and selection gaps as indices, e.g. `["dam", 1]`. Wrapping it in backticks turns that array into a single string.
  - **Single-Choice / Selection-Quiz**: unquoted gives a number (e.g. `1`, `-1` while untouched); quoting still works, you just get the string `"1"`.
  - **Multiple-Choice**: unquoted gives a real array (e.g. `[1, 0, 1]`).
  - **Matrix-Quiz**: unquoted gives a nested array of arrays/numbers (e.g. `[[1, 0, 0], 1]`).

```markdown
What is $37 + 15$?

[[52]]
- [[?]] the solution is larger than 50
- [[?]] it is less than 55
- [[?]] it should be an even number
<script>
  let input = Number(`@input`)
  input === 52
</script>
***********************************************************************

52 is the correct solution.

***********************************************************************
```

Right vs. wrong — the only difference is the blank line before the opening `***`:

Wrong (blank line before the opening `***` breaks it):

```markdown
[[52]]
- [[?]] the solution is larger than 50

***********************************************************************
52 is the correct solution.
***********************************************************************
```

Right (no blank line before the opening `***`):

```markdown
[[52]]
- [[?]] the solution is larger than 50
***********************************************************************
52 is the correct solution.
***********************************************************************
```

## Quiz Settings (`data-*` attributes)

Settings go in an HTML attribute comment directly above the quiz (after the question paragraph). Several settings can be combined in one comment:

```markdown
You have only two trials, without a solution button ;-)

<!--
data-max-trials="2"
data-solution-button="off"
data-randomize
-->
- [( )] Wrong
- [(X)] Right
```

| Attribute | Effect |
|---|---|
| `data-randomize` | Shuffles the options (vector quizzes) or rows (matrix quizzes). The order is fixed per page load — a reload reshuffles, navigating away and back does not. |
| `data-max-trials="3"` | The quiz is resolved automatically after that many wrong trials. |
| `data-solution-button="off"` | Show/hide the "show solution" button: `on`/`off`, `true`/`false`, `enable`/`disable`. An integer shows it only after that many wrong trials (`0` = immediately, `1` = after the first wrong trial). Default: `on`. |
| `data-hint-button="2"` | Same values as `data-solution-button`, for the hint button — e.g. reveal hints only after two wrong trials. |
| `data-show-partial-solution` | For gap texts and matrix quizzes: highlights which gaps (or which matrix rows) are correct and which are wrong, instead of only "all right / wrong". |
| `data-score="2.5"` | Weight of this quiz in a SCORM export (integer or float, default `1`). Not visible in the course. |
| `data-text-solved="..."`, `data-text-failed="..."`, `data-text-resolved="..."` | Custom feedback texts (inline Markdown allowed) for solved, wrong, and resolved (after max trials / show solution). |

A generic or scripted quiz can also return an **array of booleans** instead of a single `true`/`false`; together with `data-show-partial-solution` this marks the individual parts of a compound quiz:

```markdown
<!-- data-show-partial-solution -->
The [[1]] and the [[2]] and the [[3]].
<script>
[true, false, true]
</script>
```

## Quiz Scripting Patterns

**Asynchronous checks** — end the script with `"LIA: wait"`, then report the result later with `send.lia("true")` (solved), or `send.lia("message", [], false)` to show an error message instead of marking the answer wrong:

```markdown
What is $37 + 15$?

[[52]]
<script>
setTimeout(function(){
  if (`@input` === "") {
    send.lia("You have to fill in something into the input field", [], false)
  } else {
    send.lia(`@input` === "52" ? "true" : "false")
  }
}, 1000)
"LIA: wait"
</script>
```

**Hiding the solution from the source** — compare against an encoded value, so the answer isn't readable in the raw Markdown. Wrap it in a macro to reuse it (`@0` is the first macro parameter):

```markdown
<!--
@customQuiz
[[...]]
<script>
"@0" == btoa(`@input`.trim().toLowerCase())
</script>
@end
-->

The solution is "solution":

@customQuiz(c29sdXRpb24=)
```

**Reacting to typical wrong answers** — give the quiz script an `output="topic"` and return the raw input on failure; other scripts read it with `` @input(`topic`) `` and re-run whenever it changes, e.g. to show targeted help:

```markdown
What is $37 + 15$?

[[52]]
<script output="quiz:37+15">
  if (`@input` == "52") { true } else { `@input` }
</script>

<script style="display: block">
if ("@input(`quiz:37+15`)" == "42") {
  send.liascript(`Maybe you forgot to carry the 1?`)
} else ""
</script>
```

**Accessibility** — write the question as an ordinary paragraph directly above the quiz: LiaScript uses it as the quiz's accessible label. If the question needs several blocks (a list, an image, ...), wrap them in one `<div>`; the quiz is then labelled with that element via `aria-labelledby`.

## Survey Types

Surveys reuse quiz syntax but without a right answer: brackets contain option identifiers/placeholders instead of a solution, and the UI shows a single "Submit" button (no check/hint/solution machinery). The `@input`/scripting mechanics from quizzes still apply, see Surveys and Scripting below.

### Text-Inputs

A placeholder of 3+ underscores becomes a text field. A single group of underscores → one-line text input; multiple whitespace-separated underscore groups on the same placeholder → a multi-line `textarea`, and the *number of groups sets the textarea's row count* (the length of each individual underscore run doesn't matter, only how many groups there are).

```markdown
**This is a one-liner, you can use commas to separate your inputs:**

    [[___]]

Please describe your opinion in a few sentences:

    [[___   ___   ___   ___]]
```

**A single `[[...]]` always produces exactly one input field**, no matter how many underscores, spaces, or underscore groups are inside it — everything between the double brackets is placeholder content for that one field, consumed as a whole. `[[___   ___   ___   ___]]` above does not create four separate one-line inputs; it has 4 underscore groups, so it becomes one multi-line `textarea` with 4 rows. To collect several separate free-text answers, write several `[[___]]` placeholders as separate blocks — put the label/question for each field directly above that field, not one combined question over several fields — each becomes its own independent field (with its own Submit button):

```markdown
Name

    [[___]]

Vorname

    [[___]]
```

### Single-Choice Vector

Like a single-choice quiz, but each option is `[(identifier)]` — a numeric or textual identifier rather than a checkmark. Numeric identifiers let the classroom view plot results as a distribution; non-numeric identifiers are shown as categorical values. Identifiers don't need to be sequential.

```markdown
Select one option:

    [(1)] option 1
    [(2)] option 2
    [(3)] option 3
    [(0)] option 0
```

### Multi-Choice Vector

Like a multiple-choice quiz, but each `[[identifier]]` carries a variable name/number instead of a checkmark. Prefix identifiers with a number (`[[1 red]]`) to get a continuous/numeric classroom representation instead of categorical.

```markdown
What are your favorite colors?

    [[red]]         is it red
    [[green]]       green
    [[blue]]        or blue
    [[dark purple]] last chance ;-)
```

### Survey Vector Blocks

Both vector types also accept list markers (`- [(1)] ...`) and, since LiaScript 2.0, an indented block per option — the same rule as for quizzes (see Options with Markdown Blocks above). The indentation depends on each option's own identifier: `- [(good)] ` is 11 characters wide, so its block is indented by 11 spaces. Options with identifiers of different lengths can be mixed; each block only has to line up with its own marker.

```markdown
How was the pacing of this chapter?

- [(fast)] Too fast

           I had to pause and re-read things to keep up.

- [(good)] Just right

           The speed felt natural, I could follow along easily.
```

### Single-Choice Matrix

A Matrix-Quiz header/body, but using `(identifier)` column labels in the header (no checkmarks) — each row becomes an independent single-choice (radio) group.

```markdown
What is your opinion about LiaScript?

    [(totally)(agree)(unsure)(maybe not)(disagree)]
    [                                             ] LiaScript is great?
    [                                             ] I would use it to make online **courses**?
    [                                             ] I would use it for online **surveys**?
```

### Multi-Choice Matrix

Same idea, but with `[identifier]` column labels — each row becomes an independent multiple-choice (checkbox) group.

```markdown
    [[1][2][3][4][5][6][7]]
    [                     ] question 1 ?
    [                     ] question 2 ?
    [                     ] question 3 ?
```

Matrix surveys also work with list markers, and the empty row brackets don't have to match the header's width. Prefix column labels with numbers (`(1 totally)`) to get a numeric summary in the classroom view:

```markdown
- [(1 totally)(2 agree)(3 unsure)(4 maybe not)(5 disagree)]
- [                ] LiaScript is great?
- [                ] I would use it to make online **courses**?
```

### Select and Drag & Drop Surveys

A Selection- or Drag-&-Drop-Quiz *without* any option in parentheses has no solution and therefore becomes a survey:

```markdown
Which color do you prefer?

[[ red | green | blue ]]

Which language do you use most?

[->[ Python | JavaScript | Java ]]
```

### Shuffling Survey Options

`<!-- data-randomize -->` above a survey shuffles vector options, matrix rows, and select/drag-&-drop options — the same attribute and behavior as for quizzes (see Quiz Settings). Added after LiaScript 2.0.1, so it needs a current interpreter.

```markdown
Which topic should we cover next?

<!-- data-randomize -->
- [(a)] Photosynthesis
- [(b)] Cell division
- [(c)] Genetics
```

### Surveys and Scripting

As with quizzes, attach a `<script>` after a survey to react to the submitted input or send it elsewhere. By default, an empty or whitespace-only input is treated as an error. The script's last statement controls the outcome: return `true` to accept, `send.lia("message", [], false)` to reject with a custom message, or plain `false` to reject silently. Use `alert(...)` to inspect `@input`'s shape while developing — `console.log` does not work here.

```markdown
Please enter some spaces at first:

[[___]]
<script>
  let input = `@input`.trim()

  if (input.length > 4) {
    true
  } else if (input.length == 0) {
    send.lia("Please enter some text", [], false)
  } else {
    send.lia("Please provide some meaningful input", [], false)
  }
</script>
```

### Classroom Experience

If you're presenting a course live in the browser, LiaScript can open a "classroom": connected viewers see the same anonymous, aggregated view of quiz and survey results (summary and details views, including quiz scores), plus collaborative code editing and a chat that itself interprets LiaScript syntax. Peer traffic is end-to-end encrypted.

The sync backend is chosen by the user when opening the classroom — the course author does not configure it in the Markdown. Available backends (LiaScript 2.0): Ably, Nostr, GUN, PubNub, WebSocket, PeerJS, SimplePeer, the Trystero-based P2PT/MQTT/Torrent/IPFS, Edrys, and a Local (offline) backend. Since Classrooms 2.0, rooms can be **persistent**: they are kept in a saved-rooms list with a local cache, and the GUN, Nostr, and Ably backends can optionally persist room state beyond the live session. Rooms can be named, password-protected, owned via an owner token, and locked against configuration changes. Without persistence, state only exists while at least one peer is connected.

The two Text-Input variants (see above) are aggregated differently in the classroom view: a one-line text input (single underscore group) is shown as a **word cloud**, with comma-separated terms across all submissions counted and sized by frequency — good for single-word/short-phrase answers. A `textarea` (multiple underscore groups) is shown as a list of each submitter's full response, one below another — good for longer free-text answers where you want to read full sentences, not aggregate keywords. Pick the field type with this in mind, not just for its row count.

- Disable classrooms for a course: add `classroom: disable` (or `classroom: false`) to the meta-header.
- Enable classrooms in a SCORM/IMS export (disabled by default there): add `classroom: enable` to the meta-header before exporting, and give the room a unique, quoted name so it doesn't collide with other courses.
