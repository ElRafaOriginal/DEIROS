# Inicio (móvil) · «Fianzas» y «Por cobrar» como desplegables independientes (#162). Las dos tarjetas siguen juntas en una fila pero,
# plegadas, SIN cifras (solo el título y «+»); al tocarlas despliegan, a lo ancho debajo, el total y su lista (en vez de abrir otra
# hoja); cada una por su cuenta y recordando si
# quedó abierta (deiros_dashFzOpen / deiros_dashPcOpen, plegadas por defecto). Comprueba: abrir y cerrar cada una, que lo recuerda al
# recargar, que las filas e importes son los de la hoja de siempre (openPendingDeposits / openPorCobrar), que los botones de las filas
# funcionan («Ver alquiler», marcar la fianza como devuelta, «Todo» cobrado, «Todas las fianzas»), los dos estados vacíos, el escapado,
# 44 px, tema claro y que en escritorio siguen abriendo la hoja. Datos inventados del arnés; fecha fija 20/11/2026.
# Uso: python3 tests/test_fianzas_porcobrar.py   ·   DEIROS_CAPTURAS=/carpeta guarda 2 capturas (Por cobrar abierto; las dos abiertas)
import sys,os,json,copy
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
chk=H.chk
KEYS="Object.fromEntries(['deiros_dashFzOpen','deiros_dashPcOpen'].map(k=>[k,localStorage.getItem(k)]))"
# Estado de cada tarjeta y su panel
ST=r"""(k=>{const i=k==='fz'?1:2;const b=document.querySelectorAll('#PC .dh-act')[i];const p=document.getElementById('dhP-'+k);
  const r=b.getBoundingClientRect();return {exp:b.getAttribute('aria-expanded'),ctl:b.getAttribute('aria-controls'),plus:b.querySelector('b svg').innerHTML.includes('M12 5v14'),
  rot:getComputedStyle(b.querySelector('b svg')).transform,w:r.width,h:r.height,top:r.top,
  open:!!p&&!p.hidden&&p.offsetHeight>0,empty:!!p&&p.innerHTML==='',ptop:p?p.getBoundingClientRect().top:0,pw:p?p.getBoundingClientRect().width:0,
  title:p&&p.querySelector('.dh-fph')?p.querySelector('.dh-fph').innerText.replace(/\s+/g,' ').trim():'',ls:localStorage.getItem(k==='fz'?'deiros_dashFzOpen':'deiros_dashPcOpen')};})"""
# Filas (texto de cada fila .fz-r) de un contenedor
ROWS=r"""(sel=>[...document.querySelectorAll(sel+' .fz-r')].map(r=>[r.querySelector('.t').textContent,[...r.querySelectorAll('.s')].map(s=>s.textContent).join(' | '),
  r.querySelector('.chip').textContent,r.querySelector('.r b').textContent,r.querySelector('button').textContent,r.querySelector('button').getAttribute('onclick')]))"""
def nav(pg,w=500):pg.evaluate("nav('dashboard')");pg.wait_for_timeout(w)
def recarga(pg):
    # Igual que test_inicio: si el navegador de pruebas pierde localStorage al recargar, se repone y se recarga (se prueba que la app lo LEE)
    antes=pg.evaluate(KEYS)
    for i in range(3):
        pg.wait_for_timeout(1500);pg.reload();pg.wait_for_timeout(2000)
        if pg.evaluate(KEYS)==antes:break
        print('AVISO: el navegador de pruebas perdió localStorage al recargar; se repone y se recarga otra vez',flush=True)
        pg.evaluate("(o=>{for(const k in o){if(o[k]===null)localStorage.removeItem(k);else localStorage.setItem(k,o[k]);}})(%s)"%json.dumps(antes))
    nav(pg)
def vacio():
    D=copy.deepcopy(H.D0)
    for v in D['vehicles']:
        for b in v['bookings']:
            b.pop('fianza',None);b.pop('abonoReserva',None);b['cobrado']=True;b['paid']=True
    return D
def con_raro():
    # Un alquiler terminado sin cobrar, con fianza pendiente y un nombre con HTML y comillas (escapado)
    D=copy.deepcopy(H.D0)
    D['vehicles'][3]['bookings'].append({'id':'bQ','startDate':H.d(-9),'startTime':'10:00','endDate':H.d(-6),'endTime':'10:00','platform':'sinapp','amount':95,
        'clientName':'<img src=x onerror="window.__X=1">O\'Hara "Q"','finance':[],'extras':[],'fianza':150,'delivered':True,'returned':True})
    return D
