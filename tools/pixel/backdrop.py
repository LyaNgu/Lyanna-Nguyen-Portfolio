"""Generate the tiling 8-bit backdrop layers for the home hero as crisp-edged SVGs."""
import math, sys, os
OUT = sys.argv[1]

def svg(w, h, px):
    # merge horizontal runs of the same colour into one rect
    rows = {}
    for (x, y), c in px.items(): rows.setdefault(y, {})[x] = c
    rects = []
    for y in sorted(rows):
        xs = sorted(rows[y]); i = 0
        while i < len(xs):
            x0 = xs[i]; c = rows[y][x0]; j = i
            while j + 1 < len(xs) and xs[j+1] == xs[j] + 1 and rows[y][xs[j+1]] == c: j += 1
            rects.append(f'<rect x="{x0}" y="{y}" width="{xs[j]-x0+1}" height="1" fill="{c}"/>'); i = j + 1
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'shape-rendering="crispEdges">' + ''.join(rects) + '</svg>\n')

def hash01(x, y, s=0):
    v = math.sin(x * 12.9898 + y * 78.233 + s * 37.719) * 43758.5453
    return v - math.floor(v)

# ---- distant mountains: soft teal peaks, stepped in 2px stairs
def mountains():
    W, H = 96, 36; px = {}
    peaks = [(14, 30), (40, 20), (66, 33), (88, 22)]
    for x in range(W):
        top = H
        for cx, ph in peaks:
            for off in (-W, 0, W):
                d = abs(x - (cx + off))
                t = H - ph + (d // 2) * 2 * 0.9
                top = min(top, int(t))
        for y in range(max(top, 0), H):
            c = '#a7d6c4'
            if y == top: c = '#c6e8d6'
            elif y < top + 3 and hash01(x, y) > .55: c = '#bde2cf'
            px[(x, y)] = c
    return W, H, px

# ---- rolling hills: stepped bumps with a light rim and grass speckles
def hills():
    W, H = 80, 26; px = {}
    for x in range(W):
        h = 13 + 6 * math.sin(2 * math.pi * x / W) + 3 * math.sin(4 * math.pi * x / W + 1.2)
        top = H - int(round(h))
        for y in range(top, H):
            c = '#9fd28a'
            if y == top: c = '#c2e6a2'
            elif y == top + 1: c = '#b2dd96'
            elif hash01(x, y, 1) > .93: c = '#8cc97a'
            px[(x, y)] = c
    return W, H, px

# ---- tree line: round canopies and layered pines, shaded light top-left to dark bottom-right
PAL = dict(hi='#d6e88a', light='#a6d86e', mid='#6fbf5a', dark='#3f9450', deep='#2f7a44',
           trunk='#8a5a3a', trunkd='#6b4229')

def round_tree(px, x0, base, r, trunk_h=3):
    cx, cy = x0 + r, base - trunk_h - r
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r - 1, cx + r + 2):
            dx, dy = x - cx + .5, (y - cy + .5) * 1.1
            d = math.hypot(dx, dy)
            # scalloped edge reads as leaf clumps
            edge = r + .35 * math.sin(math.atan2(dy, dx) * 6)
            if d > edge: continue
            s = (dx + dy) / r
            c = 'light' if s < -.55 else 'mid' if s < .35 else 'dark' if s < .9 else 'deep'
            if c in ('light', 'mid') and hash01(x, y, 3) > .9: c = 'hi'
            px[(x, y)] = PAL[c]
    for y in range(base - trunk_h, base):
        px[(cx - 1, y)] = PAL['trunk']; px[(cx, y)] = PAL['trunkd']

