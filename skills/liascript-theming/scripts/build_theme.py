#!/usr/bin/env python3
"""Build a LiaScript theme header block from a design-token JSON file.

  build_theme.py theme.json                 print link:/@style/@custom block
  build_theme.py theme.json --check         only run the WCAG contrast report
  build_theme.py theme.json --inject X.md   write the block into a course header
                                            (replaces a previous liascript-theming block)

Standard library only. See ../reference/token-mapping.md for the JSON schema.
"""
import argparse, colorsys, glob, json, os, re, sys, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ADAPTER = os.path.join(HERE, "..", "templates", "adapter.css")
START, END = "/* ==== liascript-theming:start ==== */", "/* ==== liascript-theming:end ==== */"

# ---------------------------------------------------------------- colors

def hex2rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError(f"not a hex color: {h!r}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def rgb2hex(c):
    return "#%02x%02x%02x" % tuple(round(v) for v in c)

def triple(c):
    return ",".join(str(round(v)) for v in c)

def luminance(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)

def hls(c):
    return colorsys.rgb_to_hls(*(v / 255 for v in c))

def from_hls(h, l, s):
    return tuple(v * 255 for v in colorsys.hls_to_rgb(h, max(0, min(1, l)), max(0, min(1, s))))

def with_lightness(c, l, sat=None):
    h, _, s = hls(c)
    return from_hls(h, l, s if sat is None else sat)

def push_contrast(c, against, target, direction):
    """Move lightness of c up (+1) or down (-1) until contrast >= target."""
    h, l, s = hls(c)
    while contrast(from_hls(h, l, s), against) < target and 0 <= l <= 1:
        l += 0.01 * direction
    return from_hls(h, l, s)

def mix(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))

WHITE = (255, 255, 255)

# ---------------------------------------------------------------- palette

def light_palette(p):
    bg, text, accent = hex2rgb(p["background"]), hex2rgb(p["text"]), hex2rgb(p["accent"])
    if contrast(accent, WHITE) < 4.5 and not p.get("keep_accent"):
        fixed = push_contrast(push_contrast(accent, WHITE, 4.5, -1), bg, 4.5, -1)
        print(f"note: accent {rgb2hex(accent)} is too light for LiaScript's white button labels "
              f"({contrast(accent, WHITE):.2f}:1) -> using {rgb2hex(fixed)}; keep the original as a "
              f"decoration color in extra_css, or set light.keep_accent=true", file=sys.stderr)
        accent = fixed
    out = {
        "background": bg,
        "text": text,
        "accent": accent,
        "accent_text": hex2rgb(p["accent_text"]) if p.get("accent_text") else push_contrast(accent, bg, 4.5, -1),
        "border": hex2rgb(p["border"]) if p.get("border") else mix(bg, text, 0.12),
        "surface": hex2rgb(p["surface"]) if p.get("surface") else mix(bg, text, 0.035),
        "surface_strong": hex2rgb(p["surface_strong"]) if p.get("surface_strong") else mix(bg, text, 0.08),
    }
    return out

def derive_dark(light):
    """Derive a dark palette from the light one: tinted near-black background,
    soft light text, accent kept as fill, a lighter accent for text."""
    acc = light["accent"]
    h, _, s = hls(acc)
    bg = from_hls(h, 0.11, min(s, 0.25))
    text = from_hls(h, 0.91, min(s, 0.15))
    fill = acc
    if contrast(fill, WHITE) < 4.5:
        fill = push_contrast(fill, WHITE, 4.5, -1)
    return {
        "background": bg,
        "text": text,
        "accent": fill,
        "accent_text": push_contrast(with_lightness(acc, 0.62), bg, 5.5, +1),
        "border": from_hls(h, 0.24, min(s, 0.2)),
        "surface": from_hls(h, 0.15, min(s, 0.22)),
        "surface_strong": from_hls(h, 0.20, min(s, 0.2)),
    }

def dark_palette(theme, light):
    d = theme.get("dark", "auto")
    auto = derive_dark(light)
    if d == "auto" or d is None:
        return auto
    out = dict(auto)
    for k, v in d.items():
        out[k] = hex2rgb(v)
    if "accent_text" not in d:
        out["accent_text"] = push_contrast(out["accent"], out["background"], 5.5, +1)
    return out

# ---------------------------------------------------------------- checks

