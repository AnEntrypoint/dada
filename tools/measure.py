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
    python3 tools/measure.py --preset state --widths 390

The snippet runs with (doc, win, W, H) in scope. Return anything
JSON-serialisable, or a string for raw output.

Three readings that cost a round to learn: `--fold N` is the *iframe height*,
so it is the viewport `win.innerHeight` sees — omit it and every width reports
3,000px tall, and any "above the fold" figure is fiction. And the `contrast`
preset's `n` is the number of **failing** rows, so `n:0` with an empty `fails`
is a clean run, not an unrun one. And the `state` preset drives the install
section's copy buttons, not a tab strip: it reports how many of them are still
`hidden` once the script has run, so `hidden:0` is both buttons revealed.

`--preset cross` answers the question this page keeps being asked: while the
sculpture descends, is any word read against it? It pauses every animation on
the page and drives them all to the same instant of the fall, then composites
the artwork's own pixels over the hero gradient under each visible word and
takes the contrast against that word's own colour, at 41 instants. `total` is
the count of instants at which a visible word sat below 4.5:1, so `total:0` is
clean; `firstVisible` is the fraction of the fall at which a word's beat let it
in, and `crossed` is the px of the artwork's ink under it.

Reduced motion is a Chromium switch, not a snippet — nothing in the page can
turn the media query on, so set it in the launch:
`CHROME_ARGS=--force-prefers-reduced-motion python3 tools/measure.py ...`
Extra flags from `CHROME_ARGS` are appended to the browser command line.
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
// window.onerror first, so a probe that dies before it can attach its listener
// still says why: a snippet containing "%" used to throw inside the (redundant)
// second decode below, and the run reported a clean "pending" instead of an error.
window.onerror=function(m){var o=document.getElementById('out');if(o.textContent==='pending')o.textContent='ERR probe: '+m;};
const q=new URLSearchParams(location.search);
const W=+q.get('w')||1440,H=+q.get('h')||3000;
const src=q.get('src')||'';
const f=document.getElementById('f');f.src=src;
f.style.width=W+'px';f.style.height=H+'px';
// q.get() already decodes; decoding again turns any literal "%" in a snippet
// into a URIError, which used to kill the probe before it ever ran.
const code=q.get('js')||'return 1;';
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

P_CROSS = r"""
// What the object crosses, and whether a word is ever read against it.
// Every animation on the page is paused and driven to the same instant, so
// the sculpture's place and each word's beat are sampled together. The ink
// under a visible word is composited over the hero's own gradient and its
// contrast taken against the word's own colour, pixel by pixel.
var STEPS = 41, STRIDE = 2, FLOOR = 4.5;
var BG0 = [247, 244, 238], BG1 = [238, 233, 220];   // .hero, 180deg
function lin(c){c/=255;return c<=0.03928?c/12.92:Math.pow((c+0.055)/1.055,2.4);}
function lum(c){return 0.2126*lin(c[0])+0.7152*lin(c[1])+0.0722*lin(c[2]);}
function ratio(a,b){var l1=lum(a),l2=lum(b);return (Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05);}
function rgb(s){var m=(s||'').match(/(\d+(?:\.\d+)?)/g);return m?[+m[0],+m[1],+m[2]]:[0,0,0];}
function bgAt(y,hr){var t=(y-hr.top)/(hr.height||1);t=t<0?0:t>1?1:t;
  return [0,1,2].map(function(i){return BG0[i]+(BG1[i]-BG0[i])*t;});}

var hero=doc.querySelector('.hero'), img=doc.querySelector('.hero-art img');
var all=doc.getAnimations?doc.getAnimations():[];
all.forEach(function(a){a.pause();});
var sink=(img.getAnimations?img.getAnimations():[])[0];
var dur=sink?sink.effect.getTiming().duration:0;
if(!dur) return {w:W, error:'no animation on .hero-art img'};

var ir=img.getBoundingClientRect();
var bw=Math.max(1,Math.round(ir.width)), bh=Math.max(1,Math.round(ir.height));
var cv=doc.createElement('canvas'); cv.width=bw; cv.height=bh;
var cx=cv.getContext('2d');
try{ cx.drawImage(img,0,0,bw,bh); }catch(e){ return {w:W, error:'draw: '+e.message}; }
var px=null;
try{ px=cx.getImageData(0,0,bw,bh).data; }catch(e){ return {w:W, error:'tainted: '+e.message}; }

var WORDS=[['.hero-bottom span:nth-child(1)','strip#1'],
           ['.hero-bottom span:nth-child(2)','strip#2'],
           ['.hero-description','description'],
           ['.build-chip','chip'],
           ['.hero .text-action','cta'],
           ['.hero h1','headline'],
           ['.hero-art figcaption span','caption']];
var els=WORDS.map(function(p){return {n:p[1], el:doc.querySelector(p[0])};})
             .filter(function(o){return o.el;});
els.forEach(function(o){o.color=rgb(win.getComputedStyle(o.el).color);});

var res=els.map(function(o){return {n:o.n, firstVisible:null, crossed:0,
                                    worst:99, worstU:null,
                                    visWorst:99, visWorstU:null, visBad:0};});
var violations=[];
for(var s=0;s<STEPS;s++){
  var u=s/(STEPS-1), t=u*dur;
  all.forEach(function(a){try{a.currentTime=t;}catch(e){}});
  var hr=hero.getBoundingClientRect(), r=img.getBoundingClientRect();
  els.forEach(function(o,k){
    var op=parseFloat(win.getComputedStyle(o.el).opacity);
    var vis=op>0.5;
    if(vis && res[k].firstVisible===null) res[k].firstVisible=+u.toFixed(3);
    var b=o.el.getBoundingClientRect();
    if(b.width<=0||b.height<=0) return;
    var x0=Math.max(b.left,r.left), x1=Math.min(b.right,r.right);
    var y0=Math.max(b.top,r.top),  y1=Math.min(b.bottom,r.bottom);
    if(x1<=x0||y1<=y0) return;
    for(var y=y0;y<y1;y+=STRIDE){
      var bg=bgAt(y,hr);
      for(var x=x0;x<x1;x+=STRIDE){
        var cxi=Math.round(x-r.left), cyi=Math.round(y-r.top);
        if(cxi<0||cyi<0||cxi>=bw||cyi>=bh) continue;
        var o4=(cyi*bw+cxi)*4, a=px[o4+3]/255;
        if(a<0.06) continue;
        res[k].crossed+=STRIDE*STRIDE;
        var over=[0,1,2].map(function(i){return px[o4+i]*a+bg[i]*(1-a);});
        var rr=ratio(o.color,over);
        if(rr<res[k].worst){res[k].worst=rr;res[k].worstU=+u.toFixed(3);}
        if(!vis) continue;
        if(rr<res[k].visWorst){res[k].visWorst=rr;res[k].visWorstU=+u.toFixed(3);}
        if(rr<FLOOR) res[k].visBad+=STRIDE*STRIDE;
      }
    }
    if(res[k].visBad>0 && res[k].visWorstU===+u.toFixed(3))
      violations.push({n:o.n, u:+u.toFixed(3), ratio:+res[k].visWorst.toFixed(2)});
  });
}
els.forEach(function(o,k){
  res[k].worst=+res[k].worst.toFixed(2);
  res[k].visWorst=+res[k].visWorst.toFixed(2);
});
return {w:W, dur:dur, steps:STEPS, stride:STRIDE, floor:FLOOR,
        words:res, violations:violations,
        total:violations.reduce(function(a,v){return a+1;},0)};
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
const btns=[...doc.querySelectorAll('[data-copy]')];
const status=doc.getElementById('copy-status');
if(!btns.length) return {w:W, err:'no [data-copy] buttons'};
const out=[];
function snap(tag){
  return {at:tag, hidden:btns.filter(b=>b.hidden).length,
    labels:btns.map(b=>b.textContent.trim()).join(' | '),
    status:(status?status.textContent.trim():'').slice(0,120)};
}
out.push(snap('load'));
btns.forEach(b=>{b.click();out.push(snap('click'+b.dataset.copy));});
const grammar=out.map(o=>o.status).filter(Boolean)
  .map(s=>({s:s,bad:/\b1 (steps|items|characters)\b/.test(s)})).filter(o=>o.bad);
return {w:W, steps:out, grammarBugs:grammar, focusable:btns.filter(b=>!b.hidden).length};
"""

