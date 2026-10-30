import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # the repository root, served as the game
OUT=_os.environ.get('SQ_OUT',_os.path.join(ROOT,'out'));_os.makedirs(OUT,exist_ok=True)  # screenshots (git-ignored)
import subprocess,time,sys,base64
from playwright.sync_api import sync_playwright
srv=subprocess.Popen([sys.executable,'-m','http.server',sys.argv[1],'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
errs=[];logs=[]
with sync_playwright() as p:
  b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:logs.append(m.text) if m.type in('warning','error') and 'Failed to load' not in m.text else None);E=lambda js:pg.evaluate(js)
  pg.goto(f'http://localhost:{sys.argv[1]}/index.html');pg.wait_for_timeout(6000);pg.click('#nmOk');E("S.tut=2;0")
  print('nebula',E("!!nebula"))
  # panorama dump
  d=E("""(()=>{const rt=nebula.material.map,W=512,H=256;const t=new THREE.WebGLRenderTarget(W,H);const sc=new THREE.Scene(),m=new THREE.Mesh(new THREE.PlaneGeometry(2,2),new THREE.MeshBasicMaterial({map:rt}));sc.add(m);
    const c=new THREE.OrthographicCamera(-1,1,1,-1,0,1);const pr=renderer.getRenderTarget();renderer.setRenderTarget(t);renderer.render(sc,c);const px=new Uint8Array(W*H*4);renderer.readRenderTargetPixels(t,0,0,W,H,px);renderer.setRenderTarget(pr);
    const cv=document.createElement('canvas');cv.width=W;cv.height=H;const g=cv.getContext('2d'),im=g.createImageData(W,H);for(let y=0;y<H;y++)for(let x=0;x<W;x++){const i=((H-1-y)*W+x)*4,j=(y*W+x)*4;for(let k=0;k<3;k++)im.data[j+k]=Math.min(255,px[i+k]*3);im.data[j+3]=255}g.putImageData(im,0,0);return cv.toDataURL('image/png')})()""")
  open(OUT+'/neb_pano.png','wb').write(base64.b64decode(d.split(',')[1]))
  E("if(!sheet.classList.contains('collapsed'))toggleSheet();0");pg.wait_for_timeout(1500)
  for k,th in enumerate([.6,2.2,3.8,5.2]):
    E(f"cam.theta={th};0");pg.wait_for_timeout(1200);pg.screenshot(path=f'{OUT}/neb_{k}.png')
srv.kill();print('errors',errs,logs[:3])
