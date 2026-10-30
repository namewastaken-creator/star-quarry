"""Close look at landmarks: python3 featclose.py PORT OUT.png i:k,i:k ...  (planet i, k-th large landmark; two views each:
from above at 35 degrees, and low across the ground)"""
import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the repository root, served as the game
OUT=_os.environ.get('SQ_OUT',_os.path.join(ROOT,'out'));_os.makedirs(OUT,exist_ok=True)  # screenshots (git-ignored)
import subprocess,time,sys
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw
port,out=sys.argv[1],sys.argv[2];jobs=[tuple(int(v) for v in x.split(':')) for x in sys.argv[3].split(',')]
srv=subprocess.Popen(['python3','-m','http.server',port,'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
errs=[];shots=[]
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page();pg.on('pageerror',lambda e:errs.append(str(e)));E=lambda js:pg.evaluate(js)
  pg.goto(f'http://localhost:{port}/index.html');pg.wait_for_timeout(5000)
  try:pg.click('#nmOk',timeout=3000)
  except Exception:pass
  E("S.tut=2;S.tipClose=1;if(!sheet.classList.contains('collapsed'))toggleSheet();0")
  for t in range(60):
    if E("surfJobs.length")==0:break
    pg.wait_for_timeout(1000)
  for i,k in jobs:
    E(f"(p=>{{p.u=true;crewState(p);p.teams=[{{}},{{}},{{}}];p.pts=60;p.al={{m:30,s:12,c:12,v:6}};Object.keys(PROGRAMS).forEach(id=>p.done[id]=1);p.set=3}})(S.planets[{i}]);crewVer++;settleVer++;refreshWorld();0")
    E(f"S.sel={i};focusPlanet({i},3);0");pg.wait_for_timeout(1500);E("while(surfJobs.length){if(surfJobs[0].step(performance.now()+1e9))surfJobs.shift()};0");pg.wait_for_timeout(1500)
    for v,(tilt,dist) in enumerate(((.35,0),(.95,0))):
      lab=E(f"""(()=>{{const i={i},w=W[i];cam.track=false;const big=[...w.feat.children].filter(o=>!o.isInstancedMesh&&!o.isSprite);
        let d=big.length?big[{k}%big.length].position.clone().normalize():plotDir(PLOT_R+2,0).applyQuaternion(w.siteQ);
        d.applyQuaternion(w.mesh.quaternion).normalize();
        // swing the camera off the landmark's vertical by the tilt, around the planet's centre
        const ax=new THREE.Vector3(0,1,0).cross(d).normalize();if(ax.lengthSq()<1e-6)ax.set(1,0,0);const c=d.clone().applyAxisAngle(ax,{tilt});
        cam.phi=Math.acos(Math.max(-1,Math.min(1,c.y)));cam.theta=Math.atan2(c.z,c.x);
        return PLANETS[i].n+' · '+PTYPE(i)+' · landmark '+{k}+' of '+big.length}})()""")
      pg.wait_for_timeout(2500);f=f'{OUT}/fc_{i}_{k}_{v}.png';pg.screenshot(path=f);shots.append((f,lab))
srv.kill()
Wd,H=390,700;img=Image.new('RGB',(2*Wd+10,(len(shots)+1)//2*(H+24)),'#05060d');d=ImageDraw.Draw(img)
for n,(f,lab) in enumerate(shots):
  r,c=n//2,n%2;im=Image.open(f).crop((0,60,390,60+H));img.paste(im,(c*(Wd+10),r*(H+24)+24));d.text((c*(Wd+10)+8,r*(H+24)+6),lab,fill='#e8eaf5')
img.save(out);print('saved',out,'errors',errs)