def report(light, dark):
    rows, ok = [], True
    def chk(mode, label, a, b, need, hard=True):
        nonlocal ok
        r = contrast(a, b)
        status = "ok" if r >= need else ("FAIL" if hard else "warn")
        if status == "FAIL":
            ok = False
        rows.append(f"  {mode:5} {label:38} {rgb2hex(a)} on {rgb2hex(b)}  {r:5.2f}  (>= {need})  {status}")
    for mode, p in (("light", light), ("dark", dark)):
        chk(mode, "text / background", p["text"], p["background"], 4.5)
        chk(mode, "accent_text / background", p["accent_text"], p["background"], 4.5)
        chk(mode, "white label / accent (buttons)", WHITE, p["accent"], 4.5, hard=False)
        chk(mode, "accent / background (UI parts)", p["accent"], p["background"], 3.0, hard=False)
        chk(mode, "text / surface_strong (notes)", p["text"], p["surface_strong"], 4.5)
    if contrast(light["accent"], light["background"]) < 4.5:
        rows.append("  note: links use the accent in light mode; accent/background < 4.5 makes links weak")
    return ok, "\n".join(rows)

# ---------------------------------------------------------------- output

def font_stack(name, fallback):
    if not name:
        return None
    if "," in name:
        return name
    return f"'{name}', {fallback}"

def google_link(fonts):
    fams = fonts.get("google") or []
    if not fams:
        return None
    q = "&".join("family=" + urllib.parse.quote(f.replace(" ", "+"), safe="+:;@,.") for f in fams)
    return f"https://fonts.googleapis.com/css2?{q}&display=swap"

def css_block(theme, light, dark):
    f = theme.get("fonts", {})
    sh = theme.get("shape", {})
    body = font_stack(f.get("body"), "sans-serif") or "'LiaSourceSansPro', sans-serif"
    heading = font_stack(f.get("heading"), "serif") or "'LiaSourceSerifPro', serif"
    mono = font_stack(f.get("mono"), "monospace") or "'LiaSourceCodePro', monospace"
    tok = [
        f"  --theme-font-body: {body};",
        f"  --theme-font-heading: {heading};",
        f"  --theme-font-mono: {mono};",
    ]
    for key, var, fb in (("subheading", "--theme-font-subheading", "sans-serif"), ("quote", "--theme-font-quote", "serif")):
        if f.get(key):
            tok.append(f"  {var}: {font_stack(f[key], fb)};")
    for key, var in (("heading_weight", "--theme-heading-weight"), ("heading_letter_spacing", "--theme-heading-letter-spacing"),
                     ("heading_transform", "--theme-heading-transform"), ("line_height", "--theme-line-height")):
        if f.get(key) is not None:
            tok.append(f"  {var}: {f[key]};")
    if f.get("size"):
        tok.append(f"  --global-font-size: {f['size']};")
    tok += [
        f"  --theme-radius: {sh.get('radius', '0.8rem')};",
        f"  --theme-radius-small: {sh.get('radius_small', sh.get('radius', '0.8rem'))};",
        f"  --theme-radius-large: {sh.get('radius_large', '0')};",
        f"  --theme-shadow: {sh.get('shadow', 'none')};",
    ]
    if sh.get("shadow_popup"):
        tok.append(f"  --theme-shadow-popup: {sh['shadow_popup']};")

    def variant(p, dark_mode):
        pal = ["  --lia-grey-dark: " + triple(p["surface"]) + ";", "  --lia-anthracite: " + triple(p["surface_strong"]) + ";"] if dark_mode \
            else ["  --lia-grey-lighter: " + triple(p["surface"]) + ";", "  --lia-grey-light: " + triple(p["surface_strong"]) + ";"]
        return "\n".join([
            f"  --color-background: {triple(p['background'])};",
            f"  --color-text: {triple(p['text'])};",
            f"  --color-border: {triple(p['border'])};",
            *pal,
        ])

    hc = theme.get("heading_color")
    heading_rule = ""
    if hc:
        heading_rule = (f":root.lia-variant-light {{ --theme-heading-color: {hc.get('light', 'inherit') if isinstance(hc, dict) else hc}; }}\n"
                        f":root.lia-variant-dark {{ --theme-heading-color: {hc.get('dark', 'inherit') if isinstance(hc, dict) else 'inherit'}; }}\n")

    name = theme.get("name", "custom theme")
    parts = [
        START,
        f"/* theme: {name} — generated by liascript-theming, edit theme.json and rebuild */",
        ":root {", *tok, "}",
        "/* surfaces & text: apply to every color theme */",
        ":root.lia-variant-light {", variant(light, False), "}",
        ":root.lia-variant-dark {", variant(dark, True), "}",
        "/* accent: only the course theme (default) and the custom radio,",
        "   so readers can still pick LiaScript's built-in color themes */",
        ":root:is(.lia-theme-default, .lia-theme-custom) {",
        f"  --color-highlight: {triple(light['accent'])};",
        f"  --color-highlight-dark: {triple(light['accent_text'])};",
        "}",
        ":root.lia-theme-default {",
        f"  --color-highlight-menu: {triple(light['accent'])};",
        "}",
        ":root:is(.lia-theme-default, .lia-theme-custom).lia-variant-dark {",
        f"  --color-highlight: {triple(dark['accent'])};",
        f"  --color-highlight-dark: {triple(dark['accent_text'])};",
        "}",
    ]
    if heading_rule:
        parts.append(heading_rule.rstrip())
    extra = theme.get("extra_css")
    parts.append(open(ADAPTER).read().strip())
    features = feature_blocks(theme)
    if features:
        parts += ["/* -- layout / density / motion features -- */", features]
    if extra:
        parts += ["/* -- theme extras -- */", extra.strip()]
    parts.append(END)
    return "\n".join(parts)

