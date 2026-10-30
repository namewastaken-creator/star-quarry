import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # the repository root, served as the game
OUT=_os.environ.get('SQ_OUT',_os.path.join(ROOT,'out'));_os.makedirs(OUT,exist_ok=True)  # screenshots (git-ignored)
import subprocess,time,sys,json
from playwright.sync_api import sync_playwright
srv=subprocess.Popen([sys.executable,'-m','http.server',sys.argv[1],'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
W=int(sys.argv[2]) if len(sys.argv)>2 else 360
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  pg=b.new_context(viewport={'width':W,'height':800},service_workers='block').new_page()
  errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));E=lambda js:pg.evaluate(js)
  pg.goto(f'http://localhost:{sys.argv[1]}/index.html');pg.wait_for_timeout(4500);pg.click('#nmOk')
  E("""S.tut=2;S.cash=5e7;for(const id of ['auto','smelt','slot2','drill1','ion1','hold1','silo1','trade1','furn','drill2','thrust'])S.research[id]=1;
    for(let i=0;i<7;i++){const p=S.planets[i];p.u=true;const q=crewState(p);q.teams=i<3?[{},{nm:'A',q:'thrifty'},{nm:'B',q:'eager'}]:[{}];q.pts=i<3?60:20;q.bought=q.pts;q.al=i<3?{m:30,s:15,c:15}:{m:10,s:5,c:5}}
    crewVer++;refreshWorld();sheet.classList.contains('collapsed')&&toggleSheet();0""");pg.wait_for_timeout(1500)
  snap="""(()=>{const out={};const top=[...pbody.children];let k=0;pbody.querySelectorAll('.card').forEach(c=>{const t=(c.querySelector('h3,.t,h2')||{}).textContent||'';const key=k+++':'+t.trim().slice(0,24);out[key]=Math.round(c.getBoundingClientRect().height)});return out})()"""
  bad=[]
  def run(tabname,setups):
    res=[]
    for label,js in setups:
      E(js+";0");E(f"setTab('{tabname}');render(true);0");pg.wait_for_timeout(700)
      res.append((label,E(snap)))
    keys=set().union(*[set(r[1]) for r in res])
    for k in sorted(keys):
      hs=[(l,r.get(k)) for l,r in res if r.get(k) is not None]
      vals={h for _,h in hs}
      if len(vals)>1: bad.append((tabname,k,hs))
    print(tabname,'cards checked',len(keys))
  run('probe',[('in',"S.probe.out=null;S.probe.nextAt=Date.now()+120000"),('out',"S.probe.nextAt=Date.now()-1;probeTick(Date.now())"),('out-late',"if(S.probe.out)S.probe.out.at=Date.now()-170000")])
  run('market',[('ready',"S.od.until=0;S.od.ready=0"),('running',"S.od.until=Date.now()+300000;S.od.ready=S.od.until+3600000;S.od.pool=1e6"),('recharging',"S.od.until=Date.now()-1;S.od.ready=Date.now()+1800000"),('auto on',"discovered().forEach(o=>S.auto['o'+o]=true)")])
  run('smelter',[('off',"S.slots.forEach(s=>setSlot(s,null))"),('on',"setSlot(S.slots[0],1);setSlot(S.slots[1],5)"),('mix',"setSlot(S.slots[0],0);setSlot(S.slots[1],null)")])
  run('research',[('poor',"S.cash=10"),('rich',"S.cash=1e12;for(let o=0;o<7;o++)S.inv[o]=1e6")])
  run('planet',[('cinder',"S.sel=0"),('cinder red',"S.sel=0;crewState(S.planets[0]).al={m:60,s:0,c:0};crewVer++"),('cinder green',"S.sel=0;crewState(S.planets[0]).al={m:2,s:29,c:29};crewVer++"),('park moving',"S.sel=0;parkGo(2)"),('park cooldown',"S.sel=0;if(S.park){S.park.t0=Date.now()-S.park.dur-1}"),('vesk silo',"S.sel=1")])
  run('events',[('base',""),('accepted',"try{evAccept(0)}catch(e){}"),('later',"")])
  run('warp',[('idle',"UPD.st='idle'"),('checking',"UPD.st='checking'"),('current',"UPD.st='current';UPD.at=Date.now()"),('new',"UPD.st='new';UPD.remote={name:'Beta 0.18.10.108',n:108}"),('new declined',"UPD.declined=true"),('fail',"UPD.st='fail'"),('armed',"try{arm('warp')}catch(e){}")])
  print('\nCARDS THAT CHANGE SIZE:' if bad else '\nno card changes size')
  for t,k,hs in bad: print(' ',t,k,hs)
  print('errs',errs)
srv.kill()
