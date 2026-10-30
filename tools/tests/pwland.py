import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # the repository root, served as the game
OUT=_os.environ.get('SQ_OUT',_os.path.join(ROOT,'out'));_os.makedirs(OUT,exist_ok=True)  # screenshots (git-ignored)
import subprocess,time,sys
from playwright.sync_api import sync_playwright
srv=subprocess.Popen([sys.executable,'-m','http.server',sys.argv[1],'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
errs=[]
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page();pg.on('pageerror',lambda e:errs.append(str(e)));E=lambda js:pg.evaluate(js)
  pg.goto(f'http://localhost:{sys.argv[1]}/index.html');pg.wait_for_timeout(5000)
  try:pg.click('#nmOk',timeout=3000)
  except Exception:pass
  E("[1,3,6,7].forEach(i=>{const p=S.planets[i];p.u=true;crewState(p);p.teams=[{}]});refreshWorld();0")
  print(E("""JSON.stringify([1,3,6,7].map(i=>{const w=W[i],P=PLANETS[i];if(!w.siteG.parent)w.mesh.add(w.siteG);w.mesh.updateMatrixWorld(true);const pad=new THREE.Vector3();w.port.getWorldPosition(pad);
    const d=PORT_DIR.clone().applyQuaternion(w.siteQ).applyQuaternion(w.mesh.quaternion),tgt=w.mesh.position.clone().addScaledVector(d,P.size);return [P.n,+tgt.distanceTo(pad).toFixed(4)]}))"""))
srv.kill();print('errors',errs)
