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
  pg.goto(f'http://localhost:{sys.argv[1]}/index.html');pg.wait_for_timeout(4500);pg.click('#nmOk');E("S.tut=2;0");pg.wait_for_timeout(1000)
  # toasts: queue
  E("window.__T=[];new MutationObserver(()=>{const t=$('toast');__T.push([Math.round(performance.now()),t.textContent.slice(0,30)])}).observe($('toast'),{childList:true,characterData:true,subtree:true});toast('First message',3000);toast('Second message',3000);toast('+5 credits',1200);toast('+9 credits',1200);0")
  pg.wait_for_timeout(9000);T=E("__T");print('toasts',[(t[0]-T[0][0],t[1]) for t in T])
  # probes: 24 h away with Night Shift
  E("S.research.night=1;S.probe.out=null;S.probe.nextAt=Date.now()-24*3600e3;S.probe.st.returned=0;0")
  print('probes in 24h',E("probeTick(Date.now(),true).length"))
  # render: focus kept, time
  E("setTab('planet');0");pg.wait_for_timeout(800)
  E("const b=document.querySelector('#pbody button:not([disabled])');b.focus();window.__fb=b;0")
  E("S.cash+=1234;render(true);0");pg.wait_for_timeout(600)
  print('focus kept',E("document.activeElement===__fb&&document.body.contains(__fb)"))
  print('render ms',E("(()=>{let t=performance.now();for(let k=0;k<20;k++){S.cash+=k+1;render(true)}return ((performance.now()-t)/20).toFixed(2)})()"))
  E("(()=>{lastHTML='';const v=viewPlanet();let t=performance.now();for(let k=0;k<20;k++)pbody.innerHTML=v;window.__old=((performance.now()-t)/20).toFixed(2)})();render(true);0");print('old innerHTML ms',E("__old"))
  # warp clears plans
  E("tune[0]={plan:{m:2}};perkPick[1]=0;S.planets[WARP_AT].u=1;S.runEarned=1e9;render(true);setTab('warp');0");pg.wait_for_timeout(500)
  E("arm={k:'warp',until:Date.now()+4000};document.querySelector('[data-act=warp]').click();0");pg.wait_for_timeout(800)
  print('after warp',E("JSON.stringify([Object.keys(tune).length,Object.keys(perkPick).length,PR])"))
  # offline with planetFlow
  E("S.planets[1].u=1;crewState(S.planets[1]).teams=[{}];0")
  print('offline',E("(()=>{const c=S.cash;offline(3600,false);return Math.round(S.cash-c)})()"))
  for t in ('planet','market','smelter','research','probe','events','warp'):
    E(f"setTab('{t}');0");pg.wait_for_timeout(500)
srv.kill();print('errors',errs)
