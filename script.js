const header=document.querySelector('[data-header]');
const menu=document.querySelector('[data-menu]');
const nav=document.querySelector('[data-nav]');
const year=document.querySelector('[data-year]');
if(year) year.textContent=new Date().getFullYear();
const imprintLink=document.querySelector('.footer a[href="#impressum"]');
const privacyLink=document.querySelector('.footer a[href="#datenschutz"]');
if(imprintLink) imprintLink.href='impressum.html';
if(privacyLink) privacyLink.href='datenschutz.html';

let raf=null;
function onScroll(){
  if(raf!==null)return;
  raf=requestAnimationFrame(()=>{
    header?.classList.toggle('scrolled',window.scrollY>20);
    raf=null;
  });
}
window.addEventListener('scroll',onScroll,{passive:true});
onScroll();

function closeNav(returnFocus=false){
  if(!nav||!menu)return;
  nav.classList.remove('open');
  document.body.classList.remove('nav-open');
  menu.setAttribute('aria-expanded','false');
  if(returnFocus)menu.focus();
}
menu?.addEventListener('click',()=>{
  const open=!nav.classList.contains('open');
  if(!open){closeNav();return;}
  nav.classList.add('open');
  document.body.classList.add('nav-open');
  menu.setAttribute('aria-expanded','true');
});
nav?.addEventListener('click',e=>{if(e.target.closest('a'))closeNav();});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav?.classList.contains('open'))closeNav(true);});

const revealEls=[...document.querySelectorAll('[data-reveal]')];
if('IntersectionObserver'in window){
  const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{
    if(entry.isIntersecting){
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  }),{threshold:.1,rootMargin:'0px 0px -30px'});
  revealEls.forEach(el=>observer.observe(el));
}else revealEls.forEach(el=>el.classList.add('visible'));

if('IntersectionObserver'in window&&nav){
  const links=[...nav.querySelectorAll('a[href^="#"]')];
  const sections=document.querySelectorAll('main section[id]');
  const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{
    if(!entry.isIntersecting)return;
    links.forEach(link=>{
      const active=link.getAttribute('href')===`#${entry.target.id}`;
      link.classList.toggle('active',active);
      active?link.setAttribute('aria-current','location'):link.removeAttribute('aria-current');
    });
  }),{rootMargin:'-25% 0px -65%'});
  sections.forEach(s=>observer.observe(s));
}

function meta(item){
  const p=document.createElement('p');
  p.className='news-meta';
  [item.category,item.meta].filter(Boolean).forEach(v=>{
    const s=document.createElement('span');
    s.textContent=v;
    p.appendChild(s);
  });
  return p;
}

function newsLink(item){
  if(!item.link||!item.linkText)return null;
  const a=document.createElement('a');
  a.className='news-link';
  a.href=item.link;
  a.textContent=item.linkText;
  return a;
}

let lightbox=null;
let lightboxImage=null;
let lightboxCaption=null;
let lightboxClose=null;
let lightboxReturnFocus=null;

function ensureNewsLightbox(){
  if(lightbox)return;
  lightbox=document.createElement('div');
  lightbox.className='news-lightbox';
  lightbox.hidden=true;
  lightbox.setAttribute('role','dialog');
  lightbox.setAttribute('aria-modal','true');
  lightbox.setAttribute('aria-label','Vergrößerte Bildansicht');

  const inner=document.createElement('div');
  inner.className='news-lightbox-inner';

  lightboxImage=document.createElement('img');
  lightboxImage.alt='';

  lightboxClose=document.createElement('button');
  lightboxClose.type='button';
  lightboxClose.className='news-lightbox-close';
  lightboxClose.setAttribute('aria-label','Großansicht schließen');
  lightboxClose.textContent='×';

  lightboxCaption=document.createElement('p');
  lightboxCaption.className='news-lightbox-caption';

  inner.appendChild(lightboxImage);
  lightbox.append(inner,lightboxClose,lightboxCaption);
  document.body.appendChild(lightbox);

  lightboxClose.addEventListener('click',closeNewsLightbox);
  lightbox.addEventListener('click',e=>{if(e.target===lightbox)closeNewsLightbox();});
  document.addEventListener('keydown',e=>{
    if(e.key==='Escape'&&lightbox&&!lightbox.hidden)closeNewsLightbox();
  });
}

function openNewsLightbox(item,trigger){
  ensureNewsLightbox();
  lightboxReturnFocus=trigger||document.activeElement;
  lightboxImage.src=item.zoomImage||item.image;
  lightboxImage.alt=item.alt||item.title||'Foto der Reitanlage Eichhorn-Nels';
  lightboxCaption.textContent=item.title||item.alt||'Reitanlage Eichhorn-Nels';
  lightbox.hidden=false;
  document.body.classList.add('news-lightbox-open');
  requestAnimationFrame(()=>lightboxClose.focus());
}

function closeNewsLightbox(){
  if(!lightbox||lightbox.hidden)return;
  lightbox.hidden=true;
  lightboxImage.removeAttribute('src');
  document.body.classList.remove('news-lightbox-open');
  lightboxReturnFocus?.focus?.();
  lightboxReturnFocus=null;
}

