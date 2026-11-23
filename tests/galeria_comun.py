# Utilidades comunes de test_galeria.py y test_copia_fotos.py (galería de 8 fotos por coche, #123 y #126):
# Firebase falso del arnés + reglas que no dejan en «vehiculos» y «nube de la galería que no responde» (window.__OFFV),
# fotos sintéticas «de móvil» (3024 px con grano), galería sembrada en la nube y menú de compartir simulado.
# Origen: la cabecera de specs/g123/test_g123.py.
import sys,os,json,datetime,base64,io,re,tempfile,time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
from PIL import Image,ImageChops,ImageDraw,ImageEnhance
from playwright.sync_api import sync_playwright
NEW=H.INDEX;SHOTS=H.CAPTURAS
D=H.datos();FAKE0=H.FAKE
TMP=tempfile.mkdtemp(prefix='g123_')
BIG=Image.open(os.path.join(H.fotos_prueba(),'big.jpg')).convert('RGB')
def phone(i,lbl,w=3024,days=0):
    x,y=(i*97)%900,(i*61)%700
    c=BIG.crop((x,y,x+w,y+w*3//4))
    c=ImageEnhance.Color(c).enhance(0.6+0.15*i);c=ImageEnhance.Brightness(c).enhance(0.85+0.05*(i%4))
    n=Image.effect_noise(c.size,10).convert('RGB');c=ImageChops.add(c,n,1.0,-128)
    dr=ImageDraw.Draw(c);dr.rectangle((40,40,620,190),fill=(20,20,20));dr.text((70,90),lbl,fill=(255,255,255))
    p=os.path.join(TMP,'foto_%02d.jpg'%i);c.save(p,'JPEG',quality=85)
    t=H.FECHA_TS-60-days*86400;os.utime(p,(t,t))   # fecha de la foto: respecto al reloj fijo del arnés
    return p
FOT={i:phone(i,'FOTO %d'%i,days=(10 if i==1 else 0)) for i in range(1,10)}
MT1=datetime.datetime.fromtimestamp(os.path.getmtime(FOT[1]),datetime.timezone.utc)
def durl(img,q=88):
    b=io.BytesIO();img.save(b,'JPEG',quality=q);return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
OLD3=durl(BIG.crop((300,200,3500,2600)).resize((1600,1200)));OLD2=durl(BIG.crop((0,0,4000,3000)).resize((1400,1050)).transpose(Image.FLIP_LEFT_RIGHT))
# Galería ya en la nube para v5 (posiciones 1 y 2) para la prueba «sin saber lo que hay en la nube»
def th(img):t=img.copy();t.thumbnail((240,240));return durl(t,60)
SEED={}
g5=[]
for pos in (1,2):
    im=BIG.crop((pos*200,100,pos*200+2400,1900)).resize((1280,960));fid='seed%d'%pos
    SEED['users/demo/vehiculos/v5/fotos/'+fid]={'v':1,'vid':'v5','pos':pos,'at':'2026-11-01T10:00:00.000Z','kb':200,'img':durl(im,65)}
    g5.append({'id':fid,'pos':pos,'at':'2026-11-01T10:00:00.000Z','kb':200,'th':th(im)})
SEED['users/demo/vehiculos/v5']={'v':1,'vid':'v5','kb':400,'fotos':g5,'subida':{'seconds':1}}
STUB=H.STUB
# Reglas que no dejan (actas y vehiculos) y «la nube de la galería no responde» (window.__OFFV)
STUB=STUB.replace("const deny=p=>window.__FSDENY&&/\\/actas(\\/|$)/.test(p);","const deny=p=>window.__FSDENY&&/\\/(actas|vehiculos)(\\/|$)/.test(p);")
STUB=STUB.replace("async function W(p,fn){await new Promise(r=>setTimeout(r,5));","async function W(p,fn){await new Promise(r=>setTimeout(r,5));if(window.__OFFV&&/\\/vehiculos/.test(p))throw err('unavailable','offline');")
STUB=STUB.replace("async function R(p){await new Promise(r=>setTimeout(r,window.__SLOW&&/\\/actas/.test(p)?12000:5));","async function R(p){await new Promise(r=>setTimeout(r,window.__SLOW&&/\\/actas/.test(p)?12000:5));if(window.__OFFV&&/\\/vehiculos/.test(p))throw err('unavailable','offline');")
assert 'vehiculos)' in STUB and STUB.count('__OFFV')==2 and 'FieldPath' in STUB
SHARE="""window.__SH=[];window.__CAN=true;navigator.canShare=()=>window.__CAN;navigator.share=async d=>{if(window.__ABORT)throw Object.assign(new Error('x'),{name:'AbortError'});const L=d.files||[];const rd=f=>new Promise(r=>{const x=new FileReader();x.onload=()=>r(x.result);x.readAsDataURL(f);});window.__SH.push({n:L.length,names:L.map(f=>f.name),types:L.map(f=>f.type),sizes:L.map(f=>f.size),title:d.title,act:navigator.userActivation?navigator.userActivation.isActive:null,first:L.length?await rd(L[0]):''});};"""
R=[];ERR=H.ERRS
def ok(name,cond,info=''):H.chk(cond,name,str(info)[:300] if info!='' else '')
def wait(pg,ms=600):pg.wait_for_timeout(ms)
def new_page(b,html,seed=None,deny=False,offv=False,old=True):
    ctx=H.new_context(b,accept_downloads=True,stub=STUB)
    ini="window.__DATA=%s;window.__ACTAS=%s;window.__DENY=%s;window.__OFFV=%s;localStorage.setItem('wg_theme','dark');localStorage.setItem('deiros_lastBackupAt',new Date().toISOString());localStorage.setItem('deiros_flotaView','extended');localStorage.setItem('deiros_fx_day','demo|'+(d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'))(new Date()));window.alert=m=>{(window.__AL=window.__AL||[]).push(m)};window.__CFR=true;window.confirm=m=>{(window.__CF=window.__CF||[]).push(m);return window.__CFR};"%(json.dumps(D),json.dumps(seed or {}),'true' if deny else 'false','true' if offv else 'false')
    if old:ini+="if(!sessionStorage.getItem('i')){sessionStorage.setItem('i','1');localStorage.setItem('wg_photo_v3',%s);localStorage.setItem('wg_photo_v2',%s);}"%(json.dumps(OLD3),json.dumps(OLD2))
    ctx.add_init_script(ini+SHARE);ctx.add_init_script(FAKE0)
    pg=ctx.new_page();tag=os.path.basename(os.path.dirname(html))+'/'+os.path.basename(html)
    pg.on('pageerror',lambda e:ERR.append(tag+': '+str(e)))
    pg.goto('file://'+os.path.abspath(html));wait(pg,3200)
    pg.evaluate("window.__toasts=[];new MutationObserver(m=>m.forEach(r=>r.addedNodes.forEach(n=>{if(n.classList&&n.classList.contains('d-toast'))window.__toasts.push(n.textContent)}))).observe(document.body,{childList:true})")
    return ctx,pg
def fs_keys(pg,pre):return pg.evaluate("p=>Object.keys(window.__FS).filter(k=>k.startsWith(p)).sort()",pre)
def fs(pg,k):return pg.evaluate("k=>JSON.parse(JSON.stringify(window.__FS[k]===undefined?null:window.__FS[k]))",k)
def gal(pg,vid):return pg.evaluate("v=>JSON.parse(JSON.stringify(_fx.A['veh:'+v]||null))",vid)
def poss(gd):return [f['pos'] for f in (gd or {}).get('fotos',[])]
def qn(pg):return pg.evaluate("_fxAll('q').then(L=>L.length)")
def bko(pg):return pg.evaluate("(()=>{const o=_backupObject();delete o.exportedAt;return JSON.stringify(o)})()")
def info(pg,vid):pg.evaluate("v=>{_gxVClose();closeSheet();openV(v);switchTab('info')}",vid);wait(pg,1500)
def shoot(pg,btn,files,vid,n):
    with pg.expect_file_chooser() as fc:pg.locator('#gxV button',has_text=btn).click()
    ch=fc.value;mul=ch.is_multiple();cap=pg.evaluate("document.getElementById('gxFile').getAttribute('capture')")
    ch.set_files(files);pg.wait_for_function("([v,n])=>_fx.A['veh:'+v]&&_fx.A['veh:'+v].fotos.length===n&&!_gx.busy",arg=[vid,n],timeout=30000);wait(pg,300)
    return mul,cap
def img_of(dataurl):return Image.open(io.BytesIO(base64.b64decode(dataurl.split(',',1)[1])))
