// main.js - extracted interactions and a11y helpers
document.addEventListener('DOMContentLoaded', () => {
    // preloader
    const preloader = document.querySelector('.preloader');
    if (preloader) setTimeout(() => preloader.style.display = 'none', 600);

    // theme toggle with ARIA
    const root = document.documentElement;
    const themeToggle = document.getElementById('themeToggle');
    function updateThemeAria() {
        if (!themeToggle) return;
        const isDark = root.getAttribute('data-theme') === 'dark';
        themeToggle.setAttribute('aria-pressed', String(isDark));
        // Update icon based on current theme
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.classList.remove('fa-moon', 'fa-sun');
            icon.classList.add(isDark ? 'fa-sun' : 'fa-moon');
        }
    }
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const current = root.getAttribute('data-theme');
            root.setAttribute('data-theme', current === 'dark' ? 'light' : 'dark');
            updateThemeAria();
        });
        updateThemeAria();
    }

    // menu toggle for mobile with ARIA
    const menuToggle = document.getElementById('menuToggle');
    const navLinks = document.getElementById('navLinks');
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            navLinks?.classList.toggle('active');
            const expanded = menuToggle.getAttribute('aria-expanded') === 'true';
            menuToggle.setAttribute('aria-expanded', String(!expanded));
        });
    }

    // Smooth scroll for nav links and close mobile menu on selection
    const navAnchors = document.querySelectorAll('.nav-links a');
    const navEl = document.querySelector('nav');
    function getNavHeight() {
        return navEl ? Math.ceil(navEl.getBoundingClientRect().height) : 80;
    }
    function updateNavOffsetCSS() {
        const h = getNavHeight();
        document.documentElement.style.setProperty('--nav-offset', `${h}px`);
    }
    // set initial CSS var
    updateNavOffsetCSS();
    navAnchors.forEach(a => {
        a.addEventListener('click', (e) => {
            const href = a.getAttribute('href');
            if (href && href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    // account for fixed nav height so section isn't hidden behind nav
                    const navHeight = getNavHeight();
                    const top = target.getBoundingClientRect().top + window.scrollY - navHeight - 12;
                    window.scrollTo({ top, behavior: 'smooth' });
                }

                // update active state immediately
                navAnchors.forEach(x => x.classList.remove('active'));
                a.classList.add('active');

                // close mobile nav if open
                if (navLinks?.classList.contains('active')) {
                    navLinks.classList.remove('active');
                    menuToggle?.setAttribute('aria-expanded', 'false');
                }
            }
        });
    });

    // typing text
    const typingText = document.getElementById('typingText');
    const phrases = ['I build fast, responsive UIs.', 'I design mobile experiences.', 'I craft accessible components.'];
    let pi = 0, ci = 0;
    function type() {
        if (!typingText) return;
        const text = phrases[pi];
        typingText.textContent = text.slice(0, ci++);
        if (ci > text.length) {
            ci = 0; pi = (pi + 1) % phrases.length;
            setTimeout(type, 1200);
        } else setTimeout(type, 60);
    }
    type();

    // reveal sections when they enter the viewport
    const sections = document.querySelectorAll('section');
    if ('IntersectionObserver' in window) {
        const obs = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12 });
        sections.forEach(s => obs.observe(s));
    } else {
        // fallback: reveal all
        sections.forEach(s => s.classList.add('visible'));
    }

    // Active nav link highlighting when sections enter viewport (accounts for fixed nav)
    let sectionObserver = null;
    function initSectionObserver() {
        if (!('IntersectionObserver' in window)) return;
        if (sectionObserver) sectionObserver.disconnect();
        const navHeight = getNavHeight();
        // update CSS var used by scroll-padding-top
        updateNavOffsetCSS();
        const rootMargin = `-${navHeight + 8}px 0px -${navHeight + 8}px 0px`;
        sectionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    navAnchors.forEach(a => {
                        if (a.getAttribute('href') === `#${id}`) {
                            navAnchors.forEach(x => x.classList.remove('active'));
                            a.classList.add('active');
                        }
                    });
                }
            });
        }, { threshold: 0.25, rootMargin });
        sections.forEach(s => sectionObserver.observe(s));
    }

    initSectionObserver();

    // Re-init observer on resize (debounced) because nav height can change
    let resizeTimer = null;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            initSectionObserver();
        }, 150);
    });

    // Ensure a default active link (home) if none is set
    if (!document.querySelector('.nav-links a.active')) {
        const first = document.querySelector('.nav-links a[href="#home"]');
        if (first) first.classList.add('active');
    }

    // skill progress animate
    document.querySelectorAll('.skill-progress').forEach(el => {
        const p = el.getAttribute('data-progress');
        if (p) el.style.width = p + '%';
    });

    // project filter - initialize with 'web' category visible by default
    const projectCards = document.querySelectorAll('.project-card');
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    // Show only web cards on initial page load
    projectCards.forEach(card => {
        if (card.getAttribute('data-category') === 'web') {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const filter = btn.getAttribute('data-filter');
            projectCards.forEach(card => {
                if (filter === 'all' || card.getAttribute('data-category') === filter) card.style.display = '';
                else card.style.display = 'none';
            });
        });
    });

    // scroll top
    const scrollTop = document.getElementById('scrollTop');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 400) scrollTop?.classList.add('visible'); else scrollTop?.classList.remove('visible');
    });
    scrollTop?.addEventListener('click', () => window.scrollTo({top:0, behavior:'smooth'}));
});
