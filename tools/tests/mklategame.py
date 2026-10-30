"""Make tools/tests/lategame.json: a maxed late-game save for performance tests and manual testing.

  python -I tools/tests/mklategame.py [port]      (run src/build.py first; it builds from the game in the repo root)

Starts a new game in headless Chromium and fills it in with the game's own rules: every planet claimed with all three
crews (the Shift Crew and Instructors picked from their first candidate), every point bought (room for 65 with
Mentoring), every training program finished, all three perk slots filled, every settlement at level 3, and all
research done. The station is parked at Cinder with its thrusters cooled down. The save is written as the game
writes it (save()), so loading it goes through the normal load path.

To play it: open the game, then in the console run
  localStorage.setItem('starquarry_save_v1', <the file's text>); location.reload()
"""
import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # the repository root, served as the game
import subprocess,time,sys,json
from playwright.sync_api import sync_playwright
port=sys.argv[1] if len(sys.argv)>1 else '8790'
OUT=_os.path.join(ROOT,'tools','tests','lategame.json')
srv=subprocess.Popen([sys.executable,'-m','http.server',port,'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
errs=[]
try:
  with sync_playwright() as p:
    b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page();pg.on('pageerror',lambda e:errs.append(str(e)));E=lambda js:pg.evaluate(js)
    pg.goto(f'http://localhost:{port}/index.html');pg.wait_for_timeout(4500)
    raw=E("""(()=>{
      SAVE_BLOCK=true;                       // nothing saves while the state is being filled in
      S.tut=2;S.st.name='Quarry Prime';S.cash=1e40;
      RESEARCH.forEach(r=>S.research[r.id]=1);
      const PK=['mine12','yield8','speed12'],AL={m:30,s:15,c:15,v:5};
      S.planets.forEach((p,i)=>{crewState(p);p.u=true;p.t=Math.random();p.load=0;p.stock=0;
        p.teams=[{}];for(const j of [1,2]){const c=crewCands(i,j)[0];p.teams.push({nm:c.nm,q:c.q})}
        Object.keys(PROGRAMS).forEach(id=>p.done[id]=1);p.prog=null;
        const cap=ptsCap(i);p.pts=cap;p.bought=cap;
        p.al={};let left=cap;for(const k of ['m','s','c','v']){p.al[k]=Math.min(left,AL[k]);left-=p.al[k]}p.al.m+=left;
        p.perks=PK.map(id=>({id,ready:0}));p.swapFree=false;p.set=3;
        if(!p.vein)p.vein=Date.now()+3600e3});
      S.park={i:0,from:0,t0:0,dur:1,cd:0,done:1};
      S.life.claims=S.planets.length;S.life.teams=S.planets.length*3;S.life.settle=S.planets.length*3;S.life.res=RESEARCH.length;
      crewVer++;settleVer++;S.cash=1e40;   // plenty for station fuel and anything else
      SAVE_BLOCK=false;save();SAVE_BLOCK=true;
      return localStorage.getItem('starquarry_save_v1')})()""")
    b.close()
finally:
  srv.kill()
if errs:print('errors',errs);sys.exit(1)
s=json.loads(raw)
with open(OUT,'w',encoding='utf-8',newline='\n') as f:json.dump(s,f,separators=(',',':'));f.write('\n')
print(f'wrote {OUT}: {sum(1 for q in s["planets"] if q["u"])} planets, {len(s["research"])} research, {len(raw)//1024} KB')
