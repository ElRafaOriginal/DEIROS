# Dinero · devolución y fianza (#138): sección «Fianza» dentro de «Registrar devolución» (devolver, retener con motivo,
# «Más tarde», cargos mayores que la fianza → «Por cobrar», daños, plataformas, validaciones) y franja «Antes de entregar»
# (cobro, fianza, carnet, edad mínima de 26 años del conductor adicional, ficha del cliente, plataforma).
# Además (de specs/tests/test_bloque2.js): km extra a 0,19 €/km y combustible = litros × (precio + 2 €/L).
# Origen: specs/c2/test_c2.py. Lo de «igual que main» (cargos guardados e importes) se ha cambiado por valores fijos.
# Uso: python3 tests/test_devolucion.py
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
const bk=(id,s,e,x)=>Object.assign({id,startDate:s,startTime:'10:00',endDate:e,endTime:'10:00',platform:'sinapp',amount:300,clientName:id,finance:[],fianza:200,paid:false,kmStart:10000,deliveredFuelLevel:'Lleno (100%)'},x||{});
const G=id=>V.find(v=>v.id===id),dv={delivered:true};
// Devoluciones
G('v1').bookings.push(bk('rD',A(-3),A(0),Object.assign({clientName:'Diana Devuelve',abonoReserva:500,cobrado:true,paid:true},dv)));        // «Todo» cobrado, sin cargos
G('v2').bookings.push(bk('rR',A(-5),A(-1),Object.assign({clientName:'Rita Retiene',abonoReserva:300,cobrado:true,paid:true},dv)));         // en gestión, fianza aparte, cargo km 24,60
G('v3').bookings.push(bk('rM',A(-4),A(-1),Object.assign({clientName:'Mario Mayor',abonoReserva:500,cobrado:true,paid:true},dv)));          // «Todo», cargos 250 > fianza
G('v3').bookings.push(bk('rM2',A(-12),A(-8),Object.assign({clientName:'Mara Mayor',abonoReserva:300,cobrado:true,paid:true},dv)));        // fianza aparte, cargos 250 > fianza
G('v5').bookings.push(bk('rDm',A(-4),A(-1),Object.assign({clientName:'Dani Daños',abonoReserva:300,cobrado:true,paid:true},dv)));          // km 20 + daños 230
G('v4').bookings.push(bk('rP',A(-4),A(-1),Object.assign({clientName:'Pedro Plataforma',platform:'amovens'},dv)));                          // Amovens con fianza apuntada
G('v1').bookings.push(bk('rL',A(-20),A(-15),Object.assign({clientName:'Lola Luego',abonoReserva:300,cobrado:true,paid:true},dv)));         // «Más tarde» y cerrar en la ficha
G('v5').bookings.push(bk('rDC',A(-12),A(-8),Object.assign({clientName:'Dora Devuelve',abonoReserva:500,cobrado:true,paid:true},dv)));      // «Todo», devolver entera con cargos
G('v2').bookings.push(bk('rV',A(-12),A(-8),Object.assign({clientName:'Vera Valida',abonoReserva:300,cobrado:true,paid:true},dv)));         // validación del motivo
// Entregas
G('v4').bookings.push(bk('dW',hoy,A(5),{clientName:'Carla Caduca',clientDni:'11111111H',amount:400}));
G('v1').bookings.push(bk('dOk',A(1),A(4),{clientName:'Olga Orden',clientDni:'22222222J',abonoReserva:500,cobrado:true,paid:true}));
G('v2').bookings.push(bk('dNo',A(2),A(6),{clientName:'Nadia Nacimiento',clientDni:'33333333P',hasExtraDriver:true,extraDriverName:'Xavi Joven',extraDriverBirth:addDays(A(2),-365*20),extraDriverLicenseExp:A(900)}));
G('v3').bookings.push(bk('dNf',A(3),A(6),{clientName:'Fulano Sinficha'}));
G('v4').bookings.push(bk('dPl',A(8),A(9),{clientName:'Paula Plataforma',platform:'getaround',fianza:0}));
G('v5').bookings.push(bk('dEx',A(2),A(4),{clientName:'Eva Expirada',clientDni:'44444444A',abonoReserva:300,cobrado:true,paid:true}));
CL.push({id:'k1',name:'Carla Caduca',dni:'11111111H',phone:'',bookingIds:['dW'],birthdate:'1985-01-01',licenseExp:A(2)});
CL.push({id:'k2',name:'Olga Orden',dni:'22222222J',phone:'',bookingIds:['dOk'],birthdate:'1980-03-03',licenseExp:A(400)});
CL.push({id:'k3',name:'Nadia Nacimiento',dni:'33333333P',phone:'',bookingIds:['dNo']});
CL.push({id:'k4',name:'Eva Expirada',dni:'44444444A',phone:'',bookingIds:['dEx'],birthdate:'1975-05-05',licenseExp:A(-3)});
V.forEach(v=>(v.bookings||[]).forEach(b=>proRataEntries(b.startDate,b.endDate,b.amount,b.platform,'',b.id).forEach(e=>v.finances.push(Object.assign(e,{vehicleId:v.id})))));
try{_invalidateRsCache()}catch(e){}
_saveToCloud=async()=>{};
window.__CF=[];window.__CFans=false;window.confirm=m=>{__CF.push(String(m));return window.__CFans;};
// Registrar devolución con los mismos pasos en main y en la copia: km, combustible «Lleno» y los importes de cargo escritos
window.__ret=(bid,kmAmt,fuAmt)=>{for(const v of V)if((v.bookings||[]).some(b=>b.id===bid))openV(v.id);openReturnModal(bid);const g=id=>document.getElementById(id),ev=e=>e.dispatchEvent(new Event('input',{bubbles:true}));
  g('retKm').value='10500';ev(g('retKm'));document.querySelector('.al-fu[data-for="retFuel"] button[data-v="Lleno (100%)"]').click();
  g('retKmAmt').value=String(kmAmt);ev(g('retKmAmt'));g('retFuelAmt').value=String(fuAmt);ev(g('retFuelAmt'));};
