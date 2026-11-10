"""Floating three-pill navbar (status pill, centre nav pill, email pill).

Rewrites the site <header> on every page in place. Idempotent: run it after
convert_export.py, or on its own: python3 tools/navbar.py
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMAIL = 'lyannanguyen21@gmail.com'
STATUS = 'Open to UX roles'
PAGES = {  # page: (logo href, works href, current link)
    'index.html': ('#top', '#work', None),
    'about.html': ('index.html', 'index.html#work', 'About'),
    'garden.html': ('index.html', 'index.html#work', 'Design Garden'),
    'triceratops.html': ('index.html', 'index.html#work', 'Works'),
    'linguistics-club.html': ('index.html', 'index.html#work', 'Works'),
}
COPY_IC = ('<svg viewBox="0 0 8 8" aria-hidden="true"><path d="M2 0h6v6H6V1H2zM0 2h5v6H0zM1 3v4h3V3z"/></svg>')


def header(logo, works, current):
    def link(href, label):
        cur = ' aria-current="page"' if label == current else ''
        return f'<a href="{href}" class="navlinks"{cur}>{label}</a>'
    return f'''<header class="sitenav">
    <div class="sitenav-row">
      <span class="nav-pill nav-status"><i class="nav-dot" aria-hidden="true"></i>{STATUS}</span>
      <nav class="nav-pill topnav" aria-label="Main">
        <a href="{logo}" class="nav-logo" aria-label="Lyanna Nguyen, home"><span class="nav-logo-ic"><img class="px" src="assets/images/chibi-head.png" alt="" width="32" height="24"></span><span class="nav-name">Lyanna</span></a>
        {link(works, 'Works')}
        {link('about.html', 'About')}
        {link('garden.html', 'Design Garden')}
        <a href="assets/files/Lyanna_Nguyen_Resume.pdf" target="_blank" rel="noopener" class="nav-cta">Resume</a>
      </nav>
      <button type="button" class="nav-pill nav-email" data-copy="{EMAIL}" aria-label="Copy email address {EMAIL}">{COPY_IC}<span class="nav-email-t">{EMAIL}</span></button>
    </div>
  </header>'''


def run():
    for page, args in PAGES.items():
        p = os.path.join(ROOT, page)
        s = open(p, encoding='utf-8').read()
        s, n = re.subn(r'<header (?:class="sitenav[^"]*"|style="position: sticky;[^"]*")>.*?</header>',
                       lambda m: header(*args), s, count=1, flags=re.S)
        assert n == 1, page
        open(p, 'w', encoding='utf-8').write(s)


if __name__ == '__main__':
    run()
