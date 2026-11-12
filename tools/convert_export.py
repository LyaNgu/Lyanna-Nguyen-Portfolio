"""Convert the single-file design export into this static multi-page site.

Usage: python3 tools/convert_export.py path/to/Lyanna_Nguyen_Portfolio_Final.html .

Regenerates the HTML pages, css/ and assets/. The scripts in js/ are hand-written and
are not touched, so keep the data-show / data-action hooks below in sync with them.
"""
import workcards  # noqa: E402  (tools/workcards.py)
import base64, hashlib, html, json, os, re, sys

SRC = sys.argv[1]
OUT = sys.argv[2]
raw = open(SRC, encoding='utf-8').read()
lines = raw.splitlines()
pi = next(i for i, l in enumerate(lines) if l.startswith('<script>window.__PAGES__'))
m = re.match(r'<script>window.__PAGES__ = (.*?);window.__BLOBS__ = (.*);</script>$', lines[pi])
PAGES, BLOBS = json.loads(m.group(1)), json.loads(m.group(2))
HEAD_CSS = re.search(r'<style>\n(.*?)</style>', raw, re.S).group(1)

# Text corrected after the export, per page.
CONTENT_FIXES = {
    # One spelling of the field across the site
    'About': [# Pixel water texture and foam in the fishing scene
              ('background-color: var(--sky); background-image: radial-gradient(ellipse 16px 2px at 50% 50%, #b9e2f7 95%, transparent 100%), radial-gradient(ellipse 10px 2px at 50% 50%, #5ea9d8 95%, transparent 100%); background-size: 96px 44px, 140px 60px; background-position: 0 0, 40px 22px;', "background-color: var(--sky); background-image: url('data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 80 40%27 width=%27320%27 height=%27160%27 shape-rendering=%27crispEdges%27%3E%3Cpath fill=%27%23b9e2f7%27 d=%27M7 2h6v1h-6zM35 2h3v1h-3zM2 7h2v1h-2zM15 7h2v1h-2zM8 12h2v1h-2zM46 12h6v1h-6zM70 12h3v1h-3zM4 17h6v1h-6zM57 17h3v1h-3zM47 22h2v1h-2zM58 22h6v1h-6zM6 27h6v1h-6zM47 27h4v1h-4zM14 32h2v1h-2zM36 32h2v1h-2zM54 32h6v1h-6zM77 32h3v1h-3zM11 37h3v1h-3zM29 37h2v1h-2zM43 37h2v1h-2zM79 37h1v1h-1z%27/%3E%3Cpath fill=%27%235ea9d8%27 d=%27M55 2h6v1h-6zM37 7h2v1h-2zM54 7h6v1h-6zM78 7h2v1h-2zM22 12h3v1h-3zM20 17h6v1h-6zM41 17h2v1h-2zM69 17h2v1h-2zM6 22h2v1h-2zM31 27h3v1h-3z%27/%3E%3Cpath fill=%27%23ffffff%27 d=%27M23 22h2v1h-2zM65 27h2v1h-2zM66 37h4v1h-4z%27/%3E%3C/svg%3E'); background-size: 320px 160px;"),
              ('      <div aria-hidden="true" style="height: 24px; background: var(--gold); box-shadow: inset 0 4px 0 #c98a3a;"></div>', '      <div class="foam" aria-hidden="true"></div>\n      <div aria-hidden="true" style="height: 24px; background: var(--gold); box-shadow: inset 0 4px 0 #c98a3a;"></div>'),
              ('UX/UI design turned out', 'UI/UX design turned out')],
    # Quiet lawn tile for the garden (tools/pixel/backdrop.py)
    'Garden': [# The page title is the page's only heading, so it's the H1
               ('<h2 style="margin: 0; display: flex; align-items: center; gap: 14px; font-family: var(--font-display); font-size: 40px; line-height: 44px; font-weight: 700;">', '<h1 style="margin: 0; display: flex; align-items: center; gap: 14px; font-family: var(--font-display); font-size: 40px; line-height: 44px; font-weight: 700;">'),
               ('>Design Garden</h2>', '>Design Garden</h1>'),
               ('background-image: radial-gradient(circle at 3px 3px, #5aa83a 2.5px, transparent 3px), radial-gradient(circle at 21px 17px, #95d46a 2px, transparent 2.5px); background-size: 38px 30px;',
                'background-image: url(assets/images/bg-lawn.svg); background-size: 512px 384px; image-rendering: pixelated;')],
    'Main': [('>Triceratops Website · Jun 2026 – Present<', '>Triceratops Website · Jun – Oct 2026<'),
             # Works: no subtitle, and the Linguistics card matches its case study summary
             ('\n        <p style="margin: 0; font-size: 20px; line-height: 32px; font-weight: 600; color: var(--ink-muted);">Two case studies, from the first interview to the final handoff.</p>', ''),
             ('>I designed the Opportunities pages that help linguistics students find programs, research and study abroad in one place.<',
              '>Made opportunities 80% easier to find for 150+ students by splitting them into undergrad and grad tracks.<'),
             # Case study tags: the top three skills each project shows
             ('<span class="pp-sticker">Paid Contract</span><span class="pp-sticker">Onboarding</span><span class="pp-sticker">Design + Dev</span>',
              '<span class="pp-sticker">Growth UX</span><span class="pp-sticker">UX Engineering</span><span class="pp-sticker">Product Onboarding</span>'),
             ('<span class="pp-sticker">#Include</span><span class="pp-sticker">User Research</span><span class="pp-sticker">Figma</span>',
              '<span class="pp-sticker">User Research</span><span class="pp-sticker">Info Architecture</span><span class="pp-sticker">Dev Handoff</span>'),
             # Keep the Works card in step with the hand-built case study hero
             ('>Streamlining onboarding to help new members get involved from day one<', '>Streamlining onboarding for new members<'),
             ('>I designed and built a Getting Started page that turns a crowded Discord into a clear first step for new members.<', '>Shipped the club&#8217;s first website in 14 weeks, giving a nearly 5,000-member Discord one clear path to a first hunt.<'),
             # 8-bit backdrop (mountains, hills, tree line, grass tufts) drawn by tools/pixel/backdrop.py
             ('    <div aria-hidden="true" style="position: absolute; left: -10%; right: 30%; bottom: 80px; height: 170px; background: #9fd28a; border-radius: 50% 50% 0 0 / 100% 100% 0 0; box-shadow: inset 0 4px 0 #b8e0a0;"></div>\n    <div aria-hidden="true" style="position: absolute; left: 35%; right: -15%; bottom: 80px; height: 130px; background: #8cc97a; border-radius: 50% 50% 0 0 / 100% 100% 0 0; box-shadow: inset 0 4px 0 #a8d890;"></div>\n',
              '    <div aria-hidden="true" style="position: absolute; left: 0; right: 0; bottom: 120px; height: 144px; background: url(assets/images/bg-mountains.svg) 0 100% / 384px 144px repeat-x; image-rendering: pixelated;"></div>\n    <div aria-hidden="true" style="position: absolute; left: 0; right: 0; bottom: 96px; height: 104px; background: url(assets/images/bg-hills.svg) -60px 100% / 320px 104px repeat-x; image-rendering: pixelated;"></div>\n    <div aria-hidden="true" style="position: absolute; left: 0; right: 0; bottom: 96px; height: 136px; background: url(assets/images/bg-trees.svg) 50% 100% / 512px 136px repeat-x; image-rendering: pixelated;"></div>\n'),
             ('<div aria-hidden="true" style="position: absolute; left: 0; right: 0; bottom: 0; height: 96px; background: var(--grass); box-shadow: inset 0 4px 0 0 #2f7d3a;"></div>',
              '<div aria-hidden="true" style="position: absolute; left: 0; right: 0; bottom: 0; height: 96px; background: url(assets/images/bg-grass.svg) 0 0 / 256px 96px repeat-x, var(--grass); box-shadow: inset 0 4px 0 0 #2f7d3a; image-rendering: pixelated;"></div>')],
}

# Pages rebuilt by hand after the export; the converter never overwrites them.
HAND_BUILT = {'triceratops.html', 'linguistics-club.html'}

