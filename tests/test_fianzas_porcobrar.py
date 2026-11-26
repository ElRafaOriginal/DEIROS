# Inicio (móvil) · «Fianzas» y «Por cobrar» (#162, ajuste de Rafael del 26/11/2026). Las dos tarjetas van juntas en una fila baja
# (64 px, como «Coches libres») con SOLO el título y «→», sin ninguna cifra; el borde y el título en dorado (morado en claro) si hay
# algo pendiente. Al tocarlas se abre la HOJA de siempre (Fianzas con «Pendientes / Retenidas / Todas»; Por cobrar con el total
# arriba), igual que antes de #163: sin desplegable en el Inicio ni claves deiros_dashFzOpen / deiros_dashPcOpen. Comprueba: sin
# cifras (texto y aria-label), misma fila y tamaño, 44 px, «→», borde y título dorados, que cada una abre su hoja (idéntica a la de
# openPendingDeposits / openPorCobrar), los filtros, «Ver alquiler» → cobrar «Todo» / fianza «Devuelta» → una fila menos al volver
# a abrir, estados vacíos (sin dorado), que las claves antiguas de #163 no despliegan nada, tema claro y escritorio sin cambios
# (3 tarjetas con sus cifras). Datos inventados del arnés; fecha fija 20/11/2026.
# Uso: python3 tests/test_fianzas_porcobrar.py   ·   DEIROS_CAPTURAS=/carpeta guarda 2 capturas (Inicio; hoja de Fianzas)
import sys,os,copy
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
chk=H.chk
# Estado de las dos tarjetas (1 = Fianzas, 2 = Por cobrar)
ST=r"""(i=>{const b=document.querySelectorAll('#PC .dh-act')[i];const r=b.getBoundingClientRect();const s=b.querySelector('b svg');
  const pr=document.createElement('i');pr.style.cssText='border:1px solid var(--acc-b);color:var(--amber)';document.body.appendChild(pr);
  const cs=getComputedStyle(pr),gB=cs.borderTopColor,gC=cs.color;pr.remove();
  return {txt:b.innerText.replace(/\s+/g,' ').trim(),al:b.getAttribute('aria-label'),exp:b.hasAttribute('aria-expanded')||b.hasAttribute('aria-controls'),
  on:b.classList.contains('on'),arr:!!s&&s.innerHTML.includes('M5 12h14'),plus:!!s&&s.innerHTML.includes('M12 5v14'),n:!!b.querySelector('.n'),
  gold:getComputedStyle(b).borderTopColor===gB,tgold:getComputedStyle(b.querySelector('.q')).color===gC,w:r.width,h:r.height,top:r.top};})"""
ROWS=r"""[...document.querySelectorAll('#SC .fz-r')].map(r=>[r.querySelector('.t').textContent,r.querySelector('.r b').textContent,r.querySelector('.chip').textContent,r.querySelector('button').getAttribute('onclick')])"""
def nav(pg,w=500):pg.evaluate("nav('dashboard')");pg.wait_for_timeout(w)
def vacio():
    D=copy.deepcopy(H.D0)
    for v in D['vehicles']:
        for b in v['bookings']:
            b.pop('fianza',None);b.pop('abonoReserva',None);b['cobrado']=True;b['paid']=True
    return D
