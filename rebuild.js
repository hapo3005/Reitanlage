const nav = document.querySelector('[data-nav]');
const toggle = document.querySelector('[data-nav-toggle]');

function closeNav(returnFocus = false) {
  if (!nav || !toggle) return;
  nav.classList.remove('open');
  document.body.classList.remove('nav-open');
  toggle.setAttribute('aria-expanded', 'false');
  if (returnFocus) toggle.focus();
}

if (nav && toggle) {
  toggle.addEventListener('click', () => {
    const open = !nav.classList.contains('open');
    if (!open) return closeNav();
    nav.classList.add('open');
    document.body.classList.add('nav-open');
    toggle.setAttribute('aria-expanded', 'true');
  });
  nav.addEventListener('click', e => { if (e.target.closest('a')) closeNav(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && nav.classList.contains('open')) closeNav(true); });
}

function setActiveNav() {
  if (!('IntersectionObserver' in window) || !nav) return;
  const links = [...nav.querySelectorAll('a[href^="#"]')];
  const sections = document.querySelectorAll('main section[id]');
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const id = entry.target.id;
      links.forEach(link => {
        const active = link.getAttribute('href') === `#${id}`;
        link.classList.toggle('active', active);
        if (active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    });
  }, { rootMargin: '-28% 0px -62% 0px' });
  sections.forEach(section => observer.observe(section));
}

function renderNewsItem(item, featured = false) {
  const article = document.createElement('article');
  article.className = featured ? 'news-feature' : '';

  if (featured) {
    const figure = document.createElement('figure');
    figure.className = `news-media${item.imageFit === 'contain' ? ' media-contain' : ''}`;
    const img = document.createElement('img');
    img.src = item.image;
    img.alt = item.alt || 'Aktuelles von der Reitanlage Eichhorn-Nels';
    img.loading = 'lazy';
    img.decoding = 'async';
    img.style.objectPosition = item.imagePosition || '50% 50%';
    figure.appendChild(img);
    article.appendChild(figure);
  }

  const copy = document.createElement('div');
  const meta = document.createElement('p');
  meta.className = 'news-meta';
  meta.textContent = [item.category, item.meta].filter(Boolean).join(' · ');
  copy.appendChild(meta);

  const title = document.createElement('h3');
  title.textContent = item.title;
  copy.appendChild(title);

  const text = document.createElement('p');
  text.textContent = item.text;
  copy.appendChild(text);

  if (item.link && item.linkText) {
    const link = document.createElement('a');
    link.href = item.link;
    link.textContent = `${item.linkText} ↗`;
    copy.appendChild(link);
  }
  article.appendChild(copy);
  return article;
}

async function loadNews() {
  const host = document.querySelector('[data-news-content]');
  if (!host) return;
  try {
    const response = await fetch('aktuelles.json', { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    const items = Array.isArray(data.items) ? data.items.filter(item => item?.title && item?.text) : [];
    if (!items.length) return;

    const layout = document.createElement('div');
    layout.className = 'news-layout';
    layout.appendChild(renderNewsItem(items[0], true));
    if (items.length > 1) {
      const list = document.createElement('div');
      list.className = 'news-list';
      items.slice(1).forEach(item => list.appendChild(renderNewsItem(item, false)));
      layout.appendChild(list);
    }
    host.replaceChildren(layout);

    const updated = document.querySelector('[data-news-updated]');
    if (updated && data.updated) {
      const parsed = new Date(`${data.updated}T12:00:00`);
      if (!Number.isNaN(parsed.getTime())) updated.textContent = `Redaktionell aktualisiert am ${parsed.toLocaleDateString('de-DE')}`;
    }
  } catch (error) {
    console.error('Aktuelles konnte nicht geladen werden:', error);
  }
}

setActiveNav();
loadNews();
const year = document.querySelector('[data-year]');
if (year) year.textContent = new Date().getFullYear();
