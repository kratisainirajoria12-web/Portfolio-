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

  // hero: the media eases in, then drifts slower than the page
  const media=document.querySelector('.hero video,.hero img');
  if(media){media.dataset.rv='';media.style.setProperty('--d','80ms');requestAnimationFrame(()=>requestAnimationFrame(()=>media.classList.add('in')));
    setTimeout(()=>{media.style.transition='none';
      const on=()=>{const y=Math.min(scrollY,800);media.style.transform=`translateY(${y*.25}px) scale(${1+y/4000})`;};
      addEventListener('scroll',on,{passive:true});on();},1300);}
})();
