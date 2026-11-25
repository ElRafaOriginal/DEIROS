# Dinero · «Rentabilidad · plataforma» del Resumen cuadra con los ingresos del periodo.
# Mes: la suma de las filas = «INGRESOS MES»; Año: = «INGRESOS 2026» (Año · acumulado); Trimestre: = la misma cuenta que
# «Ingresos mes» hecha en los tres meses del trimestre; escritorio (1280 px, histórico): = todos los ingresos sin fianzas.
# Datos inventados: alquileres que cruzan meses, ampliación, extras, cobro de devolución, fianza (no cuenta), cancelados con
# penalización (cliente y propietario), coche en gestión, ingreso manual del coche e ingresos de Negocio. Fecha fija: 20/11/2026.
# Uso: python3 tests/test_rentabilidad_plataforma.py
import sys,os,re,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
chk=H.chk
SETUP=r"""(()=>{
BF=[{id:'n1',type:'income',amount:500,date:'2026-11-03',category:'Alquiler',description:'Liquidación Amovens'},
    {id:'n2',type:'income',amount:100,date:'2026-08-10',category:'Otros'},
    {id:'n3',type:'income',amount:200,date:'2026-11-05',category:'Depósito'},
    {id:'n4',type:'expense',amount:50,date:'2026-11-05',category:'Seguro'}];
V=V.filter(v=>['v1','v2','v3','v6'].includes(v.id));
V.forEach(v=>{v.bookings=[];v.finances=[];});
const v1=V.find(v=>v.id==='v1'),v2=V.find(v=>v.id==='v2'),v3=V.find(v=>v.id==='v3'),v6=V.find(v=>v.id==='v6');
v1.vtype='own';v3.vtype='own';v2.vtype='managed';v2.ownerId='o1';v2.commission=30;
const bk=(id,s,e,pl,amt,x)=>Object.assign({id,startDate:s,startTime:'10:00',endDate:e,endTime:'10:00',platform:pl,amount:amt,clientName:'Cliente '+id,finance:[],extras:[]},x||{});
const add=(v,b)=>{v.bookings.push(b);proRataEntries(b.startDate,b.endDate,b.amount,b.platform,'',b.id).forEach(e=>v.finances.push(e));return b;};
// A · Sin app, cruza octubre → noviembre, con km extra a la devolución y depósito de la fianza (no es ingreso)
const A=add(v1,bk('A','2026-10-25','2026-11-04','sinapp',300,{returned:true}));
A.finance.push({id:'fa1',type:'income',concept:'Exceso de km',amount:19,date:'2026-11-04',_returnCharge:true});
A.finance.push({id:'fa2',type:'income',concept:'Depósito',amount:200,date:'2026-10-25'});
// B · Amovens del 10 al 15 de noviembre, ampliado hasta el 18 (+60 €), como lo guarda «Ampliar alquiler»
const B=add(v1,bk('B','2026-11-10','2026-11-15','amovens',150));
B.endDate='2026-11-18';B.finance.push({id:'fb1',type:'income',concept:'Ampliación alquiler (2026-11-15 → 2026-11-18)',amount:60,date:'2026-11-15'});
proRataEntries('2026-11-16','2026-11-18',60,'amovens','Ampliación · x','B').forEach(e=>{e._extension=true;v1.finances.push(e);});
// C · Sin app del 28/11 al 05/12 con un extra (copia _autoExtra en b.finance y en v.finances, como el alta)
const C=add(v3,bk('C','2026-11-28','2026-12-05','sinapp',400,{extras:[{id:'x1',label:'Silla',amount:20}]}));
C.finance.push({id:'fc1',type:'income',concept:'Silla',amount:20,date:'2026-11-28',_autoExtra:true});
v3.finances.push({id:'fc2',type:'income',date:'2026-11-01',category:'Silla',amount:20,_bookingId:'C',_autoExtra:true});
// D · Getaround cancelado por el cliente con 50 € de penalización; E · Getaround cancelado por el propietario (paga 30 €)
const cancel=(v,b,by,pen)=>{b.cancelled=true;b.cancellation={by,penalty:pen,date:'2026-11-11'};const e={id:'pen_'+b.id,date:'2026-11-11',concept:'Penalización cancelación',amount:pen,type:by==='client'?'income':'expense',_cancellation:true};b.finance.push(e);v.finances.push({...e,id:'vpen_'+b.id,bookingId:b.id});};
cancel(v3,add(v3,bk('D','2026-11-12','2026-11-14','getaround',200)),'client',50);
cancel(v3,add(v3,bk('E','2026-11-21','2026-11-23','getaround',90)),'owner',30);
// F · Getaround en el coche en gestión, cruza septiembre → octubre; G · Sin app en gestión en noviembre
add(v2,bk('F','2026-09-28','2026-10-03','getaround',120,{returned:true}));
add(v2,bk('G','2026-11-05','2026-11-08','sinapp',250));
// Ingreso manual del coche (sin alquiler) y un alquiler de un coche archivado (no cuenta en el Resumen)
v1.finances.push({id:'m1',type:'income',amount:80,date:'2026-11-02',category:'Alquiler',description:'Ingreso manual'});
v6.archived=true;add(v6,bk('Z','2026-11-01','2026-11-03','amovens',999));
_invalidateRsCache&&_invalidateRsCache();
return true;})()"""
# Ingresos del periodo con la MISMA cuenta que «Ingresos mes» (renderDash), para meses que cumplan inP
EQ=r"""(meses)=>{const inP=m=>meses===null||meses.includes(m);const aV=V.filter(v=>!v.archived);let t=0;
  t+=BF.filter(e=>e.type==='income'&&!_isDepositInc(e)&&inP((e.date||'').slice(0,7))).reduce((s,e)=>s+(Number(e.amount)||0),0);
  aV.forEach(v=>{t+=_plFins(v,_getVehicleAllFinancesDisplay(v).filter(e=>e.date&&inP(e.date.slice(0,7))&&!e._bfEntry)).filter(e=>e.type==='income'&&!_isDepositInc(e)).reduce((s,e)=>s+(Number(e.amount)||0),0);});
  return Math.round(t*100)/100;}"""
