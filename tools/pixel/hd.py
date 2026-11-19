"""Redraw the site's pixel art at twice the resolution, with finer detail.

Each source pixel becomes a 2x2 block, then:
  * outlines are thinned to a single fine pixel and warmed to a red-brown ink;
  * every colour area gets a light rim on its top-left and a shadow rim on its
    bottom-right, plus a second soft shade band on larger areas, for depth;
  * large flat areas get a sparse dither of their shadow tone for texture.

Usage: python3 tools/pixel/hd.py SRC OUT.png  (SRC is a rect-SVG or a PNG)
"""
import re
import sys
from collections import deque

import numpy as np
from PIL import Image

INK = (0x5c, 0x22, 0x14)          # warm red-brown outline, like hand-inked pixel art
DARKS = {(0x2b, 0x15, 0x20)}       # the old plum-black outline colour


def load(path):
    if path.endswith('.svg'):
        s = open(path).read()
        w, h = map(int, re.search(r'viewBox="0 0 (\d+) (\d+)"', s).groups())
        a = np.zeros((h, w, 4), np.uint8)
        for m in re.finditer(r'<rect x="(\d+)" y="(\d+)" width="(\d+)" height="(\d+)" fill="#([0-9a-fA-F]{6})"', s):
            x, y, rw, rh = map(int, m.groups()[:4]); c = m.group(5)
            a[y:y + rh, x:x + rw] = (int(c[:2], 16), int(c[2:4], 16), int(c[4:], 16), 255)
        return a
    return np.array(Image.open(path).convert('RGBA'))


def is_ink(c):
    return c[3] > 0 and (tuple(int(v) for v in c[:3]) in DARKS or sum(int(v) for v in c[:3]) < 150)


def mix(c, t, k):
    return tuple(int(round(int(c[i]) + (t[i] - int(c[i])) * k)) for i in range(3))


def light(c):
    return mix(c, (255, 248, 224), .32)


def shade(c, k=.22):
    # shift shadows warm (toward a plum-brown) instead of plain black
    return mix(c, (70, 30, 40), k)


