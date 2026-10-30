import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # the repository root, served as the game
OUT=_os.environ.get('SQ_OUT',_os.path.join(ROOT,'out'));_os.makedirs(OUT,exist_ok=True)  # screenshots (git-ignored)
import subprocess,time,sys
from playwright.sync_api import sync_playwright
srv=subprocess.Popen([sys.executable,'-m','http.server',sys.argv[1],'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page()
  errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));E=lambda js:pg.evaluate(js)
  pg.goto(f'http://localhost:{sys.argv[1]}/index.html');pg.wait_for_timeout(4500);pg.click('#nmOk')
  E("S.tut=2;const p=S.planets[1];p.u=true;crewState(p).teams=[{}];crewVer++;refreshWorld();setTab('planet');sheet.classList.contains('collapsed')&&toggleSheet();0");pg.wait_for_timeout(800)
  st=lambda:E("JSON.stringify({focus:cam.focus,zl:cam.zl,obj:cam.obj||'',sel:S.sel,py:Math.round((1-W[Math.max(0,cam.focus)].pos.clone().project(camera).y)/2*innerHeight),px:Math.round((W[Math.max(0,cam.focus)].pos.clone().project(camera).x+1)/2*innerWidth)})")
  chip=lambda i:E(f"document.querySelector('[data-act=\"sel\"][data-p=\"{i}\"]').click()")
  chip(1);pg.wait_for_timeout(1800);print('galaxy, tap Vesk  ',st())
  chip(0);pg.wait_for_timeout(1800);print('tap Cinder (L1)   ',st())
  E("document.querySelector('.pzname').click()");pg.wait_for_timeout(1000);chip(1);pg.wait_for_timeout(1800);print('L2, tap Vesk      ',st())
  E("cam.focus=-1;recenter();0");pg.wait_for_timeout(900);chip(1);pg.wait_for_timeout(120);chip(1);pg.wait_for_timeout(1800);print('galaxy, double-tap',st())
  chip(1);pg.wait_for_timeout(120);chip(1);pg.wait_for_timeout(1800);print('L1, double-tap    ',st())
  E("zoomStepObj('station');0");pg.wait_for_timeout(800);E("setTab('planet');0");pg.wait_for_timeout(500);chip(0);pg.wait_for_timeout(1500);print('station L1, tap Cinder',st())
  print('errs',errs)
srv.kill()
