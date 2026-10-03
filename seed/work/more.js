/* "More projects" at the end of every case study: the other two projects, with the same words as the homepage cards.
   Used by all three case studies; the page names itself with data-current on the script tag. */
(()=>{
  const P=[
    {id:'healthfab',n:'01',name:'Healthfab',meta:'Rebranding Case Study · Brand Strategy & Identity Design',line:'Same Product, New Story',href:'healthfab.html'},
    {id:'discount-discovery',n:'02',name:'Discount Discovery App',meta:'Shopify App · Case Study',line:'Every Discount, One Tap Away',href:'discount-discovery.html'},
    {id:'beauty-by-bie',n:'03',name:'Beauty by Bie',meta:'CRO Case Study · UX/UI Designer · CRO Strategy & Redesign',line:'Designing for Better Conversions',href:'beauty-by-bie.html'}];
  const me=(document.currentScript&&document.currentScript.dataset.current)||window.__moreCurrent;
  // a bundled page (Beauty by Bie) runs inside a blob: frame of its own page: resolve paths and talk to the viewer from there
  let H=window,BASE='';
  try{if(location.protocol==='blob:'&&window.parent!==window){H=window.parent;BASE=new URL('.',H.location.href).href;}}catch(e){}
  const up=H.parent!==H?H.parent:null, TGT=H===window?'':' target="_parent"';
  const self=P.find(p=>p.id===me);
  // inside the portfolio's viewer, keep its title in step with the page
  if(self&&up)up.postMessage({type:'case-title',title:self.name},'*');

  const css=`
  .more,.more *{box-sizing:border-box}
  .more{position:relative;z-index:2;margin:0;font-family:"Plus Jakarta Sans",system-ui,-apple-system,"Segoe UI",sans-serif;color:#141414;background:#fff;
    padding-block:clamp(56px,7vw,104px) clamp(64px,8vw,120px);border-top:1px solid #ececec}
  .more .in{width:min(1120px,100%);margin:0 auto;padding-inline:16px}
  @media (min-width:1152px){.more .in{padding-inline:0}}
  .more .top{display:flex;align-items:end;justify-content:space-between;gap:16px;flex-wrap:wrap}
  .more h2{font-weight:400;font-size:clamp(26px,2.7vw,40px);line-height:1.15;letter-spacing:-.01em;margin:0}
  .more .all{font-size:15px;color:#141414;text-decoration:none;border-bottom:1px solid currentColor;padding-bottom:2px}
  .more .grid{display:grid;grid-template-columns:1fr 1fr;gap:clamp(16px,2.4vw,32px);margin-top:clamp(24px,3vw,40px)}
  @media (max-width:640px){.more .grid{grid-template-columns:1fr}}
  .more a.card{display:grid;gap:14px;color:inherit;text-decoration:none;outline:none}
  .more .th{border-radius:clamp(14px,1.6vw,22px);overflow:hidden;aspect-ratio:16/9;background:#eee;
    transition:transform .7s cubic-bezier(.22,1,.36,1),box-shadow .7s cubic-bezier(.22,1,.36,1)}
  .more .th img{display:block;width:100%;height:100%;object-fit:cover;transition:transform 1s cubic-bezier(.22,1,.36,1)}
  .more .tx{display:grid;grid-template-columns:auto 1fr;gap:4px 14px;align-content:start}
  .more .tx > :not(.n){grid-column:2}
  .more .n{font-size:12px;font-weight:600;color:#9a5a33;grid-row:span 3;padding-top:5px}
  .more h3{font-weight:500;font-size:clamp(18px,1.6vw,22px);line-height:1.25;margin:0;display:flex;gap:8px;align-items:center}
  .more h3 i{font-style:normal;display:inline-block;transition:transform .45s cubic-bezier(.22,1,.36,1)}
  .more .mm{font-size:14px;color:#6f6f6f}
  .more .ln{font-size:15px}
  .more a.card:hover .th,.more a.card:focus-visible .th{transform:translateY(-6px);box-shadow:0 30px 50px -28px rgba(20,20,40,.45)}
  .more a.card:hover .th img,.more a.card:focus-visible .th img{transform:scale(1.04)}
  .more a.card:hover h3 i,.more a.card:focus-visible h3 i{transform:translate(3px,-3px)}
  .more a.card:focus-visible .th{outline:2px solid #141414;outline-offset:4px}
  /* cards are always visible; the entrance only plays where the browser can watch them come into view */
  .more .card.pre{opacity:0;transform:translateY(30px)}
  .more .card{transition:opacity .9s cubic-bezier(.22,1,.36,1),transform 1s cubic-bezier(.22,1,.36,1)}
  .more .card:nth-child(2){transition-delay:.12s}
  @media (prefers-reduced-motion:reduce){.more .card{transition:none}.more a.card:hover .th,.more a.card:hover .th img{transform:none}}`;

  function build(){
    if(document.querySelector('.more'))return true;
    const host=document.querySelector('main');if(!host)return false;
    const st=document.createElement('style');st.textContent=css;document.head.appendChild(st);
    const sec=document.createElement('section');sec.className='more';sec.setAttribute('aria-labelledby','moreTitle');
    const others=P.filter(p=>p.id!==me);
    sec.innerHTML=`<div class="in"><div class="top"><h2 id="moreTitle">More projects</h2><a class="all" href="${BASE}../index.html"${TGT} data-home>Back to all work</a></div><div class="grid">${
      others.map(p=>`<a class="card" href="${BASE}${p.href}"${TGT}><span class="th"><img src="${BASE}thumbs/${p.id}.webp" alt="" width="960" height="540"></span><span class="tx"><span class="n">${p.n}</span><h3>${p.name} <i aria-hidden="true">↗</i></h3><span class="mm">${p.meta.replace(/&/g,'&amp;')}</span><span class="ln">${p.line}</span></span></a>`).join('')}</div></div>`;
    host.after(sec);
    // in the viewer, "Back to all work" closes it; on its own it goes to the portfolio
    sec.querySelector('[data-home]').addEventListener('click',e=>{if(up){e.preventDefault();up.postMessage({type:'close-case'},'*');}});
    const cards=[...sec.querySelectorAll('.card')];
    try{if('IntersectionObserver' in window&&!matchMedia('(prefers-reduced-motion: reduce)').matches&&sec.getBoundingClientRect().top>innerHeight){
      cards.forEach(c=>c.classList.add('pre'));
      const io=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){x.target.classList.remove('pre');io.unobserve(x.target);}}),{threshold:.1});
      cards.forEach(c=>io.observe(c));
      setTimeout(()=>cards.forEach(c=>c.classList.remove('pre')),8000);   // never leave them hidden
    }}catch(e){cards.forEach(c=>c.classList.remove('pre'));}
    return true;
  }
  if(!build()){const t=setInterval(()=>{if(build())clearInterval(t);},60);setTimeout(()=>clearInterval(t),15000);}
})();
