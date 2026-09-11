/* Mobile header behavior: keep navigation available without covering content. */
(() => {
  const header = document.querySelector('[data-header]');
  const nav = document.querySelector('[data-nav]');
  const menu = document.querySelector('[data-menu]');
  if (!header) return;

  const mobile = window.matchMedia('(max-width: 820px)');
  let lastY = window.scrollY;
  let upDistance = 0;
  let downDistance = 0;
  let ticking = false;

  const syncCompactState = () => {
    const y = window.scrollY || window.pageYOffset || 0;
    header.classList.toggle('scrolled', y > 20);
  };

  const update = () => {
    const y = window.scrollY || window.pageYOffset || 0;
    const menuOpen = nav?.classList.contains('open') || menu?.getAttribute('aria-expanded') === 'true';
    const delta = y - lastY;

    syncCompactState();

    if (!mobile.matches || menuOpen || y <= 24) {
      header.classList.remove('header-hidden');
      upDistance = 0;
      downDistance = 0;
    } else if (delta > 0) {
      downDistance += delta;
      upDistance = 0;
      if (y > 140 && downDistance >= 26) header.classList.add('header-hidden');
    } else if (delta < 0) {
      upDistance += -delta;
      downDistance = 0;
      /* Do not pop the large navigation back in for tiny corrective scrolls. */
      if (upDistance >= 84) {
        header.classList.remove('header-hidden');
        upDistance = 0;
      }
    }

    lastY = y;
    ticking = false;
  };

  const scheduleUpdate = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(update);
  };

  const resyncAfterBrowserRestore = () => {
    requestAnimationFrame(() => {
      syncCompactState();
      requestAnimationFrame(() => {
        syncCompactState();
        lastY = window.scrollY || window.pageYOffset || 0;
      });
    });
  };

  const normalizeOpenMenu = () => {
    if (!nav || !menu) return;
    const opening = nav.classList.contains('open') || menu.getAttribute('aria-expanded') === 'true';
    if (!opening) return;
    header.classList.remove('header-hidden');
    upDistance = 0;
    downDistance = 0;
    nav.scrollTop = 0;
    requestAnimationFrame(() => {
      nav.scrollTop = 0;
      requestAnimationFrame(() => { nav.scrollTop = 0; });
    });
    lastY = window.scrollY;
  };

  window.addEventListener('scroll', scheduleUpdate, { passive: true });
  window.addEventListener('resize', scheduleUpdate, { passive: true });
  window.addEventListener('orientationchange', scheduleUpdate, { passive: true });
  window.addEventListener('pageshow', resyncAfterBrowserRestore, { passive: true });
  window.addEventListener('load', resyncAfterBrowserRestore, { passive: true });
  window.addEventListener('hashchange', resyncAfterBrowserRestore, { passive: true });

  menu?.addEventListener('click', normalizeOpenMenu);

  nav?.addEventListener('click', event => {
    if (!event.target.closest('a')) return;
    header.classList.remove('header-hidden');
    nav.scrollTop = 0;
    upDistance = 0;
    downDistance = 0;
    lastY = window.scrollY;
    requestAnimationFrame(syncCompactState);
  });

  mobile.addEventListener?.('change', () => {
    header.classList.remove('header-hidden');
    if (nav) nav.scrollTop = 0;
    upDistance = 0;
    downDistance = 0;
    lastY = window.scrollY;
    syncCompactState();
  });

  update();
  resyncAfterBrowserRestore();
  setTimeout(syncCompactState, 180);
  setTimeout(syncCompactState, 520);
})();

