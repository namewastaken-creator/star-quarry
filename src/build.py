"""Build Star Quarry for the web and for Android from src/game.html.

  python3 -I src/build.py              build (warns if gameplay changed but the user guide didn't; see guidecheck.py)
  python3 -I src/build.py --guide-ok   build, recording that the gameplay change doesn't affect the user guide

Outputs (paths relative to the repository root; runs from any clone, from any folder):
  index.html, sw.js, version.json, manifest.webmanifest, three-r128.min.js, sky-<hash>.jpg
                                                    the installable web game, served by GitHub Pages from main
  android/app/src/main/assets/index.html            the Android WebView app's game (one file, works offline)
  android/app/build.gradle.kts                      versionCode/versionName kept in step with the game
  dist/StarQuarry-Android.zip, dist/StarQuarry-Web.zip   handy zips of both (git-ignored)
"""
import re, os, json, zipfile, time, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src', 'game.html')
THREE = os.path.join(ROOT, 'src', 'vendor', 'three-r128.min.js')
ANDROID = os.path.join(ROOT, 'android')
DIST = os.path.join(ROOT, 'dist')
os.makedirs(DIST, exist_ok=True)
CDN = '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'

# always UTF-8 with LF line endings, so a build on Windows (whose default is cp1252 and CRLF) gives the same files and
# hashes as anywhere else
def read(path): return open(path, encoding='utf-8').read()
def write(path, text): open(path, 'w', encoding='utf-8', newline='\n').write(text)

# warn if gameplay changed without the user guide being updated (see guidecheck.py)
import sys
sys.path.insert(0, os.path.join(ROOT, 'src'))
import guidecheck
GUIDE_OK = guidecheck.check('--guide-ok' in sys.argv)
src = read(SRC)
three = read(THREE)
body = src.replace(CDN, '<script>' + three + '</script>')
body = re.sub(r'window\.__SQ=\{.*?\};\n', '', body)
cut = body.index('</style>') + len('</style>')
head_part, rest = body[:cut], body[cut:]
# pinch-zoom of the page is allowed for low-vision players (code review item 18); the map's own pinch still zooms the
# map because the canvas takes its touches (touch-action: none)
VIEWPORT = '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'

def zipdir(folder, zpath, arcroot):
    if os.path.exists(zpath): os.remove(zpath)
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for dp, _, fns in os.walk(folder):
            if '/.gradle' in dp or '/build' in dp: continue
            fns = [f for f in fns if f not in ('local.properties',) and not f.endswith(('.jks', '.keystore'))]
            for fn in fns:
                full = os.path.join(dp, fn)
                z.write(full, os.path.join(arcroot, os.path.relpath(full, folder)))

# ---------- Android ----------
android = f'<!doctype html><html lang="en"><head>{VIEWPORT}{head_part}</head><body>{rest}</body></html>'
os.makedirs(f'{ANDROID}/app/src/main/assets', exist_ok=True)
write(f'{ANDROID}/app/src/main/assets/index.html', android)

# ---------- Web (installable, full screen, offline) ----------
WEB = ROOT  # the web game is built straight into the repository root (GitHub Pages serves it from there)
pwa_head = (
    '<meta name="theme-color" content="#05060d">'
    '<meta name="description" content="A 3D idle space-mining game. No ads, no purchases.">'
    '<link rel="manifest" href="manifest.webmanifest">'
    '<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">'
    '<link rel="apple-touch-icon" href="apple-touch-icon.png">'
    '<meta name="mobile-web-app-capable" content="yes">'
    '<meta name="apple-mobile-web-app-capable" content="yes">'
    '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">'
    '<meta name="apple-mobile-web-app-title" content="Star Quarry">'
)
sw_reg = ("<script>if('serviceWorker' in navigator&&(location.protocol==='https:'||location.hostname==='localhost'))"
          "window.addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}));</script>")
# The web build keeps Three.js and the sky picture as separate files with names that change only when they do, cached
# by the service worker (code review item 16), so a daily update downloads the game script, not 0.7 MB that never
# changes. The Android app keeps everything in one file (it ships offline anyway).
import base64
web_head, web_rest = head_part, rest
three_tag = '<script>' + three + '</script>'
web_head = web_head.replace(three_tag, '<script src="three-r128.min.js"></script>'); web_rest = web_rest.replace(three_tag, '<script src="three-r128.min.js"></script>')
write(f'{WEB}/three-r128.min.js', three)
m = re.search(r'const SKY_IMG="data:image/jpeg;base64,([^"]+)"', web_rest) or re.search(r'const SKY_IMG="data:image/jpeg;base64,([^"]+)"', web_head)
SKY = None
if m:
    data = base64.b64decode(m.group(1)); SKY = f'sky-{hashlib.sha1(data).hexdigest()[:8]}.jpg'
    for f in os.listdir(WEB):
        if f.startswith('sky-') and f.endswith('.jpg') and f != SKY: os.remove(f'{WEB}/{f}')
    open(f'{WEB}/{SKY}', 'wb').write(data)
    web_head = web_head.replace(m.group(0), f'const SKY_IMG="{SKY}"'); web_rest = web_rest.replace(m.group(0), f'const SKY_IMG="{SKY}"')
