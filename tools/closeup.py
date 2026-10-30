"""Close renders of base structures from a free camera (independent of the game camera), to check ground contact
and supports: python3 closeup.py PORT OUT.png i,i [targets]  targets = name:e:n:dist;...  (plot units, dist in planet radii)"""
import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the repository root, served as the game
OUT=_os.environ.get('SQ_OUT',_os.path.join(ROOT,'out'));_os.makedirs(OUT,exist_ok=True)  # screenshots (git-ignored)
import subprocess,time,sys,base64,io
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw
port,out,ids=sys.argv[1],sys.argv[2],[int(x) for x in sys.argv[3].split(',')]
T=sys.argv[4] if len(sys.argv)>4 else "mine head:0:3.05:.35;garage conveyor:.3:1.9:.3;works pad:0:8.65:.35;refinery:2.4:-1.6:.4;habitat:2.3:1.9:.3;settlement:-2.6:-1.5:.45"
targets=[(a,float(b),float(c),float(d)) for a,b,c,d in (x.split(':') for x in T.split(';'))]
srv=subprocess.Popen(['python3','-m','http.server',port,'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
shots=[];errs=[]
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page();pg.on('pageerror',lambda e:errs.append(str(e)));E=pg.evaluate
  pg.goto(f'http://localhost:{port}/index.html');pg.wait_for_timeout(5000)
  try:pg.click('#nmOk',timeout=3000)
  except Exception:pass
  E("S.tut=2;S.tipClose=1;if(!sheet.classList.contains('collapsed'))toggleSheet();while(surfJobs.length){if(surfJobs[0].step(performance.now()+1e9))surfJobs.shift()};0")
  for i in ids:
    E(f"(p=>{{p.u=true;crewState(p);p.teams=[{{}},{{}},{{}}];p.pts=60;p.al={{m:30,s:12,c:12,v:6}};Object.keys(PROGRAMS).forEach(id=>p.done[id]=1);p.set=3}})(S.planets[{i}]);crewVer++;settleVer++;refreshWorld();S.sel={i};focusPlanet({i},3);0")
    pg.wait_for_timeout(2000);E("while(surfJobs.length){if(surfJobs[0].step(performance.now()+1e9))surfJobs.shift()};0");pg.wait_for_timeout(1500)
    for name,e,n,dist in targets:
      url=E(f"""(()=>{{const i={i},w=W[i],R=PLANETS[i].size;w.mesh.updateMatrixWorld(true);
        const d=plotDir({e},{n}).applyQuaternion(w.siteQ),tgt=d.clone().multiplyScalar(R*1.005).applyMatrix4(w.mesh.matrixWorld);
        const up=d.clone().transformDirection(w.mesh.matrixWorld),side=new THREE.Vector3(0,1,0).cross(up).normalize(),fwd=new THREE.Vector3().crossVectors(up,side);
        const c2=new THREE.PerspectiveCamera(45,1,R*.002,R*20);c2.position.copy(tgt).addScaledVector(side,R*{dist}).addScaledVector(fwd,R*{dist}*.35).addScaledVector(up,R*{dist}*.42);c2.up.copy(up);c2.lookAt(tgt);
        const sz=renderer.getSize(new THREE.Vector2());renderer.setSize(600,600,false);renderer.render(scene,c2);const u=renderer.domElement.toDataURL('image/png');renderer.setSize(sz.x,sz.y,false);return u}})()""")
      im=Image.open(io.BytesIO(base64.b64decode(url.split(',')[1])));shots.append((im,E(f"PLANETS[{i}].n")+' · '+name))
srv.kill()
Wd=300;n=len(targets);img=Image.new('RGB',(Wd*n+10*(n-1),len(ids)*(Wd+20)),'#05060d');d=ImageDraw.Draw(img)
for k,(im,lab) in enumerate(shots):
  r,c=k//n,k%n;img.paste(im.convert('RGB').resize((Wd,Wd)),(c*(Wd+10),r*(Wd+20)+20));d.text((c*(Wd+10)+6,r*(Wd+20)+4),lab,fill='#e8eaf5')
img.save(out);print('saved',out,errs)
