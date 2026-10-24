# Classroom API for templates (`LIA.classroom`)

Checked against the LiaScript 2.5.0 source (`src/typescript/liascript/service/Sync.ts`, `sync/Base/db.ts`). The user documentation is the "Classroom API" section of the LiaScript docs course.

A LiaScript classroom synchronizes quizzes, surveys, code and the chat between all participants. `LIA.classroom` lets templates use the same connection for their own collaborative widgets: drawing together, markers on a map, votes, small games. The object always exists, also without a classroom, so a template works the same in a single browser and in a room.

| Part | Use it for | Stored | Since |
|---|---|---|---|
| `connected`, `on('connect' / 'disconnect')` | is there a classroom | — | 0.14.0 |
| `me`, `owner`, `mode`, `peers()`, `on('peers')` | who is in it, how it is configured | — | 2.5.0 |
| `publish()`, `subscribe()`, `unsubscribe()` | short messages: reactions, signals, cursor pings | not stored, a late subscriber only gets the last message of a topic | 0.14.0, sender since 2.5.0 |
| `layer(name)` | an own state per participant: strokes, votes, markers | locally in the browser and in the classroom | 2.5.0 |
| `array(name)`, `map(name)`, `text(name)` | one state everyone changes (experimental) | only in the classroom | 2.5.0 |

Pick `layer` whenever something has to be remembered. Pick pubsub only for things that may get lost.

## Compatibility checks

```js
const C = window.LIA && window.LIA.classroom
if (C && C.layer) { /* 2.5.0 or newer */ }
else if (C) { /* 0.14.0 – 2.4.0: only connected, on, publish, subscribe */ }
```

Up to 2.4.0 `on()` returns nothing, so guard the remover: `const off = C.on(…); if (typeof off === 'function') off()`. Show a short note in the widget when `layer` is missing, rather than failing silently (the CollaborativeDrawing template writes "This LiaScript version does not support LIA.classroom.layer.").

## Who is in the room (since 2.5.0)

```js
LIA.classroom.connected   // true once the room is synced
LIA.classroom.me          // { id, name, color, symbol, me: true, owner }, also without a classroom (name '')
LIA.classroom.owner       // am I the owner of the room
LIA.classroom.mode        // 'shared' | 'summary' | 'details', null without a classroom
LIA.classroom.peers()     // everybody in the room right now, including me; [] without a classroom

const off = LIA.classroom.on('peers', peers => { … })  // joined, left, renamed, new owner
LIA.classroom.on('connect', () => { … })
LIA.classroom.on('disconnect', () => { … })
off()                                                   // every on() returns a remover
```

- `on('peers')` is called at once with the current list, `on('connect')` at once if already connected. You do not need to check the state first. `peers` also fires on disconnect, with `[]`.
- `me.id` is the browser's `lia-token` from localStorage, the same id inside and outside a room. `color` and `symbol` are the color and emoji the person has in the chat, so a template can mark who did what without its own color scheme.
- `name` is the chat name of the peer, `''` if none was set. LiaScript hands it to templates in every mode. LiaScript itself shows quiz answers anonymously in Summary and with names in Details; check `mode` before showing names if the widget should behave the same.

## Publish & subscribe

```js
LIA.classroom.publish('MyTemplate:wave', '👋')
const id = LIA.classroom.subscribe('MyTemplate:wave', (message, from) => { … })
LIA.classroom.unsubscribe(id)
```

- **Always call `LIA.classroom.publish(…)` through the object.** LiaScript replaces the function on connect and back on disconnect. A reference taken earlier (`const pub = LIA.classroom.publish`) keeps the stub that only logs "not connected".
- Without a classroom `publish` drops the message with a console warning.
- `from` (since 2.5.0) is the sender as a person object. The sender's browser claims it, nobody verifies it. Messages from LiaScript before 2.5.0 arrive without `from`.
- **Own messages:** whether your own message comes back to your own `subscribe` depends on the backend. Edrys, Nostr, MQTT, Torrent, IPFS, Ably and PubNub echo it, GUN, PeerJS, SimplePeer and WebSocket do not. Update the own view directly after publishing and skip messages with `from && from.me`.
- In 2.5.0 the Ably and PubNub backends do not deliver messages from other peers to `subscribe`, only the own echo. The Local backend has no pubsub at all. Layers work on all backends; use them when the widget must work everywhere.
- A new subscriber gets the last message of the topic again, after 100 ms (late slides, revisits). That also holds for `0`, `false` and `""` since 2.5.0. The memory is cleared when the room changes; up to 2.4.0 a room change replayed the last message of the previous room.
- Messages must survive `JSON.stringify`.

## Layers (since 2.5.0)

Every participant writes into an own layer. It is stored locally, also without a classroom, synchronized when joining one, and stays with the participant after leaving, including what was done in the room.

```js
const layer = LIA.classroom.layer('MyTemplate:' + id)

const off = layer.on((layers, info) => {
  // layers = [{ id, name, me, editable, color, symbol, values: [...] }, ...]
  // info.remote: the own layer was changed by somebody else (the owner)
})

await layer.push({ x: 10, y: 20 })     // append to the own layer
const own = layer.get()                // a copy of the own values
await layer.set(own.slice(0, -1))      // replace the own layer: undo, erase, move
await layer.set(values, layers[i].id)  // owner only: replace another peer's layer
off()
```

**Who sees what** follows the classroom mode, like quiz and survey answers:

