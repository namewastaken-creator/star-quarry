import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # the repository root, served as the game
OUT=_os.environ.get('SQ_OUT',_os.path.join(ROOT,'out'));_os.makedirs(OUT,exist_ok=True)  # screenshots (git-ignored)
import subprocess,time,sys
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server',sys.argv[1],'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page()
  errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));E=lambda js:pg.evaluate(js)
  pg.goto(f'http://localhost:{sys.argv[1]}/index.html');pg.wait_for_timeout(4500);pg.click('#nmOk')
  st="(()=>{const t=cam.obj==='probe'?probeObj.position:cam.obj==='station'?STP:null;let px=null;if(t){const v=t.clone().project(camera);px=[Math.round((v.x+1)/2*innerWidth),Math.round((1-v.y)/2*innerHeight)]}const zb=document.querySelector('#pbody .pzname');return JSON.stringify({obj:cam.obj,zl:cam.zl,tr:cam.tr,st:cam.station,pr:cam.probe,at:px,btn:zb?zb.textContent+' '+Math.round(zb.getBoundingClientRect().width):null,open:!sheet.classList.contains('collapsed')})})()"
  E("S.tut=2;setTab('research');sheet.classList.contains('collapsed')&&toggleSheet();0");pg.wait_for_timeout(500)
  for k in range(3):
    E("document.querySelector('#pbody .pzname').click()");pg.wait_for_timeout(1300);print('station step',k+1,E(st))
    if k==0: E("toggleSheet()");pg.wait_for_timeout(1500);print(' closed     ',E(st));pg.screenshot(path=OUT+'/st_l1.png');E("toggleSheet()");pg.wait_for_timeout(900)
  # wheel locked + drag turns
  E("document.querySelector('#pbody .pzname').click()");pg.wait_for_timeout(1200);t0=E("cam.theta");pg.mouse.move(195,150);pg.mouse.wheel(0,500);pg.wait_for_timeout(300)
  pg.mouse.move(150,150);pg.mouse.down();pg.mouse.move(250,150,steps=8);pg.mouse.up();pg.wait_for_timeout(400);print('station after wheel+drag',E(st),'theta moved',round(E("cam.theta")-t0,2))
  # probe: launch it
  E("S.probe.nextAt=Date.now()-1;0");pg.wait_for_timeout(3000)
  E("setTab('probe');0");pg.wait_for_timeout(600)
  print('probe out',E("!!S.probe.out"),'name',E("(document.querySelector('#pbody .pzname')||{}).getAttribute&&document.querySelector('#pbody .pzname').getAttribute('aria-label')"))
  for k in range(3):
    E("document.querySelector('#pbody .pzname')&&document.querySelector('#pbody .pzname').click()");pg.wait_for_timeout(1500);print('probe step',k+1,E(st))
  E("document.querySelector('#pbody .pzname').click()");pg.wait_for_timeout(800)
  E("S.probe.out.at=Date.now()-ECON.PROBE_FLY*1000-10;0");pg.wait_for_timeout(3000);print('after probe docks',E(st))
  print('errs',errs)
srv.kill()
