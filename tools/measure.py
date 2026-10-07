#!/usr/bin/env python3
"""Measure the DADA web page in headless Chromium without touching web/.

Every round of this project needs the same thing: render the page at several
widths, run a snippet against the live DOM, read a number. Doing it by hand
costs a hand-encoded query string, a manual `?v=` cache bust, and scraping a
<pre> out of a --dump-dom dump. This does all three, on a *copy* of the page
in a temp dir, so the published files are never edited to take a measurement.

    python3 tools/measure.py --preset overflow
    python3 tools/measure.py --preset all --widths 1440,900,390
    python3 tools/measure.py --file /tmp/check.js --widths 1440,390
    python3 tools/measure.py --expr 'return doc.title'
    python3 tools/measure.py --shot /tmp/fold.png --widths 1440 --fold 900
    python3 tools/measure.py --shot /tmp/no-h1.png --widths 1440 --fold 900 \
            --expr 'doc.querySelector(".hero h1").style.visibility="hidden"'

The snippet runs with (doc, win, W, H) in scope. Return anything
JSON-serialisable, or a string for raw output.
"""

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, 'web')
CHROME = '/usr/bin/chromium'

PROBE = """<!doctype html><meta charset="utf-8"><style>html,body{margin:0}iframe{border:0}</style>
<iframe id="f" src=""></iframe>
<pre id="out">pending</pre>
<script>
const q=new URLSearchParams(location.search);
const W=+q.get('w')||1440,H=+q.get('h')||3000;
const src=q.get('src')||'';
const f=document.getElementById('f');f.src=src;
f.style.width=W+'px';f.style.height=H+'px';
const code=decodeURIComponent(q.get('js')||'return 1;');
function run(){
 try{
  const win=f.contentWindow,doc=f.contentDocument;
  if(!doc||!doc.documentElement){throw new Error('iframe document not reachable');}
  const v=new Function('doc','win','W','H',code)(doc,win,W,H);
  document.getElementById('out').textContent=(typeof v==='string'?v:JSON.stringify(v,null,1));
 }catch(e){document.getElementById('out').textContent='ERR '+e.message}
}
f.addEventListener('load',()=>{setTimeout(run,+q.get('d')||2500)});
</script>
"""

# --------------------------------------------------------------------------
# Presets: the checks this project re-runs every round. Each is a snippet
# returning a compact object, so a whole battery is one browser launch per
# width instead of one launch per question.
# --------------------------------------------------------------------------

P_OVERFLOW = r"""
const de=doc.documentElement;
const over=[...doc.querySelectorAll('*')].filter(el=>{
  const r=el.getBoundingClientRect();
  return r.width>0 && (r.right>W+1||r.left<-1);
}).slice(0,6).map(el=>el.tagName.toLowerCase()+(el.className&&typeof el.className==='string'?'.'+el.className.split(/\s+/)[0]:'')+'@'+Math.round(el.getBoundingClientRect().right));
return {w:W, scroll:de.scrollWidth, client:de.clientWidth, ovf:de.scrollWidth-de.clientWidth, past:over};
"""

P_TARGETS = r"""
function box(el){const r=el.getBoundingClientRect();return {w:Math.round(r.width),h:Math.round(r.height)};}
const sel='a,button,summary,input,select,textarea,[tabindex]:not([tabindex="-1"])';
const bad=[...doc.querySelectorAll(sel)].map(el=>{
  const b=box(el);
  const inline = el.tagName==='A' && el.parentElement && el.parentElement.tagName!=='NAV'
                 && el.parentElement.textContent.trim().length>el.textContent.trim().length+8;
  return {el:el.tagName.toLowerCase()+(el.className&&typeof el.className==='string'?'.'+el.className.split(/\s+/)[0]:''),
          w:b.w,h:b.h,fs:parseFloat(getComputedStyle(el).fontSize)||0,inline:!!inline,
          txt:(el.textContent||'').trim().slice(0,28)};
}).filter(o=>o.w>0 && !o.inline && (o.w<24||o.h<24));
const tiny=[...doc.querySelectorAll('*')].filter(el=>{
  if(!el.childNodes.length) return false;
  const t=[...el.childNodes].filter(n=>n.nodeType===3&&n.textContent.trim()).map(n=>n.textContent.trim()).join('');
  if(!t) return false;
  const r=el.getBoundingClientRect();
  return r.width>0 && parseFloat(getComputedStyle(el).fontSize)<11;
}).slice(0,8).map(el=>el.tagName.toLowerCase()+':'+el.textContent.trim().slice(0,24));
return {w:W, under24:bad, tinyText:tiny};
"""

P_BANDS = r"""
const out=[...doc.querySelectorAll('section,footer,nav')].map(s=>{
  const r=s.getBoundingClientRect();
  if(r.height<20) return null;
  const kids=[...s.querySelectorAll('*')].filter(el=>{
    const k=el.getBoundingClientRect();
    return k.width>0&&k.height>0&&(el.textContent||'').trim().length>0;
  });
  if(!kids.length) return null;
  const L=Math.min(...kids.map(k=>k.getBoundingClientRect().left));
  const R=Math.max(...kids.map(k=>k.getBoundingClientRect().right));
  return {band:(s.id||s.className||s.tagName).toString().split(/\s+/)[0].slice(0,18),
          left:Math.round(L), right:Math.round(R)};
}).filter(Boolean);
return {w:W, bands:out};
"""

