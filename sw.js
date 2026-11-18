// Star Quarry offline support. The game page is always re-checked with the server when online (no-cache,
// so GitHub Pages' 10-minute browser cache can't hold back an update)
// and served from the cache when offline.
const CACHE='starquarry-4e96e66cd4';
const CORE=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png','./icon-maskable-512.png','./apple-touch-icon.png','./three-r187.min.js','./sky-2537c021.jpg','./css-core-ff92a1b1.css','./css-orig-761f07e9.css','./css-sp-20a5d7d6.css','./planet-0-1024-6c327be8.webp','./planet-0-512-937ff0d6.webp','./planet-0-mask-221ee4f5.webp','./planet-1-1024-5c94ea4f.webp','./planet-1-512-1bab9bbb.webp','./planet-2-1024-9c1a4462.webp','./planet-2-512-ff239527.webp','./planet-3-1024-0885b82a.webp','./planet-3-512-09053434.webp','./planet-4-1024-f174f8e5.webp','./planet-4-512-0317962e.webp','./planet-5-1024-4d04c838.webp','./planet-5-512-2fd7e09e.webp','./planet-6-1024-625f6a3d.webp','./planet-6-512-00620d1c.webp','./planet-6-mask-30f040b4.webp','./planet-7-1024-dd7617e4.webp','./planet-7-512-e44092d9.webp','./planet-7-mask-55caeeaf.webp','./planet-8-1024-440c68d0.webp','./planet-8-512-4dfb9425.webp','./planet-9-1024-cafa0a86.webp','./planet-9-512-6fc787c9.webp','./planet-10-1024-313ccc06.webp','./planet-10-512-40463e9e.webp','./planet-10-mask-bd49b8bb.webp','./planet-11-1024-d1083d20.webp','./planet-11-512-5ed3567a.webp','./planet-12-1024-b761ceb6.webp','./planet-12-512-e71cba9d.webp','./planet-13-1024-b42a7879.webp','./planet-13-512-f31f0dc3.webp','./planet-14-1024-7c8306ac.webp','./planet-14-512-3daf383b.webp','./planet-14-mask-dc5ac1e0.webp','./planet-15-1024-239cf237.webp','./planet-15-512-c033b8f0.webp','./planet-16-1024-8a33e789.webp','./planet-16-512-1ab9a997.webp','./planet-17-1024-5bc645f9.webp','./planet-17-512-67d763c4.webp','./planet-18-1024-14515f53.webp','./planet-18-512-c19323ae.webp','./planet-18-mask-6a9e0779.webp','./planet-19-1024-408135da.webp','./planet-19-512-4a6a55a6.webp','./planet-20-1024-6283db61.webp','./planet-20-512-5d6838b3.webp','./planet-20-mask-3d5644cb.webp','./planet-21-1024-0bc94fc6.webp','./planet-21-512-f50386ec.webp'];
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
  // icons, manifest, Three.js, the sky, the stylesheets and web fonts: cache first, refreshed in the background, and only a
  // successful response is ever stored
  e.respondWith(caches.match(req).then(hit=>{
    const net=fetch(req).then(r=>{if(r&&r.ok&&!r.redirected){const copy=r.clone();caches.open(CACHE).then(c=>c.put(req,copy))}return r}).catch(()=>hit||Response.error());
    return hit||net}));
});
