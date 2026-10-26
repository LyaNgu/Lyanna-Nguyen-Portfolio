"""Draw the home hero's cottage as a crisp-edged 60x55 pixel SVG.

The door, the two windows and the chimney stay where index.html's overlays expect them:
door x26-33 / y28-41, windows x14-21 and x39-46 / y30-33, chimney top around x42 / y2.

    python3 tools/pixel/cottage.py assets/images/a-pixel-cottage.svg
"""
import sys

W, H = 60, 55
px = {}

C = dict(
    line='#5a3524',                                                  # soft brown outline
    roof='#f2a65a', roofhi='#ffc985', roofsh='#d9803f', roofdk='#b8622f',  # warm thatch shingles
    wall='#f8ead2', wallsh='#ead3b0',                                # cream plaster
    beam='#9a6440', beamdk='#74472b',                                # timber frame
    stone='#c9bfb0', stonedk='#9e9385', chim='#b8aea0', chimdk='#7d7266',
    glass='#ffe9a8', glassdk='#f0c36a', shutter='#e39aa8', shutterdk='#c27383',
    box='#9a6440', pink='#f6a6c8', white='#ffffff', yellow='#ffd85a',
    leaf='#6fbf5a', leafdk='#3f9450', leafhi='#a6d86e',
    awn1='#fff3dc', awn2='#e88a9c', lamp='#ffd27a', lampdk='#2b1520',
    path='#f0b54a', pathdk='#c98a3a', door='#2b1520',
)

def put(x, y, c):
    if 0 <= x < W and 0 <= y < H: px[(x, y)] = C[c]

def rect(x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1): put(x, y, c)

