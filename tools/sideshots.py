"""Low side views of a planet's base, to check that structures sit on the ground and that raised things have supports:
python3 sideshots.py PORT OUT.png i,i [mid]  (tier 3 base; five views each: pad, mine head, works pad, refinery, settlement)
  mid: a part-built base instead (2 crews, pad tier 2, refinery tier 2, Town)"""
import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the repository root, served as the game
OUT=_os.environ.get('SQ_OUT',_os.path.join(ROOT,'out'));_os.makedirs(OUT,exist_ok=True)  # screenshots (git-ignored)
import subprocess,time,sys
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw
port,out,ids=sys.argv[1],sys.argv[2],[int(x) for x in sys.argv[3].split(',')];mid=len(sys.argv)>4 and sys.argv[4]=='mid'
BUILD=("p.teams=[{},{}];p.pts=40;p.al={m:20,s:7,c:7,v:6};p.done={pros:1};p.set=2" if mid else
       "p.teams=[{},{},{}];p.pts=60;p.al={m:30,s:12,c:12,v:6};Object.keys(PROGRAMS).forEach(id=>p.done[id]=1);p.set=3")
srv=subprocess.Popen([sys.executable,'-m','http.server',port,'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
shots=[];errs=[]
VIEWS=[('pad',[0,0]),('mine head',[0,3.05]),('works pad',[0,8.65]),('refinery',[2.95,-1.35]),('settlement',[-3.12,-1.8])]
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page();pg.on('pageerror',lambda e:errs.append(str(e)));E=pg.evaluate
  pg.goto(f'http://localhost:{port}/index.html');pg.wait_for_timeout(5000)
  try:pg.click('#nmOk',timeout=3000)
  except Exception:pass
  E("S.tut=2;S.tipClose=1;if(!sheet.classList.contains('collapsed'))toggleSheet();while(surfJobs.length){if(surfJobs[0].step(performance.now()+1e9))surfJobs.shift()};0")
  for i in ids:
    E(f"(p=>{{p.u=true;crewState(p);{BUILD}}})(S.planets[{i}]);crewVer++;settleVer++;refreshWorld();S.sel={i};focusPlanet({i},3);0")
    pg.wait_for_timeout(1500);E("while(surfJobs.length){if(surfJobs[0].step(performance.now()+1e9))surfJobs.shift()};0");pg.wait_for_timeout(1000)
    for name,xy in VIEWS:
      xy2=E(f"""(()=>{{const w=W[{i}];cam.track=false;const d=plotDir({xy[0]},{xy[1]}).applyQuaternion(w.siteQ).applyQuaternion(w.mesh.quaternion).normalize();
        const ax=new THREE.Vector3(0,1,0).cross(d).normalize(),c=d.clone().applyAxisAngle(ax,1.25);cam.phi=Math.acos(c.y);cam.theta=Math.atan2(c.z,c.x);
        return 0}})()""")
      pg.wait_for_timeout(2200)
      xy2=E(f"""(()=>{{const w=W[{i}];w.mesh.updateMatrixWorld(true);const q=plotDir({xy[0]},{xy[1]}).applyQuaternion(w.siteQ).multiplyScalar(PLANETS[{i}].size).applyMatrix4(w.mesh.matrixWorld).project(camera);return[(q.x+1)/2*innerWidth,(1-q.y)/2*innerHeight]}})()""")
      f=f'{OUT}/side_{i}_{len(shots)}.png';pg.screenshot(path=f);shots.append((f,xy2,E(f"PLANETS[{i}].n")+' · '+name))
srv.kill()
Wd=300;img=Image.new('RGB',(Wd*len(VIEWS)+10*(len(VIEWS)-1),len(ids)*(Wd+20)),'#05060d');d=ImageDraw.Draw(img)
for k,(f,(x,y),lab) in enumerate(shots):
  r,c=k//len(VIEWS),k%len(VIEWS);im=Image.open(f).crop((int(x-75),int(y-95),int(x+75),int(y+55))).resize((Wd,Wd))
  img.paste(im,(c*(Wd+10),r*(Wd+20)+20));d.text((c*(Wd+10)+6,r*(Wd+20)+4),lab,fill='#e8eaf5')
img.save(out);print('saved',out,errs)
