#!/usr/bin/env python3
"""Extract design tokens from a PowerPoint (.pptx / .potx) file — stdlib only.

  pptx_theme.py deck.pptx                 JSON report on stdout
  pptx_theme.py deck.pptx --draft t.json  also write a theme.json draft for build_theme.py
  pptx_theme.py deck.pptx --render DIR    also render slides to DIR/slide-N.png
                                          (needs soffice + pdftoppm) for visual review
                                          and scripts/image_palette.sh

What it reads:
  * ppt/theme/theme1.xml   color scheme (dk1 lt1 dk2 lt2 accent1-6 hlink) + major/minor fonts
  * slide masters/layouts/slides: title & body text styles (font, size, bold, color),
    color usage split into fills / text / lines, backgrounds (solid, gradient, image),
    shape geometry (roundRect radius), outer shadows, line widths
The theme color scheme is often generic (e.g. LibreOffice/Office default) while the
real design sits in direct formatting — so the report ranks the colors that are
actually *used* and the draft prefers them.
"""
import argparse, collections, colorsys, glob, json, os, re, shutil, subprocess, sys, tempfile, zipfile
import xml.etree.ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
A = "{%s}" % NS["a"]
P = "{%s}" % NS["p"]
EMU_PER_PT = 12700

# Office / system fonts → close, freely available Google Fonts
FONT_MAP = {
    "calibri": "Carlito", "calibri light": "Carlito", "cambria": "Caladea",
    "arial": "Arimo", "helvetica": "Arimo", "helvetica neue": "Inter", "arial narrow": "Archivo Narrow",
    "times new roman": "Tinos", "times": "Tinos", "georgia": "Gelasio", "garamond": "EB Garamond",
    "courier new": "Cousine", "consolas": "Inconsolata", "menlo": "JetBrains Mono", "monaco": "JetBrains Mono",
    "segoe ui": "Noto Sans", "segoe ui light": "Noto Sans", "aptos": "Inter", "aptos display": "Inter",
    "century gothic": "Questrial", "gill sans": "Lato", "gill sans mt": "Lato", "verdana": "Noto Sans",
    "tahoma": "Noto Sans", "trebuchet ms": "Fira Sans", "franklin gothic": "Libre Franklin",
    "franklin gothic book": "Libre Franklin", "palatino": "Domine", "book antiqua": "Domine",
    "corbel": "Open Sans", "candara": "Nunito", "constantia": "Gelasio", "rockwell": "Roboto Slab",
    "dejavu sans": "Noto Sans", "liberation sans": "Arimo", "liberation serif": "Tinos",
    "open sans": "Open Sans", "roboto": "Roboto", "lato": "Lato", "montserrat": "Montserrat",
    "source sans pro": "Source Sans 3", "noto sans": "Noto Sans", "inter": "Inter",
}
SERIF_HINT = ("times", "georgia", "garamond", "cambria", "palatino", "antiqua", "constantia", "rockwell", "serif", "tinos", "gelasio")


def hx(v):
    return "#" + v.lower()


