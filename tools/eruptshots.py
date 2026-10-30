import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the repository root, served as the game
OUT=_os.environ.get('SQ_OUT',_os.path.join(ROOT,'out'));_os.makedirs(OUT,exist_ok=True)  # screenshots (git-ignored)
import subprocess,time,sys,os
from playwright.sync_api import sync_playwright
from PIL import Image
port,i,k,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4];TILT=float(os.environ.get('TILT','1.0'))
srv=subprocess.Popen(['python3','-m','http.server',port,'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
AIM=f"""(()=>{{const w=W[{i}],v=w.feat.children[{k}];cam.track=false;const d=v.position.clone().normalize().applyQuaternion(w.mesh.quaternion).normalize();
  const ax=new THREE.Vector3(0,1,0).cross(d).normalize(),c=d.clone().applyAxisAngle(ax,{TILT});cam.phi=Math.acos(c.y);cam.theta=Math.atan2(c.z,c.x)}})();0"""
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page();E=pg.evaluate
  pg.goto(f'http://localhost:{port}/index.html');pg.wait_for_timeout(5000)
  try:pg.click('#nmOk',timeout=3000)
  except Exception:pass
  E("S.tut=2;S.tipClose=1;if(!sheet.classList.contains('collapsed'))toggleSheet();0");pg.wait_for_function("surfJobs.length===0",timeout=90000)
  E(f"(p=>{{p.u=true;crewState(p);p.teams=[{{}}]}})(S.planets[{i}]);crewVer++;refreshWorld();S.sel={i};focusPlanet({i},3);0");pg.wait_for_timeout(3000)
  E(AIM);pg.wait_for_timeout(2500);E(f"W[{i}].feat.children[{k}].userData.erupt();0");fr=[]
  for n in range(12):
    E(AIM);pg.wait_for_timeout(60);xy=E(f"(()=>{{const w=W[{i}],v=w.feat.children[{k}];v.updateMatrixWorld(true);const q=new THREE.Vector3(0,PLANETS[{i}].size*.16*.8,0).applyMatrix4(v.matrixWorld).project(camera);return[(q.x+1)/2*innerWidth,(1-q.y)/2*innerHeight]}})()")
    f=f'{OUT}/er_{n}.png';pg.screenshot(path=f,timeout=90000);fr.append((f,xy));pg.wait_for_timeout(int(os.environ.get('GAP','350')))
srv.kill()
ims=[Image.open(f).crop((int(x-130),int(y-170),int(x+130),int(y+90))).resize((390,390)) for f,(x,y) in fr];W,H=ims[0].size;g=Image.new('RGB',(W*4,H*3))
for n,im in enumerate(ims):g.paste(im,((n%4)*W,(n//4)*H))
g.save(out);print('saved')
