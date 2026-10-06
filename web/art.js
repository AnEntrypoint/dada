const tau=Math.PI*2;
const unit=vector=>{const length=Math.hypot(...vector)||1;return vector.map(value=>value/length);};
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const center=(u,ambition)=>{const angle=u*tau;const bend=.42+ambition*.38;const radius=1.6+bend*Math.cos(angle*3);return [radius*Math.cos(angle*2),radius*Math.sin(angle*2),(.8+ambition*.52)*Math.sin(angle*3)];};
function surface(u,v,ambition){const c=center(u,ambition);const next=center(u+.0001,ambition);const tangent=unit(next.map((value,index)=>value-c[index]));const side=unit(cross(tangent,[0,0,1]));const normal=unit(cross(tangent,side));const rupture=u>.71&&u<.84?Math.sin((u-.71)/.13*Math.PI):0;const angle=v*tau+rupture*2.4;const width=.27+ambition*.19+rupture*.24;const edge=.09+.018*Math.sin(u*tau*12);return c.map((value,index)=>value+side[index]*(Math.cos(angle)*width+rupture*.32)+normal[index]*(Math.sin(angle)*edge+rupture*.28));}
function rotate(point,yaw,pitch){const y=Math.cos(yaw),s=Math.sin(yaw),p=Math.cos(pitch),q=Math.sin(pitch);const x=point[0]*y+point[2]*s;const z=-point[0]*s+point[2]*y;return [x,point[1]*p-z*q,point[1]*q+z*p];}
export function createSculpture(canvas){
  const context=canvas.getContext('2d');
  if(!context)return null;
  const preference=matchMedia('(prefers-reduced-motion: reduce)');
  const state={ambition:.63,yaw:-.34,pitch:.58,paused:preference.matches,palette:'vermilion',visible:true};
  let width=0,height=0,lastTime=0,frame=0;
  const observer=new ResizeObserver(entries=>{const bounds=entries[0].contentRect;width=bounds.width;height=bounds.height;const ratio=Math.min(devicePixelRatio||1,1.5);canvas.width=Math.round(width*ratio);canvas.height=Math.round(height*ratio);context.setTransform(ratio,0,0,ratio,0,0);draw();});
  const viewObserver=new IntersectionObserver(entries=>{state.visible=entries[0].isIntersecting;if(state.visible)draw();});
  observer.observe(canvas);viewObserver.observe(canvas);
  function draw(){
    if(!width||!height)return;
    context.clearRect(0,0,width,height);
    const scale=Math.min(width,height)*.145;
    const origin=[width*.55,height*.49];
    const shadow=context.createRadialGradient(origin[0],height*.84,0,origin[0],height*.84,width*.3);
    shadow.addColorStop(0,'rgba(25,25,21,.14)');shadow.addColorStop(1,'rgba(25,25,21,0)');
    context.save();context.translate(0,height*.70);context.scale(1,.15);context.fillStyle=shadow;context.fillRect(0,0,width,height);context.restore();
    const faces=[];const around=96,across=24;
    const project=point=>{const depth=8/(8-point[2]);return [origin[0]+point[0]*scale*depth,origin[1]+point[1]*scale*depth];};
    for(let i=0;i<around;i+=1){for(let j=0;j<across;j+=1){const points=[[i,j],[i+1,j],[i+1,j+1],[i,j+1]].map(([u,v])=>rotate(surface(u/around,v/across,state.ambition),state.yaw,state.pitch));const a=points[0],b=points[1],c=points[3];const normal=unit(cross(b.map((value,index)=>value-a[index]),c.map((value,index)=>value-a[index])));const light=Math.abs(normal[0]*-.3+normal[1]*-.6+normal[2]*.74);const seam=i>around*.71&&i<around*.84;const dark=i<around*.29||i>around*.86;const colors=seam?(state.palette==='cobalt'?[43,70,200]:state.palette==='graphite'?[80,80,71]:[231,65,39]):dark?[55,56,49]:[231,225,209];const shade=.55+light*.48;const color=colors.map(value=>Math.round(value*shade));faces.push({points:points.map(project),depth:points.reduce((sum,p)=>sum+p[2],0)/4,color,ink:dark});}}
    faces.sort((a,b)=>a.depth-b.depth);
    for(const face of faces){context.beginPath();face.points.forEach((point,index)=>index?context.lineTo(...point):context.moveTo(...point));context.closePath();context.fillStyle=`rgb(${face.color.join(',')})`;context.fill();context.strokeStyle=`rgba(${face.color.join(',')},.7)`;context.lineWidth=.65;context.stroke();}
  }
  function animate(time){const delta=Math.min((time-lastTime)||0,50);lastTime=time;if(!state.paused&&state.visible&&!document.hidden){state.yaw+=delta*.000075;draw();}frame=requestAnimationFrame(animate);}
  frame=requestAnimationFrame(animate);
  preference.addEventListener('change',event=>{state.paused=event.matches;draw();canvas.dispatchEvent(new CustomEvent('motionchange',{detail:state.paused}));});
  canvas.closest('figure')?.classList.add('sculpture-ready');
  return {state,draw,setAmbition(value){state.ambition=value;draw();},setPalette(value){state.palette=value;draw();},setPaused(value){state.paused=value;draw();},rotateBy(value){state.yaw+=value;draw();},exportImage(){draw();return canvas.toDataURL('image/png');},destroy(){cancelAnimationFrame(frame);observer.disconnect();viewObserver.disconnect();}};
}
