"""Save migrations: each one-time conversion runs once, in order, and S.mig records how many a save has had.

A new game's save is taken from the page (newRun) and changed to look like older saves. Each goes into localStorage
before the game loads; the game state is then read. Cases: crews from before planet levels went (econ 1), the 10x
star dust award (dust1), a furnace from before smelting became a flow, Handling points and perks, all of those in a
save with no S.mig; a save that has had every step (its old-looking data must be left alone); one that has had only
some (only the rest run); a save from a newer build (a higher S.mig is kept); a new game; and the late-game save,
which has no S.mig and must load with its crews unchanged. The number must also be in the save written afterwards.
"""
import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # the repository root, served as the game
import subprocess,time,sys,json
from playwright.sync_api import sync_playwright
srv=subprocess.Popen([sys.executable,'-m','http.server',sys.argv[1],'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
LATE=open(_os.path.join(ROOT,'tools','tests','lategame.json'),encoding='utf-8').read().strip()
errs=[]
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  u=f'http://localhost:{sys.argv[1]}/'
  def run(raw,read):
    """load the game with this save (None: no save) and return read (a JS expression) and the save written on leaving"""
    ctx=b.new_context(viewport={'width':390,'height':844},service_workers='block');pg=ctx.new_page();E=lambda js:pg.evaluate(js)
    perr=[];pg.on('pageerror',lambda e:perr.append(str(e).splitlines()[0]))
    pg.goto(u+'manifest.webmanifest')
    # saved just now, so no offline progress is added while the case runs
    E("localStorage.clear();"+(f"{{const s=JSON.parse({json.dumps(raw)});s.last=Date.now();localStorage.setItem('starquarry_save_v1',JSON.stringify(s))}}" if raw else '')+"0")
    pg.goto(u+'index.html');pg.wait_for_timeout(5000)
    got=E(f"JSON.parse(JSON.stringify({read}))")
    pg.goto(u+'manifest.webmanifest');pg.wait_for_timeout(300)
    try:stored=json.loads(E("localStorage.getItem('starquarry_save_v1')") or 'null')
    except ValueError:stored=None
    ctx.close();return got,stored,perr
  # a new game: every step counts as done; its save, without S.mig, is the base for the older-looking saves
  got,stored,perr=run(None,"{mig:S.mig,n:MIGRATIONS.length,base:newRun()}")
  N=got['n'];BASE=got['base'];del BASE['mig']
  BASE['planets'][0].update(load=0,t=0)  # Cinder's first hauler starts empty, so no ore is delivered while a case runs
  # the first probe is due 60 s after BASE was made, and later cases run after that: keep it away so it brings no ore
  BASE['probe']['nextAt']=4102444800000
  # the furnace cases use Rustcore (ore 1): Cinder mines only Emberite (ore 0), which its hauler can still deliver
  # during the wait, so the Rustcore the game holds is exactly what the migration returned
  R=1
  print(f'new game: mig {got["mig"]} of {N}')
  if got['mig']!=N:errs.append(f'new game: mig {got["mig"]}, expected {N}')
  if perr:errs.append(f'new game: errors {perr}')
  def old(f):s=json.loads(json.dumps(BASE));f(s);return json.dumps(s,separators=(',',':'))
  def econ1(s):
    s['econ']=1;s['planets'][0]['teams']=[];s['planets'][0]['mn']={'n':5,'t':{'m':2,'s':1,'c':0}};s['planets'][0]['m']=4
    s['planets'][1]['u']=True;s['planets'][1]['mn']={'n':3,'t':{'m':1}}
  def dust(s):s['dm']=50;s['dust1']=True
  def furnace(s):s['slots'][0]={'r':R,'p':.25,'a':True};s['inv']={}
  def handling(s):pl=s['planets'][0];pl['al']={'d':3,'m':1};pl['done']={'dock':1};pl['perks']=[{'id':'hand2'}]
  def all_done(s):dust(s);s['mig']=N
  def part_done(s):dust(s);s['slots'][0]={'r':R,'p':0,'a':True};s['inv']={};s['mig']=2
  def newer(s):s['mig']=N+4
  P0="S.planets[0]"
  CASES=[  # name, save, what to read, check(got) -> problem or ''
    ('crews from before planet levels went',old(econ1),
     f"{{econ:S.econ,t0:{P0}.teams,pts0:{P0}.pts,al0:{P0}.al,mn0:'mn' in {P0},m0:'m' in {P0},pts1:S.planets[1].pts,t1:S.planets[1].teams.length}}",
     lambda g:'' if g['econ']==2 and g['t0']==[{}] and g['pts0']==5 and g['al0'].get('m')==2 and g['al0'].get('s')==1
       and not g['mn0'] and not g['m0'] and g['pts1']==3 and g['t1']==1 else f'not converted: {g}'),
    ('10x star dust',old(dust),"{dm:S.dm,flag:'dust1' in S}",
     lambda g:'' if g=={'dm':5,'flag':False} else f'dust not undone: {g}'),
    ('furnace mid-bar from before the smelting flow',old(furnace),f"{{ore:S.inv[{R}]||0,a:S.slots[0].a,p:S.slots[0].p}}",
     lambda g:'' if g['ore']==6 and g['a'] is False and g['p']==.25 else f'ore not returned: {g}'),
    ('Handling points and perk',old(handling),f"{{d:'d' in {P0}.al,dock:'dock' in {P0}.done,perk:{P0}.perks[0],swap:!!{P0}.swapFree}}",
     lambda g:'' if g=={'d':False,'dock':False,'perk':None,'swap':True} else f'Handling not removed: {g}'),
    ('every step done already',old(all_done),"{dm:S.dm,flag:'dust1' in S}",
     lambda g:'' if g=={'dm':50,'flag':True} else f'a step ran again: {g}'),
    ('two steps done already',old(part_done),f"{{dm:S.dm,ore:S.inv[{R}]||0}}",
     lambda g:'' if g=={'dm':50,'ore':8} else f'wrong steps ran: {g}'),
    ('a save from a newer build',old(newer),"{}",lambda g:''),
    ('late-game save with no S.mig',LATE,"{pts:S.planets.map(p=>p.pts),teams:S.planets.map(p=>p.teams.length),dm:S.dm}",
     lambda g:'' if g=={'pts':[x.get('pts') for x in json.loads(LATE)['planets']],'teams':[len(x['teams']) for x in json.loads(LATE)['planets']],
       'dm':json.loads(LATE)['dm']} else 'crews or star dust changed')]
  for name,raw,read,check in CASES:
    got,stored,perr=run(raw,f"Object.assign({read},{{mig:S.mig}})")
    want=N+4 if name.startswith('a save from a newer') else N
    bad=check({k:v for k,v in got.items() if k!='mig'}) or ('' if got['mig']==want else f'mig {got["mig"]}, expected {want}') \
      or ('' if stored and stored.get('mig')==want else f'saved mig {stored and stored.get("mig")}, expected {want}')
    print(f'{name}: mig {got["mig"]}, saved mig {stored and stored.get("mig")}'+(f', {bad}' if bad else '')+(f', errors {perr}' if perr else ''))
    if bad:errs.append(f'{name}: {bad}')
    if perr:errs.append(f'{name}: errors {perr}')
srv.kill();print('errors',errs)
