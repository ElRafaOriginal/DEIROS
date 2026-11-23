# Dinero de los alquileres cancelados (#100): «Pendiente de cobro» del coche, Clientes (lista, cuadrícula y ficha),
# «Top alquileres» y €/DÍA del informe por periodo, y «En X d» en hora local (reloj fijo a las 00:30 y a mediodía en Madrid).
# Origen: specs/d100/test_d100.py. La sección «igual que main» se ha cambiado por importes fijos esperados
# (comisión, liquidación, negocio por mes y KPI del Resumen con estos datos). Fecha fija del arnés: 20/11/2026.
# Uso: python3 tests/test_dinero_cancelados.py
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
T.bk=(id,s,e,x)=>Object.assign({id,startDate:s,startTime:'09:00',endDate:e,endTime:'09:00',platform:'sinapp',amount:100,clientName:'Ana',finance:[],paid:false},x||{});
// Cancelación igual que submitCancelBooking (marca + penalización en b.finance y copia en v.finances); el prorrateo se queda en v.finances
T.cancel=(v,b,by,pen)=>{b.cancelled=true;b.cancellation={by,penalty:pen,date:T.hoy};if(pen>0){const e={id:'pen_'+b.id,date:T.hoy,concept:'Penalización cancelación ('+(by==='client'?'cliente':'DEIROS')+')',amount:pen,type:by==='client'?'income':'expense',notes:'',_cancellation:true};b.finance.push(e);v.finances.push({...e,id:'vpen_'+b.id,bookingId:b.id,vehicleId:v.id});}};
T.add=(vid,b,pr)=>{const v=V.find(x=>x.id===vid);v.bookings.push(b);if(pr){const f=proRataEntries(b.startDate,b.endDate,b.amount,b.platform,'',b.id);f.forEach(e=>v.finances.push(e));b.financeIds=f.map(e=>e.id);}return [v,b];};
T.scen=()=>{const M=T.M,P=T.P;
  V.forEach(v=>{v.bookings=[];v.finances=[];});CL.length=0;
  T.add('v1',T.bk('a',M+'-02',M+'-06',{platform:'amovens',amount:100,clientName:'Ana'}),true);
  let [v,b]=T.add('v1',T.bk('c',M+'-10',M+'-14',{platform:'amovens',amount:500,clientName:'Bea'}),true);T.cancel(v,b,'client',50);
  [v,b]=T.add('v1',T.bk('g',M+'-15',M+'-17',{platform:'getaround',amount:600,clientName:'Ana'}),true);T.cancel(v,b,'owner',30);
  [v,b]=T.add('v1',T.bk('h',M+'-24',M+'-26',{amount:400,clientName:'Bea'}),true);T.cancel(v,b,'client',0);
  T.add('v1',T.bk('p',M+'-20',M+'-22',{amount:200,clientName:'Ana',paid:true,cobrado:true}),true);
  V.find(x=>x.id==='v1').finances.push({id:'e1',type:'expense',date:M+'-05',category:'Lavado',amount:20,description:'Lavado'});
  T.add('v2',T.bk('x',P+'-28',M+'-03',{amount:600,clientName:'Carla'}),true);
  T.add('v3',T.bk('q',P+'-10',P+'-12',{amount:150,clientName:'Dani'}),true);
  T.add('v3',T.bk('r',M+'-05',M+'-08',{amount:300,clientName:'Dani'}),true);
  [v,b]=T.add('v3',T.bk('k',M+'-12',M+'-13',{amount:200,clientName:'Dani'}),true);T.cancel(v,b,'client',40);
  v3.finances.push({id:'e2',type:'expense',date:M+'-06',category:'Limpieza',amount:25,description:'Limpieza'});
  v3.finances.push({id:'e3',type:'expense',date:M+'-07',category:'Seguro',amount:50,description:'Seguro'});
  v3.finances.push({id:'e4',type:'expense',date:P+'-11',category:'Combustible',amount:15,description:'Gasoil'});
  _invalidateRsCache();return true;};
