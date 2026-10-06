import {createSculpture} from './art.js';
const sculpture=createSculpture(document.getElementById('hero-sculpture'));
const motion=document.getElementById('motion-toggle');
function syncMotion(){motion.setAttribute('aria-pressed',String(sculpture.state.paused));motion.innerHTML=sculpture.state.paused?'Resume motion <span aria-hidden="true">▷</span>':'Pause motion <span aria-hidden="true">Ⅱ</span>';}
if(sculpture){syncMotion();motion.addEventListener('click',()=>{sculpture.setPaused(!sculpture.state.paused);syncMotion();});document.getElementById('hero-sculpture').addEventListener('motionchange',syncMotion);}
