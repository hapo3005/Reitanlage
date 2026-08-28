/* Reitanlage Eichhorn-Nels — mobile closing behavior, 2026-08-28.
   The closing chapter gets the full mobile viewport instead of being covered by the floating header. */
(() => {
  const body = document.body;
  const pricing = document.querySelector('#preise');
  const header = document.querySelector('[data-header]');
  if (!body || !pricing || !header) return;

  const mobile = window.matchMedia('(max-width: 820px)');
  let ticking = false;

  const sync = () => {
    if (!mobile.matches || body.classList.contains('journal-page')) {
      body.classList.remove('closing-zone');
      ticking = false;
      return;
    }

    const pricingTop = pricing.getBoundingClientRect().top;
    const closing = pricingTop <= 72;
    body.classList.toggle('closing-zone', closing);

    if (closing && !body.classList.contains('nav-open')) {
      header.classList.add('header-hidden');
    }

    ticking = false;
  };

  const schedule = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(sync);
  };

  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule, { passive: true });
  window.addEventListener('orientationchange', schedule, { passive: true });
  window.addEventListener('pageshow', schedule, { passive: true });
  window.addEventListener('load', schedule, { passive: true });
  window.addEventListener('hashchange', schedule, { passive: true });
  mobile.addEventListener?.('change', schedule);

  sync();
})();