return true;})()
"""
SNAP="id=>{for(const v of V){const b=(v.bookings||[]).find(x=>x.id===id);if(b)return {rec:b.abonoReserva,cob:b.cobrado,paid:b.paid,ret:b.returned,del:b.delivered,st:b.fianzaStatus,amt:b.fianzaRetainedAmount,why:b.fianzaRetainedReason,at:!!b.fianzaReturnedAt,rc:(b.finance||[]).filter(f=>f._returnCharge).map(f=>[f.concept,f.amount]),falta:_bkCobro(b).falta,cst:_bkCobro(b).st};}}"
# Las mismas devoluciones en main y en la copia (en la copia, además, la decisión de la fianza)
OPS=[('rD',0,0),('rR',24.6,0),('rM',150,100),('rM2',250,0),('rDm',20,0),('rP',30,0),('rL',0,0),('rDC',24.6,0)]
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
    ctx,pg=ctxpage(br,HTML)
    J=lambda js,a=None:pg.evaluate(js,a);W=lambda ms=400:pg.wait_for_timeout(ms)
    J(SETUP);S=lambda i:J(SNAP,i);F=lambda n:J("fmtF(%r)"%n);N=lambda x:x.replace('\xa0',' ')
    def tap(loc):
        try: loc.click(timeout=3000)
        except Exception as e: chk(False,'Toque',str(e).split('\n')[0][:140])
    sc=lambda:N(J("document.getElementById('SC').textContent"))
    seg=lambda:J("[...document.querySelectorAll('#retFzSeg button')].map(b=>[b.dataset.m,b.getAttribute('aria-pressed'),b.textContent.replace(/\\s+/g,' ').trim()])")
    res=lambda:N(J("(document.getElementById('retFzRes')||{}).textContent||''"))
    cob=lambda:N(J("(document.getElementById('retFzCob')||{}).textContent||''"))
    msg=lambda:N(J("(document.getElementById('retFzMsg')||{}).textContent||''"))
    confirm=lambda:tap(pg.locator('#SC button',has_text='Confirmar devolución'))
    ret=lambda b,k,f:(J("([b,k,f])=>__ret(b,k,f)",[b,k,f]),W(300))
    # ── 1. Sin cargos: «Devolver todo» ──
    ret('rD',0,0)
    chk(J("!!document.getElementById('retFzSeg')") and 'Fianza' in sc(),'La hoja «Registrar devolución» tiene la sección «05 Fianza»')
    s=seg();chk([x[0] for x in s]==['dev','ret','tarde'] and s[0][1]=='true' and s[1][2]=='Retener','Sin cargos: «Devolver todo» marcado por defecto (con «Retener» y «Más tarde»)',s)
    chk(res()==N(F(200)) and 'Sin cargos' in msg(),'A devolver = 200 € («Sin cargos: se devuelve entera»)',(res(),msg()))
    chk(J("[...document.querySelectorAll('#retFzSeg button,#retFzDn')].every(e=>e.getBoundingClientRect().height>=44)"),'Botones y casilla de la fianza ≥ 44 px')
    confirm();W(600);s=S('rD')
    chk(s['ret'] and s['st']=='returned' and s['at'] and s['rec']==500 and s['amt'] is None,'Confirmar: devuelto, fianza «Devuelta» (con fecha), lo recibido no cambia (500)',s)
    chk('Detalle del alquiler' in sc() and 'Devuelta' in sc(),'Después se abre la ficha del alquiler con la fianza «Devuelta» (y su botón de WhatsApp)')
    chk(J("(()=>{const b=V.find(v=>v.id==='v1').bookings.find(x=>x.id==='rD');return !!_waTxFz(b,V.find(v=>v.id==='v1'));})()"),'El WhatsApp «Fianza devuelta» queda disponible')
    J("closeSheet()")
    # ── 2. Cargos menores que la fianza: «Retener X» con motivo; fianza cobrada aparte ──
    ret('rR',24.6,0)
    s=seg();chk(s[1][1]=='true' and s[1][2]==N('Retener '+F(24.6)),'Con cargo de 24,60 €: «Retener 24,60 €» marcado por defecto',s)
    chk(J("document.getElementById('retFzAmt').value")=='24.6' and J("document.getElementById('retFzRsn').value")==N('Exceso de km '+F(24.6)),'Importe y motivo rellenados desde los cargos («Exceso de km 24,60 €»)',N(J("document.getElementById('retFzRsn').value")))
    chk(res()==N(F(175.4)),'A devolver = 200 − 24,60 = 175,40 €',res())
    chk(N(F(300))+' → '+N(F(324.6)) in cob() and 'no quedará nada' in cob(),'Avisa: lo recibido pasa de 300 a 324,60 (la fianza paga el cargo) y no queda nada por cobrar',cob())
    pg.fill('#retFzDn','10');W(200)
    chk(res()==N(F(165.4)) and 'Daños u otros '+N(F(10)) in N(J("document.getElementById('retFzRsn').value")),'«Daños u otros» 10 €: a devolver 165,40 y el motivo lo añade')
    pg.fill('#retFzDn','');W(200)
    if SHOTS:J("document.getElementById('actaOf')?.remove();document.querySelector('#SC .al-h:has(+ .rf-l)').scrollIntoView({block:'start'})");W(300);pg.screenshot(path=SHOTS+'/c2-1-devolucion-retener.png')
    confirm();W(600);s=S('rR')
    chk(s['st']=='partial' and s['amt']==24.6 and s['why']==N('Exceso de km '+F(24.6)) and '\xa0' not in s['why'] and s['at'],'Fianza «Retenida en parte»: 24,60 € y motivo, con los campos de siempre',s)
    chk(s['rec']==324.6 and s['cob'] and s['falta']==0,'Lo recibido 324,60 → «Cobrado», nada en «Por cobrar»',s)
    chk('rR' not in [r['b']['id'] for r in J("_porCobrar()")['rows']],'rR no sale en «Por cobrar»')
    J("closeSheet()")
    # ── 3. Cargos mayores que la fianza («Todo» cobrado): retener entera y el resto a «Por cobrar» ──
    ret('rM',150,100)
    s=seg();chk(s[1][1]=='true' and s[1][2]==N('Retener '+F(200)),'Cargos 250 > fianza 200: «Retener 200 €»',s)
    chk(res()==N(F(0)) and N(F(50)) in msg() and 'debe además' in msg(),'A devolver 0 € y «el cliente debe además 50 €»',msg())
    chk(N(F(50)) in cob() and 'Por cobrar' in cob() and '→' not in cob(),'«Quedará por cobrar 50 €», sin tocar lo recibido (la fianza ya estaba en lo recibido)',cob())
    if SHOTS:J("document.getElementById('actaOf')?.remove();document.querySelector('#SC .al-h:has(+ .rf-l)').scrollIntoView({block:'start'})");W(300);pg.screenshot(path=SHOTS+'/c2-2-devolucion-cargos-mayores.png')
    confirm();W(600);s=S('rM')
    chk(s['st']=='retained' and s['amt']==200 and s['rec']==500 and s['falta']==50 and s['cst']=='par','Fianza «Retenida» (200), recibido 500 y falta 50 → «Parcial»',s)
    pc=J("_porCobrar()");row=[r for r in pc['rows'] if r['b']['id']=='rM']
    chk(len(row)==1,'rM sale en «Por cobrar» del Inicio (mecanismo de #137)',[r['b']['id'] for r in pc['rows']])
    J("closeSheet()")
    ret('rM2',250,0)
    chk(N(F(300))+' → '+N(F(500)) in cob() and N(F(50)) in cob(),'Fianza aparte y cargos 250: lo recibido 300 → 500 y quedan 50 por cobrar',cob())
    confirm();W(600);s=S('rM2')
    chk(s['st']=='retained' and s['rec']==500 and s['falta']==50,'rM2: «Retenida», recibido 500, falta 50',s)
    J("closeSheet()")
    # ── 3b. Daños que superan lo que queda: no se apuntan solos ──
    ret('rDm',20,0);pg.fill('#retFzDn','230');W(200)
    chk(N(J("document.getElementById('retFzRB').textContent"))==N(F(200)) and N(F(50)) in cob() and 'no se apuntan solos' in cob(),'Km 20 + daños 230: retener 200; avisa de que 50 € de daños no se apuntan solos',cob())
    confirm();W(600);s=S('rDm')
    chk(s['st']=='retained' and s['rec']==320 and s['falta']==0 and 'Daños u otros' in N(s['why']),'rDm: «Retenida», recibido 320 (el km lo paga la fianza), sin «Por cobrar»; los daños no son ingreso',s)
    J("closeSheet()")
    # ── 4. Fianza de plataforma ──
    ret('rP',30,0)
    s=seg();chk([x[0] for x in s]==['dev','tarde'] and s[0][2]=='Devuelta' and s[1][1]=='true','Amovens: sin «Retener»; «Devuelta» o «Más tarde» (por defecto, con cargos)',s)
    chk('la gestiona Amovens' in sc() and not J("document.getElementById('retFzDn')") and not J("document.getElementById('retFzRes')"),'Explica que la gestiona Amovens y que los cargos se reclaman allí; sin resta ni daños')
    tap(pg.locator('#retFzSeg button[data-m=dev]'));W(200);confirm();W(600);s=S('rP')
    chk(s['st']=='returned' and s['rec'] is None,'Elegida «Devuelta»: fianza devuelta y lo recibido sin tocar',s)
    J("closeSheet()")
    # ── 5. «Más tarde» y cerrar después desde la ficha, como siempre ──
    ret('rL',0,0);tap(pg.locator('#retFzSeg button[data-m=tarde]'));W(200)
    chk('queda pendiente' in msg() and res()=='—','«Más tarde»: aviso de que queda pendiente',msg())
    confirm();W(600);s=S('rL')
    chk(s['ret'] and (s['st'] in (None,'','pending')) and J("document.getElementById('SH').classList.contains('open')")==False,'Devuelto con la fianza pendiente (como antes: no se abre nada más)',s)
    J("nav('dashboard')");W(500);t=J("[...document.querySelectorAll('#PC .dh-act')].map(e=>e.innerText.replace(/\\s+/g,' '))")
    chk(any('FIANZAS' in x for x in t),'El Inicio sigue con «Fianzas»',t)
    J("showBookingById('rL')");W(500)
    J("document.querySelector('#SC details.al-acc').open=true");pg.fill('#fzAmt_rL','50');pg.fill('#fzRsn_rL','Arañazo en el paragolpes')
    tap(pg.locator('#SC button',has_text='Retener parte'));W(500);s=S('rL')
    chk(s['st']=='partial' and s['amt']==50 and s['why']=='Arañazo en el paragolpes','Cerrada después desde la ficha («Retener una parte»), igual que siempre',s)
    J("closeSheet()")
    # ── 6. «Todo» cobrado y devolver entera con cargos: pide confirmación al bajar lo recibido ──
    ret('rDC',24.6,0);tap(pg.locator('#retFzSeg button[data-m=dev]'));W(200)
    chk('se cobran aparte' in msg() and N(F(500))+' → '+N(F(300)) in cob() and N(F(24.6)) in cob(),'Devolver entera con cargos: avisa (500 → 300 y quedan 24,60 por cobrar)',(msg(),cob()))
    J("__CF=[];__CFans=true");confirm();W(600);cf=J("__CF.slice()");J("__CFans=false");s=S('rDC')
    chk(len(cf)==1 and 'Quitar «Cobrado»' in cf[0],'Pide la confirmación de siempre (#137) antes de bajar lo recibido',cf)
    chk(s['st']=='returned' and s['rec']==300 and s['falta']==24.6,'Aceptada: fianza «Devuelta», recibido 300 y 24,60 en «Por cobrar»',s)
    J("closeSheet()")
    # ── 7. Validación: retener sin motivo no guarda nada ──
    ret('rV',30,0);pg.fill('#retFzRsn','');W(100);J("window.__AL=[]");confirm();W(400);s=S('rV')
    chk(J("window.__AL")==['Indica el motivo de la retención'] and not s['ret'] and not s['rc'],'Retener sin motivo: aviso de siempre y no se guarda la devolución',(J("window.__AL"),s))
    pg.fill('#retFzAmt','250');pg.fill('#retFzRsn','x');J("window.__AL=[]");confirm();W(400)
    chk(len(J("window.__AL"))==1 and 'no superar la fianza' in J("window.__AL")[0] and not S('rV')['ret'],'Retener más que la fianza: aviso y nada guardado')
    J("closeSheet();window.__AL=[]")
    # ── 8. Cargos guardados (valores fijos; antes «igual que main») ──
    EXP={'rD':[],'rR':[['Exceso de km',24.6]],'rM':[['Exceso de km',150],['Combustible faltante',100]],'rM2':[['Exceso de km',250]],'rDm':[['Exceso de km',20]],
         'rP':[['Exceso de km',30]],'rL':[],'rDC':[['Exceso de km',24.6]]}
    got={b:S(b)['rc'] for b,_,_ in OPS}
    chk(got==EXP and all(S(b)['ret'] for b,_,_ in OPS),'Cargos de km y combustible guardados como cobros de la devolución (_returnCharge) en las %d devoluciones'%len(OPS),got)
    # ── 9. «Antes de entregar» ──
    J("openV('v4');_fxDeliver('dW')");W(700)
    rows=lambda:J("[...document.querySelectorAll('#fxPre .fx-pr')].map(r=>[r.className.replace('fx-pr','').trim(),r.querySelector('span').textContent.replace(/\\s+/g,' ').trim(),(r.querySelector('button')||{}).textContent||''])")
    pchip=lambda:N(J("(document.querySelector('#fxPre .fx-ph .chip')||{}).textContent||''")).strip()
    r=[[a,N(b_),N(c)] for a,b_,c in rows()]
    chk(J("!!document.querySelector('#SC .stitle')&&document.getElementById('fxPre').compareDocumentPosition(document.getElementById('fxKm'))&4"),'La franja está arriba, antes de «01 Km y combustible»')
    chk(r[0]==['w','Falta cobrar '+N(F(400))+' del alquiler','Cobrar'],'Falta cobrar 400 € del alquiler, con «Cobrar»',r[0])
    chk(r[1]==['w','Fianza: faltan '+N(F(200))+' en lo recibido','Todo '+N(F(600))],'Fianza: faltan 200 €, con «Todo 600 €» (como la ficha)',r[1])
    import datetime
    exp=(H.HOY+datetime.timedelta(days=2)).strftime('%d/%m/%Y')
    chk(r[2]==['e','El carnet caduca antes de la devolución ('+exp+')',''],'Carnet que caduca antes de la devolución: aviso rojo con la fecha (texto de la ficha del cliente)',r[2])
    chk(pchip()=='3 por revisar' and len(r)==3,'Cabecera «3 por revisar»',pchip())
    chk(J("[...document.querySelectorAll('#fxPre button')].every(b=>b.getBoundingClientRect().height>=44)"),'Botones de la franja ≥ 44 px')
    if SHOTS:J("document.getElementById('actaOf')?.remove();document.querySelector('#SC .d-ch').scrollIntoView({block:'start'})");W(300);pg.screenshot(path=SHOTS+'/c2-3-entregar-antes.png')
    pg.fill('#fxKm','12345')
    tap(pg.locator('#fxPre button',has_text='Cobrar'));W(500);s=S('dW');r=rows()
    chk(s['rec']==400 and s['cob'] and N(r[0][1])=='Alquiler cobrado' and r[0][0]=='ok','«Cobrar»: recibido 400 (cobrado) y la fila pasa a «Alquiler cobrado»',(s,r[0]))
    chk(J("document.getElementById('fxKm').value")=='12345' and 'Entregar coche' in sc(),'La hoja sigue abierta y no se pierde lo escrito')
    tap(pg.locator('#fxPre button',has_text='Todo'));W(500);s=S('dW');r=rows()
    chk(s['rec']==600 and N(r[1][1])==N('Fianza cobrada · '+F(200)) and pchip()=='1 por revisar','«Todo»: recibido 600, «Fianza cobrada» y queda 1 aviso (el carnet)',(s,r[1],pchip()))
    J("window.__AL=[]");J("_fxConfirmDelivery()");W(600);s=S('dW')
    chk(s['del'] and J("window.__AL")==[],'No bloquea: se entrega con el aviso del carnet')
    J("closeSheet()")
    J("openV('v1');_fxDeliver('dOk')");W(500);r=rows()
    chk([x[0] for x in r]==['ok','ok','ok'] and pchip()=='Todo en orden','Todo cobrado (alquiler + fianza) y ficha en regla: «Todo en orden» con 3 filas en verde',r)
    J("closeSheet();openV('v2');_fxDeliver('dNo')");W(500);r=[[a,N(b_)] for a,b_,_ in rows()]
    chk(['w','Falta la fecha de nacimiento del cliente: es obligatoria para comprobar la edad mínima (26 años).'] in r and ['w','Falta la caducidad del carnet'] in r,'Ficha sin nacimiento ni caducidad: avisos con el texto de #112',r)
    chk(['e','Conductor adicional: menor de 26 en la fecha de inicio: no se puede alquilar'] in r,'Conductor adicional de 20 años: aviso rojo (regla de 26 años)',r)
    J("closeSheet();openV('v5');_fxDeliver('dEx')");W(500);r=[[a,N(b_)] for a,b_,_ in rows()]
    exp=(H.HOY-datetime.timedelta(days=3)).strftime('%d/%m/%Y')
    chk(['e','Carnet caducado el '+exp] in r,'Carnet ya caducado: «Carnet caducado el …»',r)
    J("closeSheet();openV('v3');_fxDeliver('dNf')");W(500);r=[[a,N(b_)] for a,b_,_ in rows()]
    chk(['w','Sin ficha de cliente: no se pueden comprobar la edad ni el carnet'] in r,'Sin ficha de cliente: lo dice',r)
    J("closeSheet();openV('v4');_fxDeliver('dPl')");W(500);r=[[a,N(b_)] for a,b_,_ in rows()]
    chk(r[0]==['','Lo cobra Getaround'] and not any('Fianza' in x[1] for x in r),'Getaround: «Lo cobra Getaround» y sin fila de fianza',r)
    tap(pg.locator('#fxPre button',has_text='Contrato'));W(600)
    chk('Contrato de alquiler' in sc(),'«Contrato» abre el contrato de ese alquiler')
    J("closeSheet()")
    # ── 10. Importes fijos ──
    r=pg.evaluate(H.MONEY)
    chk(r['settle']=={'v2':[924.6,0,277.38,647.22,0,277.38]},'Liquidación de v2 en gestión (alquileres + cargo de km): 924,60, comisión 277,38, al propietario 647,22',r['settle'])
    chk(r['tIncExp']=={'v1':[900,0],'v2':[924.6,0],'v3':[1814.99,607.7],'v4':[1030,0],'v5':[944.6,0],'v6':[0,0]},'Ingresos y gastos por coche (los cargos de la devolución suman; la fianza y los daños no son ingreso)',r['tIncExp'])
    chk(r['biz']=={'2026-11 income':6386.97,'2026-11 expense':805.09,'2026-10 income':1270,'2026-10 expense':609},'Negocio por mes',r['biz'])
    chk(r['dash']==['INGRESOS MES 7034,19 €','GASTOS MES 805,09 €','BENEFICIO 2026 6890,10 €','BENEFICIO 6109,10 €'],'KPI del Resumen',r['dash'])
    # ── 11. Km y combustible en la devolución (de specs/tests/test_bloque2.js, ahora con la app real) ──
    J("""(()=>{const v=V.find(x=>x.id==='v1');v.tankL=50;v.fuel='Gasolina';
      v.bookings.push({id:'kF',startDate:addDays(todayStr(),-4),startTime:'10:00',endDate:todayStr(),endTime:'10:00',platform:'sinapp',amount:200,clientName:'Km Fuel',finance:[],fianza:0,
        delivered:true,kmStart:10000,deliveredFuelLevel:'Lleno (100%)',extras:[{id:'exKmPrepago',label:'Km sueltos (300 km × 0,15€)',amount:45}]});})()""")
    chk(J("_kmPrepagoOf({extras:[{id:'exKmPrepago',label:'Km sueltos (300 km × 0,15€)',amount:45}]})")==300 and J("_kmPrepagoOf({extras:[{id:'exKmPrepago',label:'Km sueltos',amount:30}]})")==200,'Km sueltos prepagados: de la etiqueta (300) o del importe a 0,15 €/km (30 € → 200)')
    chk(J("_fuelFrac('Reserva')===0.1&&_fuelFrac('Lleno (100%)')===1&&_fuelFrac('1/4')===0.25"),'Niveles de combustible: Lleno 1, 1/4 0,25, Reserva 0,1')
    chk(J("_fuelProd('Diésel')==='ga'&&_fuelProd('Gasolina')==='e5'&&_fuelProd('GLP')==='glp'"),'Carburante del coche → producto del Ministerio')
    chk(J("_fuelRecargo()")==2,'Recargo por defecto: 2 €/L')
    chk(J("_fianzaDefault()")=='200','Fianza por defecto: 200 €')
    J("openV('v1');openReturnModal('kF')");W(500)
    chk(J("_retKmRate")==0.19,'Km excedidos a la devolución: 0,19 €/km',J("_retKmRate"))
    chk(J("_retKmLimit===calcKmInc(4,false)+300"),'Límite de km = los incluidos por días + 300 km sueltos',J("[_retKmLimit,calcKmInc(4,false)]"))
    J("""(()=>{const g=id=>document.getElementById(id),ev=e=>e.dispatchEvent(new Event('input',{bubbles:true}));
      g('retKm').value=String(10000+_retKmLimit+100);ev(g('retKm'));document.querySelector('.al-fu[data-for="retFuel"] button[data-v="1/4"]').click();
      g('retFuelPrice').value='1.5';ev(g('retFuelPrice'));})()""");W(300)
    fu=J("[document.getElementById('retFuelL').value,document.getElementById('retFuelAmt').value,document.getElementById('retKmAmt').value]")
    chk(float(fu[0])==37.5 and float(fu[1])==131.25,'Combustible: 50 L × (1 − 1/4) = 37,5 L × (1,50 + 2 €/L) = 131,25 €',fu)
    chk(abs(float(fu[2])-19)<0.001,'Exceso de 100 km × 0,19 = 19 €',fu[2])
    J("document.getElementById('retFzSeg')&&document.querySelector('#retFzSeg button[data-m=tarde]')&&document.querySelector('#retFzSeg button[data-m=tarde]').click()");W(200)
    tap(pg.locator('#SC button',has_text='Confirmar devolución'));W(600)
    fc=J("V.find(v=>v.id==='v1').bookings.find(b=>b.id==='kF').finance.filter(f=>f._returnCharge).map(f=>[f.concept,f.amount,f.notes||''])")
    chk(any(f[0]=='Combustible faltante' and f[1]==131.25 and '37.5 L' in f[2] for f in fc) and any(f[0]=='Exceso de km' and abs(f[1]-19)<0.001 for f in fc),'Cobros guardados: combustible 131,25 € (con los litros en la nota) y exceso de km 19 €',fc)
    J("closeSheet()")
    # Precio medio del municipio (precios.json de prueba servido por el arnés)
    J("(()=>{const v=V.find(x=>x.id==='v5');v.tankL=60;v.bookings.push({id:'kG',startDate:addDays(todayStr(),-2),startTime:'10:00',endDate:todayStr(),endTime:'10:00',platform:'sinapp',amount:90,clientName:'Precio Muni',finance:[],fianza:0,delivered:true,kmStart:0,deliveredFuelLevel:'Lleno (100%)'});openV('v5');openReturnModal('kG');})()");W(500)
    J("(async()=>{const g=id=>document.getElementById(id);g('retFuelL').value='30';await _retPriceMuni('Pinto (MADRID)');})()");W(500)
    pm=J("[document.getElementById('retFuelPrice').value,document.getElementById('retPriceInfo').textContent,document.getElementById('retFuelAmt').value]")
    chk(pm[0]=='1.429' and 'Media de 11 gasolineras en Pinto' in pm[1] and 'datos del 15/11/2026' in pm[1],'Precio del municipio: Pinto, gasóleo A 1,429 €/L (media de 11 gasolineras)',pm)
    chk(abs(float(pm[2])-round(30*(1.429+2),2))<0.001,'Importe = 30 L × (1,429 + 2) = 102,87 €',pm[2])
    J("closeSheet()")
    br.close()
run()
H.fin()
