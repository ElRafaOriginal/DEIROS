# Dinero · comisión del gestor (#90) y liquidación al propietario, con las funciones REALES de la app en el navegador.
# Desde COMM_RULE_FROM ('2026-11', incluido) y con propietario: max(0, facturado − gastos 5.3) × %. Antes: facturado × %.
# Origen: specs/com90/test_com90.js (casos 1–9 y A7). Se ha quitado la comparación «igual que main» (sección 10):
# esos casos ya están cubiertos con valores fijos (octubre = regla antigua, sin propietario = regla antigua).
# Añadido: el PDF de liquidación del propietario (dlOwnerReport) con importes fijos en octubre y noviembre de 2026.
# Uso: python3 tests/test_comision.py
import sys,os,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
JS=r"""(()=>{const R=[];const near=(a,b)=>Math.abs(a-b)<1e-9;
function ok(label,c){R.push([!!c,label,'']);}
function eq(label,got,exp){const bad=Object.keys(exp).filter(k=>typeof exp[k]==='boolean'?got[k]!==exp[k]:!near(got[k],exp[k]));
  R.push([!bad.length,label,bad.map(k=>k+'='+got[k]+' (esperado '+exp[k]+')').join(', ')]);}
const inc=(d,a,c='Alquiler')=>({type:'income',date:d,amount:a,category:c});
const exp=(d,a,c)=>({type:'expense',date:d,amount:a,category:c});
const car={vtype:'managed',ownerId:'o1',commission:30};
const noOwner={vtype:'managed',ownerId:null,commission:30};
const S=(v,f,m)=>_ownerSettle(v,f,m),T=(v,f)=>_settleTotals(v,f);
const mes=(ym,a,g1,g2)=>[inc(ym+'-03',a),exp(ym+'-10',g1,'Limpieza'),exp(ym+'-20',g2,'Plataforma')];
ok("COMM_RULE_FROM = '2026-11'",COMM_RULE_FROM==='2026-11');
const oct=mes('2026-10',1000,50,50);
eq('oct-2026 1000/100/30% → 300/600 (regla antigua)',S(car,oct),{tI:1000,tE:100,base:1000,net53:false,commAmt:300,toOwner:600,deficit:0,mgr:300});
const nov=mes('2026-11',1000,50,50);
eq('nov-2026 1000/100/30% → 270/630 (regla nueva)',S(car,nov),{tI:1000,tE:100,base:900,net53:true,commAmt:270,toOwner:630,deficit:0,mgr:270});
eq('nov-2026 con ym explícito',S(car,nov,'2026-11'),{commAmt:270,toOwner:630});
eq('mes explícito manda sobre las fechas (ym=2026-10)',S(car,nov,'2026-10'),{net53:false,commAmt:300,toOwner:600});
eq('diciembre 2027 → regla nueva',S(car,mes('2027-12',1000,50,50)),{commAmt:270,toOwner:630});
eq('septiembre 2025 → regla antigua',S(car,mes('2025-09',1000,50,50)),{commAmt:300,toOwner:600});
eq('marzo 2025 700/120 → regla antigua: 210/370',S(car,mes('2025-03',700,120,0)),{commAmt:210,toOwner:370,deficit:0});
const malN=[inc('2026-11-02',50),exp('2026-11-05',80,'Combustible')];
eq('nov mes malo 50/80 → comisión 0, propietario 0, déficit 30, mgr −30',S(car,malN),{base:0,commAmt:0,toOwner:0,deficit:30,mgr:-30});
const malO=[inc('2026-10-02',50),exp('2026-10-05',80,'Combustible')];
eq('oct mes malo 50/80 → comisión 15, propietario 0, déficit 45, mgr −30',S(car,malO),{commAmt:15,toOwner:0,deficit:45,mgr:-30});
eq('nov sin movimientos → 0',S(car,[],'2026-11'),{commAmt:0,toOwner:0,deficit:0,mgr:0});
eq('nov sin facturación con 40 de parking → comisión 0, déficit 40',S(car,[exp('2026-11-01',40,'Parking')]),{commAmt:0,toOwner:0,deficit:40,mgr:-40});
const s52=ym=>[inc(ym+'-01',1000),exp(ym+'-02',200,'Seguro'),exp(ym+'-03',60,'Multa'),exp(ym+'-04',90,'Mantenimiento'),exp(ym+'-05',30,'Reparación')];
eq('nov solo 5.2 y multa → 300/700 (los 5.2 los paga el propietario aparte)',S(car,s52('2026-11')),{tE:0,paid:320,other:60,commAmt:300,toOwner:700,mgr:300});
eq('oct solo 5.2 y multa → 300/700',S(car,s52('2026-10')),{tE:0,paid:320,other:60,commAmt:300,toOwner:700,mgr:300});
const all=[...oct,...nov,inc('2026-12-02',50),exp('2026-12-05',80,'Combustible')];
eq('oct+nov+dic: comisión 570, propietario 1230, déficit 30, mgr 540',T(car,all),{tI:2050,tE:280,commAmt:570,toOwner:1230,deficit:30,mgr:540});
eq('oct malo + nov malo: comisión 15, déficit 75, mgr −60',T(car,[...malO,...malN]),{commAmt:15,toOwner:0,deficit:75,mgr:-60});
eq('nov comisión 0 %',S({...car,commission:0},nov),{commAmt:0,toOwner:900,mgr:0});
eq('nov comisión vacía → 30 %',S({...car,commission:''},nov),{comm:30,commAmt:270,toOwner:630});
eq('nov comisión 100 %',S({...car,commission:100},nov),{commAmt:900,toOwner:0,deficit:0,mgr:900});
eq('sin propietario nov (datos antiguos): 30 % de 1000',S(noOwner,nov),{base:1000,net53:false,commAmt:300,toOwner:600,deficit:0,mgr:300});
eq('sin propietario nov mes malo: regla antigua, sin déficit',S(noOwner,malN),{commAmt:15,deficit:0});
eq('nov categorías normalizadas (suscripcion, LAVADO = 5.3)',S(car,[inc('2026-11-01',200),exp('2026-11-02',10,'suscripcion'),exp('2026-11-03',10,'LAVADO')]),{tE:20,commAmt:54,toOwner:126});
{const base=S(car,nov);
 ['Franquicia','Daño cliente'].forEach(c=>{const r=S(car,[...nov,exp('2026-11-15',80,c)]);
  eq(c+' nov: no cambia toOwner ni commAmt, cuenta en other',r,{commAmt:base.commAmt,toOwner:base.toOwner,tE:base.tE,other:base.other+80,paid:base.paid});
  const b2=S(car,oct),r2=S(car,[...oct,exp('2026-10-15',80,c)]);
  eq(c+' oct: igual',r2,{commAmt:b2.commAmt,toOwner:b2.toOwner,other:b2.other+80});});
 const rp=S(car,[...nov,exp('2026-11-15',80,'Reparación')]);
 eq('Reparación nov: en paid (5.2), no se descuenta',rp,{commAmt:base.commAmt,toOwner:base.toOwner,tE:base.tE,paid:base.paid+80});}
// bizContrib: lo que gana el negocio con un coche en gestión = comisión − déficit (cláusula 5.5)
{const v=V.find(x=>x.id==='v2');const keep=[v.bookings,v.finances];v.bookings=[];v.finances=[...oct,...nov].map((e,i)=>Object.assign({id:'t'+i},e));
 ok('bizContrib v2 (gestión): ingreso del negocio = mgr de los meses (oct 300 + nov 270 = 570)',near(bizContrib(v).inc,570)&&bizContrib(v).exp===0);
 [v.bookings,v.finances]=keep;}
return R;})()"""
# Liquidación del propietario: coche en gestión v2 (30 %), octubre y noviembre de 2026
LIQ=r"""async()=>{const v=V.find(x=>x.id==='v2');v.bookings=[];
 v.finances=[{id:'l1',type:'income',date:'2026-10-03',amount:1000,category:'Alquiler',description:'Octubre'},{id:'l2',type:'expense',date:'2026-10-10',amount:100,category:'Limpieza',description:'Limpieza oct'},
   {id:'l3',type:'income',date:'2026-11-03',amount:1000,category:'Alquiler',description:'Noviembre'},{id:'l4',type:'expense',date:'2026-11-10',amount:100,category:'Limpieza',description:'Limpieza nov'},
   {id:'l5',type:'expense',date:'2026-11-12',amount:200,category:'Seguro',description:'Seguro (5.2)'}];
 _invalidateRsCache&&_invalidateRsCache();
 const r={};for(const m of ['2026-10','2026-11'])r[m]=(await __pdfText(()=>dlOwnerReport('o1',m))).map(t=>t.replace(/[  ]/g,' '));return r;}"""