FILES = {
    'Main': 'index.html', 'About': 'about.html', 'Garden': 'garden.html',
    'CaseStudy-Linguistics': 'linguistics-club.html', 'CaseStudy-Include': 'triceratops.html',
}
EXT = {'image/png': 'png', 'image/webp': 'webp', 'image/jpeg': 'jpg', 'image/svg+xml': 'svg',
       'font/woff2': 'woff2', 'application/pdf': 'pdf', 'image/gif': 'gif'}
DATA_RE = re.compile(r'data:([\w/+.-]+);base64,([A-Za-z0-9+/=]+)')

# ---------------------------------------------------------------- assets
# Names for assets that carry no alt text (keyed by the first 8 hex chars of their SHA-1).
RENAME = {
    '201fccc2': 'icon-letter', '2f082456': 'icon-sprout', 'ac6f105f': 'icon-watering-can',
    'ccdde39b': 'icon-heart', 'e45a9f71': 'icon-download', '5992af6d': 'cursor-arrow',
    'fdf5557d': 'cursor-pointer', '7c86bcb0': 'chibi-head', '9da8c471': 'chibi-happy',
    '29114d32': 'chibi-love', '07eea9b8': 'chibi-calm', '555f11e1': 'chibi-wow', '462f02dc': 'chibi-wink',
    '6e5b7e5b': 'sticker-triceratops-blue', 'b818ba6d': 'sticker-triceratops-yellow',
    '5431050c': 'triceratops-hero-background',
    '252790e8': 'proto-lin-ucd-logo', '079cb268': 'proto-wug-a', 'd310a7b8': 'proto-wug-b',
    '6e1ec4ed': 'proto-wug-c', '8eb13b4f': 'proto-wug-small-a', '54bf9d1c': 'proto-wug-small-b',
    '8778bee1': 'proto-footer-wave-mobile', '346694bd': 'proto-footer-wave-desktop',
    'e01cc607': 'proto-band-mobile', '6d812d98': 'proto-band-desktop', 'bcc16d34': 'proto-map-kerr-hall',
    '3c5a3b2f': 'proto-clr', 'd945017a': 'proto-global-affairs', '057b3758': 'proto-linguistics-major',
    'f7341629': 'proto-ferreiralab', '1e652af7': 'proto-phd', '86f24728': 'proto-ma',
    'f91a5b8b': 'proto-governing-committee', '25092d86': 'proto-phonetics-lab',
    'b53c9b1d': 'hanken-grotesk-400', '4b14b5c9': 'hanken-grotesk-500', 'a16cd99a': 'hanken-grotesk-600',
    '1f8766dd': 'hanken-grotesk-700', '39c01c25': 'gochi-hand',
}
assets = {}      # sha -> relative path from site root
used_names = set()

def slug(t):
    t = re.sub(r"[’']", '', t.lower())
    t = re.sub(r'[^a-z0-9]+', '-', t).strip('-')
    return '-'.join(t.split('-')[:6])[:48].strip('-')

def save(mime, b64, hint=''):
    data = base64.b64decode(b64)
    h = hashlib.sha1(data).hexdigest()
    if h in assets:
        return assets[h]
    ext = EXT[mime]
    folder = {'woff2': 'fonts', 'pdf': 'files'}.get(ext, 'images')
    if ext == 'pdf':
        name = 'Lyanna_Nguyen_Resume'
    else:
        name = RENAME.get(h[:8]) or slug(hint) or ('img-' + h[:8])
        if name in used_names:
            name = name + '-' + h[:6]
    used_names.add(name)
    if ext == 'svg':
        txt = data.decode('utf-8')
        if 'shape-rendering' not in txt[:300]:
            txt = re.sub(r'<svg\b', '<svg shape-rendering="crispEdges"', txt, count=1)
        data = txt.encode('utf-8')
    rel = f'assets/{folder}/{name}.{ext}'
    os.makedirs(os.path.join(OUT, 'assets', folder), exist_ok=True)
    open(os.path.join(OUT, rel), 'wb').write(data)
    assets[h] = rel
    return rel

# Find a human hint for every blob: alt text of the first <img> that uses it.
hints = {}
for P in PAGES.values():
    for tag in re.findall(r'<img\b[^>]*>', P['tpl']):
        sm = re.search(r'src="/_blob/([0-9a-f]{32})"', tag)
        am = re.search(r'alt="([^"]+)"', tag)
        if sm and am and sm.group(1) not in hints:
            hints[sm.group(1)] = html.unescape(am.group(1))
blob_path = {}
for bid, uri in BLOBS.items():
    mm = DATA_RE.match(uri)
    blob_path[bid] = save(mm.group(1), mm.group(2), hints.get(bid, ''))

def resolve_blobs(s, prefix=''):
    return re.sub(r'/_blob/([0-9a-f]{32})', lambda mm: prefix + blob_path[mm.group(1)], s)

# ---------------------------------------------------------------- template helpers
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
TOKEN = re.compile(r'<!--.*?-->|<(/?)([a-zA-Z][\w:-]*)((?:[^>"\']|"[^"]*"|\'[^\']*\')*?)(/?)>', re.S)

def add_attr_to_top_level(fragment, attrs):
    """Add `attrs` to every top-level element of an HTML fragment."""
    out, depth, pos = [], 0, 0
    for t in TOKEN.finditer(fragment):
        between = fragment[pos:t.start()]
        if depth == 0 and between.strip():
            raise ValueError('bare text in sc-if: %r' % between[:80])
        out.append(between)
        pos = t.end()
        tok = t.group(0)
        if tok.startswith('<!--'):
            out.append(tok); continue
        closing, name, selfclose = t.group(1), t.group(2).lower(), t.group(4)
        if closing:
            depth -= 1; out.append(tok); continue
        if depth == 0:
            if name == 'sc-if':
                raise ValueError('nested sc-if at top level')
            tok = tok[:1 + len(t.group(2))] + attrs + tok[1 + len(t.group(2)):]
        out.append(tok)
        if not selfclose and name not in VOID:
            depth += 1
    tail = fragment[pos:]
    if depth == 0 and tail.strip():
        raise ValueError('bare text in sc-if tail: %r' % tail[:80])
    out.append(tail)
    return ''.join(out)

def convert_scif(tpl, shows):
    """Replace <sc-if value="{{x}}"> blocks with data-show markers (innermost first)."""
    pat = re.compile(r'<sc-if value="\{\{([^}]+)\}\}"[^>]*>((?:(?!<sc-if\b).)*?)</sc-if>', re.S)
    while True:
        mm = pat.search(tpl)
        if not mm:
            break
        expr, body = mm.group(1).strip(), mm.group(2)
        name, initial = shows[expr]
        attrs = f' data-show="{name}"' + ('' if initial else ' hidden')
        tpl = tpl[:mm.start()] + add_attr_to_top_level(body, attrs) + tpl[mm.end():]
    return tpl

def fill(tpl, values, actions):
    def ev(mm):
        attr, expr = mm.group(1), mm.group(2).strip()
        rep = actions[expr]
        return rep if rep else ''
    tpl = re.sub(r'\s(on[A-Za-z]+)="\{\{([^}]+)\}\}"', lambda mm: (' ' + ev(mm)) if ev(mm) else '', tpl)
    def hole(mm):
        k = mm.group(1).strip()
        if k not in values:
            raise KeyError(k)
        return html.escape(str(values[k]), quote=True)
    return re.sub(r'\{\{([^}]+)\}\}', hole, tpl)

def fix_links(tpl):
    def link(mm):
        page, hash_ = mm.group(1), mm.group(2) or ''
        return 'href="' + FILES[page] + hash_ + '"'
    tpl = re.sub(r'href="([\w-]+)\.dc\.html(#[\w-]*)?"', link, tpl)
    # "Works"/"Contact" links on sub pages pointed at the home page top; send them to their sections.
    tpl = re.sub(r'href="index\.html"([^>]*>)Works<', r'href="index.html#work"\1Works<', tpl)
    tpl = re.sub(r'href="index\.html"([^>]*>)Contact<', r'href="index.html#contact"\1Contact<', tpl)
    return tpl

