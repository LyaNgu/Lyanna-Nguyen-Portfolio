"""Convert the single-file design export into this static multi-page site.

Usage: python3 tools/convert_export.py path/to/Lyanna_Nguyen_Portfolio_Final.html .

Regenerates the HTML pages, css/ and assets/. The scripts in js/ are hand-written and
are not touched, so keep the data-show / data-action hooks below in sync with them.
"""
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
    # Quiet lawn tile for the garden (tools/pixel/backdrop.py)
    'Garden': [('background-image: radial-gradient(circle at 3px 3px, #5aa83a 2.5px, transparent 3px), radial-gradient(circle at 21px 17px, #95d46a 2px, transparent 2.5px); background-size: 38px 30px;',
                'background-image: url(assets/images/bg-lawn.svg); background-size: 512px 384px; image-rendering: pixelated;')],
    'Main': [('>Triceratops Website · Jun 2026 – Present<', '>Triceratops Website · Jun – Oct 2026<'),
             # Keep the Works card in step with the hand-built case study hero
             ('>Streamlining onboarding to help new members get involved from day one<', '>Streamlining onboarding for new members<'),
             ('>I designed and built a Getting Started page that turns a crowded Discord into a clear first step for new members.<', '>Designing for interested students, 60% of whom said unclear rules kept them from joining.<'),
             # 8-bit backdrop (mountains, hills, tree line, grass tufts) drawn by tools/pixel/backdrop.py
             ('    <div aria-hidden="true" style="position: absolute; left: -10%; right: 30%; bottom: 80px; height: 170px; background: #9fd28a; border-radius: 50% 50% 0 0 / 100% 100% 0 0; box-shadow: inset 0 4px 0 #b8e0a0;"></div>\n    <div aria-hidden="true" style="position: absolute; left: 35%; right: -15%; bottom: 80px; height: 130px; background: #8cc97a; border-radius: 50% 50% 0 0 / 100% 100% 0 0; box-shadow: inset 0 4px 0 #a8d890;"></div>\n',
              '    <div aria-hidden="true" style="position: absolute; left: 0; right: 0; bottom: 120px; height: 144px; background: url(assets/images/bg-mountains.svg) 0 100% / 384px 144px repeat-x; image-rendering: pixelated;"></div>\n    <div aria-hidden="true" style="position: absolute; left: 0; right: 0; bottom: 96px; height: 104px; background: url(assets/images/bg-hills.svg) -60px 100% / 320px 104px repeat-x; image-rendering: pixelated;"></div>\n    <div aria-hidden="true" style="position: absolute; left: 0; right: 0; bottom: 96px; height: 136px; background: url(assets/images/bg-trees.svg) 50% 100% / 512px 136px repeat-x; image-rendering: pixelated;"></div>\n'),
             ('<div aria-hidden="true" style="position: absolute; left: 0; right: 0; bottom: 0; height: 96px; background: var(--grass); box-shadow: inset 0 4px 0 0 #2f7d3a;"></div>',
              '<div aria-hidden="true" style="position: absolute; left: 0; right: 0; bottom: 0; height: 96px; background: url(assets/images/bg-grass.svg) 0 0 / 256px 96px repeat-x, var(--grass); box-shadow: inset 0 4px 0 0 #2f7d3a; image-rendering: pixelated;"></div>')],
}

# Pages rebuilt by hand after the export; the converter never overwrites them.
HAND_BUILT = {'triceratops.html'}

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
# Opening plays in 1.5s: every loader timing scaled to 1.5/3.6 (js/home.js hides it at 1550ms)
LOADER_SPEED = [('3.6s steps(36)', '1.5s steps(18)'), ('ldrBar 3s steps(15)', 'ldrBar 1.25s steps(10)'),
                ('ldrFade 3.6s', 'ldrFade 1.5s'), ('ldrHole 3.6s', 'ldrHole 1.5s'), ('ldrDrop .45s steps(5) 2', 'ldrDrop .2s steps(4) 2')]
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
site_css += '\n/* Phone menu: hamburger button and dropdown panel (built by js/site.js) */\n.navburger{display:none}\n@media (max-width:760px){\n.navburger{display:inline-grid;align-content:center;gap:4px;width:44px;height:40px;margin-left:8px;padding:0 10px;border:0;border-radius:6px;background:var(--surface);box-shadow:inset 0 0 0 3px var(--wood-dark);cursor:pointer}\n.navburger span{display:block;height:3px;background:var(--wood-dark);transition:transform .2s ease,opacity .2s ease}\n.menu-open .navburger span:nth-child(1){transform:translateY(7px) rotate(45deg)}\n.menu-open .navburger span:nth-child(2){opacity:0}\n.menu-open .navburger span:nth-child(3){transform:translateY(-7px) rotate(-45deg)}\n.navburger:focus-visible{outline:3px solid var(--focus);outline-offset:2px}\n.navpanel{position:absolute;left:0;right:0;top:100%;display:flex;flex-direction:column;padding:6px 20px 14px;background:var(--surface-raised);border-bottom:4px solid var(--wood);box-shadow:0 3px 0 var(--wood-dark);font-family:var(--font-pixel);font-size:22px;letter-spacing:.04em;text-transform:uppercase}\n.navpanel[hidden]{display:none}\n.navpanel .navlinks{display:block!important;padding:12px 4px!important;border-bottom:2px dashed var(--surface-sunken)}\n.navpanel .navlinks:last-child{border-bottom:0}\n}\n@media (prefers-reduced-motion:reduce){.navburger span{transition:none}}\n'
open(os.path.join(OUT, 'css', 'site.css'), 'w').write(site_css)
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
        for _a, _b in [('animation-delay: 1.85s;', 'animation-delay: .77s;'), ('animation-delay: 2s;', 'animation-delay: .83s;'),
                       ('animation-delay: 2.15s;', 'animation-delay: .9s;'), ('animation-delay: 2.3s;', 'animation-delay: .96s;')]:
            assert tpl.count(_a) == 1, _a
            tpl = tpl.replace(_a, _b)
        # The scroll-following tour guide is permanently switched off (showComp is always false).
        tpl, n = re.subn(r'  <!-- TOUR GUIDE -->.*?(?=  <!-- NAV -->)', '', tpl, flags=re.S)
        assert n == 1 and 'showComp' not in tpl
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
