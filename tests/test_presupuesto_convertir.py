# Presupuestos · «Convertir en alquiler» (Rafael, 26/11/2026): el botón sale mientras NO exista de verdad el alquiler creado desde el
# presupuesto, sea cual sea su estado («Aceptado» = 'convertido' elegido a mano, el 'aceptado' antiguo, pendiente o rechazado).
# El alquiler es el de q.bookingId si sigue existiendo (cancelado también cuenta; borrado → se puede volver a convertir) o, en los
# antiguos sin bookingId, el del mismo coche y misma fecha de inicio con la nota «Generado desde presupuesto <número>».
# No se puede convertir dos veces; editar el presupuesto conserva bookingId (antes se perdía) y no choca con su propio alquiler.
# Sin campos nuevos. Uso: python3 tests/test_presupuesto_convertir.py
import sys,os,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
chk=H.chk;d=H.d
def qt(i,st,veh,start,end,**k):
    q={'id':i,'num':'PRE-2026-%s'%i.upper(),'vehicleId':veh,'clientName':'Cliente '+i.upper(),'clientId':'cx','createdAt':d(-3)+'T10:00:00',
       'startDate':start,'startTime':'10:00','endDate':end,'endTime':'10:00','dur':2,'baseAmount':60,'extras':[],'discount':0,'fianza':200,'status':st,'totalAmount':60,'notes':''}
    q.update(k);return q
def datos():
    D=H.datos()
    D['clients'].append({'id':'cx','name':'Cliente CX','dni':'00000077T','phone':'600 000 077','email':'','notes':'','rating':0,'birthdate':'1980-01-01','bookingIds':[]})
    v1=[v for v in D['vehicles'] if v['id']=='v1'][0];v5=[v for v in D['vehicles'] if v['id']=='v5'][0]
    v1['bookings']+=[H._bk(91,-30,-27,'Cliente CE',100,notes='Generado desde presupuesto PRE-2026-CE · Descuento 5,00 €',returned=True,delivered=True),
                     H._bk(93,30,33,'Cliente CJ',90,notes='Generado desde presupuesto PRE-2026-CJ'),
                     H._bk(92,40,42,'Cliente CH',60,cancelled=True,notes='Generado desde presupuesto PRE-2026-CH')]
    D['quotes']+=[qt('ca','convertido','v1',d(2),d(4)),                         # «Aceptado» a mano, sin alquiler
                  qt('cb','aceptado','v5',d(20),d(22)),                         # 'aceptado' antiguo, sin alquiler
                  qt('cc','convertido','v4',d(-5),d(3),bookingId='b4'),         # convertido de verdad
                  qt('cd','convertido','v4',d(50),d(52),bookingId='bzz'),       # su alquiler se borró
                  qt('ce','convertido','v1',d(-30),d(-27)),                     # antiguo editado tras convertir (sin bookingId), alquiler devuelto
                  qt('cf','pendiente','v4',d(8),d(10),bookingId='b4'),          # convertido y vuelto a «Pendiente» a mano
                  qt('cg','rechazado','v1',d(-30),d(-27),num='PRE-2026-C'),     # número que es el principio de otro: no se confunde
                  qt('ch','convertido','v1',d(40),d(42),bookingId='b92'),       # su alquiler está cancelado: cuenta como convertido
                  qt('ci','convertido','v1',d(31),d(33),num='PRE-2026-CJ'),     # mismo número que la nota de b93 pero otra fecha de inicio
                  qt('cj','convertido','v1',d(30),d(33))]                       # antiguo sin bookingId, alquiler futuro (b93)
    return D