def clean(tpl):
    def cls(mm):
        v = ' '.join(mm.group(1).split())
        return f' class="{v}"' if v else ''
    tpl = re.sub(r' class="([^"]*)"', cls, tpl)
    tpl = re.sub(r'\s+hint-placeholder-val="[^"]*"', '', tpl)
    tpl = re.sub(r'[ \t]+\n', '\n', tpl)
    tpl = re.sub(r'\n{3,}', '\n\n', tpl)
    return tpl.strip('\n')

# ---------------------------------------------------------------- per-page config
def toc_values():
    v = {}
    for i, k in enumerate(['overview', 'challenge', 'research', 'process', 'solution', 'results', 'reflect']):
        on = i == 0
        v[f'toc.{k}.cur'] = 'location' if on else 'false'
        v[f'toc.{k}.fw'] = '800' if on else '600'
        v[f'toc.{k}.col'] = 'var(--ink)' if on else 'var(--ink-muted)'
    return v

CONFIG = {
    'Main': dict(
        values={'rootCls': '', 'cls.top': '', 'cls.work': '', 'cls.resume': '', 'doorAria': 'Knock on the door',
                'doorCls': '', 'doorOpen': 'none', 'girlCls': '', 'typed': '', 'envCls': '', 'mailAria': 'false'},
        shows={'loader': ('loader', False), 'knocking': ('knocking', False), 'showHint': ('knock-hint', True),
               'greeted': ('greeted', False), 'showNext': ('dialog-next', False),
               'showChoices': ('dialog-choices', False), 'mailClosed': ('mail-closed', True),
               'mailOpen': ('mail-open', False)},
        actions={'skipLoader': 'data-action="skip-loader"', 'knock': 'data-action="knock"', 'houseKey': '',
                 'dlgClick': 'data-action="dialog-advance"', 'next': 'data-action="dialog-next"',
                 'startTour': 'data-action="close-dialog"', 'closeTalk': 'data-action="close-dialog"',
                 'toggleMail': 'data-action="toggle-mail"'},
    ),
    'About': dict(
        values={'rootCls': '', 'cls.about': '', **{f'songs.s{i}.aria': 'false' for i in range(4)}},
        shows={'coverOk': ('cover', True), **{f'songs.s{i}.on': (f'song-{i}', False) for i in range(4)}},
        actions={f'songs.s{i}.toggle': f'data-action="toggle-song" data-song="{i}"' for i in range(4)},
    ),
    'Garden': dict(
        values={'rootCls': '', 'cls.playground': '',
                **{f'tabs.{k}.{p}': v for k in ['all', 'visual', 'illus', 'photo', 'motion']
                   for p, v in zip(['pressed', 'bg', 'fg'],
                                   ['true', 'var(--wood)', 'var(--on-wood)'] if k == 'all'
                                   else ['false', 'var(--surface-raised)', 'var(--ink)'])}},
        shows={f'pg.{k}': (f'cat-{k}', True) for k in ['visual', 'illus', 'photo', 'motion']},
        actions={f'tabs.{k}.pick': f'data-action="filter" data-filter="{k}"'
                 for k in ['all', 'visual', 'illus', 'photo', 'motion']},
    ),
}
CS = dict(
    values={'rootCls': '', 'markTop': '0px', 'baCls': '', 'baBefore': 'true', 'baAfter': 'false',
            'resAria': 'false', 'resLbl': '▸ See', **toc_values()},
    shows={'resOpen': ('research-more', False), 'showTop': ('back-to-top', False)},
    actions={},
)
CONFIG['CaseStudy-Linguistics'] = CS
CONFIG['CaseStudy-Include'] = CS

# ---------------------------------------------------------------- CSS
main_css = PAGES['Main']['css']
cs_css = PAGES['CaseStudy-Include']['css']
for n in ('About', 'Garden'):
    assert PAGES[n]['css'] == main_css, n
assert PAGES['CaseStudy-Linguistics']['css'] == cs_css

def css_assets(css, prefix):
    css = resolve_blobs(css, prefix)
    return DATA_RE.sub(lambda mm: prefix + save(mm.group(1), mm.group(2)), css)

main_lines, cs_lines = main_css.split('\n'), cs_css.split('\n')
# The case-study sheet is the shared sheet with a few extra rules; split them out.
extra = []
for l in cs_lines:
    if l not in main_lines:
        extra.append(l)
shared_line5 = next(l for l in main_lines if l.startswith('.dlg{'))
dlg_core, dlg_media = shared_line5.split('@media', 1)
for i, l in enumerate(extra):
    if l.startswith(dlg_core):
        extra[i] = l[len(dlg_core):]
os.makedirs(os.path.join(OUT, 'css'), exist_ok=True)
open(os.path.join(OUT, 'css', 'pixel-pals.css'), 'w').write(
    '/* Pixel Pals — cozy farm design-system components. */\n' + HEAD_CSS.strip() + '\n')
site_css = css_assets(main_css, '../').strip()
site_css = site_css.replace(':root{', '/* Design tokens */\n:root{', 1)
# Loader backdrop: replace the custom-property mask reveal, which mobile Safari renders transparent.
site_css = site_css.replace("@property --ldr-r{syntax:'<length>';inherits:false;initial-value:0px}\n@keyframes ldrReveal{0%,80%{--ldr-r:0px}100%{--ldr-r:calc(120vmax + 160px)}}\n.ldr-bg{-webkit-mask-image:radial-gradient(circle at 50% 46%,transparent calc(var(--ldr-r) - 160px),#000 var(--ldr-r));mask-image:radial-gradient(circle at 50% 46%,transparent calc(var(--ldr-r) - 160px),#000 var(--ldr-r));animation:ldrReveal 3.6s cubic-bezier(.5,0,.3,1) both}\n@supports not (mask-image:radial-gradient(circle,#000,#000)){.ldr-bg{animation:ldrFade 3.6s linear both}}",
                            '/* Backdrop reveal: a growing hole whose solid surround is a box-shadow. Avoids animating a\n   custom property inside a mask, which mobile Safari renders as fully transparent. */\n@keyframes ldrHole{0%,80%{width:0;height:0}100%{width:300vmax;height:300vmax}}\n.ldr-bg{right:auto!important;bottom:auto!important;left:50%!important;top:46%!important;width:0;height:0;border-radius:50%;transform:translate(-50%,-50%);background:radial-gradient(closest-side,rgba(207,234,250,0) 70%,#cfeafa 100%)!important;box-shadow:0 0 0 150vmax #cfeafa;animation:ldrHole 3.6s cubic-bezier(.5,0,.3,1) both}', 1)
# Let the dialogue box grow for long lines instead of clipping the Next button.
# Opening animation, reworked with the basic motion principles: the seed falls under gravity,
# squashes and bounces; the can arcs in, tips back before pouring and overshoots on the way back;
# drops stretch as they fall; the sprout squashes up, overshoots and settles; the bloom pops and settles.
LOADER_MOTION = {
    '@keyframes ldrSeed{': '@keyframes ldrSeed{0%{transform:translateY(-40px) scale(.9,1.15);opacity:0;animation-timing-function:cubic-bezier(.55,0,1,.45)}6%{opacity:1}22%{transform:translateY(160px) scale(1.25,.72);animation-timing-function:cubic-bezier(.2,.8,.4,1)}27%{transform:translateY(149px) scale(.94,1.08);animation-timing-function:cubic-bezier(.55,0,1,.45)}32%{transform:translateY(160px) scale(1.12,.88);animation-timing-function:ease-out}36%{transform:translateY(160px)}42%{transform:translateY(168px);opacity:1}56%,100%{transform:translateY(168px);opacity:0}}',
    '@keyframes ldrCan{': '@keyframes ldrCan{0%,36%{transform:translate(80px,-16px);opacity:0;animation-timing-function:cubic-bezier(.2,.8,.4,1)}40%{transform:translate(34px,-14px);opacity:1;animation-timing-function:cubic-bezier(.3,0,.3,1)}44%{transform:none;opacity:1;animation-timing-function:ease-in-out}48%{transform:rotate(7deg)}54%,72%{transform:rotate(-32deg);animation-timing-function:cubic-bezier(.3,0,.2,1)}78%{transform:rotate(6deg);animation-timing-function:ease-in-out}83%{transform:rotate(0);opacity:1;animation-timing-function:cubic-bezier(.55,0,1,.45)}92%,100%{transform:translateX(80px);opacity:0}}',
    '@keyframes ldrDrop{': '@keyframes ldrDrop{0%{transform:translateY(0) scale(.9,1);opacity:0}15%{opacity:1}100%{transform:translateY(56px) scale(.75,1.45);opacity:0}}',
    '@keyframes ldrSprout{': '@keyframes ldrSprout{0%,54%{transform:scale(0);animation-timing-function:cubic-bezier(.2,.8,.4,1)}60%{transform:scale(.55,.3);animation-timing-function:cubic-bezier(.3,0,.4,1)}67%{transform:scale(.62,.9);animation-timing-function:cubic-bezier(.2,.8,.4,1)}73%{transform:scale(1.06,1.12);animation-timing-function:ease-in-out}79%{transform:scale(.97,.95)}84%,100%{transform:scale(1)}}',
    '@keyframes ldrBloom{': '@keyframes ldrBloom{0%,80%{transform:scale(0);opacity:0;animation-timing-function:cubic-bezier(.2,.8,.4,1)}86%{transform:scale(1.3);opacity:1;animation-timing-function:ease-in-out}90%{transform:scale(.9);opacity:1}94%{transform:scale(1.05)}97%,100%{transform:scale(1);opacity:1}}',
}
_lines = site_css.split('\n')
for _i, _l in enumerate(_lines):
    for _k, _v in LOADER_MOTION.items():
        if _l.startswith(_k):
            _lines[_i] = _v
