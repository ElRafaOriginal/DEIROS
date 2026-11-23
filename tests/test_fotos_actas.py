# Fotos y actas de entrega y devolución (#105, PR 1): hoja «Entregar coche» (con y sin fotos), compresión en el móvil
# (1280 px, < 300 KB, sello de fecha), guardado FUERA de data/main (users/{uid}/actas/… y …/fotos/…), cola sin conexión en
# IndexedDB que se sube sola al volver la red, devolución con guía y daños («Nuevo» / «Ya existía»), Comparar, borrar el
# alquiler borra sus fotos, limpieza a 6 meses con «Conservar», la copia v4 normal no lleva fotos (solo la «copia con fotos»,
# ver test_galeria.py) y error de reglas de Firebase (permission-denied).
# Origen: specs/fotos105/test_pr1.py. Quitado lo de «igual que main» (HTML de pantallas, copia, devolución e importes: lo
# cubren test_pantallas, test_copia y test_devolucion); «solo cambian campos existentes» es ahora una lista fija de campos.
# Fotos sintéticas generadas por el arnés (sin fotos reales). Uso: python3 tests/test_fotos_actas.py
import sys,os,json,datetime,base64,io,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
from PIL import Image
from playwright.sync_api import sync_playwright
NEW=H.INDEX;SHOTS=H.CAPTURAS
D=H.datos();FAKE0=H.FAKE
hoy=H.HOY;d=H.d
iso=lambda n:(H.AHORA+datetime.timedelta(days=n)).isoformat()
FOTOS=H.fotos_prueba();M=FOTOS+'/';BIG=FOTOS+'/big.jpg'
VV={v['id']:v for v in D['vehicles']}
# Alquileres de prueba (ficticios): b7 y b12 empiezan hoy sin entregar; b8 y b9 cerrados hace > 6 meses; b41 devuelto hace 37 días
VV['v1']['bookings'].append({'id':'b7','startDate':d(0),'startTime':'09:00','endDate':d(3),'endTime':'09:00','platform':'sinapp','amount':120,'clientName':'Lucía Prueba Ejemplo','clientPhone':'600 000 007','fianza':200,'finance':[],'extras':[]})
VV['v5']['bookings'].append({'id':'b12','startDate':d(0),'startTime':'10:00','endDate':d(4),'endTime':'10:00','platform':'sinapp','amount':160,'clientName':'Alejandro J. Martínez','clientPhone':'600 000 012','fianza':200,'deliveryPlace':'Pinto centro','finance':[],'extras':[]})
VV['v4']['bookings'].append({'id':'b8','startDate':d(-222),'startTime':'10:00','endDate':d(-215),'endTime':'10:00','platform':'sinapp','amount':210,'clientName':'Cliente Antiguo Uno','fianza':200,'delivered':True,'returned':True,'returnedAt':iso(-215),'fianzaStatus':'returned','fianzaReturnedAt':iso(-212),'cobrado':True,'paid':True,'finance':[],'extras':[]})
VV['v5']['bookings'].append({'id':'b9','startDate':d(-260),'startTime':'10:00','endDate':d(-250),'endTime':'10:00','platform':'sinapp','amount':300,'clientName':'Cliente Antiguo Dos','delivered':True,'returned':True,'returnedAt':iso(-250),'cobrado':True,'paid':True,'finance':[],'extras':[]})
for b in VV['v4']['bookings']:
    if b['id']=='b41':b['returnedAt']=iso(-37)
TH='data:image/jpeg;base64,'+base64.b64encode((lambda b:(Image.new('RGB',(240,180),(90,90,100)).save(b,'JPEG',quality=60),b.getvalue())[1])(io.BytesIO())).decode()
def acta(bid,fase,n,keep=False):
    fotos=[{'id':f'{bid}{fase[0]}{i}','tipo':['frontal','lat_der','trasera','lat_izq','interior','cuadro'][i],'n':i+1,'at':iso(-250),'nota':'','kb':180,'th':TH} for i in range(n)]
    A={f'users/demo/actas/{bid}__{fase}':{'v':1,'bid':bid,'vid':'','fase':fase,'at':iso(-250),'km':1000,'combustible':'Lleno (100%)','lugar':'','nota':'','keep':keep,'kb':180*n,'fotos':fotos}}
    for f in fotos:A[f'users/demo/actas/{bid}__{fase}/fotos/{f["id"]}']={'v':1,'bid':bid,'fase':fase,'tipo':f['tipo'],'at':f['at'],'kb':180,'img':TH}
    return A