with H.playwright() as p:
    br=H.launch(p)
    ctx,pg=H.open_app(br,extra="window.alert=m=>{(window.__AL=window.__AL||[]).push(String(m))};")
    for good,label,info in pg.evaluate(JS):H.chk(good,label,info)
    pg.evaluate(H.PDFTEXT)
    r=pg.evaluate(LIQ)
    o,n=r['2026-10'],r['2026-11']
    H.chk(not [t for t in o+n if t.startswith('ERROR')],'Liquidación: los dos PDF se generan sin error',[t for t in o+n if t.startswith('ERROR')])
    H.chk('LIQUIDACIÓN MENSUAL · 00000000T · OCTUBRE 2026 · 1 VEHÍCULO' in o,'Liquidación oct-2026: cabecera con DNI, mes y nº de coches',o[:6])
    H.chk(o.count('1000,00 €')>=2 and '300,00 €' in o and '600,00 €' in o and '100,00 €' in o,'Liquidación oct-2026 (regla antigua): ingresos 1.000, comisión 300, gastos 5.3 100, al propietario 600',o)
    H.chk('TOTAL A PAGAR A ANA PROPIETARIA EJEMPLO' in o and o[o.index('TOTAL A PAGAR A ANA PROPIETARIA EJEMPLO')+1]=='600,00 €','Liquidación oct-2026: «TOTAL A PAGAR» 600,00 €')
    H.chk('270,00 €' in n and '630,00 €' in n and 'Comisión 30%' in n,'Liquidación nov-2026 (regla nueva): comisión (1.000 − 100) × 30 % = 270 y al propietario 630',n)
    H.chk('Pagado directamente por el propietario (no se descuenta): 200,00 €' in n,'Liquidación nov-2026: el seguro (5.2) sale como pagado por el propietario y no se descuenta')
    H.chk('GASTOS DESCONTADOS (CLÁUSULA 5.3)' in n and 'Limpieza nov' in ' '.join(n),'Liquidación nov-2026: tabla de gastos descontados (5.3) con la limpieza')
    H.chk(n[n.index('TOTAL A PAGAR A ANA PROPIETARIA EJEMPLO')+1]=='630,00 €','Liquidación nov-2026: «TOTAL A PAGAR» 630,00 €')
    H.chk(not pg.evaluate("window.__AL||[]"),'Sin alertas',pg.evaluate("window.__AL||[]"))
    br.close()
H.fin()
