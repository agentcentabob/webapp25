const CACHE_NAME = "urbannotes-cache2";
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/manifest.json',
// icons
  '/static/icons/account_in.png',
  '/static/icons/account_out.png',
  '/static/icons/logo_black.png',
  '/static/icons/logo_white.png',
  '/static/icons/full_logo_black.png',
// home page images
  '/static/images/amsterdam_lr.jpg',
  '/static/images/parallel_ferries.jpg',
  '/static/images/shinjuku_street.jpg',
  '/static/images/westmead_lr.jpg',
];

// install event
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
      .then(() => self.skipWaiting())  // activates immediately
  );
});

// fetch event
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});

// activate event
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())  // take control immediately
  );
});