MAIN="users/demo/data/main"
NW="window.__FSOPS.filter(p=>p==='%s').length"%MAIN
CLOUD="JSON.parse(JSON.stringify(window.__FS['%s']))"%MAIN
NB="V.reduce((s,v)=>s+(v.bookings||[]).length,0)"
def Q(i):return "QT.find(q=>q.id==='%s')"%i
with H.playwright() as p:
    br=H.launch(p)
    D=datos()
    ctx,pg=H.open_app(br,data=D,extra="window.alert=m=>{(window.__AL=window.__AL||[]).push(String(m))};window.confirm=()=>true;",wait=2500)
    J=lambda js,a=None:pg.evaluate(js,a);W=lambda ms=400:pg.wait_for_timeout(ms)
    def ficha(i):
        J("closeSheet();nav('quotes');_quoteEditId='%s';showQuoteDetail(document.getElementById('PC'))"%i);W(300)
        return J("[...document.querySelectorAll('#PC .qt-acts button')].map(b=>b.textContent.trim())"),J("document.getElementById('PC').innerText")
    def conv(i):
        b,t=ficha(i);return any('Convertir en alquiler' in x for x in b) and 'Ya convertido en alquiler' not in t
    def ya(i):
        b,t=ficha(i);return not any('Convertir en alquiler' in x for x in b) and 'Ya convertido en alquiler' in t
    print('── 1. Qué presupuestos ofrecen «Convertir en alquiler» ──')
    chk(J(NW)==0,'Abrir la app no escribe nada (no hay pendientes vencidos)',J(NW))
    chk(conv('ca'),"«Aceptado» elegido a mano ('convertido' sin alquiler): sale «Convertir en alquiler»")
    chk(J("document.querySelector('#PC .qt-c .d-ch .chip').textContent")=='Aceptado','…y su chip sigue diciendo «Aceptado»')
    h=J("(()=>{const b=[...document.querySelectorAll('#PC .qt-acts button')].find(x=>x.textContent.includes('Convertir en alquiler'));return b&&b.offsetHeight})()")
    chk(h and h>=44,'Botón «Convertir en alquiler» de al menos 44 px',h)
    chk(conv('cb'),"'aceptado' antiguo sin alquiler: sale «Convertir en alquiler»")
    chk(ya('cc'),'Convertido de verdad (su alquiler existe): «Ya convertido en alquiler», sin botón')
    chk(conv('cd'),'Convertido cuyo alquiler se borró: se puede volver a convertir')
    chk(ya('ce'),'Antiguo sin bookingId (editado tras convertir): reconoce su alquiler por la nota, el coche y la fecha → «Ya convertido»')
    chk(ya('cf'),'Convertido y vuelto a «Pendiente» a mano: «Ya convertido» (antes dejaba crear un segundo alquiler)')
    chk(conv('cg'),'Número que es el principio de otro (PRE-2026-C ≠ PRE-2026-CE): no se confunde, sale «Convertir»')
    chk(ya('ch'),'Su alquiler está cancelado: cuenta como convertido')
    chk(conv('ci'),'Misma nota pero otra fecha de inicio: no se toma por convertido')
    chk(conv('q1') and conv('q3'),'Pendiente y rechazado de los datos de siempre: «Convertir» como siempre')
    print('── 2. Convertir un «Aceptado» y no poder convertirlo dos veces ──')
    n0=J(NB);w0=J(NW);fz0=J("V.find(v=>v.id==='v1').finances.length")
    ficha('ca');pg.locator('#PC .qt-acts button:has-text("Convertir en alquiler")').click();W(1200)
    bid=J(Q('ca')+".bookingId")
    chk(J(NB)==n0+1 and bid and J("V.find(v=>v.id==='v1').bookings.some(b=>b.id==='%s')"%bid),'Tocar «Convertir en alquiler» crea UN alquiler en el coche',[J(NB)-n0,bid])
    chk(J(Q('ca')+".status")=='convertido' and J(NW)==w0+1,"Queda 'convertido' («Aceptado») con su bookingId y se guarda en la nube",J(NW)-w0)
    fz1=J("V.find(v=>v.id==='v1').finances.length")
    chk(ya('ca'),'Su ficha ya dice «Ya convertido en alquiler»')
    J("window.__AL=[]");J("convertQuoteToBooking('ca')");W(300)
    chk(J(NB)==n0+1 and J("V.find(v=>v.id==='v1').finances.length")==fz1,'Llamarlo otra vez (doble toque, botón viejo): no crea otro alquiler ni otros ingresos',[J(NB)-n0])
    chk(any('ya está convertido' in a for a in J("window.__AL")),'…y avisa de que ya está convertido',J("window.__AL"))
    for i in ['cc','ce','cf','ch']:
        J("window.__AL=[]");J("convertQuoteToBooking('%s')"%i);W(150)
    chk(J(NB)==n0+1 and J("window.__AL.length")==1,'Tampoco se pueden convertir otra vez cc, ce, cf ni ch (su alquiler existe)',J(NB)-n0)
    print('── 3. Editar conserva el enlace con el alquiler ──')
    w0=J(NW);J("window.__AL=[]")
    J("openEditQuote('ca')");W(700);J("_saveQuote()");W(1200)
    chk(J(Q('ca')+".bookingId")==bid,'Editar un convertido y guardar: conserva su bookingId (antes se perdía)',J(Q('ca')+".bookingId"))
    chk(not J("window.__AL.length") and J(NW)==w0+1,'Sin aviso de conflicto con su propio alquiler; se guarda',J("window.__AL"))
    cl=J(CLOUD);qc=[q for q in cl['quotes'] if q['id']=='ca'][0]
    chk(qc.get('bookingId')==bid and qc['status']=='convertido','En la nube: el presupuesto editado sigue con su bookingId',qc.get('bookingId'))
    chk(ya('ca'),'Tras editar: sigue «Ya convertido en alquiler» (no vuelve a ofrecer «Convertir»)')
    J("window.__AL=[]");J("openEditQuote('cj')");W(700);J("_saveQuote()");W(1000)
    chk(not J("window.__AL.length") and J(Q('cj')+".bookingId")=='b93','Antiguo sin bookingId con su alquiler futuro: editar no choca con él y lo enlaza (bookingId = b93)',[J("window.__AL"),J(Q('cj')+".bookingId")])
    J("openEditQuote('ce')");W(700);J("_saveQuote()");W(1000)
    chk(J(Q('ce')+".bookingId")=='b91' and ya('ce'),'Antiguo editado otra vez: queda enlazado a su alquiler (b91)',J(Q('ce')+".bookingId"))
    J("openEditQuote('cb')");W(700);J("_saveQuote()");W(1000)
    chk('bookingId' not in J(Q('cb')) and conv('cb'),'Editar uno sin alquiler no le inventa enlace: sigue «Convertir»')
    print('── 4. Sin campos nuevos ──')
    cl=J(CLOUD);orig={q['id']:set(q.keys()) for q in D['quotes']}
    nuevos={q['id']:sorted(set(q.keys())-orig.get(q['id'],set())-{'bookingId'}) for q in cl['quotes'] if q['id'] in orig}
    ext=sorted(set().union(*[set(q.keys()) for q in cl['quotes']])-set().union(*orig.values())-{'kmIncTotal','customRate','basePriceBreakdown','extrasAmount','dailyRate'})
    chk(not ext,'Presupuestos en la nube: ningún campo que no existiera ya (solo bookingId, que ya existía)',ext)
    b=[x for v in cl['vehicles'] for x in v['bookings'] if x['id']==bid][0]
    chk('quoteId' not in b and b['notes'].startswith('Generado desde presupuesto PRE-2026-CA'),'El alquiler creado es el de siempre (nota «Generado desde presupuesto …», sin campos nuevos)',b.get('notes'))
    print('── 5. Borrar el alquiler deja convertir otra vez; el antiguo «Aceptado» se convierte ──')
    J("closeSheet();AV='v1';CV='vehicles';renderDetail(document.getElementById('PC'))");W(300)
    J("deleteBooking('%s')"%bid);W(1200)
    chk(not J("V.some(v=>(v.bookings||[]).some(b=>b.id==='%s'))"%bid) and conv('ca'),'Borrado su alquiler: «Convertir en alquiler» vuelve a salir')
    n0=J(NB);ficha('ca');pg.locator('#PC .qt-acts button:has-text("Convertir en alquiler")').click();W(1200)
    chk(J(NB)==n0+1 and J(Q('ca')+".bookingId")!=bid,'Se vuelve a convertir: un alquiler nuevo y bookingId nuevo')
    n0=J(NB);ficha('cb');pg.locator('#PC .qt-acts button:has-text("Convertir en alquiler")').click();W(1200)
    chk(J(NB)==n0+1 and J(Q('cb')+".status")=='convertido' and J(Q('cb')+".bookingId"),"'aceptado' antiguo: se convierte (queda 'convertido' con bookingId)")
    ctx.close()
    print('── 6. Al volver a abrir (datos de la nube) ──')
    ctx,pg=H.open_app(br,data=cl,wait=2500,theme='light');J=lambda js,a=None:pg.evaluate(js,a);W=lambda ms=400:pg.wait_for_timeout(ms)
    chk(ya('ca') and ya('cj') and ya('cc') and conv('cd') and J(NW)==0,'Tras recargar: cada uno igual que antes, sin escrituras (tema claro)')
    ctx.close()
    H.fin()
