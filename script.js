const header = document.querySelector("[data-header]");
const navToggle = document.querySelector("[data-nav-toggle]");
const nav = document.querySelector("[data-nav]");

const newsStyles = document.createElement("link");
newsStyles.rel = "stylesheet";
newsStyles.href = "aktuelles.css";
document.head.appendChild(newsStyles);

function createNewsSection() {
  const moments = document.querySelector("#einblicke");
  if (!moments || document.querySelector("#aktuelles")) return;

  const section = document.createElement("section");
  section.className = "section news-section";
  section.id = "aktuelles";
  section.innerHTML = `
    <div class="container">
      <div class="news-heading" data-reveal>
        <div>
          <p class="eyebrow">Aktuelles vom Hof</p>
          <h2>Was gerade auf der Reitanlage passiert.</h2>
        </div>
        <p>Termine, freie Möglichkeiten, Kurse und Neuigkeiten – dieser Bereich wird laufend gepflegt.</p>
      </div>
      <div data-news-content>
        <p class="news-empty">Aktuelles wird geladen …</p>
      </div>
      <p class="news-updated" data-news-updated hidden></p>
    </div>
  `;
  moments.before(section);

  const priceLink = nav?.querySelector('a[href="#preise"]');
  if (nav && !nav.querySelector('a[href="#aktuelles"]')) {
    const link = document.createElement("a");
    link.href = "#aktuelles";
    link.textContent = "Aktuelles";
    nav.insertBefore(link, priceLink || nav.querySelector(".nav-contact"));
  }
}

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
    host.innerHTML = '<p class="news-empty">Die aktuellen Meldungen konnten gerade nicht geladen werden. Termine und Verfügbarkeiten bitte direkt telefonisch oder per WhatsApp erfragen.</p>';
    console.error("Aktuelles konnte nicht geladen werden:", error);
  }
}

function updateScrollUI() {
  header?.classList.toggle("scrolled", window.scrollY > 24);
}

window.addEventListener("scroll", updateScrollUI, { passive: true });
window.addEventListener("resize", updateScrollUI);
updateScrollUI();

if (navToggle && nav) {
  navToggle.addEventListener("click", () => {
    const open = !nav.classList.contains("open");
    nav.classList.toggle("open", open);
    document.body.classList.toggle("nav-open", open);
    navToggle.setAttribute("aria-expanded", String(open));
    navToggle.setAttribute("aria-label", open ? "Menü schließen" : "Menü öffnen");
  });

  nav.addEventListener("click", event => {
    if (!event.target.closest("a")) return;
    nav.classList.remove("open");
    document.body.classList.remove("nav-open");
    navToggle.setAttribute("aria-expanded", "false");
    navToggle.setAttribute("aria-label", "Menü öffnen");
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
    }, { threshold: 0.14, rootMargin: "0px 0px -50px 0px" });
  }

  items.forEach(item => revealObserver.observe(item));
}

function setupSectionObserver() {
  if (!("IntersectionObserver" in window)) return;
  const navLinks = document.querySelectorAll('.main-nav a[href^="#"]');
  const sections = document.querySelectorAll("main section[id]");
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const id = entry.target.id;
      navLinks.forEach(link => link.classList.toggle("active", link.getAttribute("href") === `#${id}`));
    });
  }, { rootMargin: "-25% 0px -65% 0px", threshold: 0 });
  sections.forEach(section => observer.observe(section));
}

createNewsSection();
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
