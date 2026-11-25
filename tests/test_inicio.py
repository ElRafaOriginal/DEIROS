# Inicio (Resumen) · nuevo orden en el móvil: «Resultado flota» arriba con el ojo (oculta resultado, margen, ingresos y gastos
# del mes como «••••» y lo recuerda en deiros_dashHide), «Disponibilidad» (Coches libres · Fianzas · Por cobrar), «Alertas»
# plegable (recuerda si se deja abierta; con vencidas, número en rojo y se abre sola una vez por cada vencida nueva), «Hoy»,
# En alquiler ahora, Próximos, Año acumulado, Evolución y Rentabilidad. Escritorio: Resultado → Disponibilidad → Hoy → Año.
# Las cifras no cambian: se recalculan con la cuenta de siempre y, si se da DEIROS_BASE=<index.html anterior>, se comparan
# una a una con las de esa copia (móvil y escritorio). Datos inventados del arnés; fecha fija 20/11/2026.
# Uso: python3 tests/test_inicio.py   ·   DEIROS_BASE=/ruta/index_base.html python3 tests/test_inicio.py
import sys,os,re,json,copy
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
chk=H.chk
BASE=os.environ.get('DEIROS_BASE','')
ORDEN=r"""[...document.querySelectorAll('#PC .anim > *')].map(e=>{
  if(e.matches('.dh-card.hl'))return 'Resultado';
  if(e.matches('.dh-acts'))return 'Disponibilidad';
  if(e.matches('details')){const t=(e.querySelector('summary .q')||{}).textContent||'';return t.split(/[ ·]/)[0];}
  if(e.matches('section')){const h=e.querySelector('h2');return h?h.textContent.split(' ')[0]:'section';}
  if(e.matches('.dh-sec')&&e.querySelector('.dh-card.hl'))return 'Resultado';
  return e.tagName.toLowerCase();})"""
CARD=r"""(()=>{const c=document.querySelector('#PC .dh-res');const b=c&&c.querySelector('.dh-eye');const r=b?b.getBoundingClientRect():{width:0,height:0};
  const p=b?b.querySelector('svg').innerHTML:'';
  return {hid:!!c&&c.classList.contains('hid'),txt:c?c.innerText.replace(/[  ]/g,' '):'',pressed:b&&b.getAttribute('aria-pressed'),label:b&&b.getAttribute('aria-label'),
    w:r.width,h:r.height,off:p.includes('M4 4l16 16'),ls:localStorage.getItem('deiros_dashHide'),
    mkCol:c&&c.classList.contains('hid')?getComputedStyle(c.querySelector('.spec b.dh-mk')).color:'',bg:c?getComputedStyle(c).backgroundColor:''};})()"""
AL=r"""(()=>{const d=document.querySelector('#PC details.dh-al');if(!d)return null;const q=d.querySelectorAll('summary .q');
  return {open:d.open,label:q[0].textContent,lblErr:q[0].classList.contains('err'),num:q[1].textContent,numErr:q[1].classList.contains('err'),numAc:q[1].classList.contains('ac'),
    rows:d.querySelectorAll('.dh-row').length,n:getAlerts().length,ls:localStorage.getItem('deiros_dashAlOpen')};})()"""
# Las cifras del mes con la cuenta de siempre (copia literal de renderDash), para comparar con lo pintado
EQ=r"""(()=>{const aV=V.filter(v=>!v.archived);const now=new Date();const curM=now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0');let mI=0,mE=0;
  mI+=BF.filter(e=>e.type==='income'&&!_isDepositInc(e)&&e.date.startsWith(curM)).reduce((s,e)=>s+(Number(e.amount)||0),0);
  mE+=BF.filter(e=>e.type==='expense'&&e.date.startsWith(curM)).reduce((s,e)=>s+(Number(e.amount)||0),0);
  aV.forEach(v=>{const mF=_plFins(v,_getVehicleAllFinancesDisplay(v).filter(e=>e.date&&e.date.startsWith(curM)&&!e._bfEntry));
    mI+=mF.filter(e=>e.type==='income'&&!_isDepositInc(e)).reduce((s,e)=>s+(Number(e.amount)||0),0);mE+=mF.filter(e=>e.type==='expense').reduce((s,e)=>s+(Number(e.amount)||0),0);});
  const n=x=>x.replace(/[  ]/g,' ');return {mI:n(fmt(mI)),mE:n(fmt(mE)),mP:n(fmt(mI-mE)),mg:mI>0?'Margen '+Math.round((mI-mE)/mI*100)+' %':''};})()"""
