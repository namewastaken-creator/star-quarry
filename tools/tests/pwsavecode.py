"""Your save (Warp tab): export, import, backups, and sealed save codes that refuse to load once changed.

Exports the late-game save (tools/tests/lategame.json) as a code and as a downloaded file, then in a fresh game:
codes that are changed by one character, cut short, not a code at all, sealed but the wrong shape, or from a newer
format must all be refused without touching the game; the downloaded file loads through Load file; the code loads
only on the second tap, after which the game reloads with the late-game save and the fresh game is kept as a backup;
Restore a backup brings the fresh game back and keeps the late-game one as a backup.
"""
import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # the repository root, served as the game
OUT=_os.environ.get('SQ_OUT',_os.path.join(ROOT,'out'));_os.makedirs(OUT,exist_ok=True)  # screenshots (git-ignored)
import subprocess,time,sys,json
from playwright.sync_api import sync_playwright
LATE=open(_os.path.join(ROOT,'tools','tests','lategame.json'),encoding='utf-8').read().strip()
srv=subprocess.Popen([sys.executable,'-m','http.server',sys.argv[1],'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
errs=[]
def need(ok,what):
  print(('ok   ' if ok else 'FAIL ')+what)
  if not ok:errs.append(what)
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  u=f'http://localhost:{sys.argv[1]}/'
  def page(seed):
    ctx=b.new_context(viewport={'width':390,'height':844},service_workers='block',accept_downloads=True);pg=ctx.new_page()
    pg.on('pageerror',lambda e:errs.append('page error: '+str(e).splitlines()[0]))
    pg.goto(u+'manifest.webmanifest');pg.evaluate("localStorage.clear()")
    if seed:pg.evaluate(f"localStorage.setItem('starquarry_save_v1',{json.dumps(seed)})")
    pg.goto(u+'index.html');pg.wait_for_timeout(3000)
    if pg.evaluate("!$('nm').hidden"):pg.click('#nmOk')
    pg.evaluate("setTab('warp');document.querySelector('#sheet')&&0");pg.wait_for_timeout(400)
    return ctx,pg
  # export from the late-game save
  ctx,pg=page(LATE);E=pg.evaluate
  orig=E("JSON.stringify({p:S.planets.map(q=>[q.u,q.pts,q.al,q.set]),r:Object.keys(S.research).length,n:S.st.name})")
  pg.click('[data-act=svexp]');pg.wait_for_timeout(300)
  code=E("$('svCode').value")
  need(code.startswith('SQ1-') and len(code)>200,'export shows a save code')
  need('planets' not in code and 'research' not in code and '"' not in code,'the code is not readable JSON')
  with pg.expect_download() as d:pg.click('#svFile')
  path=_os.path.join(OUT,'pwsavecode.sqsave');d.value.save_as(path)
  need(open(path,encoding='utf-8').read().strip()==code,'Download file saves the same code ('+d.value.suggested_filename+')')
  pg.screenshot(path=_os.path.join(OUT,'pwsavecode_export.png'));ctx.close()
  # a fresh game: refused codes leave everything as it is
  ctx,pg=page(None);E=pg.evaluate
  fresh=E("localStorage.getItem('starquarry_save_v1')")
  pg.click('[data-act=svimp]');pg.wait_for_timeout(200)
  mid=len(code)//2;flip='A' if code[mid]!='A' else 'B'
  bad=[('a code changed by one character',code[:mid]+flip+code[mid+1:],'changed or damaged'),
       ('a code cut short',code[:-40],'Paste the whole code'),
       ('text that isn\'t a code','{"v":1,"cash":1e99}',"isn't a Star Quarry save code"),
       ('a sealed save of the wrong shape',E("sealSave({v:1,planets:5})"),"can't be read by this version"),
       ('a sealed save from a newer format',E("sealSave({v:2,planets:[{}]})"),'newer version')]
  for name,c,want in bad:
    pg.fill('#svCode',c);pg.click('#svMain');pg.wait_for_timeout(100)
    msg=E("$('svMsg').textContent");hid=E("$('svGo').hidden")
    need(want in msg and hid,f'{name} is refused ({msg[:60]})')
  need(E("localStorage.getItem('starquarry_save_v1')")==fresh and E("S.planets.filter(q=>q.u).length")==1,'refused codes change nothing')
  # Load file, then the code itself: one tap arms, the second replaces
  pg.set_input_files('#svPick',path);pg.wait_for_timeout(400)
  need(E("$('svCode').value")==code and not E("$('svGo').hidden"),'Load file reads the downloaded file and checks it')
  pg.screenshot(path=_os.path.join(OUT,'pwsavecode_import.png'))
  pg.click('#svGo');pg.wait_for_timeout(300)
  need(E("S.planets.filter(q=>q.u).length")==1 and 'Tap again' in E("$('svGo').textContent"),'the first tap only asks to tap again')
  with pg.expect_navigation():pg.click('#svGo')
  pg.wait_for_timeout(3000)
  now=E("JSON.stringify({p:S.planets.map(q=>[q.u,q.pts,q.al,q.set]),r:Object.keys(S.research).length,n:S.st.name})")
  need(now==orig,'the imported game matches the exported one (planets, points, settlements, research, station name)')
  need('Save imported' in E("LOAD_NOTE"),'the player is told the save was imported')
  baks=E("saveBackups().filter(x=>x.s).map(x=>x.s.planets.filter(q=>q.u).length)")
  need(1 in baks,'the fresh game was kept as a backup')
  # Restore a backup brings the fresh game back, and keeps the late-game one
  pg.evaluate("setTab('warp');0");pg.wait_for_timeout(400);pg.click('[data-act=svbak]');pg.wait_for_timeout(300)
  btn=E("[...document.querySelectorAll('#svList [data-svk]')].findIndex(x=>saveBackups().find(y=>y.k===x.dataset.svk).s.planets.filter(q=>q.u).length===1)")
  sel=f'#svList [data-svk] >> nth={btn}'
  pg.click(sel);pg.wait_for_timeout(200)
  with pg.expect_navigation():pg.click(sel)
  pg.wait_for_timeout(3000)
  need(E("S.planets.filter(q=>q.u).length")==1 and 'Backup restored' in E("LOAD_NOTE"),'Restore a backup brings the fresh game back')
  need(22 in E("saveBackups().filter(x=>x.s).map(x=>x.s.planets.filter(q=>q.u).length)"),'the late-game save was kept as a backup')
  ctx.close()
srv.kill();print('errors',errs)
