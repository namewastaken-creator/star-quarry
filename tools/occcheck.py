"""World kits occupancy check: on all 22 planets, builds a full tier 3 base (3 crews, 24 hauling points, every
training program, City) and the close-up landmarks, then proves no landmark overlaps the plot or any reserved
footprint (OCC), and reports any base part that stands outside every reservation.
Usage: python3 occcheck.py PORT  (serves /home/claude/StarQuarryWeb on localhost:PORT)"""
import subprocess,time,sys,json
from playwright.sync_api import sync_playwright
port=sys.argv[1] if len(sys.argv)>1 else '9600'
srv=subprocess.Popen(['python3','-m','http.server',port,'--bind','127.0.0.1'],cwd='/home/claude/StarQuarryWeb',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
errs=[]
JS=r"""(()=>{const out=[];
S.planets.forEach((p,i)=>{p.u=true;crewState(p);p.teams=[{},{},{}];p.pts=Math.max(p.pts||0,60);p.al={m:30,s:12,c:12,v:6};Object.keys(PROGRAMS).forEach(id=>p.done[id]=1);p.set=3});
crewVer++;settleVer++;refreshWorld();
W.forEach((w,i)=>{syncBase(w,i);if(w.siteG&&!w.siteG.parent)w.mesh.add(w.siteG);w.mesh.updateMatrixWorld(true);buildFeatures(w,i);w.mesh.updateMatrixWorld(true);
  const R=PLANETS[i].size,unit=R*.16,inv=new THREE.Matrix4().copy(w.mesh.matrixWorld).invert(),v=new THREE.Vector3(),m=new THREE.Matrix4(),sc=new THREE.Vector3(),q=new THREE.Quaternion();
  let feats=0,bad=[];
  const test=(pos,rad,what,inPlot)=>{feats++;if(!occFar(w,pos,rad)){bad.push(`${what} on the far mining field`);return}const [x,z,f]=plotXY(w,pos);if(f<.2)return;const d=Math.hypot(x,z);
    if(!inPlot&&d<PLOT_R+rad-1e-6){bad.push(`${what} inside plot (d ${d.toFixed(2)}, r ${rad.toFixed(2)})`);return}
    for(const o of OCC)if(Math.hypot(x-o.x,z-o.z)<o.r+rad-1e-6){bad.push(`${what} on ${o.kind}`);return}};
  w.feat.children.forEach(o=>{
    if(o.isInstancedMesh){o.geometry.computeBoundingSphere();const br=o.geometry.boundingSphere.radius;for(let k=0;k<o.count;k++){o.getMatrixAt(k,m);m.decompose(v,q,sc);test(v.clone(),br*Math.max(sc.x,sc.z)/unit,o.userData.inPlot?'base tree':'instance',!!o.userData.inPlot)}}
    else{o.updateMatrixWorld(true);const b=new THREE.Box3().setFromObject(o);const c=b.getCenter(new THREE.Vector3()).applyMatrix4(inv),sz=b.getSize(new THREE.Vector3());
      const p0=o.position.clone();test(p0,Math.max(sz.x,sz.z)*.0/unit+(o.userData.fr||0),o.type)}});
  // base parts outside every reservation (informational)
  let outside=0,parts=0;var outEx=window.__outEx||(window.__outEx=[]);w.siteG.updateMatrixWorld(true);w.siteG.traverse(o=>{if(!o.isMesh||o.userData.glow)return;for(let a=o;a;a=a.parent)if(a.userData.mobile)return;parts++;o.getWorldPosition(v).applyMatrix4(inv);
    if(v.lengthSq()<1e-6)return;const [x,z]=plotXY(w,v.clone());if(!OCC.some(r=>Math.hypot(x-r.x,z-r.z)<=r.r+.25)&&occFar(w,v.clone(),.3)){outside++;if(i===1&&outEx.length<12)outEx.push([x.toFixed(2),z.toFixed(2),o.geometry.type])}});
  out.push({i,n:PLANETS[i].n,type:PTYPE(i),feats,bad:bad.length,first:bad.slice(0,3),parts,outside})});
out.ex=window.__outEx;return JSON.stringify({out,ex:window.__outEx})})()"""
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
  pg.goto(f'http://localhost:{port}/index.html');pg.wait_for_timeout(5000)
  try:pg.click('#nmOk',timeout=3000)
  except Exception:pass
  rr=json.loads(pg.evaluate(JS));res=rr['out'];print('examples outside (planet 1):',rr['ex'])
srv.kill()
fail=0
for r in res:
  ok=r['bad']==0;fail+=0 if ok else 1
  print(f"{'PASS' if ok else 'FAIL'} {r['i']:2d} {r['n']:<13} {r['type']:<5} features {r['feats']:4d} overlaps {r['bad']} base parts {r['parts']} outside reservations {r['outside']} {r['first'] if not ok else ''}")
print('ALL PASS' if fail==0 else f'{fail} planets FAIL','| page errors:',errs)
sys.exit(1 if fail or errs else 0)
