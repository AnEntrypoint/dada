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
  const state=reopened.has(step)?'reopened':stale.has(step)?'stale, depends on a reopened decision':rerun.has(step)?'re-run, was stale':'';
  button.setAttribute('aria-label',name+(state?', '+state:''));
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

function showStep(step){
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
  const n=stale.size;
  caseStatus.textContent=kickerOf(step)+' — recorded design study.'+(wasStale?' Re-run: it was marked stale.':'')+(n?' '+n+' later step'+(n>1?'s':'')+' still marked stale.':'');
  return true;
}

function reopenEarlier(){
  const at=Math.max(0,order.indexOf(current)-1);
  const target=order[at];
  order.slice(at+1).forEach(step=>stale.add(step));
  reopened.add(target);
  showStep(target);
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
    button.addEventListener('click',()=>showStep(button.dataset.step));
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
  showStep('brief');
}

const copyStatus=document.getElementById('copy-status');
document.querySelectorAll('[data-copy]').forEach(button=>{
  button.hidden=false;
  button.addEventListener('click',async()=>{
    const source=document.getElementById(button.dataset.copy);
    if(!source)return;
    const original=button.textContent;
    const done=()=>{button.textContent='Copied \u2713';setTimeout(()=>{button.textContent=original;},2600);};
    try{
      await navigator.clipboard.writeText(source.textContent);
      copyStatus.textContent=button.dataset.copy==='install-command'?'Setup copied. Run it in your project folder.':'Brief copied. Bring it to your agent.';
      done();
    }catch{
      const range=document.createRange();
      range.selectNodeContents(source);
      const selection=getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      copyStatus.textContent='Text selected. Use your browser copy command.';
    }
  });
});