# Optional feature blocks, emitted only when their token is set (all rendered & verified).
DENSITY = {
    "compact": {"line": 1.4, "block": "0.6rem", "h": "0.8em 0.4em", "quote": "1.4rem 1.8rem",
                "td": "0.6rem 1.6rem 0.6rem 1rem", "th": "0.8rem 1.6rem 0.8rem 1rem", "gap": "1.4rem", "li": "0.2rem"},
    "airy":    {"line": 1.7, "block": "1.6rem", "h": "1.2em 0.9em", "quote": "3.2rem 4rem",
                "td": "1.4rem 3.2rem 1.4rem 1.6rem", "th": "1.6rem 3.2rem 1.6rem 1.6rem", "gap": "3.2rem", "li": "0.6rem"},
}

def feature_blocks(theme):
    lay, sh, out = theme.get("layout", {}), theme.get("shape", {}), []
    if lay.get("heading_align"):
        a = lay["heading_align"]
        out.append(f".lia-slide__content :is(h1, h2, h3, .h1, .h2, .h3) {{ text-align: {a}; }}")
        if a == "center":
            out.append(".lia-slide__content :is(h1, h2, h3, .h1, .h2, .h3)::after { margin-inline: auto; }")
    if lay.get("content_width"):
        out.append(f".lia-canvas.lia-mode--textbook .lia-slide__content {{ max-width: {lay['content_width']}; margin-inline: auto; }}")
    if lay.get("header") == "accent":
        out += [
            "/* full-bleed header in the accent color with white icons */",
            ".lia-header { background-color: rgb(var(--color-highlight)); border-bottom: 0; margin: 0; padding-inline: 3rem; }",
            ".lia-header .lia-support-menu--closed, .lia-header .lia-support-menu__nav { background-color: transparent; }",
            ".lia-header :is(.lia-btn, .lia-support-menu__item) { color: rgb(255, 255, 255) !important; }",
            ".lia-support-menu--open .lia-btn, .lia-support-menu__submenu .lia-btn { color: rgb(var(--color-highlight)) !important; }",
            ":root.lia-variant-dark :is(.lia-support-menu--open .lia-btn, .lia-support-menu__submenu .lia-btn) { color: rgb(var(--color-highlight-dark)) !important; }",
            ".lia-header .lia-progress { background-color: rgba(255, 255, 255, 0.75); }",
            ".lia-toc--closed #lia-btn-toc, .lia-toc--hidden #lia-btn-toc { color: rgb(255, 255, 255); }",
        ]
    d = DENSITY.get(theme.get("density", ""))
    if d:
        out += [
            f"/* density: {theme['density']} */",
            f"body {{ line-height: var(--theme-line-height, {d['line']}); }}",
            f".lia-slide__content :is(p, ul, ol, .lia-paragraph) {{ margin-block-end: {d['block']}; }}",
            f".lia-slide__content li + li {{ margin-block-start: {d['li']}; }}",
            f".lia-slide__content :is(h1, h2, h3, .h1, .h2, .h3) {{ margin-block: {d['h']}; }}",
            f".lia-quote {{ padding: {d['quote']}; }}",
            f".lia-table__data {{ padding: {d['td']}; }}",
            f".lia-table__header {{ padding: {d['th']}; }}",
            f".lia-quiz, .lia-code, .lia-table-responsive, details {{ margin-block-end: {d['gap']}; }}",
        ]
    if sh.get("border_width"):
        w = sh["border_width"]
        out += [
            f"/* border width {w} */",
            f":is(.lia-btn--outline, .lia-code__input, .lia-dropdown, .lia-quiz__input, details, .lia-code--inline) {{ border-width: {w}; }}",
            f":is(.lia-checkbox[type='checkbox'], .lia-radio[type='radio']):not(:checked) {{ border-width: {w}; }}",
            f".lia-header, .lia-table__head, .lia-table__header, .lia-table__data {{ border-width: {w}; }}",
            f".lia-toc {{ border-inline-end-width: {w}; }}",
        ]
    motion = theme.get("motion")
    if motion in ("subtle", "lively"):
        dist, dur = ("1.2rem", "0.5s") if motion == "subtle" else ("2.4rem", "0.7s")
        out += [
            f"/* motion: {motion} — disabled for readers who prefer reduced motion */",
            "@media (prefers-reduced-motion: no-preference) {",
            f"  .lia-slide__content {{ animation: theme-enter {dur} cubic-bezier(0.2, 0.7, 0.2, 1) backwards; }}",
            "  .lia-effect { animation: theme-pop 0.45s ease-out backwards; }",
            "  .lia-btn:not(.lia-btn--transparent) { transition: transform 0.15s ease, box-shadow 0.15s ease; }",
            "  .lia-btn:not(.lia-btn--transparent):hover { transform: translateY(-2px); box-shadow: 0 0.4rem 1rem rgba(var(--color-highlight), 0.35); }",
            "  .lia-link { text-underline-offset: 0.3em; transition: text-decoration-thickness 0.2s ease, text-underline-offset 0.2s ease; }",
            "  .lia-link:hover { text-decoration-thickness: 0.2rem; text-underline-offset: 0.15em; }",
            "  .lia-toc__link { transition: transform 0.2s ease; }",
            "  .lia-toc__link:hover { transform: translateX(0.4rem); }",
            "}",
            f"@keyframes theme-enter {{ from {{ opacity: 0; transform: translateY({dist}); }} }}",
            "@keyframes theme-pop { from { opacity: 0; transform: translateY(0.6rem) scale(0.98); } }",
        ]
    return "\n".join(out)

MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
        ".gif": "image/gif", ".svg": "image/svg+xml", ".woff2": "font/woff2", ".woff": "font/woff"}

def embed_assets(css, base_dir):
    """url('embed:path') -> data: URI. Relative url()s in theme CSS resolve against the
    LiaScript app, not the course, so local textures/ornaments/fonts must be inlined."""
    def repl(m):
        path = os.path.join(base_dir, m.group(2))
        ext = os.path.splitext(path)[1].lower()
        data = open(path, "rb").read()
        if len(data) > 150_000:
            print(f"warning: embedding {m.group(2)} adds {len(data) // 1024} KB to every page load", file=sys.stderr)
        if ext == ".svg":
            uri = "data:image/svg+xml," + urllib.parse.quote(data.decode("utf-8"), safe=" =:/;,'-_.()")
        else:
            import base64
            uri = f"data:{MIME.get(ext, 'application/octet-stream')};base64," + base64.b64encode(data).decode()
        return f'url("{uri}")'
    return re.sub(r"""url\((['"]?)embed:([^'")]+)\1\)""", repl, css)

def build(theme, base_dir="."):
    if theme.get("extra_css"):
        theme = dict(theme, extra_css=embed_assets(theme["extra_css"], base_dir))
    light = light_palette(theme["light"])
    dark = dark_palette(theme, light)
    css = css_block(theme, light, dark)
    links = [u for u in [google_link(theme.get("fonts", {}))] + theme.get("fonts", {}).get("links", []) if u]
    if links:
        # remember the generated links, so a later --inject removes exactly these
        css = css.replace(START, START + "\n/* links: " + " ".join(links) + " */", 1)
    custom = theme.get("custom", "--color-highlight-menu: 255,255,255;")
    return light, dark, links, css, custom

def header_block(links, css, custom):
    out = ["link:     " + u for u in links]
    if links:
        out.append("")
    out += ["@style", css, "@end", "", "@custom", custom, "@end"]
    return "\n".join(out)

# ---------------------------------------------------------------- inject

