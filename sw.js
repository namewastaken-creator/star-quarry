// Star Quarry offline support. The game page is always re-checked with the server when online (no-cache,
// so GitHub Pages' 10-minute browser cache can't hold back an update)
// and served from the cache when offline.
const CACHE='starquarry-a645a43447';
const CORE=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png','./icon-maskable-512.png','./apple-touch-icon.png','./three-r128.min.js','./sky-2537c021.jpg'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
// The game's own address (the folder and index.html) is the only page kept for offline play. A response replaces
// that copy only when it really is the game: a 200 for that address (not a redirect, so not a Wi-Fi sign-in page), HTML,
// with the game's code in it. Anything else (a 404 or 5xx mid-deploy, a sign-in page, no network) gets the offline
// copy when there is one. Other pages on the site (the device preview, say) aren't touched.
const SCOPE=new URL(self.registration.scope).pathname,GAME=[SCOPE,SCOPE+'index.html'],MARK='starquarry_save_v1';
async function realGame(r){if(!r||!r.ok||r.redirected||!(r.headers.get('content-type')||'').includes('text/html'))return false;
  try{return (await r.clone().text()).includes(MARK)}catch(e){return false}}
self.addEventListener('fetch',e=>{
  const req=e.request;if(req.method!=='GET')return;
  const url=new URL(req.url),same=url.origin===location.origin;
  // update checks always go to the network so a new version is never hidden by the cache
  if(url.pathname.endsWith('/version.json'))return;
  if(same&&GAME.includes(url.pathname)){
    e.respondWith((async()=>{let r=null;try{r=await fetch(req,{cache:'no-cache'})}catch(err){}
      if(await realGame(r)){const copy=r.clone();e.waitUntil(caches.open(CACHE).then(c=>c.put('./index.html',copy)));return r}
      return (await caches.match('./index.html'))||r||Response.error()})());return}
  if(req.mode==='navigate'||(same&&url.pathname.endsWith('.html')))return;
  // icons, manifest, Three.js, the sky and web fonts: cache first, refreshed in the background, and only a
  // successful response is ever stored
  e.respondWith(caches.match(req).then(hit=>{
    const net=fetch(req).then(r=>{if(r&&r.ok&&!r.redirected){const copy=r.clone();caches.open(CACHE).then(c=>c.put(req,copy))}return r}).catch(()=>hit||Response.error());
    return hit||net}));
});
