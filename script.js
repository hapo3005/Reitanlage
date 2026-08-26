const premiumStyles = document.createElement("link");
premiumStyles.rel = "stylesheet";
premiumStyles.href = "premium.css?v=20260826-worldclass1";
document.head.appendChild(premiumStyles);

const header = document.querySelector("[data-header]");
const navToggle = document.querySelector("[data-nav-toggle]");
const nav = document.querySelector("[data-nav]");

function buildMeta(item) {
  const meta = document.createElement("p");
  meta.className = "news-meta";
  [item.category, item.meta].filter(Boolean).forEach(value => {
    const span = document.createElement("span");
    span.textContent = value;
    meta.appendChild(span);
  });
  return meta;
}

function buildNewsLink(item) {
  if (!item.link || !item.linkText) return null;
  const link = document.createElement("a");
  link.className = "news-link";
  link.href = item.link;
  link.textContent = `${item.linkText} →`;
  return link;
}

function applyImageFraming(image, imageWrap, item) {
  const fit = item.imageFit === "contain" ? "contain" : "cover";
  const desktopPosition = item.imagePosition || "50% 50%";
  const mobilePosition = item.imagePositionMobile || desktopPosition;

  image.dataset.fit = fit;
  image.style.setProperty("--image-fit", fit);
  image.style.setProperty("--image-position", desktopPosition);
  image.style.setProperty("--image-position-mobile", mobilePosition);
  imageWrap.classList.toggle("is-contain", fit === "contain");
}

function renderNewsItem(item, featured = false) {
  const article = document.createElement("article");
  article.dataset.reveal = "";
  if (featured) article.className = "news-feature";

  const imageWrap = document.createElement("div");
  imageWrap.className = featured ? "news-feature-image" : "news-thumb";

  const image = document.createElement("img");
  image.src = item.image;
  image.alt = item.alt || "Aktuelles von der Reitanlage Eichhorn-Nels";
  image.loading = "lazy";
  image.decoding = "async";
  applyImageFraming(image, imageWrap, item);
  imageWrap.appendChild(image);

  const copy = document.createElement("div");
  if (featured) copy.className = "news-feature-copy";
  copy.appendChild(buildMeta(item));

  const title = document.createElement("h3");
  title.textContent = item.title;
  copy.appendChild(title);

  const text = document.createElement("p");
  text.textContent = item.text;
  copy.appendChild(text);

  const link = buildNewsLink(item);
  if (link) copy.appendChild(link);

  article.append(imageWrap, copy);
  return article;
}

async function loadNews() {
  const host = document.querySelector("[data-news-content]");
  if (!host) return;

  try {
    const response = await fetch("aktuelles.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    const items = Array.isArray(data.items) ? data.items.filter(item => item?.title && item?.text) : [];

    if (!items.length) {
      host.innerHTML = '<p class="news-empty">Aktuell sind keine Meldungen veröffentlicht. Für Termine und Verfügbarkeiten bitte direkt Kontakt aufnehmen.</p>';
      return;
    }

    const layout = document.createElement("div");
    layout.className = "news-layout";
    layout.appendChild(renderNewsItem(items[0], true));

    if (items.length > 1) {
      const list = document.createElement("div");
      list.className = "news-list";
      items.slice(1).forEach(item => list.appendChild(renderNewsItem(item)));
      layout.appendChild(list);
    }

    host.replaceChildren(layout);

    const updated = document.querySelector("[data-news-updated]");
    if (updated && data.updated) {
      const parsed = new Date(`${data.updated}T12:00:00`);
      if (!Number.isNaN(parsed.getTime())) {
        updated.textContent = `Redaktionell aktualisiert am ${parsed.toLocaleDateString("de-DE")}`;
        updated.hidden = false;
      }
    }

    setupRevealObservers(host.querySelectorAll("[data-reveal]"));
  } catch (error) {
    console.error("Aktuelles konnte nicht geladen werden:", error);
  }
}

let scrollFrame = null;
function updateScrollUI() {
  header?.classList.toggle("scrolled", window.scrollY > 24);
  scrollFrame = null;
}

function requestScrollUI() {
  if (scrollFrame !== null) return;
  scrollFrame = requestAnimationFrame(updateScrollUI);
}

window.addEventListener("scroll", requestScrollUI, { passive: true });
updateScrollUI();

function closeNavigation({ returnFocus = false } = {}) {
  if (!nav || !navToggle) return;
  nav.classList.remove("open");
  document.body.classList.remove("nav-open");
  navToggle.setAttribute("aria-expanded", "false");
  navToggle.setAttribute("aria-label", "Menü öffnen");
  if (returnFocus) navToggle.focus();
}

if (navToggle && nav) {
  navToggle.addEventListener("click", () => {
    const open = !nav.classList.contains("open");
    if (!open) {
      closeNavigation();
      return;
    }

    nav.classList.add("open");
    document.body.classList.add("nav-open");
    navToggle.setAttribute("aria-expanded", "true");
    navToggle.setAttribute("aria-label", "Menü schließen");
  });

  nav.addEventListener("click", event => {
    if (event.target.closest("a")) closeNavigation();
  });

  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && nav.classList.contains("open")) {
      closeNavigation({ returnFocus: true });
    }
  });
}

let revealObserver;
function setupRevealObservers(elements) {
  const items = Array.from(elements);
  if (!("IntersectionObserver" in window)) {
    items.forEach(item => item.classList.add("is-visible"));
    return;
  }

  if (!revealObserver) {
    revealObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -42px 0px" });
  }

  items.forEach(item => revealObserver.observe(item));
}

function setupSectionObserver() {
  if (!("IntersectionObserver" in window)) return;
  const navLinks = Array.from(document.querySelectorAll('.main-nav a[href^="#"]'));
  const sections = document.querySelectorAll("main section[id]");

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const id = entry.target.id;

      navLinks.forEach(link => {
        const active = link.getAttribute("href") === `#${id}`;
        link.classList.toggle("active", active);
        if (active) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
    });
  }, { rootMargin: "-24% 0px -66% 0px", threshold: 0 });

  sections.forEach(section => observer.observe(section));
}

setupRevealObservers(document.querySelectorAll("[data-reveal]"));
setupSectionObserver();
loadNews();

const details = document.querySelector(".price-details");
if (details) {
  details.addEventListener("toggle", () => {
    if (details.open) {
      setTimeout(() => details.scrollIntoView({ behavior: "smooth", block: "nearest" }), 80);
    }
  });
}

const year = document.querySelector("[data-year]");
if (year) year.textContent = new Date().getFullYear();
