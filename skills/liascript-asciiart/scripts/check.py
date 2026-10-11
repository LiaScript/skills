#!/usr/bin/env python3
"""Check the grid of LiaScript ```ascii blocks before rendering.

usage: python3 check.py INPUT.md

For every drawing it prints each row with its width in cells, as svgbob counts
them (2 for East Asian Wide/Fullwidth or with U+FE0F, else 1), so you can see
where a right border will not line up (rows that share a right border must
have the same count). It also warns about:

  - tabs (not expanded, a tab is one cell)
  - characters that count as 1 cell but browsers draw from an emoji font,
    about 2 cells wide, so they overlap the next cell (add U+FE0F or a space)
  - flags (1 cell, drawn 2 wide), ZWJ sequences and skin tones (2 cells, but
    older fonts split them into several glyphs)
  - rows of `.` or `'` (dotted leaders become a solid line)
"""

import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render import extract_blocks  # noqa: E402

ZWJ, VS16, VS15 = "‍", "️", "︎"

# Code points that have an emoji presentation in common emoji fonts, but are
# neither Wide nor written with U+FE0F, so svgbob gives them 1 cell (Unicode
# Emoji=Yes, Emoji_Presentation=No, plus a few that fonts draw colorful).
EMOJI_TEXT_DEFAULT = set(map(ord,
    "©®‼⁉™ℹ↔↕↖↗↘↙↩↪⌨⏏⏭⏮⏯⏱⏲⏸⏹⏺Ⓜ▪▫▶◀◻◼☀☁☂☃☄☎☑☘☝☠☢☣☦☪☮☯☸☹☺♀♂♟♠♣♥♦♨♻♾⚒⚔⚕⚖⚗⚙⚛⚜⚠⚧⚰⚱⛈⛏⛑⛓⛩⛰⛱⛴⛷⛸⛹"
    "✂✈✉✌✍✏✒✔✖✝✡✳✴❄❇❣❤➡⤴⤵⬅⬆⬇〰〽㊗㊙"))


def graphemes(line):
    out = []
    for ch in line:
        cp = ord(ch)
        joins = out and (
            unicodedata.category(ch).startswith("M")
            or ch in (ZWJ, VS16, VS15)
            or 0xFE00 <= cp <= 0xFE0F
            or 0x1F3FB <= cp <= 0x1F3FF
            or 0xE0020 <= cp <= 0xE007F
            or out[-1].endswith(ZWJ)
            or (0x1F1E6 <= cp <= 0x1F1FF and len(out[-1]) == 1
                and 0x1F1E6 <= ord(out[-1]) <= 0x1F1FF)
        )
        if joins:
            out[-1] += ch
        else:
            out.append(ch)
    return out


def width(g):
    return 2 if VS16 in g or unicodedata.east_asian_width(g[0]) in "WF" else 1


def check(ascii, n):
    rows = ascii.split("\n")
    print("--- drawing %d (row, cells, text) ---" % n)
    for y, row in enumerate(rows, 1):
        gs = graphemes(row.rstrip())
        w = sum(width(g) for g in gs)
        notes = []
        if "\t" in row:
            notes.append("TAB")
        for g in gs:
            cp = ord(g[0])
            if cp in EMOJI_TEXT_DEFAULT and VS16 not in g:
                notes.append("%s: 1 cell, but may be drawn ~2 wide from an emoji font -> add U+FE0F (2 cells) or a space after" % g)
            elif 0x1F1E6 <= cp <= 0x1F1FF:
                notes.append("%s: flag counts 1 cell, drawn 2 wide -> add a space after" % g)
            if ZWJ in g or any(0x1F3FB <= ord(c) <= 0x1F3FF for c in g):
                notes.append("%s: ZWJ/skin-tone sequence, 2 cells" % g)
        if re.search(r"[.']{4,}", row):
            notes.append("dotted leader becomes a line")
        print("%3d %3d  %s%s" % (y, w, row.rstrip(), "   <- " + "; ".join(dict.fromkeys(notes)) if notes else ""))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for n, b in enumerate(extract_blocks(Path(sys.argv[1]).read_text()), 1):
        check(b["ascii"], n)


if __name__ == "__main__":
    main()
