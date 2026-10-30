"""Bad saves: a save the game can't use must never be lost, and the game must still start.

For each case the save (and sometimes an older backup) goes into localStorage before the game loads, the game runs
past its first autosave and the page is left (which saves again). Then every case must still have the original save,
byte for byte, somewhere in storage (the save itself or a backup); an older backup must survive too; the game must
be running; and the player must be told. Cases: unreadable JSON, readable but the wrong shape (no planets, planets
not a list, a missing planet, research not an object), a save from a newer format, a bad save while an older backup
is already kept, a save that passes those checks but fails while the game starts (it must reload once and start a
new game, saving nothing over it), and a bad save when the backup can't be written (storage full). A good late-game save must load
with no note.
"""
import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # the repository root, served as the game
import subprocess,time,sys,json
from playwright.sync_api import sync_playwright
srv=subprocess.Popen([sys.executable,'-m','http.server',sys.argv[1],'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
LATE=open(_os.path.join(ROOT,'tools','tests','lategame.json'),encoding='utf-8').read().strip()
late=lambda f:(lambda s:(f(s),json.dumps(s,separators=(',',':')))[1])(json.loads(LATE))
OLD=late(lambda s:s.update(cash=12345))   # an older backup that must survive
def drop3(s):s['planets'][3]=None
def nores(s):s['research']=None
def teams5(s):s['planets'][2]['teams']=5   # passes the shape check, but starting the game fails
CASES=[  # name, save, older backup already kept, backups can't be written
  ('unreadable JSON','{"v":1,"cash":5,"planets":[{"u":tr',None,False),
  ('no planets','{"v":1,"cash":5}',None,False),
  ('planets not a list','{"v":1,"planets":7}',None,False),
  ('a missing planet',late(drop3),None,False),
  ('research not an object',late(nores),None,False),
  ('newer format','{"v":2,"x":1}',None,False),
  ('fails while the game starts',late(teams5),None,False),
  ('bad save with an older backup kept','{not json',OLD,False),
  ('newer format with an older backup kept','{"v":2,"y":1}',OLD,False),
  ('bad save, storage full for the backup','{not json either',None,True),
  ('good late-game save',LATE,None,False)]
errs=[]
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  u=f'http://localhost:{sys.argv[1]}/'
  for name,raw,old,full in CASES:
    ctx=b.new_context(viewport={'width':390,'height':844},service_workers='block');pg=ctx.new_page();E=lambda js:pg.evaluate(js)
    perr=[];pg.on('pageerror',lambda e:perr.append(str(e).splitlines()[0]))
    if full:  # anything but the save itself throws, as when storage is nearly full
      ctx.add_init_script("{const o=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k!=='starquarry_save_v1'&&k.startsWith('starquarry_save_v1'))throw new DOMException('full','QuotaExceededError');return o.call(this,k,v)}}")
    pg.goto(u+'manifest.webmanifest')
    E(f"localStorage.clear();localStorage.setItem('starquarry_save_v1',{json.dumps(raw)});"+(f"localStorage.setItem('starquarry_save_v1_bak',{json.dumps(old)});" if old else '')+"0")
    pg.goto(u+'index.html');pg.wait_for_timeout(7000)
    running=E("typeof S==='object'&&!!S&&Array.isArray(S.planets)&&S.planets.length>0")
    note=E("typeof LOAD_NOTE==='string'?LOAD_NOTE:''") if running else ''
    pg.goto(u+'manifest.webmanifest');pg.wait_for_timeout(300)
    store=E("Object.fromEntries(Object.keys(localStorage).map(k=>[k,localStorage.getItem(k)]))")
    good=name.startswith('good')
    kept=good or raw in store.values();oldkept=not old or old in store.values()
    print(f'{name}: running {running}, original kept {kept}, older backup kept {oldkept}, note {note[:70]!r}, keys {sorted(store)}' + (f', boot errors {perr}' if perr else ''))
    if not running:errs.append(f'{name}: the game did not start')
    if not kept:errs.append(f'{name}: the original save was lost')
    if not oldkept:errs.append(f'{name}: the older backup was overwritten')
    if good and note:errs.append(f'{name}: a good save showed a note')
    if not good and not note and running:errs.append(f'{name}: the player was not told')
    # the save that fails while starting throws once, before the reload that starts a new game
    if perr and not name.startswith('fails'):errs.append(f'{name}: errors while starting {perr}')
    ctx.close()
srv.kill();print('errors',errs)
