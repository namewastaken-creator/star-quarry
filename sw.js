// Star Quarry offline support. The game page is always re-checked with the server when online (no-cache,
// so GitHub Pages' 10-minute browser cache can't hold back an update)
// and served from the cache when offline.
const CACHE='starquarry-62f6516cec';
const CORE=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png','./icon-maskable-512.png','./apple-touch-icon.png','./three-r128.min.js','./sky-2537c021.jpg'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{
  const req=e.request;if(req.method!=='GET')return;
  const url=new URL(req.url);
  // update checks always go to the network so a new version is never hidden by the cache
  if(url.pathname.endsWith('/version.json'))return;
  if(req.mode==='navigate'||(url.origin===location.origin&&url.pathname.endsWith('.html'))){
    // only a good response replaces the offline copy; an error page (a 404 or 5xx mid-deploy) never does, and the
    // offline copy is served instead when there is one
    e.respondWith(fetch(req,{cache:'no-cache'}).then(r=>{if(r.ok){const copy=r.clone();caches.open(CACHE).then(c=>c.put('./index.html',copy));return r}
      return caches.match('./index.html').then(hit=>hit||r)}).catch(()=>caches.match('./index.html')));return}
  // icons, manifest and web fonts: cache first, refresh in the background
  e.respondWith(caches.match(req).then(hit=>{
    const net=fetch(req).then(r=>{if(r&&(r.ok||r.type==='opaque')){const copy=r.clone();caches.open(CACHE).then(c=>c.put(req,copy))}return r}).catch(()=>hit);
    return hit||net}));
});
