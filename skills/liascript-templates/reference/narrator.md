# Narrator Hook & Avatars

Templates can follow the narration (`--{{n}}--` read via TTS, or played as audio/video recordings) and show an **avatar** in the draggable video-comment overlay.

**Events** — `lia-narrator` on `window`, `e.detail` holds the current state plus the event:

| Field | Content |
|---|---|
| `type` | `start`, `stop`, `pause`, `resume`, `boundary`, `progress`, `media`, `error` |
| `status` | `idle`, `speaking`, `paused` |
| `source` | `tts`, `audio`, `video` (or `null`) |
| `id` | class of the comments, e.g. `lia-tts-3`; `null` for inline playback |
| `elements`, `text` | the comment elements that are read, and their text |
| `voice`, `lang`, `translated` | narrator voice, language, whether the course is read in a translation |
| `media` | the `<audio>`/`<video>` element that plays, else `null` |
| `charIndex`, `charLength` | word boundaries (`boundary`, TTS only), e.g. for lip sync or highlighting |
| `current`, `total` | seconds played (`progress`, recordings only) |
| `error` | message (`error`) |

`window.LIA.narrator.state` returns the same state at any time, `window.LIA.narrator.EVENT` is `"lia-narrator"`.

**Avatar** — `window.LIA.narrator.registerAvatar('tag-name')` registers a custom element (a valid name with a hyphen, else it is rejected with a console warning; `null` removes it). LiaScript renders it in the overlay for every animation step that has narration but **no video**; videos always win. The element gets `id="lia-tts-avatar"`, `data-voice` (the narrator), `data-step` and every `data-*` annotation of the step's comments, written in the course as `<!-- data-speaker="anna" -->` in front of `--{{n}}--`. LiaScript keeps the element across steps and only changes its attributes, so react in `attributeChangedCallback`. YouTube, Vimeo and other embedded videos in narration comments are played in the same overlay. They count as videos, so they replace the avatar too, and their events have `source: 'video'` with `media: null` (they are iframes, not `<video>` elements). The overlay is hidden when the user turns on "Hide video & avatar comments".

```markdown
<!--
@onload
if (!customElements.get('dog-avatar')) {
  customElements.define('dog-avatar', class extends HTMLElement {
    static get observedAttributes() { return ['data-speaker', 'data-step'] }

    connectedCallback() {
      this.innerHTML = '<div style="font-size: 6rem; text-align: center">🐶</div>'
      this.onNarrator = (e) => {
        this.style.opacity = e.detail.status === 'speaking' ? '1' : '0.6'
      }
      window.addEventListener(window.LIA.narrator.EVENT, this.onNarrator)
    }

    disconnectedCallback() {
      window.removeEventListener(window.LIA.narrator.EVENT, this.onNarrator)
    }

    attributeChangedCallback(name, old, value) {
      // e.g. switch the figure per data-speaker
    }
  })
  window.LIA.narrator.registerAvatar('dog-avatar')
}
@end
-->
```
