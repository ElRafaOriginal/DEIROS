# Extra de entrega (#121): un solo «Entrega» con importe libre (50 € por defecto, decimales con coma) en el alta, la edición,
# el presupuesto (y al convertirlo en alquiler), el contrato y el recibo; los alquileres y presupuestos ANTIGUOS con
# «Entrega a domicilio» 49 € y «Aeropuerto» 59 € (tests/datos/entrega121_antiguos.json, creados con la app anterior) se
# siguen viendo, editando y cobrando igual.
# Origen: specs/e121/test_e121.py. La fase 1 (crear los antiguos con main) es ahora el fichero de datos fijo; las
# comparaciones «igual que main» se han cambiado por importes y textos fijos o se han quitado (huellas de totales).
# Uso: python3 tests/test_entrega_extra.py
import sys,os,json,re,datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
import base64,subprocess,copy,tempfile
HTML=H.INDEX;SHOTS=H.CAPTURAS
route,D0,FAKE=H.route,H.datos(),H.FAKE
g={'P':"document.getElementById('mainPage')",'D':D0,'route':route,'FAKE':FAKE}
import datetime
hoy=H.HOY;d=lambda n:(hoy+datetime.timedelta(days=n)).isoformat()
from playwright.sync_api import sync_playwright
ERR=H.ERRS
def ok(n,c,i=''):H.chk(c,n,i)
TMP=tempfile.mkdtemp(prefix='deiros_e121_')
CAP="""window.__PDF=[];_savePDF=function(doc,fn){window.__PDF.push([fn,doc.output('datauristring')]);};0"""
def pdftxt(uri):
    p=os.path.join(TMP,'x.pdf');open(p,'wb').write(base64.b64decode(uri.split(',',1)[1]))
    return subprocess.run(['pdftotext','-raw',p,'-'],capture_output=True,text=True).stdout.replace(' ',' ')
def lastpdf(pg):
    a=pg.evaluate("window.__PDF.length?window.__PDF[window.__PDF.length-1][1]:''")
    pg.evaluate("window.__PDF=[]");return pdftxt(a) if a else ''
def mkpage(b,html,data,tag):
    ctx=H.new_context(b,viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True,is_mobile=True);ctx.route('**/*',route)
    ctx.add_init_script("window.__DATA=%s;localStorage.setItem('wg_theme','dark');localStorage.setItem('deiros_lastBackupAt',new Date().toISOString());window.alert=m=>{(window.__AL=window.__AL||[]).push(String(m))};window.confirm=()=>true;"%json.dumps(data))
    ctx.add_init_script(FAKE)
    pg=ctx.new_page();pg.on('pageerror',lambda e:ERR.append(tag+': '+str(e)))
    pg.goto('file://'+os.path.abspath(html));pg.wait_for_timeout(2200);pg.evaluate(CAP);return ctx,pg
J=lambda pg,js,a=None:pg.evaluate(js,a)
W=lambda pg,ms=350:pg.wait_for_timeout(ms)
# Alta con la interfaz: v1, fechas libres, cliente c1 (con nacimiento), importe 100; ticks = filas a marcar; amt = texto del importe de la Entrega
def step1(pg,s):
    J(pg,"""([s,e])=>{const set=(i,v)=>{const el=document.getElementById(i);el.value=v;el.dispatchEvent(new Event('input',{bubbles:true}));};
      set('rSD',s);set('rST','10:00');set('rED',e);set('rET','10:00');_clPickerSelect('rClientPicker','c1');const a=document.getElementById('rAmt');a.value='100';a.dataset.autoCalc='0';_recalcRentalExtras();}""",[d(s),d(s+3)])
def alta(pg,s,ticks,amt=None):
    J(pg,"try{closeSheet()}catch(e){};openV('v1');openNewRental()");W(pg,600)
    step1(pg,s);J(pg,"_rwGo(2)");W(pg)
    for t in ticks:pg.locator('#row_ex_'+t).click();W(pg,120)
    if amt is not None:pg.locator('#exEntregaImp').fill(amt);W(pg,120)
    tot=J(pg,"document.getElementById('exTotalAmt').textContent")
    J(pg,"window.__NB=new Set(V.flatMap(v=>(v.bookings||[]).map(b=>b.id)))");J(pg,"_rwGo(3)");W(pg)
    shot=None
    J(pg,"submitRental()");W(pg,700)
    bid=J(pg,"V.flatMap(v=>(v.bookings||[]).map(b=>b.id)).find(i=>!window.__NB.has(i))")
    return bid,tot
