/* Final keyboard/focus safeguards for dialog and mobile navigation. */
document.addEventListener('keydown',event=>{
  if(event.key!=='Tab')return;

  if(lightbox && !lightbox.hidden){
    event.preventDefault();
    lightboxClose?.focus();
    return;
  }

  if(nav?.classList.contains('open') && menu){
    const focusables=[menu,...nav.querySelectorAll('a[href]')].filter(el=>!el.hasAttribute('disabled'));
    if(!focusables.length)return;
    const first=focusables[0];
    const last=focusables[focusables.length-1];
    if(event.shiftKey && document.activeElement===first){
      event.preventDefault();
      last.focus();
    }else if(!event.shiftKey && document.activeElement===last){
      event.preventDefault();
      first.focus();
    }
  }
});

/* Discoverable kinetic cue for the scroll-to-top arrow, especially on touch.
   It runs as a short directional impulse with a long pause instead of a
   continuous bounce, and is fully disabled for reduced-motion users. */
window.addEventListener('load',()=>{
  const reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
  let timer=0;

  const findControl=()=>{
    const button=document.querySelector('.back-to-top');
    const surface=button?.firstElementChild;
    const iconWrap=surface?.firstElementChild;
    const arrow=iconWrap?.querySelector('svg');
    return {button,iconWrap,arrow};
  };

  const isVisible=button=>{
    if(!button || document.hidden)return false;
    const style=getComputedStyle(button);
    return style.visibility!=='hidden' && Number(style.opacity)>.5 && button.getBoundingClientRect().width>0;
  };

  const cue=()=>{
    const {button,iconWrap,arrow}=findControl();
    if(reducedMotion.matches || !isVisible(button) || !iconWrap || !arrow)return;
    if(button.matches(':hover,:focus-visible'))return;
    if(arrow.getAnimations().some(animation=>animation.playState==='running'))return;

    arrow.animate(
      [
        {transform:'translateY(0)',opacity:1,offset:0},
        {transform:'translateY(-13px)',opacity:0,offset:.38},
        {transform:'translateY(13px)',opacity:0,offset:.40},
        {transform:'translateY(0)',opacity:1,offset:1}
      ],
      {duration:720,easing:'cubic-bezier(.22,.78,.22,1)'}
    );
    iconWrap.animate(
      [
        {transform:'translateY(0)',offset:0},
        {transform:'translateY(-2px)',offset:.26},
        {transform:'translateY(0)',offset:1}
      ],
      {duration:720,easing:'cubic-bezier(.22,.78,.22,1)'}
    );
  };

  const schedule=()=>{
    clearTimeout(timer);
    timer=window.setTimeout(()=>{
      cue();
      schedule();
    },3600);
  };

  reducedMotion.addEventListener?.('change',()=>{
    const {iconWrap,arrow}=findControl();
    if(reducedMotion.matches){
      clearTimeout(timer);
      arrow?.getAnimations().forEach(animation=>animation.cancel());
      iconWrap?.getAnimations().forEach(animation=>animation.cancel());
    }else{
      schedule();
    }
  });

  document.addEventListener('visibilitychange',()=>{
    if(document.hidden){
      clearTimeout(timer);
    }else if(!reducedMotion.matches){
      schedule();
    }
  });

  if(!reducedMotion.matches){
    window.setTimeout(cue,900);
    schedule();
  }
});
