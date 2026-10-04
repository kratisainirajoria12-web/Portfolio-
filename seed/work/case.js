/* Motion for Krati's case studies, in the spirit of her CRO page: staggered reveals, a soft hero parallax,
   counting figures, and a close button that returns to the portfolio. */
(()=>{
  const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const root=document.documentElement;

  // close: inside the portfolio's viewer, ask it to close; opened on its own, go back to the portfolio
  const close=document.querySelector('.close');
  if(close)close.addEventListener('click',e=>{
    if(window.parent!==window){e.preventDefault();window.parent.postMessage({type:'close-case'},'*');}
  });
  addEventListener('keydown',e=>{if(e.key==='Escape'&&window.parent!==window)window.parent.postMessage({type:'close-case'},'*');});

  if(reduce)return;
  root.classList.add('js');

  // reveal: each block of the sheet, children staggered
  const groups=[document.querySelector('.head'),...document.querySelectorAll('.sheet section')].filter(Boolean);
  const targets=[];
  groups.forEach(g=>[...g.children].forEach((c,i)=>{c.dataset.rv='';c.style.setProperty('--d',Math.min(i,5)*90+'ms');targets.push(c);}));
  // grids and strips: their items come in one after another
  document.querySelectorAll('.grid,.strip').forEach(g=>[...g.children].forEach((c,i)=>{c.dataset.rv='';c.style.setProperty('--d',150+i*90+'ms');targets.push(c);}));
  const io=new IntersectionObserver(es=>es.forEach(e=>{if(!e.isIntersecting)return;e.target.classList.add('in');io.unobserve(e.target);
    e.target.querySelectorAll('[data-count]').forEach(countUp);}),{threshold:.12,rootMargin:'0px 0px -8% 0px'});
  targets.forEach(t=>io.observe(t));
  // anything above the fold shows straight away, in order
  requestAnimationFrame(()=>targets.forEach(t=>{if(t.getBoundingClientRect().top<innerHeight*.92){t.classList.add('in');io.unobserve(t);}}));

  // figures in the copy count up when they come into view
  function countUp(el){const to=parseFloat(el.dataset.count),dec=(el.dataset.count.split('.')[1]||'').length,t0=performance.now(),d=1400;
    const step=t=>{const k=Math.min(1,(t-t0)/d),v=to*(1-Math.pow(1-k,3));el.textContent=v.toFixed(dec);if(k<1)requestAnimationFrame(step);};
    el.textContent=(0).toFixed(dec);requestAnimationFrame(step);}

  // images: tilt toward the cursor, lift, and a light that follows it, clipped to the image's own shape
  document.querySelectorAll('.shot,.persona').forEach(card=>{
    const img=card.querySelector('img');if(!img)return;
    const sh=document.createElement('span');sh.className='sheen';sh.setAttribute('aria-hidden','true');
    const m=`url("${img.currentSrc||img.src}")`;sh.style.webkitMaskImage=m;sh.style.maskImage=m;card.appendChild(sh);
    card.addEventListener('pointermove',e=>{if(e.pointerType==='touch')return;const r=card.getBoundingClientRect(),x=(e.clientX-r.left)/r.width,y=(e.clientY-r.top)/r.height;
      const k=Math.min(1,520/r.width)*4;card.style.setProperty('--ry',((x-.5)*k).toFixed(2)+'deg');card.style.setProperty('--rx',((.5-y)*k).toFixed(2)+'deg');
      card.style.setProperty('--mx',(x*100).toFixed(1)+'%');card.style.setProperty('--my',(y*100).toFixed(1)+'%');card.classList.add('hov');});
    card.addEventListener('pointerleave',()=>{card.classList.remove('hov');card.style.setProperty('--rx','0deg');card.style.setProperty('--ry','0deg');});
  });

  // Discount Discovery hero: the headline rises word by word inside the frame, then "Create." types itself in
  const dda=document.querySelector('.hero.dda');
  if(dda){
    dda.querySelectorAll('.big .wd').forEach((w,i)=>w.style.setProperty('--d',300+i*90+'ms'));
    requestAnimationFrame(()=>requestAnimationFrame(()=>dda.classList.add('on')));
    const lts=[...dda.querySelectorAll('.create .lt')],caret=dda.querySelector('.caret');
    setTimeout(()=>{caret.style.opacity='1';lts.forEach((l,i)=>setTimeout(()=>{l.style.opacity='1';if(i===lts.length-1){caret.style.opacity='';caret.classList.add('blink');}},i*95));},1150);
    const copy=dda.querySelector('.copy');
    dda.addEventListener('pointermove',e=>{const r=dda.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;
      copy.style.transform=`translate(${(x*10).toFixed(1)}px,${(y*6).toFixed(1)}px)`;});
    dda.addEventListener('pointerleave',()=>copy.style.transform='');
  }

  // hero: the media eases in, then grows slightly as the sheet slides over it (anchored at the bottom, so no edge ever shows)
  const media=document.querySelector('.hero > video,.dda .frame');
  if(media){if(media.tagName==='VIDEO'){media.dataset.rv='';media.style.setProperty('--d','80ms');requestAnimationFrame(()=>requestAnimationFrame(()=>media.classList.add('in')));}
    media.style.transformOrigin='50% 100%';
    setTimeout(()=>{media.style.transition='none';
      const on=()=>{const y=Math.min(scrollY,800);media.style.transform=`scale(${(1+y/2500).toFixed(4)})`;};
      addEventListener('scroll',on,{passive:true});on();},1300);}
})();
