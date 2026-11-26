# Analítica · pantalla nueva (bloque B): período Mes · Año · Todo con variación, las 4 cifras del período, previsión del mes,
# lista única de coches (lo que deja cada uno, ocupación, estado de hoy y amortización de los propios), comparativa automática
# (este mes, el anterior y el mismo mes del año pasado), «Más datos» plegado (clientes, duración, turismo vs furgoneta) y sin los
# bloques y textos que sobraban. Datos inventados; fecha fija del arnés: 20/11/2026. Cuentas a mano (comisión 30 %):
#   Coche Uno (propio, compra 8000 €): nov 2025 150 · oct 330 − 100 = 230 · nov 400 + 120 (empieza el 25) − 40 = 480
#   Furgo Dos (gestión): oct 500 × 30 % = 150 · nov (600 − 50 de limpieza, 5.3) × 30 % = 165 · Coche Tres (propio): sin alquileres, taller 21 y 22/11
#   Beneficio flota: nov 645 (propios 480 + gestión 165) · oct 380 · nov 2025 150 → ▲ 70 % vs oct · ▲ 330 % vs nov 2025
#   Año 2026: 380 + 645 = 1025 (▲ 583 % vs ene–nov 2025: 150) · Todo: 1175 = Negocio (1115) − generales (−60)
#   Noviembre: 24 días alquilados de 90 = 27 % · facturado 1120 € → 46,67 €/día alquilado · 12,44 €/día disponible · 64 días libres
#   Octubre (Coche Tres aún sin actividad): 22 de 62 = 35 % · 830 € → 37,73 €/día alq. · 13,39 €/día disp. · 40 libres
#   Previsión: hecho o en curso 400 + 600 = 1000 € · por empezar 120 € · días libres del 21 al 30: 6 + 7 + 8 = 21
#   Amortización Coche Uno: beneficio 860 € (11 %); ritmo (230 + 480) / 6 meses = 118,33 €/mes → 7140 / 118,33 = 60,3 → ~61 meses
# Uso: python3 tests/test_analitica_pantalla.py
import sys,os,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
chk=H.chk
SCEN=r"""(()=>{
 const mk=(id,s,e,cl,amt,pl,x)=>Object.assign({id,startDate:s,startTime:'10:00',endDate:e,endTime:'10:00',platform:pl,amount:amt,clientName:cl,finance:[],extras:[]},x||{});
 V=[{id:'v1',name:'Coche Uno',plate:'0000AAA',model:'Uno',year:2020,vtype:'own',purchase_price:8000,vehicle_type:'turismo',color:'#8B5CF6',
     bookings:[mk('p1','2025-11-10','2025-11-15','Ana Prueba',150,'sinapp',{clientDni:'00000001R',returned:true,delivered:true}),
               mk('p2','2026-10-01','2026-10-11','Ana Prueba',330,'sinapp',{clientDni:'00000001R',returned:true,delivered:true}),
               mk('p3','2026-11-01','2026-11-11','Bea Prueba',400,'amovens',{returned:true,delivered:true}),
               mk('p4','2026-11-25','2026-11-28','Carla Prueba',120,'sinapp')],
     finances:[{id:'f1',type:'expense',amount:100,date:'2026-10-03',category:'Mantenimiento'},{id:'f2',type:'expense',amount:40,date:'2026-11-05',category:'Combustible'}]},
    {id:'v2',name:'Furgo Dos',plate:'1111BBB',model:'Dos',year:2020,vtype:'managed',ownerId:'o1',commission:30,vehicle_type:'l1h1',color:'#14B8A6',
     bookings:[mk('q1','2026-10-10','2026-10-20','Dani Prueba',500,'getaround',{returned:true,delivered:true}),
               mk('q2','2026-11-15','2026-11-23','Ana Prueba',600,'sinapp',{clientDni:'00000001R',delivered:true})],
     finances:[{id:'g1',type:'expense',amount:50,date:'2026-11-08',category:'Limpieza'}]},
    {id:'v3',name:'Coche Tres',plate:'2222CCC',model:'Tres',year:2019,vtype:'own',vehicle_type:'turismo',color:'#8B5CF6',bookings:[],finances:[],
     calendar:{'2026-11-21':'maintenance','2026-11-22':'maintenance'}}];
 V.forEach(v=>v.bookings.forEach(b=>{const fe=proRataEntries(b.startDate,b.endDate,b.amount,b.platform,'',b.id);fe.forEach(e=>v.finances.push(e));b.financeIds=fe.map(e=>e.id);b.financeId=fe[0]&&fe[0].id;}));
 BF=[{id:'n1',type:'expense',amount:60,date:'2026-11-02',category:'Gestoría'}];
 _analyticsOwnership='';_analyticsVtype='';_invalidateRsCache();return true;})()"""
