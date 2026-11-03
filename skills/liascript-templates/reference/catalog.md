# Existing templates

Repositories tagged with the GitHub topic `liascript-template` (snapshot 2026-11, year = last push). Before building a new template, check whether one of these already does the job. If it does, point the user to it; its `README.md` shows the `import:` line and the macros. If it covers only part of the request, propose a contribution to that repository or a small extra template that the course imports alongside it.

New templates appear all the time, so also search live:

```bash
gh api -X GET search/repositories -f q='topic:liascript-template' -f per_page=100 \
  --jq '.items[] | "\(.html_url)  \(.description)"'
# without gh:
curl -s 'https://api.github.com/search/repositories?q=topic:liascript-template&per_page=100'
```

## Programming languages and code execution

| Repository | What it does |
|---|---|
| LiaTemplates/Pyodide | Python in the browser (Pyodide), 2026 |
| LiaTemplates/Skulpt | Python tutorials with Skulpt, 2026 |
| LiaTemplates/PyScript | PyScript, 2022 |
| LiaTemplates/BiwaScheme | Scheme interpreter, 2025 |
| LiaTemplates/Tau-Prolog | Prolog (Tau-Prolog), 2026 |
| LiaTemplates/Curiosity-Prolog | Prolog (curiosity-driven), 2019 |
| LiaTemplates/JSCPP | C++ interpreter JSCPP, 2019 |
| LiaTemplates/Lua | Lua interpreter and VM, 2019 |
| LiaTemplates/qalb | Arabic Lisp dialect, 2026 |
| LiaTemplates/ProcessingJS | Processing.js sketches, 2020 |
| LiaTemplates/p5js | p5.js sketches, 2021 |
| LiaTemplates/WebDev | HTML/CSS/JS web development, 2019 |
| LiaTemplates/Algebrite | Computer algebra system (CAS), 2026 |
| LiaScript/CodeRunner | Server that runs code snippets in many languages, 2026 |
| LiaTemplates/BlocklyCode | Blockly blocks synced with Python/JS code, turtle graphics, step mode, 2026 |
| jh-488/lia-blockly | Python ↔ Blockly blocks, 2026 |
| LiaTemplates/ScratchBlocks | Scratch 3 blocks and stage in code blocks, 2026 |
| LiaTemplates/ExplainGit | Interactive git visualisation, 2020 |

## Databases and queries

| Repository | What it does |
|---|---|
| LiaTemplates/SQLite | SQLite via sql.js: create, query, import, export, 2025 |
| LiaTemplates/PGlite | PostgreSQL (PGlite), 2026 |
| LiaTemplates/DuckDB | DuckDB, 2026 |
| LiaTemplates/AlaSQL | In-memory SQL, also on JSON, 2020 |
| LiaTemplates/PouchDB | PouchDB / NoSQL code blocks, 2025 |
| LiaTemplates/Redis | Redis, 2025 |
| LiaTemplates/Comunica | SPARQL queries, semantic web, 2026 |
| LiaTemplates/dbdiagram | Entity-relationship diagrams (dbdiagram), 2025 |

## Diagrams, math and visualisation

| Repository | What it does |
|---|---|
| LiaTemplates/mermaid_template | Mermaid diagrams, 2023 |
| LiaTemplates/plantUML | PlantUML diagrams, 2024 |
| LiaTemplates/Tikz-Jax | TikZ to image, also live-coding, 2024 |
| LiaTemplates/Vega | Vega visualisations, 2020 |
| LiaTemplates/JSXGraph | Dynamic geometry and function plots, 2025 |
| MINT-the-GAP/lia-coordinate | Interactive coordinate systems (JSXGraph), 2026 |
| LiaTemplates/GGBScript | Subset of GeoGebra script, 2025 |
| LiaTemplates/VTK | VTK scientific visualisation, 2020 |
| LiaTemplates/SpreadSheet | Spreadsheets (jspreadsheet), 2025 |

## Science, engineering and hardware