P_CONTRAST = r"""
function lin(c){c/=255;return c<=0.03928?c/12.92:Math.pow((c+0.055)/1.055,2.4);}
function lum(rgb){return 0.2126*lin(rgb[0])+0.7152*lin(rgb[1])+0.0722*lin(rgb[2]);}
function parse(s){const m=(s||'').match(/[\d.]+/g);return m?m.slice(0,3).map(Number).map(v=>v*(m.length>3&&+m[3]<1?1:1)):null;}
function bgOf(el){
  let n=el;
  while(n&&n!==doc.documentElement){
    const c=getComputedStyle(n).backgroundColor;
    const p=parse(c);
    if(p&&!/rgba\(0, 0, 0, 0\)/.test(c)){
      const a=(c.match(/[\d.]+/g)||[])[3];
      if(a===undefined||+a>0.5) return p;
    }
    n=n.parentElement;
  }
  return [255,255,255];
}
const rows=[];
[...doc.querySelectorAll('p,h1,h2,h3,h4,li,a,span,button,em,strong,code,figcaption,small')].forEach(el=>{
  const t=[...el.childNodes].filter(n=>n.nodeType===3&&n.textContent.trim()).map(n=>n.textContent.trim()).join(' ');
  if(!t) return;
  const r=el.getBoundingClientRect();
  if(r.width<2||r.height<2) return;
  const cs=getComputedStyle(el);
  if(cs.visibility==='hidden'||cs.display==='none'||+cs.opacity===0) return;
  const fg=parse(cs.color), bg=bgOf(el);
  if(!fg) return;
  const L1=lum(fg),L2=lum(bg);
  const ratio=(Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
  const px=parseFloat(cs.fontSize), bold=(parseInt(cs.fontWeight)||400)>=700;
  const large=px>=24||(bold&&px>=18.66);
  const need=large?3:4.5;
  if(ratio<need) rows.push({el:el.tagName.toLowerCase(),txt:t.slice(0,30),px:Math.round(px*10)/10,
    ratio:Math.round(ratio*100)/100,need:need,fg:cs.color,bg:'rgb('+bg.join(',')+')'});
});
rows.sort((a,b)=>a.ratio-b.ratio);
return {w:W, fails:rows.slice(0,12), n:rows.length};
"""

P_STRUCTURE = r"""
const ids=[...doc.querySelectorAll('[id]')].map(e=>e.id);
const dup=ids.filter((v,i)=>ids.indexOf(v)!==i);
return {w:W, lang:doc.documentElement.lang||null, title:doc.title,
  h:[...doc.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h=>h.tagName),
  dupIds:dup, imgsNoAlt:[...doc.querySelectorAll('img')].filter(i=>!i.hasAttribute('alt')).length,
  svgRoleImg:[...doc.querySelectorAll('svg[role=img]')].length,
  svgHidden:[...doc.querySelectorAll('svg[aria-hidden=true]')].length,
  live:[...doc.querySelectorAll('[aria-live]')].map(e=>e.getAttribute('aria-live')),
  focusRules:[...doc.styleSheets].length};
"""

P_STATE = r"""
const btns=[...doc.querySelectorAll('[data-step]')];
const status=doc.getElementById('case-status');
const panels=[...doc.querySelectorAll('[data-panel]')];
if(!btns.length) return {w:W, err:'no [data-step] buttons'};
const out=[];
function snap(tag){
  return {at:tag,
    tabs:btns.map(b=>b.dataset.step+':'+(b.getAttribute('aria-selected')==='true'?'SEL':'')
      +(b.hasAttribute('data-stale')?'+stale':'')+(b.hasAttribute('data-rerun')?'+rerun':'')
      +(b.hasAttribute('data-reopened')?'+reopened':'')).join(' '),
    shown:panels.filter(p=>p.hidden===false||getComputedStyle(p).display!=='none').map(p=>p.dataset.panel).join(','),
    status:(status?status.textContent.trim():'').slice(0,120)};
}
out.push(snap('load'));
btns.forEach(b=>{b.click();out.push(snap('click'+b.dataset.step));});
const reopen=doc.getElementById('reopen')||doc.querySelector('[data-reopen]')||[...doc.querySelectorAll('button')].find(b=>/reopen/i.test(b.textContent));
if(reopen){reopen.click();out.push(snap('reopen'));}
if(btns.length){btns[btns.length-1].click();out.push(snap('revisit-last'));}
const grammar=out.map(o=>o.status).filter(s=>s).map(s=>({s:s,bad:/\b1 (steps|steps that depend)\b|\b1 step(s)? that depend\b/.test(s)})).filter(o=>o.bad);
return {w:W, steps:out, grammarBugs:grammar, focusable:btns.filter(b=>b.tabIndex===0).map(b=>b.dataset.step)};
"""

