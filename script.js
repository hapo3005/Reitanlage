const header = document.querySelector(".site-header");
const navToggle = document.querySelector(".nav-toggle");
const navLinks = document.querySelector(".nav-links");
const revealElements = document.querySelectorAll(".reveal");
const contactForm = document.querySelector(".contact-form");
const formMessage = document.querySelector(".form-message");
const progressBar = document.createElement("div");

progressBar.className = "scroll-progress";
document.body.appendChild(progressBar);

const updateScrollProgress = () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;

    progressBar.style.width = `${progress}%`;
};

window.addEventListener("scroll", () => {
    if (window.scrollY > 40) {
        header.classList.add("scrolled");
    } else {
        header.classList.remove("scrolled");
    }

    updateScrollProgress();
});

window.addEventListener("load", updateScrollProgress);

if (navToggle && navLinks) {
    navToggle.addEventListener("click", () => {
        navLinks.classList.toggle("active");
        navToggle.classList.toggle("active");
    });
}

document.querySelectorAll(".nav-links a").forEach((link) => {
    link.addEventListener("click", () => {
        navLinks.classList.remove("active");
        navToggle.classList.remove("active");
    });
});

/* PREMIUM REVEAL ANIMATION */

const revealObserver = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                revealObserver.unobserve(entry.target);
            }
        });
    },
    {
        threshold: 0.14,
        rootMargin: "0px 0px -70px 0px",
    }
);

revealElements.forEach((element, index) => {
    element.style.transitionDelay = `${Math.min(index * 35, 240)}ms`;
    revealObserver.observe(element);
});

/* HERO PARALLAX */

const hero = document.querySelector(".hero");
const heroContent = document.querySelector(".hero-content");
const heroCard = document.querySelector(".hero-card");

const updateHeroParallax = () => {
    if (!hero) return;

    const scrollY = window.scrollY;
    const heroHeight = hero.offsetHeight;

    if (scrollY <= heroHeight) {
        hero.style.backgroundPosition = `center ${scrollY * 0.25}px`;

        if (heroContent) {
            heroContent.style.transform = `translateY(${scrollY * 0.08}px)`;
        }

        if (heroCard) {
            heroCard.style.transform = `translateY(${scrollY * -0.06}px)`;
        }
    }
};

window.addEventListener("scroll", updateHeroParallax);

/* CONTACT FORM */

if (contactForm) {
    contactForm.addEventListener("submit", (event) => {
        event.preventDefault();

        const name = contactForm.name.value.trim();
        const email = contactForm.email.value.trim();
        const interest = contactForm.interest.value;
        const message = contactForm.message.value.trim();

        if (!name) {
            formMessage.textContent = "Bitte gib deinen Namen ein.";
            formMessage.classList.add("show");
            return;
        }

        const subject = encodeURIComponent(`Anfrage Reitanlage Eichhorn-Nels: ${interest}`);
        const body = encodeURIComponent(
            `Name: ${name}\nE-Mail: ${email}\nInteresse: ${interest}\n\nNachricht:\n${message}`
        );

        window.location.href = `mailto:eichhorn.c@t-online.de?subject=${subject}&body=${body}`;

        formMessage.textContent = `Danke, ${name}! Deine E-Mail-Anfrage wurde vorbereitet.`;
        formMessage.classList.add("show");

        contactForm.reset();

        setTimeout(() => {
            formMessage.classList.remove("show");
        }, 4500);
    });
}

/* PREMIUM CARD TILT */

const tiltCards = document.querySelectorAll(
    ".horse-card, .news-card, .lesson-list div, .stable-features div, .contact-details, .contact-form"
);

