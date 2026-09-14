/* Final homepage interaction pass: deterministic active navigation state. */
(()=>{
  const nav=document.querySelector('[data-nav]');
  if(!nav)return;
  const links=[...nav.querySelectorAll('a[href^="#"]')];
  const pairs=links.map(link=>{
    const id=link.getAttribute('href')?.slice(1);
    return {link,section:id?document.getElementById(id):null};
  }).filter(item=>item.section);
  if(!pairs.length)return;

  let ticking=false;
  function setActive(){
    ticking=false;
    const marker=Math.min(Math.max(window.innerHeight*.28,150),250);
    let current=null;
    for(const item of pairs){
      const rect=item.section.getBoundingClientRect();
      if(rect.top<=marker)current=item;
      else break;
    }
    if(window.innerHeight+window.scrollY>=document.documentElement.scrollHeight-4){
      current=pairs[pairs.length-1];
    }
    for(const item of pairs){
      const active=item===current;
      item.link.classList.toggle('active',active);
      if(active)item.link.setAttribute('aria-current','location');
      else item.link.removeAttribute('aria-current');
    }
  }
  function requestUpdate(){
    if(ticking)return;
    ticking=true;
    requestAnimationFrame(setActive);
  }
  window.addEventListener('scroll',requestUpdate,{passive:true});
  window.addEventListener('resize',requestUpdate,{passive:true});
  window.addEventListener('hashchange',requestUpdate);
  window.addEventListener('load',requestUpdate,{once:true});
  requestUpdate();
})();