def lum_sat(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    _, l, s = colorsys.rgb_to_hls(r, g, b)
    return l, s


def apply_mods(hexcol, el):
    """Apply the common DrawingML color modifiers (lumMod/lumOff/tint/shade)."""
    r, g, b = (int(hexcol[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    for m in el:
        tag, val = m.tag.replace(A, ""), int(m.get("val", "100000")) / 100000
        if tag == "lumMod":
            l *= val
        elif tag == "lumOff":
            l += val
        elif tag == "tint":
            l = l + (1 - l) * (1 - val)
        elif tag == "shade":
            l *= val
    r, g, b = colorsys.hls_to_rgb(h, max(0, min(1, l)), s)
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


class Deck:
    def __init__(self, path):
        self.z = zipfile.ZipFile(path)
        self.names = self.z.namelist()
        self.scheme, self.fonts = {}, {}
        self.clrmap = {"bg1": "lt1", "tx1": "dk1", "bg2": "lt2", "tx2": "dk2"}
        self.read_theme()

    def xml(self, name):
        return ET.fromstring(self.z.read(name))

    def read_theme(self):
        themes = sorted(n for n in self.names if re.match(r"ppt/theme/theme\d+\.xml$", n))
        if not themes:
            return
        t = self.xml(themes[0])
        cs = t.find(".//a:clrScheme", NS)
        if cs is not None:
            for c in cs:
                key = c.tag.replace(A, "")
                s = c.find("a:srgbClr", NS)
                sysc = c.find("a:sysClr", NS)
                if s is not None:
                    self.scheme[key] = hx(s.get("val"))
                elif sysc is not None:
                    self.scheme[key] = hx(sysc.get("lastClr", "000000"))
        fs = t.find(".//a:fontScheme", NS)
        if fs is not None:
            for kind in ("majorFont", "minorFont"):
                lat = fs.find(f"a:{kind}/a:latin", NS)
                if lat is not None:
                    self.fonts[kind] = lat.get("typeface")
        masters = sorted(n for n in self.names if re.match(r"ppt/slideMasters/slideMaster\d+\.xml$", n))
        if masters:
            cm = self.xml(masters[0]).find("p:clrMap", NS)
            if cm is not None:
                self.clrmap.update(cm.attrib)

    def color(self, el):
        """Resolve a fill element's color (srgbClr / schemeClr / sysClr) to hex."""
        if el is None:
            return None
        for c in el:
            tag = c.tag.replace(A, "")
            if tag == "srgbClr":
                return apply_mods(hx(c.get("val")), c)
            if tag == "schemeClr":
                key = c.get("val")
                key = self.clrmap.get(key, key)
                base = self.scheme.get(key)
                return apply_mods(base, c) if base else None
            if tag == "sysClr":
                return apply_mods(hx(c.get("lastClr", "000000")), c)
        return None

    def font_name(self, rpr):
        lat = rpr.find("a:latin", NS) if rpr is not None else None
        if lat is None:
            return None
        tf = lat.get("typeface", "")
        if tf.startswith("+mj"):
            return self.fonts.get("majorFont")
        if tf.startswith("+mn"):
            return self.fonts.get("minorFont")
        return tf or None


def analyse(path):
    d = Deck(path)
    parts = sorted(n for n in d.names if re.match(r"ppt/(slideMasters/slideMaster|slideLayouts/slideLayout|slides/slide)\d+\.xml$", n))
    fills, texts, lines = collections.Counter(), collections.Counter(), collections.Counter()
    fonts = {"title": collections.Counter(), "body": collections.Counter()}
    sizes = {"title": collections.Counter(), "body": collections.Counter()}
    bold = {"title": collections.Counter(), "body": collections.Counter()}
    tcolor = {"title": collections.Counter(), "body": collections.Counter()}
    geoms, radii, line_w = collections.Counter(), [], collections.Counter()
    backgrounds, shadows = [], 0
    n_slides = sum(1 for n in parts if "/slides/" in n)

    for name in parts:
        root = d.xml(name)
        weight = 3 if "/slides/" in name else 1  # what is on real slides counts more
        # backgrounds
        for bg in root.iter(P + "bg"):
            bgpr = bg.find("p:bgPr", NS)
            if bgpr is not None:
                sf, gf, bf = bgpr.find("a:solidFill", NS), bgpr.find("a:gradFill", NS), bgpr.find("a:blipFill", NS)
                if sf is not None:
                    backgrounds.append(("solid", d.color(sf), name))
                elif gf is not None:
                    stops = [d.color(gs) for gs in gf.iter(A + "gs")]
                    backgrounds.append(("gradient", stops, name))
                elif bf is not None:
                    backgrounds.append(("image", None, name))
            ref = bg.find("p:bgRef", NS)
            if ref is not None:
                backgrounds.append(("theme-ref", d.color(ref), name))
        # shapes
        for sp in root.iter(P + "sp"):
            ph = sp.find(".//p:nvPr/p:ph", NS)
            ptype = ph.get("type", "body") if ph is not None else "shape"
            role = "title" if ptype in ("title", "ctrTitle") else ("body" if ptype in ("body", "subTitle", "obj") or ph is not None else "shape")
            sppr = sp.find("p:spPr", NS)
            if sppr is not None:
                g = sppr.find("a:prstGeom", NS)
                if g is not None:
                    geoms[g.get("prst")] += 1
                    if g.get("prst") == "roundRect":
                        gd = g.find("a:avLst/a:gd", NS)
                        adj = int(gd.get("fmla", "val 16667").split()[-1]) if gd is not None else 16667
                        ext = sppr.find("a:xfrm/a:ext", NS)
                        if ext is not None:
                            short = min(int(ext.get("cx", 0)), int(ext.get("cy", 0)))
                            radii.append(round(short * adj / 100000 / EMU_PER_PT, 1))  # in pt
                sf = sppr.find("a:solidFill", NS)
                if sf is not None and (c := d.color(sf)):
                    fills[c] += weight
                gf = sppr.find("a:gradFill", NS)
                if gf is not None:
                    for gs in gf.iter(A + "gs"):
                        if c := d.color(gs):
                            fills[c] += weight
                ln = sppr.find("a:ln", NS)
                if ln is not None:
                    w = int(ln.get("w", "0"))
                    lsf = ln.find("a:solidFill", NS)
                    if w and lsf is not None:
                        line_w[round(w / EMU_PER_PT, 2)] += 1
                        if c := d.color(lsf):
                            lines[c] += weight
                if sppr.find(".//a:outerShdw", NS) is not None:
                    shadows += 1
            # text runs
            for rpr in list(sp.iter(A + "rPr")) + list(sp.iter(A + "defRPr")) + list(sp.iter(A + "endParaRPr")):
                sf = rpr.find("a:solidFill", NS)
                c = d.color(sf) if sf is not None else None
                if c:
                    texts[c] += weight
                if role in fonts:
                    if f := d.font_name(rpr):
                        fonts[role][f] += weight
                    if rpr.get("sz"):
                        sizes[role][int(rpr.get("sz")) / 100] += weight
                    if rpr.get("b") is not None:
                        bold[role][rpr.get("b") in ("1", "true")] += weight
                    if c:
                        tcolor[role][c] += weight
        # master text styles
        tx = root.find("p:txStyles", NS)
        if tx is not None:
            for role, tag in (("title", "p:titleStyle"), ("body", "p:bodyStyle")):
                st = tx.find(tag, NS)
                if st is None:
                    continue
                lvl = st.find("a:lvl1pPr/a:defRPr", NS)
                if lvl is not None:
                    if lvl.get("sz"):
                        sizes[role][int(lvl.get("sz")) / 100] += 1
                    if f := d.font_name(lvl):
                        fonts[role][f] += 1
                    sf = lvl.find("a:solidFill", NS)
                    if sf is not None and (c := d.color(sf)):
                        tcolor[role][c] += 1

    pres = d.xml("ppt/presentation.xml") if "ppt/presentation.xml" in d.names else None
    size = None
    if pres is not None and (s := pres.find("p:sldSz", NS)) is not None:
        size = {"width_pt": int(s.get("cx")) / EMU_PER_PT, "height_pt": int(s.get("cy")) / EMU_PER_PT}

    def top(counter, n=8):
        return [[k, v] for k, v in counter.most_common(n)]

    pictures = sum(len(list(d.xml(n).iter(A + "blip"))) for n in parts)
    notes = []
    if sum(fills.values()) < 5:
        notes.append("few vector fills: the design probably lives in images — use --render and "
                     "image_palette.sh on the rendered slides")
    if pictures and any("slideLayout" in n or "slideMaster" in n for n in parts
                        for _ in d.xml(n).iter(A + "blip")):
        notes.append("masters/layouts contain pictures (background art / textures)")
    if d.scheme.get("accent1", "").lower() in ("#18a303", "#4472c4", "#156082", "#0f9ed5"):
        notes.append("theme color scheme looks like an application default — trust used_* colors")

    return {
        "file": os.path.basename(path),
        "slides": n_slides,
        "slide_size": size,
        "theme_colors": d.scheme,
        "theme_fonts": d.fonts,
        "backgrounds": [{"kind": k, "color": c, "part": n} for k, c, n in backgrounds][:12],
        "used_fill_colors": top(fills),
        "used_text_colors": top(texts),
        "used_line_colors": top(lines, 5),
        "title": {"fonts": top(fonts["title"], 3), "sizes_pt": top(sizes["title"], 4), "bold": top(bold["title"], 2), "colors": top(tcolor["title"], 3)},
        "body": {"fonts": top(fonts["body"], 3), "sizes_pt": top(sizes["body"], 4), "bold": top(bold["body"], 2), "colors": top(tcolor["body"], 3)},
        "geometry": top(geoms, 8),
        "round_rect_radii_pt": sorted(radii)[:20],
        "line_widths_pt": top(line_w, 4),
        "outer_shadows": shadows,
        "pictures": pictures,
        "notes": notes,
    }


def google(font):
    if not font:
        return None
    return FONT_MAP.get(font.lower(), font)


def draft(rep):
    """Turn the report into a theme.json draft (a starting point, not the answer)."""
    tc = rep["theme_colors"]
    bgs = [b["color"] for b in rep["backgrounds"] if b["kind"] in ("solid", "theme-ref") and isinstance(b["color"], str)]
    background = collections.Counter(bgs).most_common(1)[0][0] if bgs else tc.get("lt1", "#ffffff")
    # a very light, heavily used fill is usually a full-slide rectangle acting as background
    light_fills = [c for c, _ in rep["used_fill_colors"][:2] if lum_sat(c)[0] > 0.86 and c != "#ffffff"]
    if not bgs and light_fills:
        background = light_fills[0]
    body_colors = [c for c, _ in rep["body"]["colors"]] + [c for c, _ in rep["used_text_colors"]]
    text = next((c for c in body_colors if abs(lum_sat(c)[0] - lum_sat(background)[0]) > 0.45), tc.get("dk1", "#222222"))
    candidates = [c for c, _ in rep["used_fill_colors"]] + [c for c, _ in rep["title"]["colors"]] + \
                 [tc[k] for k in ("accent1", "accent2", "accent3") if k in tc]
    accent = next((c for c in candidates if lum_sat(c)[1] > 0.3 and 0.2 < lum_sat(c)[0] < 0.7), tc.get("accent1", "#147375"))
    # saturated colors that are too light for white button labels become decoration
    decor = [c for c in dict.fromkeys(candidates) if lum_sat(c)[1] > 0.3 and 0.15 < lum_sat(c)[0] < 0.85][:6]
    tfont = google(rep["title"]["fonts"][0][0] if rep["title"]["fonts"] else rep["theme_fonts"].get("majorFont"))
    bfont = google(rep["body"]["fonts"][0][0] if rep["body"]["fonts"] else rep["theme_fonts"].get("minorFont"))
    fams = []
    for f in dict.fromkeys(x for x in (tfont, bfont) if x):
        fams.append(f + ":wght@400;600;700")
    radius = "0.8rem"
    if rep["round_rect_radii_pt"]:
        med = rep["round_rect_radii_pt"][len(rep["round_rect_radii_pt"]) // 2]
        radius = f"{min(2.0, max(0.3, med / 10)):.1f}rem"
    elif rep["geometry"] and rep["geometry"][0][0] == "rect":
        radius = "0"
    title_bold = rep["title"]["bold"][0][0] if rep["title"]["bold"] else True
    return {
        "name": os.path.splitext(rep["file"])[0],
        "source": f"pptx: {rep['file']}",
        "fonts": {
            "body": bfont or "Source Sans 3",
            "heading": tfont or bfont or "Source Serif 4",
            "google": fams,
            "heading_weight": 700 if title_bold else 400,
        },
        "light": {"background": background, "text": text, "accent": accent},
        "_decor_colors": decor,
        "dark": "auto",
        "shape": {
            "radius": radius, "radius_small": radius, "radius_large": radius if radius != "0" else "0",
            "shadow": "0 0.3rem 1rem rgba(0,0,0,0.15)" if rep["outer_shadows"] else "none",
        },
        "_review": "draft from pptx_theme.py — check against the rendered slides before building",
    }


def render(path, outdir):
    if not (shutil.which("soffice") and shutil.which("pdftoppm")):
        print("render skipped: soffice and pdftoppm are needed", file=sys.stderr)
        return []
    os.makedirs(outdir, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, path],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pdf = glob.glob(os.path.join(tmp, "*.pdf"))[0]
        subprocess.run(["pdftoppm", "-png", "-r", "60", pdf, os.path.join(outdir, "slide")], check=True)
    return sorted(glob.glob(os.path.join(outdir, "slide*.png")))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pptx")
    ap.add_argument("--draft", metavar="THEME.json")
    ap.add_argument("--render", metavar="DIR")
    a = ap.parse_args()
    rep = analyse(a.pptx)
    if a.render:
        rep["rendered"] = render(a.pptx, a.render)
    print(json.dumps(rep, indent=1, ensure_ascii=False))
    if a.draft:
        with open(a.draft, "w", encoding="utf-8") as f:
            json.dump(draft(rep), f, indent=2, ensure_ascii=False)
        print(f"draft written to {a.draft}", file=sys.stderr)


if __name__ == "__main__":
    main()
