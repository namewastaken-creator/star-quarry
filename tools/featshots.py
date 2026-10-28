"""Close-up views of the plot edge and the nearest landmarks, one row per planet:
python3 featshots.py PORT OUT.png i,i,i   (tier 3 base, zoom level 3; left: the plot edge, right: a landmark)"""
import subprocess,time,sys
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw
port,out,ids=sys.argv[1],sys.argv[2],[int(x) for x in sys.argv[3].split(',')]
srv=subprocess.Popen(['python3','-m','http.server',port,'--bind','127.0.0.1'],cwd='/home/claude/StarQuarryWeb',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
errs=[];shots=[]
AIM="""(([e,n],k)=>{const i=%d,w=W[i];cam.track=false;let d;
  if(k===0)d=plotDir(e,n).applyQuaternion(w.siteQ);
  else{const c=[...w.feat.children].filter(o=>!o.isInstancedMesh&&!o.isSprite);let best=null,bd=9;
    const pd=PORT_DIR.clone().applyQuaternion(w.siteQ);
    (c.length?c.map(o=>o.position.clone().normalize()):[plotDir(0,-10).applyQuaternion(w.siteQ)]).forEach(v=>{const a=v.angleTo(pd);if(a<bd){bd=a;best=v}});d=best}
  d.applyQuaternion(w.mesh.quaternion).normalize();cam.phi=Math.acos(d.y)*.93;cam.theta=Math.atan2(d.z,d.x)+.12})(%s,%d);0"""
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
    E(f"(p=>{{p.u=true;crewState(p);p.teams=[{{}},{{}},{{}}];p.pts=60;p.al={{m:30,s:12,c:12,v:6}};Object.keys(PROGRAMS).forEach(id=>p.done[id]=1);p.set=3}})(S.planets[{i}]);crewVer++;settleVer++;refreshWorld();0")
    E(f"S.sel={i};focusPlanet({i},3);0");pg.wait_for_timeout(1500);E("while(surfJobs.length){if(surfJobs[0].step(performance.now()+1e9))surfJobs.shift()};0");pg.wait_for_timeout(1500)
    for k,xy in enumerate(([5.5,-5.5],[0,0])):
      E(AIM%(i,str(xy),k));pg.wait_for_timeout(300);E("while(surfJobs.length){if(surfJobs[0].step(performance.now()+1e9))surfJobs.shift()};0");pg.wait_for_timeout(2500)
      f=f'/tmp/claude-0/fs_{i}_{k}.png';pg.screenshot(path=f);shots.append((i,k,f,E(f"PLANETS[{i}].n+' · '+PTYPE({i})")+(' · plot edge' if k==0 else ' · landmark')))
srv.kill()
Wd,H=390,620;img=Image.new('RGB',(2*Wd+10,len(ids)*(H+24)),'#05060d');d=ImageDraw.Draw(img)
for k,(i,v,f,lab) in enumerate(shots):
  r,c=k//2,k%2;im=Image.open(f).crop((0,80,390,80+H));img.paste(im,(c*(Wd+10),r*(H+24)+24));d.text((c*(Wd+10)+8,r*(H+24)+6),lab,fill='#e8eaf5')
img.save(out);print('saved',out,'errors',errs)
