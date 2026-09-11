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

/* Modern, accessible scroll-to-top control. */
(() => {
  const button = document.createElement('button');
  const arrow = document.createElement('span');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  button.type = 'button';
  button.className = 'back-to-top';
  button.setAttribute('aria-label', 'Nach oben scrollen');
  button.setAttribute('title', 'Nach oben');
  button.style.cssText = [
    'position:fixed',
    'right:calc(20px + env(safe-area-inset-right,0px))',
    'bottom:calc(20px + env(safe-area-inset-bottom,0px))',
    'z-index:250',
    'width:48px',
    'height:48px',
    'display:grid',
    'place-items:center',
    'padding:0',
    'border:1px solid rgba(244,240,231,.42)',
    'border-radius:50%',
    'background:rgba(23,56,45,.94)',
    'color:#f4f0e7',
    'box-shadow:0 10px 28px rgba(7,24,17,.20),inset 0 1px 0 rgba(255,255,255,.14)',
    'backdrop-filter:blur(10px)',
    '-webkit-backdrop-filter:blur(10px)',
    'cursor:pointer',
    'opacity:0',
    'visibility:hidden',
    'pointer-events:none',
    'transform:translateY(10px) scale(.94)',
    'transition:opacity .22s ease,transform .22s ease,visibility .22s ease,background .18s ease,box-shadow .18s ease',
    'touch-action:manipulation',
    '-webkit-tap-highlight-color:transparent'
  ].join(';');

  arrow.textContent = '↑';
  arrow.setAttribute('aria-hidden', 'true');
  arrow.style.cssText = 'display:block;font:300 24px/1 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;transform:translateY(-1px)';
  button.appendChild(arrow);
  document.body.appendChild(button);

  const setVisible = () => {
    const visible = (window.scrollY || window.pageYOffset || 0) > 560;
    button.style.opacity = visible ? '1' : '0';
    button.style.visibility = visible ? 'visible' : 'hidden';
    button.style.pointerEvents = visible ? 'auto' : 'none';
    button.style.transform = visible ? 'translateY(0) scale(1)' : 'translateY(10px) scale(.94)';
  };

  button.addEventListener('click', () => {
    window.scrollTo({ top: 0, left: 0, behavior: reducedMotion.matches ? 'auto' : 'smooth' });
  });
  button.addEventListener('pointerenter', () => {
    button.style.background = 'rgba(23,48,39,.99)';
    button.style.boxShadow = '0 13px 32px rgba(7,24,17,.25),inset 0 1px 0 rgba(255,255,255,.18)';
    button.style.transform = 'translateY(-2px) scale(1.02)';
  });
  button.addEventListener('pointerleave', setVisible);
  button.addEventListener('focus', () => {
    button.style.outline = '3px solid rgba(179,145,103,.58)';
    button.style.outlineOffset = '3px';
  });
  button.addEventListener('blur', () => {
    button.style.outline = 'none';
  });

  let scheduled = false;
  const schedule = () => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => {
      setVisible();
      scheduled = false;
    });
  };

  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('pageshow', schedule, { passive: true });
  window.addEventListener('resize', schedule, { passive: true });
  setVisible();
})();
