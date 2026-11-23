# Arnés común de las pruebas de DEIROS Fleet.
# Carga la app REAL (../index.html) en Chromium sin pantalla, a 390 px, con:
#  · Firebase falso EN MEMORIA (Auth + Firestore compat: documentos, subcolecciones, where(documentId,'in'),
#    FieldPath, runTransaction y «modo lento»). Nada sale a internet.
#  · Datos de prueba FICTICIOS (ningún cliente real): 6 coches, propietario, clientes, presupuestos y movimientos.
#  · Fecha y reloj fijos: 20/11/2026 10:00 en Madrid (se puede cambiar por prueba con new_context(..., fecha=...)).
#  · jsPDF, xlsx y fuentes servidos desde tests/.cache/ (ver vendor.py); precios de carburante falsos.
# Uso desde una prueba:  import harness as H  ·  with H.playwright() as p: br=H.launch(p); ctx,pg=H.open_app(br)
import os,sys,re,json,copy,datetime

TESTS=os.path.dirname(os.path.abspath(__file__))
REPO=os.path.dirname(TESTS)
# DEIROS_INDEX permite probar otra copia (p. ej. la de una rama); por defecto, el index.html del repo
INDEX=os.path.abspath(os.environ.get('DEIROS_INDEX') or os.path.join(REPO,'index.html'))
if TESTS not in sys.path:sys.path.insert(0,TESTS)
# DEIROS_CAPTURAS=<carpeta>: algunas pruebas guardan ahí capturas de pantalla (opcional)
CAPTURAS=os.environ.get('DEIROS_CAPTURAS','')
if CAPTURAS:os.makedirs(CAPTURAS,exist_ok=True)
import vendor

# ───────────────────────── Fecha fija ─────────────────────────
FECHA='2026-11-20T10:00:00+01:00'      # «ahora» en el navegador (Europe/Madrid)
TZ='Europe/Madrid'
HOY=datetime.date(2026,11,20)
AHORA=datetime.datetime(2026,11,20,10,0,0)
FECHA_TS=datetime.datetime.fromisoformat(FECHA).timestamp()   # «ahora» del navegador en segundos (epoch)
def d(n,base=None):
    """Fecha ISO (AAAA-MM-DD) a n días de hoy (fijo)."""
    return ((base or HOY)+datetime.timedelta(days=n)).isoformat()
