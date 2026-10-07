const caseStudy=document.getElementById('case-study');
const stepButtons=[...document.querySelectorAll('[data-step]')];
const stepPanels=[...document.querySelectorAll('[data-panel]')];
const caseStatus=document.getElementById('case-status');

function showStep(step,announce=true){
  const panel=stepPanels.find(item=>item.dataset.panel===step);
  if(!panel)return false;
  stepPanels.forEach(item=>{item.hidden=item!==panel;});
  stepButtons.forEach(button=>{button.setAttribute('aria-pressed',String(button.dataset.step===step));});
  if(announce)caseStatus.textContent=panel.querySelector('.case-kicker').textContent+' — recorded design study.';
  return true;
}

if(caseStudy&&stepButtons.length===stepPanels.length&&stepPanels.length){
  caseStudy.classList.add('enhanced-case');
  document.querySelector('[data-step-controls]').hidden=false;
  showStep('refine',false);
  stepButtons.forEach(button=>button.addEventListener('click',()=>showStep(button.dataset.step)));
}

const copyStatus=document.getElementById('copy-status');
document.querySelectorAll('[data-copy]').forEach(button=>{
  button.hidden=false;
  button.addEventListener('click',async()=>{
    const source=document.getElementById(button.dataset.copy);
    if(!source)return;
    try{
      await navigator.clipboard.writeText(source.textContent);
      copyStatus.textContent=button.dataset.copy==='install-command'?'Setup copied. Run it in your project folder.':'Brief copied. Bring it to your agent.';
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
