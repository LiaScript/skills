---
name: liascript-syntax
description: >
  Use when writing, editing, reviewing or debugging a LiaScript course — Markdown
  with an HTML-comment header like `<!-- author: … narrator: … -->` and syntax such
  as `{{1}}`, `--{{1}}--`, `[[X]]`, `[(X)]` — or when someone asks what LiaScript
  can do: quizzes and surveys ("change the quiz feedback text", "hide the solution
  button", limit trials), animations, narration and read-aloud buttons, charts,
  executable code, math, DevServer, `agent:` links. German triggers:
  "LiaScript-Kurs schreiben", "Quiz/Umfrage einbauen", "Rückmeldung beim Quiz
  ändern", "Lösung ausblenden", "Antworten vorlesen lassen", "Agenten-Link im
  Kurs". For macro templates use liascript-templates, for colors, fonts and themes
  liascript-theming, for drawing ```ascii diagrams liascript-asciiart.
license: CC0-1.0
---

# LiaScript

LiaScript turns plain Markdown into interactive, offline-capable online courses, rendered entirely in the browser — no server, no build step. A course is always a normal `.md` file: it must stay readable in any editor or Markdown viewer, so write correct Markdown first and LiaScript second.

## Navigation — read the file that matches the task

| File | Covers | Read when... |
|---|---|---|
| `reference/syntax-core.md` | Meta-header, slides and structure, paragraph/list parsing rules, text formatting and escapes, media, lists/tables/code/HTML blocks, custom styling, comments, footnotes, math, links to slides | Writing or reviewing general course content |
| `reference/quizzes-surveys.md` | All quiz types incl. drag & drop word banks and matching tables, options with Markdown blocks, quiz settings (trials, solution/hint buttons, feedback texts), reading quizzes aloud, quiz scripting, surveys, classroom mode, where state is stored | Any graded or ungraded question, or deciding whether a quiz behavior is possible |
| `reference/interactivity.md` | Effects (animations, narration, voices, playback buttons, audio/video comments), executable code blocks, the `send`/JS API, script attributes and input widgets, calling macros | Making content interactive, executable, narrated or animated |
| `reference/presentation-pattern.md` | Slides that work in all three modes: narration *before* its block, step 0, grouped steps, picture sequences with `{{n-m}}`, spoken-only remarks | Any course with animations or narration, especially slides that must also read well as a text |
| `reference/visuals.md` | Table→chart, ASCII-art syntax, SVG, chart fine-tuning | Adding a chart or diagram |
| `reference/tooling.md` | `liascript-devserver`, `agent:` links and the MCP bridge, `@liascript/exporter` overview, editors, publishing and hosting | Running, exporting or publishing a course; connecting it to an AI agent |
| `reference/philosophy-patterns.md` | Philosophy and best-practice patterns: mode choice, accessibility, offline use, narrator voice, pinned imports | A design choice, not a syntax lookup |
| `examples/course-template.md` | Complete tested course: narrated slides, picture sequence, read-aloud quiz with custom feedback, word bank, survey, agent link, with authoring notes | Starting a new course, or as a model for structure and narration |

## Top pitfalls

These fail silently — the course renders, just wrong. Check them first when reviewing or debugging:

1. **Every heading `#`–`######` starts a new slide.** For headings inside a slide use Setext underlines or wrap them in `<section>` (`syntax-core.md`, Structuring).
2. **Emphasis must stay on one physical line.** A hard line break inside `**…**` leaks asterisks (`syntax-core.md`, Text Formatting).
3. **A line starting with `- `, `1. `, `>` or `2019. ` inside a paragraph starts a new block** (`syntax-core.md`, Structuring).
4. **No blank line between a quiz and its opening `***` solution line**, or the solution is always visible (`quizzes-surveys.md`, Tweaks).
5. **Quiz options with blocks need exact indentation**: 8 spaces after `- [[X]] `/`- [(X)] `, 6 after a task's `- [ ] `. Too little ends the quiz (`quizzes-surveys.md`, Options with Markdown Blocks).
6. **A quiz's attribute comment goes between question and options**, directly above the first option, no blank line. Above the question it sets attributes on the paragraph and the quiz ignores it (`quizzes-surveys.md`, Where the comment goes).
7. **The "show solution" button is on unless switched off**: `data-max-trials` alone does not hide it. Self-checks, young learners and free-text quizzes need `data-solution-button="off"` (`quizzes-surveys.md`, Quiz Settings).
8. **`--{{n}}--` never makes anything appear**; content that should appear needs `{{n}}` (`interactivity.md`, Effects).
9. **Narration goes before its block**, not collected at the top or bottom of a slide; otherwise Textbook mode shows all pictures first and all explanations after (`presentation-pattern.md`).
10. **Separate HTML comments with a blank line.** Two stacked comments merge, and the attribute comment (chart, style, quiz settings) is lost (`syntax-core.md`, Comments).
11. **Use `<!--- … --->` for authoring notes**, LiaScript ignores them; a plain `<!-- -->` is read as attributes or hidden narration. Inside a note never write `-->`: the note ends there and the rest shows up as text (`syntax-core.md`, Comments).
12. **Image + text side by side needs no blank line** between them (`syntax-core.md`, Text Formatting).
13. **External CSS/JS is not bundled**: animate.css classes, fonts and libraries need a `link:`/`script:` entry first (`interactivity.md`, Effects).
14. **Raw `<svg>` must not be fenced**, and an `ascii` fence must start at the left margin (`visuals.md`).
15. **A table without enough numeric columns gets no chart**, not even the toggle; truth tables (only 0/1) and single rows with zeros stay tables too. Force a chart with `data-type` (`visuals.md`, How the type is guessed).
16. **`version: 0.x` never stores quiz state**; use `>= 1.0.0` for a published course (`syntax-core.md`, Meta-Header).
17. **Link to a heading anchor, not a slide number**: `#5` breaks when a slide is inserted. `## 3. Why do leaves fall?` → `#3.-why-do-leaves-fall?`; equal headings share the anchor of the first, and an unknown anchor silently does nothing (`syntax-core.md`, Links to slides).
18. **Name every `<script input=…>` with `aria-label`**, else a screen reader only hears "slider" or "checkbox" (`interactivity.md`, Naming inputs).

## Can LiaScript do this?

Many behaviors are configurable. Check this table and the matching reference before telling a user "LiaScript can't do that".

| Request | Answer |
|---|---|
| Change a quiz's "correct"/"wrong" text | Yes: `data-text-solved`, `data-text-failed`, `data-text-resolved`; course-wide via header macros (`quizzes-surveys.md`) |
| Different feedback per wrong answer | Yes: quiz script with `throw new Error("…")` |
| Hide "show solution" / show it after n tries | Yes: `data-solution-button="off"` / `="3"` |
| Limit attempts | Yes: `data-max-trials="2"` |
| Read questions and answers aloud | Yes: a playback button `{!>}{…}` (same as `{\|>}{…}`) in the question and in every option |
| Word bank / matching exercise | Yes: drag & drop gaps `[->[…]]` in a paragraph or table, with `data-randomize` |
| Let learners change a submitted survey | Yes: `data-updates-allowed` |
| Explain the answer after a survey | Yes: a `***` solution block below the survey appears after submitting |
| Change survey "thank you"/submit texts | No, only via CSS |
| Disable the quiz "check" button | No |
| Word cloud | Of survey answers: one-line text survey in the classroom. From a table: `data-type="wordcloud"` (`visuals.md`) |
| Read formulas aloud / own wording for a formula | Automatic in German and English; own text via `$…$<!-- aria-label="…" -->` (`syntax-core.md`, Math) |
| YouTube/Vimeo video as narration | Yes: `!?[⏯](youtube-url&start=60&end=75)` in a `--{{n}}--` comment (`interactivity.md`) |
| Learners take media offline | Yes, the learner chooses "Download media for offline use"; streams like YouTube are skipped (`tooling.md`) |
| Narrated slides that also read as a text | Yes: `presentation-pattern.md`, `examples/course-template.md` |
| Run code (JS, Python, SQL, …) | JS directly; other languages via templates (`liascript-templates` skill) |
| Animated speaker/avatar for the narration | Via a template: `LIA.narrator.registerAvatar` (`liascript-templates` skill); per-step `data-*` annotations (`presentation-pattern.md`) |
| Talk to an AI agent from the course | Yes, in the DevServer: `agent:` links (`tooling.md`) |
| Draw, vote or place markers together in a classroom | Via a template on `LIA.classroom.layer`, e.g. [CollaborativeDrawing](https://github.com/LiaTemplates/CollaborativeDrawing) (`liascript-templates` skill) |

## Cheatsheet

Meta-header — every course starts with one:
```markdown
<!--
author:   Your Name
email:    you@example.com
version:  0.0.1
language: en
narrator: UK English Female
-->
```

Quiz: one list item per option, `[( )]`/`[(X)]` for single choice, `[[ ]]`/`[[X]]` for multiple choice. Settings go in the attribute comment between question and options:
```markdown
Welche Farbe hat der Himmel?

<!-- data-text-solved="⭐ Super!" data-text-failed="🔁 Nochmal!" data-solution-button="off" -->
- [( )] {|>}{grün}
- [(X)] {|>}{blau}
```

Link to another slide by its heading anchor: `[see the summary](#summary)`.

Input widget, named for screen readers:
```markdown
<script input="range" min="0" max="100" value="50" aria-label="volume">
"Volume: @input %"
</script>
```

Executable JS block — the `<script>@input</script>` line right below the fence adds a Run button and a terminal:
````markdown
``` js
1 + 1
```
<script>@input</script>
````

For anything beyond this, open the matching `reference/` file instead of guessing.
