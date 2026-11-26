# Analítica · cifras correctas (bloque A): «Beneficio flota» (propios + comisión − déficit asumido) en la cabecera y en la Comparativa,
# que cuadra con Negocio salvo los ingresos y gastos generales; Comparativa y ocupación con los coches del filtro (desde el
# bloque B, en las cifras del período; la ocupación «Histórico» ya no está); amortización con una sola cifra (meses al ritmo de los últimos 6 meses) y solo de coches propios; sin «Proyección anual»;
# clientes sin anonimizados; informe PDF: plataformas = Ingresos, período «10/2026 a 11/2026», sin proyección ni break-even;
# «Informe PDF» de escritorio abre el selector de período. Datos inventados; fecha fija del arnés: 20/11/2026.
# Cuentas a mano (comisión 30 %; octubre con la regla antigua, noviembre con la de #90):
#   v1 propio (compra 6000 €): oct 300 − 100 = 200 · nov (400 + 20) − 50 = 370 · dic (reserva) 100 → beneficio 670 €
#       ritmo = (200 + 370) / 2 meses = 285 €/mes · falta 6000 − 670 = 5330 € → 5330 / 285 = 18,7 → ~19 meses
#   v2 en gestión (compra 15000 €, no debe salir en ROI): oct 500 × 30 % = 150 · nov (600 − 40 limpieza 5.3) × 30 % = 168
#       (la reparación de 200 € es 5.2: la paga el propietario y no se descuenta)
#   Beneficio flota: oct 300 + 150 − 100 = 350 · nov 420 + 168 − 50 = 538 · todo 670 + 318 = 988
#   Negocio = Beneficio flota + generales (nov: − 60 de gestoría) → nov 478 · todo 928
# Uso: python3 tests/test_analitica_cifras.py
import sys,os,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
chk=H.chk
SCEN=r"""(()=>{
 const mk=(id,s,e,cl,amt,pl,x)=>Object.assign({id,startDate:s,startTime:'10:00',endDate:e,endTime:'10:00',platform:pl,amount:amt,clientName:cl,finance:[],extras:[]},x||{});
 V=[{id:'v1',name:'Turismo Uno',plate:'0000AAA',model:'Uno',year:2020,vtype:'own',purchase_price:6000,vehicle_type:'turismo',color:'#8B5CF6',
     bookings:[mk('k1','2026-10-01','2026-10-11','Ana Prueba',300,'sinapp',{clientDni:'00000001R',returned:true,delivered:true}),
               mk('k2','2026-11-02','2026-11-12','Ana Prueba',400,'amovens',{clientDni:'00000001R',returned:true,delivered:true}),
               mk('k3','2026-12-10','2026-12-15','Bea Prueba',100,'sinapp')],
     finances:[{id:'f1',type:'expense',amount:100,date:'2026-10-10',category:'Mantenimiento'},{id:'f2',type:'expense',amount:50,date:'2026-11-05',category:'Combustible'},
               {id:'f3',type:'income',amount:20,date:'2026-11-15',category:'Venta accesorio'}]},
    {id:'v2',name:'Furgo Dos',plate:'1111BBB',model:'Dos',year:2020,vtype:'managed',ownerId:'o1',commission:30,purchase_price:15000,vehicle_type:'l1h1',color:'#14B8A6',
     bookings:[mk('m1','2026-10-05','2026-10-15','Cliente anonimizado',500,'getaround',{returned:true,delivered:true}),
               mk('m2','2026-11-03','2026-11-13','Cliente anonimizado',600,'sinapp',{returned:true,delivered:true})],
     finances:[{id:'g1',type:'expense',amount:40,date:'2026-11-08',category:'Limpieza'},{id:'g2',type:'expense',amount:200,date:'2026-11-09',category:'Reparación'}]}];
 V.forEach(v=>v.bookings.forEach(b=>{const fe=proRataEntries(b.startDate,b.endDate,b.amount,b.platform,'',b.id);fe.forEach(e=>v.finances.push(e));b.financeIds=fe.map(e=>e.id);b.financeId=fe[0]&&fe[0].id;}));
 BF=[{id:'n1',type:'expense',amount:60,date:'2026-11-02',category:'Gestoría'}];
 _analyticsOwnership='';_analyticsVtype='';_invalidateRsCache();window.alert=()=>{};return true;})()"""
