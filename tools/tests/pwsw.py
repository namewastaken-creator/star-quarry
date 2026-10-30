"""Offline copy (service worker): the game's offline copy must only ever be replaced by the real game.

Serves the repository root from its own small server that can misbehave on request, lets the service worker install,
then reloads the game while the server answers the game's address with: a Wi-Fi sign-in page (200 OK, not the
game), a server error (500), a redirect to a sign-in page, and no network at all. Each time the game must still load
(from the offline copy) and the offline copy must still be the game. Also opens another page on the site (the device
preview), which must not replace the offline copy either.
"""
import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # the repository root, served as the game
import sys,threading,functools
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
MODE={'m':''}
PORTAL=b'<!doctype html><title>Sign in to Wi-Fi</title><p>Sign in to continue</p>'
class H(SimpleHTTPRequestHandler):
  def log_message(self,*a):pass
  def do_GET(self):
    path=self.path.split('?')[0];m=MODE['m']
    if path in('/','/index.html')and m:
      if m=='portal':return self.send(200,PORTAL)
      if m=='error':return self.send(500,b'<!doctype html><title>500</title><p>Server error</p>')
      if m=='redirect':self.send_response(302);self.send_header('Location','/portal.html');self.end_headers();return
    if path=='/portal.html':return self.send(200,PORTAL)
    return super().do_GET()
  def send(self,code,body):
    self.send_response(code);self.send_header('Content-Type','text/html');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
srv=ThreadingHTTPServer(('127.0.0.1',int(sys.argv[1])),functools.partial(H,directory=ROOT));threading.Thread(target=srv.serve_forever,daemon=True).start()
errs=[]
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  ctx=b.new_context(viewport={'width':390,'height':844});pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));E=lambda js:pg.evaluate(js)
  u=f'http://localhost:{sys.argv[1]}/'
  pg.goto(u+'index.html');E("navigator.serviceWorker.ready.then(()=>0)");pg.reload();pg.wait_for_timeout(1500)
  print('controlled by the service worker',E("!!navigator.serviceWorker.controller"))
  copy=lambda:E("caches.match('./index.html').then(r=>r?r.text():'').then(t=>t.includes('starquarry_save_v1'))")
  game=lambda:E("typeof S==='object'&&!!S&&Array.isArray(S.planets)")
  print('offline copy is the game',copy())
  def case(name,mode=None,offline=False,url='index.html'):
    MODE['m']=mode or '';ctx.set_offline(offline)
    try:pg.goto(u+url,wait_until='load');pg.wait_for_timeout(2500);g=game()
    except Exception as e:g=False;print(' ',name,'load failed:',str(e).splitlines()[0])
    MODE['m']='';ctx.set_offline(False);pg.goto(u+'manifest.webmanifest');c=copy()
    print(f'{name}: game loaded {g}, offline copy still the game {c}')
    if not g:errs.append(f'{name}: the game did not load')
    if not c:errs.append(f'{name}: the offline copy was replaced by something that is not the game')
  case('Wi-Fi sign-in page','portal')
  case('server error','error')
  case('redirect to a sign-in page','redirect')
  case('no network',offline=True)
  case('folder address while offline',offline=True,url='')
  # another page on the site: loads as itself, and doesn't become the offline copy
  pg.goto(u+'src/artifact/preview.html?src=/index.html');pg.wait_for_timeout(1500)
  own=E("!!document.getElementById('phone')");print('device preview loads as itself',own)
  if not own:errs.append('the device preview page was replaced by the game')
  pg.goto(u+'manifest.webmanifest');c=copy();print('offline copy still the game after the preview',c)
  if not c:errs.append('opening the device preview replaced the offline copy')
  b.close()
srv.shutdown();print('errors',errs)
