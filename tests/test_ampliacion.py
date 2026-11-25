# Hoja «Ampliar alquiler» (#153): «+N días» (horas de reloj, mismo criterio que calcRentalPrice), Precio/día y Diferencia
# enlazados (manda la última escrita; la otra se calcula), cambio de fechas, total del alquiler, casos límite (sin fecha,
# fecha anterior, negativo, texto, plataformas, sin coste) y que lo guardado y el anexo son los de siempre: lo mismo que
# escribir el nuevo total a mano con la hoja de antes (valores fijos comprobados con main ee5d91d).
# Uso: python3 tests/test_ampliacion.py   (DEIROS_CAPTURAS=<carpeta> guarda 2 capturas de la hoja)
import sys,os,json,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
chk=H.chk;N=H.N
D=H.datos()
# b3 (Renault 2222CCC, Sin app): 414,99 € del 19/10 21:00 al 07/12 20:00 (48 d 23 h → 49 días cobrados) → sugerido 8,47 €/día
# Alquiler sin hora de fin (criterio daysBetween) y uno de Amovens ya en los datos (b1)
v4=[v for v in D['vehicles'] if v['id']=='v4'][0]
v4['bookings'].append({'id':'bNT','startDate':H.d(-2),'startTime':'','endDate':H.d(8),'endTime':'','platform':'sinapp','amount':300,'clientName':'Cliente Sin Hora','finance':[],'extras':[]})
FIN=H.d(17)          # fin actual de b3: 2026-12-07
def fd(n):return H.d(17+n)
SNAP=r"""(id=>{const v=V.find(v=>(v.bookings||[]).some(b=>b.id===id));const b=v.bookings.find(b=>b.id===id);
  const amp=(b.finance||[]).filter(f=>f.type==='income'&&String(f.concept||'').startsWith('Ampliaci')).map(f=>({concept:f.concept,amount:f.amount,date:f.date,notes:f.notes}));
  const ext=(v.finances||[]).filter(f=>f.bookingId===id&&f._extension).map(f=>[f.date,Math.round(f.amount*100)/100]);
  return {endDate:b.endDate,endTime:b.endTime,amount:b.amount,amp,ext,extSum:Math.round(ext.reduce((s,x)=>s+x[1],0)*100)/100,nIds:(b.financeIds||[]).length,
    total:Math.round(_bookingClientTotal(b)*100)/100,last:window._extLastData};})"""
