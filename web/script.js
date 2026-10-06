import {createSculpture} from './art.js?v=07';
const sculpture=createSculpture(document.getElementById('hero-sculpture'));
const motion=document.getElementById('motion-toggle');
function syncMotion(){motion.setAttribute('aria-pressed',String(sculpture.state.paused));motion.innerHTML=sculpture.state.paused?'Resume motion <span aria-hidden="true">▷</span>':'Pause motion <span aria-hidden="true">Ⅱ</span>';}
if(sculpture){motion.hidden=false;syncMotion();motion.addEventListener('click',()=>{sculpture.setPaused(!sculpture.state.paused);syncMotion();});document.getElementById('hero-sculpture').addEventListener('motionchange',syncMotion);}

import {setupLab} from './lab.js?v=07';
setupLab();

const copyStatus=document.getElementById('copy-status');
document.querySelectorAll('[data-copy]').forEach(button=>{button.hidden=false;button.addEventListener('click',async()=>{const source=document.getElementById(button.dataset.copy);try{await navigator.clipboard.writeText(source.textContent);copyStatus.textContent=button.dataset.copy==='install-command'?'Setup copied. Run it in your project folder.':'Brief copied. Bring it to your agent.';}catch{const range=document.createRange();range.selectNodeContents(source);const selection=getSelection();selection.removeAllRanges();selection.addRange(range);copyStatus.textContent='Text selected. Use your browser copy command.';}});});
