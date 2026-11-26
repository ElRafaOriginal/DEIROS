# Dinero · cobros (#137): una sola forma de marcar el cobro en la ficha (cantidad, «Todo», «Solo alquiler», deshacer con
# confirmación), «Por cobrar» en el Inicio y en Finanzas del coche, lista del coche, cancelados con penalización,
# plataformas, y el RECIBO en PDF con el mismo estado de cobro que la ficha (la fianza va aparte).
# Origen: specs/b2/test_b2.py. Quitado lo de «igual que main» (texto de los recibos y del resto de PDF, importes):
# los recibos se comprueban con textos fijos; que todos los PDF se generen está en test_pdfs.py; importes fijos al final.
# Uso: python3 tests/test_cobros.py
import sys,os,json,re,datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
HTML=H.INDEX;SHOTS=H.CAPTURAS
route,D0,FAKE=H.route,H.datos(),H.FAKE
g={'P':"document.getElementById('mainPage')",'D':D0,'route':route,'FAKE':FAKE}
from playwright.sync_api import sync_playwright
errs=H.ERRS;chk=H.chk
SETUP=r"""
(()=>{const hoy=todayStr(),A=n=>addDays(hoy,n);
V.forEach(v=>{v.bookings=[];v.finances=(v.finances||[]).filter(f=>!f.bookingId&&!f._bookingId);});
const bk=(id,s,e,x)=>Object.assign({id,startDate:s,startTime:'10:00',endDate:e,endTime:'10:00',platform:'sinapp',amount:100,clientName:id,finance:[],fianza:0,paid:false},x||{});
const G=id=>V.find(v=>v.id===id);
G('v1').bookings.push(bk('bZ',A(-3),A(2),{clientName:'Zoe Cero',delivered:true,amount:400,fianza:200}));                       // en curso, sin cobrar
G('v1').bookings.push(bk('bP',A(-10),A(-5),{clientName:'Pablo Parcial',delivered:true,returned:true,amount:300,fianza:200,abonoReserva:100})); // devuelto, cobrado en parte
G('v2').bookings.push(bk('bT',A(-8),A(-6),{clientName:'Teresa Total',delivered:true,returned:true,amount:250}));                // en gestión, sin fianza
G('v3').bookings.push(bk('bV',A(-20),A(-15),{clientName:'Víctor Viejo',delivered:true,returned:true,amount:350,fianza:200,cobrado:true,paid:true})); // antiguo: cobrado sin cantidad
G('v3').bookings.push(bk('bA',A(-4),A(-1),{clientName:'Amaia Amovens',platform:'amovens',delivered:true,returned:true,amount:180}));            // plataforma
G('v4').bookings.push(bk('bF',A(5),A(8),{clientName:'Fede Futuro',amount:500,fianza:200}));                                   // futuro
G('v4').bookings.push(bk('bC',A(10),A(12),{clientName:'Carla Cancela',amount:400,cancelled:true,cancellation:{by:'client',penalty:60,date:A(-1)},
  finance:[{id:'pc1',date:A(-1),concept:'Penalización cancelación (cliente)',amount:60,type:'income',notes:'',_cancellation:true}]}));    // cancelado por el cliente, penalización 60
G('v5').bookings.push(bk('bX',A(-2),A(3),{clientName:'Xavi Extras',delivered:true,amount:200,fianza:200,extras:[{id:'exSilla',label:'Silla',amount:30}]})); // alquiler 230 + fianza 200
G('v5').bookings.push(bk('bD',A(-6),A(-4),{clientName:'Dani Deiros',amount:300,cancelled:true,cancellation:{by:'owner',penalty:30,date:A(-7)},
  finance:[{id:'pd1',date:A(-7),concept:'Penalización cancelación (DEIROS)',amount:30,type:'expense',notes:'',_cancellation:true}]}));   // penalización que paga DEIROS
V.forEach(v=>(v.bookings||[]).forEach(b=>proRataEntries(b.startDate,b.endDate,b.amount,b.platform,'',b.id).forEach(e=>v.finances.push(Object.assign(e,{vehicleId:v.id})))));
G('v4').finances.push({id:'vpc1',date:A(-1),concept:'Penalización cancelación (cliente)',amount:60,type:'income',_cancellation:true,bookingId:'bC',vehicleId:'v4'});
G('v5').finances.push({id:'vpd1',date:A(-7),concept:'Penalización cancelación (DEIROS)',amount:30,type:'expense',_cancellation:true,bookingId:'bD',vehicleId:'v5'});
try{_invalidateRsCache()}catch(e){}
_saveToCloud=async()=>{}; // sin nube en la prueba (el Firebase simulado no tiene runTransaction): solo evita el aviso «Error al guardar» en las capturas
window.__CF=[];window.__CFans=false;window.confirm=m=>{__CF.push(String(m));return window.__CFans;};
return true;})()
"""


