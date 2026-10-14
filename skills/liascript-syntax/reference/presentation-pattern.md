# Presentation Pattern

One LiaScript source should work as a narrated presentation *and* read as a well-structured text. The official docs: "You need to balance these features properly so that your course can be read in Textbook mode and used for presentations and more." The idea: like a slide deck, every new point that appears is also explained by the narrator — and in Textbook mode, where everything is shown at once, the same source reads as a text in which explanation, picture, explanation, list follow each other naturally.

A complete, tested example course in this style: `examples/course-template.md`.

## What each mode shows

| Mode | `{{n}}` blocks | `--{{n}}--` narration |
|---|---|---|
| Textbook | all visible at once, each with a step-number badge | shown in place as ordinary paragraphs |
| Presentation | revealed click by click | spoken, not shown |
| Slides | revealed click by click | spoken and shown as speaker notes: a side panel on wide screens, below the slide on narrower ones |

`mode:` in the header only sets the default; learners can switch. So every slide must work in all three.

## The core rule: narration *before* its block

Write each step as a pair: first the `--{{n}}--` paragraph that explains, then the `{{n}}` block it explains.

```markdown
## The Dog

                    --{{0}}--
This is a dog. Many dogs live with people.

![A dog](img/dog.jpg)

                    --{{1}}--
When a dog is happy, it barks. We write it like this: Woof woof!

                      {{1}}
> **The dog barks:** Woof woof!

                    --{{2}}--
Dogs make even more sounds.

                      {{2}}
* A dog **growls** when it feels threatened.
* A dog **howls** when it is alone.
```

- **Presentation/Slides:** a click reveals the block and the narrator explains it at the same moment.
- **Textbook:** each explanation stands directly before its picture, quote or list, like an introducing sentence. The result is a normal text (explanation → image → explanation → quote → explanation → list), not a page with all explanations piled up at the top or bottom.

Never collect the narration of a slide in one place (all `--{{n}}--` at the end, or all at the start). In Presentation mode nobody notices, but in Textbook mode the page falls apart into a list of visuals followed by a wall of text.

## Step 0: the static frame

Content without any `{{n}}` marker is visible immediately in every mode. Start a slide with `--{{0}}--` followed by ungated content (heading text, a picture): the narrator introduces the slide as soon as it opens, and in Textbook mode this is the opening paragraph.

## Several blocks under one step

To reveal several blocks together (a bold label, an image, a list), wrap them in a `***` block (or `<section>`). Put the narration *inside*, after the label, so Textbook mode reads label → explanation → content:

```markdown
                      {{1}}
************************************************************

**LiaScript-DevServer:**

                    --{{1}}--
If you use another editor, you can run a local development server.
It updates your course in the browser on every save.

![Screencast of the dev server](img/devserver.gif)

************************************************************
```

## Sequences with `{{n-m}}`

`{{n-m}}` shows a block from step `n` and hides it again at step `m`. Use it for a picture sequence where each picture replaces the previous one, e.g. screenshots of a workflow or the stages of a story:

```markdown
                    --{{0}}--
Click the share button in the top right corner.

          {{0-1}}
![Share menu](img/step-1.png)

                    --{{1}}--
This opens the overview. Choose a backend.

          {{1-2}}
![Overview](img/step-2.png)

                    --{{2}}--
Enter a room name and connect.

          {{2}}
![Form](img/step-3.png)
```

In Presentation mode exactly one picture is visible at a time. In Textbook mode all pictures appear one below the other, each preceded by its explanation — a step-by-step guide. Only use `{{n-m}}` for content that still makes sense when every stage is shown together; never to "correct" something shown earlier, because Textbook mode shows both versions.

## Narration that does not belong in the text

Some remarks only make sense spoken: transitions ("Now let's look at…"), praise, "click next". Put them in an HTML comment — spoken in Presentation/Slides, never shown, also not in Textbook mode. It still counts as a step:

```markdown
<!-- --{{3}}--
Well done! Now you know the dog. Let's go on to the next page.
-->
```

Write all visible narration as full sentences that also work as reading text. A `--{{n}}--` without a matching `{{n}}` adds a step where only speech happens; use it deliberately, never as a substitute for `{{n}}` when something should appear.

## Speakers and avatars

Since LiaScript 2.2.0 a template can show a **narrator avatar**, an animated figure in the video-comment overlay, for every step that has narration but no video. An attribute comment in front of a narration marker passes extra information to it, e.g. who speaks:

```markdown
                    <!-- data-speaker="anna" data-mood="happy" -->
                    --{{1}}--
When a dog is happy, it barks.
```

Every `data-*` annotation of the step's comments reaches the avatar as an attribute, together with `data-voice` and `data-step`. Without an avatar template the annotations have no visible effect, so they are safe to write. Video comments always take precedence, and the setting "Hide video & avatar comments" hides avatars too. Building such an avatar is template work (`liascript-templates` skill, Narrator hook).

## Source layout

The official docs indent narration markers and block markers far to the right (narration about 20 spaces, block markers 2 spaces further). Plain Markdown viewers show them as small code lines; in the source they stand out from the content, and the pairing is easy to see. Indentation of 4+ spaces does not change the meaning in LiaScript.

## Checklist

- [ ] Every new point that appears has narration, placed directly **before** its `{{n}}` block (or inside a `***` group after its label).
- [ ] The slide starts with `--{{0}}--` and ungated content.
- [ ] Spoken-only remarks are hidden in `<!-- --{{n}}-- … -->`.
- [ ] `{{n-m}}` only for sequences whose stages all make sense together.
- [ ] `narrator:` matches `language:` (see `philosophy-patterns.md`).
- [ ] Previewed in Textbook (does it read like a text?), Presentation (does each click show and explain one thing?) and Slides.
