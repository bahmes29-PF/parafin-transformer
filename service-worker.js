const CACHE_NAME = 'parafin-v1';
const urlsToCache = [
  '/',
  '/assets/icon.png',
  '/assets/spark_signage.png',
  '/assets/city_express_signage.PNG',
  '/assets/garner_signage.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => response || fetch(event.request))
  );
});
