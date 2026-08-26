const heroViewportStyles=document.createElement('link');
heroViewportStyles.rel='stylesheet';
heroViewportStyles.href='hero-mobile.css?v=20260826-1';
document.head.appendChild(heroViewportStyles);
const heroVisual=document.querySelector('.hero-image img');
if(heroVisual){heroVisual.src='images/reitbeteiligung1.png';heroVisual.alt='Pferd im Abendlicht auf der Reitanlage Eichhorn-Nels';heroVisual.loading='eager';heroVisual.fetchPriority='high'}
const heroCaption=document.querySelector('.hero-image figcaption');
if(heroCaption)heroCaption.textContent='Minderlittgen · zwischen Stall, Pferd und Eifel.';
const header=document.querySelector('[data-header]');
const menu=document.querySelector('[data-menu]');
const nav=document.querySelector('[data-nav]');
const year=document.querySelector('[data-year]');
if(year) year.textContent=new Date().getFullYear();
let raf=null;
function onScroll(){if(raf!==null)return;raf=requestAnimationFrame(()=>{header?.classList.toggle('scrolled',window.scrollY>20);raf=null})}
window.addEventListener('scroll',onScroll,{passive:true});onScroll();
function closeNav(returnFocus=false){if(!nav||!menu)return;nav.classList.remove('open');document.body.classList.remove('nav-open');menu.setAttribute('aria-expanded','false');if(returnFocus)menu.focus()}
menu?.addEventListener('click',()=>{const open=!nav.classList.contains('open');if(!open){closeNav();return}nav.classList.add('open');document.body.classList.add('nav-open');menu.setAttribute('aria-expanded','true')});
nav?.addEventListener('click',e=>{if(e.target.closest('a'))closeNav()});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav?.classList.contains('open'))closeNav(true)});
const revealEls=[...document.querySelectorAll('[data-reveal]')];
if('IntersectionObserver'in window){const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('visible');observer.unobserve(entry.target)}}),{threshold:.1,rootMargin:'0px 0px -30px'});revealEls.forEach(el=>observer.observe(el))}else revealEls.forEach(el=>el.classList.add('visible'));
if('IntersectionObserver'in window&&nav){const links=[...nav.querySelectorAll('a[href^="#"]')];const sections=document.querySelectorAll('main section[id]');const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(!entry.isIntersecting)return;links.forEach(link=>{const active=link.getAttribute('href')===`#${entry.target.id}`;link.classList.toggle('active',active);active?link.setAttribute('aria-current','location'):link.removeAttribute('aria-current')})}),{rootMargin:'-25% 0px -65%'});sections.forEach(s=>observer.observe(s))}
function meta(item){const p=document.createElement('p');p.className='news-meta';[item.category,item.meta].filter(Boolean).forEach(v=>{const s=document.createElement('span');s.textContent=v;p.appendChild(s)});return p}
function newsLink(item){if(!item.link||!item.linkText)return null;const a=document.createElement('a');a.className='news-link';a.href=item.link;a.textContent=`${item.linkText} →`;return a}
function newsItem(item,featured=false){const article=document.createElement('article');article.dataset.reveal='';if(featured)article.className='news-feature';const wrap=document.createElement('div');wrap.className=featured?'news-feature-image':'news-thumb';if(item.imageFit==='contain')wrap.classList.add('is-contain');const img=document.createElement('img');img.src=item.image;img.alt=item.alt||'Aktuelles von der Reitanlage Eichhorn-Nels';img.loading='lazy';img.decoding='async';img.style.setProperty('--image-fit',item.imageFit==='contain'?'contain':'cover');img.style.setProperty('--image-position',item.imagePosition||'50% 50%');wrap.appendChild(img);const copy=document.createElement('div');copy.appendChild(meta(item));const h=document.createElement('h3');h.textContent=item.title;copy.appendChild(h);const p=document.createElement('p');p.textContent=item.text;copy.appendChild(p);const a=newsLink(item);if(a)copy.appendChild(a);article.append(wrap,copy);return article}
async function loadNews(){const host=document.querySelector('[data-news-content]');if(!host)return;try{const response=await fetch('aktuelles.json',{cache:'no-store'});if(!response.ok)throw new Error(response.status);const data=await response.json();const items=(data.items||[]).filter(i=>i?.title&&i?.text);if(!items.length){host.innerHTML='<p>Aktuell sind keine Meldungen veröffentlicht. Für Termine und Verfügbarkeiten bitte direkt Kontakt aufnehmen.</p>';return}const layout=document.createElement('div');layout.className='news-layout';layout.appendChild(newsItem(items[0],true));if(items.length>1){const list=document.createElement('div');list.className='news-list';items.slice(1).forEach(i=>list.appendChild(newsItem(i)));layout.appendChild(list)}host.replaceChildren(layout);const updated=document.querySelector('[data-news-updated]');if(updated&&data.updated){const d=new Date(`${data.updated}T12:00:00`);if(!Number.isNaN(d.getTime()))updated.textContent=`Redaktionell aktualisiert am ${d.toLocaleDateString('de-DE')}`}host.querySelectorAll('[data-reveal]').forEach(el=>el.classList.add('visible'))}catch(err){console.error('Aktuelles konnte nicht geladen werden',err);host.innerHTML='<p>Die aktuellen Meldungen konnten nicht geladen werden. Termine bitte direkt telefonisch oder per WhatsApp erfragen.</p>'}}
loadNews();