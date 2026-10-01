#!/usr/bin/env bash
# Dominant colors of an image (or a rendered slide/PDF page) via ImageMagick.
#
#   image_palette.sh IMAGE [N=8]
#
# Prints one line per color, most frequent first:
#   share%  #hex  L=lightness S=saturation  role-hint
# plus the overall mean lightness (tells whether the source "feels" light or dark).
# Needs: magick (ImageMagick 7) or convert (IM 6).
set -euo pipefail
img="${1:?usage: image_palette.sh IMAGE [N]}"
n="${2:-8}"
IM=$(command -v magick || command -v convert || { echo "ImageMagick not found" >&2; exit 1; })

mean=$("$IM" "$img" -colorspace Gray -format '%[fx:round(100*mean)]' info:)

"$IM" "$img" -resize 256x256\> -alpha off +dither -colorspace LAB -colors "$n" -colorspace sRGB \
     -format '%c' histogram:info:- \
| sed -nE 's/^ *([0-9]+):.*(#[0-9A-Fa-f]{6}).*/\1 \2/p' \
| sort -rn \
| python3 -c '
import sys, colorsys
rows = [l.split() for l in sys.stdin if l.strip()]
total = sum(int(c) for c, _ in rows) or 1
for c, h in rows:
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (1, 3, 5))
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    share = 100 * int(c) / total
    if l > 0.88: hint = "background (light)"
    elif l < 0.16: hint = "background (dark) / text"
    elif s > 0.45 and 0.25 < l < 0.7: hint = "accent candidate"
    elif s < 0.15: hint = "neutral / border / surface"
    else: hint = "secondary"
    print(f"{share:5.1f}%  {h.lower()}  L={l:.2f} S={s:.2f}  {hint}")
'
echo "mean lightness: ${mean}%  ($( [ "$mean" -ge 55 ] && echo 'light source → light theme first' || echo 'dark source → consider dark: true or a dark-first palette'))"
