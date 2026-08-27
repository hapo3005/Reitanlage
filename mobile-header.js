/* Mobile header behavior: keep navigation available without covering content. */
(() => {
  const header = document.querySelector('[data-header]');
  const nav = document.querySelector('[data-nav]');
  const menu = document.querySelector('[data-menu]');
  if (!header) return;

  const mobile = window.matchMedia('(max-width: 820px)');
  let lastY = window.scrollY;
  let ticking = false;

  const update = () => {
    const y = window.scrollY || window.pageYOffset || 0;
    const menuOpen = nav?.classList.contains('open') || menu?.getAttribute('aria-expanded') === 'true';
    const delta = y - lastY;

    if (!mobile.matches || menuOpen || y <= 16) {
      header.classList.remove('header-hidden');
    } else if (delta > 10 && y > 140) {
      header.classList.add('header-hidden');
    } else if (delta < -10) {
      header.classList.remove('header-hidden');
    }

    lastY = y;
    ticking = false;
  };

  const scheduleUpdate = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(update);
  };

  window.addEventListener('scroll', scheduleUpdate, { passive: true });
  window.addEventListener('resize', scheduleUpdate, { passive: true });
  window.addEventListener('orientationchange', scheduleUpdate, { passive: true });

  menu?.addEventListener('click', () => {
    header.classList.remove('header-hidden');
    requestAnimationFrame(() => {
      const opening = nav?.classList.contains('open') || menu.getAttribute('aria-expanded') === 'true';
      if (opening && nav) nav.scrollTop = 0;
      lastY = window.scrollY;
    });
  });

  nav?.addEventListener('click', event => {
    if (!event.target.closest('a')) return;
    header.classList.remove('header-hidden');
    lastY = window.scrollY;
  });

  mobile.addEventListener?.('change', () => {
    header.classList.remove('header-hidden');
    if (nav) nav.scrollTop = 0;
    lastY = window.scrollY;
  });

  update();
})();
