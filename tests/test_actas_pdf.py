# Actas de entrega y devolución en PDF (#105, PR 2): las dos actas con 0, 3 y 8 fotos (nombre, páginas, imágenes,
# textos de partes, km, daños, cargos y fianza, hora de cada foto, < 1 MB), generar no escribe nada en la nube, «Generar acta»
# (descarga) y «Enviar acta» (menú de compartir, también sin toque activo), acta sin red con miniaturas y «SIN FOTO», avisos
# al confirmar entrega y devolución, borrar un alquiler o un coche avisa de cuántas fotos se borran (nube lenta y sin red).
# Origen: specs/fotos105/test_pr2.py. Quitado: «main no avisaba» y «el resto de PDF igual que main» (ver test_pdfs.py).
# Necesita pdftotext/pdfinfo/pdfimages (poppler-utils). Fotos sintéticas del arnés. Uso: python3 tests/test_actas_pdf.py
import sys,os,json,datetime,base64,io,re,subprocess,tempfile,time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
from PIL import Image,ImageChops,ImageDraw
from playwright.sync_api import sync_playwright
NEW=H.INDEX;SHOTS=H.CAPTURAS
D=H.datos();FAKE0=H.FAKE
hoy=H.HOY;d=H.d;iso=H.iso
TMP=tempfile.mkdtemp(prefix='f105b_')
hoy=H.HOY
BIG=Image.open(os.path.join(H.fotos_prueba(),'big.jpg'))
def foto(i,portrait=False,label=''):
    x,y=(i*331)%1500,(i*197)%1100
    c=BIG.crop((x,y,x+2400,y+1800)).resize((1280,960))
    if portrait:c=c.rotate(90,expand=True)
    n=Image.effect_noise(c.size,13).convert('RGB');c=ImageChops.add(c,n,1.0,-128)
    dr=ImageDraw.Draw(c);dr.rectangle((c.size[0]-330,c.size[1]-40,c.size[0],c.size[1]),fill=(0,0,0));dr.text((c.size[0]-320,c.size[1]-30),label,fill=(255,215,0))
    b=io.BytesIO();c.save(b,'JPEG',quality=65);big='data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
    t=c.copy();t.thumbnail((240,240));b2=io.BytesIO();t.save(b2,'JPEG',quality=60);th='data:image/jpeg;base64,'+base64.b64encode(b2.getvalue()).decode()
    return big,th,len(b.getvalue())//1024
GUIA=['frontal','lat_der','trasera','lat_izq','interior','cuadro']
ACTAS={};KB=[]
def acta(bid,fase,fotos,km,comb,at,lugar='',nota='',vid='',borradas=None):
    F=[];k=0
    for i,(tipo,extra) in enumerate(fotos):
        fid=f'{bid}{fase[0]}{i}';big,th,kb=foto(i+(7 if fase=='devolucion' else 0),portrait=(tipo=='interior'),label=f'{bid} {fase} {tipo}');KB.append(kb)
        if tipo=='dano':k+=1
        f={'id':fid,'tipo':tipo,'n':k if tipo=='dano' else GUIA.index(tipo)+1,'at':extra.get('at',at),'nota':extra.get('nota',''),'kb':kb,'th':th}
        if 'nuevo' in extra:f['nuevo']=extra['nuevo']
        F.append(f)
        ACTAS[f'users/demo/actas/{bid}__{fase}/fotos/{fid}']={'v':1,'bid':bid,'fase':fase,'tipo':tipo,'at':f['at'],'kb':kb,'img':big}
    ACTAS[f'users/demo/actas/{bid}__{fase}']={'v':1,'bid':bid,'vid':vid,'fase':fase,'at':at,'km':km,'combustible':comb,'lugar':lugar,'nota':nota,'keep':False,'kb':sum(f['kb'] for f in F),'fotos':F,'subida':{'seconds':1}}
    if borradas:ACTAS[f'users/demo/actas/{bid}__{fase}']['borradas']=borradas
