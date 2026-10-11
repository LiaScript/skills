# Philosophy & Patterns

## Why LiaScript Exists

> "With LiaScript, we tried to implement an extended Markdown format that should enable everyone to create, share, adapt, translate or correct online courses without the need of being a web-developer. We believe that a language-based approach, instead of a tooling-centered one, provides more flexibility, freedom of creativity, and sustainability."

> "Everything has been woven around Markdown, so that the content can still be read and interpreted with any kind of editor or Markdown-interpreter."

### The Four Goals (verbatim)

- **Simplicity**: with a human-centered markup-language, anyone should be enabled to create and modify content.
- **Interactive**: the browser is the next operating systems and although content with LiaScript is developed within a "static" markup-language it should not be presented that way.
- **Extendability**: everything that is not part of LiaScript shall be embeddable and importable.
- **Durability**: platforms go down, the development of proprietary software/formats is discontinued, but LiaScript is not hosted on one platform (it can be hosted everywhere) and even without the LiaScript interpreter the content is still readable and interpretable with every editor; you could even print or engrave it on stone or clay. Furthermore, if you use some kind of versioning system (e.g. git) you can refer to any previous version of your course.

> "Imagine a world where everyone would have the same access to high quality educational content for free."

> "No further hosting is required, no further compilation step, the JavaScript interpreter of LiaScript does everything else directly within the browser at client-side."

## Best-Usage Patterns

### Choose the mode by pacing

`mode: Presentation` or `Slides` for content the audience follows at the author's pace (a lecture, a guided demo): reveals and narration happen click by click. `mode: Textbook` for longer, reference-style or self-paced content: nothing is gated, and `--{{n}}--` narration turns into visible text. Presentation and Slides differ only in where narration appears (hidden vs. speaker-notes panel). Build so that all three work — see `presentation-pattern.md`.

### Accessibility: give every visual cue a text equivalent

The official docs admit that "not all of the previous examples we have shown were perfect in the sense of accessibility … they might not be perfectly for people that require a screen-reader". Mitigate it:

- Write the question as a plain paragraph directly above each quiz; LiaScript uses it as the quiz's accessible label.
- For quizzes whose result is only visible as a checkmark or grid position (e.g. matrix quizzes), add `[[?]]` hints and a `***` solution block with the reasoning in words.
- Use `--{{n}}--` to say what is shown at that step, not a different remark. For young readers and language learners, put `{|>}{…}` read-aloud buttons into questions and quiz options (`quizzes-surveys.md`'s Reading quizzes aloud).
- Give images meaningful alt text; it is also what a plain Markdown viewer shows.

### Offline and durability: keep external dependencies minimal

Every `script:`, `link:` and `import:` entry is fetched before the course works, and a CDN URL is a single point of failure once a learner is offline or the host disappears. Use as few as possible, and prefer files you control: put them next to the course in the repository and reference them relatively.

### Match `narrator` to `language`

The two fields are independent; LiaScript does not derive one from the other. Pick a voice in the course language (`language: de` with `narrator: Deutsch Female`). Otherwise German text is read with an English voice, or the reverse.

### Pin `import:` for a stable course

Use a tagged or commit URL in `import:` once a course is finished (e.g. `.../Pyodide/0.3.5/README.md`), and `master`/`main` only while developing the template alongside the course. An unpinned import can change or break the course whenever the template's default branch changes. Templates usually offer both URLs (see the `liascript-templates` skill, Pattern 10).