def iso(n,h=10,m=0):
    """Fecha-hora ISO en UTC a n días de hoy, a la hora local h:m de Madrid."""
    t=datetime.datetime.combine(HOY+datetime.timedelta(days=n),datetime.time(h,m))
    off=1 if not (3<t.month<10 or (t.month==3 and t.day>=29) or (t.month==10 and t.day<25)) else 2  # suficiente para 2026
    return (t-datetime.timedelta(hours=off)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
MES=HOY.strftime('%Y-%m')
MES_ANT=(HOY.replace(day=1)-datetime.timedelta(days=3)).strftime('%Y-%m')

# ───────────────────────── Datos ficticios ─────────────────────────
OWN,MAN='#8B5CF6','#14B8A6'
def _bk(i,s,e,cl,amt,pl='sinapp',st='10:00',et='10:00',**k):
    b={'id':'b'+str(i),'startDate':d(s),'startTime':st,'endDate':d(e),'endTime':et,'platform':pl,'amount':amt,'clientName':cl,'finance':[],'extras':[]};b.update(k);return b
def datos():
    """Copia nueva de los datos de prueba (data/main). Todo inventado."""
    m,pm=MES,MES_ANT
    V=[
     {'id':'v1','name':'Ford Focus','plate':'0000AAA','model':'Focus','year':2019,'vtype':'own','color':OWN,'vehicle_type':'turismo','fuel':'Gasolina','km':98000,'itv_date':d(40),'insurance_date':d(90),'finances':[],
      'bookings':[_bk(1,6,9,'Lucía Herrera Gómez',120,'amovens','09:30','19:00')]},
     {'id':'v2','name':'Fiat','plate':'1111BBB','model':'Fiorino','year':2020,'vtype':'managed','commission':30,'ownerId':'o1','color':MAN,'vehicle_type':'l1h1','fuel':'Diésel','km':120000,'itv_date':d(-3),'insurance_date':d(80),
      'finances':[{'id':'e5','type':'expense','amount':120,'date':m+'-03','category':'Reparación','desc':'Pastillas de freno'}],
      'bookings':[_bk(2,-16,0,'María Fernanda Castillo Rodríguez',155,'sinapp','08:00','08:00',clientPhone='600 000 001',fianza=200,delivered=True,abonoReserva=200)]},
     {'id':'v3','name':'Renault','plate':'2222CCC','model':'Clio','year':2018,'vtype':'own','color':OWN,'vehicle_type':'turismo','fuel':'Gasolina','km':143000,'itv_date':d(120),'insurance_date':d(6),
      'finances':[{'id':'e1','type':'expense','amount':356.4,'date':m+'-05','category':'Seguro','desc':'Póliza trimestral'},{'id':'e2','type':'expense','amount':62.3,'date':m+'-09','category':'Combustible','desc':''},
                  {'id':'e3','type':'income','amount':414.99,'date':m+'-02','category':'Alquiler','desc':'Alquiler mensual'},{'id':'e4','type':'expense','amount':189,'date':pm+'-14','category':'Mantenimiento periódico','desc':'Aceite y filtros','km':139800}],
      'bookings':[_bk(3,-32,17,'Alejandro José Martínez de la Fuente',414.99,'sinapp','21:00','20:00',clientPhone='600 000 002',clientDni='00000001R',fianza=200,delivered=True,abonoReserva=300,kmStart=140100,notes='Entrega en Pinto centro'),
                  _bk(31,20,24,'Jorge P.',160,'getaround')]},
     {'id':'v4','name':'Peugeot','plate':'3333DDD','model':'208','year':2021,'vtype':'own','color':OWN,'vehicle_type':'turismo','fuel':'Gasolina','km':48210,'itv_date':d(200),'insurance_date':d(24),'maint_km':39500,'finances':[],
      'bookings':[_bk(4,-5,3,'Diego Alexander González Santamaría',80,'sinapp','10:00','10:00',fianza=200,delivered=True),_bk(41,-40,-37,'Marta Ruiz',150,'sinapp',returned=True,delivered=True,paid=True,cobrado=True)]},
     {'id':'v5','name':'Citroën C3','plate':'4444EEE','model':'C3','year':2020,'vtype':'own','color':OWN,'vehicle_type':'turismo','fuel':'Diésel','km':77000,'itv_date':d(60),'insurance_date':d(150),'finances':[],
      'bookings':[_bk(5,-17,13,'Francisco Javier García Cea',540,'sinapp','11:00','11:00',fianza=200,delivered=True,abonoReserva=740)],'calendar':{d(15):'maintenance',d(16):'maintenance'}},
     {'id':'v6','name':'Seat Ibiza','plate':'5555FFF','model':'Ibiza','year':2016,'vtype':'own','vehicle_type':'turismo','archived':True,'archiveReason':'sold','color':'#8B5CF6','finances':[],'bookings':[]}]
    return {'rev':1,'vehicles':V,
     'bizFinances':[{'id':'f1','type':'income','amount':1480,'date':m+'-03','category':'Alquiler','desc':'Liquidación Amovens'},{'id':'f2','type':'expense','amount':356.4,'date':m+'-05','category':'Seguro','desc':'Flota'},
                    {'id':'f7','type':'expense','amount':29.99,'date':m+'-07','category':'Suscripción','desc':'Software'},{'id':'f3','type':'income','amount':1210,'date':pm+'-10','category':'Alquiler'},{'id':'f4','type':'expense','amount':420,'date':pm+'-12','category':'Reparación'}],
     'owners':[{'id':'o1','name':'Ana Propietaria Ejemplo','dni':'00000000T','phone':'600 000 002','email':'ana@ejemplo.es','iban':'ES0000000000000000000000'}],
     'clients':[{'id':'c1','name':'Alejandro José Martínez de la Fuente','dni':'00000001R','phone':'600 000 002','email':'alejandro@ejemplo.es','rating':4,'bookingIds':['b3'],'address':'C/ Ejemplo 1, 28320 Pinto','birthdate':'1990-05-14','nationality':'Española','license':'00000001R','licenseExp':d(300)},
                {'id':'c2','name':'María Fernanda Castillo Rodríguez','dni':'00000002W','phone':'600 000 001','bookingIds':['b2'],'rating':5},{'id':'c3','name':'Marta Ruiz','dni':'00000003A','phone':'600 000 003','bookingIds':['b41'],'licenseExp':d(20)}],
     'recurring':[{'id':'r1','name':'Seguro flota','category':'Seguro','freq':'monthly','amount':356.4,'active':True,'lastApplied':m+'-05'},{'id':'r2','name':'Parking nave','category':'Parking','freq':'monthly','amount':90,'active':True},
                  {'id':'r3','name':'Impuesto circulación','category':'Impuesto','freq':'yearly','amount':112,'active':False,'vId':'v3'}],
     'quotes':[{'id':'q1','num':'PRE-2026-0042','vehicleId':'v4','clientName':'Lucía Herrera Gómez','clientId':'','createdAt':d(-1)+'T10:00:00','startDate':d(12),'startTime':'10:00','endDate':d(16),'endTime':'10:00','dur':4,'baseAmount':116,'extras':[],'discount':0,'fianza':200,'status':'pendiente','total':116},
               {'id':'q2','num':'PRE-2026-0041','vehicleId':'v1','clientName':'Jorge P.','createdAt':d(-6)+'T10:00:00','startDate':d(-2),'startTime':'10:00','endDate':d(5),'endTime':'10:00','dur':7,'baseAmount':175,'extras':[],'discount':0,'fianza':200,'status':'aceptado','total':175},
               {'id':'q3','num':'PRE-2026-0039','vehicleId':'v2','clientName':'Mudanzas Ejemplo S.L.','createdAt':d(-20)+'T10:00:00','startDate':d(-15),'startTime':'10:00','endDate':d(-14),'endTime':'10:00','dur':1,'baseAmount':35,'extras':[],'discount':0,'fianza':200,'status':'rechazado','total':35}]}
D0=datos()
COMPANY={'nombre':'DEIROS','nif':'B00000000','direccion':'C/ Ejemplo 12, 28320 Pinto','telefono':'600 000 000','ciudad':'Pinto'}
# Datos de empresa ficticios en localStorage (como los guarda la app en cada móvil)
FAKE="localStorage.setItem('deiros_company',%s);"%json.dumps(json.dumps(COMPANY))
# Precios de carburante falsos (mismo formato que publica el robot del Ministerio)
FUELDATA={'v':1,'fecha':'15/11/2026 6:30:12','productos':['e5','ga','glp'],
  'm':[['Pinto','MADRID',1.539,12,1.429,11,0.959,2],['Valdemoro','MADRID',1.549,9,1.439,9,None,0],['Getafe','MADRID',1.529,30,1.419,28,0.949,3]],
  'e':[[40.244,-3.700,0],[40.246,-3.703,0],[40.193,-3.678,1],[40.305,-3.731,2]]}

# ───────────────────────── Firebase falso ─────────────────────────
# Firestore en memoria (window.__FS: ruta → documento). Rutas users/demo/... (usuario «demo»).
#  · window.__FSOPS: rutas escritas · window.__FSQ: consultas where · window.__DENY: niega las rutas /actas
#  · window.__SLOW: las lecturas de /actas tardan 12 s · sin red (navigator.onLine=false) las lecturas fallan
#    y las escrituras esperan a que vuelva la red (como el SDK).
STUB=r"""(function(){
const FS=window.__FS={};window.__FSOPS=[];window.__FSDENY=!!window.__DENY;
const clone=x=>x===undefined?undefined:JSON.parse(JSON.stringify(x));
function res(v){if(v&&v.__st)return {seconds:Math.floor(Date.now()/1000),nanoseconds:0};if(Array.isArray(v))return v.map(res);if(v&&typeof v==='object'){const o={};for(const k in v)o[k]=res(v[k]);return o;}return v;}
const deny=p=>window.__FSDENY&&/\/actas(\/|$)/.test(p);
const err=(c,m)=>Object.assign(new Error(m),{code:c});
function online(){return new Promise(ok=>{if(navigator.onLine)return ok();window.addEventListener('online',function h(){window.removeEventListener('online',h);ok();});});}
async function W(p,fn){await new Promise(r=>setTimeout(r,5));if(deny(p))throw err('permission-denied','Missing or insufficient permissions.');await online();fn();window.__FSOPS.push(p);}
async function R(p){await new Promise(r=>setTimeout(r,window.__SLOW&&/\/actas/.test(p)?12000:5));if(deny(p))throw err('permission-denied','Missing or insufficient permissions.');if(!navigator.onLine)throw err('unavailable','offline');}
function Doc(path){this.path=path;this.id=path.split('/').pop();}
Doc.prototype.collection=function(n){return new Col(this.path+'/'+n);};
Doc.prototype.get=async function(){await R(this.path);const d=FS[this.path];return {exists:d!==undefined,id:this.id,ref:this,data:()=>clone(d)};};
Doc.prototype.set=function(data,o){const p=this.path;return W(p,()=>{const v=res(clone(data));FS[p]=o&&o.merge?Object.assign({},FS[p]||{},v):v;});};
Doc.prototype.update=function(data){const p=this.path;return W(p,()=>{FS[p]=Object.assign({},FS[p]||{},res(clone(data)));});};
Doc.prototype.delete=function(){const p=this.path;return W(p,()=>{delete FS[p];});};
Doc.prototype.onSnapshot=function(){return()=>{};};
function Col(path){this.path=path;}
Col.prototype.doc=function(id){return new Doc(this.path+'/'+(id||Math.random().toString(36).slice(2)));};
Col.prototype.get=async function(){await R(this.path);const pre=this.path+'/';const docs=Object.keys(FS).filter(k=>k.startsWith(pre)&&k.slice(pre.length).indexOf('/')<0).map(k=>{const r=new Doc(k);return {id:r.id,ref:r,exists:true,data:()=>clone(FS[k])};});return {docs,size:docs.length,empty:!docs.length,forEach:f=>docs.forEach(f)};};
Col.prototype.where=function(f,op,vals){const col=this;return {get:async function(){await R(col.path);const docs=(vals||[]).map(id=>col.path+'/'+id).filter(k=>FS[k]!==undefined).map(k=>{const r=new Doc(k);return {id:r.id,ref:r,exists:true,data:()=>clone(FS[k])};});window.__FSQ=(window.__FSQ||0)+1;return {docs,size:docs.length,empty:!docs.length,forEach:f=>docs.forEach(f)};}};};
const dbo={collection:n=>new Col(n),enablePersistence:async()=>{},runTransaction:async fn=>{const ops=[];const tx={get:r=>r.get(),set:(r,d,o)=>{ops.push(()=>r.set(d,o));return tx;},update:(r,d)=>{ops.push(()=>r.update(d));return tx;}};const out=await fn(tx);for(const o of ops)await o();return out;}};
const fsf=function(){return dbo;};fsf.FieldValue={serverTimestamp:()=>({__st:1})};fsf.FieldPath={documentId:()=>'__name__'};
window.firebase={initializeApp(){},auth(){return{onAuthStateChanged(cb){setTimeout(()=>cb({uid:'demo'}),30)},signOut(){},signInWithEmailAndPassword(){return Promise.reject()}}},firestore:fsf};
FS['users/demo/data/main']=clone(window.__DATA);
if(window.__ACTAS)Object.assign(FS,clone(window.__ACTAS));
})();"""

# ───────────────────────── Red simulada ─────────────────────────
_FONT_CSS=("".join("@font-face{font-family:'Syne';src:url(https://fonts.local/syne-%d.woff2) format('woff2');font-weight:%d}"%(w,w) for w in (400,500,600,700,800))+
           "".join("@font-face{font-family:'JetBrains Mono';src:url(https://fonts.local/jbm-%d.woff2) format('woff2');font-weight:%d}"%(w,w) for w in (400,500,600))+
           "@font-face{font-family:'Doto';src:url(https://fonts.local/doto-900.woff2) format('woff2');font-weight:100 900}")
_vendor_ok=[False]
def prepare():
    """Prepara la caché de librerías (una vez por proceso)."""
    if not _vendor_ok[0]:
        vendor.ensure(verbose=False);_vendor_ok[0]=True
def make_route(stub=None):
    """Devuelve el manejador de rutas: Firebase falso (stub), librerías y fuentes de la caché; nada sale a internet."""
    prepare()
    def route(r):
        u=r.request.url
        if u.startswith('file://') or u.startswith('data:') or u.startswith('blob:'):return r.continue_()
        if 'firebase-app-compat' in u:return r.fulfill(body=stub or STUB,content_type='text/javascript')
        if 'firebasejs' in u:return r.fulfill(body='',content_type='text/javascript')
        if 'precios.json' in u:return r.fulfill(body=json.dumps(FUELDATA),content_type='application/json')
        for k,f in (('jspdf','jspdf.umd.min.js'),('xlsx','xlsx.full.min.js')):
            if k in u:
                if vendor.have(f):return r.fulfill(path=vendor.path(f),content_type='text/javascript')
                return r.fulfill(body='',content_type='text/javascript')
        if 'fonts.googleapis' in u:return r.fulfill(body=_FONT_CSS,content_type='text/css')
        if u.startswith('https://fonts.local/'):
            f=u.rsplit('/',1)[1]
            if vendor.have(f):return r.fulfill(path=vendor.path(f),content_type='font/woff2')
        return r.fulfill(status=404,body='')
    return route
route=make_route()

# ───────────────────────── Navegador ─────────────────────────
def playwright():
    from playwright.sync_api import sync_playwright
    return sync_playwright()
def launch(p):
    exe=os.environ.get('DEIROS_CHROME') or None
    return p.chromium.launch(executable_path=exe,args=['--no-sandbox'])
def init_script(data=None,theme='dark',extra=''):
    return ("window.__DATA=%s;localStorage.setItem('wg_theme','%s');localStorage.setItem('deiros_lastBackupAt',new Date().toISOString());%s"
            %(json.dumps(D0 if data is None else data),theme,extra))
def new_context(br,fecha=FECHA,tz=TZ,stub=None,routes=True,**kw):
    """Contexto de navegador de 390×844 con la fecha fija, la zona horaria de Madrid y la red simulada."""
    o=dict(viewport={'width':390,'height':844},device_scale_factor=1,timezone_id=tz,locale='es-ES');o.update(kw)
    ctx=br.new_context(**o)
    if fecha:ctx.clock.install(time=fecha)
    if routes:ctx.route('**/*',make_route(stub) if stub else route)
    return ctx
def open_app(br,data=None,extra='',theme='dark',company=True,wait=2000,errs=None,tag='',actas=None,**kw):
    """Abre la app con los datos dados. extra: JS de arranque (antes de la app). errs: lista donde anotar errores JS."""
    ctx=new_context(br,**kw)
    ex=extra
    if actas is not None:ex="window.__ACTAS=%s;"%json.dumps(actas)+ex
    ctx.add_init_script(init_script(data,theme,ex))
    if company:ctx.add_init_script(FAKE)
    pg=ctx.new_page()
    E=ERRS if errs is None else errs
    pg.on('pageerror',lambda e:E.append((tag+': ' if tag else '')+str(e)))
    pg.goto('file://'+INDEX);pg.wait_for_timeout(wait)
    return ctx,pg

# ───────────────────────── Resultados ─────────────────────────
OK=[0];BAD=[0];ERRS=[];FALLOS=[]
def chk(c,m,i=''):
    """Una comprobación: imprime OK/FALLO y la cuenta."""
    c=bool(c);m=re.sub(r"\s*\n\s*"," | ",str(m))
    i=re.sub(r"\s*\n\s*"," | ",str(i)) if i!='' and i is not None else ''
    print(('OK    ' if c else 'FALLO ')+m+(' · '+i if i and (not c or len(i)<160) else ''),flush=True)
    if c:OK[0]+=1
    else:BAD[0]+=1;FALLOS.append(m)
ok=lambda m,c,i='':chk(c,m,i)
def fin():
    """Comprueba que no hubo errores JS, imprime el resumen y sale con 0 (todo OK) o 1."""
    chk(not ERRS,'Sin errores JS en la página',ERRS[:5])
    print('\nRESUMEN: %d OK, %d fallos'%(OK[0],BAD[0]),flush=True)
    sys.exit(1 if BAD[0] else 0)
def N(x):
    """Quita los espacios duros de los importes (1.234,00 €)."""
    return x.replace('\xa0',' ').replace(' ',' ') if isinstance(x,str) else x

# Texto de los PDF: envuelve jsPDF para anotar cada text() — en el navegador: await __pdfText(()=>fn()) (sin las líneas con hora)
# o await __pdfText(()=>fn(),true) (todas). Un error al generar queda como «ERROR …» en la lista.
PDFTEXT=r"""window.__pdfText=async function(fn,todo){await ensureLib('jspdf');const O=window.jspdf.jsPDF;const L=[];
  const W=function(){const d=new O(...arguments);const t=d.text;d.text=function(x){L.push(Array.isArray(x)?x.join(' '):String(x));return t.apply(this,arguments);};return d;};
  Object.assign(W,O);W.API=O.API;window.jspdf.jsPDF=W;const s=window._savePDF;window._savePDF=()=>{};
  try{await fn();}catch(e){L.push('ERROR '+e.message);}finally{window.jspdf.jsPDF=O;window._savePDF=s;}return todo?L:L.filter(t=>!/\d{1,2}:\d{2}/.test(t));};true"""

# Resumen de importes (para fijar valores esperados): liquidación y comisión por coche, ingresos/gastos por coche,
# negocio por mes y KPI del Resumen. Uso: pg.evaluate(H.MONEY)
MONEY=r"""(()=>{const r={};const R2=x=>Math.round(x*100)/100,pick=o=>['tI','tE','commAmt','toOwner','deficit','mgr'].map(k=>R2(o[k]));
  r.settle=Object.fromEntries(V.filter(v=>v.vtype==='managed').map(v=>[v.id,pick(_settleTotals(v,_getVehicleAllFinances(v)))]));
  r.tIncExp=Object.fromEntries(V.map(v=>[v.id,[R2(tInc(v)),R2(tExp(v))]]));
  const be={};_getBizEntriesWithMgmt().forEach(e=>{const k=e.date.slice(0,7)+' '+e.type;be[k]=R2((be[k]||0)+Number(e.amount));});r.biz=be;
  nav('dashboard');r.dash=(document.getElementById('PC').innerHTML.replace(/&nbsp;/g,' ').match(/(INGRESOS MES|GASTOS MES|BENEFICIO[^<]*)<b[^>]*>[^<]+<\/b>/g)||[]).map(t=>t.replace(/<[^>]+>/g,' ').replace(/[\u00a0\u202f]/g,' ').replace(/\s+/g,' ').trim());
  return r;})()"""

# ───────────────────────── Fotos de prueba ─────────────────────────
# Fotos sintéticas (degradados, formas y grano: nada real), generadas con Pillow en una carpeta temporal:
#  big.jpg (4032×3024, como la de un móvil) y muestras de 1280×960 con el nombre del hueco (entrega_frontal.jpg…).
_FOTOS=[None]
def fotos_prueba():
    if _FOTOS[0]:return _FOTOS[0]
    import tempfile,random
    from PIL import Image,ImageDraw,ImageChops
    out=tempfile.mkdtemp(prefix='deiros_fotos_')
    def img(w,h,seed,label,noise=0):
        rnd=random.Random(seed)
        im=Image.new('RGB',(w,h));dr=ImageDraw.Draw(im)
        c1=[rnd.randint(40,200) for _ in range(3)];c2=[rnd.randint(40,200) for _ in range(3)]
        for y in range(0,h,4):
            t=y/h;dr.rectangle((0,y,w,y+4),fill=tuple(int(a+(b-a)*t) for a,b in zip(c1,c2)))
        for _ in range(14):
            x,y=rnd.randint(0,w),rnd.randint(0,h);r=rnd.randint(w//30,w//6)
            dr.ellipse((x-r,y-r,x+r,y+r),fill=tuple(rnd.randint(0,255) for _ in range(3)))
        dr.rectangle((w//5,h//2,w*4//5,h*4//5),fill=(30,30,40));dr.text((w//20,h//20),label,fill=(255,215,0))
        if noise:im=ImageChops.add(im,Image.effect_noise((w,h),noise).convert('RGB'),1.0,-128)
        return im
    img(4032,3024,1,'big',noise=40).save(os.path.join(out,'big.jpg'),'JPEG',quality=92)
    n=2
    for fase in ('entrega','devolucion'):
        for t in ('frontal','lat_der','trasera','lat_izq','interior','cuadro','dano1','dano2'):
            img(1280,960,n,fase+' '+t,noise=8).save(os.path.join(out,'%s_%s.jpg'%(fase,t)),'JPEG',quality=80);n+=1
    _FOTOS[0]=out;return out