tiltCards.forEach((card) => {
    card.addEventListener("mousemove", (event) => {
        const rect = card.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotateX = ((y - centerY) / centerY) * -4;
        const rotateY = ((x - centerX) / centerX) * 4;

        card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px)`;
    });

    card.addEventListener("mouseleave", () => {
        card.style.transform = "";
    });
});

/* COUNTER ANIMATION */

const counters = document.querySelectorAll(".stable-features strong");

const counterObserver = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;

            const counter = entry.target;
            const rawValue = counter.textContent.trim();
            const configuredSuffix = counter.dataset.suffix || "";

            if (rawValue.includes("x")) {
                counterObserver.unobserve(counter);
                return;
            }

            if (rawValue.includes("%")) {
                animateCounter(counter, 0, parseInt(rawValue), "%");
            } else if (!isNaN(parseInt(rawValue))) {
                animateCounter(counter, 0, parseInt(rawValue), configuredSuffix);
            }

            counterObserver.unobserve(counter);
        });
    },
    {
        threshold: 0.6,
    }
);

counters.forEach((counter) => {
    counterObserver.observe(counter);
});

function animateCounter(element, start, end, suffix) {
    const duration = 1200;
    const startTime = performance.now();

    const update = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const value = Math.round(start + (end - start) * eased);

        element.textContent = `${value}${suffix}`;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    };

    requestAnimationFrame(update);
}

/* NEWS CAROUSEL */

const newsTrack = document.querySelector(".news-track");
const newsCards = document.querySelectorAll(".news-card");
const prevNewsBtn = document.querySelector(".carousel-btn-prev");
const nextNewsBtn = document.querySelector(".carousel-btn-next");
const dotsContainer = document.querySelector(".carousel-dots");
const newsCarousel = document.querySelector(".news-carousel");

let currentNewsIndex = 0;
let autoplayInterval = null;
let isDragging = false;
let startX = 0;
let currentTranslate = 0;

const getVisibleNewsCards = () => {
    if (window.innerWidth <= 680) return 1;
    if (window.innerWidth <= 950) return 2;
    return 3;
};

const getMaxNewsIndex = () => {
    return Math.max(newsCards.length - getVisibleNewsCards(), 0);
};

const createNewsDots = () => {
    if (!dotsContainer) return;

    dotsContainer.innerHTML = "";

    const dotCount = getMaxNewsIndex() + 1;

    for (let i = 0; i < dotCount; i++) {
        const dot = document.createElement("button");

        dot.classList.add("carousel-dot");
        dot.setAttribute("aria-label", `News Slide ${i + 1}`);

        if (i === currentNewsIndex) {
            dot.classList.add("active");
        }

        dot.addEventListener("click", () => {
            currentNewsIndex = i;
            updateNewsCarousel();
            restartAutoplay();
        });

        dotsContainer.appendChild(dot);
    }
};

const updateNewsCarousel = () => {
    if (!newsTrack || newsCards.length === 0) return;

    const cardWidth = newsCards[0].getBoundingClientRect().width;
    const gap = 24;
    const moveX = currentNewsIndex * (cardWidth + gap);

    currentTranslate = -moveX;
    newsTrack.style.transform = `translateX(${currentTranslate}px)`;

    newsCards.forEach((card, index) => {
        card.classList.toggle("active-news-card", index === currentNewsIndex);
    });

    document.querySelectorAll(".carousel-dot").forEach((dot, index) => {
        dot.classList.toggle("active", index === currentNewsIndex);
    });
};

const goToNextNews = () => {
    if (currentNewsIndex < getMaxNewsIndex()) {
        currentNewsIndex++;
    } else {
        currentNewsIndex = 0;
    }

    updateNewsCarousel();
};

const goToPrevNews = () => {
    if (currentNewsIndex > 0) {
        currentNewsIndex--;
    } else {
        currentNewsIndex = getMaxNewsIndex();
    }

    updateNewsCarousel();
};

const startAutoplay = () => {
    if (!newsTrack || newsCards.length === 0) return;

    autoplayInterval = setInterval(() => {
        goToNextNews();
    }, 5200);
};

const stopAutoplay = () => {
    if (autoplayInterval) {
        clearInterval(autoplayInterval);
        autoplayInterval = null;
    }
};

const restartAutoplay = () => {
    stopAutoplay();
    startAutoplay();
};

if (nextNewsBtn && prevNewsBtn && newsCards.length > 0) {
    nextNewsBtn.addEventListener("click", () => {
        goToNextNews();
        restartAutoplay();
    });

    prevNewsBtn.addEventListener("click", () => {
        goToPrevNews();
        restartAutoplay();
    });

    window.addEventListener("resize", () => {
        if (currentNewsIndex > getMaxNewsIndex()) {
            currentNewsIndex = getMaxNewsIndex();
        }

        createNewsDots();
        updateNewsCarousel();
    });

    if (newsCarousel) {
        newsCarousel.addEventListener("mouseenter", stopAutoplay);
        newsCarousel.addEventListener("mouseleave", startAutoplay);
    }

    createNewsDots();
    updateNewsCarousel();
    startAutoplay();
}

/* NEWS SWIPE / DRAG */

if (newsTrack) {
    newsTrack.addEventListener("pointerdown", (event) => {
        isDragging = true;
        startX = event.clientX;
        newsTrack.classList.add("is-dragging");
        stopAutoplay();
    });

    window.addEventListener("pointermove", (event) => {
        if (!isDragging) return;

        const diff = event.clientX - startX;
        newsTrack.style.transform = `translateX(${currentTranslate + diff}px)`;
    });

    window.addEventListener("pointerup", (event) => {
        if (!isDragging) return;

        const diff = event.clientX - startX;

        if (diff < -70) {
            goToNextNews();
        } else if (diff > 70) {
            goToPrevNews();
        } else {
            updateNewsCarousel();
        }

        isDragging = false;
        newsTrack.classList.remove("is-dragging");
        startAutoplay();
    });
}

/* ACTIVE NAV HIGHLIGHT */

const sections = document.querySelectorAll("main section[id]");
const navItems = document.querySelectorAll(".nav-links a[href^='#']");

const navObserver = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;

            const id = entry.target.getAttribute("id");

            navItems.forEach((item) => {
                item.classList.toggle("active-link", item.getAttribute("href") === `#${id}`);
            });
        });
    },
    {
        threshold: 0.35,
    }
);

sections.forEach((section) => {
    navObserver.observe(section);
});
