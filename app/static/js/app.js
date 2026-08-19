/**
 * Cricket Predictor Pro — Frontend JavaScript
 * Handles navigation, target slider, form interactions, and animations.
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initThemeToggle();
    initNavbarAvatar();
    initTargetSlider();
    initFormHandling();
    initScrollAnimations();
});


/* ─── Navigation ──────────────────────────────────────────────────────────── */

function initNavigation() {
    const navToggle = document.getElementById('navToggle');
    const navLinks  = document.getElementById('navLinks');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            navToggle.classList.toggle('active');
        });

        // Close on any nav-link click (mobile)
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
                navLinks.classList.remove('active');
                navToggle.classList.remove('active');
            }
        });
    }

    // Solidify navbar background on scroll via CSS classes (theme-aware)
    const navbar = document.getElementById('navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 30) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        }, { passive: true });
    }
}


/* ─── Theme Toggle (Dark / Light) ────────────────────────────────────────── */

function initThemeToggle() {
    const btn = document.getElementById('themeToggle');
    if (!btn) return;

    btn.addEventListener('click', () => {
        const html = document.documentElement;
        const current = html.getAttribute('data-theme') || 'dark';
        const next = current === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', next);
        localStorage.setItem('cpp_theme', next);
    });
}


/* ─── Navbar Avatar (synced from localStorage profile) ───────────────────── */

function initNavbarAvatar() {
    try {
        const profile = JSON.parse(localStorage.getItem('cricket_predictor_profile')) || {};
        updateNavbarAvatar(profile.avatar || '', profile.name || '');
    } catch { /* no profile yet */ }
}

// Exported to window so profile page can call it after save
window.updateNavbarAvatar = function(avatarSrc, name) {
    const img = document.getElementById('navAvatarImg');
    const ph  = document.getElementById('navAvatarPlaceholder');
    const nameEl = document.getElementById('navProfileName');

    if (avatarSrc) {
        if (img) { img.src = avatarSrc; img.style.display = 'block'; }
        if (ph)  ph.style.display = 'none';
    } else {
        if (img) img.style.display = 'none';
        if (ph)  ph.style.display = 'flex';
    }
    if (nameEl && name) {
        nameEl.textContent = name.split(' ')[0]; // first name only
    }
};


/* ─── Target Slider (arrow-controlled, no browser scrollbar) ─────────────── */

function initTargetSlider() {
    const track = document.getElementById('targetSlider');
    const btnL  = document.getElementById('sliderLeft');
    const btnR  = document.getElementById('sliderRight');
    if (!track || !btnL || !btnR) return;

    // Amount to scroll per arrow click (px) — one "card" width
    const STEP = 180;

    function updateArrows() {
        const maxScroll = track.scrollWidth - track.clientWidth;
        btnL.disabled = track.scrollLeft <= 2;
        btnR.disabled = track.scrollLeft >= maxScroll - 2;
    }

    btnL.addEventListener('click', () => {
        track.scrollBy({ left: -STEP, behavior: 'smooth' });
    });

    btnR.addEventListener('click', () => {
        track.scrollBy({ left: STEP, behavior: 'smooth' });
    });

    // Re-check arrows after every scroll settles
    track.addEventListener('scroll', updateArrows, { passive: true });

    // Allow track to scroll (override CSS overflow for JS control)
    track.style.overflowX = 'auto';

    // Scroll active button into view on page load
    const active = track.querySelector('.switcher-btn-active');
    if (active) {
        setTimeout(() => {
            active.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        }, 100);
    }

    // Initial arrow state
    setTimeout(updateArrows, 150);

    // Touch / swipe support on the track
    let startX = 0;
    track.addEventListener('touchstart', (e) => { startX = e.touches[0].clientX; }, { passive: true });
    track.addEventListener('touchend',   (e) => {
        const diff = startX - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 30) track.scrollBy({ left: diff, behavior: 'smooth' });
    }, { passive: true });
}


/* ─── Form Handling ───────────────────────────────────────────────────────── */

function initFormHandling() {
    const form = document.getElementById('predictForm');
    if (!form) return;

    const btn       = document.getElementById('predictBtn');
    const btnText   = btn?.querySelector('.btn-text');
    const btnLoad   = btn?.querySelector('.btn-loading');

    form.addEventListener('submit', () => {
        if (btnText) btnText.style.display = 'none';
        if (btnLoad) btnLoad.style.display = 'inline-flex';
        if (btn)     btn.disabled = true;
    });

    // Green label glow on focus
    form.querySelectorAll('.form-input').forEach(input => {
        input.addEventListener('focus', () => input.parentElement.classList.add('focused'));
        input.addEventListener('blur',  () => input.parentElement.classList.remove('focused'));
    });
}


/* ─── Scroll-triggered Card Animations ────────────────────────────────────── */

function initScrollAnimations() {
    // Cards start visible; animate-in adds a subtle lift-in effect
    const cards = document.querySelectorAll(
        '.format-card, .target-card, .model-card, .result-card, .compare-target-block'
    );
    if (!cards.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, { rootMargin: '0px 0px -40px 0px', threshold: 0.08 });

    cards.forEach(el => observer.observe(el));
}


/* ─── Injected CSS helpers ────────────────────────────────────────────────── */

const _css = document.createElement('style');
_css.textContent = `
    /* Card lift-in animation (cards are always visible; this adds polish) */
    .format-card, .target-card, .model-card, .result-card, .compare-target-block {
        transition: opacity 0.45s ease, transform 0.45s ease;
    }
    .animate-in {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }

    /* Form label highlight on focus */
    .form-group.focused .form-label { color: #4ade80; }

    /* Hamburger → ✕ animation */
    .nav-toggle.active .toggle-bar:nth-child(1) { transform: translateY(7px)  rotate(45deg);  }
    .nav-toggle.active .toggle-bar:nth-child(2) { opacity: 0; }
    .nav-toggle.active .toggle-bar:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

    /* Slider track scrollbar always hidden */
    #targetSlider::-webkit-scrollbar { display: none; }
    #targetSlider { -ms-overflow-style: none; scrollbar-width: none; }
`;
document.head.appendChild(_css);
