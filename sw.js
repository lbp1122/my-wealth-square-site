// The public site is now a concept/marketing website rather than an installable
// calculator. This worker removes caches from the old Balance Sheet Square PWA
// and unregisters itself so returning visitors receive the current website.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map((key) => caches.delete(key)));
    await self.registration.unregister();
    await self.clients.claim();
  })());
});