PRESETS = {
    'overflow': P_OVERFLOW,
    'targets': P_TARGETS,
    'bands': P_BANDS,
    'contrast': P_CONTRAST,
    'structure': P_STRUCTURE,
    'state': P_STATE,
    'cross': P_CROSS,
}
ALL = ['overflow', 'targets', 'bands', 'contrast', 'structure', 'state', 'cross']

# The case panels are hidden unless their tab is chosen, so a rect taken inside
# one reads 0x0. Clicking the tab first is the whole of the fix.
TAB_PRELUDE = (
    "(function(){var _n=%s;"
    "var _t=doc.getElementById('step-'+_n)||doc.querySelector('[data-step=\"'+_n+'\"]')"
    "||doc.querySelector(_n);"
    "if(_t)_t.click();})();\n")


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


def warn_snippet(code):
    """Name the three traps that make a snippet lie instead of fail.

    `document` is the probe wrapper, not the page: it is empty of the staged
    copy, so a snippet that reaches for it finds 0 elements and reports a clean
    zero rather than an error. `doc` is the page.
    """
    if re.search(r'\bdocument\s*\.', code):
        sys.stderr.write(
            'warning: snippet uses `document` — the staged page is `doc`. '
            '`document` is the empty probe wrapper, so this returns 0 elements, '
            'not an error.\n')
    if re.search(r'\bquerySelector\(\s*[\'"][^\'"]*,', code):
        sys.stderr.write(
            'warning: querySelector() with a comma list returns only the first '
            'match — use querySelectorAll().\n')
    if re.search(r'\}\s*\(\s*\)|^\s*\(function', code, re.M):
        sys.stderr.write(
            'warning: an IIFE in a snippet throws — the probe wraps the code as '
            'a function body, so write statements and a return.\n')


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
    ap.add_argument('--tab', metavar='STEP',
                    help='click this case-study tab before measuring (brief, ideas, make, '
                         'critique, refine, or a selector) — panels are hidden otherwise')
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

    if code:
        warn_snippet(code)

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
                if a.tab:
                    c = TAB_PRELUDE % json.dumps(a.tab) + c
                dump, err = render(probe, os.path.join(site, 'index.html'), c,
                                   w, height, a.delay, a.nojs,
                                   extra=os.environ.get('CHROME_ARGS', '').split())
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