assert 'three-r128.min.js' in web_head + web_rest
web = f'<!doctype html><html lang="en"><head>{VIEWPORT}{pwa_head}{web_head}</head><body>{web_rest}{sw_reg}</body></html>'
write(f'{WEB}/index.html', web)

manifest = {
    "name": "Star Quarry", "short_name": "Star Quarry",
    "description": "A 3D idle space-mining game. No ads, no purchases.",
    "start_url": "./", "scope": "./", "id": "./",
    "display": "fullscreen", "display_override": ["fullscreen", "standalone"],
    "orientation": "portrait", "background_color": "#05060d", "theme_color": "#05060d",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
    ]
}
write(f'{WEB}/manifest.webmanifest', json.dumps(manifest, indent=2))

version = hashlib.sha1(web.encode()).hexdigest()[:10]
sw = f"""// Star Quarry offline support. The game page is always re-checked with the server when online (no-cache,
// so GitHub Pages' 10-minute browser cache can't hold back an update)
// and served from the cache when offline.
const CACHE='starquarry-{version}';
const CORE=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png','./icon-maskable-512.png','./apple-touch-icon.png','./three-r128.min.js'{(",'./"+SKY+"'") if SKY else ''}];
self.addEventListener('install',e=>{{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()))}});
self.addEventListener('activate',e=>{{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))}});
// The game's own address (the folder and index.html) is the only page kept for offline play. A response replaces
// that copy only when it really is the game: a 200 for that address (not a redirect, so not a Wi-Fi sign-in page), HTML,
// with the game's code in it. Anything else (a 404 or 5xx mid-deploy, a sign-in page, no network) gets the offline
// copy when there is one. Other pages on the site (the device preview, say) aren't touched.
const SCOPE=new URL(self.registration.scope).pathname,GAME=[SCOPE,SCOPE+'index.html'],MARK='starquarry_save_v1';
async function realGame(r){{if(!r||!r.ok||r.redirected||!(r.headers.get('content-type')||'').includes('text/html'))return false;
  try{{return (await r.clone().text()).includes(MARK)}}catch(e){{return false}}}}
self.addEventListener('fetch',e=>{{
  const req=e.request;if(req.method!=='GET')return;
  const url=new URL(req.url),same=url.origin===location.origin;
  // update checks always go to the network so a new version is never hidden by the cache
  if(url.pathname.endsWith('/version.json'))return;
  if(same&&GAME.includes(url.pathname)){{
    e.respondWith((async()=>{{let r=null;try{{r=await fetch(req,{{cache:'no-cache'}})}}catch(err){{}}
      if(await realGame(r)){{const copy=r.clone();e.waitUntil(caches.open(CACHE).then(c=>c.put('./index.html',copy)));return r}}
      return (await caches.match('./index.html'))||r||Response.error()}})());return}}
  if(req.mode==='navigate'||(same&&url.pathname.endsWith('.html')))return;
  // icons, manifest, Three.js, the sky and web fonts: cache first, refreshed in the background, and only a
  // successful response is ever stored
  e.respondWith(caches.match(req).then(hit=>{{
    const net=fetch(req).then(r=>{{if(r&&r.ok&&!r.redirected){{const copy=r.clone();caches.open(CACHE).then(c=>c.put(req,copy))}}return r}}).catch(()=>hit||Response.error());
    return hit||net}}));
}});
"""
write(f'{WEB}/sw.js', sw)
# version.json: what the running game compares itself against when checking for updates
_vm = re.search(r"const APP_VER=\{name:'([^']+)',n:(\d+)\};", src)
APP_NAME, APP_N = _vm.group(1), int(_vm.group(2))
_cl = json.loads(read(os.path.join(ROOT, 'src', 'changelog.json')))
_notes = '; '.join(c['t'] for c in _cl if c.get('v') == APP_NAME)
# the last 40 versioned changes, so a game several versions behind can list everything new and see if any was important
_log = [{"v": c["v"], "t": c["t"], **({"imp": True} if c.get("imp") else {})} for c in _cl if c.get("v")][:40]
write(f'{WEB}/version.json', json.dumps({"name": APP_NAME, "n": APP_N, "notes": _notes, "log": _log}))
# keep the Android app's version in step (versionCode must rise with each build)
_g = f'{ANDROID}/app/build.gradle.kts'
_gs = read(_g)
_gs = re.sub(r'versionCode = \d+', f'versionCode = {max(1, APP_N)}', _gs)
_gs = re.sub(r'versionName = "[^"]*"', f'versionName = "{APP_NAME}"', _gs)
write(_g, _gs)
zipdir(ANDROID, f'{DIST}/StarQuarry-Android.zip', 'StarQuarryAndroid')
# the web zip holds just the published files (not the repository's sources and tools)
WEB_FILES = ['index.html', 'sw.js', 'version.json', 'manifest.webmanifest', 'three-r128.min.js', 'icon-192.png', 'icon-512.png',
             'icon-maskable-512.png', 'apple-touch-icon.png'] + ([SKY] if SKY else [])
if os.path.exists(f'{DIST}/StarQuarry-Web.zip'): os.remove(f'{DIST}/StarQuarry-Web.zip')
with zipfile.ZipFile(f'{DIST}/StarQuarry-Web.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for fn in WEB_FILES: z.write(os.path.join(WEB, fn), os.path.join('StarQuarryWeb', fn))
print('built', APP_NAME, version, 'web index', round(len(web)/1e6, 2), 'MB')