VV={v['id']:v for v in D['vehicles']}
VV['v5']['tankL']=45
# b22: 8 + 8 fotos (6 guiadas + 2 daños), conductor adicional, cargos de la devolución y fianza retenida en parte
VV['v5']['bookings'].append({'id':'bk22ZZ8Q7','startDate':d(-5),'startTime':'09:30','endDate':d(-1),'endTime':'19:00','platform':'sinapp','amount':180,
  'clientName':'Lucía Herrera Gómez','clientDni':'00000009Y','clientPhone':'600 000 009','extraDriverName':'Pablo Herrera Ruiz','extraDriverDni':'00000010F','hasExtraDriver':True,
  'fianza':200,'fianzaStatus':'partial','fianzaRetainedAmount':60,'fianzaRetainedReason':'Arañazo paragolpes trasero','deliveryPlace':'Estación de Pinto','returnPlace':'C/ Real 12, Pinto',
  'delivered':True,'deliveredAt':iso(-5,9,41),'kmStart':76000,'deliveredFuelLevel':'Lleno (100%)','returned':True,'returnedAt':iso(-1,19,12),'kmEnd':77350,'returnedFuelLevel':'1/2',
  'finance':[{'id':'rc1','type':'income','concept':'Exceso de km','amount':45.6,'date':d(-1),'notes':'240 km extra en devolución','_returnCharge':True},
             {'id':'rc2','type':'income','concept':'Combustible faltante','amount':58.28,'date':d(-1),'notes':'Faltan 22.5 L (Lleno (100%) → 1/2) · 1.59 €/L + 2 €/L de recargo','_returnCharge':True}],'extras':[]})
G8E=[(t,{'at':iso(-5,9,30+i)}) for i,t in enumerate(GUIA)]+[('dano',{'nota':'Roce · puerta trasera derecha','at':iso(-5,9,37)}),('dano',{'nota':'Llanta delantera izquierda rozada','at':iso(-5,9,38)})]
G8D=[(t,{'at':iso(-1,19,i)}) for i,t in enumerate(GUIA)]+[('dano',{'nota':'Arañazo de 8 cm en el paragolpes trasero','nuevo':True,'at':iso(-1,19,7)}),('dano',{'nota':'Roce puerta trasera derecha','nuevo':False,'at':iso(-1,19,8)})]
G8E[4]=('interior',{'at':iso(-6,18,5)}) # foto de la galería hecha el día antes: sale con su fecha
acta('bk22ZZ8Q7','entrega',G8E,76000,'Lleno (100%)',iso(-5,9,41),'Estación de Pinto','Cliente avisado del roce trasero','v5')
acta('bk22ZZ8Q7','devolucion',G8D,77350,'1/2',iso(-1,19,12),'','','v5')
# b21: 3 + 3 fotos (Peugeot 3333DDD), sin cargos y fianza devuelta
VV['v4']['bookings'].append({'id':'b21','startDate':d(-9),'startTime':'10:00','endDate':d(-7),'endTime':'10:00','platform':'sinapp','amount':90,'clientName':'Jorge Pérez Ejemplo','clientDni':'00000011P','clientPhone':'600 000 011',
  'fianza':200,'fianzaStatus':'returned','delivered':True,'deliveredAt':iso(-9,10,5),'kmStart':47000,'deliveredFuelLevel':'3/4','returned':True,'returnedAt':iso(-7,10,20),'kmEnd':47300,'returnedFuelLevel':'3/4','finance':[],'extras':[]})
acta('b21','entrega',[(t,{}) for t in GUIA[:3]],47000,'3/4',iso(-9,10,5),'Pinto centro','','v4')
acta('b21','devolucion',[(t,{}) for t in GUIA[:3]],47300,'3/4',iso(-7,10,20),'','','v4')
for b in VV['v4']['bookings']:
    if b['id']=='b41':b.update({'kmStart':46000,'kmEnd':46200})
