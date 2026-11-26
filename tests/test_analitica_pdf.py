# Analítica · informe PDF (bloque C): 4 páginas (Resumen con barras por mes · Coches con barras por coche · Desglose de gastos y duración · Clientes y plataformas) con las MISMAS cifras que la pantalla
# (_anVs, _anIdx, _anStats y _anRange): Beneficio flota del período y su variación, las 4 cifras, comparativa, coches con su ocupación,
# lo que deja cada uno y la amortización de los propios, turismo vs furgoneta, clientes (sin anonimizados) y duración; período desde/hasta,
# cabecera y pie de los PDF de siempre, tamaño pequeño y sin bloques ni textos antiguos. Mismos datos inventados que test_analitica_pantalla.py
# (fecha fija 20/11/2026). Gráficos (secciones 10 a 14; ingresos, gastos y beneficio flota por mes); desglose de gastos (15): se dibujan, escala con negativos y ceros, un solo coche, de 1 a 12 meses; plataformas = Facturado. Cuentas a mano: noviembre 645 € (propios 480 + gestión 165), ▲ 70 % vs oct (380) y ▲ 330 % vs nov 2025 (150);
# 27 % de ocupación (▼ 8 pt), 46,67 € de precio medio día (▲ 24 %), 12,44 € que rinde al día (▼ 7 %), 64 días libres (▲ 24 d);
# octubre y noviembre: 1025 € (sin variación frente a ago-sep, que no tuvo actividad; ▲ 583 % vs oct-nov 2025: 150 €).
# Uso: python3 tests/test_analitica_pdf.py
import sys,os,re,base64,subprocess,tempfile
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
chk=H.chk
TMP=tempfile.mkdtemp(prefix='deiros_anpdf_')
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
# Registra texto, rectángulos (con su relleno), líneas y páginas del PDF: __pdfOps(()=>generateAnalyticsPDF(…))
OPS=r"""window.__pdfOps=async function(fn){await ensureLib('jspdf');const O=window.jspdf.jsPDF;const L=[];const al=window.alert;window.alert=m=>L.push({t:'error',s:String(m)});
  const W=function(){const d=new O(...arguments);const t=d.text,r=d.rect,ln=d.line,ap=d.addPage;let pg=1;
    d.text=function(x,a,b){L.push({t:'text',s:Array.isArray(x)?x.join(' '):String(x),x:a,y:b,p:pg});return t.apply(this,arguments);};
    d.rect=function(a,b,c,e,st){L.push({t:'rect',x:a,y:b,w:c,h:e,st:st,f:this.getFillColor(),p:pg});return r.apply(this,arguments);};
    d.line=function(a,b,c,e){L.push({t:'line',x1:a,y1:b,x2:c,y2:e,p:pg});return ln.apply(this,arguments);};
    d.addPage=function(){pg++;return ap.apply(this,arguments);};return d;};
  Object.assign(W,O);W.API=O.API;window.jspdf.jsPDF=W;const s=window._savePDF;window._savePDF=()=>{};
  try{await fn();}catch(e){L.push({t:'error',s:e.message});}finally{window.jspdf.jsPDF=O;window._savePDF=s;window.alert=al;}return L;};true"""
CAP=r"""(()=>{window.__AL=[];window.alert=m=>window.__AL.push(String(m));window.__PDF=null;
 _savePDF=function(doc,fn){window.__PDF={name:fn,u:doc.output('datauristring')};};return true;})()"""
def pdf(pg,a,b):
    pg.evaluate("()=>{window.__PDF=null;window.__AL=[];}")
    L=[H.N(t) for t in pg.evaluate("([a,b])=>__pdfText(()=>generateAnalyticsPDF(a,b),true)",[a,b])]
    pg.evaluate("([a,b])=>generateAnalyticsPDF(a,b)",[a,b]);pg.wait_for_timeout(300)
    r=pg.evaluate("window.__PDF");f=None
    if r:
        f=os.path.join(TMP,r['name']);open(f,'wb').write(base64.b64decode(r['u'].split(',',1)[1]))
    return L,f,(r or {}).get('name'),pg.evaluate("window.__AL")
def pages(f):
    o=subprocess.run(['pdfinfo',f],capture_output=True,text=True).stdout;m=re.search(r'Pages:\s+(\d+)',o);return int(m.group(1)) if m else 0