# Captura del texto de un PDF (jsPDF envuelto; sin horas) y de todos los PDF con los mismos datos (recibos con varios estados de cobro; el resto, para comparar con main)
PDFS=r"""(async()=>{await ensureLib('jspdf');const O=window.jspdf.jsPDF,hoy=todayStr(),M=hoy.slice(0,7),P=addDays(M+'-01',-1).slice(0,7);
  const cap=async fn=>{const L=[];const W=function(){const d=new O(...arguments);const t=d.text;d.text=function(x){L.push(Array.isArray(x)?x.join(' '):String(x));return t.apply(this,arguments);};return d;};
    Object.assign(W,O);W.API=O.API;window.jspdf.jsPDF=W;const s=window._savePDF;window._savePDF=()=>{};try{await fn();}catch(e){L.push('ERROR '+e.message);}finally{window.jspdf.jsPDF=O;window._savePDF=s;}return L.filter(t=>!/\d{1,2}:\d{2}/.test(t));};
  const B=id=>{for(const v of V){const b=(v.bookings||[]).find(x=>x.id===id);if(b)return b;}};
  const rc={},ot={},rs={};const _g0=window.generateReceiptPDF;
  const generateReceiptPDF=async id=>{const k=Object.keys(rc).includes(id)?id+'@'+B(id).abonoReserva:id;rs[k]=typeof _bkCobro==='function'?[_bkCobro(B(id)).st,!!B(id).cancelled]:null;return _g0(id);};
  for(const id of ['bZ','bP','bT','bV','bA','bF','bC','bX','bD'])rc[id]=await cap(()=>generateReceiptPDF(id));
  Object.assign(B('bX'),{abonoReserva:230,cobrado:true,paid:true});rc['bX@230']=await cap(()=>generateReceiptPDF('bX'));   // alquiler cobrado, fianza aparte sin cobrar
  Object.assign(B('bX'),{abonoReserva:430});rc['bX@430']=await cap(()=>generateReceiptPDF('bX'));                         // alquiler + fianza
  Object.assign(B('bT'),{abonoReserva:250,cobrado:true,paid:true});rc['bT@250']=await cap(()=>generateReceiptPDF('bT'));   // cobrado, sin fianza
  window.__CFans=false;const al=window.__AL||[];window.__AL=[];window.__CF=[];
  return JSON.stringify({rc,ot,al,rs});})()"""
SNAP="id=>{for(const v of V){const b=(v.bookings||[]).find(x=>x.id===id);if(b)return {rec:b.abonoReserva,cobrado:b.cobrado,paid:b.paid,json:JSON.stringify(b)};}}"