site_css = '\n'.join(_lines)
assert all(v in site_css for v in LOADER_MOTION.values())
# Opening plays in 3.5s: every loader timing scaled to 3.5/3.6 (js/home.js hides it at 3550ms)
LOADER_SPEED = [('3.6s steps(36)', '3.5s steps(35)'), ('ldrBar 3s steps(15)', 'ldrBar 2.9s steps(15)'),
                ('ldrFade 3.6s', 'ldrFade 3.5s'), ('ldrHole 3.6s', 'ldrHole 3.5s'), ('ldrDrop .45s steps(5) 2', 'ldrDrop .44s steps(5) 2')]
for _a, _b in LOADER_SPEED:
    assert _a in site_css, _a
    site_css = site_css.replace(_a, _b)
site_css = site_css.replace('.dlg{height:192px;', '.dlg{min-height:192px;', 1)
site_css = site_css.replace('@media (max-width:760px){.dlg{height:240px}', '@media (max-width:760px){.dlg{min-height:240px}', 1)
site_css += ('\n\n/* Dialogue: the box grows to fit long lines; a hidden copy of the full line reserves the space\n'
             '   before it finishes typing, so the box never resizes mid-sentence. */\n'
             '.dlg-text>p{display:grid}.dlg-ghost,.dlg-shown{grid-area:1/1}.dlg-ghost{visibility:hidden}\n'
             '/* The portrait keeps one size whatever the line length; only the text box grows */\n'
             '.dlg-port{align-self:start}.dlg-port>div:first-child{flex:none!important;height:122px}\n')
site_css += ('\n/* Opening: squash and stretch from the base; drops fall under gravity */\n'
             '.ldr-seed{transform-origin:50% 100%}.ldr-drop{animation-timing-function:cubic-bezier(.55,0,1,.45)}\n')
