"""Cute single-pill navbar (ref: jessicahsu.design): pixel icon + label per link, soft sliding hover.

Rewrites the site <header> on every page in place. Idempotent: python3 tools/navbar.py
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = {  # page: (home href, works href, current link)
    'index.html': ('#top', '#work', 'Home'),
    'about.html': ('index.html', 'index.html#work', 'About'),
    'garden.html': ('index.html', 'index.html#work', 'Play'),
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
    'Play': ic('<path class="s" d="M12 20v-7.5"/><path d="M12 12.5C12 8.6 9.3 6 5.5 6c0 3.9 2.7 6.5 6.5 6.5zM12 11c0-3.3 2.4-5.6 6.5-5.6 0 3.4-2.4 5.6-6.5 5.6z"/><path class="s" d="M7.5 20h9"/>'),
    'Resume': ic('<path d="M7 3.5h6.6L18.5 8v11A1.5 1.5 0 0 1 17 20.5H7A1.5 1.5 0 0 1 5.5 19V5A1.5 1.5 0 0 1 7 3.5z"/><path class="s" d="M9 12.5h6M9 15.8h4"/>'),
}


SOUND = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9.5h3.2L12 5.5v13l-4.8-4H4z"/>'
         '<path class="s on" d="M15.5 9a4.2 4.2 0 0 1 0 6M18 6.6a7.6 7.6 0 0 1 0 10.8"/>'
         '<path class="s off" d="M16 9.5l5 5M21 9.5l-5 5"/></svg>')


BOOTH = '<div class="booth" aria-hidden="true"><span class="booth-post l"></span><span class="booth-post r"></span><span class="booth-lights"><i style="left:3.0%;top:10px;--c:#e5645a"></i><i style="left:10.8%;top:24px;--c:#f0b54a"></i><i style="left:18.7%;top:24px;--c:#7cc44f"></i><i style="left:26.5%;top:10px;--c:#7cc0ea"></i><i style="left:34.3%;top:10px;--c:#c9a6ef"></i><i style="left:42.2%;top:24px;--c:#e5645a"></i><i style="left:50.0%;top:24px;--c:#f0b54a"></i><i style="left:57.8%;top:10px;--c:#7cc44f"></i><i style="left:65.7%;top:10px;--c:#7cc0ea"></i><i style="left:73.5%;top:24px;--c:#c9a6ef"></i><i style="left:81.3%;top:24px;--c:#e5645a"></i><i style="left:89.2%;top:10px;--c:#f0b54a"></i><i style="left:97.0%;top:10px;--c:#7cc44f"></i></span><div class="booth-back"><span class="booth-girl"><span class="bob"><img class="px" src="assets/images/chibi-happy.png" alt="" width="32" height="39"></span></span><span class="booth-bubble">Step right up! Come see my catches ✿</span><span class="booth-plant"><svg viewBox="0 0 16 16" shape-rendering="crispEdges"><path fill="#4f9e3c" d="M7 2h2v6H7zM4 4h2v1h1v3H5V7H4zM10 4h2v3h-1v1H9V5h1z"/><path fill="#7cc44f" d="M7 3h1v5H7zM5 5h1v2H5zM10 5h1v2h-1z"/><path fill="#5e2f18" d="M3 8h10v1h-1v6H4V9H3z"/><path fill="#b9764a" d="M4 9h8v1H4zM5 10h6v4H5z"/><path fill="#d6935e" d="M5 10h2v4H5z"/></svg></span><span class="booth-yarn"><svg viewBox="0 0 12 10" shape-rendering="crispEdges"><path fill="#5e2f18" d="M3 1h5v1h2v1h1v4h-1v1H8v1H3V8H2V7H1V3h1V2h1z"/><path fill="#f6a5b8" d="M3 2h5v1h2v4H9v1H3V7H2V3h1z"/><path fill="#fbd0dc" d="M4 3h1v1H4zM6 3h1v1h1v1H6zM4 5h1v1h1v1H4zM8 5h1v1H8z"/><path fill="#e5809a" d="M3 6h1v1h1v1H3zM7 6h2v1H7z"/></svg></span></div><div class="booth-counter"><span></span></div></div>'


def header(home, works, current):
    def link(href, label, extra=''):
        cur = ' aria-current="page"' if label == current else ''
        return f'<a href="{href}" class="navlinks" aria-label="{label}"{cur}{extra}>{ICONS[label]}<span>{label}</span></a>'
    return f'''<header class="sitenav">
    <nav class="nav-pill topnav" aria-label="Main">
      <span class="nav-hl" aria-hidden="true"></span><span class="nav-cur" aria-hidden="true"></span>
      {link(home, 'Home')}
      {link(works, 'Works')}
      {link('about.html', 'About')}
      {link('garden.html', 'Play')}
      {link('assets/files/Lyanna_Nguyen_Resume.pdf', 'Resume', ' target="_blank" rel="noopener"')}
    </nav>
  </header>'''


def run():
    for page, args in PAGES.items():
        p = os.path.join(ROOT, page)
        s = open(p, encoding='utf-8').read()
        s, n = re.subn(r'<header class="sitenav[^"]*">.*?</header>', lambda m: header(*args), s, count=1, flags=re.S)
        assert n == 1, page
        if page in ('index.html', 'about.html', 'garden.html') and '<main' not in s:   # main landmark (WCAG)
            i = s.index('</header>') + len('</header>'); j = s.index('<footer', i)
            s = s[:i] + '\n  <main id="main">' + s[i:j].rstrip() + '\n  </main>\n\n  ' + s[j:]
        # fonts: connect early and load the stylesheet without blocking first paint (font-display: swap)
        FONT = 'https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&amp;family=Pixelify+Sans:wght@400..700&amp;family=VT323&amp;display=swap'
        if 'fonts.gstatic.com' not in s:
            s = s.replace('<link rel="preconnect" href="https://fonts.googleapis.com">',
                          '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>', 1)
        s = s.replace(f'<link href="{FONT}" rel="stylesheet">',
                      f'<link rel="preload" as="style" href="{FONT}"><link href="{FONT}" rel="stylesheet" media="print" onload="this.media=\'all\'"><noscript><link href="{FONT}" rel="stylesheet"></noscript>', 1)
        if page == 'index.html':   # opening animation (~3s): water drop timing
            for old, new in (('1.8s;"', '1.54s;"'), ('1.94s;"', '1.66s;"'), ('2.09s;"', '1.79s;"'), ('2.24s;"', '1.92s;"'),
                             ('0.99s;"', '1.54s;"'), ('1.07s;"', '1.66s;"'), ('1.15s;"', '1.79s;"'), ('1.23s;"', '1.92s;"')):
                s = s.replace('animation-delay: ' + old, 'animation-delay: ' + new)
        # self-hosted pixel fonts, preloaded so they swap in before first paint; Google Fonts now only serves Nunito
        OLDF = 'https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&amp;family=Pixelify+Sans:wght@400..700&amp;family=VT323&amp;display=swap'
        NEWF = 'https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&amp;display=swap'
        s = s.replace(OLDF, NEWF)
        if 'pixelify-sans-latin.woff2' not in s:
            pre = ('<link rel="preload" as="font" type="font/woff2" crossorigin href="assets/fonts/pixelify-sans-latin.woff2">'
                   '<link rel="preload" as="font" type="font/woff2" crossorigin href="assets/fonts/vt323-latin.woff2">\n')
            s = s.replace('<link rel="preconnect" href="https://fonts.googleapis.com">', pre + '<link rel="preconnect" href="https://fonts.googleapis.com">', 1)
        # all fonts self-hosted: drop the Google Fonts links and preload Nunito alongside the pixel fonts
        NEWF2 = 'https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&amp;display=swap'
        s = s.replace(f'<link rel="preload" as="style" href="{NEWF2}"><link href="{NEWF2}" rel="stylesheet" media="print" onload="this.media=\'all\'"><noscript><link href="{NEWF2}" rel="stylesheet"></noscript>', '')
        s = s.replace('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>', '')
        s = re.sub(r'<link rel="preload" as="style" href="https://fonts\.googleapis\.com[^\n]*?</noscript>\n?', '', s)
        s = re.sub(r'<link rel="preconnect" href="https://fonts\.g[^>]*>', '', s)
        if '<noscript' not in s:
            s = s.replace('\n</noscript>\n', '\n')
        if 'nunito-latin.woff2' not in s:
            s = s.replace('<link rel="preload" as="font" type="font/woff2" crossorigin href="assets/fonts/pixelify-sans-latin.woff2">',
                          '<link rel="preload" as="font" type="font/woff2" crossorigin href="assets/fonts/nunito-latin.woff2"><link rel="preload" as="font" type="font/woff2" crossorigin href="assets/fonts/pixelify-sans-latin.woff2">', 1)
        if page == 'about.html' and 'class="booth"' not in s:   # shopkeeper booth on the Catches stall
            s = s.replace('<span class="stall-sign">Lyanna’s Catches</span></div>', '<span class="stall-sign">Lyanna’s Catches</span></div>' + BOOTH, 1)
        if 'js/sfx.js' not in s:
            s = s.replace('<script src="js/site.js"></script>', '<script src="js/site.js"></script>\n<script src="js/sfx.js"></script>', 1)
        s = s.replace('made with &lt;3</span>', 'made with &lt;3 · UI sounds by <a href="https://lolurio.itch.io/" target="_blank" rel="noopener" style="color:inherit">lolurio</a></span>', 1)
        open(p, 'w', encoding='utf-8').write(s)


if __name__ == '__main__':
    run()
