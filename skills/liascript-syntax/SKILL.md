---
name: liascript-syntax
description: >
  LiaScript authoring reference — syntax for quizzes and surveys (incl. feedback
  texts, solution button, trials), effects, text-to-speech and read-aloud buttons,
  charts, executable code, styling, math; best-usage patterns; tooling (DevServer,
  exporter, `agent:` links for AI agents). Use when writing, editing, reviewing or
  debugging a LiaScript course — Markdown with an HTML-comment header like
  `<!-- author: … narrator: … -->` and `{{1}}`, `--{{1}}--`, `[[X]]`, `[(X)]` — or
  when asking what LiaScript can do ("change the quiz feedback text?", "hide the
  solution button", "read the answers aloud"). German triggers: "LiaScript-Kurs
  schreiben", "Quiz/Umfrage einbauen", "Rückmeldung beim Quiz ändern", "Lösung
  ausblenden", "Antworten vorlesen lassen", "Agenten-Link im Kurs". For reusable
  templates/macros see template-development; for colors, fonts, themes see
  liascript-theming.
license: CC0-1.0
---

# LiaScript

LiaScript turns plain Markdown into interactive, offline-capable online courses, rendered entirely in the browser — no server, no build step. A course is always a normal `.md` file: it must stay readable in any editor or Markdown viewer, so write correct Markdown first and LiaScript second. For the philosophy and design patterns (mode choice, accessibility, offline use) see `reference/philosophy-patterns.md`.

## Navigation — read the file that matches the task

| File | Covers | Read when... |
|---|---|---|
| `reference/syntax-core.md` | Meta-header, document structuring, paragraph/list parsing rules, text formatting & escapes, media, lists/task lists/blockquotes/alerts/tables/code/HTML blocks, custom styling, comments, footnotes, math & formulas | Writing or reviewing general course content/structure |
| `reference/quizzes-surveys.md` | All quiz types incl. drag & drop word banks and matching tables, generic quizzes, options/hints with multi-line Markdown blocks (2.0), quiz settings (trials, solution/hint buttons, custom feedback texts per quiz, course-wide or per wrong answer), reading quizzes aloud, quiz scripting, surveys and their settings, classroom mode, where state is stored | Adding or debugging any graded or ungraded question, or deciding whether a quiz behavior is possible |
| `reference/interactivity.md` | Effects (animations; TTS narration incl. voices per course/slide/comment, rate/pitch, translation control; playback buttons; optional audio/video comments), interactive code blocks, the `send`/JS API, script attributes and input widgets, defining/calling macros (template *authoring* — see the `template-development` skill) | Making content interactive, executable, narrated, or animated |
| `reference/presentation-pattern.md` | How to build slides that work in all three modes: narration *before* its block so Textbook mode reads as text, step 0, grouped steps, picture sequences with `{{n-m}}`, spoken-only remarks, what each mode shows | Building any course with animations or narration, especially lecture/slide-style content that must also read well as a text |
| `reference/visuals.md` | Table→chart plot types, ASCII-art, SVG, chart fine-tuning | Adding a diagram, chart, or ASCII visualization |
| `reference/tooling.md` | `liascript-devserver`, the DevServer's agent bridge (`agent:` links, MCP tools, chat), `@liascript/exporter` (CLI + export formats), editors, publishing/hosting workflow | Running, exporting, publishing, or setting up a course project; connecting a course to an AI agent |
| `reference/philosophy-patterns.md` | Philosophy quotes + best-practice patterns (mode selection, accessibility, offline-first design, narrator/TTS usage, versioned imports) | Making a design/style choice, not just a syntax lookup |
| `examples/course-template.md` | Complete, tested example course (primary school, "Animals and Their Sounds"): narrated slides following the presentation pattern, picture sequence, quiz with read-aloud options and custom feedback, drag & drop word bank, survey, agent link — with authoring notes explaining each decision | Starting a new course, or as a model for structure and narration |

## Top pitfalls

These fail silently — the course renders, just wrong. Check them first when reviewing or debugging:

1. **Every heading `#`–`######` starts a new slide.** For headings inside a slide use Setext underlines or wrap them in `<section>` (`syntax-core.md`, Structuring).
2. **Emphasis must stay on one physical line.** A hard line break inside `**…**` leaks asterisks (`syntax-core.md`, Text Formatting).
3. **A line starting with `- `, `1. `, `>` or `2019. ` inside a paragraph starts a new block** (`syntax-core.md`, Structuring).
4. **No blank line between a quiz and its opening `***` solution line**, or the solution is always visible (`quizzes-surveys.md`, Tweaks).
5. **Quiz options with blocks (2.0) need exact indentation**: 8 spaces after `- [[X]] `. Too little ends the quiz (`quizzes-surveys.md`, Options with Markdown Blocks).
6. **`--{{n}}--` never makes anything appear**; content that should appear needs `{{n}}` (`interactivity.md`, Effects).
7. **Separate HTML comments with a blank line.** Two stacked comments merge, and the attribute comment (chart, style, quiz settings) is lost (`syntax-core.md`, Comments).
8. **Image + text side by side needs no blank line** between them (`syntax-core.md`, Text Formatting).
9. **Attribute names up to LiaScript 2.1.2 are case-sensitive**: `data-readonly`, `localestyle` and other `Intl` options only work in lowercase, `data-showGutter` only in camelCase. After 2.1.2 any spelling works (`interactivity.md`).
10. **External CSS/JS is not bundled**: animate.css classes, fonts and libraries need a `link:`/`script:` entry first (`interactivity.md`, Effects).
11. **Raw `<svg>` must not be fenced**, and an `ascii` fence must start at the left margin (`visuals.md`).
12. **`version: 0.x` never stores quiz state**; use `>= 1.0.0` for a published course (`syntax-core.md`, Meta-Header).
13. **Use `<!--- … --->` for authoring notes**, LiaScript ignores them; a plain `<!-- -->` is read as attributes or hidden narration. Inside a note never write `-->`: the note ends at the first `-->`, and the rest shows up as text (`syntax-core.md`, Comments).
14. **Narration goes before its block**, not collected at the top or bottom of a slide; otherwise Textbook mode shows all pictures first and all explanations after (`presentation-pattern.md`).
15. **Before saying "LiaScript can't do that"**, check the reference — many quiz behaviors are configurable (feedback texts, solution button, trials, read-aloud).

## Can LiaScript do this?

| Request | Answer |
|---|---|
| Change a quiz's "correct"/"wrong" text | Yes: `data-text-solved`, `data-text-failed`, `data-text-resolved`; course-wide via header macros (`quizzes-surveys.md`) |
| Different feedback per wrong answer | Yes: quiz script with `throw new Error("…")` |
| Hide "show solution" / show it after n tries | Yes: `data-solution-button="off"` / `="3"` |
| Limit attempts | Yes: `data-max-trials="2"` |
| Read questions and answers aloud | Yes: a playback button `{!>}{…}` (same as `{\|>}{…}`) in the question and in every option |
| Word bank / matching exercise | Yes: drag & drop gaps `[->[…]]` in a paragraph or table, with `data-randomize` |
| Let learners change a submitted survey | Yes: `data-updates-allowed` |
| Change survey "thank you"/submit texts | No, only via CSS |
| Disable the quiz "check" button | No |
| Narrated slides that also read as a text | Yes: `presentation-pattern.md`, `examples/course-template.md` |
| Run code (JS, Python, SQL, …) | Yes: JS directly; other languages via templates (`template-development` skill) |
| Talk to an AI agent from the course | Yes, in the DevServer: `agent:` links (`tooling.md`) |

## Cheatsheet

Minimal meta-header (every course needs one, as an HTML comment at the top of the file):
```markdown
<!--
author:   Your Name
email:    you@example.com
version:  0.0.1
language: en
narrator: UK English Female
-->
```

Slides are headings — every heading level (`#` … `######`) starts a new slide; deeper levels nest in the table of contents.

Single-choice quiz:
```markdown
- [( )] Wrong answer
- [(X)] Right answer
```

Multiple-choice quiz:
```markdown
- [[X]] Correct, checked
- [[ ]] Incorrect, left unchecked
```

Quiz settings go in an attribute comment directly above the quiz. Feedback texts, the solution button and trials are all configurable. Before telling a user that something is impossible, check Quiz Settings in `reference/quizzes-surveys.md`:
```markdown
<!-- data-text-solved="⭐ Super!" data-text-failed="🔁 Nochmal!" data-solution-button="off" -->
- [( )] {|>}{grün}
- [(X)] {|>}{blau}
```

Options, hints, and tasks can carry whole Markdown blocks (LiaScript ≥ 2.0) — indent the block to line up with the text after the marker: 8 spaces for `- [[X]] `/`- [(X)] `, 6 for a task's `- [ ] `. Too little indentation silently ends the quiz:
````markdown
- [[X]] Valid syntax

        ``` markdown
        - [[X]] Yes
        ```

- [[ ]] Invalid syntax

        ``` markdown
        - (X) Yes
        ```
````

Executable code block (attach a `<script>@input</script>` tag right below the fence to make a JS block runnable, with output shown in a terminal panel):
````markdown
``` js
1 + 1
```
<script>@input</script>
````

For anything beyond this — full quiz type list, effects, charts, macros, publishing — go to the matching `reference/` file above rather than guessing.
