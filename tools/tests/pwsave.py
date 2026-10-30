import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # the repository root, served as the game
OUT=_os.environ.get('SQ_OUT',_os.path.join(ROOT,'out'));_os.makedirs(OUT,exist_ok=True)  # screenshots (git-ignored)
import subprocess,time,sys
from playwright.sync_api import sync_playwright
srv=subprocess.Popen([sys.executable,'-m','http.server',sys.argv[1],'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
errs=[]
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  ctx=b.new_context(viewport={'width':390,'height':844},service_workers='block');pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));E=lambda js:pg.evaluate(js)
  u=f'http://localhost:{sys.argv[1]}/index.html'
  pg.goto(u);pg.wait_for_timeout(1500)
  for case,val in [('corrupt','{not json'),('newer','{"v":2,"x":1}')]:
    pg.goto(u.replace('index.html','manifest.webmanifest'));pg.wait_for_timeout(300)
    E(f"localStorage.clear();localStorage.setItem('starquarry_save_v1',{val!r});0");pg.goto(u);pg.wait_for_timeout(9000)
    print(case,E("JSON.stringify({bak:localStorage.getItem('starquarry_save_v1_bak'),main:(localStorage.getItem('starquarry_save_v1')||'').slice(0,20),block:SAVE_BLOCK,toast:$('toast').textContent.slice(0,60)})"))
  E("localStorage.clear();0");pg.reload();pg.wait_for_timeout(6000)
  E("const o=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k==='starquarry_save_v1')throw new Error('quota');return o.call(this,k,v)};save();0");pg.wait_for_timeout(500)
  print('quota toast',E("$('toast').textContent.slice(0,50)"))
srv.kill();print('errors',errs)