def pdf_checks(my,p2):
    N=lambda x:x.replace('\xa0',' ').replace(' ',' ')
    F=lambda n:N(p2.evaluate("fmtF(%r)"%n))
    rc=lambda k:[N(t) for t in my['rc'][k]]
    st=lambda k:(rc(k)[2],rc(k)[3])  # sello y línea de estado (_pdfTitle: «Recibo», «.», sello; luego la línea)
    # ── Recibo: el mismo cobro que la ficha ──
    chk(st('bX@230')[0]=='PAGADO' and st('bX@230')[1]=='ALQUILER LIQUIDADO COMPLETAMENTE  —  la fianza va aparte','Recibo cobrado (230 de alquiler, fianza 200 sin cobrar): «PAGADO» y la fianza aparte',st('bX@230'))
    t=rc('bX@230');chk('ESTADO DE LA FIANZA: PENDIENTE DE COBRO' in t and 'NO SE SUMA AL ALQUILER' in t and 'ALQUILER COMPLETAMENTE ABONADO' in t,'Recibo cobrado: el bloque Fianza sigue con su propio estado y el alquiler «completamente abonado»')
    chk(st('bT@250')==('PAGADO','IMPORTE LIQUIDADO COMPLETAMENTE'),'Recibo cobrado sin fianza: «PAGADO» e «IMPORTE LIQUIDADO COMPLETAMENTE»',st('bT@250'))
    chk(st('bX@430')==('PAGADO','IMPORTE LIQUIDADO COMPLETAMENTE') and 'ESTADO DE LA FIANZA: COBRADA' in rc('bX@430'),'Recibo con «Todo» (alquiler + fianza): «PAGADO», todo liquidado y fianza «COBRADA»',st('bX@430'))
    chk(st('bP')==('PAGO PARCIAL','PAGO PARCIAL  —  recibido '+F(100)+' · alquiler '+F(200)+' por abonar'),'Recibo parcial (100 de 300, fianza 200): «PAGO PARCIAL», falta 200 del alquiler, sin sumar la fianza',st('bP'))
    chk(st('bV')[0]=='PAGADO' and 'ALQUILER COMPLETAMENTE ABONADO' in rc('bV') and F(350) in rc('bV'),'Recibo antiguo marcado cobrado sin cantidad: «PAGADO», recibido 350 y «completamente abonado»',st('bV'))
    chk(st('bZ')==('PENDIENTE DE COBRO','PENDIENTE DE LIQUIDACIÓN  —  alquiler '+F(400)+' por abonar'),'Recibo sin cobrar con fianza: pendiente solo el alquiler (400), la fianza aparte',st('bZ'))
    chk(st('bF')==('PENDIENTE DE COBRO','PENDIENTE DE LIQUIDACIÓN  —  alquiler '+F(500)+' por abonar'),'Recibo futuro con fianza: igual, sin la fianza',st('bF'))
    # Sello = estado de la ficha (Cobrado / Parcial / Pendiente) y lo que falta = el de la ficha
    m=my['rs'] # estado de la ficha (_bkCobro) en el momento de generar cada recibo
    MAP={'cob':'PAGADO','par':'PAGO PARCIAL','pen':'PENDIENTE DE COBRO','nada':'SIN IMPORTE'}
    PLAT={'bA':'LO COBRA AMOVENS'}  # #149: alquiler de plataforma sin cantidad apuntada → «Lo cobra Amovens/Getaround»
    okm=[k for k,x in m.items() if x and (rc(k)[2]==('CANCELADO' if x[1] else PLAT.get(k) or MAP[x[0]]))]
    chk(len(okm)==len(m),'Sello del recibo = estado de cobro de la ficha en los %d recibos (Cobrado → PAGADO, Parcial → PAGO PARCIAL, Pendiente → PENDIENTE DE COBRO; cancelado → CANCELADO; plataforma sin cobro apuntado → LO COBRA AMOVENS)'%len(m),{k:(m[k][0],rc(k)[2]) for k in m if k not in okm})
    for k in ('bA','bC','bD'):
        chk(len(rc(k))>20 and not any(x.startswith('ERROR') for x in rc(k)),'Recibo '+k+' (Amovens / cancelado por el cliente / por DEIROS): se genera con contenido',len(rc(k)))
    chk(rc('bC')[2]=='CANCELADO' and rc('bD')[2]=='CANCELADO','Recibos de alquileres cancelados: sello «CANCELADO»',(rc('bC')[2],rc('bD')[2]))
    chk(my['al']==[],'Sin alertas al generar los recibos',my['al'])
def ctxpage(br,path):
    ctx=H.new_context(br,viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True,is_mobile=True);ctx.route('**/*',route)
    ctx.add_init_script("window.__DATA=%s;localStorage.setItem('wg_theme','dark');localStorage.setItem('deiros_lastBackupAt',new Date().toISOString());window.alert=m=>{(window.__AL=window.__AL||[]).push(String(m))};"%json.dumps(D0))
    ctx.add_init_script(FAKE)
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(path));pg.wait_for_timeout(2000)
    return ctx,pg
