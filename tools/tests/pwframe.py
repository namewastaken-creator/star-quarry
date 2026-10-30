"""Frame time in the late game: load tools/tests/lategame.json (every planet claimed and maxed, all research; remake
it with mklategame.py) and fail if the game's own work in any frame, or in a tap, takes longer than LIMIT_MS.

Measured per frame: the frame loop minus drawing the 3D scene (headless Chromium draws in software, which is slow and
uneven, and isn't what this test is about). Taps: opening the Park window while the parking ranking is being worked
out (it used to work the forecast out on the spot) and switching to every tab. Also checks that the Park window fills
in by itself, that the ranking finishes, and that a ranking made during a station move goes stale when it arrives.
"""
import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # the repository root, served as the game
OUT=_os.environ.get('SQ_OUT',_os.path.join(ROOT,'out'));_os.makedirs(OUT,exist_ok=True)  # screenshots (git-ignored)
import subprocess,time,sys,json
from playwright.sync_api import sync_playwright
LIMIT_MS=50
SAVE=open(_os.path.join(ROOT,'tools','tests','lategame.json'),encoding='utf-8').read().strip()
srv=subprocess.Popen([sys.executable,'-m','http.server',sys.argv[1],'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
errs=[]
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  ctx=b.new_context(viewport={'width':390,'height':844},service_workers='block')
  # the save goes in before the game's script reads it (once, so a reload keeps the game's own save)
  ctx.add_init_script("if(!sessionStorage.getItem('sq_seeded')){localStorage.setItem('starquarry_save_v1',"+json.dumps(SAVE)+");sessionStorage.setItem('sq_seeded','1')}")
  pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));E=lambda js:pg.evaluate(js)
  pg.goto(f'http://localhost:{sys.argv[1]}/index.html');pg.wait_for_timeout(3000)
  print('planets',E("S.planets.filter(p=>p.u).length"),'research',E("Object.keys(S.research).length"))
  # time every frame's own work: frame() minus renderer.render
  # and, for a slow frame, which of the frame's parts took the time
  E("""window.__fw=[];window.__slow=[];const fr=frame,rr=renderer.render.bind(renderer);let rt=0,parts={};
    renderer.render=(a,b)=>{const t=performance.now();rr(a,b);rt+=performance.now()-t};
    for(const f of ['offline','step','probeTick','veinTick','progTick','updateWorld','glideView','evPlayTick','placeLabels','parkJob','evCheck','galTick','evBadge','tabBadges','centerUI','hud','render','save']){
      const g=window[f];window[f]=function(){const t=performance.now();try{return g.apply(this,arguments)}finally{parts[f]=(parts[f]||0)+performance.now()-t}}}
    frame=function(n){rt=0;parts={};const dt=n-lastT,t=performance.now();fr(n);const d=performance.now()-t-rt;__fw.push(d);
      if(d>LIMIT)__slow.push({ms:Math.round(d),dt:Math.round(dt),parts:Object.fromEntries(Object.entries(parts).filter(e=>e[1]>2).map(e=>[e[0],Math.round(e[1])]))})};0""".replace('LIMIT',str(LIMIT_MS)))
  slow=lambda what,ms:errs.append(f'{what} took {ms:.0f} ms (limit {LIMIT_MS})') if ms>LIMIT_MS else None
  tap=lambda js:E(f"(()=>{{const t=performance.now();{js};return performance.now()-t}})()")
  # a fresh ranking, then the Park window for a spot it hasn't reached yet
  E("PR=null;PRJ=null;setTab('research');0");pg.wait_for_timeout(500)
  x=E("S.planets.length-1")
  ms=tap(f"parkAsk({x})");print(f'Park window while ranking: {ms:.1f} ms');slow('Opening the Park window',ms)
  t=time.time()
  while time.time()-t<120 and E("$('pkGo').textContent")=='Working out…':pg.wait_for_timeout(500)
  print(f'Park window filled after {time.time()-t:.0f} s:',E("$('pkGo').textContent"))
  if E("$('pkGo').textContent")=='Working out…':errs.append('the Park window never filled in')
  E("$('pk').hidden=true;0")
  for k in range(240):
    if E("parkRankReady()"):break
    pg.wait_for_timeout(500)
  print(f'ranking ready after {time.time()-t:.0f} s')
  if not E("parkRankReady()"):errs.append('the parking ranking never finished')
  pg.wait_for_timeout(5000)
  fw=E("__fw");print(f'frames {len(fw)}, game work per frame: median {sorted(fw)[len(fw)//2]:.1f} ms, worst {max(fw):.1f} ms')
  slow('A frame',max(fw))
  for s in E("__slow"):print('slow frame',s)
  for tb in E("[...document.querySelectorAll('[data-tab]')].map(b=>b.dataset.tab)"):
    ms=tap(f"setTab('{tb}')");print(f'tab {tb}: {ms:.1f} ms');slow(f'Switching to the {tb} tab',ms)
  # stale rankings: one older than PR_REFRESH (wall clock: a phone's performance clock stops while it sleeps) isn't ready
  old=E("PR.t=Date.now()-PR_REFRESH-1000;parkRankReady()");print('an old ranking still counts as ready',old)
  if old:errs.append('a parking ranking older than PR_REFRESH still counts as ready')
  # after the station parks at the best spot, the Best parking spot card must not offer that spot while it re-ranks
  E("PR.t=Date.now();0");best=E("PR.list[0].x")
  E(f"S.park={{i:{best},from:S.park.i,t0:Date.now()-PARK_MOVE-1000,dur:PARK_MOVE,cd:Date.now()+PARK_CD,done:1}};0")
  offered=E(f"viewBestPark().includes('data-p=\"{best}\"')");print('card offers the spot the station is parked at',offered)
  if offered:errs.append('the Best parking spot card offers the spot the station is already parked at')
  pg.screenshot(path=_os.path.join(OUT,'pwframe.png'))
srv.kill();print('errors',errs)
