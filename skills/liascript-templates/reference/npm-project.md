# Template as an npm Project (bundling a library)

When a JS library lives **only on npm** (no usable CDN/UMD build), needs to be **bundled with its
dependencies**, or you want a **self-contained template with a pinned version**, make the template a
real npm project: install the library, bundle a small entry point into `dist/index.js`, and load
that bundle from the header with `script: dist/index.js`. This is the build-time alternative to
loading a prebuilt CDN script.

> Real-world example: [LiaTemplates/Algebrite](https://github.com/LiaTemplates/Algebrite) bundles the
> npm-only `algebrite` CAS this way.

## Two distribution models

| Model | Build step? | Header |
|---|---|---|
| CDN / prebuilt | none | `script: https://cdn.../lib.min.js` |
| npm-bundled | `npm install` → `npm run build` | `script: dist/index.js` |

## Project layout
```
src/index.js      ← entry point: import the npm lib, attach what you need to window
dist/index.js     ← the bundle (COMMITTED — LiaScript loads it raw from the repo)
package.json
README.md         ← the template/course; header has `script: dist/index.js`
```

## `package.json`
Parcel is the bundler the LiaTemplates ecosystem uses (least config); esbuild/rollup/webpack work
too.
```json
{
  "name": "lia-mylib",
  "version": "0.1.0",
  "app": "dist/index.js",
  "scripts": { "build": "npx parcel build src/index.js" },
  "targets": { "app": {} },
  "devDependencies": {
    "mylib": "^1.0.0",
    "parcel": "^2.16.4"
  }
}
```
`"app": "dist/index.js"` together with `"targets": { "app": {} }` tells Parcel to emit a single,
fixed output filename — without it Parcel produces a content-hashed name and the `script:` line
can't reference a stable `dist/index.js`.

## `src/index.js` — expose globals the macros call
The bundle's only job is to put the library (and any helpers) on `window`, so macro `<script>`
blocks can reach it:
```js
// CommonJS
window.MyLib = require('mylib')

// or ESM
import MyLib from 'mylib'
window.MyLib = MyLib

// expose your own helpers too
window.myHelper = (input) => { /* ... */ }
```
Expose exactly what the macros reference — e.g. a `@MyLib.eval` macro that runs
`window.MyLib.run(\`@input\`)`.

## Build & setup
```bash
npm install        # pull deps into node_modules/
npm run build      # bundle src/index.js → dist/index.js
```
Re-run `npm run build` after any change to `src/` or after bumping the library version.

## Commit `dist/`, ignore the rest (important gotcha)
Unlike a normal npm package, the **bundle must be committed**: LiaScript fetches
`script: dist/index.js` *raw from the repository at runtime*, so an uncommitted `dist/` means the
template is broken for everyone importing it. Put `node_modules/` and `.parcel-cache/` in
`.gitignore`; do **not** ignore `dist/`.

## Versioning
Pin the npm dependency (`"mylib": "^1.0.0"`) so rebuilds are reproducible, and — per
Pattern 10 in `patterns.md` — offer consumers both a pinned
import URL (a tag/commit) and the `master` URL. Credit the bundled library in the header
`attribute:` field (see the skeleton in `SKILL.md`).

## File structure
```
README.md            ← the template IS a LiaScript course
src/
  index.js           ← bundler entry point
dist/
  index.js           ← the bundle (committed)
package.json
```
Every slide in README.md demonstrates one macro with a live example, then an "Implementation" slide at the end shows all macro definitions.