def hd(src, scale=2, char=False):
    h, w = src.shape[:2]
    S = scale
    ink = np.zeros((h, w), bool); solid = src[..., 3] > 0
    def edge(y, x):
        return any(not (0 <= y + dy < h and 0 <= x + dx < w) or src[y + dy, x + dx, 3] == 0
                   for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)))
    for y in range(h):
        for x in range(w):
            c = src[y, x]
            exact = tuple(int(v) for v in c[:3]) in DARKS
            ink[y, x] = c[3] > 0 and (exact or (sum(int(v) for v in c[:3]) < 200 and edge(y, x)))
    # fill colour for ink pixels: the most common non-ink neighbour
    fillc = src.copy()
    for y in range(h):
        for x in range(w):
            if not ink[y, x]: continue
            cnt = {}
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and solid[yy, xx] and not ink[yy, xx]:
                        k = tuple(src[yy, xx]); cnt[k] = cnt.get(k, 0) + 1
            fillc[y, x] = max(cnt, key=cnt.get) if cnt else (*INK, 255)
    H, W = h * S, w * S
    out = np.zeros((H, W, 4), np.uint8)
    kind = np.zeros((H, W), np.int8)   # 0 empty, 1 fill, 2 ink
    def src_solid(y, x):
        return 0 <= y < h and 0 <= x < w and solid[y, x]
    for y in range(h):
        for x in range(w):
            if not solid[y, x]: continue
            for sy in range(S):
                for sx in range(S):
                    Y, X = y * S + sy, x * S + sx
                    if not ink[y, x]:
                        out[Y, X] = src[y, x]; kind[Y, X] = 1; continue
                    # keep ink only on the side that faces outside, or as a 1px line inside
                    keep = False
                    if sy == 0 and not src_solid(y - 1, x): keep = True
                    if sy == S - 1 and not src_solid(y + 1, x): keep = True
                    if sx == 0 and not src_solid(y, x - 1): keep = True
                    if sx == S - 1 and not src_solid(y, x + 1): keep = True
                    inner = all(src_solid(y + dy, x + dx) for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)))
                    if inner and sy == 0 and sx == 0: keep = True
                    if inner:
                        # a thin interior line: keep the top row if it runs across, left column if down
                        horiz = (ink[y, x - 1] if x > 0 else False) or (ink[y, x + 1] if x < w - 1 else False)
                        vert = (ink[y - 1, x] if y > 0 else False) or (ink[y + 1, x] if y < h - 1 else False)
                        if horiz and sy == 0: keep = True
                        if vert and sx == 0: keep = True
                        if not horiz and not vert: keep = True
                    if keep:
                        own = tuple(int(v) for v in src[y, x, :3])
                        out[Y, X] = (*(INK if own in DARKS else own), 255); kind[Y, X] = 2
                    else:
                        out[Y, X] = fillc[y, x]; kind[Y, X] = 1
    # regions of same fill colour
    reg = -np.ones((H, W), int); sizes = []; rid = 0
    for Y in range(H):
        for X in range(W):
            if kind[Y, X] != 1 or reg[Y, X] >= 0: continue
            c = tuple(out[Y, X]); q = deque([(Y, X)]); reg[Y, X] = rid; n = 0
            while q:
                a, b = q.popleft(); n += 1
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = a + dy, b + dx
                    if 0 <= yy < H and 0 <= xx < W and reg[yy, xx] < 0 and kind[yy, xx] == 1 and tuple(out[yy, xx]) == c:
                        reg[yy, xx] = rid; q.append((yy, xx))
            sizes.append(n); rid += 1
    base = out.copy()
    def other(Y, X, r):
        return not (0 <= Y < H and 0 <= X < W) or reg[Y, X] != r
    for Y in range(H):
        for X in range(W):
            r = reg[Y, X]
            if r < 0 or sizes[r] < 6: continue
            c = tuple(base[Y, X][:3])
            top = other(Y - 1, X, r); left = other(Y, X - 1, r)
            bot = other(Y + 1, X, r); right = other(Y, X + 1, r)
            bot2 = other(Y + 2, X, r); right2 = other(Y, X + 2, r)
            if char: continue
            if (bot or right) and sizes[r] >= 10:
                out[Y, X, :3] = shade(c)
            elif (top or left) and not (bot or right) and sizes[r] >= 10:
                out[Y, X, :3] = light(c)
            elif (bot2 or right2) and sizes[r] >= 60:
                out[Y, X, :3] = shade(c, .11)
            elif sizes[r] >= 120 and (X + Y * 3) % 7 == 0 and (Y // 2 + X) % 3 == 0:
                out[Y, X, :3] = shade(c, .08)
    if char:
        out = char_detail(out, kind, reg, sizes)
    return out


def hx(c):
    return '%02x%02x%02x' % tuple(int(v) for v in c[:3])


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def char_detail(out, kind, reg, sizes):
    """Hand-style finishing for the chibi sprites (they share one palette)."""
    H, W = out.shape[:2]
    o = out.copy()
    col = [[hx(out[Y, X]) if out[Y, X, 3] else None for X in range(W)] for Y in range(H)]
    def at(Y, X):
        return col[Y][X] if 0 <= Y < H and 0 <= X < W else None
    SKIN, BLUSH = 'fad4b6', 'f4968c'
    HAIR, HAIR_MID, HAIR_HI = '1e1828', '2e263a', '4e4260'
    for Y in range(H):
        for X in range(W):
            c = col[Y][X]
            if c is None: continue
            # blush: soft checker dither into the skin instead of a solid bar
            if c == BLUSH and (X + Y) % 2 and (at(Y - 1, X) != BLUSH or at(Y + 1, X) != BLUSH):
                o[Y, X, :3] = rgb(SKIN)
            # hair: fine strands of the mid tone, and 1px sheen under the highlight streaks
            elif c == HAIR and (X - Y) % 5 == 0 and at(Y - 1, X) in (HAIR, HAIR_MID) and at(Y + 1, X) == HAIR:
                o[Y, X, :3] = rgb(HAIR_MID)
            elif c == HAIR_HI and at(Y + 1, X) != HAIR_HI:
                o[Y, X, :3] = mix(rgb(HAIR_HI), (150, 140, 190), .35)
            # eyes: keep a 1px catchlight and add a warm lower iris
            elif c == '3c2224' and at(Y + 1, X) not in ('3c2224', 'ffffff') and at(Y - 1, X) == '3c2224' and at(Y - 2, X) == '3c2224':
                o[Y, X, :3] = rgb('8a5a5a')
            # bandana: darker fold line under the knot and a lighter top rim
            elif c == 'd6463a' and at(Y + 1, X) in ('a02c2e', '5c1e24'):
                o[Y, X, :3] = mix(rgb(c), (90, 20, 30), .2)
            elif c == 'd6463a' and at(Y - 1, X) in ('5c1e24', None):
                o[Y, X, :3] = rgb('f06e58')
    # round the corners of the tiny dark features (closed eyes, mouth) so they read as fine curves
    for Y in range(H):
        for X in range(W):
            c = col[Y][X]
            if c not in ('3c2224', '963c38'): continue
            n = sum(at(Y + dy, X + dx) == c for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)))
            d = sum(at(Y + dy, X + dx) == c for dy, dx in ((-1, -1), (-1, 1), (1, -1), (1, 1)))
            if n == 2 and d == 1 and at(Y - 1, X) == c and at(Y, X - 1) == c and Y % 2 == 1 and X % 2 == 1 and c == '963c38':
                o[Y, X, :3] = rgb(SKIN)
    return o


if __name__ == '__main__':
    a = load(sys.argv[1])
    Image.fromarray(hd(a, char='--char' in sys.argv)).save(sys.argv[2], optimize=True)
    print(sys.argv[2], a.shape[1] * 2, 'x', a.shape[0] * 2)