T.chartTxt=v=>{const d=document.createElement('div');d.innerHTML=buildMonthlyChart(v);d.querySelectorAll('.fl-pd').forEach(e=>e.remove());return d.textContent.replace(/\s+/g,' ');};
T.pend=v=>{const d=document.createElement('div');d.innerHTML=buildMonthlyChart(v);const p=d.querySelector('.fl-pd');return p?[p.querySelector('b').textContent,p.querySelector('.d-meta').textContent]:null;};
// Importes fijos con este escenario: liquidación por coche, comisiones, negocio por mes y KPI del Resumen
T.money=()=>{const r={};const R2=x=>Math.round(x*100)/100,pick=o=>['tI','tE','commAmt','toOwner','deficit','mgr'].map(k=>R2(o[k]));
  r.settle=Object.fromEntries(V.map(v=>[v.id,pick(_settleTotals(v,_getVehicleAllFinances(v)))]));
  r.comm=_getManagedCommissions().map(x=>[x.v.id,x.comm,R2(x.vI),R2(x.vE),R2(x.commAmt),R2(x.toOwner)]);
  const be={};_getBizEntriesWithMgmt().forEach(e=>{const k=e.date.slice(0,7)+' '+e.type;be[k]=R2((be[k]||0)+Number(e.amount));});r.biz=be;
  r.tIncExp=Object.fromEntries(V.map(v=>[v.id,[R2(tInc(v)),R2(tExp(v))]]));
  nav('dashboard');r.dash=(document.getElementById('PC').innerHTML.replace(/&nbsp;/g,' ').match(/(INGRESOS MES|GASTOS MES|BENEFICIO[^<]*)<b[^>]*>[^<]+<\/b>/g)||[]).map(t=>t.replace(/<[^>]+>/g,' ').replace(/[  ]/g,' ').replace(/\s+/g,' ').trim());
  return r;};
