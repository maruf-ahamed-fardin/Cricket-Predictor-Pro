/**
 * Cricket Predictor Pro — Frontend JavaScript
 * Features: Navigation, Toast, Theme, Avatar, Target Slider,
 *           Form Validation, Scroll Animations, History,
 *           Share, i18n, PWA registration.
 */

/* ─── Boot ─────────────────────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initThemeToggle();
    initNavbarAvatar();
    initTargetSlider();
    initFormHandling();
    initScrollAnimations();
    initToastSystem();
    initI18n();
    initSettingsDropdown();
    registerServiceWorker();
    initShareButton();
    initExportButtons();
    initHistoryPage();
    initCompareFilter();
});


/* ─── Navigation ──────────────────────────────────────────────────────────── */

function initNavigation() {
    const navToggle = document.getElementById('navToggle');
    const navLinks  = document.getElementById('navLinks');
    if (!navToggle || !navLinks) return;

    navToggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        navToggle.classList.toggle('active');
        navToggle.setAttribute('aria-expanded', navLinks.classList.contains('active'));
    });

    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
            navToggle.classList.remove('active');
            navToggle.setAttribute('aria-expanded', 'false');
        });
    });

    document.addEventListener('click', (e) => {
        if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
            navLinks.classList.remove('active');
            navToggle.classList.remove('active');
            navToggle.setAttribute('aria-expanded', 'false');
        }
    });

    // Escape key closes mobile menu
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            navLinks.classList.remove('active');
            navToggle.classList.remove('active');
        }
    });

    const navbar = document.getElementById('navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            navbar.classList.toggle('navbar-scrolled', window.scrollY > 30);
        }, { passive: true });
    }
}


/* ─── Theme Toggle (Dark / Light) ────────────────────────────────────────── */

function initThemeToggle() {
    const btn = document.getElementById('themeToggle');
    if (!btn) return;
    btn.addEventListener('click', () => {
        const html = document.documentElement;
        const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', next);
        localStorage.setItem('cpp_theme', next);
    });
}


/* ─── Navbar Avatar ───────────────────────────────────────────────────────── */

function initNavbarAvatar() {
    try {
        const profile = JSON.parse(localStorage.getItem('cricket_predictor_profile')) || {};
        updateNavbarAvatar(profile.avatar || '', profile.name || '');
    } catch { /* no profile yet */ }
}

window.updateNavbarAvatar = function(avatarSrc, name) {
    const img    = document.getElementById('navAvatarImg');
    const ph     = document.getElementById('navAvatarPlaceholder');
    const nameEl = document.getElementById('navProfileName');
    if (avatarSrc) {
        if (img) { img.src = avatarSrc; img.style.display = 'block'; }
        if (ph)  ph.style.display = 'none';
    } else {
        if (img) img.style.display = 'none';
        if (ph)  ph.style.display = 'flex';
    }
    if (nameEl && name) nameEl.textContent = name.split(' ')[0];
};


/* ─── Target Slider ───────────────────────────────────────────────────────── */

function initTargetSlider() {
    const track = document.getElementById('targetSlider');
    const btnL  = document.getElementById('sliderLeft');
    const btnR  = document.getElementById('sliderRight');
    if (!track || !btnL || !btnR) return;

    const STEP = 180;

    function updateArrows() {
        const max = track.scrollWidth - track.clientWidth;
        btnL.disabled = track.scrollLeft <= 2;
        btnR.disabled = track.scrollLeft >= max - 2;
    }

    btnL.addEventListener('click', () => track.scrollBy({ left: -STEP, behavior: 'smooth' }));
    btnR.addEventListener('click', () => track.scrollBy({ left:  STEP, behavior: 'smooth' }));
    track.addEventListener('scroll', updateArrows, { passive: true });
    track.style.overflowX = 'auto';

    const active = track.querySelector('.switcher-btn-active');
    if (active) setTimeout(() => active.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' }), 100);
    setTimeout(updateArrows, 150);

    // Touch swipe
    let startX = 0;
    track.addEventListener('touchstart', e => { startX = e.touches[0].clientX; }, { passive: true });
    track.addEventListener('touchend',   e => {
        const diff = startX - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 30) track.scrollBy({ left: diff, behavior: 'smooth' });
    }, { passive: true });
}


