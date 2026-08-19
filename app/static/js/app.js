/**
 * Cricket Predictor Pro — Frontend JavaScript
 * Handles navigation, form interactions, and animations.
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initFormHandling();
    initScrollAnimations();
});


/* ─── Navigation ──────────────────────────────────────────────────────────── */

function initNavigation() {
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            navToggle.classList.toggle('active');
        });

        // Close menu on link click (mobile)
        navLinks.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });

        // Close menu on outside click
        document.addEventListener('click', (e) => {
            if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
                navLinks.classList.remove('active');
                navToggle.classList.remove('active');
            }
        });
    }

    // Navbar background on scroll
    const navbar = document.getElementById('navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.style.background = 'rgba(6, 8, 15, 0.95)';
                navbar.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.3)';
            } else {
                navbar.style.background = 'rgba(6, 8, 15, 0.85)';
                navbar.style.boxShadow = 'none';
            }
        });
    }
}


/* ─── Form Handling ───────────────────────────────────────────────────────── */

function initFormHandling() {
    const form = document.getElementById('predictForm');
    if (!form) return;

    const btn = document.getElementById('predictBtn');
    const btnText = btn?.querySelector('.btn-text');
    const btnLoading = btn?.querySelector('.btn-loading');

    form.addEventListener('submit', () => {
        if (btnText) btnText.style.display = 'none';
        if (btnLoading) btnLoading.style.display = 'inline-flex';
        if (btn) btn.disabled = true;
    });

    // Input animation on focus
    form.querySelectorAll('.form-input').forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('focused');
        });
        input.addEventListener('blur', () => {
            input.parentElement.classList.remove('focused');
        });
    });
}


/* ─── Scroll Animations ───────────────────────────────────────────────────── */

function initScrollAnimations() {
    const observerOptions = {
        root: null,
        rootMargin: '0px 0px -60px 0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe cards and sections
    const animatables = document.querySelectorAll(
        '.format-card, .target-card, .model-card, .result-card, .compare-target-block'
    );
    animatables.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });
}

// CSS class for animation
const style = document.createElement('style');
style.textContent = `
    .animate-in {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }
    .form-group.focused .form-label {
        color: #4ade80;
    }
    .nav-toggle.active .toggle-bar:nth-child(1) {
        transform: translateY(7px) rotate(45deg);
    }
    .nav-toggle.active .toggle-bar:nth-child(2) {
        opacity: 0;
    }
    .nav-toggle.active .toggle-bar:nth-child(3) {
        transform: translateY(-7px) rotate(-45deg);
    }
`;
document.head.appendChild(style);