def pine(px, x0, base, w, tiers=3):
    cx = x0 + w // 2; top = base - 2 - tiers * 5
    for t in range(tiers):
        ty = top + t * 5; half_max = 2 + t * (w // 2 - 2) // max(tiers - 1, 1)
        for k in range(7):
            y = ty + k; half = min(half_max, 1 + k * half_max // 5)
            if k == 6: half -= 1
            for x in range(cx - half, cx + half + 1):
                rel = (x - cx) / max(half, 1)
                c = 'light' if rel < -.35 else 'mid' if rel < .4 else 'dark'
                if k <= 1: c = 'hi' if rel < .2 else 'light'
                if k >= 5 and c != 'dark': c = 'mid' if rel < 0 else 'dark'
                px[(x, y)] = PAL[c]
    for y in range(base - 2, base):
        px[(cx, y)] = PAL['trunk']; px[(cx + 1, y)] = PAL['trunkd']

def bush(px, x0, base, w):
    for x in range(x0, x0 + w):
        h = 3 + int(1.5 * math.sin((x - x0) / (w - 1) * math.pi) + .5)
        for y in range(base - h, base):
            rel = (x - x0) / w
            c = 'light' if y == base - h else 'mid' if rel < .6 else 'dark'
            px[(x, y)] = PAL[c]

def canopy_band(px, W, base, h):
    # a continuous back row of darker canopies so the tree line reads as a dense wood
    for x in range(W):
        top = base - h - int(round(2.2 * abs(math.sin(math.pi * x / 7)) + 1.2 * math.sin(2 * math.pi * x / W * 3)))
        for y in range(top, base):
            c = '#4f9f52' if y > top else '#6fbf5a'
            if y > top + 2 and hash01(x, y, 5) > .8: c = '#3f9450'
            px[(x, y)] = c

def trees():
    W, H = 128, 34; px = {}; b = H
    canopy_band(px, W, b, 9)
    pine(px, 2, b, 12)
    round_tree(px, 15, b, 8)
    pine(px, 34, b, 10, 2)
    round_tree(px, 46, b, 6)
    pine(px, 60, b, 14, 3)
    round_tree(px, 76, b, 9, 4)
    pine(px, 97, b, 10, 2)
    round_tree(px, 108, b, 7)
    bush(px, 28, b, 7)
    bush(px, 90, b, 8)
    return W, H, px

# ---- grass strip: tufts and tiny flowers over the existing grass colour
def grass():
    W, H = 64, 24; px = {}
    tufts = [(3, 5), (12, 15), (22, 7), (27, 19), (7, 20), (17, 2), (36, 11), (44, 4), (51, 17), (58, 9), (40, 21), (61, 2)]
    for x, y in tufts:
        for dx, dy in ((0, 0), (2, 0), (1, -1), (-1, -1), (3, -1)):
            px[(x + dx, y + dy)] = '#4f9e3c'
    flowers = [(14, 21, '#f6a6c8'), (47, 14, '#ffffff')]
    for x, y, c in flowers:
        for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)): px[((x + dx) % W, y + dy)] = c
        px[(x, y)] = '#f0b54a'
    return W, H, px

# ---- lawn: a grass tile for the Design Garden, in the home screen's grass green. Only a few
# low-contrast tufts and one tiny flower, so the artwork stays the focus. Tiles in both directions.
def lawn():
    W, H = 128, 96; px = {}
    for y in range(H):
        for x in range(W):
            px[(x, y)] = '#7cc44f'
    for x, y in [(18, 16), (84, 30), (44, 62), (110, 78)]:
        for dx, dy in ((0, 0), (2, 0), (1, -1), (-1, -1), (3, -1)):
            px[((x + dx) % W, (y + dy) % H)] = '#70b947'
    x, y = 66, 84
    for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
        px[((x + dx) % W, (y + dy) % H)] = '#f3e6c4'
    px[(x, y)] = '#f0c96a'
    return W, H, px

# Distance haze: the tree line is blended toward the pale sky so the farmhouse stays the focus
HAZE, FADE = (0xcd, 0xe8, 0xef), {'bg-trees': .45}

def fade(c, a):
    rgb = [int(c[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(v + (hz - v) * a):02x}' for v, hz in zip(rgb, HAZE))

for name, fn in [('bg-mountains', mountains), ('bg-hills', hills), ('bg-trees', trees), ('bg-grass', grass), ('bg-lawn', lawn)]:
    w, h, px = fn()
    px = {k: fade(c, FADE.get(name, 0)) for k, c in px.items()}
    px = {(x % w, y): c for (x, y), c in px.items() if 0 <= y < h}
    open(os.path.join(OUT, name + '.svg'), 'w').write(svg(w, h, px))
    print(name, w, h, len(px))