with H.playwright() as p:
    br=H.launch(p)
    ctx,pg=H.open_app(br,data=D,extra="window.alert=m=>{(window.__AL=window.__AL||[]).push(String(m))};window.confirm=()=>true;")
    J=lambda js,a=None:pg.evaluate(js,a);W=lambda ms=150:pg.wait_for_timeout(ms)
    J(H.PDFTEXT)
    T=lambda sel:N(J("s=>{const e=document.querySelector(s);return e?[...e.childNodes].map(n=>n.textContent).join(' ').replace(/\\s+/g,' ').trim():null}",sel))
    val=lambda i:J("i=>document.getElementById(i).value",i)
    calc=lambda i:J("i=>document.getElementById(i).classList.contains('ex-calc')",i)
    dis=lambda:J("document.getElementById('extOk').disabled")
    def setv(i,v):pg.fill('#'+i,v);W()
    def open_(bid,vid):
        J("([v,b])=>{try{closeSheet()}catch(e){};openV(v);openExtendBooking(b)}",[vid,bid]);W(500)
    # ── Al abrir ──
    open_('b3','v3')
    chk(J("!!document.getElementById('extPd')&&!!document.getElementById('extDiff')&&document.getElementById('extNewTotal').type==='hidden'"),'Hoja: casillas Precio/día y Diferencia; el total que se guarda va oculto')
    chk(J("['extPd','extDiff'].every(i=>{const e=document.getElementById(i);return e.type==='text'&&e.getAttribute('inputmode')==='decimal'})"),'Precio/día y Diferencia: teclado decimal (type=text, admiten coma)')
    chk(T('label[for=extPd]')=='Precio/día' and T('label[for=extDiff]')=='Diferencia a pagar','Rótulos «Precio/día» y «Diferencia a pagar»')
    chk(val('extPd')=='8,47','Sugerido: precio/día del propio alquiler (414,99 € ÷ 49 días = 8,47)',val('extPd'))
    chk(val('extDiff')=='' and calc('extDiff') and not calc('extPd'),'Al abrir: diferencia vacía y marcada como calculada')
    chk(T('#extDays')=='+0 días Elige una fecha posterior al 07/12/2026' and J("document.getElementById('extDays').classList.contains('off')"),'Al abrir (misma fecha): «+0 días», aviso neutro',T('#extDays'))
    chk(dis(),'Al abrir (misma fecha): «Confirmar ampliación» desactivado')
    chk(N(T('#extCalcBox'))=='Total del alquiler 414,99 €','Al abrir: «Total del alquiler 414,99 €»',T('#extCalcBox'))
    chk('Introduce el nuevo total' not in J("document.getElementById('SC').textContent") and 'Nuevo importe total' not in J("document.getElementById('SC').textContent"),'Ya no está «Nuevo importe total» ni «Introduce el nuevo total…»')
    # ── Días ──
    setv('extNewEnd',fd(3))
    chk(T('#extDays')=='+3 días Hasta el 10/12/2026 a las 20:00','+3 días (misma hora)',T('#extDays'))
    chk(not dis(),'Con fecha posterior: botón activo')
    chk(val('extDiff')=='25,41' and calc('extDiff'),'Precio/día sugerido × 3 = 25,41 en Diferencia (calculada)',val('extDiff'))
    chk(T('#extLink')=='',"Sin explicación del cálculo (Rafael: lo más limpio posible)",T('#extLink'))
    setv('extNewEnd',fd(1));chk(T('#extDays').startswith('+1 día Hasta'),'+1 día (singular)',T('#extDays'))
    setv('extNewEnd',fd(3))
    # ── Precio/día → diferencia ──
    setv('extPd','50')
    chk(val('extDiff')=='150,00' and calc('extDiff') and not calc('extPd'),'Precio/día 50 → Diferencia 150,00 (3 días)',val('extDiff'))
    chk(N(T('#extCalcBox'))=='Total del alquiler 564,99 €','Total del alquiler 564,99 €, sin desglose',T('#extCalcBox'))
    chk(val('extNewTotal')=='564.99','Nuevo total que se guardará = total actual + diferencia (564.99)',val('extNewTotal'))
    setv('extPd','33,5');chk(val('extDiff')=='100,50','Precio/día con coma (33,5) → 100,50',val('extDiff'))
    # ── Diferencia → precio/día ──
    setv('extDiff','100')
    chk(val('extPd')=='33,33' and calc('extPd') and not calc('extDiff'),'Diferencia 100 → Precio/día 33,33 (calculado)',val('extPd'))
    chk(T('#extLink')=='',"Sin explicación del cálculo",T('#extLink'))
    setv('extDiff','1.234,50');chk(val('extPd')=='411,50' and val('extNewTotal')=='1649.49','Diferencia «1.234,50» (miles y coma) → 411,50 €/día; total 1649.49',(val('extPd'),val('extNewTotal')))
    setv('extDiff','100')
    # ── Cambio de fechas: manda la última editada ──
    setv('extNewEnd',fd(5))
    chk(val('extDiff')=='100' and val('extPd')=='20,00','Última editada = Diferencia: al cambiar a +5 días se recalcula el precio/día (20,00)',(val('extDiff'),val('extPd')))
    setv('extPd','20')
    setv('extNewEnd',fd(4))
    chk(val('extPd')=='20' and val('extDiff')=='80,00','Última editada = Precio/día: al cambiar a +4 días se recalcula la diferencia (80,00)',(val('extPd'),val('extDiff')))
    # ── Horas sueltas (mismo criterio que calcRentalPrice) ──
    setv('extNewTime','23:00')
    chk(T('#extDays').startswith('+4 días y 3 h Hasta el ') and 'se cobran' not in T('#extDays'),'+4 días y 3 h (menos de 6 h: proporcional)',T('#extDays'))
    chk(val('extDiff')=='90,00','4 días × 20 + 3 h × 20/6 = 90,00 (= calcRentalPrice)',val('extDiff'))
    chk(J("String(calcRentalPrice(%s,'20:00',%s,'23:00',20).total)"%(json.dumps(FIN),json.dumps(fd(4))))=='90','calcRentalPrice da lo mismo (90)')
    setv('extDiff','90');chk(val('extPd')=='20,00','Diferencia 90 con 4 d y 3 h → 20,00 €/día (inversa coherente)',val('extPd'))
    setv('extNewTime','04:00')
    chk(T('#extDays').startswith('+3 días y 8 h Hasta el ') and 'cobran' not in T('#extDays'),'Fin a las 04:00 (de 20:00): +3 días y 8 h → se cobran 4 días',T('#extDays'))
    setv('extPd','20');chk(val('extDiff')=='80,00','4 días cobrados × 20 = 80,00 (= calcRentalPrice)',val('extDiff'))
    chk(J("String(calcRentalPrice(%s,'20:00',%s,'04:00',20).total)"%(json.dumps(FIN),json.dumps(fd(4))))=='80','calcRentalPrice da lo mismo (80)')
    setv('extNewTime','20:00')
    # ── Casos límite ──
    setv('extDiff','-10')
    chk(dis() and 'positivo' in T('#extCalcBox') and val('extNewTotal')=='' and val('extPd')=='','Diferencia negativa: aviso, botón desactivado y nada que guardar',T('#extCalcBox'))
    J("_confirmExtend()");W()
    chk(J("V.find(v=>v.id==='v3').bookings.find(b=>b.id==='b3').endDate")==FIN and 'positivo' in (J("(window.__AL||[]).slice(-1)[0]") or ''),'Confirmar con negativo (forzado): no guarda y avisa')
    setv('extDiff','abc');chk(dis() and 'positivo' in T('#extCalcBox'),'Diferencia con texto: aviso y botón desactivado')
    setv('extDiff','150');chk(not dis(),'Diferencia válida: botón activo otra vez')
    setv('extNewEnd',H.d(15))
    chk(dis() and J("document.getElementById('extDays').classList.contains('err')") and 'posterior' in T('#extCalcBox'),'Fecha anterior al fin actual: aviso en rojo y botón desactivado',T('#extDays'))
    chk('Total del alquiler 414,99 €' in N(T('#extCalcBox')),'Fecha anterior: el total no suma nada')
    if H.CAPTURAS:
        setv('extNewEnd',fd(3));setv('extPd','50');J("document.getElementById('SC').scrollTop=0");W(300)
        pg.screenshot(path=os.path.join(H.CAPTURAS,'a153-1-precio-dia.png'))
        J("document.getElementById('SC').scrollTop=99999");W(300)
        pg.screenshot(path=os.path.join(H.CAPTURAS,'a153-2-total.png'))
    # ── Guardar: igual que escribir el total a mano en la hoja de antes ──
    setv('extNewEnd',fd(3));setv('extNewTime','20:00');setv('extDiff','150')
    J("_confirmExtend()");W(500)
    s=J(SNAP,'b3')
    EXP={'endDate':fd(3),'endTime':'20:00','amount':414.99,'amp':[{'concept':'Ampliación alquiler ('+FIN+' → '+fd(3)+')','amount':150,'date':'2026-11-20','notes':'Total anterior: 414.99€ · Nuevo total: 564.99€'}],
         'ext':[[fd(1),150]],'extSum':150,'total':564.99}
    chk(all(s[k]==EXP[k] for k in EXP),'Guardado = lo que guarda la hoja de antes escribiendo 564,99: fin, hora, «Ampliación alquiler (…)» 150, notas y prorrateo',{k:s[k] for k in EXP})
    chk(s['last']['extraPrice']==150 and s['last']['newTotal']==564.99 and s['last']['curTotal']==414.99,'Datos del anexo (_extLastData): 414,99 + 150 = 564,99',s['last'])
    chk(N(J("(window.__AL||[]).slice(-1)[0]"))=='Alquiler ampliado hasta '+fd(3)+'.\n+150,00 € adicionales (nuevo total: 564,99 €)','Aviso al confirmar igual que antes',J("(window.__AL||[]).slice(-1)[0]"))
    chk(J("JSON.stringify(Object.keys(V.find(v=>v.id==='v3').bookings.find(b=>b.id==='b3')).sort())")==J("JSON.stringify(Object.keys(%s).sort())"%json.dumps([b for b in D['vehicles'][2]['bookings'] if b['id']=='b3'][0]|{'financeIds':0,'financeId':0})),'Sin campos nuevos en el alquiler')
    # ── Anexo (PDF) y Enviar anexo ──
    t=N(' '.join(J("__pdfText(()=>generateExtensionPDF('b3'),true)")))
    chk('ERROR' not in t and '3 días adicionales' in t and '564,99 €' in t and '150,00 €' in t and '414,99 €' in t,'Anexo: 3 días adicionales, 414,99 € → 564,99 € y ampliación 150,00 €',t[:300])
    chk('quedando el importe total del alquiler en 564,99 €' in t,'Anexo: cláusula con el nuevo total (texto legal sin cambios)')
    # ── Segunda ampliación: el sugerido incluye la anterior ──
    open_('b3','v3')
    chk(val('extPd')=='10,87','Segunda ampliación: sugerido = (414,99 + 150 de la anterior) ÷ 52 días = 10,87',val('extPd'))
    # ── Sin coste: vaciar el precio/día (como dejar el total vacío antes) ──
    setv('extNewEnd',fd(4));setv('extPd','')
    chk(val('extDiff')=='' and val('extNewTotal')=='' and not dis() and 'Sin coste' not in T('#extCalcBox'),'Precio/día vacío: sin coste adicional y botón activo',T('#extCalcBox'))
    J("_confirmExtend()");W(400);s2=J(SNAP,'b3')
    chk(s2['endDate']==fd(4) and len(s2['amp'])==1 and s2['total']==564.99,'Ampliación sin coste: solo cambia la fecha (como con el total vacío)',s2)
    # ── Plataforma (Amovens): sin sugerido, se escribe lo que paga la plataforma ──
    open_('b1','v1')
    chk(val('extPd')=='' and 'paga la plataforma' not in T('#SC') and 'Sugerido' not in T('#SC'),'Amovens: precio/día vacío y sin pistas')
    setv('extNewEnd',H.d(11));setv('extDiff','45')
    chk(T('#extDays')=='+2 días Hasta el 01/12/2026 a las 19:00' and val('extPd')=='22,50' and N(T('#extCalcBox'))=='Total del alquiler 165,00 €','Amovens: +2 días, 45 € → 22,50 €/día, total 165,00 €',(T('#extDays'),T('#extCalcBox')))
    J("_confirmExtend()");W(400);s3=J(SNAP,'b1')
    chk(s3['amp'] and s3['amp'][0]['amount']==45 and s3['extSum']==45,'Amovens: se guarda igual (Ampliación 45 € prorrateada)',s3)
    # ── Alquiler sin horas: días con daysBetween ──
    open_('bNT','v4')
    chk(val('extPd')=='30,00','Sin horas: sugerido 300 € ÷ 10 días = 30,00',val('extPd'))
    setv('extNewTime','09:00');setv('extNewEnd',H.d(10))
    chk(T('#extDays')=='+2 días Hasta el 30/11/2026' and val('extDiff')=='60,00','Sin hora de fin original: +2 días por fechas (daysBetween), 60,00',(T('#extDays'),val('extDiff')))
    # ── Ficha del alquiler: botones del anexo como siempre ──
    J("closeSheet();showBookingById('b3')");W(500)
    chk(J("[...document.querySelectorAll('#SC button')].some(b=>/Anexo de ampliación/.test(b.textContent))&&[...document.querySelectorAll('#SC button')].some(b=>/Enviar anexo/.test(b.textContent))"),'Ficha: «Anexo de ampliación» y «Enviar anexo» siguen')
    # ── 390 px: nada se sale ──
    open_('b3','v3');setv('extNewEnd',fd(3));setv('extPd','50')
    o=J("(()=>{const sc=document.getElementById('SC');return [...sc.querySelectorAll('*')].filter(e=>{const r=e.getBoundingClientRect();return r.width&&(r.right>391||r.left<-1)}).map(e=>e.id||e.className).slice(0,5)})()")
    chk(not o,'A 390 px nada se sale de la hoja',o)
    h=J("['extPd','extDiff','extOk'].map(i=>Math.round(document.getElementById(i).getBoundingClientRect().height))")
    chk(min(h)>=44,'Casillas y botón de al menos 44 px',h)
    ctx.close();br.close()
H.fin()