def run():
  with H.playwright() as p:
    br=H.launch(p)
    ctx,pg=H.open_app(br,has_touch=True,is_mobile=True);J=pg.evaluate;W=pg.wait_for_timeout
    st=lambda k:J(ST,k);sh_open=lambda:J("document.getElementById('SH').classList.contains('open')")
    nav(pg)
    # ── 1. Por defecto: las dos tarjetas como siempre, plegadas ──
    f,c=st('fz'),st('pc')
    chk(f['exp']=='false' and c['exp']=='false' and f['ctl']=='dhP-fz' and c['ctl']=='dhP-pc','Por defecto plegadas: aria-expanded="false" y aria-controls de su panel',(f['exp'],c['exp']))
    chk(not f['open'] and not c['open'] and f['empty'] and c['empty'],'Plegadas: los paneles están ocultos y vacíos (nada de su texto en el Inicio)')
    chk(abs(f['top']-c['top'])<1 and abs(f['w']-c['w'])<1 and abs(f['h']-c['h'])<1,'Fianzas y Por cobrar siguen juntas en la misma fila y con el mismo tamaño',(f['top'],c['top'],f['w'],c['w'],f['h']))
    chk(f['w']>=44 and f['h']>=44,'Tarjetas de al menos 44 px')
    chk(f['plus'] and c['plus'],'En el móvil llevan «+» (patrón de los plegables), no «→»')
    tile=J("[...document.querySelectorAll('#PC .dh-act')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())")
    pc=J("_porCobrar()");nfz=J("_depRows('pending').length")
    chk(tile[1]=='FIANZAS' and tile[2]=='POR COBRAR' and not any(ch.isdigit() for ch in tile[1]+tile[2]) and nfz>0 and len(pc['rows'])>0,'Plegadas, sin ninguna cifra: solo «Fianzas» y «Por cobrar» (aunque haya pendientes)',tile)
    chk(J("[...document.querySelectorAll('#PC .dh-act')].slice(1).every(b=>!b.hasAttribute('aria-label')&&!/\\d/.test(b.textContent))"),'Ni en el texto ni en aria-label de las tarjetas hay cifras')
    # Lo que mostraba la hoja de antes (las hojas siguen existiendo: Fianzas del menú y Por cobrar del coche)
    J("openPendingDeposits()");W(400);hFz=J(ROWS,'#SC');J("closeSheet()");W(300)
    J("openPorCobrar()");W(400);hPc=J(ROWS,'#SC');hPcT=J("document.querySelector('#SC .al-pd b').textContent");J("closeSheet()");W(300)
    chk(len(hFz)>=3 and len(hPc)>=2,'Hay filas de ejemplo en las dos hojas (%d fianzas, %d por cobrar)'%(len(hFz),len(hPc)))
    # ── 2. Abrir Fianzas: solo Fianzas ──
    pg.locator('#PC .dh-act').nth(1).tap();W(400)
    f,c=st('fz'),st('pc')
    chk(not sh_open(),'Al tocar «Fianzas» no se abre ninguna hoja')
    chk(f['open'] and f['exp']=='true' and f['ls']=='1' and not c['open'] and c['exp']=='false','Fianzas desplegada (aria-expanded="true", deiros_dashFzOpen=1); Por cobrar sigue plegada',(f,c))
    chk(f['ptop']>f['top']+f['h'] and f['pw']>f['w']*1.8,'La lista sale debajo de la fila y a lo ancho',(f['ptop'],f['pw']))
    chk(f['rot']!='none','El «+» gira al abrir',f['rot'])
    sFz=J("fmtF(_depRows('pending').reduce((t,r)=>t+(Number(r.b.fianza)||0),0))")
    chk(H.N(f['title'])==H.N('FIANZAS %d fianzas pendientes · %s'%(len(hFz),sFz)),'Arriba de la lista: título y total («%d fianzas pendientes · %s»)'%(len(hFz),H.N(sFz)),f['title'])
    chk(H.N(sFz)==H.N(J("fmtF(%s)"%'+'.join(str(float(x[3].replace('\xa0',' ').replace(' €','').replace('.','').replace(',','.'))) for x in hFz))),'El total de fianzas es la suma de las filas de la hoja')
    iFz=J(ROWS,'#dhP-fz')
    chk(iFz==hFz,'Fianzas: mismas filas, orden, chips, importes y botones que la hoja de antes',[x[:4] for x in iFz])
    # ── 3. Abrir también Por cobrar: las dos, una debajo de otra ──
    pg.locator('#PC .dh-act').nth(2).tap();W(400)
    f,c=st('fz'),st('pc')
    chk(f['open'] and c['open'] and c['ls']=='1' and c['exp']=='true' and c['ptop']>f['ptop'],'Las dos abiertas: Fianzas y debajo Por cobrar, cada una con su título',(f['title'],c['title']))
    iPc=J(ROWS,'#dhP-pc')
    chk(iPc==hPc,'Por cobrar: mismos alquileres, «lo que falta» y botones que la hoja de antes',[x[:4] for x in iPc])
    chk(H.N(c['title'])==H.N('POR COBRAR %s · %d alquileres'%(hPcT,len(hPc))),'Arriba de la lista: título y total con céntimos (el de la hoja) · N alquileres',c['title'])
    t2=J("[...document.querySelectorAll('#PC .dh-act')].slice(1).map(b=>b.innerText.trim())")
    chk(t2==['FIANZAS','POR COBRAR'],'Abiertas, las tarjetas siguen sin cifras (las cifras van en la lista)',t2)
    if H.CAPTURAS:
        pg.set_viewport_size({'width':390,'height':1500});W(300)
        J("document.querySelector('#PC .dh-acts').scrollIntoView({block:'start'});document.getElementById('mainPage').scrollTop-=12");W(300)
        pg.screenshot(path=os.path.join(H.CAPTURAS,'fzpc-02-las-dos-abiertas.png'))
        pg.set_viewport_size({'width':390,'height':844});W(300)
    # ── 4. Cerrar Fianzas: Por cobrar sigue abierta ──
    pg.locator('#PC .dh-act').nth(1).tap();W(400)
    f,c=st('fz'),st('pc')
    chk(not f['open'] and f['empty'] and f['exp']=='false' and f['ls']=='0' and c['open'],'Al volver a tocar Fianzas se pliega (deiros_dashFzOpen=0); Por cobrar sigue abierta')
    if H.CAPTURAS:
        J("document.querySelector('#PC .dh-acts').scrollIntoView({block:'start'});document.getElementById('mainPage').scrollTop-=12");W(300)
        pg.screenshot(path=os.path.join(H.CAPTURAS,'fzpc-01-por-cobrar-abierto.png'))
    # ── 5. Recordar al recargar ──
    recarga(pg);f,c=st('fz'),st('pc')
    chk(not f['open'] and c['open'] and c['exp']=='true' and f['exp']=='false','Tras recargar: Por cobrar sigue abierta y Fianzas plegada',(f['ls'],c['ls']))
    chk(J(ROWS,'#dhP-pc')==hPc,'Tras recargar, la lista de Por cobrar es la misma')
    pg.locator('#PC .dh-act').nth(1).tap();W(300);recarga(pg);f,c=st('fz'),st('pc')
    chk(f['open'] and c['open'],'Abiertas las dos y recargado: siguen abiertas las dos')
    pg.locator('#PC .dh-act').nth(2).tap();W(300);recarga(pg);f,c=st('fz'),st('pc')
    chk(f['open'] and not c['open'] and c['empty'],'Cerrada solo Por cobrar y recargado: Fianzas abierta, Por cobrar plegada')
    J("renderDash(document.getElementById('PC'))");W(200)
    chk(st('fz')['open'] and not st('pc')['open'],'Al repintar el Inicio se mantiene el estado de cada una')
    pg.locator('#PC .dh-act').nth(2).tap();W(300)
    # ── 6. Botones de las filas ──
    sz=J("[...document.querySelectorAll('#PC .dh-fp button')].map(b=>{const r=b.getBoundingClientRect();return Math.min(r.width,r.height)})")
    chk(sz and min(sz)>=43.5,'Botones de las filas y «Todas las fianzas» de al menos 44 px',min(sz) if sz else sz)
    fila=pg.locator('#dhP-pc .fz-r').first;nom=fila.locator('.t').text_content();bid=J("_porCobrar().rows[0].b.id")
    fila.locator('button').tap();W(600)
    chk(sh_open() and 'Detalle del alquiler' in J("document.getElementById('SC').textContent") and nom in J("document.getElementById('SC').textContent"),'Por cobrar: «Ver alquiler» abre la ficha de ese alquiler',nom)
    pg.locator('#SC .al-cq button',has_text='Todo').tap();W(600)
    chk(J("_bkCobro(V.flatMap(v=>v.bookings||[]).find(b=>b.id===%r)).falta"%bid)==0,'Desde la ficha se cobra «Todo»')
    J("closeSheet()");W(300);nav(pg)
    iPc2=J(ROWS,'#dhP-pc')
    chk(st('pc')['open'] and len(iPc2)==len(hPc)-1 and nom not in [x[0] for x in iPc2],'Al volver al Inicio, Por cobrar sigue abierta y ya sin ese alquiler',[x[0] for x in iPc2])
    fz0=J("_depRows('pending')[0].b.id")
    pg.locator('#dhP-fz .fz-r').first.locator('button').tap();W(600)
    chk(sh_open() and 'Fianza reembolsable' in J("document.getElementById('SC').textContent"),'Fianzas: «Ver alquiler» abre la ficha con su fianza')
    pg.locator('#SC .al-seg button',has_text='Devuelta').tap();W(500)
    chk(J("_fianzaStatus(V.flatMap(v=>v.bookings||[]).find(b=>b.id===%r))"%fz0)=='returned','Desde la ficha se marca la fianza como «Devuelta»')
    J("closeSheet()");W(300);nav(pg)
    iFz2=J(ROWS,'#dhP-fz')
    chk(st('fz')['open'] and len(iFz2)==len(hFz)-1 and ("'%s'"%fz0) not in ' '.join(x[5] for x in iFz2),'Al volver, Fianzas sigue abierta con una pendiente menos',len(iFz2))
    pg.locator('#dhP-fz .dh-fpa').tap();W(500)
    chk(sh_open() and J("(document.querySelector('#SC .d-seg button[aria-pressed=\"true\"]')||{}).textContent")=='Todas','«Todas las fianzas» abre la hoja de siempre con el filtro «Todas»')
    J("closeSheet()");W(300)
    ctx.close()
    # ── 7. Estados vacíos ──
    ctx,pg=H.open_app(br,data=vacio(),extra="localStorage.setItem('deiros_dashFzOpen','1');localStorage.setItem('deiros_dashPcOpen','1');");J=pg.evaluate;nav(pg)
    t=J("[document.getElementById('dhP-fz').innerText,document.getElementById('dhP-pc').innerText].map(x=>x.replace(/\\s+/g,' ').trim())")
    chk(t[0]=='FIANZAS Sin fianzas pendientes Todas las fianzas' and J("document.querySelectorAll('#dhP-fz .fz-r').length")==0,'Fianzas vacía: «Sin fianzas pendientes»',t[0])
    chk(t[1]=='POR COBRAR Nada por cobrar' and J("document.querySelectorAll('#dhP-pc .fz-r').length")==0 and '€' not in t[1],'Por cobrar vacía: «Nada por cobrar»',t[1])
    ctx.close()
    # ── 8. Escapado ──
    ctx,pg=H.open_app(br,data=con_raro(),extra="localStorage.setItem('deiros_dashFzOpen','1');localStorage.setItem('deiros_dashPcOpen','1');");J=pg.evaluate;nav(pg)
    chk(J("!document.querySelector('#PC .dh-fp img')&&!window.__X"),'Un nombre con HTML no se interpreta (ni en Fianzas ni en Por cobrar)')
    chk(J("[...document.querySelectorAll('#dhP-pc .fz-r .t')].some(e=>e.textContent.includes('O\\'Hara \"Q\"'))"),'Se ve tal cual, con comillas')
    ctx.close()
    # ── 9. Tema claro ──
    ctx,pg=H.open_app(br,theme='light',extra="localStorage.setItem('deiros_dashPcOpen','1');");J=pg.evaluate;nav(pg)
    chk(J("!document.getElementById('dhP-pc').hidden&&getComputedStyle(document.querySelector('#dhP-pc .dh-fph b')).color!==getComputedStyle(document.body).backgroundColor"),'Tema claro: Por cobrar abierta y legible')
    ctx.close()
    # ── 10. Escritorio: la hoja de siempre (aunque en el móvil quedara abierta) ──
    ctx,pg=H.open_app(br,viewport={'width':1280,'height':900},extra="localStorage.setItem('deiros_dashFzOpen','1');localStorage.setItem('deiros_dashPcOpen','1');");J=pg.evaluate;nav(pg,600)
    chk(J("!document.querySelector('#PC .dh-fp')&&[...document.querySelectorAll('#PC .dh-act')].every(b=>!b.hasAttribute('aria-expanded'))"),'Escritorio: sin desplegables ni aria-expanded')
    pg.locator('#PC .dh-act').nth(2).click();pg.wait_for_timeout(500)
    chk(J("document.getElementById('SH').classList.contains('open')")and 'Lo que falta del alquiler' in J("document.getElementById('SC').textContent"),'Escritorio: «Por cobrar» abre su hoja')
    J("closeSheet()");pg.locator('#PC .dh-act').nth(1).click();pg.wait_for_timeout(500)
    chk(J("document.getElementById('SH').classList.contains('open')")and 'Fianzas de los alquileres' in J("document.getElementById('SC').textContent"),'Escritorio: «Fianzas» abre su hoja')
    ctx.close()
  H.fin()
if __name__=='__main__':run()
