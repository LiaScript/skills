# Diagram catalogue

Where text diagrams are used: RFCs and protocol specs (packet headers, state
machines, message flows), code comments, READMEs and man pages, and teaching
material (data structures, networks, logic, circuits, physics). Every template
below was rendered with elm-svgbob and checked by eye. Copy one, then adapt it.

Ratings: **good** = draws cleanly. **tricks** = works if you follow the note.
**poor** = use a different tool (an image, a chart, a table).

| Type | Rating | Note |
|---|---|---|
| Flowchart | good | diamond with `+` at all four vertices |
| Sequence / message flow | good | dashed reply with `<~~~~` or `<- - -` |
| Architecture / block diagram | good | emoji icons need 2 cells |
| Network topology | good | a bare `( Internet )` stays text; add `.---.` above and `'---'` below for a stadium |
| State machine | good | loop-backs with `.`/`'` corners |
| UML class, ER | good | `– name` (en dash), inheritance arrowhead `/ \` over `+-+-+` |
| Linked list, array, stack, hash table | good | `*-+--->` pointer dot; no `"` quotes, no `...` |
| Tree, graph | good | node names `A`, `V`, `v`, `o`, `O` next to `/ \ |` turn into shapes |
| RFC bit layout | good | dividers become solid lines |
| Git graph | good | commit dots with `*` or `o`; avoid `A` as a commit name |
| Pipeline / DAG | good | |
| Timeline / Gantt | good | bars from `■■■■`; `#` and `█` rows melt together |
| Timing / waveform | good | `__|  |__` pattern |
| Circuit | tricks | resistor `/\/\/`, capacitor `---`/`---`, source `( ~ )`, diode `--|>|--`, switch `--o/ o--` |
| Logic gates | tricks | AND and NOT draw well, OR does not |
| Control loop / signal flow | good | summing junction `.-.` / `( + )` / `'-'` |
| Coordinates, vectors, optics | good | |
| Bar chart | good | vertical bars from `##`; horizontal bars from `■` or `▄` |
| Sparkline | good | `▁▂▃▄▅▆▇█` (text glyphs) |
| Table, Kanban | good | header rule with `+----+----+`; no `+====+====+` (a `+` inside a `=` run breaks the double line) |
| UI mockup / wireframe | good | ASCII or box drawing, not mixed |
| Floor plan | good | |
| Mind map, file tree | good | no trailing `/` on names (`src/` draws a slash line) |
| Venn diagram, free curves, organic shapes | poor | no circle art in this fork |

## Flowchart

````markdown
<!-- style="max-width: 400px; display: block; margin: auto" -->
``` ascii
          .-------.
         (  start  )
          '---+---'
              |
              v
       +-------------+
       | read input  |
       +------+------+
              |
              +
             / \
            /   \       no      +-------+
           + ok? +------------->| retry |
            \   /               +---+---+
             \ /                    |
              +                     |
              |  yes                |
              v                     |
       +-------------+              |
       |    save     |<-------------'
       +-------------+
```
````
The decision diamond has `+` at all four vertices, so lines can enter and leave
at each of them. `<` and `>` as vertices stay text. The text inside needs one
space to each slant.

## Sequence diagram

````markdown
<!-- style="max-width: 320px" -->
``` ascii
   😎                    👩
   Bob                  Alice
    |                      |
    |  hello               |
    +--------------------->|
    |                      |
    |  is it ok?           |
    |<~~~~~~~~~~~~~~~~~~~~~+
    |                      |
```
````
Keep names off the lifeline column: `Alice` directly above `|` turns its `A`
into an arrowhead.

## Architecture with emoji

````markdown
<!-- style="max-width: 560px" -->
``` ascii   Fig.: Request path
 +-----------+  HTTPS  +-----------+  gRPC  +-------------+
 | 🌐 Browser|-------->|  Gateway  |------->| 🔐 Auth     |
 +-----------+         +-----+-----+        +-------------+
                             |
                             | AMQP
                             v
                       +-----------+   SQL  +-------------+
                       | ⚙️ Worker |------->| 🗄️ Postgres |
                       +-----------+        +-------------+
```
````
Each emoji takes 2 cells, so its row has one space less before the right
border. Check with `scripts/check.py`.

## Network topology

````markdown
``` ascii
              .----------.
             ( Internet   )
              '----+-----'
                   |
              +----+----+
              | Router  |
              +----+----+
                   |  192.168.1.0/24
        +----------+----------+
        |          |          |
     +--+--+    +--+--+    +--+--+
     | PC1 |    | PC2 |    | NAS |
     +-----+    +-----+    +-----+
```
````

## State machine

````markdown
``` ascii
                 +---------+
       .-------->| CLOSED  |
       |         +----+----+
       |              | passive open
       |              v
       | close   +---------+  rcv SYN   +----------+
       '---------+ LISTEN  +----------->| SYN RCVD |
                 +---------+            +----------+
```
````

## UML class diagram