| Repository | What it does |
|---|---|
| LiaTemplates/AVR8js | Arduino (AVR) simulator, 2026 |
| LiaTemplates/MicroBit-Simulator | micro:bit simulator, 2025 |
| LiaTemplates/WebSerial | Code editor ↔ real device via Web Serial, 2025 |
| LiaTemplates/DigiSim | Digital circuit simulation (SimcirJS), 2026 |
| LiaTemplates/mec2 | 2D mechanics / physics simulation, 2020 |
| LiaTemplates/ChemfigJS | Molecular formulas like LaTeX chemfig, 2025 |
| LiaTemplates/ChemmacrosJS | Chemistry notation like LaTeX chemmacros, 2025 |
| LiaTemplates/KekuleJS | Chemistry: molecules, editor, viewer (Kekule.js), 2026 |
| LiaTemplates/PeriodicTable | Periodic table, 2021 |
| LiaTemplates/jscad | Parametric 3D CAD (JSCAD), 2025 |
| LiaTemplates/gcode-preview | G-code (3D printing) preview, 2025 |
| LiaTemplates/three.js | 3D scenes and buildings with floor plan and section views, 2026 |
| LiaTemplates/aframe | VR / 3D scenes (A-Frame), 2021 |
| LiaTemplates/Pannellum | 360° panorama images, 2019 |
| LiaTemplates/TensorflowJS | Machine learning (TensorFlow.js), 2019 |
| LiaTemplates/TextAnalysis | Text metrics, 2021 |
| LiaTemplates/ABCjs | Music in ABC notation, 2025 |

## Content, media and storytelling

| Repository | What it does |
|---|---|
| LiaTemplates/Wikimedia | Wikimedia content with title, license and attribution, 2026 |
| LiaTemplates/Wictionary | Words with live Wiktionary tooltips, 2026 |
| LiaTemplates/citations | Citations, 2026 |
| LiaTemplates/BeforeAndAfter | Before/after image slider, 2024 |
| LiaTemplates/Chat-Simulation | Simulated chat from JSON, 2025 |
| LiaTemplates/pixijs | Branching picture stories: scenes, dialog, choices, sound (PixiJS), 2026 |
| LiaTemplates/virtual-speaker | Animated avatars that speak the narration, 2026 |
| LiaTemplates/LiveEdit-Embeddings | Embedded LiaScript LiveEditor examples, 2025 |

## Quizzes and exercises

| Repository | What it does |
|---|---|
| LiaTemplates/Speech-Recognition-Quiz | Quizzes that check spoken text, 2025 |
| MichaelMarkert/LiaScript_DragAndDrop_Template | Drag-and-drop exercises, 2025 |
| MINT-the-GAP/lia-kachel | Drag-and-drop tile quizzes with touch support, 2026 |
| MINT-the-GAP/lia-marker | Text highlighting and marker quiz, 2026 |
| MINT-the-GAP/lia-Mathe | Fraction quizzes with circle/rectangle visuals, 2026 |
| MINT-the-GAP/lia-orthography | Orthography exercises, 2026 |
| MINT-the-GAP/lia-canvas-ocr | Handwriting canvas with LaTeX OCR, 2026 |
| MINT-the-GAP/lia-DynFlex | Resizable flex containers with quiz elements, 2026 |
| MINT-the-GAP/lia-timer | Reveal the solution after a timer, 2026 |
| MINT-the-GAP/lia-freeze-v2 | Submission link with state snapshot and freeze, 2026 |

## Presentation, navigation and classroom

| Repository | What it does |
|---|---|
| LiaTemplates/Fullscreen | Hide the nav bar in fullscreen presentations, 2022 |
| MINT-the-GAP/lia-board-mode | Full-width presentation layout, font-size slider, 2026 |
| MINT-the-GAP/lia-annotation | Pen/eraser annotation overlay for live presentations, 2026 |
| MINT-the-GAP/lia-navigation | Collapsible navigation with bookmarks, 2026 |
| LiaTemplates/reference-jump | Jump to a section and highlight an element, 2026 |
| LiaTemplates/CollaborativeDrawing | Shared whiteboards in a LiaScript classroom, 2026 |
