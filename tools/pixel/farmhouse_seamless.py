"""Make a copy of the exported farmhouse that stands straight on the hero's grass.

The export draws the house on a boxed patch of lawn with a dark outline. This drops that patch
(everything below the bushes except the garden path) and adds a soft contact shadow instead,
so the page's own grass strip shows through.

    python3 tools/pixel/farmhouse_seamless.py assets/images/a-pixel-farmhouse-with-a-red.svg \
        assets/images/a-pixel-farmhouse-seamless.svg
"""
import re, sys

GROUND_TOP = 46            # first row of the exported lawn patch
PATH = {'#f0b54a', '#c98a3a'}
SHADOW = '#6ab443'         # a shade darker than the page grass (#7cc44f)

src, dst = sys.argv[1], sys.argv[2]
svg = open(src).read()
rect = re.compile(r'<rect x="(\d+)" y="(\d+)" width="(\d+)" height="(\d+)" fill="(#\w+)"\s*/?>(?:</rect>)?')

def keep(m):
    y, fill = int(m.group(2)), m.group(5).lower()
    return y < GROUND_TOP or fill in PATH

kept = [m.group(0) for m in rect.finditer(svg) if keep(m)]
shadow = [f'<rect x="3" y="{GROUND_TOP}" width="21" height="1" fill="{SHADOW}"/>',
          f'<rect x="36" y="{GROUND_TOP}" width="21" height="1" fill="{SHADOW}"/>']
head = svg[:svg.index('<rect')]
open(dst, 'w').write(head + ''.join(shadow + kept) + '</svg>\n')