T=lambda s:H.N(re.sub(r'\s+',' ',s or '')).strip()
with H.playwright() as p:
    br=H.launch(p)
    ctx,pg=H.open_app(br)
    J=lambda js,a=None:pg.evaluate(js,a)
    J(SCEN);J("setAnalyticsPeriod('mes')")
    tx=lambda sel:T(J("s=>{const e=document.querySelector(s);return e?e.textContent:''}",sel))
    # ── 1. Estructura: cabecera con período, 4 cifras, previsión, coches, comparativa y «Más datos»; nada de lo que sobraba ──
    hs=J("[...document.querySelectorAll('.an-h h3')].map(h=>h.textContent.trim())")
    chk(hs==['Previsión del mes','Coches','Comparativa','Más datos'],'Bloques: cabecera y cifras, Previsión del mes, Coches, Comparativa y Más datos',hs)
    acc=J("[...document.querySelectorAll('details.an-acc>summary>.t')].map(t=>t.textContent.trim())")
    chk(acc==['Elegir otros meses','Clientes','Duración de los alquileres','Turismo vs furgoneta'],'Plegados: solo «Elegir otros meses», Clientes, Duración y Turismo vs furgoneta (fuera Ranking, ROI, Actividad vs beneficio, Ocupación, Eficiencia y Proyección)',acc)
    chk(J("[...document.querySelectorAll('details.an-acc')].every(d=>!d.open)"),'Todos los plegados empiezan cerrados')
    al=T(J("document.querySelector('.an').textContent"))
    malos=[x for x in ('déficit','÷','por cada','beneficio 100%','propios +','Ranking','ROI','Proyección','Eficiencia','Tiempo muerto') if x in al]
    chk(not malos,'Sin textos que explican cálculos ni bloques antiguos',malos)
    # ── 2. Cabecera «Mes»: Beneficio flota de noviembre con su variación ──
    hero=tx('.an-hero')
    chk(re.search(r'BENEFICIO FLOTA ?nov 2026 ?645 ?,00 €',hero,re.I),'Cabecera «Mes»: Beneficio flota de nov 2026 = 645 €',hero)
    chk(tx('.an-hero .an-dl')=='▲ 70 % vs oct · ▲ 330 % vs nov 2025','Variación: ▲ 70 % vs oct (380 €) · ▲ 330 % vs nov 2025 (150 €)',tx('.an-hero .an-dl'))
    chk(re.search(r'Propios \(2\) ?480,00 € ?Gestión \(1\) ?165,00 €',hero),'Propios 480 € y Gestión 165 € (sin rótulos explicativos)',hero)
    neg=J("""m=>{const s=a=>a.reduce((t,e)=>t+(e.type==='income'&&!_isDepositInc(e)?1:e.type==='expense'?-1:0)*(Number(e.amount)||0),0);
      return [s(_getBizEntriesWithMgmt().filter(e=>e.date.startsWith(m))),s(BF.filter(e=>e.date.startsWith(m)))];}""",'2026-11')
    chk(abs(neg[0]-neg[1]-645)<0.005,'Noviembre: cuadra con Negocio (585 €) salvo los 60 € de generales',neg)
    # ── 3. Las 4 cifras del mes y su variación frente a octubre ──
    k=J("""[...document.querySelectorAll('.an-k4>div')].map(d=>[d.querySelector('span').textContent.trim(),d.querySelector('b').textContent.trim(),(d.querySelector('em')||{}).textContent||''])""")
    k={a:(H.N(b),H.N(c).strip()) for a,b,c in k}
    chk(k.get('Ocupación')==('27%','▼ 8 pt'),'Ocupación 27 % (24 de 90 días), ▼ 8 pt vs octubre (35 %)',k.get('Ocupación'))
    chk(k.get('Precio medio día')==('46,67 €','▲ 24 %'),'Precio medio día 46,67 € (1120 / 24), ▲ 24 % (37,73 €)',k.get('Precio medio día'))
    chk(k.get('Rinde al día')==('12,44 €','▼ 7 %'),'Rinde al día 12,44 € (1120 / 90), ▼ 7 % (13,39 €)',k.get('Rinde al día'))
    chk(k.get('Días libres')==('64 d','▲ 24 d'),'Días libres 64 (15 + 21 + 28, sin los 2 de taller), ▲ 24 d en rojo (40 en octubre)',k.get('Días libres'))
    chk(J("document.querySelector('.an-k4>div:nth-child(4) .an-d').classList.contains('err')"),'Más días libres que el mes anterior se marca en rojo')
    # ── 4. Previsión del mes ──
    pv=J("[...document.querySelectorAll('.an-pv .an-li')].map(r=>[r.querySelector('span').textContent.trim(),r.querySelector('b').textContent.trim()])")
    pv={a:H.N(b) for a,b in pv}
    chk(pv=={'Hecho o en curso':'1000,00 €','Reservado, por empezar':'120,00 €','Días libres hasta fin de mes':'21 d'},'Previsión: hecho o en curso 1000 €, por empezar 120 €, 21 días libres del 21 al 30',pv)
    # ── 5. Coches: orden por lo que dejan, ocupación, estado de hoy y amortización ──
    cars=[T(c) for c in J("[...document.querySelectorAll('.an-car')].map(r=>r.textContent)")]
    chk([c.split(' ')[0]+' '+c.split(' ')[1] for c in cars]==['Coche Uno','Furgo Dos','Coche Tres'],'Coches ordenados por lo que dejan: 480, 165 y 0 €',cars)
    chk(len(cars)==3 and cars[0]=='Coche Uno 50% ocup. · 17,33 €/día disp. Libre desde hace 9 d · próximo 25/11 Amortizado 11 % · ~61 meses 480,00 €','Coche Uno: 50 % · 17,33 €/día disp. · libre desde hace 9 d · próximo 25/11 · amortizado 11 % · ~61 meses',cars[:1])
    chk(len(cars)==3 and cars[1]=='Furgo Dos 30% ocup. · 20,00 €/día disp. · gestión 30 % Alquilado hasta 23/11 165,00 €','Furgo Dos: alquilado hasta 23/11, comisión 30 %, sin amortización',cars[1:2])
    chk(len(cars)==3 and cars[2]=='Coche Tres 0% ocup. · 0,00 €/día disp. Libre · sin reserva 0,00 €','Coche Tres: libre y sin reserva',cars[2:])
    chk(J("[...document.querySelectorAll('.an-car')][2].querySelector('.s.ac')!==null") and J("[...document.querySelectorAll('.an-car')][0].querySelector('.s.ac')===null"),'Libre sin reserva en dorado; con reserva próxima, en gris')
    chk(J("_amortMeses(V[0],8000,860)")==61,'_amortMeses(Coche Uno) = 61 (ritmo de los últimos 6 meses: 710 / 6)')
    # ── 6. Comparativa automática ──
    cmp=J("[...document.querySelectorAll('.an-c3>div')].map(r=>[...r.children].map(c=>c.textContent.trim()))")
    cmp=[[H.N(x) for x in r] for r in cmp]
    exp=[['','nov','oct','nov 2025'],['Facturado','1120 €','830 €','150 €'],['Gastos','40 €','100 €','0 €'],['Beneficio flota','645 €','380 €','150 €'],['Alquileres','3','2','1'],['Clientes','3','2','1']]
    chk(cmp==exp,'Comparativa: nov · oct · nov 2025 (facturado, gastos, beneficio flota, alquileres y clientes)',cmp)
    # ── 7. Más datos del período ──
    J("document.querySelectorAll('details.an-acc').forEach(d=>d.open=true)")
    cl=T(J("[...document.querySelectorAll('details.an-acc')].find(d=>d.querySelector('summary>.t').textContent.trim()==='Clientes').innerText"))
    chk(re.match(r'01 Clientes 3 clientes únicos 0 \(0%\)',cl,re.I),'Clientes de noviembre: 3 únicos, 0 recurrentes',cl[:80])
    tv=T(J("document.querySelector('.an-tb').innerText"))
    chk('Beneficio flota 480,00 € 165,00 €' in tv and 'Facturado 520,00 € 600,00 €' in tv,'Turismo vs furgoneta con las cifras de la pantalla: beneficio flota 480 + 165 = cabecera',tv)
    # ── 8. Año y Todo ──
    J("setAnalyticsPeriod('ano')")
    chk(re.search(r'2026 ?1025 ?,00 €',tx('.an-hero')) and tx('.an-hero .an-dl')=='▲ 583 % vs ene–nov 2025','«Año»: 1025 € (oct + nov), ▲ 583 % vs ene–nov 2025',[tx('.an-hero'),tx('.an-hero .an-dl')])
    J("setAnalyticsPeriod('todo')")
    allneg=J("""()=>{const s=a=>a.reduce((t,e)=>t+(e.type==='income'&&!_isDepositInc(e)?1:e.type==='expense'?-1:0)*(Number(e.amount)||0),0);return [s(_getBizEntriesWithMgmt()),s(BF)];}""")
    chk(re.search(r'Todo ?1175 ?,00 €',tx('.an-hero')) and abs(allneg[0]-allneg[1]-1175)<0.005 and tx('.an-hero .an-dl')=='Desde nov 2025','«Todo»: 1175 € = Negocio − generales, «Desde nov 2025»',[tx('.an-hero'),allneg])
    J("document.querySelectorAll('details.an-acc').forEach(d=>d.open=true)")
    cl=T(J("[...document.querySelectorAll('details.an-acc')].find(d=>d.querySelector('summary>.t').textContent.trim()==='Clientes').innerText"))
    chk(re.match(r'01 Clientes 4 clientes únicos 1 \(25%\)',cl,re.I),'Clientes de «Todo»: 4 únicos, 1 recurrente (Ana)',cl[:80])
    chk(tx('.an-c3 .h')==tx('.an-c3 .h') and 'nov 2025' in tx('.an-c3 .h'),'La comparativa sigue siendo por meses aunque el período sea «Todo»')
    # ── 9. Filtro «Gestión»: cabecera = comisión; comparativa con «—» si no hay actividad ──
    J("_analyticsOwnership='managed';setAnalyticsPeriod('mes')")
    chk(re.search(r'165 ?,00 €',tx('.an-hero')) and not J("document.querySelector('.an-hs')"),'«Gestión»: cabecera 165 € y sin el reparto Propios / Gestión',tx('.an-hero'))
    cmp=[[H.N(x) for x in r] for r in J("[...document.querySelectorAll('.an-c3>div')].map(r=>[...r.children].map(c=>c.textContent.trim()))")]
    chk(cmp[3]==['Beneficio flota','165 €','150 €','—'],'«Gestión»: comparativa 165 / 150 € y «—» en nov 2025 (sin actividad)',cmp[3] if len(cmp)>3 else cmp)
    J("_analyticsOwnership='';nav('analytics')")
    # ── 10. Período recordado en este móvil; tocar un coche abre su ficha ──
    J("setAnalyticsPeriod('ano')");pg.reload();pg.wait_for_timeout(1500);J(SCEN);J("nav('analytics')");pg.wait_for_timeout(300)
    chk(J("_analyticsPer")=='ano' and J("document.querySelector('.an-per [aria-pressed=true]').textContent.trim()")=='Año','El período elegido se recuerda al volver a abrir la app')
    J("setAnalyticsPeriod('mes')")
    pg.locator('.an-car').first.click();pg.wait_for_timeout(300)
    chk(J("AV")=='v1','Tocar un coche abre su ficha')
    J("AV=null;nav('analytics')");pg.wait_for_timeout(300)
    # ── 11. Móvil: tamaños táctiles y nada se sale (oscuro) ──
    hmin=J("Math.min(...[...document.querySelectorAll('.an-per button,.an-car,.an-own button')].map(b=>b.getBoundingClientRect().height))")
    chk(hmin>=44,'Botones de período, filas de coche y filtros de al menos 44 px',hmin)
    J("document.querySelectorAll('details.an-acc').forEach(d=>d.open=true)")
    sw=J("Math.max(document.documentElement.scrollWidth,...[...document.querySelectorAll('.an *')].filter(e=>!e.closest('.d-pills')).map(e=>Math.ceil(e.getBoundingClientRect().right)))")
    chk(sw<=390,'Nada se sale a 390 px en modo oscuro (salvo la fila de tipos, que se desliza como siempre)',sw)
    if H.CAPTURAS:pg.screenshot(path=os.path.join(H.CAPTURAS,'analitica-oscuro.png'),full_page=True)
    ctx.close()
    # ── 12. Modo claro ──
    ctx,pg=H.open_app(br,theme='light',tag='claro')
    pg.evaluate(SCEN);pg.evaluate("setAnalyticsPeriod('mes')");pg.wait_for_timeout(300)
    pg.evaluate("document.querySelectorAll('details.an-acc').forEach(d=>d.open=true)")
    sw=pg.evaluate("Math.max(document.documentElement.scrollWidth,...[...document.querySelectorAll('.an *')].filter(e=>!e.closest('.d-pills')).map(e=>Math.ceil(e.getBoundingClientRect().right)))")
    chk(sw<=390 and 'Beneficio flota' in pg.evaluate("document.querySelector('.an-hero').textContent"),'Modo claro: misma pantalla y nada se sale',sw)
    ctx.close();br.close()
H.fin()
