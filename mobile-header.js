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
    const y = window.scrollY;
    const menuOpen = nav?.classList.contains('open') || menu?.getAttribute('aria-expanded') === 'true';

    if (!mobile.matches || menuOpen || y < 90) {
      header.classList.remove('header-hidden');
    } else if (y > lastY + 5) {
      header.classList.add('header-hidden');
    } else if (y < lastY - 5) {
      header.classList.remove('header-hidden');
    }

    lastY = y;
    ticking = false;
  };

  window.addEventListener('scroll', () => {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(update);
    }
  }, { passive: true });

  menu?.addEventListener('click', () => header.classList.remove('header-hidden'));
  mobile.addEventListener?.('change', () => {
    header.classList.remove('header-hidden');
    lastY = window.scrollY;
  });
})();