def run():
  with sync_playwright() as p:
    br=H.launch(p)
    # Referencia: importes en main con los mismos datos
    c2,p2=ctxpage(br,HTML);p2.evaluate(SETUP);myP=json.loads(p2.evaluate(PDFS))
    pdf_checks(myP,p2);c2.close()
    ctx,pg=ctxpage(br,HTML)
    J=lambda js,a=None:pg.evaluate(js,a);W=lambda ms=400:pg.wait_for_timeout(ms)
    J(SETUP)
    F=lambda n:J("fmtF(%r)"%n);N=lambda x:x.replace('\xa0',' ')
    def tap(loc):
        try: loc.click(timeout=3000)
        except Exception as e: chk(False,'Toque',str(e).split('\n')[0][:140])
    sh_open=lambda:J("document.getElementById('SH').classList.contains('open')")
    sc=lambda:J("document.getElementById('SC').textContent")
    S=lambda i:J(SNAP,i)
    chip=lambda:J("(document.querySelector('#SC .al-s .al-h .chip')||{}).textContent||''").strip()
    falta=lambda:J("(document.querySelector('#SC .al-pd b')||{}).textContent||''")
    def guardar(bid,val):
        J("showBookingById(%r)"%bid);W(500)
        pg.fill('#abonoInput_'+bid,str(val));tap(pg.locator('#SC .al-in button'));W(500)
    # ── 0. Antes de tocar nada: Por cobrar ──
    pc=J("_porCobrar()");ids=sorted(r['b']['id'] for r in pc['rows'])
    chk(ids==sorted(['bZ','bP','bT','bC','bX']),'Por cobrar: empezados/terminados sin cobrar + cancelado con penalización; fuera el futuro, Amovens, el antiguo cobrado y la penalización que paga DEIROS',ids)
    chk(abs(pc['tot']-(400+200+250+60+230))<0.001,f'Por cobrar total = 400 + (300−100) + 250 + 60 + 230 = 1140',pc['tot'])
    # ── 1. Ficha: una sola forma (sin botón «Marcar cobrado»), estado Pendiente, atajos ──
    J("nav('dashboard');showBookingById('bZ')");W(600)
    tg=J("[...document.querySelectorAll('#SC .al-tg button')].map(b=>b.textContent.trim())")
    chk(len(tg)==2 and not any('obrado' in t for t in tg),'Ficha: la tira de estado ya no tiene «Marcar cobrado» (Entregado · Devuelto)',tg)
    chk(chip().endswith('Pendiente'),'Ficha bZ sin nada recibido: estado «Pendiente»',chip())
    at=J("[...document.querySelectorAll('#SC .al-cq button')].map(b=>b.textContent.replace(/\\s+/g,' ').trim())")
    chk(len(at)==2 and at[0]==N('Todo '+F(600)) and at[1]==N('Solo alquiler '+F(400)),'Atajos: «Todo 600 €» (alquiler + fianza) y «Solo alquiler 400 €»',at)
    chk(J("[...document.querySelectorAll('#SC .al-cq button,#SC .al-in button')].every(b=>b.getBoundingClientRect().height>=44)"),'Atajos y Guardar ≥ 44 px')
    if SHOTS:
        os.makedirs(SHOTS,exist_ok=True)
    # ── 2. Cantidad 0, parcial y total ──
    guardar('bZ',0);s=S('bZ')
    chk(s['rec']==0 and s['cobrado'] is False and s['paid'] is False and J("__CF.length")==0,'Cantidad 0: queda 0, cobrado=false, paid=false, sin preguntar',s)
    chk(sh_open() and 'Zoe Cero' in sc() and chip().endswith('Pendiente'),'Guardar no cierra la ficha (antes se cerraba)')
    guardar('bZ',150);s=S('bZ')
    chk(s['rec']==150 and s['cobrado'] is False and s['paid'] is False,'Cantidad parcial 150: cobrado=false y paid=false',s)
    chk(chip().endswith('Parcial') and falta()==F(250),f'Ficha: estado «Parcial» y «Falta por cobrar» {F(250)}',(chip(),falta()))
    chk(abs(J("_porCobrar().tot")-(1140-150))<0.001,'Por cobrar resta lo cobrado en parte (990)',J("_porCobrar().tot"))
    guardar('bZ',400);s=S('bZ')
    chk(s['rec']==400 and s['cobrado'] is True and s['paid'] is True,'Cantidad = alquiler (400): cobrado=true y paid=true',s)
    chk(chip().endswith('Cobrado') and falta()==F(0) and 'no incluida' in sc(),'Ficha: «Cobrado», falta 0 € y la fianza sale «no incluida» (va aparte)',chip())
    chk('bZ' not in [r['b']['id'] for r in J("_porCobrar()")['rows']],'Cobrado: sale de Por cobrar')
    # ── 3. Deshacer con Cancelar y con Aceptar ──
    J("__CF=[]");s0=S('bZ')['json'];guardar('bZ',100)
    cf=J("__CF.slice()")
    chk(len(cf)==1 and 'Quitar «Cobrado»' in cf[0] and F(100) in cf[0] and F(300) in cf[0],'Bajar de 400 a 100: pide confirmación y dice cuánto faltará (300)',cf)
    chk(S('bZ')['json']==s0 and J("document.getElementById('abonoInput_bZ').value")=='400','Cancelar: nada cambia y la casilla vuelve a 400')
    J("__CF=[]");tap(pg.locator('#SC button',has_text='Quitar cobro'));W(500);cf=J("__CF.slice()")
    chk(len(cf)==1 and F(400) in cf[0] and S('bZ')['json']==s0,'«Quitar cobro» pide confirmación (con la cantidad); Cancelar no cambia nada',cf)
    J("__CF=[];__CFans=true");tap(pg.locator('#SC button',has_text='Quitar cobro'));W(500);s=S('bZ')
    chk(s['rec']==0 and s['cobrado'] is False and s['paid'] is False and chip().endswith('Pendiente'),'Aceptar: recibido 0, cobrado/paid false, «Pendiente»',s)
    J("__CFans=false;__CF=[]")
    # ── 4. Atajos ──
    J("showBookingById('bX')");W(500)
    tap(pg.locator('#SC .al-cq button',has_text='Solo alquiler'));W(500);s=S('bX')
    chk(s['rec']==230 and s['cobrado'] is True and s['paid'] is True,'«Solo alquiler» en bX: 230 (200 + extra 30, sin la fianza) y cobrado',s)
    chk(sh_open() and chip().endswith('Cobrado') and J("document.querySelector('#SC .al-cq button[aria-pressed=\"true\"]').textContent").startswith('Solo alquiler'),'Guarda al momento, la ficha sigue abierta y el atajo queda marcado')
    if SHOTS:
        J("document.querySelector('#SC .al-s .al-h').scrollIntoView({block:'start'})");W(300);pg.screenshot(path=SHOTS+'/b2-02-ficha-cobros-atajos.png')
    tap(pg.locator('#SC .al-cq button',has_text='Todo'));W(500);s=S('bX')
    chk(s['rec']==430 and s['cobrado'] is True and J("__CF.length")==0,'«Todo»: 430 (alquiler + fianza), cobrado, sin preguntar',s)
    chk('incluida' in sc() and 'no incluida' not in sc(),'Con «Todo», la fianza sale «incluida»')
    # ── 5. Antiguo cobrado sin cantidad ──
    J("showBookingById('bV')");W(500)
    t=sc()
    chk(chip().endswith('Cobrado') and 'Marcado como cobrado sin cantidad' in t and J("document.querySelector('#SC .al-ch .chip').textContent")=='Terminado','Antiguo «cobrado» sin cantidad: sigue «Cobrado» y «Terminado», con el aviso para registrar la cantidad')
    chk(S('bV')['rec'] is None and S('bV')['cobrado'] is True,'Abrir la ficha no cambia sus datos')
    # ── 6. Plataforma ──
    J("showBookingById('bA')");W(500)
    chk('Lo cobra Amovens' in chip() and J("document.querySelector('#SC .al-ch .chip').textContent")=='Terminado' and 'no cuenta en «Por cobrar»' in sc(),'Amovens devuelto: «Lo cobra Amovens», «Terminado» (no «Por cobrar») y aviso',chip())
    # ── 7. Botón principal «Cobrar X €» del devuelto en parte ──
    J("showBookingById('bP')");W(500)
    pri=J("document.querySelector('#SC .al-pri').textContent.trim()")
    chk(J("document.querySelector('#SC .al-ch .chip').textContent")=='Por cobrar' and pri=='Cobrar '+F(200),'Devuelto con 100 de 300: chip «Por cobrar» y botón principal «Cobrar 200 €»',pri)
    if SHOTS:
        J("closeSheet()");W(200)
    # ── 8. Por cobrar en el Inicio y su lista ──
    J("closeSheet();nav('dashboard')");W(700)
    tile=J("[...document.querySelectorAll('#PC .dh-act')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())")
    exp=J("_porCobrar()")
    chk(len(tile)==3 and tile[1]=='FIANZAS' and tile[2]=='POR COBRAR','Inicio (móvil): «Por cobrar» al lado de «Fianzas», sin cifras (#162)',tile)
    chk(J("(()=>{const a=[...document.querySelectorAll('#PC .dh-act')].map(e=>e.getBoundingClientRect());return Math.abs(a[1].top-a[2].top)<1&&a[2].left>a[1].left&&a[0].width>a[1].width*1.8;})()"),'Móvil: Fianzas y Por cobrar en la misma fila; Coches libres a lo ancho encima')
    if SHOTS:J(g['P']+".scrollTop=0");W(200);pg.screenshot(path=SHOTS+'/b2-01-inicio-por-cobrar.png')
    tap(pg.locator('#PC .dh-act').nth(2));W(600)
    rows=J("[...document.querySelectorAll('#SC .fz-r')].map(r=>[r.querySelector('.t').textContent,r.querySelector('.r b').textContent,r.querySelector('.chip').textContent])")
    chk(sh_open() and 'Por cobrar' in sc() and len(rows)==len(exp['rows']),'Al tocarlo se abre la lista de esos alquileres',rows)
    want={'Zoe Cero':F(400),'Pablo Parcial':F(200),'Teresa Total':F(250),'Carla Cancela':F(60)}
    chk(all(dict((r[0],r[1]) for r in rows).get(k)==v for k,v in want.items()) and 'Xavi Extras' not in [r[0] for r in rows],'Cada fila con lo que falta (Zoe 400, Pablo 200, Teresa 250, Carla 60); Xavi ya cobrado no sale',rows)
    chk(J("(document.querySelector('#SC .al-pd b')||{}).textContent")==F(exp['tot']),'Total de la lista = _porCobrar',F(exp['tot']))
    if SHOTS:pg.screenshot(path=SHOTS+'/b2-03-lista-por-cobrar.png')
    tap(pg.locator('#SC .fz-r',has_text='Teresa Total').locator('button'));W(600)
    chk('Teresa Total' in sc() and 'Detalle del alquiler' in sc(),'«Ver alquiler» abre su ficha')
    tap(pg.locator('#SC .al-cq button',has_text='Todo'));W(600)
    chk(S('bT')['cobrado'] is True and S('bT')['rec']==250,'Cobrar «Todo» desde ahí (sin fianza = 250)')
    J("closeSheet()");W(300)
    tap(pg.locator('#PC .dh-act').nth(2));W(600)
    t2=J("[...document.querySelectorAll('#SC .fz-r .t')].map(e=>e.textContent)")
    chk(sh_open() and len(t2)==len(exp['rows'])-1 and 'Teresa Total' not in t2,'Al cerrar y volver a tocar «Por cobrar», la hoja tiene un alquiler menos',t2)
    J("closeSheet()");W(300)
    # ── 9. Escritorio: los 3 accesos en fila ──
    pg.set_viewport_size({'width':1280,'height':900});W(300);J("nav('dashboard')");W(600)
    chk(J("(()=>{const a=[...document.querySelectorAll('#PC .dh-act')].map(e=>e.getBoundingClientRect());return a.length===3&&Math.abs(a[0].top-a[2].top)<1&&a[1].left<a[2].left;})()"),'Escritorio: Coches libres · Fianzas · Por cobrar en una fila')
    pg.set_viewport_size({'width':390,'height':844});W(300)
    # ── 10. Finanzas del coche: mismo cálculo, toca y abre la lista ──
    J("openV('v1');switchTab('finances')");W(700)
    pd=J("(()=>{const p=document.querySelector('#PC .fl-pd');return p?[p.querySelector('b').textContent,p.querySelector('.d-meta').textContent,p.querySelector('.q').textContent]:null})()")
    chk(pd==[F(400+200),'2 alquileres con cobro pendiente','Por cobrar'],'Finanzas de v1: «Por cobrar» 600 = Zoe 400 + lo que falta de Pablo 200 (antes 700, sin restar lo recibido)',pd)
    J("document.querySelector('#PC .fl-pd').click()");W(500)
    chk(J("document.querySelectorAll('#SC .fz-r').length")==2 and 'Ford Focus' in sc(),'Tocarlo abre la lista de ese coche')
    J("closeSheet();openV('v4');switchTab('finances')");W(500)
    pd4=J("(()=>{const p=document.querySelector('#PC .fl-pd');return p?p.querySelector('b').textContent:null})()")
    chk(pd4==F(60),'v4: solo la penalización del cancelado (60); el futuro de 500 no cuenta (antes 560)',pd4)
    # ── 11. Lista de alquileres del coche: «Cobrar/Cobrado» por la cantidad ──
    J("closeSheet();openV('v1')");W(700)
    row=lambda:pg.locator('#PC .fl-bk').filter(has_text='Pablo Parcial')
    chk('Parcial' in row().text_content(),'Lista del coche: el devuelto con 100 de 300 sale «Parcial»',row().inner_text()[:80])
    J("__CF=[]");tap(row().locator('.ck-a button').nth(2));W(500);s=S('bP')
    chk(s['rec']==300 and s['cobrado'] is True and s['paid'] is True and J("__CF.length")==0,'«Cobrar» en la lista: recibido = 300 (cubre el alquiler), cobrado y paid',s)
    chk('Finalizado' in row().text_content(),'Y la fila pasa a «Finalizado»')
    s0=S('bP')['json'];tap(row().locator('.ck-a button').nth(2));W(500)
    chk(J("__CF.length")==1 and S('bP')['json']==s0,'«Cobrado» en la lista: pide confirmación; Cancelar no cambia nada')
    # ── 12. Cancelado con penalización: ficha ──
    J("showBookingById('bC')");W(500)
    at=J("[...document.querySelectorAll('#SC .al-cq button')].map(b=>b.textContent.replace(/\\s+/g,' ').trim())")
    chk(at==[N('Todo '+F(60))] and chip().endswith('Pendiente'),'Cancelado con penalización: un solo atajo «Todo 60 €» (sin fianza) y «Pendiente»',at)
    tap(pg.locator('#SC .al-cq button',has_text='Todo'));W(500)
    chk(S('bC')['cobrado'] is True and 'bC' not in [r['b']['id'] for r in J("_porCobrar()")['rows']],'Cobrada la penalización: sale de Por cobrar')
    J("closeSheet()")
    # ── 13. Importes fijos (antes: «igual que main») ──
    r=pg.evaluate(H.MONEY)
    chk(r['settle']=={'v2':[250,0,75,175,0,75]},'Liquidación del coche en gestión v2 (Teresa 250, cobrada): comisión 75, al propietario 175',r['settle'])
    chk(r['tIncExp']=={'v1':[700,0],'v2':[250,0],'v3':[944.99,607.7],'v4':[560,0],'v5':[230,30],'v6':[0,0]},'Ingresos y gastos por coche: los cobros no cambian lo facturado (v4: futuro 500 + penalización 60, sin el precio del cancelado; v5: 200 + 30 de extra − 30 de penalización que paga DEIROS)',r['tIncExp'])
    chk(r['biz']=={'2026-11 income':3919.99,'2026-11 expense':835.09,'2026-10 income':1280,'2026-10 expense':609},'Negocio por mes',r['biz'])
    chk(r['dash']==['INGRESOS MES 4094,99 €','GASTOS MES 835,09 €','BENEFICIO 2026 3930,90 €','BENEFICIO 3139,90 €'],'KPI del Resumen',r['dash'])
    chk(not J("window.__AL||[]"),'Sin alertas',J("window.__AL||[]"))
    br.close()
run()
H.fin()
