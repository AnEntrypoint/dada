#!/usr/bin/env python3
"""Measure the contrast a reader actually receives, from rendered pixels.

`measure.py --preset contrast` reads getComputedStyle and walks ancestors for a
background colour. That is the right check for text on a flat field, and it is
blind to everything else: text sitting on an image, on a bleed, on a gradient,
under a translucent overlay, or on anything composited. It happily reported
PASS for the hero's closing sentences while they sat on a near-black band of
the artwork.

This answers the same question from the other end: from the pixels. It reads
the ink from the CSS and the ground from a second render in which every glyph
is transparent, so the two things WCAG actually compares — the type colour and
the colour behind it — are each measured where they are unambiguous.

    python3 tools/pixcontrast.py --sel '.hero-bottom'
    python3 tools/pixcontrast.py --widths 1440,900,390           # whole page
    python3 tools/pixcontrast.py --all --widths 1440,650

Why two renders. Sampling one screenshot and splitting its pixels into "glyph"
and "field" by luminance cannot work for small type: at 12px a stem is one
pixel wide and subpixel-antialiased, so nearly every pixel of the letter is a
blend and almost none reaches the ink's own value. Any threshold then counts
most of the letter as background, and the background's worst percentile becomes
a half-covered stem — which is how this tool first reported 1.4:1 for words
that sit at 13:1. Making the type transparent removes the letter from the
second render entirely, so what is left in the rect is only the ground: its
typical value, and its worst — the darkest part of the artwork behind a veil,
say, which is the pixel the reader can lose the word on.

Occlusion is read by comparing the two crops: a rect whose pixels do not change
when the type is made transparent had no type painted in it at all.

Rect, type size and ink come from the live DOM (measure.py); pixels come from
screenshots of the same staged copy at the same iframe height, so every half
sees one layout.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

from PIL import Image
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEASURE = os.path.join(ROOT, 'tools', 'measure.py')

# Both halves must see one layout. measure.py sizes the iframe that holds the
# page, so an iframe shorter than the page gets its own scrollbar and the page
# renders 15px narrower than it does in a taller one — the rects then name
# pixels that are not there. One height for the rects and for both screenshots.
FOLD = 12000

# One sample per text run per line box, not per element. An element that holds
# a child in another colour — a <p> round a <code>, a button round its numeral
# — puts that child's ink inside the element's rect. Sizing the rect to the
# text run itself removes it, and gives every line its own measurement. SVG
# <text> is skipped: it is painted by fill, not by colour, so the CSS ink is
# not what lands.
RECTS = r"""
const sel=SELECTOR;
const scope = sel==='*' ? doc.body : doc.querySelector(sel);
if(!scope) return {w:W, err:'selector not found: '+sel};
const out=[], walk=doc.createTreeWalker(scope, NodeFilter.SHOW_TEXT);
let n;
while((n=walk.nextNode())){
  const t=n.textContent.replace(/\s+/g,' ').trim();
  if(!t) continue;
  const el=n.parentElement;
  if(!el||el.closest('svg')) continue;
  const cs=win.getComputedStyle(el);
  if(cs.visibility==='hidden'||cs.display==='none'||+cs.opacity===0) continue;
  if(/rgba\(.*,\s*0\)/.test(cs.color)) continue;
  const rg=doc.createRange(); rg.selectNodeContents(n);
  // A wrapped run ends in a sliver one space wide: it holds no glyph, so it
  // measures as "nothing painted". Merge the rects that share a line box.
  const byline=new Map();
  for(const r of rg.getClientRects()){
    if(r.width<4||r.height<4||r.bottom<0||r.top>4000) continue;
    const k=Math.round(r.top);
    const cur=byline.get(k);
    byline.set(k, cur ? {l:Math.min(cur.l,r.left),t:Math.min(cur.t,r.top),
                         r:Math.max(cur.r,r.right),b:Math.max(cur.b,r.bottom)} :
                        {l:r.left,t:r.top,r:r.right,b:r.bottom});
  }
  let lines=0;
  for(const r of byline.values()){
    if(lines>3) break;
    const er=el.getBoundingClientRect();
    out.push({txt:t.slice(0,26),x:r.l,y:r.t,r:r.r,b:r.b,
              ex:er.left,ey:er.top,er:er.right,eb:er.bottom,
              px:parseFloat(cs.fontSize)||0,fw:parseInt(cs.fontWeight)||400,
              col:cs.color,tag:el.tagName.toLowerCase()});
    lines++;
  }
}
return {w:W, blocks:out.slice(0,400)};
"""

# The same page with no type in it: what is left in a rect is the ground.
HIDE = r"""
const st=doc.createElement('style');
st.textContent='*{color:transparent!important;-webkit-text-fill-color:transparent!important}';
doc.head.appendChild(st);
return doc.querySelectorAll('*').length;
"""


def lin(c):
    c = np.asarray(c, dtype=float) / 255.0
    return np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lum(rgb):
    """WCAG relative luminance of an sRGB triple, from a CSS colour string."""
    m = re.findall(r'([\d.]+)', rgb or '')
    if len(m) < 3:
        return None
    c = [float(x) / 255.0 for x in m[:3]]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def L(a):
    a = np.asarray(a, dtype=float)
    return 0.2126 * lin(a[..., 0]) + 0.7152 * lin(a[..., 1]) + 0.0722 * lin(a[..., 2])


def ratio(x, y):
    return round((max(x, y) + 0.05) / (min(x, y) + 0.05), 2)


def rects_for(width, selector):
    code = RECTS.replace('SELECTOR', json.dumps(selector))
    p = subprocess.run([sys.executable, MEASURE, '--file', '/dev/stdin',
                        '--widths', str(width), '--fold', str(FOLD), '--raw'],
                       input=code, capture_output=True, text=True)
    m = re.search(r'\{[\s\S]*\}\s*$', p.stdout.strip())
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except ValueError:
        return None


def shoot(width, out, code=None):
    cmd = [sys.executable, MEASURE, '--widths', str(width), '--fold', str(FOLD), '--shot', out]
    if code:
        fd, path = tempfile.mkstemp(suffix='.js')
        os.write(fd, code.encode())
        os.close(fd)
        try:
            subprocess.run([sys.executable, MEASURE, '--file', path, '--widths', str(width),
                            '--fold', str(FOLD), '--shot', out], capture_output=True)
        finally:
            os.remove(path)
    else:
        subprocess.run(cmd, capture_output=True)
    return Image.open(out).convert('RGB') if os.path.exists(out) else None


def crop(img, b):
    # A text run's box is the font's, and it reaches about a pixel above and
    # below the element's own box — outside the padding its ground is painted
    # on. Cropping to the intersection keeps unveiled pixels out of the sample.
    x0, y0 = max(0, int(b['x']), int(b.get('ex', b['x']))), max(0, int(b['y']), int(b.get('ey', b['y'])))
    x1 = min(img.width, int(b['r']), int(b.get('er', b['r'])))
    y1 = min(img.height, int(b['b']), int(b.get('eb', b['b'])))
    if x1 - x0 < 2 or y1 - y0 < 2:
        return None
    return np.asarray(img.crop((x0, y0, x1, y1))).astype(np.int16)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--sel', default='*', help="scope: a selector, or '*' for the page")
    ap.add_argument('--all', action='store_true', help="alias for --sel '*'")
    ap.add_argument('--widths', default='1440,900,650,390,320')
    ap.add_argument('--min', type=float, default=0.0,
                    help='only report ratios at or below this (0 = report every text box)')
    ap.add_argument('--shot-dir', default='/tmp')
    a = ap.parse_args()
    sel = '*' if a.all else a.sel

    worst = []
    for w in [int(x) for x in a.widths.split(',') if x.strip()]:
        info = rects_for(w, sel)
        if not info or 'blocks' not in info:
            print('%d: %s' % (w, (info or {}).get('err', 'no result')))
            continue
        blocks = info['blocks']
        if not blocks:
            print('%d: no text boxes in %s' % (w, sel))
            continue
        bare = shoot(w, os.path.join(a.shot_dir, 'pix-bare-%d.png' % w), HIDE)
        inked = shoot(w, os.path.join(a.shot_dir, 'pix-inked-%d.png' % w))
        if bare is None or inked is None:
            print('%d: no render' % w)
            continue
        print('=== %d ===' % w)
        for b in blocks:
            ink = lum(b.get('col'))
            cb, ci = crop(bare, b), crop(inked, b)
            if ink is None or cb is None or ci is None or cb.size < 9:
                continue
            need = 3.0 if (b['px'] >= 24 or (b['fw'] >= 700 and b['px'] >= 18.66)) else 4.5
            # nothing was painted if making the type transparent changes no pixel
            h = min(cb.shape[0], ci.shape[0])
            wd = min(cb.shape[1], ci.shape[1])
            painted = int((np.abs(cb[:h, :wd] - ci[:h, :wd]).max(axis=2) > 8).sum())
            if painted < 6:
                worst.append((w, b['txt'], 0.0, 0.0))
                print('FLAT   %-9s %5.1fpx %4d px differ — no type painted, occluded?  %s'
                      % (b['tag'], b['px'], painted, b['txt'][:26]))
                continue
            field = L(cb).ravel()
            typical = float(np.median(field))
            # the ground pixel nearest the ink is the one that can lose the word
            bg = float(np.percentile(field, 5) if ink < typical else np.percentile(field, 95))
            r, typ = ratio(ink, bg), ratio(ink, typical)
            if a.min and r > a.min:
                continue
            ok = r >= need
            if not ok:
                worst.append((w, b['txt'], r, need))
            print('%-6s %-9s %5.1fpx need %-4s ratio %-6s (typ %-6s) ink %.3f bg %.3f  %s' % (
                ('FAIL' if not ok else 'ok'), b['tag'], b['px'], need, r, typ,
                ink, bg, b['txt'][:26]))
        for f in ('pix-bare-%d.png' % w, 'pix-inked-%d.png' % w):
            q = os.path.join(a.shot_dir, f)
            if os.path.exists(q):
                os.remove(q)
    if worst:
        print('\n%d problem%s:' % (len(worst), '' if len(worst) == 1 else 's'))
        for w, t, r, n in worst:
            print('  %d  %-28s %s' % (w, t[:28], ('not painted' if not n else '%.2f < %.1f' % (r, n))))
    return 1 if worst else 0


if __name__ == '__main__':
    sys.exit(main())
