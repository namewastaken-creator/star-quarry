import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # the repository root, served as the game
OUT=_os.environ.get('SQ_OUT',_os.path.join(ROOT,'out'));_os.makedirs(OUT,exist_ok=True)  # screenshots (git-ignored)
import subprocess,time,sys,json
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server',sys.argv[1],'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
errs=[]
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page();pg.on('pageerror',lambda e:errs.append(str(e)));E=lambda js:pg.evaluate(js)
  pg.goto(f'http://localhost:{sys.argv[1]}/index.html');pg.wait_for_timeout(4500);pg.click('#nmOk')
  E("""S.tut=2;RESEARCH.forEach(r=>S.research[r.id]=1);S.planets.forEach((p,i)=>{p.u=true;crewState(p);p.teams=[{},{},{}];p.pts=65;p.bought=65;p.al={m:30,s:15,c:15,v:5};Object.keys(PROGRAMS).forEach(id=>p.done[id]=1)});crewVer++;refreshWorld();0""")
  E("""window.__mx=0;window.__n=0;const pj=window.parkJob;window.parkJob=function(){const t=performance.now();pj();const d=performance.now()-t;__n++;if(d>__mx)__mx=d};0""")
  t=time.time()
  E("PR=null;PRJ=null;0")
  for k in range(240):
    pg.wait_for_timeout(500)
    if E("parkRankReady()"):break
  print('ready after',round(time.time()-t,1),'s; frames',E("__n"),'max parkJob ms',round(E("__mx"),1))
  # compare with the one-shot evaluation
  print('compare',E("(()=>{const base=parkBase();const a=PR.list.slice(0,3).map(e=>[e.x,+e.gain.toFixed(4)]);const b=PR.list.slice(0,3).map(e=>{const q=parkEval(e.x,base);return [q.x,+q.gain.toFixed(4)]});return JSON.stringify([a,b])})()"))
  # change points: should start a new ranking
  E("__mx=0;S.planets[3].al.m-=1;S.planets[3].al.s+=1;0");pg.wait_for_timeout(300);print('stale after point move',not E("parkRankReady()"))
  for k in range(240):
    pg.wait_for_timeout(500)
    if E("parkRankReady()"):break
  print('re-ranked, max ms',round(E("__mx"),1))
  E("setTab('research');0");pg.wait_for_timeout(1000);print('card',E("(document.querySelector('.bprow')||{}).textContent||'none'")[:120])
  E("const t=performance.now();parkAsk(PR.list[0].x);window.__ask=performance.now()-t;0");print('parkAsk ms',round(E("__ask"),1))
srv.kill();print('errors',errs)
