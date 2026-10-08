const caseStudy=document.getElementById('case-study');
const stepButtons=[...document.querySelectorAll('[data-step]')];
const stepPanels=[...document.querySelectorAll('[data-panel]')];
const caseStatus=document.getElementById('case-status');
const reopen=document.querySelector('[data-reopen]');

const order=stepButtons.map(button=>button.dataset.step);
const stale=new Set();
const rerun=new Set();
const reopened=new Set();
let current=order[0]||null;

function kickerOf(step){
  const panel=stepPanels.find(item=>item.dataset.panel===step);
  return panel?panel.querySelector('.case-kicker').textContent:step.toUpperCase();
}

function label(button){
  const step=button.dataset.step;
  const name=button.textContent.replace(/^\s+|\s+$/g,'');
  const states=[];
  if(reopened.has(step))states.push('reopened');
  if(stale.has(step))states.push('stale, depends on a reopened decision');
  if(rerun.has(step))states.push('was re-run after going stale');
  button.setAttribute('aria-label',name+(states.length?', '+states.join('; '):''));
}

function paint(){
  stepButtons.forEach(button=>{
    const step=button.dataset.step;
    button.toggleAttribute('data-reopened',reopened.has(step));
    button.toggleAttribute('data-stale',stale.has(step));
    button.toggleAttribute('data-rerun',rerun.has(step));
    label(button);
  });
  stepPanels.forEach(panel=>{
    const step=panel.dataset.panel;
    panel.toggleAttribute('data-reopened',reopened.has(step));
    panel.toggleAttribute('data-rerun',rerun.has(step));
  });
  if(reopen)reopen.disabled=order.indexOf(current)<=0;
}

// A return-mark with only one of its two terms beside it promises a return it
// cannot show: at 320 the buttons stack and three of the four arrows point at
// the next line rather than at the next step. Turn exactly the separators whose
// following button has wrapped, so the mark still joins the two terms it names
// — across a row where they sit side by side, down a row where they do not.
const separators=[...document.querySelectorAll('.case-controls i')];
function fitSeparators(){
  // Read phase, from the unturned geometry: clear the last pass first, or the
  // shift it wrote is measured as part of the slot it is correcting.
  separators.forEach(sep=>{sep.classList.remove('sep-turned');sep.style.left='0px';});
  const turned=separators.map((sep,index)=>{
    const before=stepButtons[index],after=stepButtons[index+1];
    return !!(before&&after&&Math.abs(after.offsetTop-before.offsetTop)>4);
  });
  // Write phase. A mark turned to point down does *not* get moved onto the next
  // button's centre: its box would then sit on the letters of a tab it does not
  // join (measured 156px² over "01 BRIEF" at 390, 156px² over "03 MAKE" at 320),
  // because the shift is horizontal while the mark keeps the previous row's
  // baseline. Down in its own slot it clears every tab's text — 0px² at
  // 320/390/500/650 — and still says "this row continues below".
  separators.forEach((sep,index)=>{
    if(turned[index])sep.classList.add('sep-turned');
  });
}

function showStep(step,move){
  const button=stepButtons.find(item=>item.dataset.step===step);
  const panel=stepPanels.find(item=>item.dataset.panel===step);
  if(!button||!panel)return false;
  stepPanels.forEach(item=>{item.hidden=item!==panel;});
  stepButtons.forEach(item=>{
    const on=item===button;
    item.setAttribute('aria-selected',String(on));
    item.tabIndex=on?0:-1;
  });
  const wasStale=stale.has(step);
  current=step;
  if(wasStale){stale.delete(step);rerun.add(step);}
  paint();
  // Only scroll for a move the reader made. On the initial paint the panel is
  // far below the fold, and scrolling to it would land the reader past the
  // hero before they have seen the page.
  if(move){
    const vh=window.innerHeight||document.documentElement.clientHeight||0;
    const top=panel.getBoundingClientRect().top;
    if(vh&&(top>vh-160||top<0))panel.scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
  }
  const later=order.slice(order.indexOf(step)+1).filter(s=>stale.has(s)).length;
  caseStatus.textContent=kickerOf(step)+' — recorded design study.'+(wasStale?' Re-run: it went stale and was revisited.':'')+(later?' '+later+' later step'+(later>1?'s':'')+' still marked stale.':'');
  return true;
}

function reopenEarlier(){
  const at=Math.max(0,order.indexOf(current)-1);
  const target=order[at];
  stale.clear();
  order.slice(at+1).forEach(step=>stale.add(step));
  reopened.add(target);
  showStep(target,true);
  const n=stale.size;
  caseStatus.textContent='REOPENED '+kickerOf(target)+' — '+n+' step'+(n>1?'s':'')+' that '+(n>1?'depend':'depends')+' on it marked stale until revisited.';
  stepButtons[at].focus();
}

if(caseStudy&&stepButtons.length&&stepPanels.length){
  caseStudy.classList.add('enhanced-case');
  document.querySelector('[data-step-controls]').hidden=false;
  stepButtons.forEach((button,index)=>{
    const panel=document.getElementById(button.getAttribute('aria-controls'));
    panel.setAttribute('role','tabpanel');
    panel.setAttribute('aria-labelledby',button.id);
    panel.tabIndex=0;
    button.addEventListener('click',()=>showStep(button.dataset.step,true));
    button.addEventListener('keydown',event=>{
      const move={ArrowRight:1,ArrowLeft:-1}[event.key];
      let target;
      if(move!==undefined)target=stepButtons[(index+move+stepButtons.length)%stepButtons.length];
      else if(event.key==='Home')target=stepButtons[0];
      else if(event.key==='End')target=stepButtons[stepButtons.length-1];
      else return;
      event.preventDefault();
      showStep(target.dataset.step);
      target.focus();
    });
  });
  if(reopen){
    reopen.hidden=false;
    reopen.addEventListener('click',reopenEarlier);
  }
  // The panel the reader is owed first is the one where the objections and their
  // measurements are printed: evidence before promise.
  showStep('critique');
  fitSeparators();
  addEventListener('resize',fitSeparators);
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(fitSeparators);
  // One objection is still undischarged (FORMALIST: the strip still reads as a
  // fixed sequence to a glancing reader). Carry it as an object, not as a voice:
  // CRITIQUE is reopened and every later step stale, so the debt is visible in
  // the strip and spoken in each button's accessible name — which survives the
  // first click, where a status line stating it once would not.
  if(order.includes('critique')){
    reopened.add('critique');
    order.slice(order.indexOf('critique')+1).forEach(step=>stale.add(step));
    paint();
  }
}

const copyStatus=document.getElementById('copy-status');
document.querySelectorAll('[data-copy]').forEach(button=>{
  button.hidden=false;
  button.addEventListener('click',async()=>{
    const source=document.getElementById(button.dataset.copy);
    if(!source)return;
    if(!button.dataset.label)button.dataset.label=button.textContent;
    const original=button.dataset.label;
    clearTimeout(button._revert);
    const flash=text=>{button.textContent=text;clearTimeout(button._revert);button._revert=setTimeout(()=>{button.textContent=original;},2600);};
    try{
      await navigator.clipboard.writeText(source.textContent);
      copyStatus.textContent=button.dataset.copy==='install-command'?'Setup copied. Run it in your project folder.':'Brief copied. Bring it to your agent.';
      flash('Copied ✓');
    }catch{
      const range=document.createRange();
      range.selectNodeContents(source);
      const selection=getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      copyStatus.textContent='Text selected. Use your browser copy command.';
      flash('Selected ✓');
    }
  });
});