site_css += '\n/* Elements toggled by the page scripts */\n[hidden]{display:none!important}\n'
site_css += workcards.CSS
site_css += '\n/* The fish sprite faces left but jumps to the right: mirror it so it leaps head-first */\n.fishjump svg{transform:scaleX(-1)}\n'
site_css += '\n/* About: pixel water texture, white foam where the water meets the sand, pixel ripples at the bobber */\n.foam{height:24px;margin-top:-24px;position:relative;background:url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 40 6\' width=\'160\' height=\'24\' shape-rendering=\'crispEdges\'%3E%3Cpath fill=\'%23d7f0fb\' d=\'M0 5h1v1h-1zM1 5h1v1h-1zM2 5h1v1h-1zM3 5h1v1h-1zM4 5h1v1h-1zM5 5h1v1h-1zM6 5h1v1h-1zM7 5h1v1h-1zM8 5h1v1h-1zM9 5h1v1h-1zM10 5h1v1h-1zM11 5h1v1h-1zM12 5h1v1h-1zM13 5h1v1h-1zM14 5h1v1h-1zM15 5h1v1h-1zM16 5h1v1h-1zM17 5h1v1h-1zM18 5h1v1h-1zM19 5h1v1h-1zM20 5h1v1h-1zM21 5h1v1h-1zM22 5h1v1h-1zM23 5h1v1h-1zM24 5h1v1h-1zM25 5h1v1h-1zM26 5h1v1h-1zM27 5h1v1h-1zM28 5h1v1h-1zM29 5h1v1h-1zM30 5h1v1h-1zM31 5h1v1h-1zM32 5h1v1h-1zM33 5h1v1h-1zM34 5h1v1h-1zM35 5h1v1h-1zM36 5h1v1h-1zM37 5h1v1h-1zM38 5h1v1h-1zM39 5h1v1h-1z\'/%3E%3Cpath fill=\'%23ffffff\' d=\'M0 3h1v2h-1zM1 3h1v2h-1zM2 3h1v2h-1zM3 2h1v3h-1zM4 2h1v3h-1zM5 1h1v4h-1zM6 1h1v4h-1zM7 2h1v3h-1zM8 2h1v3h-1zM9 2h1v3h-1zM10 3h1v2h-1zM11 3h1v2h-1zM12 3h1v2h-1zM13 2h1v3h-1zM14 2h1v3h-1zM15 1h1v4h-1zM16 1h1v4h-1zM17 2h1v3h-1zM18 2h1v3h-1zM19 2h1v3h-1zM20 3h1v2h-1zM21 3h1v2h-1zM22 3h1v2h-1zM23 2h1v3h-1zM24 2h1v3h-1zM25 1h1v4h-1zM26 1h1v4h-1zM27 2h1v3h-1zM28 2h1v3h-1zM29 2h1v3h-1zM30 3h1v2h-1zM31 3h1v2h-1zM32 3h1v2h-1zM33 2h1v3h-1zM34 2h1v3h-1zM35 1h1v4h-1zM36 1h1v4h-1zM37 2h1v3h-1zM38 2h1v3h-1zM39 2h1v3h-1z\'/%3E%3C/svg%3E") 0 100%/160px 24px repeat-x;image-rendering:pixelated;animation:foamdrift 6s steps(10) infinite alternate}\n@keyframes foamdrift{to{background-position:40px 100%}}\n.ripple{border:0!important;border-radius:0!important;box-shadow:none!important;height:4px!important;background:linear-gradient(90deg,#fff6d8 0 20%,transparent 20% 80%,#fff6d8 80%)}\n@media (prefers-reduced-motion:reduce){.foam{animation:none}}\n'
site_css += '\n/* Touch targets: header, footer, menu and filter controls reach 44px on touch and narrow screens */\n@media (max-width:900px),(pointer:coarse){\nheader a[href="index.html"],header a[href="#top"]{min-height:44px}\n.topnav .navlinks{padding-top:11px!important;padding-bottom:11px!important}\nfooter nav a{display:flex!important;align-items:center;min-height:44px;box-sizing:border-box}\n.pp-btn.navburger{width:44px;height:44px}\n[data-action="filter"]{min-height:44px}\n}\n'
site_css += '\n/* Phone menu: a pixel plank button with a pixel hamburger / X, and a dropdown panel (js/site.js) */\n.navburger{display:none}\n@media (max-width:760px){\n.pp-btn.navburger{display:inline-grid;place-items:center;width:40px;height:36px;margin-left:12px;padding:0}\n.navburger svg{width:20px;height:16px;fill:var(--wood-dark);shape-rendering:crispEdges}\n.navburger .nb-close{width:18px;height:16px}\n.navburger[aria-expanded="true"] .nb-open,.navburger[aria-expanded="false"] .nb-close{display:none}\n.navpanel{position:absolute;left:0;right:0;top:100%;display:flex;flex-direction:column;padding:6px 20px 14px;background:var(--surface-raised);border-bottom:4px solid var(--wood);box-shadow:0 3px 0 var(--wood-dark);font-family:var(--font-pixel);font-size:22px;letter-spacing:.04em;text-transform:uppercase}\n.navpanel[hidden]{display:none}\n.navpanel .navlinks{display:block!important;padding:12px 4px!important;border-bottom:2px dashed var(--surface-sunken)}\n.navpanel .navlinks:last-child{border-bottom:0}\n}\n'
site_css += '\n/* About: Lyanna\'s Catches awning redrawn as pixel art (shaded stripes, stepped flaps, a notched plank sign) */\n.stall-awning{height:72px;background:url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 32 18\' width=\'32\' height=\'18\' shape-rendering=\'crispEdges\'%3E%3Crect x=\'0\' y=\'0\' width=\'16\' height=\'18\' fill=\'%23f8ebc4\'/%3E%3Crect x=\'0\' y=\'0\' width=\'16\' height=\'1\' fill=\'%23fff7e0\'/%3E%3Crect x=\'1\' y=\'1\' width=\'2\' height=\'13\' fill=\'%23fff7e0\'/%3E%3Crect x=\'14\' y=\'1\' width=\'2\' height=\'17\' fill=\'%23ead7a8\'/%3E%3Crect x=\'0\' y=\'13\' width=\'16\' height=\'5\' fill=\'%23ead7a8\'/%3E%3Crect x=\'0\' y=\'17\' width=\'16\' height=\'1\' fill=\'%23dcc48e\'/%3E%3Crect x=\'16\' y=\'0\' width=\'16\' height=\'18\' fill=\'%23f0cf86\'/%3E%3Crect x=\'16\' y=\'0\' width=\'16\' height=\'1\' fill=\'%23f9e2ad\'/%3E%3Crect x=\'17\' y=\'1\' width=\'2\' height=\'13\' fill=\'%23f9e2ad\'/%3E%3Crect x=\'30\' y=\'1\' width=\'2\' height=\'17\' fill=\'%23ddb565\'/%3E%3Crect x=\'16\' y=\'13\' width=\'16\' height=\'5\' fill=\'%23ddb565\'/%3E%3Crect x=\'16\' y=\'17\' width=\'16\' height=\'1\' fill=\'%23c99e4e\'/%3E%3C/svg%3E") center top/128px 72px repeat-x;image-rendering:pixelated;box-shadow:0 -4px 0 var(--wood-dark),-4px 0 0 var(--wood-dark),4px 0 0 var(--wood-dark)}\n.stall-awning::after{bottom:-24px;height:24px;background:url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 32 6\' width=\'32\' height=\'6\' shape-rendering=\'crispEdges\'%3E%3Crect x=\'0\' y=\'0\' width=\'16\' height=\'1\' fill=\'%23f8ebc4\'/%3E%3Crect x=\'0\' y=\'1\' width=\'16\' height=\'1\' fill=\'%23f8ebc4\'/%3E%3Crect x=\'1\' y=\'2\' width=\'14\' height=\'1\' fill=\'%23f8ebc4\'/%3E%3Crect x=\'2\' y=\'3\' width=\'12\' height=\'1\' fill=\'%23ead7a8\'/%3E%3Crect x=\'4\' y=\'4\' width=\'8\' height=\'1\' fill=\'%23ead7a8\'/%3E%3Crect x=\'0\' y=\'0\' width=\'16\' height=\'1\' fill=\'%23ead7a8\'/%3E%3Crect x=\'0\' y=\'2\' width=\'1\' height=\'1\' fill=\'%235e2f18\'/%3E%3Crect x=\'15\' y=\'2\' width=\'1\' height=\'1\' fill=\'%235e2f18\'/%3E%3Crect x=\'1\' y=\'3\' width=\'1\' height=\'1\' fill=\'%235e2f18\'/%3E%3Crect x=\'14\' y=\'3\' width=\'1\' height=\'1\' fill=\'%235e2f18\'/%3E%3Crect x=\'2\' y=\'4\' width=\'2\' height=\'1\' fill=\'%235e2f18\'/%3E%3Crect x=\'12\' y=\'4\' width=\'2\' height=\'1\' fill=\'%235e2f18\'/%3E%3Crect x=\'4\' y=\'5\' width=\'8\' height=\'1\' fill=\'%235e2f18\'/%3E%3Crect x=\'5\' y=\'4\' width=\'6\' height=\'1\' fill=\'%23dcc48e\'/%3E%3Crect x=\'16\' y=\'0\' width=\'16\' height=\'1\' fill=\'%23f0cf86\'/%3E%3Crect x=\'16\' y=\'1\' width=\'16\' height=\'1\' fill=\'%23f0cf86\'/%3E%3Crect x=\'17\' y=\'2\' width=\'14\' height=\'1\' fill=\'%23f0cf86\'/%3E%3Crect x=\'18\' y=\'3\' width=\'12\' height=\'1\' fill=\'%23ddb565\'/%3E%3Crect x=\'20\' y=\'4\' width=\'8\' height=\'1\' fill=\'%23ddb565\'/%3E%3Crect x=\'16\' y=\'0\' width=\'16\' height=\'1\' fill=\'%23ddb565\'/%3E%3Crect x=\'16\' y=\'2\' width=\'1\' height=\'1\' fill=\'%235e2f18\'/%3E%3Crect x=\'31\' y=\'2\' width=\'1\' height=\'1\' fill=\'%235e2f18\'/%3E%3Crect x=\'17\' y=\'3\' width=\'1\' height=\'1\' fill=\'%235e2f18\'/%3E%3Crect x=\'30\' y=\'3\' width=\'1\' height=\'1\' fill=\'%235e2f18\'/%3E%3Crect x=\'18\' y=\'4\' width=\'2\' height=\'1\' fill=\'%235e2f18\'/%3E%3Crect x=\'28\' y=\'4\' width=\'2\' height=\'1\' fill=\'%235e2f18\'/%3E%3Crect x=\'20\' y=\'5\' width=\'8\' height=\'1\' fill=\'%235e2f18\'/%3E%3Crect x=\'21\' y=\'4\' width=\'6\' height=\'1\' fill=\'%23c99e4e\'/%3E%3C/svg%3E") center top/128px 24px repeat-x;background-repeat:repeat-x;image-rendering:pixelated;filter:none}\n.stall-sign{top:-30px;transform:none;padding:6px 26px 4px;background:none;border:16px solid transparent;border-image:url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 8 8\' width=\'8\' height=\'8\' shape-rendering=\'crispEdges\'%3E%3Crect x=\'1\' y=\'0\' width=\'6\' height=\'1\' fill=\'%235e2f18\'/%3E%3Crect x=\'0\' y=\'1\' width=\'1\' height=\'6\' fill=\'%235e2f18\'/%3E%3Crect x=\'7\' y=\'1\' width=\'1\' height=\'6\' fill=\'%235e2f18\'/%3E%3Crect x=\'1\' y=\'7\' width=\'6\' height=\'1\' fill=\'%235e2f18\'/%3E%3Crect x=\'1\' y=\'1\' width=\'6\' height=\'6\' fill=\'%23a0522a\'/%3E%3Crect x=\'1\' y=\'1\' width=\'6\' height=\'1\' fill=\'%23c8743c\'/%3E%3Crect x=\'1\' y=\'6\' width=\'6\' height=\'1\' fill=\'%237a3d1f\'/%3E%3C/svg%3E") 3 fill/16px/0 stretch;image-rendering:pixelated;box-shadow:none;filter:drop-shadow(4px 4px 0 var(--pixel-shadow));margin:-16px;font-family:var(--font-display);text-shadow:2px 2px 0 #5e2f18;letter-spacing:.02em}\n.stall-sign::before,.stall-sign::after{content:"";position:absolute;top:50%;width:6px;height:6px;margin-top:-3px;background:#e8c27a;box-shadow:0 0 0 2px #5e2f18}\n.stall-sign::before{left:-6px}.stall-sign::after{right:-6px}\n/* About: no white fade at the sides of the catches rows */\n.stall-marquee{-webkit-mask-image:none;mask-image:none}\n'
site_css += "/* About: whole awning stripes and flaps at both ends, and photo rows clipped inside the stall's inner border */\n.stall-awning{background-repeat:round no-repeat}\n.stall-awning::after{background-repeat:round no-repeat}\n.stall-marquee{margin:0 -20px}\n.stall-track{padding-left:20px}\n.stall-shelf{margin-left:-20px;margin-right:-20px}\n"
site_css += '\n/* Floating pill navbar (tools/navbar.py): status pill, centre nav pill, email pill */\n.sitenav{position:sticky;top:0;z-index:30;padding:14px 20px 0;background:transparent;pointer-events:none}\n.sitenav{margin-bottom:-70px}\n#top .hero-grid{padding-top:118px!important}\n.sitenav-row{max-width:1200px;margin:0 auto;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:16px}\n.nav-pill{pointer-events:auto;display:inline-flex;align-items:center;gap:8px;background:var(--surface-raised);color:var(--ink);\n  box-shadow:0 -3px 0 0 var(--wood-dark),0 3px 0 0 var(--wood-dark),-3px 0 0 0 var(--wood-dark),3px 0 0 0 var(--wood-dark),5px 6px 0 0 var(--pixel-shadow),inset 0 -3px 0 0 var(--surface-sunken)}\n.nav-status{justify-self:start;padding:7px 14px 8px 12px;font-size:14px;line-height:18px;font-weight:700}\n.nav-dot{width:10px;height:10px;background:#4fbf6a;box-shadow:0 0 0 2px #2f7d3a;animation:navblink 2.4s steps(1) infinite}\n@keyframes navblink{50%{background:#9ee6a9}}\n.sitenav .topnav{justify-self:center;gap:4px!important;padding:5px 5px 6px;white-space:nowrap;font-family:var(--font-pixel);font-size:20px!important;line-height:20px;letter-spacing:.04em;text-transform:uppercase}\n.nav-logo{display:flex;align-items:center;gap:8px;margin-right:6px;text-decoration:none;color:var(--ink)}\n.nav-logo-ic{display:grid;place-items:center;width:40px;height:40px;background:var(--wood-dark);box-shadow:inset 0 -3px 0 #3a1f17,inset 0 2px 0 #8a4a2a}\n.nav-logo-ic img{width:32px;height:24px;image-rendering:pixelated}\n.nav-name{display:none;font-family:var(--font-display);font-size:20px;font-weight:700;text-transform:none;letter-spacing:0}\n.sitenav .topnav .navlinks{display:block;padding:10px 10px!important;text-decoration:none;color:var(--ink)}\n.sitenav .topnav .navlinks:hover{color:var(--accent-text)}\n.sitenav .navlinks[aria-current="page"]{color:var(--accent-text);text-decoration:underline;text-underline-offset:5px;text-decoration-thickness:3px}\n.nav-cta{display:inline-flex;align-items:center;min-height:40px;margin-left:6px;padding:0 16px;background:var(--wood-dark);color:#fdf1d3;text-decoration:none;\n  box-shadow:inset 0 -3px 0 #3a1f17,inset 0 2px 0 #8a4a2a;transition:transform .1s steps(2)}\n.nav-cta:hover{background:var(--wood);color:#fff}\n.nav-cta:active{transform:translateY(2px)}\n.nav-email{justify-self:end;border:0;padding:7px 14px 8px 12px;font:700 14px/18px var(--font-body);cursor:pointer}\n.nav-email svg{width:14px;height:14px;fill:var(--wood-dark);shape-rendering:crispEdges}\n.nav-email:hover .nav-email-t{color:var(--accent-text)}\n.nav-email.copied .nav-email-t{color:#2f7d3a}\n.nav-pill:focus-visible,.nav-cta:focus-visible,.nav-logo:focus-visible,.sitenav .navlinks:focus-visible{outline:3px solid var(--focus);outline-offset:3px}\n/* the old header\'s burger + panel, restyled for the pill */\n.sitenav .navburger{margin-left:6px}\n.sitenav .navpanel{pointer-events:auto;position:static;max-width:420px;margin:12px auto 0;padding:6px 18px 12px;border:0;background:var(--surface-raised);\n  box-shadow:0 -3px 0 0 var(--wood-dark),0 3px 0 0 var(--wood-dark),-3px 0 0 0 var(--wood-dark),3px 0 0 0 var(--wood-dark),5px 6px 0 0 var(--pixel-shadow)}\n@media (max-width:1100px){.nav-status,.nav-email{display:none}.sitenav-row{grid-template-columns:1fr}}\n@media (max-width:760px){\n  .sitenav{padding:10px 12px 0}\n  .sitenav{margin-bottom:-64px}\n  #top .hero-grid{padding-top:96px!important}\n  .sitenav .topnav{width:100%;justify-content:flex-start}\n  .nav-name{display:block}\n  .sitenav .topnav .nav-cta{margin-left:auto}\n  .sitenav .topnav .navlinks{display:none!important}\n  .sitenav .navpanel .navlinks{display:block!important}\n}\n.sitenav .navpanel .navlinks{color:var(--ink);text-decoration:none}\n.sitenav .navpanel .navlinks[aria-current="page"]{color:var(--accent-text);text-decoration:underline}\n@media (prefers-reduced-motion:reduce){.nav-dot{animation:none}}\n'
site_css += '\n/* Only the centre nav pill follows the scroll; the status and email pills stay at the top */\n.sitenav{position:relative}\n.sitenav .topnav{position:fixed;z-index:31;top:14px;left:50%;transform:translateX(-50%)}\n.sitenav .navpanel{position:fixed;z-index:31;top:84px;left:12px;right:12px}\n.sitenav .nav-email{grid-column:3}\n@media (max-width:760px){.sitenav .topnav{top:10px;left:12px;right:12px;width:auto;transform:none;justify-self:stretch}.sitenav .navpanel{top:74px}}\n'
site_css += '/* Side pills: vertically centred on the centre nav pill */\n.sitenav-row{min-height:51px}\n'
site_css += "\n/* Selected work, image-first (ref: amylalai.com): a large cover per project with one caption line (title left, tags right) */\n#work > div:has(> .workcard){display:flex!important;flex-direction:column;gap:56px!important}\n#work .workcard{margin:0;padding:0;background:none!important;border:0!important;box-shadow:none!important}\n#work .workcard > .cardlink{display:flex!important;flex-direction:column;gap:14px}\n#work .workcard > .cardlink > div:first-child{margin:0!important;min-height:0!important;aspect-ratio:2/1;border-radius:12px;box-shadow:0 0 0 3px var(--wood-dark),6px 6px 0 3px var(--pixel-shadow)!important;transition:transform .2s steps(3)}\n#work .workcard:not(.wc-soon):hover > .cardlink > div:first-child{transform:translate(-2px,-3px)}\n#work .workcard > .cardlink > div:last-child{display:grid!important;grid-template-columns:1fr auto;align-items:baseline;gap:4px 24px!important;padding:0 2px!important;justify-content:initial!important}\n#work .workcard h3{grid-column:1;font-size:22px!important;line-height:30px!important}\n#work .workcard > .cardlink > div:last-child > p:first-of-type{grid-column:1;grid-row:2;font-size:15px!important}\n#work .workcard > .cardlink > div:last-child > p:nth-of-type(2){display:none}\n#work .workcard > .cardlink > div:last-child > div:has(.pp-sticker){grid-column:2;grid-row:1;display:block!important;text-align:right}\n#work .workcard > .cardlink > div:last-child > div:last-child:has(.readcs){display:none!important}\n#work .wc-soon > .cardlink > div:last-child > div:last-child:has(.readcs){display:flex!important;grid-column:2;grid-row:2;justify-content:flex-end;margin:0!important;padding:0!important}\n#work .wc-soon .readcs.soon{font-size:15px}\n/* covers: let the art breathe at the larger size */\n#work .wc-lc-laptop{width:58%}\n#work .yt-laptop{width:46%}\n#work .yt-cookie{width:min(64%,600px)!important}\n@media (max-width:760px){\n  #work > div:has(> .workcard){gap:40px!important}\n  #work .workcard > .cardlink > div:first-child{aspect-ratio:4/3}\n  #work .workcard > .cardlink > div:last-child{grid-template-columns:1fr}\n  #work .workcard > .cardlink > div:last-child > div:has(.pp-sticker),#work .wc-soon > .cardlink > div:last-child > div:last-child:has(.readcs){grid-column:1;grid-row:auto;justify-content:flex-start}\n  #work .wc-lc-laptop{width:76%}#work .yt-laptop{width:62%}#work .yt-cookie{width:min(86%,420px)!important}\n  #work .workcard > .cardlink > div:last-child > div:has(.pp-sticker){text-align:left}\n}\n\n/* Covers show Lyanna's actual screens, slowly scrolling (paused on hover so it can be read) */\n.wc-wins{position:absolute;inset:9% 7% -4%;display:grid;grid-template-columns:1fr 1fr;gap:5%;z-index:1}\n.wc-win{display:flex;flex-direction:column;overflow:hidden;border-radius:10px 10px 0 0;background:#fff;box-shadow:0 0 0 3px #2b1f17,0 20px 36px rgba(20,30,50,.4)}\n.wc-win.fs{margin-top:9%}\n.wc-win-bar{display:flex;align-items:center;gap:5px;padding:7px 10px;background:#fdf1d3;box-shadow:inset 0 -2px 0 #2b1f17}\n.wc-win-bar i{width:7px;height:7px;background:var(--wood-light)}\n.wc-win-bar b{margin-left:6px;font-family:var(--font-pixel);font-size:15px;line-height:15px;font-weight:400;letter-spacing:.05em;text-transform:uppercase;color:var(--ink)}\n.wc-win-scr{position:relative;flex:1;overflow:hidden}\n.wc-win-scr img,.wc-lc-lid img.wc-lc-scroll{display:block;width:100%;height:100%;object-fit:cover;object-position:50% 0;animation:wcScroll var(--d,38s) ease-in-out infinite alternate}\n.wc-win.fs img{--d:30s;animation-delay:-6s}\n.wc-lc-lid img.wc-lc-scroll{--d:18s}\n@keyframes wcScroll{0%,6%{object-position:50% 0}94%,100%{object-position:50% 100%}}\n.workcard:hover .wc-win-scr img,.workcard:hover .wc-lc-scroll{animation-play-state:paused}\n@media (prefers-reduced-motion:reduce){.wc-win-scr img,.wc-lc-scroll{animation:none}}\n@media (max-width:760px){.wc-wins{inset:8% 5% -4%}.wc-win-bar b{font-size:12px}}\n/* tags back to colour blocks */\n#work .workcard > .cardlink > div:last-child > div:has(.pp-sticker){display:flex!important;flex-wrap:wrap;justify-content:flex-end;gap:8px!important;text-align:initial}\n@media (max-width:760px){#work .workcard > .cardlink > div:last-child > div:has(.pp-sticker){justify-content:flex-start}}\n"
site_css += '\n/* Cute single nav pill (ref: jessicahsu.design): pixel icon + label per link, a soft highlight that slides to the hovered link */\n.sitenav{display:flex;justify-content:center;padding:14px 16px 0}\n.sitenav .topnav{position:fixed;top:14px;left:50%;transform:translateX(-50%);z-index:31;display:flex!important;align-items:center;gap:2px!important;padding:5px!important;\n  background:#fdf1d3f2;border-radius:999px;box-shadow:0 0 0 3px var(--wood-dark),0 5px 0 0 var(--pixel-shadow),inset 0 -3px 0 var(--surface-sunken);\n  font-family:var(--font-pixel);font-size:19px!important;line-height:19px;letter-spacing:.04em;text-transform:uppercase;white-space:nowrap}\n.sitenav .topnav .navlinks{position:relative;z-index:1;display:flex!important;align-items:center;gap:7px;padding:9px 14px 8px!important;border-radius:999px;color:var(--ink-muted);text-decoration:none!important}\n.sitenav .topnav .navlinks svg{width:16px;height:16px;fill:currentColor;shape-rendering:crispEdges;flex:none}\n.sitenav .topnav .navlinks:hover,.sitenav .topnav .navlinks:focus-visible{color:var(--ink)}\n.sitenav .topnav .navlinks[aria-current="page"]{color:var(--ink);background:var(--gold);box-shadow:0 0 0 2px var(--wood-dark)}\n.sitenav .topnav .navlinks:hover svg{animation:navIconHop .35s steps(3)}\n@keyframes navIconHop{50%{transform:translateY(-3px)}}\n.sitenav .nav-hl{position:absolute;z-index:0;top:5px;bottom:5px;left:0;width:0;border-radius:999px;background:var(--surface-sunken);opacity:0;transition:left .28s cubic-bezier(.22,1,.36,1),width .28s cubic-bezier(.22,1,.36,1),opacity .16s}\n.sitenav .topnav.has-hl .nav-hl{opacity:1}\n.sitenav .navburger,.sitenav .navpanel,.nav-status,.nav-email{display:none!important}\n@media (max-width:760px){\n  .sitenav .topnav{top:10px;font-size:16px!important;line-height:16px}\n  .sitenav .topnav .navlinks{gap:5px;padding:8px 9px 7px!important}\n  .sitenav .topnav .navlinks svg{width:13px;height:13px}\n}\n@media (max-width:420px){.sitenav .topnav .navlinks span{display:none}.sitenav .topnav .navlinks[aria-current="page"] span{display:inline}.sitenav .topnav .navlinks{padding:9px 11px!important}}\n@media (prefers-reduced-motion:reduce){.sitenav .nav-hl{transition:none}.sitenav .topnav .navlinks:hover svg{animation:none}}\n.sitenav{height:70px;box-sizing:border-box;margin-bottom:-70px!important}\n@media (max-width:760px){.sitenav{height:64px;margin-bottom:-64px!important}}\n'
site_css += '\n/* Nav pill v2: round, cute icons, and a gold block that glides to the clicked link (and across pages) */\n.sitenav .topnav .navlinks svg{width:18px;height:18px;fill:#fdf1d3;stroke:currentColor;stroke-width:2.1;stroke-linecap:round;stroke-linejoin:round;shape-rendering:auto;overflow:visible}\n.sitenav .topnav .navlinks svg .k{fill:currentColor;stroke:none}\n.sitenav .topnav .navlinks svg .s{fill:none}\n.sitenav .topnav .navlinks[aria-current="page"]{background:none!important;box-shadow:none!important}\n.sitenav .topnav .navlinks[aria-current="page"] svg{fill:#fff6d8}\n.sitenav .nav-cur{position:absolute;z-index:0;top:5px;bottom:5px;left:0;width:0;border-radius:999px;background:var(--gold);box-shadow:0 0 0 2px var(--wood-dark),inset 0 -3px 0 #d79a3e;view-transition-name:nav-cur;\n  transition:left .42s cubic-bezier(.34,1.45,.5,1),width .42s cubic-bezier(.34,1.45,.5,1)}\n.sitenav .nav-cur.no-anim{transition:none}\n.sitenav .topnav:not(.has-cur) .nav-cur{opacity:0}\n.sitenav .topnav .navlinks:hover svg{animation:navIconBop .4s cubic-bezier(.3,1.6,.5,1)}\n@keyframes navIconBop{40%{transform:translateY(-3px) rotate(-8deg) scale(1.12)}}\n@view-transition{navigation:auto}\n::view-transition-group(nav-cur){animation-duration:.42s;animation-timing-function:cubic-bezier(.34,1.3,.5,1)}\n@media (max-width:760px){.sitenav .topnav .navlinks svg{width:16px;height:16px}}\n@media (prefers-reduced-motion:reduce){.sitenav .nav-cur{transition:none}.sitenav .topnav .navlinks:hover svg{animation:none}@view-transition{navigation:none}}\n'
site_css += '\n/* Nav icons: a gentle tilt that holds while hovered, then eases back */\n.sitenav .topnav .navlinks svg{transition:transform .25s cubic-bezier(.3,1.4,.5,1)}\n.sitenav .topnav .navlinks:hover svg,.sitenav .topnav .navlinks:focus-visible svg{animation:none!important;transform:rotate(-12deg)}\n@media (prefers-reduced-motion:reduce){.sitenav .topnav .navlinks svg{transition:none}}\n'
site_css += '\n/* Work captions (ref: billguo.me): an outcome-led title, then one short result line */\n#work .workcard > .cardlink > div:last-child > p:nth-of-type(2){display:block!important;grid-column:1;grid-row:3;margin:2px 0 0!important;font-size:16px!important;line-height:24px!important;color:var(--ink)!important;font-weight:600}\n\n/* The pixel display font draws "fi" as a broken ligature ("find" reads "And"), so ligatures are off site-wide */\n*{font-variant-ligatures:no-common-ligatures;font-feature-settings:"liga" 0}\n'
site_css += '\n/* Work captions: title only (plus tags) */\n#work .workcard > .cardlink > div:last-child > p:nth-of-type(n){display:none!important}\n#work .workcard h3{align-self:center}\n'
site_css += '#work .workcard > .cardlink > div:last-child > p:first-of-type{display:block!important;grid-column:1;grid-row:2}\n'
open(os.path.join(OUT, 'css', 'site.css'), 'w').write(site_css)
import navbar; navbar.run()  # floating pill navbar on every page
open(os.path.join(OUT, 'css', 'case-study.css'), 'w').write(
    '/* Extra rules for the case-study pages (annotations, before/after, table of contents). */\n'
    + css_assets('\n'.join(l for l in extra if l.strip()), '../') + '\n')