VIEJAS="localStorage.setItem('deiros_dashFzOpen','1');localStorage.setItem('deiros_dashPcOpen','1');"
def run():
  with H.playwright() as p:
    br=H.launch(p)
    ctx,pg=H.open_app(br,has_touch=True,is_mobile=True,extra=VIEJAS);J=pg.evaluate;W=pg.wait_for_timeout
    st=lambda i:J(ST,i);sh_open=lambda:J("document.getElementById('SH').classList.contains('open')");sc=lambda:J("document.getElementById('SC').textContent")
    nav(pg)
    # ── 1. Tarjetas del móvil ──
    f,c=st(1),st(2);nfz=J("V.reduce((t,v)=>t+(v.bookings||[]).filter(b=>!b.cancelled&&_fianzaStatus(b)==='pending').length,0)");pc=J("_porCobrar()")
    chk(nfz>0 and len(pc['rows'])>0,'Hay fianzas pendientes (%d) y alquileres por cobrar (%d) en los datos'%(nfz,len(pc['rows'])))
    chk(f['txt']=='FIANZAS' and c['txt']=='POR COBRAR','Solo el título, sin ninguna cifra (ni «· N» ni importe)',(f['txt'],c['txt']))
    chk(f['al']=='Fianzas, hay pendientes' and c['al']=='Por cobrar, hay pendientes' and not any(ch.isdigit() for ch in f['al']+c['al']),'aria-label sin cifras («…, hay pendientes»)',(f['al'],c['al']))
    chk(not f['n'] and not c['n'],'Sin el número grande (.n) en las tarjetas del móvil')
    chk(abs(f['top']-c['top'])<1 and abs(f['w']-c['w'])<1 and abs(f['h']-c['h'])<1,'Fianzas y Por cobrar juntas en la misma fila y con el mismo tamaño',(f['top'],c['top'],f['w'],c['w']))
    chk(abs(f['h']-64)<1.5 and f['w']>=44,'Tarjetas de 64 px de alto (≥ 44 px)',(f['w'],f['h']))
    chk(f['arr'] and c['arr'] and not f['plus'] and not c['plus'],'Indicador «→» (el del escritorio), no «+»')
    chk(not f['exp'] and not c['exp'],'Sin aria-expanded ni aria-controls')
    chk(f['on'] and c['on'] and f['gold'] and c['gold'] and f['tgold'] and c['tgold'],'Con pendientes: borde y título dorados')
    chk(J("!document.querySelector('#PC .dh-fp,#dhP-fz,#dhP-pc')"),'Ningún desplegable en el Inicio (aunque el móvil tenga las claves antiguas de #163 a «1»)')
    chk(J("typeof _dashFzpc==='undefined'&&typeof _depRows==='undefined'&&typeof _pcListH==='undefined'&&typeof _depListH==='undefined'"),'Sin las funciones del desplegable ni las compartidas de #163')
    if H.CAPTURAS:
        J("document.getElementById('mainPage').scrollTop=0");W(300)
        pg.screenshot(path=os.path.join(H.CAPTURAS,'fzpc2-01-inicio.png'))
    # Lo que da la hoja llamada directamente (menú lateral)
    J("openPendingDeposits()");W(400);hFz=J("document.getElementById('SC').innerHTML");rFz=J(ROWS);J("closeSheet()");W(300)
    J("openPorCobrar()");W(400);hPc=J("document.getElementById('SC').innerHTML");rPc=J(ROWS);J("closeSheet()");W(300)
    # ── 2. Tocar «Fianzas»: la hoja de siempre ──
    pg.locator('#PC .dh-act').nth(1).tap();W(500)
    seg=J("[...document.querySelectorAll('#SC .d-seg button')].map(b=>[b.textContent,b.getAttribute('aria-pressed')])")
    chk(sh_open() and 'Fianzas de los alquileres' in sc(),'Al tocar «Fianzas» se abre la hoja de Fianzas')
    chk(seg==[['Pendientes','true'],['Retenidas','false'],['Todas','false']],'Con «Pendientes / Retenidas / Todas» y «Pendientes» marcada',seg)
    chk(J("document.getElementById('SC').innerHTML")==hFz and len(rFz)==nfz,'Idéntica a la hoja del menú (%d pendientes)'%nfz,len(rFz))
    if H.CAPTURAS:pg.screenshot(path=os.path.join(H.CAPTURAS,'fzpc2-02-hoja-fianzas.png'))
    pg.locator('#SC .d-seg button',has_text='Todas').tap();W(400)
    chk(J("(document.querySelector('#SC .d-seg button[aria-pressed=\"true\"]')||{}).textContent")=='Todas' and len(J(ROWS))>=len(rFz),'La pestaña «Todas» funciona')
    J("closeSheet()");W(300)
    # ── 3. Tocar «Por cobrar»: la hoja con el total arriba ──
    pg.locator('#PC .dh-act').nth(2).tap();W(500)
    chk(sh_open() and 'Lo que falta del alquiler' in sc(),'Al tocar «Por cobrar» se abre su hoja')
    chk(J("(document.querySelector('#SC .al-pd b')||{}).textContent")==J("fmtF(_porCobrar().tot)") and J("(document.querySelector('#SC .al-pd .q')||{}).textContent")=='Total · %d alquileres'%len(pc['rows']),'Con el total arriba (= _porCobrar, con céntimos)')
    chk(J("document.getElementById('SC').innerHTML")==hPc and len(rPc)==len(pc['rows']),'Idéntica a openPorCobrar()')
    # ── 4. Botones de las filas ──
    bid=J("_porCobrar().rows[0].b.id");nom=rPc[0][0]
    pg.locator('#SC .fz-r').first.locator('button').tap();W(600)
    chk('Detalle del alquiler' in sc() and nom in sc(),'Por cobrar: «Ver alquiler» abre la ficha',nom)
    pg.locator('#SC .al-cq button',has_text='Todo').tap();W(600)
    chk(J("_bkCobro(V.flatMap(v=>v.bookings||[]).find(b=>b.id===%r)).falta"%bid)==0,'Desde la ficha se cobra «Todo»')
    J("closeSheet()");W(300);nav(pg)
    pg.locator('#PC .dh-act').nth(2).tap();W(500)
    r2=J(ROWS)
    chk(sh_open() and len(r2)==len(rPc)-1 and ("'%s'"%bid) not in ' '.join(x[3] for x in r2),'Al volver a tocar «Por cobrar», un alquiler menos',len(r2))
    J("closeSheet()");W(300)
    pg.locator('#PC .dh-act').nth(1).tap();W(500)
    fz0=J("(document.querySelector('#SC .fz-r button').getAttribute('onclick').match(/'([^']+)'/)||[])[1]")
    pg.locator('#SC .fz-r').first.locator('button').tap();W(600)
    chk('Fianza reembolsable' in sc(),'Fianzas: «Ver alquiler» abre la ficha con su fianza')
    pg.locator('#SC .al-seg button',has_text='Devuelta').tap();W(500)
    chk(J("_fianzaStatus(V.flatMap(v=>v.bookings||[]).find(b=>b.id===%r))"%fz0)=='returned','Desde la ficha se marca la fianza como «Devuelta»')
    J("closeSheet()");W(300);nav(pg)
    pg.locator('#PC .dh-act').nth(1).tap();W(500)
    chk(sh_open() and len(J(ROWS))==len(rFz)-1,'Al volver a tocar «Fianzas», una pendiente menos')
    J("closeSheet()");W(300)
    chk(J("['deiros_dashFzOpen','deiros_dashPcOpen'].every(k=>localStorage.getItem(k)==='1')"),'La app no escribe ni usa las claves antiguas (se quedan como estaban)')
    ctx.close()
    # ── 5. Sin pendientes: sin dorado y la hoja con su estado vacío ──
    ctx,pg=H.open_app(br,data=vacio(),has_touch=True,is_mobile=True);J=pg.evaluate;nav(pg)
    f,c=J(ST,1),J(ST,2)
    chk(f['txt']=='FIANZAS' and c['txt']=='POR COBRAR' and f['al']=='Fianzas' and c['al']=='Por cobrar','Sin pendientes: el mismo título y aria-label simple')
    chk(not f['on'] and not c['on'] and not f['gold'] and not f['tgold'] and not c['tgold'],'Sin pendientes: borde y título neutros')
    pg.locator('#PC .dh-act').nth(1).tap();W=pg.wait_for_timeout;W(500)
    chk('Sin fianzas en esta lista' in J("document.getElementById('SC').textContent"),'Hoja de Fianzas vacía: «Sin fianzas en esta lista»')
    J("closeSheet()");W(300);pg.locator('#PC .dh-act').nth(2).tap();W(500)
    chk('Nada por cobrar' in J("document.getElementById('SC').textContent"),'Hoja de Por cobrar vacía: «Nada por cobrar»')
    ctx.close()
    # ── 6. Tema claro ──
    ctx,pg=H.open_app(br,theme='light',has_touch=True,is_mobile=True);J=pg.evaluate;nav(pg)
    f=J(ST,1)
    chk(f['txt']=='FIANZAS' and f['on'] and f['gold'] and f['tgold'] and J("getComputedStyle(document.querySelector('#PC .dh-act:nth-child(2) .q')).color")=='rgb(106, 13, 173)','Tema claro: sin cifras, borde y título en morado de marca')
    pg.locator('#PC .dh-act').nth(1).tap();pg.wait_for_timeout(500)
    chk(J("document.getElementById('SH').classList.contains('open')"),'Tema claro: abre la hoja')
    ctx.close()
    # ── 7. Escritorio: sin cambios (3 tarjetas en fila, con sus cifras y «→», abren la hoja) ──
    ctx,pg=H.open_app(br,viewport={'width':1280,'height':900},extra=VIEJAS);J=pg.evaluate;nav(pg,600)
    f,c=J(ST,1),J(ST,2);pc=J("_porCobrar()")
    chk(J("(()=>{const a=[...document.querySelectorAll('#PC .dh-act')].map(e=>e.getBoundingClientRect());return a.length===3&&Math.abs(a[0].top-a[2].top)<1&&a[1].left<a[2].left;})()"),'Escritorio: Coches libres · Fianzas · Por cobrar en una fila')
    chk(f['n'] and c['n'] and f['arr'] and c['arr'] and J("!document.querySelector('#PC .dh-fpb')"),'Escritorio: con sus cifras y «→», como antes')
    chk(c['txt'].startswith('POR COBRAR · %d'%len(pc['rows'])) and c['al']==J("'Por cobrar: '+fmtF(_porCobrar().tot)+', %d alquileres'"%len(pc['rows'])),'Escritorio: «Por cobrar · N», el importe y su aria-label de siempre',(c['txt'],c['al']))
    pg.locator('#PC .dh-act').nth(2).click();pg.wait_for_timeout(500)
    chk(J("document.getElementById('SH').classList.contains('open')")and 'Lo que falta del alquiler' in J("document.getElementById('SC').textContent"),'Escritorio: «Por cobrar» abre su hoja')
    J("closeSheet()");pg.wait_for_timeout(300);pg.locator('#PC .dh-act').nth(1).click();pg.wait_for_timeout(500)
    chk(J("document.getElementById('SH').classList.contains('open')")and 'Fianzas de los alquileres' in J("document.getElementById('SC').textContent"),'Escritorio: «Fianzas» abre su hoja')
    ctx.close()
  H.fin()
if __name__=='__main__':run()
