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