# ---------------------------------------------------------------- pages
FONT_LINK = re.search(r'<link rel="preconnect".*?>\s*<link[^>]*fonts\.googleapis[^>]*>', raw).group(0)
SCRIPTS = {'Main': ['home.js'], 'About': ['about.js'], 'Garden': ['garden.js'],
           'CaseStudy-Linguistics': ['case-study.js'], 'CaseStudy-Include': ['case-study.js']}
DESC = 'Lyanna Nguyen — Product Designer & UX Researcher. Cognitive Science @ UC Davis.'

for name, P in PAGES.items():
    cfg = CONFIG[name]
    tpl = P['tpl']
    if name == 'Main':
        for _a, _b in [('animation-delay: 1.85s;', 'animation-delay: 1.8s;'), ('animation-delay: 2s;', 'animation-delay: 1.94s;'),
                       ('animation-delay: 2.15s;', 'animation-delay: 2.09s;'), ('animation-delay: 2.3s;', 'animation-delay: 2.24s;')]:
            assert tpl.count(_a) == 1, _a
            tpl = tpl.replace(_a, _b)
        tpl = workcards.apply(tpl)
        # The scroll-following tour guide is permanently switched off (showComp is always false).
        tpl, n = re.subn(r'  <!-- TOUR GUIDE -->.*?(?=  <!-- NAV -->)', '', tpl, flags=re.S)
        assert n == 1 and 'showComp' not in tpl
    # Plain labels on external and download links (no trailing arrows)
    for _a in ('LinkedIn ↗<', 'Resume ↗<', 'Resume ↓<'):
        assert _a in tpl, (name, _a)
        tpl = tpl.replace(_a, _a.replace(' ↗', '').replace(' ↓', ''))
    # Extract the embedded interactive prototype into its own page.
    def proto(mm):
        doc = html.unescape(mm.group(1))
        doc = DATA_RE.sub(lambda d: '../' + save(d.group(1), d.group(2)), doc)
        os.makedirs(os.path.join(OUT, 'prototypes'), exist_ok=True)
        open(os.path.join(OUT, 'prototypes', 'linguistics-club.html'), 'w').write(doc)
        return 'src="prototypes/linguistics-club.html"'
    tpl = re.sub(r'srcdoc="([^"]*)"', proto, tpl)
    # Hooks for the page scripts.
    tpl = tpl.replace('{{typed}}<span class="cur" aria-hidden="true" style="color: var(--wood);">▌</span>',
                      '<span class="dlg-ghost" aria-hidden="true"></span><span class="dlg-shown"><span class="dlg-typed"></span>'
                      '<span class="cur" aria-hidden="true" style="color: var(--wood);">▌</span></span>')
    tpl = tpl.replace('<span aria-hidden="true" style="position: absolute; left: 0; top: {{markTop}};',
                      '<span class="toc-mark" aria-hidden="true" style="position: absolute; left: 0; top: {{markTop}};')
    tpl = convert_scif(tpl, cfg['shows'])
    tpl = fill(tpl, cfg['values'], cfg['actions'])
    tpl = resolve_blobs(tpl)
    tpl = DATA_RE.sub(lambda d: save(d.group(1), d.group(2)), tpl)
    tpl = fix_links(tpl)
    # Song embeds load only when opened, so a hidden player never streams in the background.
    tpl = re.sub(r'(<iframe [^>]*?)\ssrc="(https://open\.spotify\.com[^"]*)"', r'\1 data-src="\2"', tpl)
    tpl = clean(tpl)
    # Content corrections made after the export.
    for old, new in CONTENT_FIXES.get(name, []):
        assert old in tpl, (name, old)
        tpl = tpl.replace(old, new)
    if name == 'Main':
        # No resume section: the resume lives in the PDF (nav Resume button) and the night-time
        # footer is the contact section, so Contact links and the dialogue point there instead.
        tpl, n = re.subn(r'\n  <div style="max-width: 1080px; margin: 0 auto; padding: 0 20px;">\n    <!-- STOP 3: THE MAILBOX -->.*?</section>\n  </div>\n', '\n', tpl, flags=re.S)
        assert n == 1
        tpl = tpl.replace('<footer style="', '<footer id="contact" style="scroll-margin-top: 68px; ', 1)
        tpl = tpl.replace('href="#resume"', 'href="#contact"')
        tpl = tpl.replace('<a data-show="dialog-choices" hidden href="#contact" class="pp-btn secondary" data-action="close-dialog">Just the resume</a>',
                          '<a data-show="dialog-choices" hidden href="assets/files/Lyanna_Nguyen_Resume.pdf" target="_blank" rel="noopener" class="pp-btn secondary" data-action="close-dialog">Just the resume</a>')
        assert '#resume' not in tpl and 'Lyanna_Nguyen_Resume.pdf" target="_blank" rel="noopener" class="pp-btn secondary"' in tpl
    # No contact section any more: drop the Contact links, and Resume becomes a plain nav link
    tpl, n = re.subn(r'\n[ ]*<a href="[^"]*#contact"[^>]*>Contact</a>', '', tpl)
    assert n == 2, (name, n)
    tpl, n = re.subn(r'class="pp-btn navres" style="[^"]*"', 'class="navlinks" style="padding: 8px 10px; text-decoration: none; color: var(--ink);"', tpl)
    assert n == 1, (name, n)
    css = ['css/pixel-pals.css', 'css/site.css'] + (['css/case-study.css'] if name.startswith('CaseStudy') else [])
    title = P['title']
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{html.escape(DESC)}">
<link rel="icon" href="{blob_path['3d04620ca257bc0131b8bef0887d78cb'] if '3d04620ca257bc0131b8bef0887d78cb' in blob_path else ''}">
{FONT_LINK}
''' + ''.join(f'<link rel="stylesheet" href="{c}">\n' for c in css) + f'''</head>
<body>
{tpl}
<script src="js/site.js"></script>
''' + ''.join(f'<script src="js/{s}"></script>\n' for s in SCRIPTS[name]) + '''</body>
</html>
'''
    assert '{{' not in doc and '/_blob/' not in doc and 'sc-if' not in doc and ';base64,' not in doc, name
    if FILES[name] in HAND_BUILT and os.path.exists(os.path.join(OUT, FILES[name])):
        print('kept hand-built', FILES[name]); continue
    open(os.path.join(OUT, FILES[name]), 'w').write(doc)

# Drop assets no page references (e.g. sprites only used by the disabled tour guide).
texts = ''
for root, _, files in os.walk(OUT):
    for f in files:
        if f.endswith(('.html', '.css')):
            texts += open(os.path.join(root, f)).read()
for h, rel in list(assets.items()):
    if os.path.basename(rel) not in texts:
        os.remove(os.path.join(OUT, rel)); print('unused', rel); del assets[h]
print('assets', len(assets))
