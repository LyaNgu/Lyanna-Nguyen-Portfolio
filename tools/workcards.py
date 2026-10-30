"""Works cards on the home page: stickers pop on hover (Triceratops) and the Linguistics card becomes
the same hover collage as its case study banner. Used by tools/convert_export.py and run once on index.html."""
import re

STAR = '<svg viewBox="0 0 24 24"><path d="M12 0C13 8 16 11 24 12C16 13 13 16 12 24C11 16 8 13 0 12C8 11 11 8 12 0Z"/></svg>'
SPARKS = [(7, 16, 30, 0, 3.2), (12, 70, 20, 1.1, 2.8), (90, 20, 26, .6, 3.8), (93, 62, 18, 1.8, 3.0), (80, 82, 14, .3, 2.6)]
LC_CARD = ('<div class="wc-lc" style="position: relative; margin: 12px; min-height: 260px; border-radius: var(--radius-md); overflow: hidden; box-shadow: inset 0 0 0 2px #00000022;">\n'
    '            <div class="lc-sky" aria-hidden="true">'
    + ''.join(f'<span class="lc-spark" style="left:{x}%;top:{y}%;--s:{sz}px;--d:{d}s;--t:{t}s">{STAR}</span>' for x, y, sz, d, t in SPARKS)
    + '</div>\n'
    '            <div class="wc-lc-screen"><img src="assets/images/lc-final-search.webp" alt="The final Linguistics Club Undergraduate Programs page with program search and filters" loading="lazy"></div>\n'
    '            <figure class="lc-mini lc-detail" aria-hidden="true"><img src="assets/images/lc-final-save-visit.webp" alt="" loading="lazy"></figure>\n'
    '            <figure class="lc-mini lc-mail" aria-hidden="true"><img src="assets/images/lc-final-mailing-list.webp" alt="" loading="lazy"></figure>\n'
    '            <img class="lc-wug" aria-hidden="true" alt="" src="assets/images/wug.png" loading="lazy">\n'
    '          </div>')

CSS = '''
/* Works cards: the Triceratops stickers pop and the Linguistics collage tilts in on hover, matching each case study's banner */
.wc-sticker{transition:translate .35s cubic-bezier(.3,1.6,.5,1),scale .35s cubic-bezier(.3,1.6,.5,1),filter .35s ease}
.workcard:hover .wc-sticker{translate:0 -10px;scale:1.12;filter:drop-shadow(0 12px 12px rgba(30,40,60,.3))!important}
.wc-lc{background:linear-gradient(160deg,#f1eefe,#d4cff7 50%,#ab9fe8)}
.wc-lc .lc-sky{position:absolute;inset:0;pointer-events:none}
.wc-lc .lc-spark{position:absolute;width:var(--s);height:var(--s);margin:calc(var(--s) / -2) 0 0 calc(var(--s) / -2);animation:lcTwinkle var(--t) ease-in-out var(--d) infinite}
.wc-lc .lc-spark svg{display:block;width:100%;height:100%;fill:#fff;filter:drop-shadow(0 0 6px #fff) drop-shadow(0 0 2px #8f84e0)}
@keyframes lcTwinkle{0%,100%{transform:scale(.55) rotate(0);opacity:.35}50%{transform:scale(1) rotate(45deg);opacity:1}}
.wc-lc-screen{position:absolute;z-index:1;left:12%;right:12%;top:11%;bottom:-6%;border-radius:12px 12px 0 0;overflow:hidden;background:#fff;box-shadow:0 0 0 3px #2b1f17,0 20px 36px rgba(40,30,110,.4)}
.wc-lc-screen img{display:block;width:100%;height:100%;object-fit:cover;object-position:left top}
.wc-lc .lc-mini,.wc-lc .lc-wug{position:absolute;transition:transform .55s cubic-bezier(.2,.9,.25,1.15),opacity .35s ease}
.wc-lc .lc-mini{z-index:3;margin:0;border-radius:8px;overflow:hidden;background:#fff;box-shadow:0 0 0 2px #fff,0 12px 24px rgba(70,50,150,.3);opacity:0}
.wc-lc .lc-mini img{display:block;width:100%;height:auto}
.wc-lc .lc-detail{left:3%;bottom:8%;width:34%;transform:translate(-70%,25%) rotate(-14deg)}
.wc-lc .lc-mail{right:3%;top:6%;width:24%;transform:translate(70%,-20%) rotate(14deg)}
.wc-lc .lc-wug{z-index:4;right:2%;bottom:0;width:24%;height:auto;transform:translateY(105%)}
.workcard:hover .wc-lc .lc-mini{opacity:1}
.workcard:hover .wc-lc .lc-detail{transform:rotate(-4deg)}
.workcard:hover .wc-lc .lc-mail{transform:rotate(4deg);transition-delay:.08s}
.workcard:hover .wc-lc .lc-wug{transform:none;transition-delay:.15s}
@media (prefers-reduced-motion:reduce){.wc-sticker,.wc-lc .lc-mini,.wc-lc .lc-wug{transition:opacity .2s}.wc-lc .lc-spark{animation:none}}
'''

def apply(tpl):
    tpl, n = re.subn(r'<img aria-hidden="true" alt="" src="assets/images/sticker-triceratops-', '<img class="wc-sticker" aria-hidden="true" alt="" src="assets/images/sticker-triceratops-', tpl)
    assert n == 4, n
    start = tpl.index('<div style="position: relative; margin: 12px; min-height: 260px; border-radius: var(--radius-md); background: radial-gradient(circle at 50% 48%')
    end = tpl.index('<div style="padding: 24px 28px 28px;', start)
    end = tpl.rindex('          </div>\n', start, end)
    tpl = tpl[:start] + LC_CARD + '\n' + tpl[end + len('          </div>\n'):]
    return tpl
