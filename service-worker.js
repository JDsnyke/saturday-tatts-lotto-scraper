const CACHE_NAME = 'australian-lottery-lab-bulma-v1';
const BULMA_URL = 'https://cdn.jsdelivr.net/npm/bulma@1.0.4/css/bulma.min.css';
const LUCIDE_URL = 'https://unpkg.com/lucide@1.33.0/dist/umd/lucide.js';
const STATIC_ASSETS = [
  './',
  './index.html',
  './benchmark.html',
  './games.html',
  './assets/ui.js',
  './assets/app.js',
  './assets/benchmark.js',
  './assets/certificates.js',
  './assets/games.js',
  './assets/favicon.svg',
  './assets/site.webmanifest',
  './assets/lotto_stats.json',
  './assets/data_provenance.json',
  './assets/game_catalog.json',
  BULMA_URL,
  LUCIDE_URL,
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  const isLocal = url.origin === self.location.origin;
  const isLibrary = event.request.url === BULMA_URL || event.request.url === LUCIDE_URL;
  if (!isLocal && !isLibrary) return;

  const isData = isLocal && (
    url.pathname.endsWith('/assets/lotto_stats.json') ||
    url.pathname.endsWith('/assets/data_provenance.json') ||
    url.pathname.endsWith('/assets/game_catalog.json')
  );

  if (isData) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy));
          return response;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then(cached => cached || fetch(event.request).then(response => {
      const copy = response.clone();
      caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy));
      return response;
    }))
  );
});
