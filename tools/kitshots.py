"""Screenshots of tier 1 and tier 3 bases for chosen planets: python3 kitshots.py PORT OUT.png i,i,i [zoom]"""
import subprocess,time,sys
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw
port,out,ids=sys.argv[1],sys.argv[2],[int(x) for x in sys.argv[3].split(',')];zl=int(sys.argv[4]) if len(sys.argv)>4 else 1;aim=sys.argv[5] if len(sys.argv)>5 else ""
srv=subprocess.Popen(['python3','-m','http.server',port,'--bind','127.0.0.1'],cwd='/home/claude/StarQuarryWeb',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
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
  for i in ids:
    for tier in (1,3):
      if tier==1:E(f"(p=>{{p.u=true;crewState(p);p.teams=[{{}}];p.al={{}};p.pts=0;p.done={{}};p.set={1 if aim=='set' else 0}}})(S.planets[{i}]);crewVer++;settleVer++;refreshWorld();0")
      else:E(f"(p=>{{p.u=true;crewState(p);p.teams=[{{}},{{}},{{}}];p.pts=60;p.al={{m:30,s:12,c:12,v:6}};Object.keys(PROGRAMS).forEach(id=>p.done[id]=1);p.set=3}})(S.planets[{i}]);crewVer++;settleVer++;refreshWorld();0")
      E(f"S.sel={i};focusPlanet({i},{zl});0");pg.wait_for_timeout(2500)
      if aim=='ref':
        E(f"(()=>{{const w=W[{i}];cam.track=false;const d=plotDir(1.4,-1.1).applyQuaternion(w.siteQ).applyQuaternion(w.mesh.quaternion).normalize();cam.phi=Math.acos(d.y)*.9;cam.theta=Math.atan2(d.z,d.x)}})();0")
      if aim=='mine':
        E(f"(()=>{{const w=W[{i}];cam.track=false;const d=plotDir(...WORKS).applyQuaternion(w.siteQ).applyQuaternion(w.mesh.quaternion).normalize();cam.phi=Math.acos(d.y)*.92;cam.theta=Math.atan2(d.z,d.x)}})();0")
      if aim=='set':
        E(f"(()=>{{const w=W[{i}];cam.track=false;const d=plotDir(...LAY.set).applyQuaternion(w.siteQ).applyQuaternion(w.mesh.quaternion).normalize();cam.phi=Math.acos(d.y)*.92;cam.theta=Math.atan2(d.z,d.x)}})();0")
      pg.wait_for_timeout(2500)
      f=f'/tmp/claude-0/ks_{i}_{tier}.png';pg.screenshot(path=f);shots.append((i,tier,f,E(f"PLANETS[{i}].n+' · '+PTYPE({i})+' · tier '+{tier}")))
srv.kill()
W,H=390,560;cols=2;rows=len(ids)
img=Image.new('RGB',(cols*W+10,rows*(H+24)),'#05060d');d=ImageDraw.Draw(img)
for k,(i,tier,f,lab) in enumerate(shots):
  r,c=k//2,k%2;im=Image.open(f).crop((0,90,390,90+H));img.paste(im,(c*(W+10),r*(H+24)+24));d.text((c*(W+10)+8,r*(H+24)+6),lab,fill='#e8eaf5')
img.save(out);print('saved',out,'errors',errs)
