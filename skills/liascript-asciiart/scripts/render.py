#!/usr/bin/env python3
"""Render LiaScript ```ascii blocks to a PNG, the way LiaScript draws them.

usage: python3 render.py INPUT.md OUT.png [--dark] [--scale 1.5] [--width PX] [--svg]

INPUT is a Markdown file; every ```ascii / ```art block is rendered, together
with the <!-- key="value" --> comment directly above it (passed as attributes to
the <svg>, as LiaScript does) and the caption on the fence line. A file without
any such fence is rendered as one plain drawing.

--scale  draw each figure at natural size x SCALE (default 1.5); LiaScript itself
         stretches the svg to the full content width unless a style limits it
--width  give every figure this fixed width in px instead (like a LiaScript page)
--font F override the svg text font (e.g. "Liberation Mono" ~ Courier New on
         Windows, "DejaVu Sans Mono" ~ Linux) to see how other systems draw it
--no-params  ignore the <!-- ... --> parameters (e.g. to zoom past a max-width)
--svg    also print the generated <svg> markup to stdout
--html   also write the generated page next to OUT (OUT.html)

@style ... @end blocks of the course header are applied to the page, so
class-based styling (`<!-- class="x" -->` + `svg.x text {...}`) shows up.

Uses the svgbob source in $SVGBOB_SRC (default: ~/Workspace/Projects/Elm/elm-svgbob/src),
or the published package if that directory does not exist. Needs elm and chromium.
"""

import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent / "render"
CACHE = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "elm-svgbob-render"
DEFAULT_SRC = Path.home() / "Workspace/Projects/Elm/elm-svgbob/src"

FENCE = re.compile(r"^(`{3,})(.*)$")
COMMENT = re.compile(r"<!--(.*?)-->", re.S)
ATTR = re.compile(r"""([^\s=]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|(\S+)))?""")


def parse_attrs(text):
    return [[m.group(1), next((g for g in m.groups()[1:] if g is not None), "")]
            for m in ATTR.finditer(text)]


def extract_blocks(md):
    lines = md.split("\n")
    blocks, i = [], 0
    while i < len(lines):
        m = FENCE.match(lines[i])
        if not m:
            i += 1
            continue
        ticks, rest = len(m.group(1)), m.group(2)
        tag = re.match(r"[\t ]*(ascii|art)\b[\t ]*(.*)$", rest, re.I)
        if not tag and not (ticks > 8):
            # an ordinary code block, skip it
            j = i + 1
            while j < len(lines) and not lines[j].startswith("`" * ticks):
                j += 1
            i = j + 1
            continue
        caption = (tag.group(2) if tag else rest).strip() or None
        body, j = [], i + 1
        while j < len(lines) and not re.match(r"^`{%d}" % ticks + ("$" if ticks <= 8 else ""), lines[j].rstrip()):
            body.append(lines[j])
            j += 1
        # comment directly above the fence (blank lines not allowed in between)
        attrs, k = [], i - 1
        if k >= 0 and lines[k].strip().endswith("-->"):
            start = k
            while start >= 0 and "<!--" not in lines[start]:
                start -= 1
            c = COMMENT.search("\n".join(lines[start:k + 1]))
            if c:
                attrs = parse_attrs(c.group(1))
        blocks.append({"ascii": "\n".join(body), "attrs": attrs, "caption": caption})
        i = j + 1
    if not blocks:
        blocks.append({"ascii": md.rstrip("\n"), "attrs": [], "caption": None})
    return blocks


def cell_width(g):
    """Mirror of WChar.graphemeWidth (good enough for sizing the screenshot)."""
    if "️" in g:
        return 2
    return 2 if unicodedata.east_asian_width(g[0]) in "WF" else 1


def natural_size(ascii):
    rows = ascii.split("\n")
    cols = max((sum(cell_width(c) for c in r) for r in rows), default=0)
    return cols * 8 + 10, len(rows) * 16 + 10


