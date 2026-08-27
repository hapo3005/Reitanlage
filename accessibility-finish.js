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