acta('b41','entrega',[(t,{}) for t in GUIA[:2]],46000,'Lleno (100%)',iso(-40,10,0),'','','v4')
# b20: 0 + 0 fotos (actas solo con km y combustible), sin fianza
VV['v1']['bookings'].append({'id':'b20','startDate':d(-12),'startTime':'10:00','endDate':d(-10),'endTime':'10:00','platform':'sinapp','amount':70,'clientName':'Cliente Sin Fotos','clientPhone':'600 000 020',
  'delivered':True,'deliveredAt':iso(-12,10,2),'kmStart':97000,'deliveredFuelLevel':'Lleno (100%)','returned':True,'returnedAt':iso(-10,10,9),'kmEnd':97400,'returnedFuelLevel':'Lleno (100%)','finance':[],'extras':[]})
acta('b20','entrega',[],97000,'Lleno (100%)',iso(-12,10,2),'','','v1');acta('b20','devolucion',[],97400,'Lleno (100%)',iso(-10,10,9),'','','v1')
print('Fotos de prueba en la nube: %d · %d–%d KB cada una (1280 px, JPEG 0,65, con grano)'%(len(KB),min(KB),max(KB)))
SHARE="""window.__SH=[];navigator.canShare=()=>true;navigator.share=async d=>{const f=d.files[0];window.__SH.push({name:f.name,type:f.type,size:f.size,act:navigator.userActivation?navigator.userActivation.isActive:null});};"""
route=H.route
ERR=H.ERRS
def ok(name,cond,info=''):H.chk(cond,name,info)
def wait(pg,ms=600):pg.wait_for_timeout(ms)
def new_page(b,html,share=False):
    ctx=H.new_context(b,accept_downloads=True)
    ctx.add_init_script("window.__DATA=%s;window.__ACTAS=%s;window.__DENY=false;localStorage.setItem('wg_theme','dark');localStorage.setItem('deiros_lastBackupAt',new Date().toISOString());localStorage.setItem('deiros_fx_day','demo|'+(d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'))(new Date()));window.alert=m=>{(window.__AL=window.__AL||[]).push(m)};window.__CFR=true;window.confirm=m=>{(window.__CF=window.__CF||[]).push(m);return window.__CFR};%s"%(json.dumps(D),json.dumps(ACTAS),SHARE if share else ''))
    ctx.add_init_script(FAKE0)
    pg=ctx.new_page();tag=os.path.basename(os.path.dirname(html))+'/'+os.path.basename(html)
    pg.on('pageerror',lambda e:ERR.append(tag+': '+str(e)))
    pg.goto('file://'+os.path.abspath(html));wait(pg,2200);pg.evaluate("ensureLib('jspdf')")  # el botón carga jsPDF antes de _actaPDF
    return ctx,pg
def pdf_of(pg,bid,fase):
    r=pg.evaluate("([b,f])=>_actaPDF(b,f).then(r=>({name:r.name,n:r.n,u:r.doc.output('datauristring')}))",[bid,fase])
    p=os.path.join(TMP,r['name']);open(p,'wb').write(base64.b64decode(r['u'].split(',',1)[1]));return p,r
