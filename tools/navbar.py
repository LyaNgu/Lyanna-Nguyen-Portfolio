"""Cute single-pill navbar (ref: jessicahsu.design): pixel icon + label per link, soft sliding hover.

Rewrites the site <header> on every page in place. Idempotent: python3 tools/navbar.py
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = {  # page: (home href, works href, current link)
    'index.html': ('#top', '#work', 'Home'),
    'about.html': ('index.html', 'index.html#work', 'About'),
    'garden.html': ('index.html', 'index.html#work', 'Garden'),
    'triceratops.html': ('index.html', 'index.html#work', 'Works'),
    'linguistics-club.html': ('index.html', 'index.html#work', 'Works'),
}


def px(rows):
    r = ''.join(f'M{x} {y}h1v1h-1z' for y, row in enumerate(rows) for x, c in enumerate(row) if c == '#')
    return f'<svg viewBox="0 0 {len(rows[0])} {len(rows)}" aria-hidden="true"><path d="{r}"/></svg>'


ICONS = {
    'Home': px(["...##...", "..####..", ".######.", "########", ".##..##.", ".##..##.", ".##..##.", "........"]),
    'Works': px(["###.....", "#..####.", "########", "#......#", "#......#", "#......#", "########", "........"]),
    'About': px(["..####..", ".######.", ".#.##.#.", ".######.", "..####..", ".######.", "########", "........"]),
    'Garden': px(["..#..#..", ".###.##.", "..####..", "...##...", "...##...", "########", ".######.", "........"]),
    'Resume': px(["#####...", "#...##..", "#.....#.", "#.###.#.", "#.....#.", "#.###.#.", "#######.", "........"]),
}


def header(home, works, current):
    def link(href, label, extra=''):
        cur = ' aria-current="page"' if label == current else ''
        return f'<a href="{href}" class="navlinks"{cur}{extra}>{ICONS[label]}<span>{label}</span></a>'
    return f'''<header class="sitenav">
    <nav class="nav-pill topnav" aria-label="Main">
      <span class="nav-hl" aria-hidden="true"></span>
      {link(home, 'Home')}
      {link(works, 'Works')}
      {link('about.html', 'About')}
      {link('garden.html', 'Garden')}
      {link('assets/files/Lyanna_Nguyen_Resume.pdf', 'Resume', ' target="_blank" rel="noopener"')}
    </nav>
  </header>'''


def run():
    for page, args in PAGES.items():
        p = os.path.join(ROOT, page)
        s = open(p, encoding='utf-8').read()
        s, n = re.subn(r'<header class="sitenav[^"]*">.*?</header>', lambda m: header(*args), s, count=1, flags=re.S)
        assert n == 1, page
        open(p, 'w', encoding='utf-8').write(s)


if __name__ == '__main__':
    run()