ACTAS={};[ACTAS.update(acta(*a)) for a in (('b8','entrega',3),('b8','devolucion',2),('b9','entrega',2),('b41','entrega',2))]
route=H.route
ERR=H.ERRS
def ok(name,cond,info=''):H.chk(cond,name,info)
def wait(pg,ms=600):pg.wait_for_timeout(ms)
def main_doc(pg):return pg.evaluate("JSON.parse(JSON.stringify(window.__FS['users/demo/data/main']))")
def bk(doc,bid):
    for v in doc['vehicles']:
        for b in v.get('bookings',[]):
            if b['id']==bid:return b
def fs_keys(pg,pre):return pg.evaluate("p=>Object.keys(window.__FS).filter(k=>k.startsWith(p)).sort()",pre)
def shoot(pg,loc,path,aid):
    n0=pg.evaluate("a=>(_fx.A[a]&&_fx.A[a].fotos.length)||0",aid)
    with pg.expect_file_chooser() as fc: loc.click()
    fc.value.set_files(path)
    pg.wait_for_function("([a,n])=>_fx.A[a]&&_fx.A[a].fotos.length!==n||document.getElementById('fxV')",arg=[aid,n0],timeout=15000);wait(pg,300)
def new_page(b,html,deny=False,actas=True,offline_day=True):
    ctx=H.new_context(b)
    ctx.add_init_script("window.__DATA=%s;window.__ACTAS=%s;window.__DENY=%s;localStorage.setItem('wg_theme','dark');localStorage.setItem('deiros_lastBackupAt',new Date().toISOString());%swindow.alert=m=>{(window.__AL=window.__AL||[]).push(m)};window.confirm=m=>{(window.__CF=window.__CF||[]).push(m);return true};"%(json.dumps(D),json.dumps(ACTAS if actas else {}),'true' if deny else 'false',"localStorage.setItem('deiros_fx_day','demo|'+(d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'))(new Date()));" if offline_day else ''))
    ctx.add_init_script(FAKE0)
    pg=ctx.new_page();tag=os.path.basename(os.path.dirname(html))+'/'+os.path.basename(html)
    pg.on('pageerror',lambda e:ERR.append(tag+': '+str(e)))
    pg.goto('file://'+os.path.abspath(html));wait(pg,2200)
    pg.evaluate("window.__toasts=[];new MutationObserver(m=>m.forEach(r=>r.addedNodes.forEach(n=>{if(n.classList&&n.classList.contains('d-toast'))window.__toasts.push(n.textContent)}))).observe(document.body,{childList:true})")
    return ctx,pg
def toasts(pg):return pg.evaluate("window.__toasts")
def cmp_sheet_shot(pg,name):
    if SHOTS: pg.screenshot(path=os.path.join(SHOTS,name))