def pdftext(p):return subprocess.run(['pdftotext','-layout',p,'-'],capture_output=True,text=True).stdout
def pages(p):return int(re.search(r'Pages:\s+(\d+)',subprocess.run(['pdfinfo',p],capture_output=True,text=True).stdout).group(1))
def nimgs(p):return len([l for l in subprocess.run(['pdfimages','-list',p],capture_output=True,text=True).stdout.splitlines()[2:] if l.strip()])
def flat(s):return re.sub(r'\s+',' ',s)
def fs_keys(pg,pre):return pg.evaluate("p=>Object.keys(window.__FS).filter(k=>k.startsWith(p)).sort()",pre)
def bk(pg,bid):return pg.evaluate("id=>{let r=null;V.forEach(v=>(v.bookings||[]).forEach(b=>{if(b.id===id)r=b}));return r?JSON.parse(JSON.stringify(r)):null}",bid)
TXE='El cliente declara haber recibido el vehículo en el estado descrito en esta acta'
TXD='El cliente declara haber devuelto el vehículo en el estado descrito en esta acta'
with sync_playwright() as p:
    br=H.launch(p)
    ctx,pg=new_page(br,NEW,share=True)
    # ───────────── 1 · Las dos actas con 0, 3 y 8 fotos (fotos leídas de la subcolección: nada en el móvil)
    ok('Al empezar no hay fotos en este móvil (caché «img» vacía)',pg.evaluate("_fxAll('img').then(L=>L.length)")==0)
    casos=[('b20',0,1,0),('b21',3,2,3),('bk22ZZ8Q7',8,2,8)]
    M0=pg.evaluate("JSON.stringify(window.__FS['users/demo/data/main'])")
    for bid,n,pgs,ni in casos:
        for fase in ('entrega','devolucion'):
            path,r=pdf_of(pg,bid,fase);t=flat(pdftext(path));kb=os.path.getsize(path)//1024
            dev=fase=='devolucion';plate={'b20':'0000AAA','b21':'3333DDD','bk22ZZ8Q7':'4444EEE'}[bid]
            ok(f'{bid} {fase} ({n} fotos): nombre «{r["name"]}»',r['name']==('Acta-devolucion-' if dev else 'Acta-entrega-')+plate+'-'+(d(-1) if bid=='bk22ZZ8Q7' and dev else d(-5) if bid=='bk22ZZ8Q7' else d(-7) if bid=='b21' and dev else d(-9) if bid=='b21' else d(-10) if dev else d(-12))+'.pdf')
            ok(f'{bid} {fase}: {pgs} página(s), {ni} imágenes de fotos (+ logo), {kb} KB',pages(path)==pgs and nimgs(path)==ni+pgs,(pages(path),nimgs(path)))
            num=('ACT-D-' if dev else 'ACT-E-')+re.sub('[^A-Za-z0-9]','',bid)[-6:].upper()
            need=[('Acta de devolución' if dev else 'Acta de entrega'),num,plate,'01 PARTES','02 VEHÍCULO','03 KM Y COMBUSTIBLE','04 DAÑOS Y NOTAS',(TXD if dev else TXE),'POR EL ARRENDADOR','EL CLIENTE','Página 1 de %d'%pgs]
            need+=([str(n)+' FOTOS','y en sus %d fotos'%n,'FOTOS DE LA '+('DEVOLUCIÓN' if dev else 'ENTREGA'),'La fecha y la hora de cada foto son las del móvil'] if n else ['SIN FOTOS','en esta acta, con los kilómetros'])
            if dev:need+=['05 CARGOS Y FIANZA','06 CONFORMIDAD']
            else:need+=['05 CONFORMIDAD']
            falta=[s for s in need if s not in t]
            ok(f'{bid} {fase}: textos del acta',not falta,falta)
            if bid=='bk22ZZ8Q7':
                ok(f'{bid} {fase}: < 1 MB con 8 fotos ({kb} KB)',kb<1024,kb)
                extra=['Conductor adicional'.upper(),'Pablo Herrera Ruiz','00000010F','Lucía Herrera Gómez','00000009Y','Citroën C3','01 FRONTAL','06 CUADRO']
                if dev:extra+=['SIN DAÑOS NUEVOS'] if False else ['DAÑOS NUEVOS: 1','NUEVO Arañazo de 8 cm en el paragolpes trasero (foto D1)','YA EXISTÍA Roce puerta trasera derecha (foto D2)','(anotado en la entrega, D1)','77.350 km','1.350 km recorridos','-50 %','faltan 22,5 L','Exceso de km','45,60 €','Combustible faltante','58,28 €','103,88 €','DETALLE EN EL RECIBO','RETENIDOS 60,00 €, SE DEVUELVEN 140,00 €','Motivo: Arañazo paragolpes trasero','C/ REAL 12, PINTO','D1 DAÑO NUEVO','D2 YA EXISTÍA','DEVUELTO EL '+datetime.date.fromisoformat(d(-1)).strftime('%d/%m/%Y')+' A LAS 19:12']
                else:extra+=['ESTADO DE SALIDA','76.000 km','DAÑO Roce · puerta trasera derecha (foto D1)','Notas: Cliente avisado del roce trasero','ESTACIÓN DE PINTO','05 INTERIOR '+datetime.date.fromisoformat(d(-6)).strftime('%d/%m')+' 18:05','01 FRONTAL 09:30','ENTREGADO EL '+datetime.date.fromisoformat(d(-5)).strftime('%d/%m/%Y')+' A LAS 09:41']
                falta=[s for s in extra if s not in t]
                ok(f'{bid} {fase}: partes, km, daños, cargos y fianza, hora de cada foto',not falta,falta)
                if SHOTS:
                    for pn in (1,2):subprocess.run(['pdftoppm','-r','110','-png','-f',str(pn),'-l',str(pn),'-singlefile',path,os.path.join(SHOTS,f'acta-{fase}-p{pn}')])
            if bid=='b21' and dev:
                ok('b21 devolución: «Sin cargos…» y «FIANZA 200,00 €: DEVUELTA»','Sin cargos de km ni de combustible.' in t and 'FIANZA 200,00 €: DEVUELTA' in t and 'sin exceso' in t,t[:0])
            if bid=='b20' and dev:ok('b20 devolución sin fotos: sello «ESTADO DE LLEGADA» y «SIN FIANZA»','ESTADO DE LLEGADA' in t and 'SIN FIANZA' in t)
    ok('Generar no escribe nada en la nube (ni actas ni fotos)',pg.evaluate("window.__FSOPS.filter(p=>/actas/.test(p)).length")==0,pg.evaluate("window.__FSOPS.slice(0,5)"))
    ok('data/main sin cambios tras generar las 6 actas',pg.evaluate("JSON.stringify(window.__FS['users/demo/data/main'])")==M0)
    # ───────────── 2 · Ficha: botones, Generar (descarga) y Enviar (menú de compartir con el PDF)
    pg.evaluate("showBookingById('bk22ZZ8Q7')");wait(pg,2500)
    bt=pg.evaluate("[...document.querySelectorAll('#fxSec .ac-b button')].map(b=>b.textContent.trim())")
    ok('«Fotos y actas»: Generar acta y Enviar acta en entrega y devolución',bt.count('Generar acta')==2 and bt.count('Enviar acta')==2,bt)
    hs=pg.evaluate("[...document.querySelectorAll('#fxSec .ac-b button')].map(b=>Math.round(b.getBoundingClientRect().height))")
    ok('Botones de al menos 44 px de alto',min(hs)>=44,hs)
    if SHOTS:
        pg.evaluate("const s=document.getElementById('SH');s.scrollTop=document.getElementById('fxSec').offsetTop-40");wait(pg,600)
        pg.screenshot(path=os.path.join(SHOTS,'ficha-fotos-y-actas.png'))
    with pg.expect_download(timeout=30000) as dl:pg.locator('#fxSec .ac-r',has_text='Devolución').locator('button',has_text='Generar acta').click()
    dp=os.path.join(TMP,'dl.pdf');dl.value.save_as(dp)
    ok('Generar acta (devolución): descarga «%s», %d páginas'%(dl.value.suggested_filename,pages(dp)),dl.value.suggested_filename=='Acta-devolucion-4444EEE-'+d(-1)+'.pdf' and pages(dp)==2)
    wait(pg,500)
    pg.locator('#fxSec .ac-r',has_text='Entrega').locator('button',has_text='Enviar acta').click()
    pg.wait_for_function("window.__SH.length>0",timeout=30000)
    sh=pg.evaluate("window.__SH[0]")
    ok('Enviar acta: navigator.share con el PDF «Acta-entrega-4444EEE-…» (< 1 MB) en el mismo toque',sh['name']=='Acta-entrega-4444EEE-'+d(-5)+'.pdf' and sh['type']=='application/pdf' and sh['size']<1024*1024 and sh['act'] is not False,sh)
    ok('El botón vuelve a su texto',pg.evaluate("[...document.querySelectorAll('#fxSec .ac-b button')].filter(b=>/Preparando/.test(b.textContent)).length")==0)
    # Sin el toque (el navegador ya no deja compartir): aviso «Acta lista» con el botón para enviarla
    # Playwright evalúa con «toque activo»: se simula que ya caducó (p. ej., si leer las fotos de la nube tarda)
    pg.evaluate("window.__UA=navigator.userActivation;Object.defineProperty(navigator,'userActivation',{configurable:true,get:()=>({isActive:false,hasBeenActive:true})})")
    pg.evaluate("window.__SH=[];_actaGo('b21','devolucion',1)");pg.wait_for_function("!!document.getElementById('actaOf')",timeout=20000)
    ok('Sin toque activo: aviso «Acta lista: Acta-devolucion-3333DDD-…» y no comparte solo',pg.evaluate("document.getElementById('actaOf').textContent").startswith('Acta lista: Acta-devolucion-3333DDD-') and pg.evaluate("window.__SH.length")==0,pg.evaluate("document.getElementById('actaOf').textContent"))
    pg.locator('#actaOf button',has_text='Enviar acta').click();wait(pg,800)
    pg.evaluate("Object.defineProperty(navigator,'userActivation',{configurable:true,get:()=>window.__UA})")
    ok('Al tocarlo, comparte el PDF',pg.evaluate("window.__SH.length")==1 and pg.evaluate("window.__SH[0].name").startswith('Acta-devolucion-3333DDD'))
    pg.evaluate("closeSheet()");wait(pg,300)
    # ───────────── 3 · Fotos en la cola (sin subir) y sin red
    ctx.set_offline(True);wait(pg,300)
    pg.evaluate("openV('v4');showBookingById('b21')");wait(pg,1500)
    pg.locator('#fxSec .ac-r',has_text='Devolución').locator('button',has_text='Ver y añadir fotos').click();wait(pg,1000)
    with pg.expect_file_chooser() as fc:pg.locator('#fxBar .btn-pri').click()
    fc.value.set_files(os.path.join(H.fotos_prueba(),'devolucion_lat_izq.jpg'));pg.wait_for_function("_fx.A['b21__devolucion'].fotos.length===4",timeout=15000);wait(pg,800)
    q=pg.evaluate("_fxAll('q').then(L=>L.filter(i=>i.t==='f').length)")
    ok('Sin red: la foto nueva está en la cola, sin subir',q==1 and len(fs_keys(pg,'users/demo/actas/b21__devolucion/fotos/'))==3,q)
    pg.evaluate("_fx.A['b21__devolucion'].fotos.push({id:'zzSinFoto',tipo:'cuadro',n:6,at:new Date().toISOString(),nota:'',kb:0})") # foto sin imagen ni miniatura
    pg.evaluate("_fxAll('img').then(L=>null)");pg.evaluate("_fxTx('img','readwrite',s=>s.clear())");wait(pg,300)
    path,r=pdf_of(pg,'b21','devolucion');t=flat(pdftext(path))
    ok('Sin red: el acta sale con 5 fotos (la de la cola con su imagen)',r['n']==5 and 'LATERAL IZQUIERDO' in t,r['n'])
    ok('Sin red: las de la nube con su miniatura («MINIATURA» ×3) y la que falta «SIN FOTO»',t.count('MINIATURA')==3 and t.count('SIN FOTO')==1,(t.count('MINIATURA'),t.count('SIN FOTO')))
    ok('Sin red: imágenes en el PDF = 4 fotos + logo ×2',nimgs(path)==6,nimgs(path))
    pg.evaluate("_fx.A['b21__devolucion'].fotos=_fx.A['b21__devolucion'].fotos.filter(f=>f.id!=='zzSinFoto')")
    pg.evaluate("closeSheet()");ctx.set_offline(False);wait(pg,3000)
    ok('Al volver la red la foto se sube (la cola queda vacía)',pg.evaluate("_fxAll('q').then(L=>L.length)")==0 and len(fs_keys(pg,'users/demo/actas/b21__devolucion/fotos/'))==4)
    # ───────────── 4 · Al confirmar: aviso con «Enviar acta» / «Ver acta»
    pg.evaluate("openV('v3');toggleDelivery('b31')");wait(pg,1200)
    pg.locator('#fxBar .btn-txt',has_text='Confirmar entrega ya').click();wait(pg,1200)
    of=pg.evaluate("(document.getElementById('actaOf')||{}).textContent||''")
    ok('Entrega confirmada: aviso «Entrega guardada…» con Enviar acta y Ver acta','Entrega guardada' in of and 'Enviar acta' in of and 'Ver acta' in of,of)
    if SHOTS:pg.screenshot(path=os.path.join(TMP,'aviso.png'))
    pg.evaluate("window.__SH=[]");pg.locator('#actaOf button',has_text='Enviar acta').click();pg.wait_for_function("window.__SH.length>0",timeout=20000)
    ok('Desde el aviso: comparte «Acta-entrega-2222CCC-hoy.pdf»',pg.evaluate("window.__SH[0].name")=='Acta-entrega-2222CCC-'+d(0)+'.pdf',pg.evaluate("window.__SH[0].name"))
    pg.evaluate("openReturnModal('b31')");wait(pg,1200);pg.fill('#retKm','143300');pg.locator('.d-seg[data-for=retFuel] button',has_text='Lleno').click();wait(pg,300)
    pg.locator('#SC .btn-pri',has_text='Confirmar devolución').click();wait(pg,1500)
    ok('Devolución confirmada: aviso «Devolución guardada…»','Devolución guardada' in pg.evaluate("(document.getElementById('actaOf')||{}).textContent||''"))
    pg.evaluate("document.getElementById('actaOf')&&document.getElementById('actaOf').remove()")
    ctx.close()
    # ───────────── 5 · Borrar un alquiler: avisa de las fotos aunque no se hayan cargado en la sesión
    ctx,pg=new_page(br,NEW)
    pg.evaluate("window.__CFR=false;window.__CF=[];AV='v5';deleteBooking('bk22ZZ8Q7')");wait(pg,1500)
    ok('Sin abrir la ficha: «Se borrarán también las 16 fotos…» (nube)',any('16 fotos' in m for m in pg.evaluate("window.__CF")),pg.evaluate("window.__CF"))
    ok('Si se cancela, no se borra nada',bk(pg,'bk22ZZ8Q7') is not None and len(fs_keys(pg,'users/demo/actas/bk22ZZ8Q7'))==18)
    pg.evaluate("window.__CFR=true;window.__CF=[];showBookingById('b21')");wait(pg,1500)
    # el rótulo «Comprobando fotos…» dura un instante: se anotan todos los rótulos que va teniendo la zona de borrar
    pg.evaluate("window.__LBL=[];window.__MO=new MutationObserver(()=>{window.__LBL.push([...document.querySelectorAll('#SC .al-dz .btn-txt')].map(b=>b.textContent.trim()).join('|'))});__MO.observe(document.getElementById('SC'),{subtree:true,childList:true,characterData:true})")
    pg.locator('#SC .al-dz .btn-txt',has_text='Eliminar').click()
    wait(pg,1500);pg.evaluate("__MO.disconnect()");lbl=' · '.join(pg.evaluate("window.__LBL"))
    ok('Desde la ficha: «Comprobando fotos…» y luego pregunta por las 6 fotos','Comprobando fotos' in lbl and any('6 fotos' in m for m in pg.evaluate("window.__CF")),(lbl,pg.evaluate("window.__CF")))
    wait(pg,1500)
    ok('Confirmado: alquiler borrado, ficha cerrada y actas/fotos borradas de la nube',bk(pg,'b21') is None and not pg.evaluate("document.getElementById('SH').classList.contains('open')") and fs_keys(pg,'users/demo/actas/b21')==[],fs_keys(pg,'users/demo/actas/b21'))
    # Nube lenta: tiempo límite y aviso de que no se pudo comprobar
    pg.evaluate("window.__SLOW=true;window.__CFR=false;window.__CF=[];AV='v5'");t0=time.time()
    pg.evaluate("deleteBooking('b5')");pg.wait_for_function("(window.__CF||[]).length>0",timeout=15000);dt=time.time()-t0
    ok('Nube lenta: pregunta a los %.1f s (límite 6 s) «No se ha podido comprobar si tiene fotos…»'%dt,dt<8 and 'No se ha podido comprobar si tiene fotos' in pg.evaluate("window.__CF[0]"),pg.evaluate("window.__CF"))
    pg.evaluate("window.__SLOW=false")
    # Sin red: entregado → aviso de no comprobado; no entregado → como siempre (sin preguntar)
    ctx.set_offline(True);wait(pg,300)
    pg.evaluate("window.__CF=[];window.__CFR=false;AV='v4';deleteBooking('b4')");wait(pg,800)
    ok('Sin red y entregado: avisa de que no se ha podido comprobar',len(pg.evaluate("window.__CF"))==1 and 'sin conexión' in pg.evaluate("window.__CF[0]") and bk(pg,'b4') is not None)
    pg.evaluate("window.__CF=[];AV='v1';deleteBooking('b1')");wait(pg,800)
    ok('Sin red y sin entregar: se borra sin preguntar, como siempre',pg.evaluate("window.__CF.length")==0 and bk(pg,'b1') is None)
    ctx.set_offline(False);wait(pg,800)
    # ───────────── 6 · Borrar un coche: el aviso dice cuántas fotos se borrarán
    pg.evaluate("deleteV('v5')");wait(pg,1500)
    t=pg.evaluate("document.getElementById('fxDelV').textContent")
    ok('Coche Citroën C3: «Se borrarán también 16 fotos de entrega y devolución (1 alquiler).»',t=='Se borrarán también 16 fotos de entrega y devolución (1 alquiler).',t)
    if SHOTS:pg.screenshot(path=os.path.join(TMP,'borrar-coche.png'))
    pg.evaluate("closeSheet();deleteV('v2')");wait(pg,1200)
    ok('Coche sin fotos: «No tiene fotos de entrega ni de devolución.»',pg.evaluate("document.getElementById('fxDelV').textContent")=='No tiene fotos de entrega ni de devolución.')
    pg.evaluate("closeSheet()");ctx.set_offline(True);wait(pg,200);pg.evaluate("deleteV('v4')");wait(pg,1200)
    ok('Sin red: «No se ha podido comprobar si tiene fotos (sin conexión)…»',pg.evaluate("document.getElementById('fxDelV').textContent").startswith('No se ha podido comprobar si tiene fotos'))
    pg.evaluate("closeSheet()");ctx.set_offline(False);wait(pg,500)
    pg.evaluate("deleteV('v5')");wait(pg,1200);pg.locator('#SC .btn-dang',has_text='Eliminar definitivamente').click();wait(pg,3000)
    ok('Eliminar definitivamente: coche y sus 16 fotos borrados',pg.evaluate("!V.some(v=>v.id==='v5')") and fs_keys(pg,'users/demo/actas/bk22ZZ8Q7')==[])
    ctx.close()
    br.close()
H.fin()
