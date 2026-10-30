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
  col="[...document.querySelectorAll('.tab')].map(b=>b.dataset.tab+':'+getComputedStyle(b).color+(b.classList.contains('alert')?'*':'')).join(' ')"
  pg.wait_for_timeout(1500);print('start',E(col))
  E("S.probe.nextAt=Date.now()-1;0");pg.wait_for_timeout(2500);print('out?',E("!!S.probe.out"),E(col))
  E("setTab('probe');0");pg.wait_for_timeout(1500);print('on probe tab',E(col))
  pg.screenshot(path=OUT+'/tab1.png',clip={'x':0,'y':0,'width':390,'height':844})
  E("S.probe.out.at=Date.now()-1e8;0");pg.wait_for_timeout(2500);print('back?',E("!!S.probe.out"),E(col))
  E("S.cash+=1e9;setTab('market');0");pg.wait_for_timeout(2500);print('cash',E(col))
  pg.screenshot(path=OUT+'/tab2.png')
srv.kill();print('errors',errs)