````markdown
<!-- style="max-width: 480px; display: block; margin: auto" -->
``` ascii
+---------------------+      +------------------------.
| User                |      | passwords are hashed   |\
+---------------------+      | w∕o salt — fix!        +-+
| – name: String      +~~~~~~+                          |
| – email: String     |      +--------------------------+
+---------------------+
| + login(): bool     |
|                     |
+----------+----------+
          / \
         +-+-+
           |
           |
+----------+----------+
| Admin               |
+---------------------+
```
````
Visibility `–` is an en dash (a `-` turns into a stroke). The empty row under
`login():` keeps the `:` away from the border. The note box gets a folded
corner from `.` / `|\` / `+-+`.

## Data structures

````markdown
``` ascii
 head
  |
  v
+---+---+    +---+---+    +---+------+
| 1 | *-+--->| 2 | *-+--->| 3 | null |
+---+---+    +---+---+    +---+------+

  lo          mid           hi
  |            |             |
  v            v             v
+----+----+----+----+----+----+         +-------+
|  2 |  5 |  7 |  9 | 11 | 14 |         |   3   |<-- top
+----+----+----+----+----+----+         +-------+
   0    1    2    3    4    5           |   2   |
                                        +-------+
         8                              |   1   |
       /   \                            +-------+
      3     10
     / \      \          +---+
    1   6      14        | 0 +--->[ cat | 3 ]--->[ dog | 7 ]
       / \    /          +---+
      4   7  13          | 1 |
                         +---+
```
````

## RFC packet header

````markdown
``` ascii
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Version|  IHL  |Type of Service|          Total Length         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Identification        |Flags|      Fragment Offset    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```
````

## Git graph and pipeline

````markdown
``` ascii
 feature          o---o---o
                 /         \
 main   o---o---o---o-------o---o

 fetch ---> build --+--> test ---+--> deploy
                    |            |
                    '--> lint ---'
```
````

## Timeline and timing diagram

````markdown
``` ascii
 Task       Jan     Feb     Mar     Apr
 Design     ■■■■■■■■
 Build              ■■■■■■■■■■■■■■■■
 Test                       ■■■■■■■■
 Release                            ◆

         ___     ___     ___     ___
 CLK  __|   |___|   |___|   |___|   |__
             _______________
 EN   ______|               |__________
```
````
`■` or `▄` bars stay separate from row to row. `█`, `▇` and `#` rows melt
into one block.

## Circuit and logic

````markdown
``` ascii
       R1 1k
  +---/\/\/\---+-------+
  |            |       |
 .-.          ---     .-.
( ~ )         --- C1  | | R2
 '-'           |      '-'
  |            |       |
  +------------+-------+
               |
             -----
              ---
               -

      ____                         |\
A ---|    \                   A ---| >o--- Y
     |     )--- Y                  |/
B ---|____/                       NOT
     AND
```
````
More parts: resistor `-[ R1 ]-`, diode `--|>|--`, switch `--o/ o--`.
OR gates and transistors do not draw well.

## Control loop

````markdown
``` ascii
           .-.        +-------+      +---------+
  r ----->( + )------>|   C   |----->|  Plant  |---+---> y
           '-'        +-------+      +---------+   |
            ^ -                                    |
            |           +--------+                 |
            '-----------+ Sensor |<----------------'
                        +--------+
```
````
A small circle is `.-.` / `( x )` / `'-'`: the `(` sits one column left of
the `.` above it.

## Coordinates and vectors

````markdown
``` ascii
      y ^
        |         * P(x, y)
        |        /
        |     r /
        |      /
        |     / θ
        +-------------------> x
        0
```
````

## Charts

````markdown
``` ascii
  40 |       ##
  30 |  ##   ##
  20 |  ##   ##   ##
  10 |  ##   ##   ##   ##
     +--------------------
        Q1   Q2   Q3   Q4

  Q1  ■■■■■■■■■■■■■■■■      62 %
  Q2  ■■■■■■■■■■■■■■■■■■■■  81 %

  trend  ▁▂▃▅▇█▇▅▃▂▁
```
````

## Table and Kanban

````markdown
``` ascii
+--------+--------+-------+
| Field  | Type   | Bytes |
+--------+--------+-------+
| id     | int    |     4 |
| name   | text   |   var |
+--------+--------+-------+
```
````

## UI mockup

ASCII version (font independent):

````markdown
``` ascii
+-------------------------------------+
| My App                    [_][o][x] |
+-------------------------------------+
|  User:     [__________________]     |
|  Password: [__________________]     |
|  [x] Remember me       [ Login ]    |
|                                     |
+-------------------------------------+
```
````

Box-drawing version (terminal look, see `unicode.md`):

````markdown
<!-- style="max-width: 360px; display: block; margin: auto" -->
``` ascii
╔══════════════════════════════[×]═╗
║ Dashboard                        ║
╟────────────┬───────────────────┬─╢
║ ▸ Overview │ Jan ■■■■■■■■      │▲║
║   Reports  │ Feb ■■■■■         │█║
║   Users    │ Mar ■■■■■■■■■■■   │░║
║   Settings │ Apr ■■■■■■        │▼║
╚════════════╧═══════════════════╧═╝▒
 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
```
````

## Mind map and file tree

````markdown
``` ascii
                .--- Syntax
               /
 LiaScript ---+----- Quizzes          project
               \                      ├── src
                '--- ASCII art        │   ├── main.rs
                                      │   └── lib.rs
                                      └── Cargo.toml
```
````