def bk(pg,bid):return J(pg,"id=>{for(const v of V){const b=(v.bookings||[]).find(x=>x.id===id);if(b)return JSON.parse(JSON.stringify({b,vf:(v.finances||[]).filter(f=>f._bookingId===id||f.bookingId===id).map(f=>({t:f.type,c:f.category,a:f.amount,d:f.date,x:!!f._autoExtra})),tot:_bookingClientTotal(b),real:_bookingRealTotal(b)}));}}",bid)
def strip(x):
    x=copy.deepcopy(x);b=x['b'];b.pop('financeIds',None);b.pop('financeId',None);b['finance']=[{k:v for k,v in f.items() if k!='id'} for f in b.get('finance',[])];return x
def editar(pg,bid,amt=None,untick=None):
    J(pg,"try{closeSheet()}catch(e){};id=>{const v=V.find(v=>(v.bookings||[]).some(b=>b.id===id));openV(v.id);editBooking(id)}",bid);W(pg,700)
    st=J(pg,"({ent:!!document.getElementById('ex_exEntregaDomicilio')?.checked,aer:document.getElementById('row_ex_exEntregaAeropuerto')?(document.getElementById('ex_exEntregaAeropuerto').checked?'marcada':'sin marcar'):'no existe',val:document.getElementById('exEntregaImp')?.value,tot:document.getElementById('exTotalAmt').textContent,inp:document.getElementById('exEntregaImp')?.getAttribute('inputmode')})")
    if amt is not None:pg.locator('#exEntregaImp').fill(amt);W(pg,120)
    if untick:pg.locator('#row_ex_'+untick).click();W(pg,120)
    J(pg,"id=>submitEditBooking(id)",bid);W(pg,700);return st
def contrato(pg,bid):
    J(pg,"try{closeSheet()}catch(e){};id=>{const v=V.find(v=>(v.bookings||[]).some(b=>b.id===id));openContractForm(v.id,id)}",bid);W(pg,700)
    st=J(pg,"({ent:!!document.getElementById('ex_exEntregaDomicilio')?.checked,val:document.getElementById('exEntregaImp')?.value,aer:!!document.getElementById('ex_exEntregaAeropuerto')?.checked,tot:document.getElementById('exTotalAmt').textContent})")
    J(pg,"id=>{const v=V.find(v=>(v.bookings||[]).some(b=>b.id===id));generateContractPDF(v.id,id)}",bid);W(pg,1500);return st,lastpdf(pg)
def recibo(pg,bid):J(pg,"id=>generateReceiptPDF(id)",bid);W(pg,1500);return lastpdf(pg)
def ficha(pg,bid):
    J(pg,"try{closeSheet()}catch(e){};id=>showBookingById(id)",bid);W(pg,700)
    return J(pg,"document.getElementById('SC').innerText.replace(/\\s+/g,' ')")
def presu(pg,ticks,amt=None,s=80,qid=None,shot=None):
    J(pg,"try{closeSheet()}catch(e){}");
    if qid:J(pg,"id=>openEditQuote(id)",qid)
    else:J(pg,"openNewQuote()")
    W(pg,500)
    if not qid:
        J(pg,"([s,e])=>{document.getElementById('qVehicle').value='v4';document.getElementById('qStart').value=s;document.getElementById('qEnd').value=e;_clPickerSelect('qClient','c1');_calcQuoteTotal();}",[d(s),d(s+4)])
    J(pg,"_qwGo(2)");W(pg)
    for t in ticks:pg.locator('[data-qexid="%s"]'%t).click();W(pg,120)
    if amt is not None:pg.locator('#qamt_exEntregaDomicilio').fill(amt);W(pg,120)
    if shot:
        pg.locator('[data-qexid="exEntregaDomicilio"]').scroll_into_view_if_needed();W(pg,300);pg.screenshot(path=shot)
    st=J(pg,"({val:document.getElementById('qamt_exEntregaDomicilio')?.value,aer:!!document.querySelector('[data-qexid=\"exEntregaAeropuerto\"]'),inp:document.getElementById('qamt_exEntregaDomicilio')?.getAttribute('inputmode')})")
    J(pg,"window.__NQ=new Set(QT.map(q=>q.id))");J(pg,"_qwGo(3)");W(pg);J(pg,"_saveQuote()");W(pg,600)
    q=J(pg,"id=>JSON.parse(JSON.stringify(id?QT.find(q=>q.id===id):QT.find(q=>!window.__NQ.has(q.id))))",qid)
    return q,st