with sync_playwright() as p:
    br=H.launch(p)
    # ───────────── 1 · Entregar SIN fotos (desde «Hoy») frente a main
    ctx,pg=new_page(br,NEW)
    b7_0=bk(main_doc(pg),'b7')
    pg.evaluate("nav('dashboard')");wait(pg,900)
    pg.locator('.dh-sec.hoy .dh-row',has_text='Lucía Prueba').locator('button.hoy-b').click();wait(pg,700)
    ok('Hoy «Entregar» abre la hoja «Entregar coche»',pg.evaluate("document.getElementById('SH').classList.contains('open')&&/Entregar coche/.test(document.getElementById('SC').textContent)"))
    ok('Km propuestos = km del coche',pg.evaluate("document.getElementById('fxKm').value")=='98000',pg.evaluate("document.getElementById('fxKm').value"))
    ok('Barra del pulgar: «Foto 1 de 6 · Frontal»',pg.evaluate("document.querySelector('#fxBar .btn-pri').textContent.trim()")=='Foto 1 de 6 · Frontal')
    pg.locator('#fxBar .btn-txt',has_text='Confirmar entrega ya').click();wait(pg,1800)
    a,bm=bk(main_doc(pg),'b7'),b7_0
    ok('Sin fotos: queda entregado con deliveredAt',a.get('delivered') is True and a.get('deliveredAt'))
    extra=sorted(set(a)-set(bm));chg=sorted(k for k in set(a)&set(bm) if a[k]!=bm[k] and k!='deliveredAt')
    ok('Entregar solo escribe campos que ya existen (delivered, deliveredAt, kmStart, deliveredFuelLevel, deliveryPlace): ningún campo nuevo en el alquiler',set(extra)<= {'delivered','deliveredAt','kmStart','deliveredFuelLevel','deliveryPlace'} and not chg,{'nuevos':extra,'distintos':chg})
    ok('kmStart y combustible escritos',a.get('kmStart')==98000 and a.get('deliveredFuelLevel')=='Lleno (100%)',(a.get('kmStart'),a.get('deliveredFuelLevel')))
    ok('Lugar vacío y sin campo previo: no se añade deliveryPlace','deliveryPlace' not in a)
    ac=pg.evaluate("JSON.parse(JSON.stringify(window.__FS['users/demo/actas/b7__entrega']||null))")
    ok('Acta de entrega en la subcolección (km, combustible, 0 fotos)',ac and ac['km']==98000 and ac['combustible']=='Lleno (100%)' and ac['fotos']==[] and ac.get('subida'),ac and {k:ac[k] for k in ('km','combustible','fotos')})
    ok('data/main no lleva actas ni fotos',not re.search(r'acta|data:image|fotos',json.dumps(main_doc(pg))))
    # ───────────── 2 · Entregar CON fotos (ficha del alquiler), compresión y guardado
    pg.evaluate("openV('v5')");wait(pg,900);pg.evaluate("showBookingById('b12')");wait(pg,700)
    pg.locator('#SC .al-pri').click();wait(pg,900)
    ok('Ficha «Marcar entregado» abre la hoja',pg.evaluate("/Entregar coche/.test(document.getElementById('SC').textContent)"))
    ok('Lugar propuesto = deliveryPlace',pg.evaluate("document.getElementById('fxPlace').value")=='Pinto centro')
    shoot(pg,pg.locator('#fxBar .btn-pri'),BIG,'b12__entrega')
    for f in ('lat_der','trasera','lat_izq'):shoot(pg,pg.locator('#fxBar .btn-pri'),M+'entrega_'+f+'.jpg','b12__entrega')
    shoot(pg,pg.locator('.ph-add',has_text='Foto de un daño'),M+'entrega_dano1.jpg','b12__entrega')
    ok('Foto de daño abre el visor con la nota',pg.evaluate("!!document.getElementById('fxVNota')"))
    pg.locator('.fx-qn button',has_text='Roce').click();pg.fill('#fxVNota','Roce · puerta trasera derecha');pg.locator('#fxV .btn-pri',has_text='Hecho').click();wait(pg,600)
    ok('Barra: «Foto 5 de 6 · Interior»',pg.evaluate("document.querySelector('#fxBar .btn-pri').textContent.trim()")=='Foto 5 de 6 · Interior')
    wait(pg,1500)
    if SHOTS:
        pg.evaluate("const s=document.getElementById('SH');const h=[...s.querySelectorAll('.al-h')][1];s.scrollTop=h.offsetTop-150");wait(pg,500)
        pg.screenshot(path=os.path.join(SHOTS,'1-entregar-coche.png'))
    pg.locator('#fxBar .btn-txt',has_text='Confirmar entrega ya').click();wait(pg,2200)
    fk=fs_keys(pg,'users/demo/actas/b12__entrega/fotos/')
    ok('5 fotos en users/{uid}/actas/b12__entrega/fotos',len(fk)==5,len(fk))
    sizes=pg.evaluate("p=>Object.keys(window.__FS).filter(k=>k.startsWith(p)).map(k=>{const s=window.__FS[k].img;return [k,Math.round((s.length-23)*3/4/1024),window.__FS[k].kb,window.__FS[k].tipo]})",'users/demo/actas/b12__entrega/fotos/')
    big=[s for s in sizes if s[3]=='frontal'][0]
    raw=base64.b64decode(pg.evaluate("k=>window.__FS[k].img.split(',')[1]",big[0]));im=Image.open(io.BytesIO(raw))
    ok('Compresión: foto de 4032×3024 (%d KB) → %d×%d, %d KB (< 300 KB)'%(os.path.getsize(BIG)//1024,im.size[0],im.size[1],big[1]),big[1]<300 and max(im.size)<=1280 and im.format=='JPEG',big)
    ok('Todas las fotos < 300 KB',all(s[1]<300 for s in sizes),[s[1] for s in sizes])
    px=im.convert('RGB').getpixel((im.size[0]-40,im.size[1]-12))
    ok('Sello de fecha y hora impreso en la esquina (franja oscura)',sum(px)<330 or px[0]>180,px)
    ac=pg.evaluate("JSON.parse(JSON.stringify(window.__FS['users/demo/actas/b12__entrega']))")
    ok('Acta: 5 fotos con miniatura y nota del daño',len(ac['fotos'])==5 and all(f.get('th','').startswith('data:image/jpeg') for f in ac['fotos']) and any(f['tipo']=='dano' and f['nota'].startswith('Roce') for f in ac['fotos']))
    ok('Miniaturas pequeñas (< 20 KB)',all(len(f['th'])*3/4/1024<20 for f in ac['fotos']),[round(len(f['th'])*3/4/1024,1) for f in ac['fotos']])
    md=main_doc(pg);mdj=json.dumps(md)
    ok('data/main sin fotos ni actas y pequeño (%d KB)'%(len(mdj)//1024),'data:image' not in mdj and 'fotos' not in mdj and len(mdj)<200*1024)
    ok('No salta el aviso de 800 KB',not any('ocupan' in t for t in toasts(pg)),toasts(pg))
    b12=bk(md,'b12');ok('b12 entregado con km 77000, Lleno y lugar',b12.get('delivered') and b12.get('kmStart')==77000 and b12.get('deliveryPlace')=='Pinto centro',{k:b12.get(k) for k in ('delivered','kmStart','deliveredFuelLevel','deliveryPlace')})
    # ───────────── 3 · Cola sin conexión y subida al volver la red
    ctx.set_offline(True);wait(pg,300)
    pg.evaluate("showBookingById('b12')");wait(pg,1200)
    ok('Ficha: «Fotos y actas» con la entrega',pg.evaluate("(document.getElementById('fxSec')||{}).textContent||''").find('Entrega')>=0)
    pg.locator('#fxSec .btn-sec',has_text='Ver y añadir fotos').first.click();wait(pg,900)
    shoot(pg,pg.locator('#fxBar .btn-pri'),M+'entrega_interior.jpg','b12__entrega');wait(pg,800)
    q=pg.evaluate("_fxAll('q').then(L=>L.map(i=>i.t))")
    ok('Sin red: la foto queda en la cola de IndexedDB',q.count('f')==1,q)
    ok('Sin red: no llega a Firestore',len(fs_keys(pg,'users/demo/actas/b12__entrega/fotos/'))==5)
    ok('Aviso «1 foto sin subir»',pg.evaluate("(document.getElementById('fxStat')||{}).textContent")=='1 foto sin subir')
    ok('Miniatura pendiente marcada en la cuadrícula',pg.evaluate("document.querySelectorAll('#fxGrid .phk.p').length")==1)
    pg.evaluate("closeSheet();nav('dashboard')");wait(pg,800)
    ok('La app no se bloquea sin red (Resumen se pinta)',pg.evaluate("/Hoy/.test(document.getElementById('PC').textContent)"))
    ctx.set_offline(False);wait(pg,2500)
    ok('Al volver la red se sube sola',len(fs_keys(pg,'users/demo/actas/b12__entrega/fotos/'))==6 and pg.evaluate("_fxAll('q').then(L=>L.length)")==0)
    ok('El aviso de pendientes desaparece',not pg.evaluate("!!document.getElementById('fxStat')"))
    pg.evaluate("showBookingById('b12')");wait(pg,1000);pg.locator('#fxSec .btn-sec',has_text='Ver y añadir fotos').first.click();wait(pg,800)
    ok('Con red, la barra sigue por la que falta: «Foto 6 de 6 · Cuadro»',pg.evaluate("document.querySelector('#fxBar .btn-pri').textContent.trim()")=='Foto 6 de 6 · Cuadro')
    shoot(pg,pg.locator('#fxBar .btn-pri'),M+'entrega_cuadro.jpg','b12__entrega');wait(pg,1200)
    ok('Con las 6 hechas, la barra dice «Listo»',pg.evaluate("document.querySelector('#fxBar .btn-pri').textContent.trim()")=='Listo')
    pg.evaluate("closeSheet()");wait(pg,400)
    # ───────────── 4 · Fotos de devolución con la guía y los daños
    pg.evaluate("openV('v5')");wait(pg,700);pg.evaluate("openReturnModal('b12')");wait(pg,1200)
    hs=pg.evaluate("[...document.querySelectorAll('#SC .al-h')].map(h=>h.querySelector('.q').textContent+' '+h.querySelector('h3').textContent)")
    ok('Devolución: 01 Fotos · 02 Kilómetros · 03 Combustible · 04 Cargos · 05 Fianza',hs==['01 Fotos de devolución','02 Kilómetros','03 Combustible','04 Cargos','05 Fianza'],hs)
    ok('La foto de la entrega sale en gris como guía (6 guías)',pg.evaluate("document.querySelectorAll('#fxGrid img.gh').length")==6)
    for f in ('frontal','lat_der','trasera'):pg.locator('#fxGrid .ph-t.nx').click();wait(pg,300);shoot(pg,pg.locator('#fxPick .btn-pri',has_text='Cámara'),M+'devolucion_'+f+'.jpg','b12__devolucion')  # tocar un hueco: «Cámara» o «Galería»
    shoot(pg,pg.locator('.ph-add',has_text='Daño nuevo'),M+'devolucion_dano1.jpg','b12__devolucion')
    ok('Daño de devolución: «Nuevo» por defecto',pg.evaluate("document.querySelector('#fxV .d-seg button[aria-pressed=true]').textContent.trim()")=='Nuevo')
    pg.fill('#fxVNota','Arañazo de 8 cm en el paragolpes trasero');pg.locator('#fxV .btn-pri',has_text='Hecho').click();wait(pg,500)
    shoot(pg,pg.locator('.ph-add',has_text='Daño nuevo'),M+'devolucion_dano2.jpg','b12__devolucion')
    pg.locator('#fxV .d-seg button',has_text='Ya existía').click();wait(pg,300);pg.fill('#fxVNota','Roce puerta trasera derecha');pg.locator('#fxV .btn-pri',has_text='Hecho').click();wait(pg,1500)
    ok('Aviso dorado «Faltan 3 fotos»',pg.evaluate("/Faltan 3 fotos/.test(document.getElementById('fxGrid').textContent)"))
    ok('Daños con palabra: «Nuevo» y «Ya existía»',pg.evaluate("[...document.querySelectorAll('#fxGrid .ph-t.dn .l,#fxGrid .ph-t.dm .l')].map(e=>e.textContent)")==['D1Nuevo','D2Ya existía'])
    if SHOTS:
        pg.evaluate("const s=document.getElementById('SH');s.scrollTop=document.getElementById('fxGrid').offsetTop-150");wait(pg,500)
        pg.screenshot(path=os.path.join(SHOTS,'2-fotos-devolucion.png'))
    pg.fill('#retKm','78400');pg.locator('.d-seg[data-for=retFuel] button',has_text='½').click();wait(pg,300)
    pg.locator('#SC .btn-pri',has_text='Confirmar devolución').click();wait(pg,2200)
    ad=pg.evaluate("JSON.parse(JSON.stringify(window.__FS['users/demo/actas/b12__devolucion']))")
    ok('Acta de devolución: 5 fotos, km y combustible',len(ad['fotos'])==5 and ad['km']==78400 and ad['combustible']=='1/2',(len(ad['fotos']),ad['km'],ad['combustible']))
    ok('Daños guardados: nuevo=true / nuevo=false con nota',[(f['n'],f.get('nuevo')) for f in ad['fotos'] if f['tipo']=='dano']==[(1,True),(2,False)])
    # ───────────── 5 · Ficha y comparación
    pg.evaluate("showBookingById('b12')");wait(pg,1500)
    sec=pg.evaluate("document.getElementById('fxSec').textContent")
    ok('Ficha: entrega «7 fotos» y devolución «Faltan 3»','7 fotos' in sec and 'Faltan 3' in sec,sec[:200])
    if SHOTS:
        pg.evaluate("const s=document.getElementById('SH');s.scrollTop=document.getElementById('fxSec').offsetTop-60");wait(pg,500);pg.screenshot(path=os.path.join(SHOTS,'ficha.png'))
    pg.locator('#fxSec .btn-pri',has_text='Comparar').click();wait(pg,2500)
    rows=pg.evaluate("[...document.querySelectorAll('#fxC .cp-row .cp-h')].map(e=>e.textContent.trim())")
    ok('Comparar: arriba el daño nuevo, luego «Ya existía», luego las guiadas',rows[0].startswith('D1') and 'Nuevo' in rows[0] and rows[1].startswith('D2') and 'Ya existía' in rows[1] and rows[2].startswith('01'),rows[:4])
    ok('Comparar: lado a lado (entrega | devolución) en Frontal',pg.evaluate("document.querySelectorAll('#fxC .cp-row')[2].querySelectorAll('img').length")==2)
    ok('Comparar: se cargan las fotos grandes',pg.evaluate("[...document.querySelectorAll('#fxC img[data-f]')].every(i=>{const a=_fx.A[i.dataset.a],f=a&&a.fotos.find(x=>x.id===i.dataset.f);return f&&i.src.length>3*f.th.length})"))
    ok('Cuadro: km y combustible al pie',pg.evaluate("/77\\.000 km · Lleno/.test(document.getElementById('fxC').textContent)"))
    if SHOTS:
        pg.screenshot(path=os.path.join(SHOTS,'comp.png'))
        a_,c_=Image.open(os.path.join(SHOTS,'ficha.png')),Image.open(os.path.join(SHOTS,'comp.png'))
        L=Image.new('RGB',(a_.width+c_.width+24,a_.height),(40,40,40));L.paste(a_,(0,0));L.paste(c_,(a_.width+24,0));L.save(os.path.join(SHOTS,'3-ficha-y-comparar.png'))
    pg.locator('#fxC .cp-row').nth(0).locator('button.f').click();wait(pg,900)
    ok('Visor: foto en grande con flechas',pg.evaluate("!!document.querySelector('#fxV #fxVImg')&&document.querySelectorAll('#fxV .fx-nav .d-ib').length==2"))
    pg.evaluate("_fxVClose();_fxCClose()")
    # ───────────── 6 · Borrar el alquiler borra sus fotos
    pg.evaluate("window.__CF=[];showBookingById('b12')");wait(pg,1200)
    pg.locator('#SC .al-dz .btn-txt',has_text='Eliminar').click();wait(pg,2500)
    ok('Pregunta antes: «Se borrarán también las 12 fotos…»',any('12 fotos' in m for m in pg.evaluate("window.__CF")),pg.evaluate("window.__CF"))
    ok('Alquiler borrado de data/main',bk(main_doc(pg),'b12') is None)
    ok('Actas y fotos de b12 borradas de Firestore',fs_keys(pg,'users/demo/actas/b12')==[],fs_keys(pg,'users/demo/actas/b12'))
    # ───────────── 7 · Limpieza a 6 meses: aviso, «Conservar» y borrado
    pg.evaluate("_fxDaily(true)");wait(pg,1500)
    t=pg.evaluate("(document.getElementById('fxOld')||{}).textContent||''")
    ok('Aviso: «Hay fotos de 2 alquileres cerrados hace más de 6 meses»',"2 alquileres" in t and 'No se borra nada' in t,t)
    pg.locator('#fxOld .btn-pri',has_text='Revisar').click();wait(pg,700)
    ok('Revisar: lista b8 y b9 (no b41, devuelto hace 37 días)',pg.evaluate("document.querySelectorAll('#SC .ac-r').length")==2 and 'Marta' not in pg.evaluate("document.getElementById('SC').textContent"))
    pg.locator('#SC .ac-r',has_text='Antiguo Dos').locator('.btn-sec',has_text='Conservar').click();wait(pg,900)
    pg.locator('#SC .btn-dang',has_text='Borrar las fotos').click();wait(pg,3000)
    ok('b8: fotos borradas de Firestore',fs_keys(pg,'users/demo/actas/b8__entrega/fotos/')==[] and fs_keys(pg,'users/demo/actas/b8__devolucion/fotos/')==[])
    a8=pg.evaluate("JSON.parse(JSON.stringify(window.__FS['users/demo/actas/b8__entrega']))")
    ok('b8: el acta se queda (borradas, sin miniaturas, km)',a8.get('borradas') and a8['km']==1000 and all('th' not in f for f in a8['fotos']))
    a9=pg.evaluate("JSON.parse(JSON.stringify(window.__FS['users/demo/actas/b9__entrega']))")
    ok('b9 «Conservar»: keep=true y sus fotos siguen',a9.get('keep') is True and len(fs_keys(pg,'users/demo/actas/b9__entrega/fotos/'))==2)
    ok('b41 (reciente) intacto',len(fs_keys(pg,'users/demo/actas/b41__entrega/fotos/'))==2)
    pg.evaluate("_fxDaily(true)");wait(pg,1200)
    ok('Al día siguiente ya no avisa (nada pendiente)',not pg.evaluate("!!document.getElementById('fxOld')"))
    # ───────────── 8 · Copia v4: sin fotos y con aviso
    pg.evaluate("openBackup()");wait(pg,500)
    nt=pg.evaluate("document.getElementById('SC').textContent")
    ok('Hoja de copia: explica que las fotos de entrega y devolución solo van en la «copia con fotos» y cuándo se borran','incluye las fotos de entrega y devolución' in nt and 'Se borran 6 meses después' in nt,nt[:200])
    bo=pg.evaluate("JSON.stringify(_backupObject())")
    ok('La copia v4 no lleva actas ni fotos de entrega/devolución (ni miniaturas)','actas' not in bo and '__entrega' not in bo and not re.search(r'"(fotos|th)"\s*:',bo),len(bo))
    pg.evaluate("closeSheet()");ctx.close()
    # ───────────── 9 · Error de reglas de Firebase (permission-denied)
    c3,p3=new_page(br,NEW,deny=True)
    p3.evaluate("openV('v1')");wait(p3,700);p3.evaluate("toggleDelivery('b7')");wait(p3,900)
    shoot(p3,p3.locator('#fxBar .btn-pri'),M+'entrega_frontal.jpg','b7__entrega');wait(p3,1500)
    tt=toasts(p3)
    ok('Reglas: mensaje claro «Firebase no deja guardar las fotos… (issue #105)»',any('Firebase no deja guardar las fotos' in t and '#105' in t for t in tt),tt)
    ok('Reglas: la foto sigue en la cola del móvil',p3.evaluate("_fxAll('q').then(L=>L.filter(i=>i.t==='f').length)")==1)
    p3.locator('#fxBar .btn-txt',has_text='Confirmar entrega ya').click();wait(p3,1800)
    ok('Reglas: la entrega se guarda igual en data/main',bk(main_doc(p3),'b7').get('delivered') is True)
    ok('Reglas: el aviso sale una sola vez',sum('Firebase no deja' in t for t in toasts(p3))==1,toasts(p3))
    c3.close()
    br.close()
H.fin()