PRESETS = {
    'overflow': P_OVERFLOW,
    'targets': P_TARGETS,
    'bands': P_BANDS,
    'contrast': P_CONTRAST,
    'structure': P_STRUCTURE,
    'state': P_STATE,
}
ALL = ['overflow', 'targets', 'bands', 'contrast', 'structure', 'state']


def stage(v=None, nojs=False):
    """Copy web/ to a temp dir with a fresh cache-bust token. Never edits web/.

    nojs=True strips every <script> from the copy, so a "with scripting off"
    figure is actually measured with scripting off. The probe's own script is
    separate and still runs — it is what reports the number.
    """
    v = v or str(int(time.time() * 1000))
    d = tempfile.mkdtemp(prefix='dada-measure-')
    site = os.path.join(d, 'site')
    shutil.copytree(WEB, site, symlinks=True)
    idx = os.path.join(site, 'index.html')
    s = open(idx, encoding='utf-8').read()
    if nojs:
        s = re.sub(r'<script\b[^>]*>.*?</script>', '', s, flags=re.S | re.I)
        s = re.sub(r'<script\b[^>]*/\s*>', '', s, flags=re.I)
    s2 = re.sub(r'([?&]v=)\d+', lambda m: m.group(1) + v, s)
    if s2 == s and '?v=' not in s:
        s2 = s.replace('.css"', '.css?v=%s"' % v).replace('.js"', '.js?v=%s"' % v)
    open(idx, 'w', encoding='utf-8').write(s2)
    probe = os.path.join(d, 'probe.html')
    open(probe, 'w', encoding='utf-8').write(PROBE)
    return d, site, probe


def render(probe, src, code, w, h, delay, nojs, shot=None, extra=()):
    url = 'file://%s?src=file://%s&w=%d&h=%d&d=%d&js=%s%s' % (
        probe, src, w, h, delay,
        __import__('urllib.parse', fromlist=['quote']).quote(code),
        '&nojs=1' if nojs else '')
    cmd = [CHROME, '--headless=new', '--no-sandbox', '--disable-gpu',
           '--allow-file-access-from-files',
           '--virtual-time-budget=15000']
    if shot:
        cmd += ['--screenshot=' + shot, '--window-size=%dx%d' % (w, h)]
    cmd += list(extra) + ['--dump-dom', url]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    return p.stdout, p.stderr


def extract(dump):
    m = re.search(r'<pre id="out">(.*?)</pre>', dump, re.S)
    if not m:
        return 'ERR no result element — page or probe failed to load'
    return html.unescape(m.group(1)).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--preset', help='one of: %s, all' % ', '.join(PRESETS))
    ap.add_argument('--file', help='file containing the JS snippet')
    ap.add_argument('--expr', help='inline JS snippet')
    ap.add_argument('--widths', default='1700,1440,1200,1000,900,768,650,500,390,320')
    ap.add_argument('--h', type=int, default=3000, help='iframe height (page height)')
    ap.add_argument('--fold', type=int, default=0,
                    help='use this as the iframe height instead of --h (viewport-sized capture)')
    ap.add_argument('--nojs', action='store_true', help='load the page without scripting')
    ap.add_argument('--delay', type=int, default=2500)
    ap.add_argument('--shot', metavar='OUT.png', help='screenshot at the first width instead of measuring')
    ap.add_argument('--raw', action='store_true', help='print raw strings, not JSON')
    a = ap.parse_args()

    if a.file:
        code = open(a.file, encoding='utf-8').read()
        names = ['snippet']
    elif a.expr:
        code = a.expr
        names = ['snippet']
    else:
        names = ALL if (a.preset or 'all') == 'all' else [a.preset]
        if a.preset not in (None, 'all') and a.preset not in PRESETS:
            ap.error('unknown preset %r' % a.preset)
        code = None

    widths = [int(x) for x in a.widths.split(',') if x.strip()]
    height = a.fold or a.h

    d, site, probe = stage(nojs=a.nojs)
    try:
        if a.shot:
            w = widths[0]
            out = a.shot if os.path.isabs(a.shot) else os.path.join(os.getcwd(), a.shot)
            dump, err = render(probe, os.path.join(site, 'index.html'), code or 'return 1',
                               w, height, a.delay, a.nojs, shot=out)
            print('%s (%dx%d)' % (out, w, height))
            return 0 if os.path.exists(out) else 1

        bad = False
        for w in widths:
            print('=== %d ===' % w)
            for name in names:
                c = code if code is not None else PRESETS[name]
                dump, err = render(probe, os.path.join(site, 'index.html'), c,
                                   w, height, a.delay, a.nojs)
                res = extract(dump)
                if res.startswith('ERR'):
                    bad = True
                    print('%s: %s' % (name, res))
                    continue
                if a.raw or len(names) == 1 and code is not None:
                    print(res)
                    continue
                try:
                    print('%s: %s' % (name, json.dumps(json.loads(res), separators=(',', ':'))))
                except ValueError:
                    print('%s: %s' % (name, res))
        return 1 if bad else 0
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
