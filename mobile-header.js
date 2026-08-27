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

  const update = () => {
    const y = window.scrollY || window.pageYOffset || 0;
    const menuOpen = nav?.classList.contains('open') || menu?.getAttribute('aria-expanded') === 'true';
    const delta = y - lastY;

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

  menu?.addEventListener('click', normalizeOpenMenu);

  nav?.addEventListener('click', event => {
    if (!event.target.closest('a')) return;
    header.classList.remove('header-hidden');
    nav.scrollTop = 0;
    upDistance = 0;
    downDistance = 0;
    lastY = window.scrollY;
  });

  mobile.addEventListener?.('change', () => {
    header.classList.remove('header-hidden');
    if (nav) nav.scrollTop = 0;
    upDistance = 0;
    downDistance = 0;
    lastY = window.scrollY;
  });

  update();
})();
