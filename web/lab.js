import {createSculpture} from './art.js?v=07';

export function setupLab(){
  const section=document.getElementById('studio');
  if(!section)return null;
  const canvas=section.querySelector('canvas');
  const sculpture=createSculpture(canvas);
  if(!sculpture)return null;
  const controls=section.querySelector('.studio-controls');
  const tension=section.querySelector('#studio-tension');
  const value=section.querySelector('#studio-value');
  const motion=section.querySelector('#studio-motion');
  const status=section.querySelector('#studio-status');
  const pigment=section.querySelector('#studio-pigment');
  const exporter=section.querySelector('#studio-export');
  controls.hidden=false;
  section.classList.add('studio-ready');
  function syncMotion(){
    motion.textContent=sculpture.state.paused?'Resume motion':'Pause motion';
    motion.setAttribute('aria-pressed',String(sculpture.state.paused));
  }
  syncMotion();
  tension.addEventListener('input',()=>{
    sculpture.setAmbition(Number(tension.value)/100);
    value.value=tension.value+' / 100';
    canvas.setAttribute('aria-label','Original three-dimensional folded form at tension '+tension.value+' of 100, with '+sculpture.state.palette+' pigment.');
  });
  section.querySelectorAll('[data-pigment]').forEach(button=>button.addEventListener('click',()=>{
    sculpture.setPalette(button.dataset.pigment);
    section.querySelectorAll('[data-pigment]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
    pigment.textContent=button.textContent.trim();
    canvas.setAttribute('aria-label','Original three-dimensional folded form at tension '+tension.value+' of 100, with '+sculpture.state.palette+' pigment.');
  }));
  section.querySelectorAll('[data-turn]').forEach(button=>button.addEventListener('click',()=>{
    sculpture.setPaused(true);
    sculpture.rotateBy(Number(button.dataset.turn));
    syncMotion();
  }));
  motion.addEventListener('click',()=>{
    sculpture.setPaused(!sculpture.state.paused);
    syncMotion();
  });
  canvas.addEventListener('motionchange',syncMotion);
  exporter.addEventListener('click',()=>{
    sculpture.draw();
    if(!canvas.width||!canvas.height){status.textContent='The form is still preparing. Try again in a moment.';return;}
    exporter.disabled=true;
    status.textContent='Preparing your form…';
    const output=document.createElement('canvas');
    const artworkWidth=1200;
    const artworkHeight=Math.round(artworkWidth*canvas.height/canvas.width);
    output.width=artworkWidth;
    output.height=artworkHeight+150;
    const context=output.getContext('2d');
    if(!context){exporter.disabled=false;status.textContent='PNG export is unavailable in this browser.';return;}
    context.fillStyle='#f2efe6';
    context.fillRect(0,0,output.width,output.height);
    context.drawImage(canvas,0,0,artworkWidth,artworkHeight);
    context.fillStyle='#191915';
    context.fillRect(50,artworkHeight+20,1100,1);
    context.font='700 34px Arial, sans-serif';
    context.fillText('DADA / FORM STUDY',50,artworkHeight+75);
    context.font='18px monospace';
    context.fillText('TENSION '+tension.value+' / '+sculpture.state.palette.toUpperCase(),50,artworkHeight+110);
    context.textAlign='right';
    context.fillText('MAKE A DIFFERENT DECISION.',1150,artworkHeight+110);
    output.toBlob(blob=>{
      exporter.disabled=false;
      if(!blob){status.textContent='The image could not be exported. Try again.';return;}
      const url=URL.createObjectURL(blob);
      const link=document.createElement('a');
      link.href=url;
      link.download='dada-form-'+tension.value+'-'+sculpture.state.palette+'.png';
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(()=>URL.revokeObjectURL(url),60000);
      status.textContent='Your PNG download is ready.';
    },'image/png');
  });
  return sculpture;
}