function photoCaption(img){
  const figure=img.closest('figure');
  const figcaption=figure?.querySelector(':scope > figcaption');
  return figcaption?.textContent?.trim()||img.alt?.trim()||'Reitanlage Eichhorn-Nels';
}

function openPhotoLightbox(img){
  openNewsLightbox({
    image:img.dataset.zoomSrc||img.currentSrc||img.src,
    alt:img.alt||'Foto der Reitanlage Eichhorn-Nels',
    title:photoCaption(img)
  },img);
}

function initPhotoZoom(root=document){
  root.querySelectorAll('main img').forEach(img=>{
    if(img.dataset.photoZoomReady==='true')return;
    if(img.closest('.news-media-button'))return;
    if(img.closest('a,button'))return;
    if(img.hasAttribute('data-no-zoom'))return;

    img.dataset.photoZoomReady='true';
    img.dataset.photoZoom='true';
    img.tabIndex=0;
    img.setAttribute('role','button');
    img.setAttribute('aria-label',`${img.alt||'Foto'} groß ansehen`);
    img.title='Bild vergrößern';
    img.addEventListener('click',()=>openPhotoLightbox(img));
    img.addEventListener('keydown',e=>{
      if(e.key==='Enter'||e.key===' '){
        e.preventDefault();
        openPhotoLightbox(img);
      }
    });
  });
}

function createNewsMedia(item,featured){
  const zoomable=item.imageZoom===true||item.imageFit==='contain';
  const wrap=document.createElement(zoomable?'button':'div');
  wrap.className=featured?'news-feature-image':'news-thumb';

  if(zoomable){
    wrap.type='button';
    wrap.classList.add('news-media-button');
    wrap.setAttribute('aria-label',`${item.title||'Flyer'} groß ansehen`);
  }
  if(item.imageFit==='contain')wrap.classList.add('is-contain');

  const img=document.createElement('img');
  img.src=featured?item.image:(item.thumbnailImage||item.image);
  img.alt=item.alt||'Aktuelles von der Reitanlage Eichhorn-Nels';
  img.loading='lazy';
  img.decoding='async';
  img.fetchPriority='low';
  img.style.setProperty('--image-fit',item.imageFit==='contain'?'contain':'cover');
  img.style.setProperty('--image-position',item.imagePosition||'50% 50%');
  img.style.setProperty('--image-position-mobile',item.imagePositionMobile||item.imagePosition||'50% 50%');
  wrap.appendChild(img);

  if(zoomable){
    const hint=document.createElement('span');
    hint.className='news-zoom-hint';
    hint.textContent=item.imageFit==='contain'?'Flyer groß ansehen':'Bild vergrößern';
    wrap.appendChild(hint);
    wrap.addEventListener('click',()=>openNewsLightbox(item,wrap));
  }
  return wrap;
}

function newsItem(item,featured=false){
  const article=document.createElement('article');
  article.dataset.reveal='';
  if(featured)article.className='news-feature';

  const media=createNewsMedia(item,featured);
  const copy=document.createElement('div');
  copy.className=featured?'news-feature-copy':'news-copy';
  copy.appendChild(meta(item));

  const h=document.createElement('h3');
  h.textContent=item.title;
  copy.appendChild(h);

  const p=document.createElement('p');
  p.textContent=item.text;
  copy.appendChild(p);

  const a=newsLink(item);
  if(a)copy.appendChild(a);
  article.append(media,copy);
  return article;
}

async function loadNews(){
  const host=document.querySelector('[data-news-content]');
  if(!host)return;
  try{
    const response=await fetch('aktuelles.json',{cache:'no-store'});
    if(!response.ok)throw new Error(response.status);
    const data=await response.json();
    const items=(data.items||[]).filter(i=>i?.title&&i?.text);
    if(!items.length){
      host.innerHTML='<p>Aktuell sind keine Meldungen veröffentlicht. Für Termine und Verfügbarkeiten bitte direkt Kontakt aufnehmen.</p>';
      return;
    }

    const layout=document.createElement('div');
    layout.className='news-layout';
    layout.appendChild(newsItem(items[0],true));

    if(items.length>1){
      const list=document.createElement('div');
      list.className='news-list';
      items.slice(1).forEach(i=>list.appendChild(newsItem(i)));
      layout.appendChild(list);
    }
    host.replaceChildren(layout);

    const updated=document.querySelector('[data-news-updated]');
    if(updated&&data.updated){
      const d=new Date(`${data.updated}T12:00:00`);
      if(!Number.isNaN(d.getTime()))updated.textContent=`Redaktionell aktualisiert am ${d.toLocaleDateString('de-DE')}`;
    }
    host.querySelectorAll('[data-reveal]').forEach(el=>el.classList.add('visible'));
    initPhotoZoom(host);
  }catch(err){
    console.error('Aktuelles konnte nicht geladen werden',err);
    host.innerHTML='<p>Die aktuellen Meldungen konnten nicht geladen werden. Termine bitte direkt telefonisch oder per WhatsApp erfragen.</p>';
  }
}

initPhotoZoom();
loadNews();
