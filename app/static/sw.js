/**
 * Cricket Predictor Pro — Service Worker
 * Caches static assets for offline support and fast repeat visits.
 */

const CACHE_NAME = 'cpp-v1';
const STATIC_ASSETS = [
    '/',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/manifest.json',
    '/static/favicon.svg',
    '/static/img/logo.svg',
    '/static/img/hero_poster.jpg',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap',
];

/* ── Install: cache static assets ──────────────────────────────────────────── */
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(STATIC_ASSETS.map(url => {
                return new Request(url, { cache: 'reload' });
            })).catch(() => {
                // Silently fail individual assets
            });
        })
    );
    self.skipWaiting();
});

/* ── Activate: clear old caches ─────────────────────────────────────────────── */
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
        )
    );
    self.clients.claim();
});

/* ── Fetch: cache-first for static, network-first for API/HTML ─────────────── */
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET and cross-origin (except fonts)
    if (request.method !== 'GET') return;

    // Network-first for API endpoints and HTML pages
    if (url.pathname.startsWith('/api/') || url.pathname === '/health') {
        event.respondWith(
            fetch(request).catch(() => new Response(JSON.stringify({ error: 'Offline' }), {
                headers: { 'Content-Type': 'application/json' }
            }))
        );
        return;
    }

    // Cache-first for static files
    if (url.pathname.startsWith('/static/') || url.hostname.includes('fonts.g')) {
        event.respondWith(
            caches.match(request).then(cached => cached || fetch(request).then(resp => {
                const clone = resp.clone();
                caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
                return resp;
            }))
        );
        return;
    }

    // Stale-while-revalidate for HTML pages
    event.respondWith(
        caches.match(request).then(cached => {
            const fetchPromise = fetch(request).then(resp => {
                caches.open(CACHE_NAME).then(cache => cache.put(request, resp.clone()));
                return resp;
            });
            return cached || fetchPromise;
        })
    );
});
