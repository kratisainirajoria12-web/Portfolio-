(()=>{
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const range=(p,a,b)=>clamp((p-a)/(b-a));
const ss=t=>t*t*(3-2*t);
const lerp=(a,b,t)=>a+(b-a)*t;
const damp=(a,b,l,dt)=>lerp(a,b,1-Math.exp(-l*dt));          // frame-rate independent smoothing
const $=s=>document.querySelector(s);
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
// monotone cubic keyframe track (never overshoots), keys [[u,value],...]
function track(K){const n=K.length,x=K.map(k=>k[0]),y=K.map(k=>k[1]),d=[],m=new Array(n).fill(0);
  for(let i=0;i<n-1;i++)d.push((y[i+1]-y[i])/(x[i+1]-x[i]));
  for(let i=1;i<n-1;i++){if(d[i-1]*d[i]>0){const h0=x[i]-x[i-1],h1=x[i+1]-x[i],w1=2*h1+h0,w2=h1+2*h0;m[i]=(w1+w2)/(w1/d[i-1]+w2/d[i]);}}
  return u=>{if(u<=x[0])return y[0];if(u>=x[n-1])return y[n-1];let i=0;while(u>x[i+1])i++;
    const h=x[i+1]-x[i],t=(u-x[i])/h,t2=t*t,t3=t2*t;
    return(2*t3-3*t2+1)*y[i]+(t3-2*t2+t)*h*m[i]+(-2*t3+3*t2)*y[i+1]+(t3-t2)*h*m[i+1];};}

/* ================= timeline (vh of scroll) ================= */
// One continuous shot. Every segment hands its last frame to the next one.
const TL={catch:[10,200],dive:[185.38,262],roots:[262,410],bloom:[410,1110],hold:[1110,1330],zoom:[1330,1440],
  macro:[1440,1600],drop:[1590,1745],fall:[1630,1800],end:[1800,1830]};
const TOTAL=1830;
// Krati's dive into the soil gets extra scroll: scroll space s is the story space u with the dive stretched
const D0=185.38,D1s=412,D1u=262,STRETCH=D1s-D1u,TOTAL_S=TOTAL+STRETCH;
const S2U=s=>s<D0?s:s<D1s?D0+(s-D0)*(D1u-D0)/(D1s-D0):s-STRETCH;
const U2S=u=>u<D0?u:u<D1u?D0+(u-D0)*(D1s-D0)/(D1u-D0):u+STRETCH;
const uOf=g=>S2U(g*TOTAL_S), gOf=u=>U2S(u)/TOTAL_S;
const catchU=f=>TL.catch[0]+f/117*(TL.catch[1]-TL.catch[0]);
const LOOP_U0=catchU(2);                          // the falling seed first enters the catch shot here
const LOOP_SHIFT=TL.end[0]-LOOP_U0;               // the end of the page is this point at the top
const vuOf=u=>u>=TL.end[0]?u-LOOP_SHIFT:u;

/* ================= frames ================= */
function seq(dir,n,k=1){return{dir,n,k,f:new Array(n)};}
const PLANT=seq('catch',109), DIVE=seq('dive',151,4), ROOTS=seq('grow',120), BLOOM=seq('bloom',280), HOLD=seq('hold',120,4), ZOOM=seq('zoom',22);
let loaded=0;const NEED=24;
const loader=$('#loader'), loadTxt=$('#loadTxt');
function load(S,i){return new Promise(r=>{if(i>=S.n||S.f[i])return r();const im=new Image();im.decoding='async';
  const sh=Math.floor(i/S.k);
  im.onload=()=>{if(S.k>1){for(let j=0;j<S.k&&sh*S.k+j<S.n;j++)S.f[sh*S.k+j]={sheet:im,row:j,naturalWidth:1280,naturalHeight:720};}
    else S.f[i]=im;if(S===PLANT&&i<NEED){loaded++;loadTxt.textContent='Planting… '+Math.round(loaded/NEED*100)+'%';}r()};
  im.onerror=r;im.src=S.k>1?S.dir+'/s'+String(sh).padStart(3,'0')+'.webp':S.dir+'/f'+String(i).padStart(3,'0')+'.webp';});}
/* scroll-aware loader: key frames of every section first, then the frames nearest the reader, 10 at a time */
const SEQPOS=()=>[[PLANT,TL.catch[0],D0],[DIVE,...TL.dive],[ROOTS,...TL.roots],[BLOOM,...TL.bloom],[HOLD,...TL.hold],[ZOOM,...TL.zoom]];
const loading=new Set();
function pickNext(){
  let tu=typeof target==='number'?uOf(target):0;if(tu>=TL.end[0])tu=0;if(tu>TL.zoom[1])tu=TL.zoom[1];const ts=U2S(tu);
  let best=null,bs=1e9;
  for(const [S,a,b] of SEQPOS())for(let i=0;i<S.n;i++){
    if(S.k>1&&i%S.k)continue;
    if(S.f[i]||loading.has(S.dir+i))continue;
    const p=S.pos?S.pos(i):a+(b-a)*i/Math.max(1,S.n-1);const key=i%8===0;
    const sc=Math.abs(U2S(p)-ts)/TOTAL_S*(key?.25:1)+(key?0:.04);
    if(sc<bs){bs=sc;best=[S,i];}}
  return best;}
function pump(){while(loading.size<10){const j=pickNext();if(!j)return;const [S,i]=j;const k=S.dir+i;loading.add(k);
  load(S,i).then(()=>{loading.delete(k);pump();});}}
(async()=>{await load(PLANT,0);await Promise.all([...Array(NEED)].map((_,i)=>load(PLANT,i)));loader.classList.add('done');pump();})();
addEventListener('scroll',()=>{if(loading.size<10)pump();},{passive:true});

const film=$('#film'),scv=$('#storyCv'),sctx=scv.getContext('2d'),gl3=$('#gl3'),dofEl=$('#dof'),tintEl=$('#tint');
function sizeCanvas(c){const d=Math.min(devicePixelRatio||1,2);c.width=Math.round(innerWidth*d);c.height=Math.round(innerHeight*d);const x=c.getContext('2d');x.imageSmoothingEnabled=true;x.imageSmoothingQuality='high';}
const portrait=()=>innerHeight>innerWidth*1.1;
const topCol=new WeakMap(),probe=document.createElement('canvas');probe.width=probe.height=1;const pctx=probe.getContext('2d',{willReadFrequently:true});
function skyOf(f){let c=topCol.get(f);if(!c){pctx.drawImage(f,0,0,f.naturalWidth,6,0,0,1,1);const d=pctx.getImageData(0,0,1,1).data;c=[d[0],d[1],d[2]];topCol.set(f,c);}return c;}
const grainEl=$('#grain'),scrimEl=$('#scrim'),dawnEl=$('#dawn'),vigEl=$('#vig');

/* golden pollen: drifts in front of the footage underground and around the bloom; scroll speed stirs it */
const pcv=$('#pollen'),pctx2=pcv.getContext('2d');
const MOTES=[...Array(innerWidth<760?45:90)].map(()=>({x:Math.random(),y:Math.random(),z:.3+Math.random()*.7,s:Math.random()*6.28}));
function pollenTick(u,time,vel,dt){
  const a=Math.max(Math.min(ss(range(u,228,280)),1-ss(range(u,560,640))), .85*Math.min(ss(range(u,1110,1170)),1-ss(range(u,1400,1450)))*(1-.55*Math.min(ss(range(u,1120,1160)),1-ss(range(u,1300,1330)))));
  if(a<=0.01){if(pcv.dataset.on){pctx2.clearRect(0,0,pcv.width,pcv.height);pcv.dataset.on='';}return;}
  pcv.dataset.on='1';const d=Math.min(devicePixelRatio||1,1.5);
  if(pcv.width!==Math.round(innerWidth*d)){pcv.width=Math.round(innerWidth*d);pcv.height=Math.round(innerHeight*d);}
  const W=pcv.width,H=pcv.height;pctx2.clearRect(0,0,W,H);pctx2.globalCompositeOperation='lighter';
  for(const m of MOTES){
    m.y-=(.015+Math.min(Math.abs(vel)*6,1.5)*.25*Math.sign(vel||1))*m.z*dt*(reduce?0:1);m.x+=Math.sin(time*.4+m.s)*.01*m.z*dt;
    if(m.y<-.05)m.y=1.05;if(m.y>1.05)m.y=-.05;
    const x=m.x*W,y=m.y*H,rad=(1.2+m.z*m.z*7)*d,tw=.55+.45*Math.sin(time*1.3+m.s*3);
    const g=pctx2.createRadialGradient(x,y,0,x,y,rad*2.6);g.addColorStop(0,`rgba(255,226,160,${.75*a*tw*m.z})`);g.addColorStop(.35,`rgba(255,190,110,${.25*a*tw*m.z})`);g.addColorStop(1,'rgba(255,170,80,0)');
    pctx2.fillStyle=g;pctx2.beginPath();pctx2.arc(x,y,rad*2.6,0,6.283);pctx2.fill();}
  pctx2.globalCompositeOperation='source-over';
}
let gLast=0;
(()=>{const c=document.createElement('canvas');c.width=c.height=160;const x=c.getContext('2d'),d=x.createImageData(160,160);
  for(let i=0;i<d.data.length;i+=4){const v=Math.random()*255|0;d.data[i]=d.data[i+1]=d.data[i+2]=v;d.data[i+3]=255;}
  x.putImageData(d,0,0);grainEl.style.backgroundImage=`url(${c.toDataURL()})`;})();
function grainTick(now){if(reduce||now-gLast<42)return;gLast=now;grainEl.style.backgroundPosition=`${Math.random()*160|0}px ${Math.random()*160|0}px`;}

/* ================= look: continuous grade + camera life (keyed like SEED) ================= */
const G={
  bri:track([[0,1],[200,.98],[260,1.06],[560,1.04],[700,1],[1110,1.03],[1440,1],[1560,1.04],[1700,1],[1830,1]]),
  sat:track([[0,1.02],[200,.95],[300,.88],[560,.92],[700,1.02],[1000,1.08],[1300,1.1],[1440,1.04],[1540,.9],[1650,.95],[1740,1],[1830,1.02]]),
  con:track([[0,1.02],[300,1.06],[700,1.02],[1300,1.03],[1540,1.08],[1700,1.02],[1830,1.02]]),
  vig:track([[0,.55],[200,.8],[300,1],[560,.95],[700,.65],[1110,.5],[1440,.6],[1560,.72],[1700,.5],[1830,.55]]),
  grain:track([[0,.06],[300,.09],[700,.06],[1300,.05],[1560,.07],[1830,.06]]),
  tint:track([[0,0],[1000,0],[1150,.12],[1400,.14],[1480,.05],[1560,.04],[1680,0],[1830,0]]),
  push:track([[0,0],[196,0],[206,.03],[215,.065],[224,0],[1830,0]]),   // the camera lunges as it breaks through the soil surface
  roll:track([[0,0],[180,0],[240,-.012],[330,.008],[470,-.006],[560,.012],[700,0],[1110,0],[1330,-.004],[1830,0]]),
  dof:track([[0,0],[1460,0],[1540,.85],[1600,1],[1660,.6],[1720,0],[1830,0]]),
};

/* ================= the shot: one canvas, one continuous camera ================= */
const pick=(S,i)=>{i=clamp(Math.round(i),0,S.n-1);let f=S.f[i];if(f)return f;
  for(let k=1;k<S.n;k++){if(S.f[i-k])return S.f[i-k];if(S.f[i+k])return S.f[i+k];}return null;};
// framing: m=1 full-bleed cover; m=0 (phones only) the underground letterbox used by the roots clip
function frameFit(iw,ih,fx,m){const cw=innerWidth,ch=innerHeight;
  const sc=Math.max(cw/iw,ch/ih);if(!portrait())m=1;
  const sl=Math.max(cw/iw,ch*.58/ih),s=lerp(sl,sc,m),w=iw*s,h=ih*s;
  return{s,w,h,dx:clamp(cw/2-fx*w,cw-w,0),dy:lerp((ch-h)*.45,(ch-h)/2,m)};}
function paint(img,fit,alpha=1,oy=0){
  if(!img)return;const d=scv.width/innerWidth;const {w,h,dx,dy}=fit;
  sctx.globalAlpha=alpha;
  if(img.sheet)sctx.drawImage(img.sheet,0,img.row*720,1280,720,dx*d,(dy+oy)*d,w*d,h*d);else sctx.drawImage(img,dx*d,(dy+oy)*d,w*d,h*d);
  sctx.globalAlpha=1;}
function bars(fit){const {h,dy}=fit,d=scv.width/innerWidth;if(h>=innerHeight-1)return;
  const col='rgb(5,4,3)',clr='rgba(5,4,3,0)';
  sctx.fillStyle=col;sctx.fillRect(0,0,scv.width,Math.max(0,dy*d));sctx.fillRect(0,(dy+h)*d,scv.width,scv.height);
  let g=sctx.createLinearGradient(0,dy*d,0,(dy+80)*d);g.addColorStop(0,col);g.addColorStop(1,clr);sctx.fillStyle=g;sctx.fillRect(0,dy*d,scv.width,80*d);
  g=sctx.createLinearGradient(0,(dy+h)*d,0,(dy+h-80)*d);g.addColorStop(0,col);g.addColorStop(1,clr);sctx.fillStyle=g;sctx.fillRect(0,(dy+h-80)*d,scv.width,80*d);}
// sub-frame blending: draw the frame and dissolve the next one in by the fraction, so scrubbing never steps
function paintBlend(get,fi,fit){const i0=Math.floor(fi),fr=fi-i0,A=get(i0),B=get(i0+1);
  paint(A,fit);if(fr>.02&&B&&B!==A)paint(B,fit,fr);bars(fit);}
const DIVE_T=[0.0,0.00686,0.01316,0.01924,0.02515,0.03107,0.03703,0.04298,0.04896,0.05484,0.06045,0.06619,0.07194,0.07749,0.0832,0.0895,0.09583,0.10268,0.1099,0.11722,0.1243,0.13125,0.13806,0.14461,0.15087,0.15681,0.16243,0.16777,0.17293,0.1779,0.18274,0.18748,0.19216,0.19675,0.20136,0.20601,0.21068,0.21536,0.22004,0.22461,0.22911,0.23355,0.23794,0.24233,0.24671,0.2511,0.25549,0.25987,0.26426,0.26865,0.27303,0.27742,0.28181,0.28619,0.29058,0.29497,0.29936,0.30374,0.30813,0.31257,0.31703,0.32153,0.32615,0.33087,0.33556,0.34024,0.3449,0.34946,0.35394,0.35842,0.36289,0.3674,0.37203,0.3768,0.38175,0.3867,0.39183,0.39715,0.40264,0.4083,0.41438,0.42069,0.4272,0.43395,0.44088,0.44802,0.45533,0.46282,0.47042,0.47816,0.48598,0.49391,0.50189,0.50993,0.518,0.52612,0.53422,0.54233,0.55044,0.55854,0.56657,0.57457,0.5825,0.59037,0.59813,0.60579,0.61335,0.62085,0.62821,0.63552,0.6428,0.65011,0.65741,0.66477,0.67221,0.67977,0.68741,0.69523,0.70324,0.71152,0.71909,0.72689,0.73491,0.74317,0.75165,0.76127,0.77111,0.78116,0.79139,0.80171,0.81211,0.82257,0.83306,0.84347,0.85383,0.86413,0.87436,0.88448,0.89454,0.90455,0.91451,0.92332,0.93209,0.94081,0.94948,0.95808,0.96668,0.97517,0.98355,0.99182,1.0];
// fractional dive frame for progress t, spaced by on-screen motion so the footage never judders
function diveFrame(t){let lo=0,hi=DIVE_T.length-1;if(t<=0)return 0;if(t>=1)return hi;
  while(hi-lo>1){const mid=(lo+hi)>>1;if(DIVE_T[mid]<=t)lo=mid;else hi=mid;}
  return lo+(t-DIVE_T[lo])/Math.max(1e-6,DIVE_T[hi]-DIVE_T[lo]);}

// bloom files: 0–22 the cracked seed, 23–182 the sprout leaving the seed and breaking through the soil (160 frames, four
// times the density of the rest so the camera tilt stays clean), 183–279 the sunflower. i is the story frame on the old 0–159 scale
const bloomIdx=i=>i<=23?i:i<63?23+(i-23)*4:i+120;
BLOOM.pos=k=>TL.bloom[0]+(k<=23?k:k<183?23+(k-23)/4:k-120)/159*(TL.bloom[1]-TL.bloom[0]);   // where a file sits in the story, for the loader

/* the seed head in 3D (three.js), created once the last zoom frame is in */
let MAC=null,macFail=false;
function macro(){if(MAC||macFail)return MAC;
  if(!window.THREE||!ZOOM.f[21]){if(!window.THREE)macFail=true;return null;}
  try{MAC=makeMacro(gl3,ZOOM.f[21]);}catch(e){macFail=true;MAC=null;}return MAC;}
let mouse={x:0,y:0,tx:0,ty:0};
addEventListener('pointermove',e=>{mouse.tx=e.clientX/innerWidth*2-1;mouse.ty=e.clientY/innerHeight*2-1;},{passive:true});

// where the falling seed sits in the catch footage (frame 2), in screen px
function catchSeed(oy){const f=frameFit(1280,720,innerWidth<760?.44:.5,1);
  return{x:f.dx+.4907*f.w,y:f.dy+.0097*f.h+oy,w:16*f.s};}

let holdT=0,holdLast=0;                                    // seconds spent in the sunflower pause
function shot(u,time){
  if(scv.width!==Math.round(innerWidth*Math.min(devicePixelRatio||1,2)))sizeCanvas(scv);
  const cw=innerWidth,ch=innerHeight,mob=cw<760,fxP=mob?.44:.5,d=scv.width/cw;
  const R=k=>range(u,TL[k][0],TL[k][1]);
  let use3D=false;
  holdT=(u>=TL.bloom[1]&&u<TL.hold[1])?holdT+Math.min(.1,Math.max(0,time-holdLast)):0;holdLast=time;
  sctx.fillStyle='#050403';sctx.fillRect(0,0,scv.width,scv.height);
  if(u<TL.catch[1]||u>=TL.end[0]){                           // Krati catches the seed and plants it
    paintBlend(i=>pick(PLANT,i),Math.min(108,range(vuOf(u),...TL.catch)*117),frameFit(1280,720,fxP,1));
  }else if(u<TL.dive[1]){                                    // Krati's own dive: the camera sinks into the soil with the seed, down into the glowing dark
    const t=R('dive'),i=diveFrame(t);
    paintBlend(k=>pick(DIVE,k),i,frameFit(1280,720,lerp(fxP,.5,ss(range(t,.2,.7))),1-ss(range(t,.62,.95))));
  }else if(u<TL.roots[1]){                                   // it cracks with light and roots
    paintBlend(i=>pick(ROOTS,i),R('roots')*119,frameFit(1280,720,.5,0));
  }else if(u<TL.bloom[1]){                                   // the shoot rises through the soil and grows into a sunflower
    const i=R('bloom')*159;paintBlend(k=>pick(BLOOM,k),bloomIdx(i),frameFit(1280,720,.5,ss(range(i,40,66))));
  }else if(u<TL.hold[1]){                                    // full bloom: the breeze moves the flower and the meadow
    const fit=frameFit(1280,720,.5,1);paint(pick(BLOOM,279),fit);
    const a=Math.min(ss(range(u,TL.hold[0],TL.hold[0]+28)),1-ss(range(u,TL.hold[1]-26,TL.hold[1])));
    // her reference clip, played in time: the camera eases back, the flower sways, butterflies cross. It starts on the
    // last bloom frame, plays forward and back, and rewinds to that frame as the reader scrolls in or out of the pause
    if(a>0&&!reduce){const n=HOLD.n-1,c=(holdT*12)%(2*n),ph=(c<=n?c:2*n-c)*a,k=Math.floor(ph),fr=ph-k,A=pick(HOLD,k),B=pick(HOLD,Math.min(n,k+1));
      if(A&&B){paint(A,fit,a);paint(B,fit,a*fr);}}
    else if(a>0)paint(pick(ZOOM,0),fit,a);
  }else if(u<TL.zoom[1]){                                    // the camera leans in
    paintBlend(k=>pick(ZOOM,k),R('zoom')*21,frameFit(1280,720,.5,1));
  }else{                                                     // the seed head, then the seeds let go and fall to Krati
    const M=macro(),F=ss(R('fall'));
    const fit=frameFit(1280,720,.5,1);
    if(F>0){                                                 // below the head: sky, then Krati's meadow rising into place
      const sky=PLANT.f[2]?skyOf(PLANT.f[2]):[150,190,225];
      sctx.fillStyle=`rgb(${sky})`;sctx.fillRect(0,0,scv.width,scv.height);
      const oy=ch*1.15*(1-ss(range(F,.15,1))),cf=frameFit(1280,720,fxP,1);
      paint(pick(PLANT,2),cf,1,oy);
      const yt=(cf.dy+oy)*d,g2=sctx.createLinearGradient(0,yt,0,yt+ch*.3*d);g2.addColorStop(0,`rgb(${sky})`);g2.addColorStop(1,`rgba(${sky},0)`);
      sctx.fillStyle=g2;sctx.fillRect(0,yt-2,scv.width,ch*.3*d);
      shot.oy=oy;
      // Krati's world stays in the dark until the seed is almost there, then fades up around it
      const dk=1-ss(range(u,1715,1790));if(dk>0){sctx.fillStyle=`rgba(5,4,3,${dk})`;sctx.fillRect(0,0,scv.width,scv.height);}
    }
    if(M){use3D=true;
      const cs=catchSeed(shot.oy||0),k=ss(range(F,.45,1));
      M.render({dark:ss(range(u,1590,1660)),reveal:ss(range(u,1715,1790)),rain:false,ripen:ss(R('macro')*1.15),push:range(u,TL.macro[0],TL.macro[1]+40),drop:R('drop'),fall:F,fade:ss(range(F,0,.25)),
        t:time,mx:mouse.x,my:mouse.y,reduce,motes:Math.min(ss(range(u,1450,1510)),1-ss(range(u,1700,1770))),
        heroScreen:null});
    }else{                                                   // no WebGL: hold the last zoom frame and let it rise away
      paint(pick(ZOOM,21),fit,1-F,-F*ch*1.1);
    }
  }
  gl3.style.visibility=use3D?'visible':'hidden';
}

/* ================= HUD + text ================= */
const CH=[[0,'01','The seed'],[240,'02','Roots'],[560,'03','Sprout'],[770,'04','Growth'],[1110,'05','Bloom'],[1440,'06','Seeds']];
const rail=$('#rail');
const railStops=[0,330,650,900,1180,1520];
CH.forEach((c,i)=>{const b=document.createElement('button');b.dataset.go=railStops[i];b.setAttribute('aria-label','Go to '+c[2]);b.innerHTML='<span>'+c[1]+' '+c[2]+'</span>';rail.appendChild(b);});
const railBtns=[...rail.children];
const chNum=$('#chNum'),chName=$('#chName'),dayEl=$('#day'),seasonEl=$('#season');
// split headings into letters (kept in words so lines still wrap), blocks get a stagger index
function splitText(el){let i=0,line=0;const letters=[];
  const walk=(node)=>{[...node.childNodes].forEach(n=>{
    if(n.nodeType===3){const frag=document.createDocumentFragment();
      n.textContent.split(/(\s+)/).forEach(tok=>{if(!tok)return;if(/^\s+$/.test(tok)){frag.appendChild(document.createTextNode(' '));return;}
        const w=document.createElement('span');w.className='w';
        for(const c of tok){const s=document.createElement('span');s.className='ch';s.textContent=c;s.style.setProperty('--i',i++);s.style.setProperty('--l',line);letters.push(s);w.appendChild(s);}
        frag.appendChild(w);});
      n.replaceWith(frag);}
    else if(n.nodeName==='BR'){line++;}
    else if(n.nodeType===1)walk(n);});};
  walk(el);letters.forEach(s=>s.style.setProperty('--n',i));}
const panels=[...document.querySelectorAll('.panel')].map(el=>{
  let b=0;[...el.children].forEach(c=>{if(/^H[12]$/.test(c.tagName))splitText(c);else{c.classList.add('blk');c.style.setProperty('--b',b++);}});
  return{el,a:+el.dataset.a,b:+el.dataset.b,live:false,timer:0};});
function setLive(p,on){if(p.live===on)return;p.live=on;clearTimeout(p.timer);const el=p.el;
  if(on){el.classList.remove('out','in');void el.offsetWidth;el.classList.add('live','in');}
  else{el.classList.remove('in');el.classList.add('out');p.timer=setTimeout(()=>{if(!p.live)el.classList.remove('live','out');},1500);}}
let lastCh=-1;
function hud(u){
  const vu=vuOf(u);
  let c=0;CH.forEach((x,i)=>{if(vu>=x[0])c=i});
  if(c!==lastCh){lastCh=c;chNum.textContent=CH[c][1];chName.textContent=CH[c][2];railBtns.forEach((b,i)=>b.classList.toggle('on',i===c));}
  const d=vu<190?0:Math.round(range(vu,190,1700)*92);
  dayEl.textContent='Day '+String(d).padStart(3,'0');
  seasonEl.textContent=d<32?'Spring':d<72?'Summer':'Late summer';
  document.body.dataset.ink=(vu>228&&vu<1720)?'light':'dark';
  document.body.dataset.hud='light';
  panels.forEach(p=>{let on=vu>=p.a&&vu<=p.b;
    if(p.el.id==='hello'&&u>TL.fall[0]+150&&u<TL.end[0])on=true;   // Krati's hello comes back as the seed reaches her
    setLive(p,on);});
}

/* ================= main loop ================= */
let target=0,cur=0,vel=0;
history.scrollRestoration='manual';
const maxScroll=()=>document.documentElement.scrollHeight-innerHeight;
function readScroll(){const max=maxScroll();target=max>0?clamp(scrollY/max):0;}
addEventListener('scroll',readScroll,{passive:true});
function resize(){sizeCanvas(scv);if(MAC)MAC.size();readScroll();}
document.querySelectorAll('[data-go]').forEach(b=>b.addEventListener('click',()=>{const max=maxScroll();
  const p=gOf(+b.dataset.go);scrollTo({top:p*max,behavior:(reduce||Math.abs(p-target)>.3)?'auto':'smooth'});}));
resize();addEventListener('resize',resize);
let t0=performance.now(),last=t0;
function frame(now){
  const dt=Math.min(.1,(now-last)/1000);last=now;
  const prev=cur;
  cur=reduce?target:damp(cur,target,4.2,dt); if(Math.abs(target-cur)<1e-6)cur=target;
  vel=damp(vel,(cur-prev)/Math.max(dt,1e-3),6,dt);
  // seamless loop: the bottom of the page shows the same frames as the top, so jump back up unnoticed
  const lim=gOf(TL.end[0]+(TL.end[1]-TL.end[0])*.5);
  if(cur>lim&&target>lim){const dg=(U2S(TL.end[0])-U2S(LOOP_U0))/TOTAL_S,max=maxScroll();cur-=dg;target-=dg;
    document.documentElement.style.scrollBehavior='auto';scrollTo(0,Math.max(0,target*max));}
  const u=uOf(cur),vu=vuOf(u),time=(now-t0)/1000;
  mouse.x=damp(mouse.x,mouse.tx,2.5,dt);mouse.y=damp(mouse.y,mouse.ty,2.5,dt);
  // camera life on the footage: slow handheld drift, mouse parallax, keyed roll, breathing scale
  const idle=reduce?0:1,inMacro=u>TL.macro[0]&&u<TL.end[0];
  const px=(-mouse.x*9+Math.sin(time*.13)*5)*idle*(inMacro?.3:1),py=(-mouse.y*6+Math.sin(time*.17+1.3)*3.5)*idle*(inMacro?.3:1);
  // during the sunflower pause the camera only drifts: no breathing zoom, no roll
  const still=Math.min(ss(range(vu,1100,1140)),1-ss(range(vu,1310,1340)));
  const sc=1.04+G.push(vu)+.005*Math.sin(time*.21)*idle*(1-still),rl=G.roll(vu)+Math.sin(time*.11)*.0015*idle*(1-still);
  film.style.transform=`translate3d(${px.toFixed(2)}px,${py.toFixed(2)}px,0) rotate(${rl.toFixed(4)}rad) scale(${sc.toFixed(4)})`;
  film.style.filter=`brightness(${G.bri(vu).toFixed(3)}) saturate(${G.sat(vu).toFixed(3)}) contrast(${G.con(vu).toFixed(3)})`;
  vigEl.style.opacity=G.vig(vu).toFixed(3);grainEl.style.opacity=G.grain(vu).toFixed(3);
  tintEl.style.opacity=G.tint(vu).toFixed(3);{const dv=G.dof(u<TL.end[0]?u:0);dofEl.style.opacity=dv.toFixed(3);dofEl.style.display=dv>.01?'block':'none';}
  shot(u,time);
  grainTick(now);
  dawnEl.style.opacity=(u>600&&u<820)?.5*Math.min(ss(range(u,610,680)),1-ss(range(u,740,820))):0;
  pollenTick(vu,time,vel,dt);
  scrimEl.style.opacity=(u>660&&u<1430)?Math.min(ss(range(u,660,720)),1-ss(range(u,1400,1430))):0;
  hud(u);
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
})();
