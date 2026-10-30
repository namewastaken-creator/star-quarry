import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # the repository root, served as the game
OUT=_os.environ.get('SQ_OUT',_os.path.join(ROOT,'out'));_os.makedirs(OUT,exist_ok=True)  # screenshots (git-ignored)
import subprocess,time,sys
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server',sys.argv[1],'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
errs=[]
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page();pg.on('pageerror',lambda e:errs.append(str(e)));E=lambda js:pg.evaluate(js)
  pg.goto(f'http://localhost:{sys.argv[1]}/index.html');pg.wait_for_timeout(4500);pg.click('#nmOk');E("S.tut=2;0")
  E("focusPlanet(0,3);0");pg.wait_for_timeout(2500)
  st="JSON.stringify([+cam.r.toFixed(1),+cam.phi.toFixed(2),+cam.target.length().toFixed(1)])"
  print('close-up',E(st))
  E("window.__s=[];const t0=performance.now();(function f(){__s.push([Math.round(performance.now()-t0),+cam.r.toFixed(1),+cam.target.length().toFixed(1)]);if(performance.now()-t0<2400)requestAnimationFrame(f)})();0")
  pg.click('#center');pg.wait_for_timeout(2700)
  s=E("__s");print('samples',[x for i,x in enumerate(s) if i%max(1,len(s)//10)==0][:12])
  pg.wait_for_timeout(600);print('end',E(st),'lit',E("$('center').classList.contains('lit')"),E('JSON.stringify([cam.focus,cam.obj,cam.follow,cam.tt.length(),cam.tr,fitDistance(),cam.phi])'))
  E("focusPlanet(2,2);0");pg.wait_for_timeout(2000);pg.click('#center');pg.wait_for_timeout(400)
  pg.mouse.move(195,200);pg.mouse.down();pg.mouse.move(240,210);pg.mouse.up();pg.wait_for_timeout(300);print('glide stopped by touch',E("cam.glide===null"))
srv.kill();print('errors',errs)