/* ─── Toast Notification System ──────────────────────────────────────────── */

function initToastSystem() {
    // Build container if not in DOM yet
    if (!document.getElementById('toastContainer')) {
        const el = document.createElement('div');
        el.id = 'toastContainer';
        el.setAttribute('aria-live', 'polite');
        el.setAttribute('aria-atomic', 'true');
        document.body.appendChild(el);
    }
}

/**
 * Show a toast notification.
 * @param {string} message  Text to display.
 * @param {'success'|'error'|'info'|'warning'} type
 * @param {number} duration  Auto-dismiss after ms (default 3500).
 */
window.showToast = function(message, type = 'info', duration = 3500) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-msg">${message}</span>
        <button class="toast-close" aria-label="Dismiss">×</button>
    `;

    toast.querySelector('.toast-close').addEventListener('click', () => dismissToast(toast));
    container.appendChild(toast);

    // Animate in
    requestAnimationFrame(() => toast.classList.add('toast-visible'));

    // Auto-dismiss
    setTimeout(() => dismissToast(toast), duration);
    return toast;
};

function dismissToast(toast) {
    toast.classList.remove('toast-visible');
    toast.classList.add('toast-hiding');
    toast.addEventListener('transitionend', () => toast.remove(), { once: true });
}


/* ─── Form Handling + Input Validation ───────────────────────────────────── */

function initFormHandling() {
    const form = document.getElementById('predictForm');
    if (!form) return;

    const btn      = document.getElementById('predictBtn');
    const btnText  = btn?.querySelector('.btn-text');
    const btnLoad  = btn?.querySelector('.btn-loading');

    // Attach validation attributes from data-* ranges
    form.querySelectorAll('.form-input[data-min]').forEach(input => {
        const min  = parseFloat(input.dataset.min);
        const max  = parseFloat(input.dataset.max);
        const step = input.dataset.step || 'any';
        input.setAttribute('min', min);
        input.setAttribute('max', max);
        input.setAttribute('step', step);

        // Real-time validation
        input.addEventListener('input', () => validateInput(input, min, max));
        input.addEventListener('blur',  () => validateInput(input, min, max));
        input.addEventListener('focus', () => input.closest('.form-group')?.classList.add('focused'));
        input.addEventListener('blur',  () => input.closest('.form-group')?.classList.remove('focused'));
    });

    form.addEventListener('submit', (e) => {
        let valid = true;
        form.querySelectorAll('.form-input[data-min]').forEach(input => {
            const min = parseFloat(input.dataset.min);
            const max = parseFloat(input.dataset.max);
            if (!validateInput(input, min, max)) valid = false;
        });

        if (!valid) {
            e.preventDefault();
            showToast('Please fix the highlighted fields before predicting.', 'error');
            return;
        }

        if (btnText) btnText.style.display = 'none';
        if (btnLoad) btnLoad.style.display = 'inline-flex';
        if (btn)     btn.disabled = true;
    });
}

function validateInput(input, min, max) {
    const val = parseFloat(input.value);
    const group = input.closest('.form-group');
    const hint  = group?.querySelector('.range-error');
    const invalid = isNaN(val) || val < min || val > max;

    input.classList.toggle('input-invalid', invalid);
    if (hint) hint.style.display = invalid ? 'block' : 'none';
    return !invalid;
}


/* ─── Prediction History (localStorage) ──────────────────────────────────── */

const HISTORY_KEY = 'cpp_prediction_history';
const MAX_HISTORY = 50;

window.savePredictionToHistory = function(entry) {
    try {
        const history = getPredictionHistory();
        history.unshift({ ...entry, id: Date.now(), timestamp: new Date().toISOString() });
        if (history.length > MAX_HISTORY) history.length = MAX_HISTORY;
        localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
        // Increment profile predictions counter
        try {
            const p = JSON.parse(localStorage.getItem('cricket_predictor_profile')) || {};
            p.predictions = (parseInt(p.predictions || 0) + 1);
            localStorage.setItem('cricket_predictor_profile', JSON.stringify(p));
        } catch {}
    } catch (e) {
        console.warn('Could not save history:', e);
    }
};

function getPredictionHistory() {
    try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) || []; }
    catch { return []; }
}

function initHistoryPage() {
    const container = document.getElementById('historyContainer');
    if (!container) return;

    renderHistory(container);

    const clearBtn = document.getElementById('clearHistoryBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (!confirm('Clear all prediction history? This cannot be undone.')) return;
            localStorage.removeItem(HISTORY_KEY);
            renderHistory(container);
            showToast('History cleared.', 'info');
        });
    }

    const exportBtn = document.getElementById('exportHistoryCsvBtn');
    if (exportBtn) exportBtn.addEventListener('click', exportHistoryCSV);
}

function renderHistory(container) {
    const history = getPredictionHistory();
    if (!history.length) {
        container.innerHTML = `
            <div class="results-empty">
                <div class="empty-icon">📋</div>
                <h3>No Predictions Yet</h3>
                <p>Go to a <a href="/predict/t20">Predict</a> page and run a prediction — it will appear here.</p>
            </div>`;
        return;
    }

    container.innerHTML = history.map((entry, i) => `
        <div class="history-card glass-card" id="hcard-${entry.id}">
            <div class="history-card-header">
                <div class="history-meta">
                    <span class="history-format format-color-${entry.format_key}">${entry.format}</span>
                    <span class="history-target">${entry.target_icon || ''} ${entry.target}</span>
                </div>
                <div class="history-time">${new Date(entry.timestamp).toLocaleString()}</div>
            </div>
            <div class="history-predictions">
                ${Object.entries(entry.predictions || {}).map(([m, p]) => `
                    <div class="history-pred ${m === entry.best_model ? 'history-pred-best' : ''}">
                        <span class="history-model-name">${m === entry.best_model ? '🏆 ' : ''}${m}</span>
                        <span class="history-value">${p.value ?? '—'}</span>
                    </div>`).join('')}
            </div>
            <div class="history-actions">
                <a href="/predict/${entry.format_key}?target=${entry.target_key}" class="btn btn-outline btn-sm">
                    🔮 Predict Again
                </a>
                <button class="btn btn-outline btn-sm" onclick="deleteHistoryEntry(${entry.id})">🗑️ Remove</button>
            </div>
        </div>`).join('');
}

window.deleteHistoryEntry = function(id) {
    const history = getPredictionHistory().filter(e => e.id !== id);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    const card = document.getElementById(`hcard-${id}`);
    if (card) { card.style.opacity = '0'; setTimeout(() => card.remove(), 300); }
    showToast('Entry removed.', 'info');
};

function exportHistoryCSV() {
    const history = getPredictionHistory();
    if (!history.length) { showToast('No history to export.', 'warning'); return; }

    const headers = ['Timestamp', 'Format', 'Target', 'Best Model', 'LR Value', 'GB Value', 'PR Value'];
    const rows = history.map(e => {
        const preds = e.predictions || {};
        return [
            e.timestamp,
            e.format,
            e.target,
            e.best_model,
            preds['Linear Regression']?.value ?? '',
            preds['Gradient Boosting']?.value ?? '',
            preds['Polynomial Regression']?.value ?? '',
        ].map(v => `"${v}"`).join(',');
    });

    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url; a.download = 'cricket_predictions.csv';
    a.click(); URL.revokeObjectURL(url);
    showToast('CSV exported!', 'success');
}


/* ─── Share Button ────────────────────────────────────────────────────────── */

function initShareButton() {
    const shareBtn = document.getElementById('shareResultBtn');
    if (!shareBtn) return;

    shareBtn.addEventListener('click', async () => {
        const format = shareBtn.dataset.format || '';
        const target = shareBtn.dataset.target || '';
        const best   = shareBtn.dataset.best   || '';
        const value  = shareBtn.dataset.value  || '';

        const text = `🏏 Cricket Predictor Pro\n${format} — ${target}\n🏆 ${best}: ${value}\nPredict at Cricket Predictor Pro!`;
        const url  = window.location.href;

        if (navigator.share) {
            try {
                await navigator.share({ title: 'Cricket Predictor Pro', text, url });
                showToast('Shared successfully!', 'success');
            } catch (err) {
                if (err.name !== 'AbortError') fallbackCopy(text);
            }
        } else {
            fallbackCopy(text);
        }
    });
}

async function fallbackCopy(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Prediction copied to clipboard!', 'success');
    } catch {
        showToast('Could not copy — please copy manually.', 'error');
    }
}


/* ─── Export (Print / PDF) ────────────────────────────────────────────────── */

function initExportButtons() {
    const printBtn = document.getElementById('printResultBtn');
    if (printBtn) {
        printBtn.addEventListener('click', () => {
            window.print();
        });
    }
}


/* ─── Compare Page: Search / Filter ──────────────────────────────────────── */

function initCompareFilter() {
    const searchInput = document.getElementById('compareSearch');
    const modelFilter = document.getElementById('compareModelFilter');
    if (!searchInput && !modelFilter) return;

    function applyFilter() {
        const query = (searchInput?.value || '').toLowerCase();
        const selectedModel = modelFilter?.value || '';

        document.querySelectorAll('.compare-target-block').forEach(block => {
            const title = block.querySelector('.compare-target-title')?.textContent.toLowerCase() || '';
            const matchesQuery  = !query || title.includes(query);

            // Model filter: hide rows that don't match
            if (selectedModel) {
                block.querySelectorAll('.compare-table tbody tr').forEach(row => {
                    const modelCell = row.querySelector('.model-name-cell')?.textContent || '';
                    row.style.display = modelCell.includes(selectedModel) ? '' : 'none';
                });
            } else {
                block.querySelectorAll('.compare-table tbody tr').forEach(row => row.style.display = '');
            }

            block.style.display = matchesQuery ? '' : 'none';
        });
    }

    searchInput?.addEventListener('input', applyFilter);
    modelFilter?.addEventListener('change', applyFilter);
}


/* ─── Scroll Animations ───────────────────────────────────────────────────── */

function initScrollAnimations() {
    const cards = document.querySelectorAll(
        '.format-card, .target-card, .model-card, .result-card, .compare-target-block, .history-card, .about-card'
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


/* ─── i18n Toggle (EN / বাংলা) ───────────────────────────────────────────── */

const I18N_KEY = 'cpp_lang';
let _translations = {};

function initI18n() {
    const savedLang = localStorage.getItem(I18N_KEY) || 'en';
    loadLanguage(savedLang);

    // Old single button support if any
    const btn = document.getElementById('langToggleBtn');
    if (btn) {
        btn.addEventListener('click', () => {
            const current = localStorage.getItem(I18N_KEY) || 'en';
            const next = current === 'en' ? 'bn' : 'en';
            loadLanguage(next);
        });
    }

    // Segmented option buttons
    const optEn = document.getElementById('langOptEn');
    const optBn = document.getElementById('langOptBn');
    if (optEn) optEn.addEventListener('click', () => loadLanguage('en'));
    if (optBn) optBn.addEventListener('click', () => loadLanguage('bn'));
}

async function loadLanguage(lang) {
    try {
        const resp = await fetch(`/static/translations/${lang}.json?v=${Date.now()}`);
        _translations = await resp.json();
        applyTranslations(_translations);
        localStorage.setItem(I18N_KEY, lang);

        // Update single toggle btn if present
        const btn = document.getElementById('langToggleBtn');
        if (btn) {
            btn.textContent = lang === 'en' ? 'বাংলা' : 'English';
            btn.setAttribute('title', lang === 'en' ? 'Switch to বাংলা' : 'Switch to English');
        }

        // Update segmented buttons in Settings dropdown
        const optEn = document.getElementById('langOptEn');
        const optBn = document.getElementById('langOptBn');
        if (optEn) optEn.classList.toggle('active', lang === 'en');
        if (optBn) optBn.classList.toggle('active', lang === 'bn');

        document.documentElement.lang = lang;
        window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang, translations: _translations } }));
    } catch (e) {
        console.warn('i18n load failed:', e);
    }
}

function initSettingsDropdown() {
    const trigger = document.getElementById('settingsDropdownTrigger');
    const dropdown = trigger?.closest('.nav-settings-dropdown');
    if (!trigger || !dropdown) return;

    trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = dropdown.classList.toggle('dropdown-open');
        trigger.setAttribute('aria-expanded', isOpen);
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!dropdown.contains(e.target)) {
            dropdown.classList.remove('dropdown-open');
            trigger.setAttribute('aria-expanded', 'false');
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            dropdown.classList.remove('dropdown-open');
            trigger.setAttribute('aria-expanded', 'false');
        }
    });
}

function applyTranslations(t) {
    if (!t) return;
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (t[key] !== undefined) {
            if (el.hasAttribute('data-i18n-html') || /<[a-z][\s\S]*>/i.test(t[key])) {
                el.innerHTML = t[key];
            } else {
                el.textContent = t[key];
            }
        }
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (t[key] !== undefined) el.placeholder = t[key];
    });
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
        const key = el.getAttribute('data-i18n-title');
        if (t[key] !== undefined) el.title = t[key];
    });
    document.querySelectorAll('[data-i18n-aria]').forEach(el => {
        const key = el.getAttribute('data-i18n-aria');
        if (t[key] !== undefined) el.setAttribute('aria-label', t[key]);
    });
}
window.applyTranslations = applyTranslations;


/* ─── PWA Service Worker ──────────────────────────────────────────────────── */

function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js', { scope: '/' })
            .then(() => console.log('SW registered'))
            .catch(err => console.warn('SW registration failed:', err));
    }
}


/* ─── Injected CSS helpers ────────────────────────────────────────────────── */

const _css = document.createElement('style');
_css.textContent = `
    /* Card lift-in animation */
    .format-card, .target-card, .model-card, .result-card,
    .compare-target-block, .history-card, .about-card {
        transition: opacity 0.45s ease, transform 0.45s ease;
    }
    .animate-in { opacity: 1 !important; transform: translateY(0) !important; }

    /* Form focus */
    .form-group.focused .form-label { color: #4ade80; }

    /* Invalid input */
    .form-input.input-invalid {
        border-color: var(--accent-red, #ef4444) !important;
        box-shadow: 0 0 0 3px rgba(239,68,68,0.15);
    }
    .range-error {
        display: none;
        font-size: 0.72rem;
        color: var(--accent-red, #ef4444);
        margin-top: 3px;
    }

    /* Hamburger → ✕ */
    .nav-toggle.active .toggle-bar:nth-child(1) { transform: translateY(7px)  rotate(45deg); }
    .nav-toggle.active .toggle-bar:nth-child(2) { opacity: 0; }
    .nav-toggle.active .toggle-bar:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

    /* Slider scrollbar hidden */
    #targetSlider::-webkit-scrollbar { display: none; }
    #targetSlider { -ms-overflow-style: none; scrollbar-width: none; }
`;
document.head.appendChild(_css);