def eur(s):
    s=H.N(s).replace('€','').replace(' ','').replace('.','').replace(',','.')
    return float(s)
def filas(pg):
    h=pg.evaluate("document.getElementById('PC').innerHTML").replace('&nbsp;',' ')
    return [(m[0],m[1],eur(m[2])) for m in re.findall(r'<span class="t">([^<]+)<span class="q">([^<]*)</span></span><b>([^<]+)</b>',h)],h
def run():
  with H.playwright() as p:
    br=H.launch(p);ctx,pg=H.open_app(br,extra="window.alert=m=>console.log('ALERT',m);window.confirm=()=>false;")
    pg.evaluate(SETUP)
    # ── Mes ──
    pg.evaluate("_dashPlatPeriod='monthly';nav('dashboard')");pg.wait_for_timeout(400)
    F,h=filas(pg)
    m=re.search(r'INGRESOS MES<b class="lg">([^<]+)</b>',h);im=eur(m.group(1)) if m else None
    eqm=pg.evaluate("("+EQ+")(['2026-11'])")
    chk(im==eqm,f'«INGRESOS MES» no cambia: {im} = cuenta de siempre {eqm}')
    s=round(sum(x[2] for x in F),2)
    chk(s==im,f'Mes: la suma de «Rentabilidad · plataforma» = INGRESOS MES ({s} = {im})',F)
    d={x[0]:x for x in F}
    chk(set(d)=={'Amovens','Getaround','Sin app','Otros ingresos'},f'Mes: filas Amovens, Getaround, Sin app y «Otros ingresos» ({list(d)})')
    chk(d.get('Amovens',(0,''))[1]=='1 alq.' and d.get('Getaround',(0,''))[1]=='0 alq.' and d.get('Sin app',(0,''))[1]=='3 alq.',
        f'Mes: alquileres con ingresos en noviembre: Amovens 1 (B), Getaround 0 (D y E cancelados), Sin app 3 (A, que viene de octubre; C y G) ({F})')
    chk(d.get('Otros ingresos',(0,0,0))[2]==580,f'Mes: «Otros ingresos» = Negocio 500 + ingreso manual del coche 80 (el depósito de Negocio no cuenta) = 580 ({d.get("Otros ingresos")})')
    chk(d.get('Amovens',(0,0,0))[2]==210,f'Mes: Amovens = 150 + ampliación 60 = 210, sin el coche archivado ({d.get("Amovens")})')
    chk(d.get('Getaround',(0,0,0))[2]==50,f'Mes: Getaround = penalización cobrada 50 (la que paga DEIROS es gasto, no resta aquí) ({d.get("Getaround")})')
    chk('sin plataforma' in d.get('Otros ingresos',(0,''))[1],'Mes: «Otros ingresos» dice «sin plataforma» en vez de un número de alquileres')
    # ── Trimestre (oct–dic) ──
    pg.evaluate("_dashPlatPeriod='quarterly';renderDash(document.getElementById('PC'))");pg.wait_for_timeout(300)
    F,h=filas(pg);s=round(sum(x[2] for x in F),2);eq=pg.evaluate("("+EQ+")(['2026-10','2026-11','2026-12'])")
    chk(s==eq,f'Trimestre: la suma de las filas = ingresos de octubre + noviembre + diciembre ({s} = {eq})',F)
    d={x[0]:x for x in F}
    chk(d.get('Getaround',(0,''))[1]=='1 alq.' and d.get('Sin app',(0,''))[1]=='3 alq.',f'Trimestre: Getaround 1 (F, parte de octubre), Sin app 3 ({F})')
    # ── Año ──
    pg.evaluate("_dashPlatPeriod='annual';renderDash(document.getElementById('PC'))");pg.wait_for_timeout(300)
    F,h=filas(pg);s=round(sum(x[2] for x in F),2)
    m=re.search(r'INGRESOS 2026<b>([^<]+)</b>',h);iy=eur(m.group(1)) if m else None
    meses=['2026-%02d'%i for i in range(1,13)]
    chk(iy==pg.evaluate("("+EQ+")(%s)"%json.dumps(meses)),f'«INGRESOS 2026» no cambia ({iy})')
    chk(s==iy,f'Año: la suma de las filas = INGRESOS 2026 de «Año · acumulado» ({s} = {iy})',F)
    d={x[0]:x for x in F}
    chk(d.get('Otros ingresos',(0,0,0))[2]==680,f'Año: «Otros ingresos» = 500 + 100 (agosto) + 80 = 680 ({d.get("Otros ingresos")})')
    # ── Sin ingresos fuera de plataforma: no sale «Otros ingresos» ──
    pg.evaluate("BF=[];V.find(v=>v.id==='v1').finances=V.find(v=>v.id==='v1').finances.filter(e=>e.id!=='m1');_dashPlatPeriod='monthly';renderDash(document.getElementById('PC'))");pg.wait_for_timeout(300)
    F,h=filas(pg);m=re.search(r'INGRESOS MES<b class="lg">([^<]+)</b>',h)
    chk([x[0] for x in F]==['Amovens','Getaround','Sin app'] and round(sum(x[2] for x in F),2)==eur(m.group(1)),f'Sin ingresos sin plataforma: solo las 3 filas de siempre y siguen sumando INGRESOS MES ({F})')
    pg.evaluate(SETUP)
    # ── Escritorio (1280 px): histórico ──
    pg.set_viewport_size({'width':1280,'height':900});pg.wait_for_timeout(300)
    pg.evaluate("nav('dashboard')");pg.wait_for_timeout(400)
    cards=pg.evaluate("(()=>{const s=[...document.querySelectorAll('#PC .sec')].find(e=>e.textContent.includes('RENTABILIDAD POR PLATAFORMA'));if(!s)return [];return [...s.nextElementSibling.children].map(c=>c.innerText);})()")
    vals=[eur(re.search(r'([-\d.,]+\s*€)',H.N(c)).group(1)) for c in cards if re.search(r'([-\d.,]+\s*€)',H.N(c))]
    eqa=pg.evaluate("("+EQ+")(null)")
    chk(len(cards)==4 and any('Otros ingresos' in c and 'Sin plataforma' in c for c in cards),f'Escritorio: 4 tarjetas, con «Otros ingresos · Sin plataforma» ({[c.replace(chr(10)," | ") for c in cards]})')
    chk(round(sum(vals),2)==eqa,f'Escritorio: la suma de las tarjetas = todos los ingresos sin fianzas ({round(sum(vals),2)} = {eqa})')
    am=[c for c in cards if 'Amovens' in c]
    chk(bool(am) and '1 alquileres' in am[0],f'Escritorio: Amovens «1 alquileres» ({am[0].replace(chr(10)," | ") if am else None})')
    ow=pg.evaluate("document.documentElement.scrollWidth<=window.innerWidth+1")
    chk(ow,'Escritorio: nada se sale de la pantalla')
    br.close()
run()
H.fin()