def ptext(f,p):return H.N(re.sub(r'\s+',' ',subprocess.run(['pdftotext','-f',str(p),'-l',str(p),'-layout',f,'-'],capture_output=True,text=True).stdout))
after=lambda L,k,n=1:L[L.index(k)+1:L.index(k)+1+n] if k in L else None
before=lambda L,k:L[L.index(k)-1] if k in L and L.index(k)>0 else None
with H.playwright() as p:
    br=H.launch(p)
    ctx,pg=H.open_app(br)
    J=lambda js,a=None:pg.evaluate(js,a)
    J(SCEN);J(H.PDFTEXT);J(CAP)
    # ── 1. Noviembre: 3 páginas, tamaño, nombre, cabecera y pie de siempre ──
    L,f,name,al=pdf(pg,'2026-11','2026-11')
    chk(f and not al and not any(t.startswith('ERROR') for t in L),'Noviembre: el PDF se genera sin avisos ni errores',[al,[t for t in L if t.startswith('ERROR')]])
    chk(f and pages(f)==4,'4 páginas (antes 6)',pages(f) if f else None)
    chk(f and os.path.getsize(f)<150*1024,'Tamaño pequeño (< 150 KB)',os.path.getsize(f) if f else None)
    chk(name=='Informe_Analiticas_2026-11_2026-11.pdf','Nombre del fichero con el período',name)
    chk('INFORME DE ANALÍTICAS' in L and 'NOV 2026' in L and 'Toda la flota' in L and 'Página 4 de 4' in L,'Cabecera y pie de los PDF de siempre (_pdfBrand): título, período, filtro y «Página N de 4»')
    if f:
        p1,p2,p3,p4=ptext(f,1),ptext(f,2),ptext(f,3),ptext(f,4)
        chk('BENEFICIO FLOTA' in p1 and 'COMPARATIVA' in p1 and 'INGRESOS, GASTOS Y BENEFICIO FLOTA POR MES' in p1 and 'LO QUE DEJA CADA COCHE' in p2 and 'COCHES' in p2 and 'TURISMO VS FURGONETA' in p2
            and 'DESGLOSE DE GASTOS' in p3 and 'DURACIÓN DE LOS ALQUILERES' in p3 and 'CLIENTES' in p4 and 'PLATAFORMAS' in p4,
            'Página 1: Beneficio flota, cifras, comparativa y barras por mes · 2: barras por coche, coches y turismo vs furgoneta · 3: desglose de gastos y duración · 4: clientes y plataformas')
        chk(all(len(x)>250 for x in (p1,p2,p3,p4)),'Ninguna página casi vacía',[len(x) for x in (p1,p2,p3,p4)])
    # ── 2. Cifras de noviembre, iguales que la pantalla «Mes» ──
    chk(after(L,'BENEFICIO FLOTA')==['645,00 €'],'Beneficio flota de noviembre 645 €',after(L,'BENEFICIO FLOTA'))
    chk(after(L,'+70 %')==['vs oct'] and after(L,'+330 %')==['vs nov 2025'],'Variación: +70 % vs oct · +330 % vs nov 2025',[t for t in L if t.startswith('vs ')])
    chk(after(L,'PROPIOS (2)')==['480,00 €'] and after(L,'GESTIÓN (1)')==['165,00 €'],'Propios 480 € y Gestión 165 €')
    K={k:(before(L,k),after(L,k)) for k in ('OCUPACIÓN','PRECIO MEDIO DÍA','RINDE AL DÍA','DÍAS LIBRES')}
    chk(K=={'OCUPACIÓN':('27%',['-8 pt']),'PRECIO MEDIO DÍA':('46,67 €',['+24 %']),'RINDE AL DÍA':('12,44 €',['-7 %']),'DÍAS LIBRES':('64 d',['+24 d'])},'Las 4 cifras y su variación frente a octubre',K)
    J("_analyticsOwnership='';setAnalyticsPeriod('mes')");pg.wait_for_timeout(200)
    scr=J("""()=>({hero:document.querySelector('.an-hero .d-n').textContent.replace(/\\s+/g,''),
      k:[...document.querySelectorAll('.an-k4>div b')].map(b=>b.textContent.trim()),
      kd:[...document.querySelectorAll('.an-k4>div')].map(d=>(d.querySelector('em')||{}).textContent||''),
      cars:[...document.querySelectorAll('.an-car')].map(r=>[r.querySelector('.n').textContent.trim(),r.querySelector(':scope>b').textContent.trim()])})""")
    scr={k:([H.N(x) for x in v] if isinstance(v,list) and v and isinstance(v[0],str) else v) for k,v in scr.items()}
    chk(H.N(scr['hero']).replace(' ','')==after(L,'BENEFICIO FLOTA')[0].replace(' ',''),'Pantalla y PDF: el mismo Beneficio flota',[scr['hero'],after(L,'BENEFICIO FLOTA')])
    chk(scr['k']==[K[k][0] for k in ('OCUPACIÓN','PRECIO MEDIO DÍA','RINDE AL DÍA','DÍAS LIBRES')],'Pantalla y PDF: las mismas 4 cifras',[scr['k']])
    sd=[re.sub(r'[▲]','+',re.sub(r'[▼]','-',H.N(x))).replace(' ','').lower() for x in scr['kd']]
    chk(sd==[K[k][1][0].replace(' ','').lower() for k in ('OCUPACIÓN','PRECIO MEDIO DÍA','RINDE AL DÍA','DÍAS LIBRES')],'Pantalla y PDF: las mismas variaciones',sd)
    # ── 3. Comparativa ──
    i=L.index('Facturado') if 'Facturado' in L else -1
    cmp={L[j]:L[j+1:j+4] for j in range(i,i+20) if j>=0 and L[j] in ('Facturado','Gastos','Beneficio flota','Alquileres','Clientes')}
    io=L.index('OCT') if 'OCT' in L else -1
    chk(io>0 and L[io-1:io+2]==['NOV 2026','OCT','NOV 2025'],'Comparativa: NOV 2026 · OCT · NOV 2025',L[io-1:io+2] if io>0 else None)
    chk(cmp=={'Facturado':['1120,00 €','830,00 €','150,00 €'],'Gastos':['40,00 €','100,00 €','0,00 €'],'Beneficio flota':['645,00 €','380,00 €','150,00 €'],'Alquileres':['3','2','1'],'Clientes':['3','2','1']},'Comparativa con las cifras de la pantalla',cmp)
    # ── 4. Coches: lo que deja cada uno (como la pantalla), ocupación y amortización solo de los propios ──
    names=[t for t in L if re.match(r'(Coche Uno|Furgo Dos|Coche Tres) · ',t)]
    chk(names==['Coche Uno · 0000AAA','Furgo Dos · 1111BBB','Coche Tres · 2222CCC'],'Coches en el mismo orden que la pantalla',names)
    rows={n.split(' · ')[0]:L[L.index(n)+1:L.index(n)+9] for n in names}
    chk(rows.get('Coche Uno',[None])[0]=='Amortizado 11 % · ~61 meses' and rows['Coche Uno'][1:7]==['2','15','50%','17,33 €','520,00 €','480,00 €'],'Coche Uno: amortizado 11 % · ~61 meses; 2 alq., 15 días, 50 %, rinde 17,33 € al día, 520 € facturado, deja 480 €',rows.get('Coche Uno'))
    chk(rows.get('Furgo Dos',[None])[0]=='Gestión 30 %' and rows['Furgo Dos'][6]=='165,00 €','Furgo Dos: gestión 30 %, sin amortización, deja 165 €',rows.get('Furgo Dos'))
    chk(rows.get('Coche Tres',[None])[0]=='0' and 'Amortizado' not in ' '.join(rows.get('Coche Tres',[])),'Coche Tres: sin precio de compra, sin amortización',rows.get('Coche Tres'))
    sc=[[H.N(a),H.N(b)] for a,b in scr['cars']];pc=[[n.split(' · ')[0],[x for x in rows[n.split(' · ')[0]] if x.endswith('€')][-1]] for n in names]
    chk(sc==pc,'Pantalla y PDF: lo mismo que deja cada coche',[sc,pc])
    chk(after(L,'TOTAL',7)==['3','24','27%','12,44 €','1120,00 €','645,00 €'][:7] or (after(L,'TOTAL',6)==['3','24','27%','12,44 €','1120,00 €','645,00 €']),'Total de coches = cifras del período (24 días, 27 %, 1120 €, 645 €)',after(L,'TOTAL',6))
    tv=L[L.index('TURISMOS (2)'):L.index('TURISMOS (2)')+18] if 'TURISMOS (2)' in L else []
    chk('FURGONETAS (1)' in tv and tv[tv.index('Beneficio flota')+1:tv.index('Beneficio flota')+3]==['480,00 €','165,00 €'] if 'Beneficio flota' in tv else False,'Turismo vs furgoneta: beneficio flota 480 / 165 €',tv)
    # ── 5. Clientes y duración (alquileres que empiezan en noviembre) ──
    chk(before(L,'CLIENTES ÚNICOS')=='3' and before(L,'CLIENTES RECURRENTES')=='0 (0%)','Clientes: 3 únicos, 0 recurrentes',[before(L,'CLIENTES ÚNICOS'),before(L,'CLIENTES RECURRENTES')])
    chk(after(L,'Corto (1-3 días)',3)==['1','33%','120,00 €'] and after(L,'Medio (4-7 días)',3)==['0','0%','-'],'Duración: 1 corto (25 al 28/11, 120 €) y ningún medio («-»)',[after(L,'Corto (1-3 días)',3),after(L,'Medio (4-7 días)',3)])
    chk(after(L,'Largo (8 días o más)',3)==['2','67%','500,00 €'],'Duración: 2 largos (400 y 600 €: Ø 500 €)',after(L,'Largo (8 días o más)',3))
    # ── 6. Nada de lo antiguo ni textos que expliquen cálculos ──
    txt=' | '.join(L)
    malos=[x for x in ('PROYECCI','Break-even','RANKING','PART.NEGOCIO','(G)','ROI','Ocup. global','ORIGEN DE CLIENTES','déficit','BFO. ACTIVIDAD','EFICIENCIA','DESGLOSE MENSUAL','DESGLOSE ECONÓMICO','Período:','€ / DÍA','€/DÍA','€/día') if x.lower() in txt.lower()]
    chk(not malos,'Sin bloques ni textos antiguos (proyección, ranking, ROI, plataformas, eficiencia, «€/día», explicaciones…)',malos)
    # ── 7. Período desde/hasta: octubre y noviembre = 1025 €; enero a noviembre = pantalla «Año» ──
    L2,f2,name2,_=pdf(pg,'2026-10','2026-11')
    chk('OCT-NOV 2026' in L2 and after(L2,'BENEFICIO FLOTA')==['1025,00 €'] and name2=='Informe_Analiticas_2026-10_2026-11.pdf','Octubre y noviembre: 1025 €, «OCT-NOV 2026»',[after(L2,'BENEFICIO FLOTA'),name2])
    chk(after(L2,'+583 %')==['vs oct-nov 2025'] and not any(t.startswith('vs ago') for t in L2),'Variación: +583 % vs oct-nov 2025; sin variación frente a ago-sep (sin actividad)',[t for t in L2 if t.startswith('vs ')])
    chk(f2 and pages(f2)==4,'Octubre y noviembre: también 4 páginas')
    L3,_,_,_=pdf(pg,'2026-11','2026-01')
    J("setAnalyticsPeriod('ano')");pg.wait_for_timeout(200)
    ano=H.N(J("document.querySelector('.an-hero .d-n').textContent.replace(/\\s+/g,'')"))
    k3=[H.N(x) for x in J("[...document.querySelectorAll('.an-k4>div b')].map(b=>b.textContent.trim())")]
    chk('ENE-NOV 2026' in L3 and after(L3,'BENEFICIO FLOTA')[0].replace(' ','')==ano.replace(' ','') and [before(L3,k) for k in ('OCUPACIÓN','PRECIO MEDIO DÍA','RINDE AL DÍA','DÍAS LIBRES')]==k3,
        'Enero a noviembre (aunque se elijan al revés) = pantalla «Año»: mismo beneficio y mismas 4 cifras',[after(L3,'BENEFICIO FLOTA'),ano,k3])
    # ── 8. Filtro «Gestión» ──
    J("_analyticsOwnership='managed';nav('analytics')")
    L4,_,_,_=pdf(pg,'2026-11','2026-11')
    chk(after(L4,'BENEFICIO FLOTA')==['165,00 €'] and 'En gestión' in L4 and not any(t.startswith('Amortizado') for t in L4) and 'PROPIOS (2)' not in L4,'«Gestión»: 165 €, «En gestión» en la cabecera, sin amortización ni reparto',[after(L4,'BENEFICIO FLOTA')])
    J("_analyticsOwnership='';nav('analytics')")
    # ── 9. Selector del informe: desde/hasta y sin la lista de contenidos antigua ──
    J("openAnalyticsReportPicker()");pg.wait_for_timeout(300)
    chk(J("!!document.getElementById('arFrom')&&!!document.getElementById('arTo')") and 'ranking' not in J("document.querySelector('.ssub').textContent").lower(),'Selector con Desde / Hasta y sin la lista de contenidos antigua')
    J("closeSheet()")
    # ══ Gráficos y plataformas ══
    J(OPS)
    GD,PU,KO,GR='#d4a800','#6a0dad','#b91c1c','#5a5a5a'
    MES=re.compile(r'^(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)$')
    def ops(a,b):return J("([a,b])=>__pdfOps(()=>generateAnalyticsPDF(a,b))",[a,b])
    def region(O,t0,t1):
        i=next((k for k,o in enumerate(O) if o['t']=='text' and o.get('s')==t0),None)
        if i is None:return []
        j=next((k for k in range(i+1,len(O)) if O[k]['t']=='text' and O[k].get('s')==t1),len(O))
        return O[i:j]
    # jsPDF guarda el color en 0-1: al leerlo puede variar en 1 unidad → se compara con tolerancia y se normaliza al de PDFS
    def cn(h):
        h=str(h or '').lstrip('#').lower()
        if len(h)!=6:return h
        c=[int(h[i:i+2],16) for i in (0,2,4)]
        for ref in (GD,PU,KO,GR):
            r=[int(ref[1+i:3+i],16) for i in (0,2,4)]
            if all(abs(x-y)<=2 for x,y in zip(c,r)):return ref
        return '#'+h
    bars=lambda G:[dict(o,f=cn(o.get('f'))) for o in G if o['t']=='rect' and o.get('st')=='F' and cn(o.get('f')) in (GD,PU,KO,GR) and not (abs(o['w']-3)<1e-6 and abs(o['h']-3)<1e-6)]
    def monthly(O):
        G=region(O,'INGRESOS, GASTOS Y BENEFICIO FLOTA POR MES','LO QUE DEJA CADA COCHE')
        hz=[o for o in G if o['t']=='line' and abs(o['y1']-o['y2'])<1e-6]
        return G,bars(G),[o['s'] for o in G if o['t']=='text' and MES.match(o.get('s',''))],(hz[-1]['y1'] if hz else None)
    def percar(O):
        G=region(O,'LO QUE DEJA CADA COCHE','COCHES')
        vz=[o['x1'] for o in G if o['t']=='line' and abs(o['x1']-o['x2'])<1e-6]
        return G,bars(G),(vz[0] if vz else None)
    near=lambda a,b:a is not None and b is not None and abs(a-b)<0.01
    # 10 · Se dibujan (noviembre: los 6 meses hasta noviembre; actividad en octubre y noviembre)
    O=ops('2026-11','2026-11')
    chk(not [o for o in O if o['t']=='error'],'Gráficos: el PDF se genera sin error',[o for o in O if o['t']=='error'])
    G,B,M,z=monthly(O)
    chk(M==['jun','jul','ago','sep','oct','nov'],'Barras por mes: un solo mes muestra los 6 últimos hasta él',M)
    chk(sorted(str(b['f']).lower() for b in B)==sorted([GD,GD,GR,GR,PU,PU]),'Barras por mes: las tres series (ingresos dorado, gastos gris, beneficio flota morado) en octubre y noviembre; los meses a cero sin barra',[b['f'] for b in B])
    lg=[o['s'] for o in G if o['t']=='text' and o.get('s') in ('INGRESOS','GASTOS','BENEFICIO FLOTA')]
    chk(sorted(lg)==['BENEFICIO FLOTA','GASTOS','INGRESOS'],'Leyenda: Ingresos, Gastos y Beneficio flota',lg)
    chk(z is not None and all(near(b['y']+b['h'],z) for b in B),'Barras por mes: todas salen de la línea del 0 hacia arriba (todo positivo)')
    nov=[b for b in B if str(b['f']).lower()==GD];hs=sorted(b['h'] for b in nov)
    chk(len(hs)==2 and abs(hs[1]/hs[0]-685/480)<0.01,'Barras por mes: altura proporcional (ingresos 685 / 480 €: facturado de los propios + comisión)',hs)
    byx=sorted(B,key=lambda b:b['x']);mo=[byx[i:i+3] for i in range(0,len(byx),3)]
    chk(len(mo)==2 and all(abs(t[0]['h']-t[1]['h']-t[2]['h'])<0.01 for t in mo),'Ingresos − Gastos = Beneficio flota en cada mes (altura de las barras: 480 − 100 = 380 · 685 − 40 = 645)',[[round(b['h'],2) for b in t] for t in mo])
    G,B,zx=percar(O)
    chk(len(B)==2 and all(str(b['f']).lower()==PU and near(b['x'],zx) for b in B),'Barras por coche: Coche Uno y Furgo Dos desde el 0 hacia la derecha; Coche Tres (0 €) sin barra',[(b['x'],b['w']) for b in B])
    chk(len(B)==2 and abs(B[0]['w']/B[1]['w']-480/165)<0.01,'Barras por coche: largo proporcional a lo que deja (480 / 165 €)')
    # 11 · Negativos: un gasto de 1000 € en octubre en Coche Uno → octubre −620 € y Coche Uno −290 € en oct-nov
    J("(()=>{V.find(v=>v.id==='v1').finances.push({id:'neg1',type:'expense',amount:1000,date:'2026-10-15',category:'Reparación'});return true;})()")
    O=ops('2026-10','2026-11');G,B,M,z=monthly(O)
    neg=[b for b in B if str(b['f']).lower()==KO];pos=[b for b in B if str(b['f']).lower()!=KO]
    ys=[o['y'] for o in G if o['t']=='text' and MES.match(o.get('s',''))]
    chk(len(neg)==1 and near(neg[0]['y'],z) and all(near(b['y']+b['h'],z) for b in pos),'Escala con negativos: el beneficio de octubre (−620 €) baja de la línea del 0 en rojo; el resto sube',[(b['f'],b['y'],b['h']) for b in B])
    top=min(o['y1'] for o in G if o['t']=='line' and abs(o['y1']-o['y2'])<1e-6)
    chk(all(b['y']>=top-0.01 and b['y']+b['h']<=max(ys)-2 for b in B),'Escala con negativos: ninguna barra se sale del gráfico',[top,max(ys)])
    chk(any(o['t']=='text' and o.get('s','').startswith('-620') for o in G),'Escala con negativos: rótulo del mínimo (-620 €)',[o.get('s') for o in G if o['t']=='text'][:12])
    G,B,zx=percar(O);n1=[b for b in B if str(b['f']).lower()==KO]
    chk(len(n1)==1 and near(n1[0]['x']+n1[0]['w'],zx),'Barras por coche: el negativo (Coche Uno, −290 €) va en rojo a la izquierda del 0',[(b['x'],b['w'],b['f']) for b in B])
    J("(()=>{const v=V.find(v=>v.id==='v1');v.finances=v.finances.filter(e=>e.id!=='neg1');return true;})()")
    # 12 · Todo a cero: un solo coche sin actividad
    J("(()=>{window.__V0=V;V=V.filter(v=>v.id==='v3');_invalidateRsCache();return true;})()")
    O=ops('2026-11','2026-11');G,B,M,z=monthly(O)
    bad=[o for o in O if o['t']=='error' or 'NaN' in str(o.get('s',''))+str(o.get('y',''))+str(o.get('h',''))+str(o.get('w',''))]
    chk(not bad and len(M)==6 and not B and z is not None,'Todo a cero: se dibuja el eje y los 6 meses, sin barras ni «NaN»',bad[:3])
    chk(not any(o['t']=='text' and o.get('s')=='1 €' for o in G),'Todo a cero: sin rótulo de máximo inventado')
    # 13 · Un solo coche (Coche Uno)
    J("(()=>{V=__V0.filter(v=>v.id==='v1');_invalidateRsCache();return true;})()")
    O=ops('2026-09','2026-11');G,B,zx=percar(O);npg=max(o.get("p",1) for o in O)
    chk(not [o for o in O if o['t']=='error'] and len(B)==1 and npg==4,'Un solo coche: una barra y el informe completo',[len(B),npg])
    J("(()=>{V=__V0;_invalidateRsCache();return true;})()")
    # 14 · De 1 a 12 meses (hasta noviembre de 2026)
    res=[]
    for n in range(1,13):
        a=J("n=>_anAdd('2026-11',-(n-1))",n);O=ops(a,'2026-11');G,B,M,z=monthly(O);npg=max(o.get("p",1) for o in O)
        exp=['jun','jul','ago','sep','oct','nov'] if n==1 else J("([a,b])=>_anMonths(a,b).map(m=>_anMon(m))",[a,'2026-11'])
        ok=not [o for o in O if o['t']=='error'] and M==exp and npg==4 and len([b for b in B if str(b['f']).lower()==GD])==len(J("([a,b])=>_anMonths(a,b).filter(m=>_anStats(_anVs(),[m]).inc)",[a,'2026-11'] if n>1 else ['2026-06','2026-11']))
        res.append((n,ok,len(M),npg))
    chk(all(r[1] for r in res),'De 1 a 12 meses: sin errores, un rótulo por mes, una barra de ingresos en cada mes con ingresos y 4 páginas',[r for r in res if not r[1]])
    # 15 · Desglose de gastos: categorías = total = «Gastos» de la comparativa; generales de Negocio aparte; por coche; sin gastos; uno; negativos; déficit
    def desg(a,b):
        L=[H.N(t) for t in J("([a,b])=>__pdfText(()=>generateAnalyticsPDF(a,b),true)",[a,b])]
        i=L.index('DESGLOSE DE GASTOS') if 'DESGLOSE DE GASTOS' in L else -1
        j=L.index('DURACIÓN DE LOS ALQUILERES') if 'DURACIÓN DE LOS ALQUILERES' in L else len(L)
        seg=L[i:j] if i>=0 else []
        rows,car,gen,tot,mode=[],[],None,None,'cat'
        k=0
        while k<len(seg):
            t=seg[k]
            if t=='POR COCHE':mode='car';k+=3;continue
            if t=='TOTAL':tot=seg[k+1];k+=2;continue
            if t=='Gastos generales (Negocio)':gen=seg[k+1];k+=2;continue
            if k+2<len(seg) and seg[k+1].endswith('€') and t not in ('DESGLOSE DE GASTOS','CATEGORÍA','GASTOS','%'):
                (rows if mode=='cat' else car).append((t,seg[k+1],seg[k+2]));k+=3;continue
            k+=1
        cmp=L[L.index('Gastos')+1] if 'Gastos' in L else None
        return rows,car,gen,tot,cmp,seg
    eur=lambda x:float(x.replace('€','').replace('.','').replace(',','.').strip())
    rows,car,gen,tot,cmp,seg=desg('2026-11','2026-11')
    chk(rows==[('Combustible','40,00 €','100%')] and tot=='40,00 €' and cmp=='40,00 €','Un solo gasto: Combustible 40 € (100 %); total = «Gastos» de la comparativa (la limpieza de la furgoneta en gestión rebaja su comisión y no entra)',[rows,tot,cmp])
    chk(gen=='60,00 €' and seg.index('Gastos generales (Negocio)')>seg.index('TOTAL'),'Gastos generales de Negocio (60 €) en una fila aparte, debajo y fuera del total',gen)
    chk(not car,'Por coche: no sale si solo gasta un coche',car)
    rows,car,gen,tot,cmp,seg=desg('2026-10','2026-11')
    chk(rows==[('Mantenimiento','100,00 €','71%'),('Combustible','40,00 €','29%')] and tot=='140,00 €' and abs(sum(eur(r[1]) for r in rows)-eur(tot))<0.005,'Octubre y noviembre: Mantenimiento 100 € (71 %) y Combustible 40 € (29 %), de mayor a menor; suman el total (140 €)',[rows,tot])
    J("""(()=>{V.find(v=>v.id==='v3').finances.push({id:'it1',type:'expense',amount:30,date:'2026-11-12',category:'ITV'});
      V.find(v=>v.id==='v1').finances.push({id:'dev1',type:'expense',amount:-30,date:'2026-11-13',category:'Seguro'});return true;})()""")
    rows,car,gen,tot,cmp,seg=desg('2026-11','2026-11')
    chk(rows==[('Combustible','40,00 €','100%'),('ITV','30,00 €','75%'),('Seguro','-30,00 €','—')] or rows==[('Combustible','40,00 €','100%'),('ITV','30,00 €','75%'),('Seguro','-30,00 €','-')],'Con una devolución (Seguro −30 €): fila negativa sin % ni barra; el resto sobre el total',rows)
    chk(tot=='40,00 €' and cmp=='40,00 €' and abs(sum(eur(r[1]) for r in rows)-eur(tot))<0.005,'Con la devolución: las categorías suman el total (40 + 30 − 30 = 40) = «Gastos» de la comparativa',[tot,cmp])
    chk([c[0] for c in car]==['Coche Tres · 2222CCC','Coche Uno · 0000AAA'] and [c[1] for c in car]==['30,00 €','10,00 €'],'Por coche: Coche Tres 30 € y Coche Uno 10 € (40 − 30), de mayor a menor',car)
    J("""(()=>{['v1','v3'].forEach(id=>{const v=V.find(x=>x.id===id);v.finances=v.finances.filter(e=>e.id!=='it1'&&e.id!=='dev1');});
      V.find(v=>v.id==='v2').finances.push({id:'lp7',type:'expense',amount:700,date:'2026-11-09',category:'Limpieza'});return true;})()""")
    rows,car,gen,tot,cmp,seg=desg('2026-11','2026-11')
    chk(rows==[('Déficit asumido (gestión)','150,00 €','79%'),('Combustible','40,00 €','21%')] and tot=='190,00 €' and cmp=='190,00 €','Gestión con déficit: «Déficit asumido (gestión)» 150 € (600 facturado − 750 de gastos 5.3), no sus gastos; total 190 € = comparativa',[rows,tot,cmp])
    O=ops('2026-11','2026-11');G,B,M,z=monthly(O)
    nb=sorted([b for b in B if b['x']>max(bb['x'] for bb in B)-25],key=lambda b:b['x'])
    chk(len(nb)==3 and abs(nb[0]['h']-nb[1]['h']-nb[2]['h'])<0.01,'Con déficit: Ingresos (520) − Gastos (190) = Beneficio flota (330) en las barras de noviembre',[round(b['h'],2) for b in nb])
    J("(()=>{const v=V.find(v=>v.id==='v2');v.finances=v.finances.filter(e=>e.id!=='lp7');return true;})()")
    J("_analyticsOwnership='managed';nav('analytics')")
    rows,car,gen,tot,cmp,seg=desg('2026-11','2026-11')
    chk(gen is None and 'Sin gastos en el período.' in seg,'«Gestión» sin déficit: «Sin gastos en el período.» y sin los generales de Negocio',seg[:6])
    J("_analyticsOwnership='';nav('analytics')")
    J("(()=>{window.__V1=V;V=V.filter(v=>v.id==='v3');BF=[];_invalidateRsCache();return true;})()")
    rows,car,gen,tot,cmp,seg=desg('2026-11','2026-11')
    chk(not rows and tot is None and 'Sin gastos en el período.' in seg,'Sin gastos: «Sin gastos en el período.» sin tabla ni total',seg[:6])
    J("(()=>{V=__V1;BF=[{id:'n1',type:'expense',amount:60,date:'2026-11-02',category:'Gestoría'}];_invalidateRsCache();return true;})()")
    # 16 · Plataformas = Facturado, con un ingreso sin alquiler («Otros ingresos») y la penalización de un cancelado
    J("""(()=>{const v=V.find(v=>v.id==='v1');v.finances.push({id:'ot1',type:'income',amount:20,date:'2026-11-16',category:'Venta accesorio'});
      v.bookings.push({id:'cx',startDate:'2026-11-17',startTime:'10:00',endDate:'2026-11-19',endTime:'10:00',platform:'getaround',amount:90,clientName:'Eva Prueba',cancelled:true,
        cancellation:{by:'client',penalty:50,date:'2026-11-16'},finance:[{id:'pen_cx',type:'income',concept:'Penalización cancelación (cliente)',amount:50,date:'2026-11-16',_cancellation:true}],extras:[]});
      _invalidateRsCache();return true;})()""")
    L5=[H.N(t) for t in J("__pdfText(()=>generateAnalyticsPDF('2026-11','2026-11'),true)")]
    i=L5.index('PLATAFORMAS') if 'PLATAFORMAS' in L5 else -1
    seg=L5[i:i+40] if i>=0 else []
    P={}
    for k,t in enumerate(seg):
        if t in ('Sin app','Amovens','Getaround','Otros ingresos','TOTAL'):P[t]=seg[k+1:k+4]
    fac=L5[L5.index('Facturado')+1] if 'Facturado' in L5 else None
    chk(P.get('Sin app')==['2','720,00 €','61%'] and P.get('Amovens')==['1','400,00 €','34%'] and P.get('Getaround')==['0','50,00 €','4%'] and P.get('Otros ingresos')==['-','20,00 €','2%'],
        'Plataformas: Sin app 2 alq. y 720 € (120 + 600), Amovens 400, Getaround 50 (penalización del cancelado, sin contarlo como alquiler) y Otros ingresos 20 (sin nº de alquileres)',P)
    chk(P.get('TOTAL',[None,None])[:2]==['3','1190,00 €'] and fac=='1190,00 €','Plataformas: el total suma lo mismo que «Facturado» (1190 €)',[P.get('TOTAL'),fac])
    J("_analyticsOwnership='';setAnalyticsPeriod('mes')")
    scr=H.N(J("[...document.querySelectorAll('.an-c3>div')].find(r=>r.children[0].textContent.trim()==='Facturado').children[1].textContent.trim()"))
    chk(scr=='1190 €','Pantalla: el mismo Facturado de noviembre (1190 €)',scr)
    ctx.close();br.close()
H.fin()
