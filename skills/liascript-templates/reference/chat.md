# Templates in LiaScript/Chat

`@liascript/chat` (`<lia-chat>`) renders every chat message as a LiaScript section, so templates work there too. What changes for a template:
- The **header of any message** (`import:`, `script:`, `link:`, macros, `@onload`, `@style`) applies to the whole chat; the host can also load templates without a visible message via `chat.define({ import: [...], script: [...], link: [...], header: '…' })`. Messages are buffered until the templates are loaded. Relative template URLs resolve against the host page (`base`).
- Scripts run like on a slide, so `@input` and `"LIA: wait"` work as usual.
- `output="name"` / `` @input(`name`) `` are scoped to their message, but **element ids are not**: the same id in two messages refers to the first one. Never render fixed ids from a macro, use `@uid` (Pattern 2) or return the element as script output (`"HTML: …"`).
- `send.register`/`send.dispatch` names are global across all messages; include a parameter or `@uid` in the name when a widget can appear in several messages.
- `agent:` links are reported to the host as an `agent` event instead of being opened.