CMP=r"""f=>{if(f!==undefined)_analyticsOwnership=f;nav('analytics');document.getElementById('cmpA').value='2026-10';document.getElementById('cmpB').value='2026-11';runComparison();
 const o={};document.querySelectorAll('#cmpResults .an-cmp>div:not(.h)').forEach(r=>{const c=r.children;o[c[0].textContent.trim()]=[c[1].textContent.trim(),c[2].textContent.trim()];});return o;}"""
N=lambda x:H.N(x) if isinstance(x,str) else [H.N(y) for y in x]
with H.playwright() as p:
    br=H.launch(p)
    ctx,pg=H.open_app(br)
    J=lambda js,a=None:pg.evaluate(js,a)
    J(SCEN);J(H.PDFTEXT)
    # ── 1. Comparativa = Beneficio flota (con comisiones) y cuadra con Negocio salvo los generales ──
    o={k:N(v) for k,v in J(CMP,'').items()}
    chk(o.get('Ingresos')==['450,00 €','588,00 €'],'Comparativa «Ingresos»: oct 300 + 150 de comisión · nov 420 + 168 de comisión',o.get('Ingresos'))
    chk(o.get('Gastos')==['100,00 €','50,00 €'],'Comparativa «Gastos»: sin los generales ni lo que paga el propietario (5.2)',o.get('Gastos'))
    chk(o.get('Beneficio')==['350,00 €','538,00 €'],'Comparativa «Beneficio» = Beneficio flota: oct 350 · nov 538',o.get('Beneficio'))
    neg=J("""m=>{const s=a=>a.reduce((t,e)=>t+(e.type==='income'&&!_isDepositInc(e)?1:e.type==='expense'?-1:0)*(Number(e.amount)||0),0);
      const bf=BF.filter(e=>!m||e.date.startsWith(m)),all=_getBizEntriesWithMgmt().filter(e=>!m||e.date.startsWith(m));return [s(all),s(bf)];}""",'2026-11')
    chk(abs(neg[0]-478)<0.005 and abs(neg[0]-neg[1]-538)<0.005,'Noviembre: Negocio 478 € = Beneficio flota 538 € − 60 € de gastos generales',neg)
    chk(o.get('Clientes únicos')==['1','1'],'Comparativa «Clientes únicos» sin «Cliente anonimizado» (1 y 1)',o.get('Clientes únicos'))
    o=J(CMP,'own');o={k:N(v) for k,v in o.items()}
    chk(o.get('Beneficio')==['200,00 €','370,00 €'] and o.get('Alquileres')==['1','1'] and o.get('Días ocupados')==['11','11'],'Comparativa con «Propios»: solo el coche propio (200 / 370 €, 1 alquiler, 11 días)',o)
    o=J(CMP,'managed');o={k:N(v) for k,v in o.items()}
    chk(o.get('Beneficio')==['150,00 €','168,00 €'] and o.get('Alquileres')==['1','1'],'Comparativa con «Gestión»: solo la comisión (150 / 168 €)',o)
    # ── 2. Cabecera «Beneficio flota» = Negocio de siempre − generales (#anB: con el período «Todo»; «Mes» = el mes actual) ──
    J("_analyticsOwnership='';setAnalyticsPeriod('todo')")
    hero=N(J("document.querySelector('.an-hero').innerText.replace(/\\s+/g,' ')"))
    allneg=J("""()=>{const s=a=>a.reduce((t,e)=>t+(e.type==='income'&&!_isDepositInc(e)?1:e.type==='expense'?-1:0)*(Number(e.amount)||0),0);return [s(_getBizEntriesWithMgmt()),s(BF)];}""")
    chk(re.search(r'BENEFICIO FLOTA',hero,re.I) and 'negocio' not in hero.lower(),'Cabecera: «Beneficio flota» (ya no «Beneficio del negocio»)',hero)
    chk(re.search(r'988 ?,00 €',hero) and abs(allneg[0]-allneg[1]-988)<0.005,'Cabecera «Todo»: 988 € = propios 670 + comisiones 318 = Negocio (928) − generales (−60)',[hero,allneg])
    meta=J("document.querySelector('.an-hero .d-meta').textContent.trim()")
    chk(meta=='Desde oct 2026','Cabecera «Todo»: debajo de la cifra, desde cuándo («Desde oct 2026»), sin explicar el cálculo',meta)
    J("setAnalyticsPeriod('mes')")
    hero=N(J("document.querySelector('.an-hero').innerText.replace(/\\s+/g,' ')"))
    chk(re.search(r'538 ?,00 €',hero),'Cabecera «Mes»: 538 € = la Comparativa de noviembre',hero)
    # ── 3. Amortización: una sola cifra, solo coches propios (#anB: en la lista «Coches»); sin «Proyección anual» ──
    J("setAnalyticsPeriod('todo')")
    an=J("""()=>{const d=[...document.querySelectorAll('details.an-acc')];d.forEach(x=>x.open=true);return d.map(x=>[x.querySelector('.t').textContent.trim(),x.innerText.replace(/\\s+/g,' ')]);}""")
    tit=[t for t,_ in an]
    txt=N(J("document.querySelector('.an').innerText.replace(/\\s+/g,' ')"))
    chk('Proyección' not in txt and 'Break-even' not in txt and 'proyect' not in txt,'Sin «Proyección anual» ni «Break-even»',tit)
    cars=J("""[...document.querySelectorAll('.an-car')].map(r=>r.innerText.replace(/\\s+/g,' '))""")
    tu=[c for c in cars if 'Turismo Uno' in c];fu=[c for c in cars if 'Furgo Dos' in c]
    chk(tu and fu and 'Amortizado' in tu[0] and 'Amortizado' not in fu[0],'Amortización: solo en el coche propio (el de gestión no la lleva)',cars)
    pay=re.findall(r'~(\d+) (mes(?:es)?)',' '.join(cars))
    chk(pay==[('19','meses')] and 'Amortizado 11 %' in tu[0],'Amortización: una sola cifra, «Amortizado 11 % · ~19 meses» ((6000 − 670) / 285 €/mes)',pay)
    chk('días al ritmo' not in txt,'Amortización: ya no en «días» (que suponía el coche alquilado todos los días)')
    chk(J("_amortMeses(V[0],6000,670)")==19 and abs(J("_amortRitmo(V[0])")-285)<0.005,'_amortRitmo = 285 €/mes (oct y nov; la reserva de diciembre no cuenta) y _amortMeses = 19')
    J("_analyticsOwnership='managed';nav('analytics')")
    chk('Amortizado' not in J("document.querySelector('.an').innerText"),'Con «Gestión» no sale ninguna amortización')
    # ── 4. Ocupación con el filtro (#anB: cifras «Ocupación» y «Días libres» del período) ──
    kpi=lambda:dict((b,a) for a,b in J("""[...document.querySelectorAll('.an-k4>div')].map(d=>[d.querySelector('b').textContent.trim(),d.querySelector('span').textContent.trim()])"""))
    J("_analyticsOwnership='own';setAnalyticsPeriod('mes')");k=kpi()
    chk(k.get('Ocupación')=='37%' and k.get('Días libres')=='19 d','«Mes» con «Propios»: 11 de 30 días = 37 %, 19 días libres (antes contaba 60 días disponibles)',k)
    J("_analyticsOwnership=''; nav('analytics')");k=kpi()
    chk(k.get('Ocupación')=='37%' and k.get('Días libres')=='38 d','«Mes» con «Todos»: 22 de 60 días, 38 libres',k)
    J("_analyticsOwnership='own';setAnalyticsPeriod('todo')");k=kpi()
    chk(k.get('Ocupación')=='30%' and k.get('Días libres')=='64 d','«Todo» con «Propios»: desde el primer mes con actividad (oct a dic: 92 días), 28 alquilados = 30 %, 64 libres',k)
    J("_analyticsOwnership='';nav('analytics')")
    # ── 5. Clientes sin anonimizados (período «Todo») ──
    cl=dict(an).get('Clientes','')
    chk(re.search(r'2 CLIENTES ÚNICOS 1 \(50%\)',N(cl),re.I) and 'anonimizado' not in cl,'Clientes: 2 únicos (Ana y Bea), 1 recurrente; sin «Cliente anonimizado»',cl[:160])
    # ── 6. Informe PDF de octubre a noviembre ──
    L=[N(t) for t in J("__pdfText(()=>generateAnalyticsPDF('2026-10','2026-11'),true)")]
    txt=' | '.join(L)
    chk(not any(t.startswith('ERROR') for t in L),'PDF: se genera sin error',[t for t in L if t.startswith('ERROR')])
    chk(any(t.startswith('Período: 10/2026 a 11/2026') for t in L),'PDF: «Período: 10/2026 a 11/2026»',[t for t in L if t.startswith('Período')])
    chk('PROYECCIÓN' not in txt.upper() and 'Break-even' not in txt,'PDF: sin proyección anual ni break-even')
    i=L.index('INGRESOS') if 'INGRESOS' in L else -1
    kpi=L[i-1] if i>0 else ''
    j=[k for k,t in enumerate(L) if t.startswith('ORIGEN DE CLIENTES')]
    pl={}
    if j:
        seg=L[j[0]:j[0]+60]
        for k,t in enumerate(seg):
            if t in ('Sin app','Amovens','Getaround','Otros ingresos'):pl[t]=(seg[k+1],seg[k+3])
    chk(kpi=='1820,00 €','PDF: «Ingresos» 1820 € (v1 300 + 420 + v2 500 + 600)',kpi)
    chk(pl=={'Sin app':('2','900,00 €'),'Getaround':('1','500,00 €'),'Amovens':('1','400,00 €'),'Otros ingresos':('-','20,00 €')},'PDF plataformas: los mismos movimientos que Ingresos (900 + 500 + 400 + 20 = 1820; «Otros ingresos» sin nº de alquileres)',pl)
    chk('Bfo. flota: 888,00 €' in L and 'BENEFICIO FLOTA' in L,'PDF: «Bfo. flota» 888 € (propio 570 + comisiones 318)',[t for t in L if 'flota' in t.lower()])
    roiP=[t for t in L if '· ~' in t and 'mes' in t]
    chk(roiP==['5330,00 € · ~19 meses'],'PDF ROI: pendiente con la misma cifra de la pantalla («5330,00 € · ~19 meses»), solo el propio',roiP)
    k=L.index('CL. UNICOS') if 'CL. UNICOS' in L else -1
    chk(k>0 and L[k-1]=='1' and 'Cliente anonimizado' not in L,'PDF clientes: 1 único (Ana), sin «Cliente anonimizado»',L[k-1] if k>0 else None)
    ctx.close()
    # ── 7. Escritorio: «Informe PDF» abre el selector de período ──
    ctx,pg=H.open_app(br,viewport={'width':1280,'height':900},tag='1280')
    pg.evaluate(SCEN);pg.evaluate("nav('analytics')");pg.wait_for_timeout(300)
    b=pg.locator('.desk-btn',has_text='Informe PDF')
    chk(b.count()==1 and b.get_attribute('onclick')=='openAnalyticsReportPicker()','Escritorio: el botón «Informe PDF» abre el selector de período')
    if b.count():
        b.click();pg.wait_for_timeout(300)
        chk(pg.evaluate("!!document.getElementById('arFrom')&&!!document.getElementById('arTo')"),'Escritorio: se ve el selector (Desde / Hasta)')
    ctx.close();br.close()
H.fin()