def inject(course, links, css, custom):
    src = open(course, encoding="utf-8").read()
    m = re.match(r"(\s*<!--)(.*?)(-->)", src, re.S)
    if not m:
        raise SystemExit(f"error: {course} has no header comment <!-- ... -->")
    head = m.group(2)
    # 0. links generated by a previous run (recorded inside the marked block)
    old = re.search(re.escape(START) + r"\n/\* links: (.*?) \*/", head)
    old_links = old.group(1).split() if old else []
    # 1. @style: replace our marked section, or prepend into an existing @style, or add one
    if START in head:
        head = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: css, head, flags=re.S)
    elif re.search(r"^@style\s*$", head, re.M):
        head = re.sub(r"^@style\s*$", lambda _: "@style\n" + css, head, count=1, flags=re.M)
    else:
        head = head.rstrip() + "\n\n@style\n" + css + "\n@end\n"
    # 2. @custom: replace or add
    if re.search(r"^@custom\s*$", head, re.M):
        head = re.sub(r"^@custom\s*$.*?^@end\s*$", lambda _: "@custom\n" + custom + "\n@end", head, count=1, flags=re.M | re.S)
    elif re.search(r"^custom:", head, re.M):
        prev = re.search(r"^custom:(.*)$", head, re.M).group(1).strip()
        print(f"note: replaced existing 'custom: {prev}'", file=sys.stderr)
        head = re.sub(r"^custom:.*$", lambda _: "\n@custom\n" + custom + "\n@end\n", head, count=1, flags=re.M)
    else:
        head = head.rstrip() + "\n\n@custom\n" + custom + "\n@end\n"
    # 3. links: drop only the ones this script added before, then add the new ones on top
    for u in old_links:
        head = re.sub(r"^link:\s*" + re.escape(u) + r"[ \t]*\n", "", head, flags=re.M)
    if links:
        head = "\n" + "".join("link:     " + u + "\n" for u in links) + head.lstrip("\n")
    src = src[:m.start(2)] + head.rstrip() + "\n" + src[m.end(2):]
    open(course, "w", encoding="utf-8").write(src)

# ---------------------------------------------------------------- main

EXAMPLES = os.path.join(HERE, "..", "examples")

def resolve_theme(arg):
    """A path to a theme.json, or the name of a bundled design (examples/<name>.json)."""
    if os.path.isfile(arg):
        return arg
    cand = os.path.join(EXAMPLES, arg[:-5] if arg.endswith(".json") else arg) + ".json"
    if os.path.isfile(cand):
        return cand
    raise SystemExit(f"error: no theme file '{arg}' and no bundled design of that name — see --list")

def list_designs():
    for f in sorted(glob.glob(os.path.join(EXAMPLES, "*.json"))):
        t = json.load(open(f, encoding="utf-8"))
        print(f"{os.path.basename(f)[:-5]:16} {t.get('name', ''):32} {t.get('mood', '')}")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("theme", nargs="?", help="theme.json path, or the name of a bundled design (see --list)")
    ap.add_argument("--list", action="store_true", help="list the bundled designs and exit")
    ap.add_argument("--check", action="store_true", help="only print the contrast report")
    ap.add_argument("--inject", metavar="COURSE.md", help="write the block into this course header")
    ap.add_argument("--css", metavar="OUT.css", help="also write the plain CSS (for link: / templates)")
    a = ap.parse_args()
    if a.list:
        list_designs()
        return
    if not a.theme:
        ap.error("theme is required (a theme.json or a bundled design name; --list shows them)")
    path = resolve_theme(a.theme)
    theme = json.load(open(path, encoding="utf-8"))
    light, dark, links, css, custom = build(theme, os.path.dirname(os.path.abspath(path)))
    ok, rep = report(light, dark)
    print("contrast report (WCAG 2.x):\n" + rep, file=sys.stderr)
    print("dark palette: " + ", ".join(f"{k}={rgb2hex(v)}" for k, v in dark.items()), file=sys.stderr)
    if a.check:
        sys.exit(0 if ok else 1)
    if a.css:
        open(a.css, "w", encoding="utf-8").write(css + "\n")
    if a.inject:
        inject(a.inject, links, css, custom)
        print(f"injected into {a.inject}", file=sys.stderr)
    else:
        print(header_block(links, css, custom))
    if not ok:
        print("WARNING: contrast failures above — adjust the palette", file=sys.stderr)

if __name__ == "__main__":
    main()