def qpdf(pg,qid):J(pg,"id=>generateQuotePDF(id)",qid);W(pg,1500);return lastpdf(pg)
FP="""JSON.stringify(V.map(v=>({id:v.id,b:(v.bookings||[]).map(b=>[b.id,_bookingClientTotal(b),_bookingRealTotal(b)]),f:_getVehicleAllFinancesDisplay(v).map(e=>[e.type,e.category,Math.round((Number(e.amount)||0)*100),e.date]).sort()})).concat(QT.map(q=>[q.id,q.totalAmount,q.extrasAmount])))"""
OLD=json.load(open(os.path.join(H.TESTS,'datos','entrega121_antiguos.json'),encoding='utf-8'))
o49,o59,q49,q59=OLD['ids'];M=OLD['M'];MQ={q['id']:q for q in OLD['quotes']}
data=copy.deepcopy(D0);v1=[v for v in data['vehicles'] if v['id']=='v1'][0]
v1['bookings']+=copy.deepcopy(OLD['bookings']);v1['finances']+=copy.deepcopy(OLD['finances']);data['quotes']+=copy.deepcopy(OLD['quotes'])
with sync_playwright() as p:
    b=H.launch(p)
    ctx,pg=mkpage(b,HTML,data,'app')
    for k,n in ((o49,'Domicilio 49'),(o59,'Aeropuerto 59')):
        x=bk(pg,k)
        ok(f'Antiguo {n}: al cargarlo, mismo total del alquiler y mismos extras que cuando se guardó',x['tot']==M[k]['tot'] and x['b']['extras']==M[k]['b']['extras'],(x['tot'],M[k]['tot']))
    f49,f59=ficha(pg,o49),ficha(pg,o59)
    fx=lambda n:('%.2f'%n).replace('.',',')
    ok('Antiguo Domicilio 49: la ficha suma los extras (silla 39 + entrega 49 = «Extras contrato +88,00 €»)','Extras contrato +88,00 €' in H.N(f49),f49[-400:])
    ok('Antiguo Aeropuerto 59: la ficha suma sus extras (entrega 59 + seguro de limpieza: +%s €)'%fx(M[o59]['tot']-100),'Extras contrato +%s €'%fx(M[o59]['tot']-100) in H.N(f59),f59[-400:])
    t=recibo(pg,o49);ok('Antiguo Domicilio 49: recibo con «Entrega a domicilio» 49,00 €',any('Entrega a domicilio' in l and '49,00' in l for l in t.split('\n')),[l for l in t.split('\n') if 'Entrega' in l])
    t=recibo(pg,o59);ok('Antiguo Aeropuerto 59: recibo con la entrega de 59,00 €',any('Entrega' in l and '59,00' in l for l in t.split('\n')),[l for l in t.split('\n') if 'Entrega' in l])
    t=qpdf(pg,q49);ok('Presupuesto antiguo Domicilio 49: PDF con la entrega 49,00 €',any('Entrega' in l and '49,00' in l for l in t.split('\n')),[l for l in t.split('\n') if 'Entrega' in l])
    t=qpdf(pg,q59);ok('Presupuesto antiguo Aeropuerto 59: PDF con la entrega 59,00 €',any('Entrega' in l and '59,00' in l for l in t.split('\n')),[l for l in t.split('\n') if 'Entrega' in l])
    # Editar antiguos sin tocar nada
    s49=editar(pg,o49);ok('Editar antiguo Domicilio 49: Entrega marcada con «49» y sin fila Aeropuerto',s49['ent'] and s49['val']=='49' and s49['aer']=='no existe',s49)
    ok('Editar antiguo Domicilio 49 sin tocar: alquiler, finanzas y totales iguales que antes',strip(bk(pg,o49))==M[o49])
    s59=editar(pg,o59);ok('Editar antiguo Aeropuerto 59: fila «anterior» marcada, Entrega sin marcar',(not s59['ent']) and s59['aer']=='marcada',s59)
    ok('Editar antiguo Aeropuerto 59 sin tocar: alquiler, finanzas y totales iguales que antes',strip(bk(pg,o59))==M[o59])
    # Contratos de los antiguos
    st,t=contrato(pg,o49);ok('Contrato antiguo Domicilio 49: línea «Entrega a domicilio» 49,00 €',st['ent'] and st['val']=='49' and 'Entrega a domicilio: 49,00 €' in t,st)
    st,t=contrato(pg,o59);ok('Contrato antiguo Aeropuerto 59: línea «Entrega aeropuerto/hotel/estación» 59,00 €',st['aer'] and 'Entrega aeropuerto/hotel/estación: 59,00 €' in t,st)
    ok('Contratos antiguos: finanzas y totales siguen iguales',strip(bk(pg,o49))['tot']==M[o49]['tot'] and strip(bk(pg,o59))['tot']==M[o59]['tot'])
    # Presupuestos antiguos: editar y guardar sin tocar
    qa,st=presu(pg,[],qid=q49);ok('Editar presupuesto antiguo Domicilio 49: importe «49», mismos extras y total',st['val']=='49' and qa['extras']==MQ[q49]['extras'] and qa['totalAmount']==MQ[q49]['totalAmount'],(st,qa['extras']))
    qa,st=presu(pg,[],qid=q59);ok('Editar presupuesto antiguo Aeropuerto 59: fila anterior, mismos extras y total',st['aer'] and qa['extras']==MQ[q59]['extras'] and qa['totalAmount']==MQ[q59]['totalAmount'],(st,qa['extras']))
    # Altas nuevas
    J(pg,"try{closeSheet()}catch(e){};openV('v1');openNewRental()");W(pg,500);step1(pg,130);J(pg,"_rwGo(2)")
    ok('Alta: sin fila Aeropuerto, una sola Entrega con teclado decimal',J(pg,"!document.getElementById('row_ex_exEntregaAeropuerto')&&document.querySelectorAll('#row_ex_exEntregaDomicilio').length===1&&document.getElementById('exEntregaImp').getAttribute('inputmode')==='decimal'"))
    n50,tot=alta(pg,60,['exEntregaDomicilio'])
    x=bk(pg,n50);e=[e for e in x['b']['extras'] if e['id']=='exEntregaDomicilio']
    ok('Alta marcando sin importe → 50 €',[i['amount'] for i in e]==[50] and e[0]['label']=='Entrega a domicilio / lugar acordado' and tot.startswith('50,00'),(e,tot))
    ok('Alta 50 €: finanzas del coche y total del alquiler',any(f['x'] and f['a']==50 and f['c']=='Entrega a domicilio / lugar acordado' for f in x['vf']) and x['tot']==150,x['tot'])
    # importe 35,5: se escribe sin marcar la fila (se marca sola)
    J(pg,"try{closeSheet()}catch(e){};openV('v1');openNewRental()");W(pg,500)
    n35,tot=alta(pg,70,[],'35,5')
    x=bk(pg,n35);e=[e for e in x['b']['extras'] if e['id']=='exEntregaDomicilio']
    ok('Alta con importe 35,5 (se marca sola) → 35,5 €',[i['amount'] for i in e]==[35.5] and tot.startswith('35,50') and x['tot']==135.5,(e,tot,x['tot']))
    if SHOTS:
        ctxS,pgS=mkpage(b,HTML,data,'capturas')
        q,_=presu(pgS,[],'35,5',s=140,shot=SHOTS+'/presupuesto-entrega-oscuro.png')
        ctxS.close();ctxS,pgS=mkpage(b,HTML,data,'capturas');pg0=pg;pg=pgS
        J(pg,"try{closeSheet()}catch(e){};openV('v1');openNewRental()");W(pg,500);step1(pg,130)
        J(pg,"_rwGo(2)");W(pg);pg.locator('#row_ex_exEntregaDomicilio').click();pg.locator('#exEntregaImp').fill('35,5');W(pg,150)
        J(pg,"document.activeElement.blur()");pg.locator('#row_ex_exEntregaDomicilio').scroll_into_view_if_needed();J(pg,"document.getElementById('SC').scrollTop+=-60");W(pg,300)
        pg.screenshot(path=SHOTS+'/alta-entrega-oscuro.png');ctxS.close();pg=pg0
    # importe 0 → 50; marcar y desmarcar → no cuenta
    J(pg,"try{closeSheet()}catch(e){};openV('v1');openNewRental()");W(pg,500);step1(pg,130);J(pg,"_rwGo(2)");W(pg)
    pg.locator('#exEntregaImp').fill('0');W(pg,100);z=J(pg,"_calcExtrasTotal(3,false).items.exEntregaDomicilio?.amt")
    pg.locator('#row_ex_exEntregaDomicilio').click();W(pg,100);z2=J(pg,"_calcExtrasTotal(3,false).items.exEntregaDomicilio")
    ok('Importe 0 → 50 € y desmarcar la quita',z==50 and z2 is None,(z,z2))
    # Edición del nuevo: muestra «35,5»; cambiar a 60
    s=editar(pg,n35);ok('Editar alta 35,5: Entrega marcada con «35,5»',s['ent'] and s['val']=='35,5' and s['inp']=='decimal',s)
    ok('Editar alta 35,5 sin tocar: igual',strip(bk(pg,n35))==strip(x))
    editar(pg,n35,amt='60');y=bk(pg,n35)
    ok('Editar a 60 €: extra, finanzas y total cambian a 60',[i['amount'] for i in y['b']['extras'] if i['id']=='exEntregaDomicilio']==[60] and y['tot']==160 and any(f['x'] and f['a']==60 for f in y['vf']) and not any(f['x'] and f['a']==35.5 for f in y['vf']),y['tot'])
    editar(pg,o59,untick='exEntregaAeropuerto');z=bk(pg,o59)
    ok('Antiguo Aeropuerto: si Rafael lo desmarca, sale (y la fila desaparece al volver a editar)',not any(i['id']=='exEntregaAeropuerto' for i in z['b']['extras']) and editar(pg,o59)['aer']=='no existe')
    # Contrato y recibo del nuevo
    st,t=contrato(pg,n35);ok('Contrato alta (60 €): Entrega marcada con «60» y línea «Entrega a domicilio / lugar acordado: 60,00 €»',st['ent'] and st['val']=='60' and 'Entrega a domicilio / lugar acordado: 60,00 €' in t,(st,[l for l in t.split('\n') if 'Entrega' in l]))
    ok('Contrato alta: total del alquiler sigue 160',bk(pg,n35)['tot']==160)
    t=recibo(pg,n50);ok('Recibo alta 50 €: línea de la Entrega',any('Entrega a domicilio / lugar acordado' in l and '50,00' in l for l in t.split('\n')),[l for l in t.split('\n') if 'Entrega' in l])
    # Presupuestos nuevos
    J(pg,"try{closeSheet()}catch(e){};openNewQuote()");W(pg,400);J(pg,"_qwGo(2)")
    ok('Presupuesto: sin fila Aeropuerto y campo decimal',J(pg,"!document.querySelector('[data-qexid=\"exEntregaAeropuerto\"]')&&document.getElementById('qamt_exEntregaDomicilio').getAttribute('inputmode')==='decimal'"))
    qn,_=presu(pg,['exEntregaDomicilio'],s=110);e=[i for i in qn['extras'] if i['id']=='exEntregaDomicilio']
    ok('Presupuesto marcando sin importe → 50 €',[i['amount'] for i in e]==[50] and qn['extrasAmount']==50,e)
    q35,st=presu(pg,[],'35,5',s=120);e=[i for i in q35['extras'] if i['id']=='exEntregaDomicilio']
    ok('Presupuesto importe 35,5 (se marca solo) → 35,5 € y total = base + 35,5',[i['amount'] for i in e]==[35.5] and abs(q35['totalAmount']-(q35['baseAmount']+35.5))<0.001,(e,q35['totalAmount'],q35['baseAmount']))
    t=qpdf(pg,q35['id']);ok('PDF del presupuesto: «+ Entrega a domicilio / lugar acordado 35,50 €»',any('Entrega a domicilio / lugar acordado' in l and '35,50' in l for l in t.split('\n')),[l for l in t.split('\n') if 'Entrega' in l])
    qe,st=presu(pg,[],qid=q35['id']);ok('Editar presupuesto 35,5: muestra «35,5» y no cambia',st['val']=='35,5' and qe['extras']==q35['extras'] and qe['totalAmount']==q35['totalAmount'],st)
    J(pg,"id=>convertQuoteToBooking(id)",q35['id']);W(pg,800)
    cb=J(pg,"id=>{const q=QT.find(q=>q.id===id);for(const v of V){const b=(v.bookings||[]).find(x=>x.id===q.bookingId);if(b)return {ex:b.extras,tot:_bookingClientTotal(b)};}return null}",q35['id'])
    ok('Convertir presupuesto 35,5 en alquiler: extra 35,5 con la misma etiqueta',cb and any(i['id']=='exEntregaDomicilio' and i['amount']==35.5 and i['label']=='Entrega a domicilio / lugar acordado' for i in cb['ex']),cb)
    ctx.close()
    b.close()
H.fin()