# Todas las cifras del Resumen (importes, margen, contadores «01») del texto completo, ordenadas: deben ser las mismas que en la base
CIFRAS=r"""(()=>{const t=document.getElementById('PC').textContent.replace(/[  ]/g,' ').replace(/\s+/g,' ');
  return [...(t.match(/-?\d[\d.]*,\d{2} €/g)||[]),...(t.match(/Margen -?\d+ %/g)||[]),...(t.match(/\b\d+ alq\.|\b\d+ pendientes|\bEn -?\d+d\b|\b\d+D\b/g)||[])].sort();})()"""
def nav(pg,w=500):pg.evaluate("nav('dashboard')");pg.wait_for_timeout(w)
# Recarga la app y la vuelve a abrir en el Resumen. Lo escrito por la app (deiros_dashHide, deiros_dashAlOpen, deiros_dashAlSeen) se
# anota antes; si el navegador de pruebas lo pierde al recargar (Chromium guarda localStorage en segundo plano y a veces, con
# file:// y mucha carga, la recarga no lo ve), se repone tal cual y se recarga otra vez: así se prueba que la app lo LEE al arrancar.
KEYS="Object.fromEntries(['deiros_dashHide','deiros_dashAlOpen','deiros_dashAlSeen'].map(k=>[k,localStorage.getItem(k)]))"
def recarga(pg):
    antes=pg.evaluate(KEYS)
    for i in range(3):
        pg.wait_for_timeout(1500);pg.reload();pg.wait_for_timeout(2000)
        if pg.evaluate(KEYS)==antes:break
        print('AVISO: el navegador de pruebas perdió localStorage al recargar; se repone y se recarga otra vez',flush=True)
        pg.evaluate("(o=>{for(const k in o){if(o[k]===null)localStorage.removeItem(k);else localStorage.setItem(k,o[k]);}})(%s)"%json.dumps(antes))
    nav(pg)
def sin_vencidas():
    D=copy.deepcopy(H.D0)
    for v in D['vehicles']:
        if v['id']=='v2':v['itv_date']=H.d(45)
        if v['id']=='v4':v.pop('maint_km',None)
    return D
def cifras_de(br,index,width):
    old=H.INDEX;H.INDEX=index
    try:
        ctx,pg=H.open_app(br,viewport={'width':width,'height':900});nav(pg,600)
        r={'money':pg.evaluate(H.MONEY)['dash'],'cifras':pg.evaluate(CIFRAS)};ctx.close();return r
    finally:H.INDEX=old