/* Premium scroll-to-top: glass squircle, bronze progress rim and kinetic arrow glide. */
(() => {
  const button = document.createElement('button');
  const surface = document.createElement('span');
  const iconWrap = document.createElement('span');
  const label = document.createElement('span');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const compact = window.matchMedia('(max-width: 820px)');
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');

  const makeArrow = accent => {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('width', '22');
    svg.setAttribute('height', '22');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('focusable', 'false');
    svg.style.cssText = [
      'position:absolute',
      'inset:1px',
      'display:block',
      'overflow:visible',
      `color:${accent}`,
      'pointer-events:none'
    ].join(';');
    path.setAttribute('d', 'M7.5 10.5 12 6l4.5 4.5M12 6v12');
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', 'currentColor');
    path.setAttribute('stroke-width', '1.65');
    path.setAttribute('stroke-linecap', 'round');
    path.setAttribute('stroke-linejoin', 'round');
    path.setAttribute('vector-effect', 'non-scaling-stroke');
    svg.appendChild(path);
    return { svg, path };
  };

  const primary = makeArrow('#f4f0e7');
  const incoming = makeArrow('#d8c7aa');
  incoming.svg.style.opacity = '0';
  incoming.svg.style.transform = 'translateY(16px)';

  button.type = 'button';
  button.className = 'back-to-top';
  button.setAttribute('aria-label', 'Nach oben scrollen');
  button.setAttribute('title', 'Nach oben');
  button.style.cssText = [
    'position:fixed',
    'right:calc(18px + env(safe-area-inset-right,0px))',
    'bottom:calc(18px + env(safe-area-inset-bottom,0px))',
    'z-index:250',
    'width:52px',
    'height:52px',
    'display:block',
    'padding:1px',
    'border:0',
    'border-radius:18px',
    'background:conic-gradient(from -90deg,#b39167 0deg,rgba(244,240,231,.20) 0deg)',
    'box-shadow:0 12px 34px rgba(7,24,17,.20)',
    'cursor:pointer',
    'opacity:0',
    'visibility:hidden',
    'pointer-events:none',
    'transform:translateY(12px) scale(.94)',
    'transition:width .28s cubic-bezier(.2,.8,.2,1),opacity .22s ease,transform .24s cubic-bezier(.2,.8,.2,1),visibility .22s ease,box-shadow .22s ease',
    'touch-action:manipulation',
    '-webkit-tap-highlight-color:transparent',
    'overflow:hidden'
  ].join(';');

  surface.style.cssText = [
    'box-sizing:border-box',
    'width:100%',
    'height:100%',
    'display:flex',
    'align-items:center',
    'justify-content:flex-start',
    'gap:8px',
    'padding:0 13px',
    'border-radius:17px',
    'background:linear-gradient(145deg,rgba(31,68,54,.96),rgba(16,43,34,.97))',
    'color:#f4f0e7',
    'box-shadow:inset 0 1px 0 rgba(255,255,255,.16),inset 0 -1px 0 rgba(0,0,0,.14)',
    'backdrop-filter:blur(16px) saturate(1.08)',
    '-webkit-backdrop-filter:blur(16px) saturate(1.08)',
    'overflow:hidden'
  ].join(';');

  iconWrap.style.cssText = [
    'position:relative',
    'flex:0 0 24px',
    'width:24px',
    'height:24px',
    'display:block',
    'overflow:hidden',
    'transition:transform .25s cubic-bezier(.2,.8,.2,1)'
  ].join(';');
  iconWrap.append(primary.svg, incoming.svg);

  label.textContent = 'Nach oben';
  label.setAttribute('aria-hidden', 'true');
  label.style.cssText = [
    'display:block',
    'max-width:0',
    'opacity:0',
    'overflow:hidden',
    'white-space:nowrap',
    'font:600 11px/1 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif',
    'letter-spacing:.055em',
    'text-transform:uppercase',
    'transform:translateX(-5px)',
    'transition:max-width .28s cubic-bezier(.2,.8,.2,1),opacity .18s ease,transform .25s ease'
  ].join(';');

  surface.append(iconWrap, label);
  button.appendChild(surface);
  document.body.appendChild(button);

  let glideSerial = 0;
  let wasVisible = false;

  const resetArrows = () => {
    primary.svg.style.opacity = '1';
    primary.svg.style.transform = 'translateY(0)';
    incoming.svg.style.opacity = '0';
    incoming.svg.style.transform = 'translateY(16px)';
  };

  const animateArrowGlide = (distance = 16, duration = 340) => {
    if (reducedMotion.matches || typeof primary.svg.animate !== 'function') return;
    const serial = ++glideSerial;
    primary.svg.getAnimations().forEach(animation => animation.cancel());
    incoming.svg.getAnimations().forEach(animation => animation.cancel());
    resetArrows();

    const outgoing = primary.svg.animate(
      [
        { transform: 'translateY(0)', opacity: 1 },
        { transform: `translateY(-${distance}px)`, opacity: 0 }
      ],
      { duration, easing: 'cubic-bezier(.22,.78,.22,1)', fill: 'forwards' }
    );
    const arriving = incoming.svg.animate(
      [
        { transform: `translateY(${distance}px)`, opacity: 0 },
        { transform: 'translateY(0)', opacity: 1 }
      ],
      { duration, easing: 'cubic-bezier(.22,.78,.22,1)', fill: 'forwards' }
    );

    Promise.allSettled([outgoing.finished, arriving.finished]).then(() => {
      if (serial === glideSerial) resetArrows();
    });
  };

  const animateArrowReveal = () => {
    if (reducedMotion.matches || typeof primary.path.animate !== 'function') return;
    const length = primary.path.getTotalLength();
    primary.path.animate(
      [
        { strokeDasharray: `${length}`, strokeDashoffset: `${length}`, opacity: .35 },
        { strokeDasharray: `${length}`, strokeDashoffset: '0', opacity: 1 }
      ],
      { duration: 460, easing: 'cubic-bezier(.2,.8,.2,1)' }
    );
    iconWrap.animate(
      [
        { transform: 'translateY(5px)', opacity: .62 },
        { transform: 'translateY(0)', opacity: 1 }
      ],
      { duration: 420, easing: 'cubic-bezier(.2,.8,.2,1)' }
    );
  };

  const applyMotionPreference = () => {
    const reduce = reducedMotion.matches;
    button.style.transition = reduce
      ? 'opacity .12s linear,visibility .12s linear'
      : 'width .28s cubic-bezier(.2,.8,.2,1),opacity .22s ease,transform .24s cubic-bezier(.2,.8,.2,1),visibility .22s ease,box-shadow .22s ease';
    label.style.transition = reduce
      ? 'none'
      : 'max-width .28s cubic-bezier(.2,.8,.2,1),opacity .18s ease,transform .25s ease';
    iconWrap.style.transition = reduce ? 'none' : 'transform .25s cubic-bezier(.2,.8,.2,1)';
    if (reduce) {
      glideSerial += 1;
      primary.svg.getAnimations().forEach(animation => animation.cancel());
      incoming.svg.getAnimations().forEach(animation => animation.cancel());
      primary.path.getAnimations().forEach(animation => animation.cancel());
      iconWrap.getAnimations().forEach(animation => animation.cancel());
      resetArrows();
    }
  };

  const setExpanded = expanded => {
    if (compact.matches || !finePointer.matches) expanded = false;
    button.style.width = expanded ? '132px' : '52px';
    button.style.boxShadow = expanded
      ? '0 16px 42px rgba(7,24,17,.26),0 2px 8px rgba(7,24,17,.10)'
      : '0 12px 34px rgba(7,24,17,.20)';
    iconWrap.style.transform = expanded && !reducedMotion.matches ? 'translateY(-2px)' : 'translateY(0)';
    label.style.maxWidth = expanded ? '72px' : '0';
    label.style.opacity = expanded ? '1' : '0';
    label.style.transform = expanded && !reducedMotion.matches ? 'translateX(0)' : expanded ? 'translateX(0)' : 'translateX(-5px)';
  };

  const sync = () => {
    const y = window.scrollY || window.pageYOffset || 0;
    const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    const progress = Math.min(1, Math.max(0, y / max));
    const degrees = Math.round(progress * 360);
    const visible = y > 560;

    button.style.background = `conic-gradient(from -90deg,#b39167 ${degrees}deg,rgba(244,240,231,.20) ${degrees}deg)`;
    button.style.opacity = visible ? '1' : '0';
    button.style.visibility = visible ? 'visible' : 'hidden';
    button.style.pointerEvents = visible ? 'auto' : 'none';
    button.style.transform = reducedMotion.matches
      ? 'none'
      : visible ? 'translateY(0) scale(1)' : 'translateY(12px) scale(.94)';

    if (visible && !wasVisible) requestAnimationFrame(animateArrowReveal);
    wasVisible = visible;
  };

  button.addEventListener('click', () => {
    setExpanded(false);
    window.scrollTo({ top: 0, left: 0, behavior: reducedMotion.matches ? 'auto' : 'smooth' });
  });
  button.addEventListener('pointerenter', () => {
    if (!finePointer.matches) return;
    setExpanded(true);
    animateArrowGlide();
  });
  button.addEventListener('pointerleave', () => setExpanded(false));
  button.addEventListener('pointerdown', event => {
    if (event.pointerType !== 'mouse') animateArrowGlide(18, 300);
  });
  button.addEventListener('focus', () => {
    setExpanded(true);
    animateArrowGlide();
    button.style.outline = '3px solid rgba(179,145,103,.58)';
    button.style.outlineOffset = '4px';
  });
  button.addEventListener('blur', () => {
    setExpanded(false);
    button.style.outline = 'none';
  });

  compact.addEventListener?.('change', () => setExpanded(false));
  finePointer.addEventListener?.('change', () => setExpanded(false));
  reducedMotion.addEventListener?.('change', () => {
    applyMotionPreference();
    sync();
  });

  let scheduled = false;
  const schedule = () => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => {
      sync();
      scheduled = false;
    });
  };

  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('pageshow', schedule, { passive: true });
  window.addEventListener('resize', schedule, { passive: true });
  window.addEventListener('orientationchange', schedule, { passive: true });
  applyMotionPreference();
  sync();
})();
