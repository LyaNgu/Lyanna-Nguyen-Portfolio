"""Soft cozy palette: tones the site's bright pixel colours down to muted sage, teal and pastel.

The converter runs every generated page, stylesheet and SVG through `soften_text`, and the
hand-built files were softened with it once. Text colours and dark outlines are kept so
contrast stays where it was.

    python3 tools/soft_palette.py FILE...     # soften files in place
"""
import colorsys, re, sys

# Exact replacements for the colours that set the mood.
EXPLICIT = {
    '#7cc44f': '#8fc088',  # grass
    '#2f7d3a': '#74a46f',  # grass edge
    '#4f9a3a': '#6f9f6a', '#5aa83a': '#79a874', '#4e9a33': '#6f9f6a', '#6cc04a': '#86b882',
    '#2f5e2c': '#4d6f55',  # footer
    '#1f3f1e': '#3b5642', '#4a7a3e': '#668a6a',
    '#7cc0ea': '#a9cfdc',  # sky
}
# Colours left alone: text and focus tokens, wood, cream surfaces and already-soft colours.
KEEP = {
    '#3a1f17', '#6b4227', '#9a3d1a', '#2f6b2b', '#2b1510', '#a0522a', '#5e2f18', '#fff3d6',
    '#f6e3b4', '#fdf1d3', '#ecd29a', '#fbe8c0', '#c9e3b8',
    '#8fc088', '#74a46f', '#a3cd98', '#99c78f', '#80b37b', '#f4f1e4', '#f3d58a',
} | set(EXPLICIT.values())


def soften_color(c):
    c = c.lower()
    if c in EXPLICIT: return EXPLICIT[c]
    if c in KEEP: return c
    r, g, b = (int(c[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    deg = h * 360
    if s < .3 or l < .3 or l > .93 or 250 <= deg <= 300:   # neutrals, outlines, client purples
        return c
    if 70 <= deg <= 170:                                    # greens drift toward sage
        deg += (125 - deg) * .3; s *= .6
    elif 180 <= deg <= 235:                                 # blues toward a pale, muted teal
        deg += (195 - deg) * .3; s *= .55; l += (.82 - l) * .25
    else:                                                   # reds, pinks, oranges, golds
        s *= .72
    l += (.7 - l) * .12
    r, g, b = colorsys.hls_to_rgb(deg / 360, min(l, 1), min(s, 1))
    return '#' + ''.join(f'{round(v * 255):02x}' for v in (r, g, b))


HEX = re.compile(r'#[0-9a-fA-F]{6}\b')

def soften_text(text):
    return HEX.sub(lambda m: soften_color(m.group(0)), text)


if __name__ == '__main__':
    for path in sys.argv[1:]:
        t = open(path).read()
        open(path, 'w').write(soften_text(t))
