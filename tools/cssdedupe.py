"""Safely remove redundant CSS from the generated site.css.

Only top-level (outside @media etc.) style rules are touched:
  * an earlier rule identical to a later one is dropped;
  * a declaration is dropped from an earlier rule when a later rule with the
    exact same selector redeclares that property with equal or higher
    importance (so the cascade result is unchanged).
At-rules (@media, @keyframes, @font-face, ...) are kept as they are.
Usage: python3 tools/cssdedupe.py css/site.css
"""
import re
import sys


def chunks(css):
    """Split into top-level chunks: ('rule', selector, body) / ('raw', text)."""
    out, i, n = [], 0, len(css)
    while i < n:
        if css.startswith('/*', i):
            j = css.find('*/', i) + 2
            out.append(('raw', css[i:j])); i = j; continue
        if css[i].isspace():
            j = i
            while j < n and css[j].isspace():
                j += 1
            out.append(('raw', css[i:j])); i = j; continue
        j = css.find('{', i)
        if j < 0:
            out.append(('raw', css[i:])); break
        head = css[i:j]
        depth, k = 0, j
        while k < n:
            if css[k] == '{':
                depth += 1
            elif css[k] == '}':
                depth -= 1
                if depth == 0:
                    break
            elif css.startswith('/*', k):
                k = css.find('*/', k) + 1
            k += 1
        body = css[j + 1:k]
        if head.strip().startswith('@'):
            out.append(('raw', css[i:k + 1]))
        else:
            out.append(('rule', head.strip(), body))
        i = k + 1
    return out


def decls(body):
    parts, cur, depth = [], '', 0
    for ch in body:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ';' and depth == 0:
            parts.append(cur); cur = ''
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    res = []
    for p in parts:
        if ':' not in p:
            continue
        prop, val = p.split(':', 1)
        prop = prop.strip().lower()
        imp = '!important' in val.replace(' ', '')
        res.append((prop, p.strip(), imp))
    return res


def dedupe(css):
    cs = chunks(css)
    rules = [(idx, c) for idx, c in enumerate(cs) if c[0] == 'rule']
    later = {}   # selector -> {prop: important?} for rules after the current one
    keep = {}
    seen_exact = set()
    for idx, (_, sel, body) in reversed(rules):
        key = (sel, body.strip())
        if key in seen_exact:
            keep[idx] = None; continue
        seen_exact.add(key)
        ds = decls(body)
        lat = later.setdefault(sel, {})
        kept = []
        for prop, text, imp in ds:
            if prop.startswith('--'):
                kept.append(text); continue
            if prop in lat and (lat[prop] or not imp):
                continue
            kept.append(text)
        for prop, text, imp in ds:
            lat[prop] = lat.get(prop, False) or imp
        keep[idx] = kept
    out = []
    for idx, c in enumerate(cs):
        if c[0] == 'raw':
            out.append(c[1]); continue
        k = keep.get(idx)
        if not k:
            continue
        out.append(c[1] + '{' + ';'.join(k) + '}')
    text = ''.join(out)
    return re.sub(r'\n{3,}', '\n\n', text)


if __name__ == '__main__':
    path = sys.argv[1]
    src = open(path, encoding='utf-8').read()
    new = dedupe(src)
    open(path, 'w', encoding='utf-8').write(new)
    print(f'{path}: {len(src)} -> {len(new)} bytes')