| Situation | `on()` gets |
|---|---|
| no classroom | the own layer (`name: ''`) |
| Shared | all layers |
| Summary, Details | the own layer; the owner gets all |
| after leaving | the own layer, including what was done in the room |

In Summary and Details the values are encrypted with the peer's key, which only the owner can unwrap.

**Rules that matter when writing a template:**

- **Values are frozen JSON copies.** Dates, Maps, functions and `undefined` do not survive (`undefined` is dropped). Values in `layers[i].values` and `get()` cannot be changed in place; copy before editing (`{ ...v }`, `structuredClone(v)`).
- **`push` and `set` return a promise** that resolves once the change is stored (and written into the room when connected) and rejects with the reason, e.g. `set(values, id)` without a connection or by a non-owner.
- **`get()` is always the own layer**, also for the owner. Read other layers from the `on` callback.
- **The owner changes others** with `set(values, id)`, but only layers that already exist in the room; `editable` tells which ones may be changed. The other peer receives the change in their own layer with `info.remote === true`, a good moment to clear an undo history.
- **`on` is called** once after the stored layer is loaded and then whenever any visible layer of that name changes. Redraw from the list each time instead of keeping a separate copy.
- **Cheap updates:** `set` only writes what differs from the room copy, so removing the last stroke of a drawing is one delete for the others. Many `push`es in a row (a stroke) are stored locally at most every 300 ms, and the last ones are saved on `pagehide`.
- **Offline changes:** when a participant reconnects, the newer copy of the own layer wins, the local one or the one the owner changed in the room meanwhile.
- **Names are shared by every template of a course.** Prefix them with the template: `'MyTemplate:' + id`. The same name in two macros on purpose lets them work on the same data.
- **`@uid` is a good name part.** It expands to `<slide>_<n>` (the n-th `@uid` on that slide), so it is the same for every participant of the same course version. Inserting a slide before it, or another `@uid` call before it on the slide, changes it, and the stored layer is no longer found. For stable names let the author pass a name as a parameter.
- **Where layers are stored:** in the LiaScript web app in IndexedDB, per course and major version, like quiz state. Only for `version: 1.0.0` and higher; with `0.x` (dev mode) and in the DevServer, web, SCORM and other exports a reload starts empty unless the participant is in a classroom. Do not test persistence with a `0.0.1` course. Templates themselves always stay below `1.0.0` (LiaTemplates convention, do not bump them), so test in a separate course with `version: 1.0.0` that imports the template.
- **Set `persistent: true`** in the header of a template that renders into the DOM (canvas, SVG). Otherwise the element is rebuilt when the slide is revisited, and the `on` callback writes into elements that no longer exist. Remove the callback with the returned function when a widget is torn down.
- A layer can be used from `@onload` before the course database is open; loading waits for it.

## Shared Yjs types (since 2.5.0, experimental)

```js
LIA.classroom.on('connect', () => {
  const list  = LIA.classroom.array('MyTemplate:list')  // Y.Array
  const dict  = LIA.classroom.map('MyTemplate:dict')    // Y.Map
  const notes = LIA.classroom.text('MyTemplate:notes')  // Y.Text
  list.observe(() => render(list.toArray()))
  list.push(['one more item'])
})
```

- `undefined` (plus a console warning) without a classroom. Every room has its own document, so request the types again after every `connect` and drop the old references on `disconnect`.
- Everyone reads and writes them in every mode: no authorship, no encryption per peer, no local copy. Saved classrooms keep them in their cache.
- The API is the plain [Yjs shared types API](https://docs.yjs.dev/api/shared-types).

## Example: one vote per participant

A layer with at most one value. Works alone (stored after a reload in a `1.0.0` course) and in a classroom (Shared: everyone sees all votes; Summary/Details: only the owner does).

```markdown
<!--
persistent: true

@vote: @vote_(@uid,@0)

@vote_
<div id="vote_@0" role="group" aria-label="@1"></div>
<div id="votes_@0" aria-live="polite"></div>
<script run-once>
;(function () {
  const C = window.LIA && window.LIA.classroom
  const box = document.getElementById('vote_@0')
  const out = document.getElementById('votes_@0')
  if (!C || !C.layer) {
    out.textContent = 'This LiaScript version cannot store votes.'
    return
  }
  const layer = C.layer('vote:@0')

  for (const choice of ['😀', '😐', '😟']) {
    const b = document.createElement('button')
    b.className = 'lia-btn lia-btn--outline'
    b.textContent = choice
    b.onclick = () => layer.set([choice]).catch(e => console.warn(e))
    box.appendChild(b)
  }

  const esc = s => String(s).replace(/[&<>"]/g, c => '&#' + c.charCodeAt(0) + ';')
  layer.on(layers => {
    out.innerHTML = layers
      .filter(l => l.values.length)
      .map(l => `<span style="color:${l.color}">${l.symbol} ${l.me ? 'you' : esc(l.name) || 'anonymous'}: ${l.values[0]}</span>`)
      .join('<br>') || 'no votes yet'
  })
})()
""
</script>
@end
-->

@vote(How do you feel today?)
```

Escape `name`: it is typed by other participants. A full drawing canvas with move, erase, undo, redo and an owner view, built only on layers, is the [CollaborativeDrawing](https://github.com/LiaTemplates/CollaborativeDrawing) template (layer version on `main`; versions before it used pubsub).
