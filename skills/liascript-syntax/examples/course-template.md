<!--
author:   Your Name
email:    you@example.com
version:  1.0.0
language: en
narrator: UK English Female

comment:  Example course for primary school: animals and their sounds.
          Shows a narrated presentation, a quiz, a gap text and a survey
          in one file that works in all three view modes.

@correct: ⭐ Great!
@retry:   🔁 Try again!
-->

# Animals and Their Sounds

<!---
Every slide follows the same order: first the narration --{{n}}--, then
the block {{n}} it explains. In Textbook mode each explanation then stands
right before its picture or list, and the slide reads like a text.
Step 0 (--{{0}}-- and content without {{n}}) is visible immediately.
--->

                    --{{0}}--
Hello! In this course you will learn how animals talk. You will hear
animal sounds, solve small riddles and put words in the right place.

<!-- style="font-size: 4em; text-align: center" -->
🐶 🐮 🐓 🐱

                    --{{1}}--
On every page you can let the computer read the texts to you. Just press
the speaker button.

                      {{1}}
> **Tip:** The button {|>}{Listen!} reads a word aloud.


## The Dog

                    --{{0}}--
This is a dog. Many dogs live with people. They are good friends.

![A dog lying in the grass](https://commons.wikimedia.org/wiki/Special:FilePath/Golde33443.jpg?width=300 "A golden retriever")<!-- style="max-width: 280px" -->
The dog is a pet. It needs food, water and lots of exercise. It hears
well and smells much better than we do.

<!---
Image and text without a blank line between them: the image floats left
and the text flows beside it. With a blank line they are stacked.
--->

                    --{{1}}--
When a dog is happy or hears something strange, it barks. We write it
like this: Woof woof!

                      {{1}}
> **The dog barks:** {|>}{Woof woof!}

                    --{{2}}--
Dogs make even more sounds. Each sound tells us how the dog feels.

                      {{2}}
* A dog **growls** when it feels threatened.
* A dog **howls** when it is alone.
* A dog **pants** when it is hot.

<!-- --{{3}}--
Well done! Now you know the dog. Let's go on to the next page.
-->

<!---
Narration inside an HTML comment is only spoken, never shown, also not
in Textbook mode. Use it for transitions that would disturb the text.
Careful: a comment must never contain the characters that close a
comment, or it ends right there.
--->


## A Morning on the Farm

<!---
Picture sequence with {{0-1}}, {{1-2}}, {{2}}: in Presentation mode each
picture replaces the previous one. In Textbook mode all of them are shown
one below the other, each with its explanation before it, like a story.
--->

                    --{{0}}--
It is still dark on the farm. All the animals are asleep.

<!-- style="font-size: 4em; text-align: center" -->
                      {{0-1}}
🌙 🏠 💤

                    --{{1}}--
Then the sun rises. The rooster wakes up first and crows loudly:
Cock-a-doodle-doo!

<!-- style="font-size: 4em; text-align: center" -->
                      {{1-2}}
🌅 🐓 {|>}{Cock-a-doodle-doo!}

                    --{{2}}--
Now everybody is awake. The cow moos, the cat meows and the dog barks.

<!-- style="font-size: 4em; text-align: center" -->
                      {{2}}
☀️ 🐮 🐱 🐶


## Riddle: What Does This Animal Say?

<!---
The question is a paragraph directly above the quiz, so screen readers
use it as the quiz label. Every option has its own read-aloud button,
so learners can listen to each answer on its own. The feedback texts
come from the macros in the header.
--->

                    --{{0}}--
Look at the animal carefully. What does it say? If you don't know, press
the light bulb.

![A black and white cow](https://commons.wikimedia.org/wiki/Special:FilePath/Cow_female_black_white.jpg?width=300)<!-- style="max-width: 300px" -->

{|>}{What does this animal say?}

<!-- data-text-solved="@correct" data-text-failed="@retry" data-solution-button="off" -->
- [( )] {|>}{Woof woof!}
- [(X)] {|>}{Moo!}
- [( )] {|>}{Cock-a-doodle-doo!}
- [[?]] This animal gives us milk.
***************************************************************

This is a **cow**. It says "Moo", lives on the farm and gives us milk. 🥛

***************************************************************

<!---
No blank line between the hint [[?]] and the first *** line, otherwise
the solution is visible right away.
--->


## Gap Text: Who Says What?

<!---
Drag & drop: all words end up in one shared word bank below the text.
data-randomize shuffles them, otherwise they would appear in the right
order. A gap with a single word is automatically correct.
--->

                    --{{0}}--
Drag the words into the right gaps. You can also tap a gap first and then
a word.

<!-- data-randomize data-text-solved="@correct" data-text-failed="@retry" -->
The dog [->[barks]]. The cat [->[meows]]. The cow [->[moos]]. The rooster [->[crows]].


## How Did You Like It?

                    --{{0}}--
Finally, we would like to know how you liked the course. There is no
right or wrong here.

How did you like the course?

- [(good)] 😀 good
- [(okay)] 😐 okay
- [(bad)] 🙁 not so good

Which animal would you like to meet next?

[[___]]

<!---
The next link only works in the LiaScript DevServer with an AI agent
(see reference/tooling.md). The command in code after it keeps the line
useful everywhere else.
--->

[▶ Explain the animal sounds more simply](agent:tutor/explain?level=easy) `:explain easy`

                    --{{1}}--
Thank you for taking part! Goodbye and see you next time.

<!-- style="font-size: 4em; text-align: center" -->
                      {{1}}
👋
