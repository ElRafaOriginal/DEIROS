# Dinero · cifras sin alquileres cancelados (#94): Resumen (totales, del mes y del año, rentabilidad por plataforma con la
# penalización), «Revisión» en Alertas, estado en Flota, avisos de devolución, asistente de contrato, propietario, Excel,
# informe de negocio (PDF) y días ocupados por mes (Comparativa e informe por periodo); también a 1280 px.
# Origen: specs/bloqueA/test_bloqueA.py (no comparaba con main). Fecha fija del arnés: 20/11/2026.
# Uso: python3 tests/test_cifras_cancelados.py
import sys,os,json,re,datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
HTML=H.INDEX
route,D0,FAKE=H.route,H.datos(),H.FAKE
g={'P':"document.getElementById('mainPage')",'D':D0,'route':route,'FAKE':FAKE}
from playwright.sync_api import sync_playwright
errs=H.ERRS;chk=H.chk
JS=r"""
window.__T={};const now=new Date(),Y=now.getFullYear(),Mo=now.getMonth();
const ym=(y,m)=>{const d=new Date(y,m,1);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0');};
const T=__T;T.M=ym(Y,Mo);T.P=ym(Y,Mo-1);T.hoy=todayStr();T.dimP=new Date(Y,Mo,0).getDate();
BF=[];V=V.filter(v=>['v1','v2','v3'].includes(v.id));
V.forEach(v=>{v.archived=false;v.bookings=[];v.finances=[];v.vtype='own';v.ownerId=null;v.itv_date='';v.insurance_date='';v.maint_date='';v.maint_km='';});
const v3=V.find(v=>v.id==='v3');v3.vtype='managed';v3.ownerId='o1';v3.commission=30;
T.bk=(id,s,e,x)=>Object.assign({id,startDate:s,startTime:'09:00',endDate:e,endTime:'09:00',platform:'sinapp',amount:100,clientName:'Ana',finance:[]},x||{});
// Cancelación igual que submitCancelBooking (marca + penalización en b.finance y copia en v.finances); el prorrateo del alquiler se queda en v.finances
T.cancel=(v,b,by,pen)=>{b.cancelled=true;b.cancellation={by,penalty:pen,date:T.hoy};if(pen>0){const e={id:'pen_'+b.id,date:T.hoy,concept:'Penalización cancelación (cliente)',amount:pen,type:by==='client'?'income':'expense',notes:'',_cancellation:true};b.finance.push(e);v.finances.push({...e,id:'vpen_'+b.id,bookingId:b.id,vehicleId:v.id});}};
T.add=(vid,b,pr)=>{const v=V.find(x=>x.id===vid);v.bookings.push(b);if(pr)proRataEntries(b.startDate,b.endDate,b.amount,b.platform,'',b.id).forEach(e=>v.finances.push(e));return [v,b];};
T.scenario1=()=>{
  V.forEach(v=>{v.bookings=[];v.finances=[];});
  T.add('v1',T.bk('a',T.M+'-02',T.M+'-06',{platform:'amovens',amount:100,clientName:'Ana'}),true);
  const [v1,c]=T.add('v1',T.bk('c',T.M+'-10',T.M+'-14',{platform:'amovens',amount:500,clientName:'Bea'}),true);T.cancel(v1,c,'client',50);
  const [v2,d]=T.add('v2',T.bk('d',addDays(T.hoy,-2),addDays(T.hoy,1),{platform:'getaround',amount:300,clientName:'Bea'}),false);T.cancel(v2,d,'owner',0);
  const [v3a,e]=T.add('v3',T.bk('e',addDays(T.hoy,2),addDays(T.hoy,4),{clientName:'Bea'}),false);T.cancel(v3a,e,'client',0);
  T.add('v3',T.bk('f',addDays(T.hoy,10),addDays(T.hoy,12),{amount:200,clientName:'Ana'}),false);
  V.find(v=>v.id==='v1').maint_date=addDays(T.hoy,10);V.find(v=>v.id==='v1').itv_date=addDays(T.hoy,20);
  V.find(v=>v.id==='v2').maint_date=addDays(T.hoy,90);
  _invalidateRsCache();
  return V.map(v=>v.bookings.map(b=>[b.id,b.startDate,b.endDate,!!b.cancelled])).flat();
};
true;
"""
def run():
  with sync_playwright() as p:
    b=H.launch(p)
    ctx=H.new_context(b,viewport={'width':390,'height':844});ctx.route('**/*',route)
    ctx.add_init_script("window.__DATA=%s;localStorage.setItem('wg_theme','dark');localStorage.setItem('deiros_lastBackupAt',new Date().toISOString());window.alert=m=>console.log('ALERT',m);window.confirm=()=>false;"%json.dumps(D0))
    ctx.add_init_script(FAKE)
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(HTML));pg.wait_for_timeout(1800)
    pg.evaluate(JS);pg.evaluate(H.PDFTEXT)
    T=pg.evaluate("__T");M,P,hoy,dimP=T['M'],T['P'],T['hoy'],T['dimP']
    bks=pg.evaluate("__T.scenario1()")
    live=[x for x in bks if not x[3]]
    expTot=len(live);expMes=sum(1 for x in live if x[1][:7]==M);expYr=sum(1 for x in live if x[1][:4]==hoy[:4])
    # ── 1. Resumen (móvil) ──
    pg.evaluate("_dashPlatPeriod='monthly';nav('dashboard')");pg.wait_for_timeout(400)
    h=pg.evaluate("document.getElementById('PC').innerHTML").replace('&nbsp;','\xa0')
    # (quitado: «ALQ. TOTALES» ya no está en el Resumen; el total sin cancelados se comprueba en el panel de Flota a 1280 px)
    m=re.search(r'(\d+) alq\. este mes',h);n=int(m.group(1)) if m else -1
    chk(n==expMes,f'Resumen «alq. este mes» = {expMes} (hay {n})')
    m=re.search(r'ALQUILERES \d{4}<b>(\d+)</b>',h);n=int(m.group(1)) if m else -1
    chk(n==expYr,f'Resumen «ALQUILERES {hoy[:4]}» = {expYr} (hay {n})')
    f0,f100,f150=pg.evaluate("[fmt(0),fmt(100),fmt(150)]")
    plat=lambda h,n:(lambda m:m.groups() if m else None)(re.search(r'<span class="t">'+n+r'<span class="q">(\d+) alq\.</span></span><b>([^<]+)</b>',h))
    a=plat(h,'Amovens')
    chk(a==('1',f150),f'Resumen móvil, rentabilidad Amovens (Mes) = 1 alq. (sin el cancelado) y {f150} (alquiler 100 + penalización 50, como el PDF) (hay {a})')
    a=plat(h,'Getaround')
    chk(a==('0',f0),f'Resumen móvil, Getaround (Mes) = 0 alq. y {f0}: cancelado por el propietario sin penalización no suma su precio (hay {a})')
    pg.evaluate("_dashPlatPeriod='annual';renderDash(document.getElementById('PC'))");pg.wait_for_timeout(300)
    a=plat(pg.evaluate("document.getElementById('PC').innerHTML").replace('&nbsp;','\xa0'),'Amovens')
    chk(a==('1',f150),f'Resumen móvil, Amovens (Año) = 1 alq. y {f150} (hay {a})')
    pg.evaluate("_dashPlatPeriod='monthly';renderDash(document.getElementById('PC'))");pg.wait_for_timeout(300)
    m=re.search(r'INGRESOS MES<b class="lg">([^<]+)</b>',h)
    chk(bool(m) and m.group(1)==f150,f'Dinero intacto: INGRESOS MES = alquiler 100 + penalización 50 = {f150} (hay {m.group(1) if m else None})')
    # ── 2. Alertas: próxima revisión ──
    al=pg.evaluate("getAlerts().map(a=>[a.vid,a.label,a.days,a.urgent,a.expired,a.ico])")
    rv=[a for a in al if a[1]=='Revisión']
    chk(len(rv)==1 and rv[0][0]=='v1' and rv[0][2] in (10,11) and rv[0][3] and not rv[0][4] and rv[0][5]=='wrench',f'Alertas: «Revisión» del v1 en 10 d, urgente (≤30 d), icono llave; la de 90 d no sale ({rv})')
    chk(any(a[1]=='ITV' and a[0]=='v1' for a in al),'Alertas: la ITV sigue saliendo igual')
    sec=re.search(r'<h2>Alertas</h2>.*?</section>',h,re.S)
    chk(bool(sec) and 'Revisión' in sec.group(0),'Resumen móvil: la sección Alertas muestra «Revisión»')
    pg.evaluate("openNotifSettings()");pg.wait_for_timeout(300)
    chk('Revisión' in pg.evaluate("document.getElementById('SC').innerHTML"),'Hoja de Notificaciones: lista «Revisión»')
    pg.evaluate("closeSheet()")
    # ── 3. Flota compacta (móvil): estado sin cancelados ──
    pg.evaluate("_vListMode='compact';nav('vehicles')");pg.wait_for_timeout(400)
    rows=pg.evaluate("[...document.querySelectorAll('#flota-results .fl-r')].map(r=>[r.querySelector('.fl-n').textContent,r.querySelector('.vr-c').textContent])")
    nm=dict(pg.evaluate("V.map(v=>[v.id,v.name])"));st={n:s for n,s in rows}
    dU=pg.evaluate("Math.ceil((new Date(addDays(__T.hoy,10))-new Date())/864e5)")
    chk(st.get(nm['v2'],'').startswith('Disponible'),f'Flota: v2 (solo un cancelado que cubre hoy) = Disponible (hay «{st.get(nm["v2"])}»)')
    chk(st.get(nm['v3'],'').startswith(f'En {dU}d'),f'Flota: v3 (cancelado en 2 d + real en 10 d) = «En {dU}d» (hay «{st.get(nm["v3"])}»)')
    # ── 4. Aviso de devoluciones de mañana sin cancelados ──
    expRet=sum(1 for x in live if x[2]==pg.evaluate("addDays(todayStr(),1)"))
    nret=pg.evaluate("(()=>{const L=[];const s=showNotif;showNotif=(t,b)=>L.push(b);const d=Object.getOwnPropertyDescriptor(Notification,'permission');Object.defineProperty(Notification,'permission',{get:()=>'granted',configurable:true});try{checkReturnNotifs();}finally{showNotif=s;if(d)Object.defineProperty(Notification,'permission',d);else delete Notification.permission;}return L.length;})()")
    chk(nret==(1 if expRet else 0),f'Aviso «Devoluciones mañana»: el cancelado de v2 que acaba mañana no avisa ({nret} avisos, esperado {1 if expRet else 0})')
    # ── 5. Asistente de contrato, paso 1 ──
    pg.evaluate("openContractWizard()");pg.wait_for_timeout(300)
    pk=pg.evaluate("[...document.querySelectorAll('#SC .pk')].map(e=>e.textContent)")
    r2=[t for t in pk if nm['v2'] in t]
    chk(bool(r2) and 'En alquiler' not in r2[0],f'Contrato paso 1: v2 no sale «En alquiler» por un cancelado ({r2[0].strip()[:80] if r2 else None})')
    pg.evaluate("closeSheet()")
    # ── 6. Ficha del propietario o1 (v3: 1 real + 1 cancelado) ──
    pg.evaluate("openOwnerProfile('o1')");pg.wait_for_timeout(400)
    m=re.search(r'(\d+) alquiler(?:es)? ·',pg.evaluate("document.getElementById('PC').textContent"))
    chk(bool(m) and m.group(1)=='1',f'Propietario: «1 alquiler» sin el cancelado (hay {m.group(0) if m else None})')
    # ── 7. Excel del coche v1: «Alquileres totales» (XLSX simulado si la librería no carga sin red) ──
    xr=pg.evaluate("(async()=>{await ensureLib('xlsx');const R=[];const a=XLSX.utils.aoa_to_sheet,w=XLSX.writeFile;XLSX.utils.aoa_to_sheet=function(r){R.push(r);return a.apply(this,arguments)};XLSX.writeFile=()=>{};try{await exportExcel('v1');}finally{XLSX.utils.aoa_to_sheet=a;XLSX.writeFile=w;}return R.flat().filter(r=>r[0]==='Alquileres totales');})()")
    chk(xr==[['Alquileres totales',1]],f'Excel v1 «Alquileres totales» = 1 (hay {xr})')
    # ── 8. Informe de negocio del mes (PDF) ──
    L=pg.evaluate("__pdfText(()=>dlBizReport(__T.M,__T.M,'Prueba'),true)")
    pl=[i for i,t in enumerate(L) if 'alq.  ·  Ticket' in t]
    am=L[pl[0]] if pl else ''
    chk(am.startswith('1 alq.') and '150' in am and '150' in L[pl[0]-1],f'Informe: Amovens «1 alq.», importe con la penalización 150 € y ticket 150 € (hay «{L[pl[0]-1] if pl else ""}» / «{am}»)')
    expCl=len({('Ana' if x[0] in 'af' else 'Bea') for x in live if x[1][:7]==M})
    cl=[t for t in L if re.match(r'\d+ clientes? únicos?$',t)]
    chk(cl==[f'{expCl} cliente'+('s únicos' if expCl!=1 else ' único')],f'Informe: clientes únicos sin los de cancelados = {expCl} (hay {cl})')
    chk('0 alquileres' in L,'Informe, clientes: Bea (solo cancelado con penalización) sale con «0 alquileres» y su importe')
    # ── 9. Comparativa: días ocupados en su mes (incluido el de devolución) ──
    cmp=lambda:pg.evaluate("""(()=>{nav('analytics');document.getElementById('cmpA').value=__T.P;document.getElementById('cmpB').value=__T.M;runComparison();
      const o={};document.querySelectorAll('#cmpResults .an-cmp>div:not(.h)').forEach(r=>{const c=r.children;o[c[0].textContent.trim()]=[c[1].textContent.trim(),c[2].textContent.trim()];});return o;})()""")
    pg.evaluate("""(()=>{V.forEach(v=>{v.bookings=[];v.finances=[];});__T.add('v2',__T.bk('x',__T.P+'-28',__T.M+'-03',{amount:100}),true);_invalidateRsCache();})()""")
    o=cmp()
    chk(o.get('Días ocupados')==[str(dimP-27),'3'],f'Comparativa, ejemplo de Rafael 28→03: A={dimP-27} (28→fin de mes; 4 si el mes tiene 31 días), B=3 (1, 2 y 3) (hay {o.get("Días ocupados")})')
    chk('Días facturados' not in o,'Comparativa: el rótulo pasa a «Días ocupados»')
    pg.evaluate("""(()=>{
      __T.add('v1',__T.bk('y',__T.M+'-10',__T.M+'-14',{amount:100,clientName:'Bea'}),true);
      __T.add('v1',__T.bk('y2',__T.M+'-14',__T.M+'-16',{amount:100,clientName:'Bea'}),true);
      const [v,z]=__T.add('v2',__T.bk('z',__T.M+'-15',__T.M+'-20',{amount:100}),true);__T.cancel(v,z,'owner',0);
      __T.add('v3',__T.bk('w',__T.M+'-05',__T.M+'-05',{amount:50}),false);_invalidateRsCache();})()""")
    o=cmp()
    eA,eB=dimP-27,3+7+1
    chk(o.get('Días ocupados')==[str(eA),str(eB)],f'Comparativa «Días ocupados»: A={eA}, B={eB} (3 del cruce en v2 + 7 en v1 (10→14 y 14→16, el 14 una vez) + 1 de un alquiler de un día; sin el cancelado) (hay {o.get("Días ocupados")})')
    chk(o.get('Alquileres')==['1','3'],f'Comparativa «Alquileres» por mes de inicio sin cancelados = 1 / 3 (hay {o.get("Alquileres")})')
    # ── 9b. Informe por periodo (PDF): mismos días ocupados repartidos por mes; KPI = suma de la tabla por vehículo ──
    def biz(a,b):
        L=pg.evaluate("__pdfText(()=>dlBizReport(%s,%s,'Prueba'),true)"%(json.dumps(a),json.dumps(b)))
        i=L.index('DÍAS OCUPADOS') if 'DÍAS OCUPADOS' in L else -1
        k=int(L[i+1]) if i>=0 and L[i+1].isdigit() else None
        rows={}
        for j,t in enumerate(L):
            if t=='DÍAS' and j>0 and L[j-1].endswith('d'):
                nmj=[x for x in L[max(0,j-14):j] if x in nm.values()]
                rows[nmj[-1] if nmj else '?']=int(L[j-1][:-1])
        return L,k,rows
    L,k,rows=biz(M,M)
    chk(k==eB,f'Informe del mes B: KPI «DÍAS OCUPADOS» = {eB} (hay {k})')
    chk('DÍAS FACTURADOS' not in L,'Informe: el rótulo del KPI pasa a «DÍAS OCUPADOS»')
    chk(rows=={nm['v1']:7,nm['v2']:3,nm['v3']:1} and sum(rows.values())==k,f'Informe del mes B: días por vehículo v1 7, v2 3 (solo el cruce, empezó el mes anterior), v3 1; suman el KPI (hay {rows})')
    chk(any(t=='%.1fd por alquiler'%(eB/3) for t in L),f'Informe del mes B: «{eB/3:.1f}d por alquiler» (3 alquileres iniciados en el mes) ({[t for t in L if "por alquiler" in t]})')
    L,k,rows=biz(P,P)
    chk(k==eA and rows=={nm['v2']:eA},f'Informe del mes A: {eA} días, todos de v2 (hay {k} / {rows})')
    L,k,rows=biz(P,M)
    chk(k==eA+eB and sum(rows.values())==k,f'Informe A→B: {eA+eB} días = A + B, y la tabla por vehículo suma lo mismo (hay {k} / {rows})')
    # ── 10. Escritorio (1280 px): rentabilidad por plataforma, panel de Flota y tabla compacta ──
    pg.evaluate("__T.scenario1()");pg.set_viewport_size({'width':1280,'height':900});pg.wait_for_timeout(300)
    pg.evaluate("nav('dashboard')");pg.wait_for_timeout(400)
    am=pg.evaluate("(()=>{const s=[...document.querySelectorAll('#PC .sec')].find(e=>e.textContent.includes('RENTABILIDAD POR PLATAFORMA'));if(!s)return '';return [...s.nextElementSibling.children].map(c=>c.innerText).find(t=>t.includes('Amovens'))||'';})()")
    chk('1 alquileres' in am and f150 in am,f'Resumen escritorio: Amovens «1 alquileres» y {f150} (alquiler + penalización, como el PDF) ({am.replace(chr(10)," | ")})')
    pg.evaluate("_vListMode='compact';nav('dashboard');nav('vehicles')");pg.wait_for_timeout(500)
    rp=pg.evaluate("(document.getElementById('flota-right-panel')||{}).innerText||''")
    m=re.search(r'Alquileres\s+(\d+)',rp)
    chk(bool(m) and int(m.group(1))==expTot,f'Flota escritorio, panel «Alquileres» = {expTot} (hay {m.group(1) if m else None})')
    tr=pg.evaluate("[...document.querySelectorAll('#flota-results tr.ftr')].map(r=>r.innerText)")
    t2=[t for t in tr if nm['v2'] in t]
    chk(bool(t2) and 'disponible' in t2[0].lower() and 'alquilado' not in t2[0].lower(),f'Flota escritorio, tabla: v2 Disponible ({t2[0].replace(chr(10)," | ")[:80] if t2 else None})')
    b.close()
run()
H.fin()