true;
"""
def newctx(b,tz=H.TZ,clock=None):
    ctx=H.new_context(b,fecha=clock or H.FECHA,tz=tz)
    ctx.add_init_script("window.__DATA=%s;localStorage.setItem('wg_theme','dark');localStorage.setItem('deiros_lastBackupAt',new Date().toISOString());window.alert=m=>console.log('ALERT',m);window.confirm=()=>false;"%json.dumps(D0))
    ctx.add_init_script(FAKE)
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    return ctx,pg
def load(pg,path):
    pg.goto('file://'+os.path.abspath(path));pg.wait_for_timeout(1800);pg.evaluate(JS);pg.evaluate(H.PDFTEXT)
def run():
  with sync_playwright() as p:
    b=H.launch(p)
    ctx,pg=newctx(b);load(pg,HTML)
    T=pg.evaluate("__T");M,P,dimP=T['M'],T['P'],T['dimP']
    pg.evaluate("__T.scen()")
    F=lambda n:pg.evaluate("fmtF(%r)"%n);Fm=lambda n:pg.evaluate("fmt(%r)"%n)
    # ── 1. Pendiente de cobro (finanzas del coche) ──
    pv1=pg.evaluate("__T.pend(V.find(v=>v.id==='v1'))")
    chk(pv1 is None,f'Por cobrar del coche v1 = nada: los de Amovens (también la penalización del cancelado) los cobra la plataforma, los cancelados no suman su precio, la penalización que paga DEIROS no es cobro y el cobrado no cuenta (hay {pv1})')
    pv3=pg.evaluate("__T.pend(V.find(v=>v.id==='v3'))")
    chk(pv3==[F(490),'3 alquileres con cobro pendiente'],f'Por cobrar v3 (en gestión) = 150 + 300 + penalización 40 del cancelado (no su precio de 200) = {F(490)} en 3 (hay {pv3})')
    pg.evaluate("(()=>{const b=V.find(v=>v.id==='v3').bookings.find(b=>b.id==='k');b.paid=b.cobrado=true;})()")
    pv3=pg.evaluate("__T.pend(V.find(v=>v.id==='v3'))")
    chk(pv3==[F(450),'2 alquileres con cobro pendiente'],f'Por cobrar v3 tras marcar cobrada la penalización = {F(450)} en 2 (hay {pv3})')
    pg.evaluate("(()=>{const b=V.find(v=>v.id==='v3').bookings.find(b=>b.id==='k');b.paid=b.cobrado=false;})()")
    # ── 2. Clientes: lista, cuadrícula y ficha ──
    exp={'Ana':(270,2),'Bea':(50,0),'Carla':(600,1),'Dani':(490,2)}
    pg.evaluate("_searchClients='';_clientsMode='extended';nav('clients')");pg.wait_for_timeout(300)
    rows=dict(pg.evaluate("[...document.querySelectorAll('#clients-results .cl-r')].map(r=>[r.querySelector('.t').textContent.trim(),[...r.querySelector('.r').children].map(x=>x.textContent.trim()).join(' ')])"))
    for n,(t,k) in exp.items():
        w=f"{Fm(t)} {k} alquiler{'es' if k!=1 else ''}"
        chk(rows.get(n)==w,f'Clientes, lista: {n} = «{w}» (hay «{rows.get(n)}»)')
    pg.evaluate("_clientsMode='grid';renderClientsBody()")
    gr=dict(pg.evaluate("[...document.querySelectorAll('#clients-results .cl-gc')].map(r=>[r.querySelector('.cl-gn').textContent.trim(),[...r.querySelectorAll('.cl-gs b')].map(x=>x.textContent)])"))
    chk(all(gr.get(n)==[Fm(t),str(k)] for n,(t,k) in exp.items()),f'Clientes, cuadrícula: Total y Alq. sin cancelados ({gr})')
    pg.evaluate("_clientsMode='extended';_clientDetail=CL.find(c=>c.name==='Ana').id;renderClientDetail(document.getElementById('PC'))");pg.wait_for_timeout(300)
    fd=pg.evaluate("""(()=>{const e=document.getElementById('PC');return{tot:e.querySelector('.cl-c .d-tot .d-n').textContent,p:e.querySelector('.cl-c .d-tot p').textContent,
      kpi:[...e.querySelectorAll('.cl-k b')].map(x=>x.textContent),hist:[...e.querySelectorAll('.cl-h')].map(r=>[r.querySelector('.s').textContent,r.querySelector('.cl-in').textContent])};})()""")
    chk(fd['tot']==Fm(270).replace('.','') and fd['p']=='2 alquileres · IVA incluido',f'Ficha de Ana: Total facturado {Fm(270)} (100 + 200 − 30 de penalización que paga DEIROS), «2 alquileres» (hay {fd["tot"]} / {fd["p"]})')
    chk(fd['kpi'][:2]==['2',Fm(135)],f'Ficha de Ana: KPI 2 alquileres y ticket medio {Fm(135)} (hay {fd["kpi"]})')
    hg=[h for h in fd['hist'] if h[0].endswith('Cancelado')]
    chk(len(hg)==1 and hg[0][1]==Fm(-30) and len(fd['hist'])==3,f'Ficha de Ana, historial: el cancelado sigue en la lista, marcado «Cancelado» y con su penalización {Fm(-30)} (hay {fd["hist"]})')
    # ── 3. Informe por periodo: «Top alquileres» sin cancelados ──
    def biz(a,bb):
        L=pg.evaluate("__pdfText(()=>dlBizReport(%s,%s,'Prueba'),true)"%(json.dumps(a),json.dumps(bb)))
        i=L.index('Top alquileres del período') if 'Top alquileres del período' in L else -1;j=L.index('Clientes del período')
        top=[t for t in L[i+1:j] if t in ('Ana','Bea','Carla','Dani')] if i>=0 else []
        rows={}
        for n,t in enumerate(L):
            if t=='€/DÍA' and L[n-2]=='DÍAS' and L[n-10]=='ING':
                rows[L[n-13]]=(L[n-11],L[n-3],L[n-1])  # nombre → ING, DÍAS, €/DÍA
        return L,top,rows
    global VN
    VN=dict(pg.evaluate("V.map(v=>[v.id,v.name])"))
    fE=lambda n:pg.evaluate("new Intl.NumberFormat('es-ES',{style:'currency',currency:'EUR',minimumFractionDigits:2,maximumFractionDigits:2}).format(%r)"%n)
    L,top,rows=biz(M,M)
    chk(sorted(top)==['Ana','Ana','Dani'],f'Informe del mes: «Top alquileres» = los 3 no cancelados (Ana 100 y 200, Dani 300); ni Bea ni los cancelados (hay {top})')
    # ── 4. €/DÍA por vehículo: ingresos del periodo (prorrateo de siempre) / días ocupados del periodo; ING sin cambios ──
    pM=600-600*(dimP-27)/6;pP=600*(dimP-27)/6
    e={VN['v1']:(fE(320),'8d',fE(350/8)+'/d'),VN['v2']:(fE(0),'3d',fE(pM/3)+'/d'),VN['v3']:(fE(340),'4d',fE(340/4)+'/d')}
    chk(rows==e,f'Informe del mes, por vehículo (ING, DÍAS, €/DÍA): v1 350/8 (100+200+penalización 50), v2 {pM:.2f}/3 (su parte del 28→03), v3 340/4; ING igual que antes ({rows} / esperado {e})')
    L,top,rows=biz(P,P)
    e={VN['v2']:(fE(600),f'{dimP-27}d',fE(100)+'/d'),VN['v3']:(fE(150),'3d',fE(50)+'/d')}
    chk(rows==e,f'Informe del mes anterior: v2 {pP:.2f}/{dimP-27} d = 100 €/d (no 600 entero entre sus días), v3 150/3 ({rows} / esperado {e})')
    # ── 5. Importes fijos (antes: «igual que main») ──
    r=pg.evaluate("__T.money()")
    # v3 en gestión (30 %): octubre 150 − 15 de combustible (regla antigua: comisión 45, propietario 90);
    # noviembre 300 + 40 de penalización − 25 de limpieza (5.3; el seguro es 5.2): comisión (340 − 25) × 30 % = 94,5, propietario 220,5
    chk(r['settle']['v3']==[490,40,139.5,310.5,0,139.5],'Liquidación v3 (oct + nov): ingresos 490, gastos 5.3 40, comisión 139,50, al propietario 310,50, sin déficit',r['settle']['v3'])
    chk(r['comm']==[['v3',0.3,490,40,139.5,310.5]],'Comisiones de coches en gestión: solo v3, 139,50 y 310,50 al propietario',r['comm'])
    chk(r['tIncExp']=={'v1':[350,50],'v2':[600,0],'v3':[490,40]},'Ingresos y gastos por coche sin el precio de los cancelados (v1 100 + 200 + penalización 50; v2 600; v3 150 + 300 + 40)',r['tIncExp'])
    chk(r['biz']=={'2026-11 income':644.5,'2026-11 expense':50,'2026-10 income':445},'Negocio por mes (con la parte del gestor de v3): nov 644,50 / 50, oct 445',r['biz'])
    chk(r['dash']==['INGRESOS MES 890,00 €','GASTOS MES 75,00 €','BENEFICIO 2026 1350,00 €','BENEFICIO 765,00 €'],'KPI del Resumen: ingresos del mes 890, gastos 75, beneficio 765 (año 1.350)',r['dash'])
    ctx.close()
    # ── 6. «En X d» en hora local: 00:30 del 20/11/2026 en Madrid (23:30 UTC del 19) y control a mediodía ──
    def clockcase(t):
        c,q=newctx(b,'Europe/Madrid',t);load(q,HTML)
        r=q.evaluate("""(()=>{V.forEach(v=>{v.bookings=[];v.finances=[];v.itv_date='';v.insurance_date='';v.maint_date='';});
          const v1=V.find(v=>v.id==='v1');v1.itv_date='2026-11-30';v1.maint_date='2026-11-30';
          __T.add('v3',__T.bk('n','2026-11-30','2026-12-02'),false);__T.add('v2',__T.bk('m','2026-11-18','2026-11-23'),false);_invalidateRsCache();
          const o={hoy:todayStr(),alert:getAlerts().filter(a=>a.vid==='v1').map(a=>a.label+':'+a.days)};
          _vListMode='compact';nav('vehicles');o.flota=[...document.querySelectorAll('#flota-results .fl-r')].map(r=>(r.querySelector('.vr-c .chip')||{}).textContent||'').filter(t=>t.startsWith('En '));
          nav('rentals');o.rent=[...document.querySelectorAll('#PC .chip')].map(x=>x.textContent.trim()).filter(t=>/^(En |Termina|En curso)/.test(t)||t.includes('En curso'));
          const d=document.createElement('div');d.innerHTML=renderInfo(v1);o.info=(d.textContent.match(/(Vence en \\d+d|En \\d+ d[^ ]*|En \\d+d)/g)||[]);return o;})()""")
        c.close();return r
    r=clockcase('2026-11-20T00:30:00+01:00')
    chk(r['hoy']=='2026-11-20','Reloj: 00:30 del 20/11 en Madrid → hoy 2026-11-20')
    chk(r['alert']==['ITV:10','Revisión:10'],f'00:30 Madrid, Alertas: ITV y Revisión del 30/11 en 10 d, no 11 (hay {r["alert"]})')
    chk(r['flota']==['En 10d'],f'00:30 Madrid, Flota compacta: alquiler del 30/11 «En 10d» (hay {r["flota"]})')
    chk('En 10d' in r['rent'] and any('3d' in t for t in r['rent'] if 'curso' in t),f'00:30 Madrid, Alquileres: Próximos «En 10d» y el que acaba el 23/11 «En curso · 3d» (hay {r["rent"]})')
    chk('Vence en 10d' in r['info'],f'00:30 Madrid, ficha del coche: ITV «Vence en 10d» (hay {r["info"]})')
    r2=clockcase('2026-11-20T12:00:00+01:00')
    chk(r2['alert']==['ITV:10','Revisión:10'] and r2['flota']==['En 10d'] and 'En 10d' in r2['rent'] and 'Vence en 10d' in r2['info'],f'Control a mediodía: los mismos 10 d que de día ya salían ({r2})')
    b.close()
run()
H.fin()
