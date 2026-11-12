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


def ic(body):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{body}</svg>'


ICONS = {
    'Home': ic('<path d="M4 11.2 12 4.5l8 6.7V19a1.5 1.5 0 0 1-1.5 1.5h-3.8v-5.2a2.7 2.7 0 0 0-5.4 0v5.2H5.5A1.5 1.5 0 0 1 4 19z"/>'),
    'Works': ic('<path d="M3.5 7.5A2.5 2.5 0 0 1 6 5h3.4c.7 0 1.3.3 1.8.8l1.1 1.2H18a2.5 2.5 0 0 1 2.5 2.5v7A2.5 2.5 0 0 1 18 19H6a2.5 2.5 0 0 1-2.5-2.5z"/>'),
    'About': ic('<circle cx="12" cy="12" r="8.5"/><circle class="k" cx="9.2" cy="10.6" r="1.25"/><circle class="k" cx="14.8" cy="10.6" r="1.25"/><path class="s" d="M9 14.2c1.6 1.7 4.4 1.7 6 0"/>'),
    'Garden': ic('<path class="s" d="M12 20v-7.5"/><path d="M12 12.5C12 8.6 9.3 6 5.5 6c0 3.9 2.7 6.5 6.5 6.5zM12 11c0-3.3 2.4-5.6 6.5-5.6 0 3.4-2.4 5.6-6.5 5.6z"/><path class="s" d="M7.5 20h9"/>'),
    'Resume': ic('<path d="M7 3.5h6.6L18.5 8v11A1.5 1.5 0 0 1 17 20.5H7A1.5 1.5 0 0 1 5.5 19V5A1.5 1.5 0 0 1 7 3.5z"/><path class="s" d="M9 12.5h6M9 15.8h4"/>'),
}


def header(home, works, current):
    def link(href, label, extra=''):
        cur = ' aria-current="page"' if label == current else ''
        return f'<a href="{href}" class="navlinks"{cur}{extra}>{ICONS[label]}<span>{label}</span></a>'
    return f'''<header class="sitenav">
    <nav class="nav-pill topnav" aria-label="Main">
      <span class="nav-hl" aria-hidden="true"></span><span class="nav-cur" aria-hidden="true"></span>
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
