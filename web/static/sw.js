/*
 * Manatee Creek Sheep — Service Worker
 *
 * Caching strategy:
 *   - App shell (HTML, CSS, fonts): Cache-first, update in background
 *   - API data: Network-first, fall back to cache (stale data > no data on a farm)
 *   - Never cache: POST requests, robots.txt, .well-known
 */

const CACHE_NAME = 'mcs-v1';
const SHELL_CACHE = 'mcs-shell-v1';
const DATA_CACHE = 'mcs-data-v1';

// App shell — cache on install
const SHELL_FILES = [
  '/',
  '/static/manifest.json',
  '/static/icon-192.svg',
  '/static/icon-512.svg',
];

// ─── Install: pre-cache app shell ───
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(SHELL_CACHE).then(cache => {
      return cache.addAll(SHELL_FILES);
    }).then(() => self.skipWaiting())
  );
});

// ─── Activate: clean old caches ───
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(k => k !== SHELL_CACHE && k !== DATA_CACHE)
            .map(k => caches.delete(k))
      );
    }).then(() => self.clients.claim())
  );
});

// ─── Fetch: routing strategy ───
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Never cache POST requests
  if (event.request.method !== 'GET') return;

  // Never cache anti-indexing files
  if (url.pathname === '/robots.txt' ||
      url.pathname.startsWith('/.well-known')) {
    return;
  }

  // API requests: network-first, cache fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(event.request, DATA_CACHE));
    return;
  }

  // App shell & static: cache-first, network fallback
  event.respondWith(cacheFirst(event.request, SHELL_CACHE));
});

// ─── Cache-first strategy ───
async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) {
    // Update cache in background
    fetch(request).then(response => {
      if (response.ok) {
        caches.open(cacheName).then(cache => cache.put(request, response));
      }
    }).catch(() => {});
    return cached;
  }
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    return new Response('Offline — no cached version available', {
      status: 503,
      headers: { 'Content-Type': 'text/plain' },
    });
  }
}

// ─── Network-first strategy ───
async function networkFirst(request, cacheName) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    const cached = await caches.match(request);
    if (cached) {
      return cached;
    }
    return new Response(JSON.stringify({ error: 'Offline — no cached data' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
