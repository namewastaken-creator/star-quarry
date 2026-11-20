// Star Quarry offline support. The game page is always re-checked with the server when online (no-cache,
// so GitHub Pages' 10-minute browser cache can't hold back an update)
// and served from the cache when offline.
const CACHE='starquarry-163d4ecd6b';
const CORE=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png','./icon-maskable-512.png','./apple-touch-icon.png','./three-r187.min.js','./sky-2537c021.jpg','./css-core-d1d3381c.css','./css-orig-8a095cbf.css','./css-sp-19ce2c0d.css','./planet-0-1024-a2987cac.webp','./planet-0-512-68f465d6.webp','./planet-0-mask-8e749581.webp','./planet-1-1024-d2df37be.webp','./planet-1-512-fa9c27f8.webp','./planet-2-1024-eea097a1.webp','./planet-2-512-71c4f09f.webp','./planet-3-1024-0885b82a.webp','./planet-3-512-09053434.webp','./planet-4-1024-f174f8e5.webp','./planet-4-512-0317962e.webp','./planet-5-1024-7249ba1f.webp','./planet-5-512-b8a9e1d6.webp','./planet-6-1024-625f6a3d.webp','./planet-6-512-00620d1c.webp','./planet-6-mask-30f040b4.webp','./planet-7-1024-dd7617e4.webp','./planet-7-512-e44092d9.webp','./planet-7-mask-55caeeaf.webp','./planet-8-1024-105aeec6.webp','./planet-8-512-d5d8f0bc.webp','./planet-9-1024-cafa0a86.webp','./planet-9-512-6fc787c9.webp','./planet-10-1024-d164af75.webp','./planet-10-512-05c9cfa2.webp','./planet-10-mask-abc00594.webp','./planet-11-1024-d1083d20.webp','./planet-11-512-5ed3567a.webp','./planet-12-1024-b761ceb6.webp','./planet-12-512-e71cba9d.webp','./planet-13-1024-b42a7879.webp','./planet-13-512-f31f0dc3.webp','./planet-14-1024-7c8306ac.webp','./planet-14-512-3daf383b.webp','./planet-14-mask-dc5ac1e0.webp','./planet-15-1024-8c7504f4.webp','./planet-15-512-1373fac3.webp','./planet-16-1024-8a33e789.webp','./planet-16-512-1ab9a997.webp','./planet-17-1024-5bc645f9.webp','./planet-17-512-67d763c4.webp','./planet-18-1024-14515f53.webp','./planet-18-512-c19323ae.webp','./planet-18-mask-6a9e0779.webp','./planet-19-1024-be9478a9.webp','./planet-19-512-4b65d6dc.webp','./planet-20-1024-6283db61.webp','./planet-20-512-5d6838b3.webp','./planet-20-mask-3d5644cb.webp','./planet-21-1024-0bc94fc6.webp','./planet-21-512-f50386ec.webp','./planet-sun-1024-d194a869.webp'];
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