def build(src):
    files = sorted(src.rglob("*.elm")) if src else []
    h = hashlib.sha256((HERE / "Main.elm").read_bytes())
    for f in files:
        h.update(f.read_bytes())
    h.update(str(src).encode())
    out = CACHE / h.hexdigest()[:16]
    js = out / "elm.js"
    if js.exists():
        return js
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy(HERE / "Main.elm", out / "Main.elm")
    conf = json.loads((HERE / "elm.json").read_text())
    if src:
        conf["source-directories"] = [".", str(src)]
    else:
        print("warning: $SVGBOB_SRC not found, using the published package 5.0.8 - "
              "newer features may be missing", file=sys.stderr)
        conf["source-directories"] = ["."]
        conf["dependencies"]["direct"]["andre-dietrich/elm-svgbob"] = "5.0.8"
    conf["elm-version"] = subprocess.run(["elm", "--version"], capture_output=True,
                                         text=True).stdout.strip()
    (out / "elm.json").write_text(json.dumps(conf, indent=4))
    r = subprocess.run(["elm", "make", "Main.elm", "--optimize", "--output=elm.js"],
                       cwd=out, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(r.stdout + r.stderr)
    return js


PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
body {{ margin: 16px; background: {bg}; color: {fg}; font-family: sans-serif; }}
.lia-figure {{ margin: 0 0 24px 0; }}
.lia-figure__caption {{ font-size: 14px; text-align: center; margin-top: 4px; }}
.verbatim {{ font: 13px sans-serif; background: rgba(255,200,0,.25); outline: 1px dashed orange; height: 100%; white-space: pre-wrap; }}
{widths}
</style></head><body><div id="app"></div>
<script>{js}</script>
<script>Elm.Main.init({{ node: document.getElementById('app'), flags: {flags} }});</script>
</body></html>"""


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    opts = {a for a in argv if a.startswith("--")}
    if len(args) < 2:
        sys.exit(__doc__)
    scale, width = 1.5, None
    if "--scale" in argv:
        scale = float(argv[argv.index("--scale") + 1])
        args.remove(argv[argv.index("--scale") + 1])
    font = None
    if "--font" in argv:
        font = argv[argv.index("--font") + 1]
        args.remove(font)
    if "--width" in argv:
        width = int(argv[argv.index("--width") + 1])
        args.remove(argv[argv.index("--width") + 1])
    infile, outfile = Path(args[0]), Path(args[1]).resolve()
    dark = "--dark" in opts

    src = Path(os.environ.get("SVGBOB_SRC", DEFAULT_SRC)).expanduser()
    js = build(src if src.is_dir() else None)

    md = infile.read_text()
    blocks = extract_blocks(md)
    if "--no-params" in opts:
        for b in blocks:
            b["attrs"] = []
    user_css = "\n".join(re.findall(r"^@style[ \t]*\n(.*?)^@end", md, re.S | re.M))
    css, page_w, page_h = [], 0, 32
    for n, b in enumerate(blocks, 1):
        w, h = natural_size(b["ascii"])
        fw = width or int(w * scale)
        css.append(".lia-figure:nth-child(%d) { width: %dpx; }" % (n, fw))
        page_w = max(page_w, fw)
        page_h += int(h * fw / w) + 24 + (30 if b["caption"] else 0)

    page = PAGE.format(
        bg="#323232" if dark else "white", fg="white" if dark else "#4b4b4b",
        widths="\n".join(css) + "\n" + user_css + ("\nsvg text { font-family: '%s' !important; }" % font if font else ""), js=js.read_text(),
        flags=json.dumps({"dark": dark, "blocks": blocks}))
    tmp = Path(tempfile.mkdtemp(prefix="svgbob-"))
    page_file = tmp / "page.html"
    page_file.write_text(page)

    if "--svg" in opts:
        r = subprocess.run(["chromium", "--headless", "--disable-gpu", "--dump-dom",
                            "--virtual-time-budget=2000", page_file.as_uri()],
                           capture_output=True, text=True)
        for svg in re.findall(r"<svg.*?</svg>", r.stdout, re.S):
            print(svg)

    # oversize the window, then crop the empty background
    win_h = int(page_h * 1.3) + 200
    subprocess.run(["chromium", "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--virtual-time-budget=2000",
                    "--window-size=%d,%d" % (page_w + 32, win_h),
                    "--screenshot=%s" % outfile, page_file.as_uri()],
                   capture_output=True, text=True, check=True)
    try:
        from PIL import Image, ImageChops
        im = Image.open(outfile).convert("RGB")
        bg = Image.new("RGB", im.size, im.getpixel((0, 0)))
        box = ImageChops.difference(im, bg).getbbox()
        if box:
            pad = 12
            im.crop((max(box[0] - pad, 0), max(box[1] - pad, 0),
                     min(box[2] + pad, im.width), min(box[3] + pad, im.height))).save(outfile)
    except ImportError:
        pass
    if "--html" in opts:
        shutil.copy(page_file, outfile.with_suffix(".html"))
        print(outfile.with_suffix(".html"))
    shutil.rmtree(tmp)
    print(outfile)


if __name__ == "__main__":
    main(sys.argv[1:])