def run():
  with H.playwright() as p:
    br=H.launch(p)
    # ── 1. Orden en el móvil (390 px) ──
    ctx,pg=H.open_app(br);nav(pg)
    o=pg.evaluate(ORDEN)
    chk(o==['Resultado','Disponibilidad','Alertas','Hoy','En','Próximos','Año','Evolución','Rentabilidad'],
        'Móvil: Resultado flota → Disponibilidad → Alertas → Hoy → En alquiler ahora → Próximos → Año → Evolución → Rentabilidad',o)
    top=pg.evaluate("document.querySelector('#PC .dh-res').getBoundingClientRect().top<document.querySelector('#PC .dh-acts').getBoundingClientRect().top")
    chk(top,'Móvil: «Resultado flota» se ve encima de «Disponibilidad»')
    # ── 2. Cifras: las de siempre ──
    e=pg.evaluate(EQ);c=pg.evaluate(CARD)
    mpE,mpD=e['mP'].split(',',1)
    chk(e['mI'] in c['txt'] and e['mE'] in c['txt'] and re.search(re.escape(mpE)+r'\s*,'+re.escape(mpD),c['txt']),f'Resultado flota: ingresos {e["mI"]}, gastos {e["mE"]} y resultado {e["mP"]} con la cuenta de siempre',c['txt'][:200])
    chk(e['mg'] in c['txt'],f'Resultado flota: «{e["mg"]}» como siempre')
    h=pg.evaluate("document.getElementById('PC').innerHTML").replace('&nbsp;',' ')
    m=re.search(r'INGRESOS MES<b class="lg">([^<]+)</b>',h)
    chk(bool(m) and H.N(m.group(1))==e['mI'],'El marcado de «INGRESOS MES» no cambia (<b class="lg">importe</b>) para el resto de pruebas')
    # ── 3. El ojo ──
    chk(not c['hid'] and c['pressed']=='false' and c['label']=='Ocultar cifras' and not c['off'],'Por defecto las cifras se ven; botón «Ocultar cifras» con el ojo abierto',c)
    chk(c['w']>=43.5 and c['h']>=43.5,f'Botón del ojo de al menos 44×44 px ({c["w"]}×{c["h"]})')
    pg.click('#PC .dh-eye');pg.wait_for_timeout(200);c=pg.evaluate(CARD)
    chk(c['hid'] and c['pressed']=='true' and c['label']=='Mostrar cifras' and c['off'],'Al tocar el ojo: cifras ocultas, «Mostrar cifras», ojo tachado',{k:c[k] for k in ('hid','pressed','label','off')})
    oculto=lambda c:'••••' in c['txt'] and e['mI'] not in c['txt'] and e['mE'] not in c['txt'] and e['mg'] not in c['txt'] and e['mP'].split(',')[0] not in c['txt']
    chk(oculto(c),'Ocultas: resultado, margen, ingresos y gastos se ven como «••••»',c['txt'][:200])
    chk('VEHÍCULOS ACTIVOS' in c['txt'] and c['ls']=='1','Ocultas: «Vehículos activos» sigue a la vista y se guarda deiros_dashHide=1')
    pg.evaluate("renderDash(document.getElementById('PC'))");pg.wait_for_timeout(200)
    chk(pg.evaluate(CARD)['hid'],'Ocultas: siguen ocultas al repintar el Resumen')
    recarga(pg);c=pg.evaluate(CARD)
    chk(c['hid'] and oculto(c) and c['off'],'Tras recargar la app, las cifras siguen ocultas')
    pg.click('#PC .dh-eye');pg.wait_for_timeout(200);c=pg.evaluate(CARD)
    chk(not c['hid'] and e['mI'] in c['txt'] and '••••' not in c['txt'] and c['ls']=='0','Al volver a tocar: las cifras se ven y se guarda deiros_dashHide=0')
    recarga(pg);c=pg.evaluate(CARD)
    chk(not c['hid'] and e['mI'] in c['txt'],'Tras recargar, siguen a la vista')
    # ── 4. Alertas plegable (con una vencida en los datos: ITV del Fiat hace 3 días) ──
    a=pg.evaluate(AL)
    chk(a and a['num']==str(a['n']).zfill(2) and a['rows']==min(5,a['n']),'Alertas: cabecera con el número de alertas y la lista de siempre (hasta 5)',a)
    chk(a and a['numErr'] and a['lblErr'] and 'vencida' in a['label'],'Con vencidas: número y rótulo en rojo y «· N vencida»',a)
    chk(a and a['open'],'Con una vencida nueva, Alertas se abre sola')
    pg.click('#PC details.dh-al > summary');pg.wait_for_timeout(250)
    chk(not pg.evaluate(AL)['open'] and pg.evaluate(AL)['ls']=='0','Alertas: se pliega al tocar la cabecera (deiros_dashAlOpen=0)')
    recarga(pg);
    chk(not pg.evaluate(AL)['open'],'Alertas: tras recargar sigue plegada (la vencida ya vista no la vuelve a abrir)',pg.evaluate(AL))
    pg.click('#PC details.dh-al > summary');pg.wait_for_timeout(250);recarga(pg)
    chk(pg.evaluate(AL)['open'],'Alertas: si se deja abierta, sigue abierta al recargar')
    pg.click('#PC details.dh-al > summary');pg.wait_for_timeout(250)
    pg.evaluate("V.find(v=>v.id==='v3').insurance_date=addDays(todayStr(),-1);renderDash(document.getElementById('PC'))");pg.wait_for_timeout(250)
    a=pg.evaluate(AL)
    chk(a['open'] and '2 vencidas' in a['label'],'Alertas: si vence otra, se vuelve a abrir sola («· 2 vencidas»)',a)
    ctx.close()
    # Sin vencidas: plegada por defecto y número en el color de acento
    ctx,pg=H.open_app(br,data=sin_vencidas());nav(pg)
    a=pg.evaluate(AL)
    chk(a and not a['open'] and a['numAc'] and not a['numErr'] and not a['lblErr'] and 'vencida' not in a['label'],'Sin vencidas: Alertas plegada por defecto, número en acento (no rojo)',a)
    pg.click('#PC details.dh-al > summary');pg.wait_for_timeout(250);recarga(pg)
    chk(pg.evaluate(AL)['open'],'Sin vencidas: abierta y recargada, sigue abierta',pg.evaluate(AL))
    ctx.close()
    # ── 5. Tema claro ──
    ctx,pg=H.open_app(br,theme='light');nav(pg)
    c=pg.evaluate(CARD)
    chk(c['w']>=43.5 and c['h']>=43.5 and not c['hid'],'Tema claro: ojo de 44 px y cifras a la vista',{k:c[k] for k in ('w','h','hid','ls')})
    pg.click('#PC .dh-eye');pg.wait_for_timeout(200);c=pg.evaluate(CARD)
    chk(c['hid'] and oculto(c) and c['mkCol'] and c['mkCol']!=c['bg'],f'Tema claro: oculta las cifras («••••» en {c["mkCol"]} sobre {c["bg"]})')
    recarga(pg);c=pg.evaluate(CARD)
    chk(c['hid'],'Tema claro: lo recuerda al recargar',{k:c[k] for k in ('hid','ls')})
    pg.click('#PC .dh-eye');pg.wait_for_timeout(200)
    chk(not pg.evaluate(CARD)['hid'],'Tema claro: vuelve a mostrarlas')
    ctx.close()
    # ── 6. Escritorio (1280 px): Resultado → Disponibilidad → Hoy → Año; el ojo también ──
    ctx,pg=H.open_app(br,viewport={'width':1280,'height':900});nav(pg,600)
    o=pg.evaluate(ORDEN)
    chk(o[:4]==['Resultado','Disponibilidad','Hoy','Año'],'Escritorio: Resultado → Disponibilidad → Hoy → Año acumulado',o)
    chk(pg.evaluate("!document.querySelector('#PC details.dh-al')&&document.getElementById('PC').textContent.includes('ALERTAS (')"),'Escritorio: Alertas sigue en su columna de la derecha')
    pg.click('#PC .dh-eye');pg.wait_for_timeout(200);c=pg.evaluate(CARD)
    chk(c['hid'] and oculto(c),'Escritorio: el ojo oculta las cifras')
    ctx.close()
    # ── 7. Mismas cifras que la base ──
    if BASE and os.path.isfile(BASE):
        for w in (390,1280):
            a,b=cifras_de(br,BASE,w),cifras_de(br,H.INDEX,w)
            chk(a['money']==b['money'] and len(b['money'])>=2,f'{w} px: INGRESOS/GASTOS MES idénticos a la base',(a['money'],b['money']))
            chk(a['cifras']==b['cifras'] and len(b['cifras'])>5,f'{w} px: todas las cifras del Resumen ({len(b["cifras"])}) idénticas a la base',[x for x in set(a['cifras'])^set(b['cifras'])][:8])
    else:
        print('(sin DEIROS_BASE: las cifras se comprueban con la cuenta de siempre, no contra otra copia)')
    if H.CAPTURAS:
        ctx,pg=H.open_app(br);nav(pg)
        pg.screenshot(path=os.path.join(H.CAPTURAS,'inicio-cifras.png'))
        pg.click('#PC .dh-eye');pg.wait_for_timeout(200);pg.screenshot(path=os.path.join(H.CAPTURAS,'inicio-ocultas.png'));ctx.close()
  H.fin()
if __name__=='__main__':run()
