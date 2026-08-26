const header = document.querySelector("[data-header]");
const navToggle = document.querySelector("[data-nav-toggle]");
const nav = document.querySelector("[data-nav]");
const progress = document.querySelector(".scroll-progress span");
const revealItems = document.querySelectorAll("[data-reveal]");
const navLinks = document.querySelectorAll('.main-nav a[href^="#"]');

/*
 * Design rule: no decorative sequence numbering such as 01 / 02 / 03.
 * The site should read like a deliberately designed local brand, not a
 * template or AI-generated portfolio layout. Real data such as years,
 * dimensions and prices remains untouched.
 */
document.querySelectorAll(".offer-index, .service-editorial-grid article > span").forEach(element => {
  element.remove();
});

const naturalLayout = document.createElement("style");
naturalLayout.textContent = `
  .offer-row {
    grid-template-columns: minmax(260px, .9fr) minmax(300px, 1.1fr) !important;
    gap: clamp(28px, 5vw, 80px) !important;
  }

  .service-editorial-grid article {
    padding-top: clamp(30px, 4vw, 48px) !important;
  }

  @media (max-width: 900px) {
    .offer-row {
      grid-template-columns: 1fr !important;
      gap: 12px !important;
    }
    .offer-row > p {
      grid-column: auto !important;
    }
  }
`;
document.head.appendChild(naturalLayout);

function updateScrollUI() {
  const y = window.scrollY;
  header?.classList.toggle("scrolled", y > 24);

  const max = document.documentElement.scrollHeight - window.innerHeight;
  if (progress) progress.style.width = `${max > 0 ? (y / max) * 100 : 0}%`;
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

  nav.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", () => {
      nav.classList.remove("open");
      document.body.classList.remove("nav-open");
      navToggle.setAttribute("aria-expanded", "false");
      navToggle.setAttribute("aria-label", "Menü öffnen");
    });
  });
}

if ("IntersectionObserver" in window) {
  const revealObserver = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      }
    }
  }, { threshold: 0.14, rootMargin: "0px 0px -50px 0px" });

  revealItems.forEach(item => revealObserver.observe(item));

  const sections = document.querySelectorAll("main section[id]");
  const navObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const id = entry.target.id;
      navLinks.forEach(link => link.classList.toggle("active", link.getAttribute("href") === `#${id}`));
    });
  }, { rootMargin: "-25% 0px -65% 0px", threshold: 0 });

  sections.forEach(section => navObserver.observe(section));
} else {
  revealItems.forEach(item => item.classList.add("is-visible"));
}

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