# ---- chimney (behind the roof)
rect(40, 2, 45, 12, 'chim')
for y in range(3, 12, 2):
    for x in range(40 + (y // 2) % 2, 46, 3): put(x, y, 'chimdk')
rect(39, 2, 46, 2, 'line'); rect(39, 3, 39, 12, 'line'); rect(46, 3, 46, 12, 'line')

# ---- main roof: a trapezoid of scalloped thatch shingles
ROOF_TOP, ROOF_BOT = 6, 24
for y in range(ROOF_TOP, ROOF_BOT + 1):
    t = (y - ROOF_TOP) / (ROOF_BOT - ROOF_TOP)
    x0, x1 = round(17 - 13 * t), round(42 + 13 * t)
    for x in range(x0, x1 + 1):
        r = (y - ROOF_TOP) % 3
        k = (x + ((y - ROOF_TOP) // 3) * 2) % 4                     # offset every other row like real shingles
        c = 'roof'
        if r == 2 and k in (0, 3): c = 'roofsh'                     # rounded bottom of each shingle
        if r == 1 and k == 0: c = 'roofsh'                          # seam between shingles
        if r == 0 and k == 2: c = 'roofhi'
        if x - x0 < 2: c = 'roofsh'
        if x1 - x < 2: c = 'roofdk'
        put(x, y, c)
    put(x0 - 1, y, 'line'); put(x1 + 1, y, 'line')
rect(16, ROOF_TOP - 1, 43, ROOF_TOP - 1, 'line')
rect(4, ROOF_BOT + 1, 55, ROOF_BOT + 1, 'roofdk')

# ---- dormer gable with a round attic window
for y in range(9, 22):
    half = (y - 9) * 8 // 12
    for x in range(30 - half - 1, 30 + half + 1):
        put(x, y, 'wall' if y > 11 else 'beam')
    put(30 - half - 2, y, 'roofdk'); put(30 + half + 1, y, 'roofdk')
    put(30 - half - 3, y, 'line'); put(30 + half + 2, y, 'line')
for (x, y) in [(28, 13), (29, 13), (30, 13), (27, 14), (31, 14), (27, 15), (31, 15), (27, 16), (31, 16), (28, 17), (29, 17), (30, 17)]:
    put(x, y, 'beamdk')
rect(28, 14, 30, 16, 'glass'); put(29, 14, 'beamdk'); put(29, 16, 'beamdk'); put(28, 15, 'beamdk'); put(30, 15, 'beamdk')

# ---- walls: cream plaster in a timber frame
WALL_TOP, WALL_BOT = 26, 43
rect(8, WALL_TOP, 51, WALL_BOT, 'wall')
rect(8, WALL_TOP, 51, WALL_TOP, 'wallsh')                             # shade under the eaves
for x in (8, 9, 24, 25, 34, 35, 50, 51): rect(x, WALL_TOP, x, WALL_BOT, 'beam')
rect(8, 36, 51, 36, 'beam')
for x in (9, 25, 35, 51): rect(x, WALL_TOP, x, WALL_BOT, 'beamdk')
for i in range(5):                                                    # diagonal braces
    put(10 + i, 41 - i, 'beam'); put(49 - i, 41 - i, 'beam')
rect(7, WALL_TOP, 7, WALL_BOT, 'line'); rect(52, WALL_TOP, 52, WALL_BOT, 'line')

# ---- windows with rose shutters and flower boxes
for wx in (14, 39):
    rect(wx - 1, 29, wx + 8, 34, 'beamdk')
    rect(wx, 30, wx + 7, 33, 'glass')
    rect(wx, 33, wx + 7, 33, 'glassdk')
    rect(wx + 3, 30, wx + 4, 33, 'beamdk'); rect(wx, 31, wx + 7, 31, 'beamdk')
    rect(wx - 3, 29, wx - 2, 34, 'shutter'); rect(wx + 9, 29, wx + 10, 34, 'shutter')
    put(wx - 2, 31, 'shutterdk'); put(wx + 10, 31, 'shutterdk')
    rect(wx - 1, 35, wx + 8, 36, 'box')
    for i, x in enumerate(range(wx - 1, wx + 9)):
        put(x, 34, ['pink', 'leaf', 'white', 'leaf', 'yellow'][i % 5])

# ---- door frame, arch and striped awning (the door itself is drawn by the page)
rect(26, 28, 33, 41, 'door')
rect(25, 26, 34, 27, 'beamdk')
for x in range(23, 37): put(x, 24, 'awn1' if (x // 2) % 2 else 'awn2'); put(x, 25, 'awn1' if (x // 2) % 2 else 'awn2')
rect(23, 26, 36, 26, 'line')
for x in range(23, 37, 2): put(x, 27, 'awn2')
put(37, 28, 'lampdk'); rect(37, 29, 37, 31, 'lamp'); put(37, 32, 'lampdk')        # little lantern

# ---- climbing ivy on the left corner
for (x, y) in [(10, 38), (11, 37), (10, 36), (11, 35), (12, 34), (11, 33), (10, 32), (11, 31), (12, 30), (11, 29)]:
    put(x, y, 'leafdk'); put(x + 1, y, 'leaf')
put(12, 37, 'pink'); put(13, 31, 'white')

# ---- stone foundation and doorstep
rect(7, 44, 52, 45, 'stone')
for x in range(8, 52, 4): put(x, 45, 'stonedk')
rect(25, 42, 34, 43, 'stone'); rect(25, 43, 34, 43, 'stonedk')

# ---- path that runs into the page's garden path (x24-35)
rect(24, 46, 35, 54, 'path'); rect(24, 46, 24, 54, 'pathdk'); rect(35, 46, 35, 54, 'pathdk')
for (x, y) in [(27, 48), (31, 50), (28, 53), (33, 47)]: put(x, y, 'pathdk')

# ---- flowering bushes that tuck the house into the grass
def bush(x0, x1, top, base=48):
    cx, rx, ry = (x0 + x1) / 2, (x1 - x0) / 2 + .5, base - top
    for x in range(x0, x1 + 1):
        dx = (x + .5 - cx) / rx
        if abs(dx) > 1: continue
        h = base - round(ry * (1 - dx * dx) ** .5 + .3 * ((x * 7) % 3 == 0))
        for y in range(h, base):
            c = 'leafhi' if y == h else 'leafdk' if dx > .45 or y > base - 2 else 'leaf'
            put(x, y, c)
    for i, x in enumerate(range(x0 + 2, x1 - 1, 3)):
        put(x, top + 2 + i % 2, ['pink', 'white', 'yellow'][i % 3])

bush(1, 13, 40); bush(46, 58, 40); bush(17, 22, 43); bush(37, 42, 43)

def svg():
    rows = {}
    for (x, y), c in px.items(): rows.setdefault(y, {})[x] = c
    out = []
    for y in sorted(rows):
        xs = sorted(rows[y]); i = 0
        while i < len(xs):
            x0 = xs[i]; c = rows[y][x0]; j = i
            while j + 1 < len(xs) and xs[j + 1] == xs[j] + 1 and rows[y][xs[j + 1]] == c: j += 1
            out.append(f'<rect x="{x0}" y="{y}" width="{xs[j] - x0 + 1}" height="1" fill="{c}"/>'); i = j + 1
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="360" height="330" '
            f'shape-rendering="crispEdges">' + ''.join(out) + '</svg>\n')

open(sys.argv[1], 'w').write(svg())
