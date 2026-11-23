# Reseñas de Google en settings (#139), sincronizadas entre dispositivos: Ajustes → «Reseñas de Google» (limpieza del
# enlace, avisos), data/main.settings.resenasUrl en la nube (rev, merge, aviso de conflicto, migración desde localStorage),
# copia v4 con settings (y copias antiguas sin settings), WhatsApp «Gracias + reseña» (solo Sin app devueltos) y atajos
# «Nuevo alquiler» / «Presupuesto» en la ficha del cliente. Con un Firestore falso COMPARTIDO entre varios «móviles».
# Origen: specs/d2/test_d2.py. Lo que se comparaba con main (pantallas, copia, dinero, textos de WhatsApp) se ha cambiado
# por textos y valores fijos o se ha quitado (pantallas sin enlace: ya las cubre test_pantallas.py).
# Uso: python3 tests/test_resenas.py
import sys,os,json,re,datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
HTML=H.INDEX;SHOTS=H.CAPTURAS
route,D0,FAKE=H.route,H.datos(),H.FAKE
g={'P':"document.getElementById('mainPage')",'D':D0,'route':route,'FAKE':FAKE}
J0_COMPANY=json.dumps(H.COMPANY)
from playwright.sync_api import sync_playwright
errs=H.ERRS;chk=H.chk
SETUP=r"""
(()=>{const hoy=todayStr(),A=n=>addDays(hoy,n),G=id=>V.find(v=>v.id===id);
const bk=(id,s,e,x)=>Object.assign({id,startDate:s,startTime:'10:00',endDate:e,endTime:'10:00',platform:'sinapp',amount:300,finance:[],fianza:0,paid:true,cobrado:true,abonoReserva:300,delivered:true},x||{});
G('v1').bookings.push(bk('gA',A(-12),A(-9),{clientName:'Gema Gracias',clientPhone:'600 000 010',returned:true,deliveryPlace:'Pinto centro'}));       // devuelto, sin fianza
G('v2').bookings.push(bk('gB',A(-30),A(-26),{clientName:'Bruno Fianza',clientPhone:'600 000 011',returned:true,fianza:200,fianzaStatus:'returned',fianzaReturnedAt:new Date().toISOString(),abonoReserva:500})); // fianza devuelta
G('v5').bookings.push(bk('gC',A(-40),A(-35),{clientName:'Carla Cancelada',clientPhone:'600 000 012',returned:true,cancelled:true}));               // cancelada
G('v3').bookings.push(bk('gD',A(-60),A(-57),{platform:'amovens',clientName:'Dani Amovens',clientPhone:'600 000 013',returned:true}));            // Amovens devuelto
G('v4').bookings.push(bk('gE',A(-70),A(-67),{platform:'getaround',clientName:'Eva Getaround',clientPhone:'600 000 014',returned:true,fianza:200,fianzaStatus:'returned',fianzaReturnedAt:new Date().toISOString()})); // Getaround con fianza devuelta
G('v1').bookings.push(bk('gF',A(-50),A(-47),{platform:'direct',clientName:'Fede Directo',clientPhone:'600 000 015',returned:true}));             // 'direct' antiguo = Sin app
CL.push({id:'k9',name:'Gema Gracias',dni:'00000009X',phone:'600 000 010',bookingIds:['gA'],birthdate:'1988-02-02',licenseExp:A(800)});
V.forEach(v=>(v.bookings||[]).forEach(b=>{if(/^g/.test(b.id))proRataEntries(b.startDate,b.endDate,b.amount,b.platform,'',b.id).forEach(e=>v.finances.push(Object.assign(e,{vehicleId:v.id})));}));
try{_invalidateRsCache()}catch(e){}
_saveToCloud=async()=>{};window.__CF=[];window.confirm=m=>{__CF.push(String(m));return true;};
window.__waT=id=>{_waPick('b',id);const r={pills:[...document.querySelectorAll('.wa-p button')].map(b=>[b.textContent,b.getAttribute('aria-pressed')]),T:_waT.map(t=>[t[0],t[2]]),tx:(document.getElementById('waTx')||{}).value,nt:(()=>{const e=document.getElementById('waNt');return e?getComputedStyle(e).display:'(no existe)';})()};return r;};
return true;})()
"""
def ctxpage(br,path):
    ctx=H.new_context(br,viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True,is_mobile=True);ctx.route('**/*',route)
    ctx.add_init_script("window.__DATA=%s;localStorage.setItem('wg_theme','dark');localStorage.setItem('deiros_lastBackupAt',new Date().toISOString());window.alert=m=>{(window.__AL=window.__AL||[]).push(String(m))};"%json.dumps(D0))
    ctx.add_init_script(FAKE)
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(path.split('/')[-2]+': '+str(e)))
    pg.goto('file://'+os.path.abspath(path));pg.wait_for_timeout(2000)
    return ctx,pg
TXT=r"""()=>{const o={};const t=()=>document.getElementById('PC').innerText.replace(/\s+/g,' ');
  for(const v of ['dashboard','rentals','vehicles','clients','quotes','biz','owners','agenda'])o[v]=(nav(v),t());
  nav('clients');_clientDetail='c1';renderClientDetail(document.getElementById('PC'));o.ficha=t();
  openNewRentalPicker();o.picker=document.getElementById('SC').innerText.replace(/\s+/g,' ');closeSheet();
  o.cf=_waTxCf(V[0].bookings.find(b=>b.id==='gA'),V[0]);o.rd=_waTxRd(V[0].bookings.find(b=>b.id==='gA'),V[0]);
  const vB=V.find(v=>v.bookings.some(b=>b.id==='gB'));o.fz=_waTxFz(vB.bookings.find(b=>b.id==='gB'),vB);
  o.waIn=(_waPick('b','b3'),_waT.map(t=>[t[0],t[1],t[2]]));_waClose();o.waB=(_waPick('b','gB'),_waT.map(t=>[t[0],t[1],t[2]]));_waClose();
  const bo=_backupObject();delete bo.exportedAt;o.settings=JSON.stringify(bo.settings);delete bo.settings;o.backup=JSON.stringify(bo);o.company=localStorage.getItem('deiros_company');
  const pl=_cloudPayload(7);delete pl.updatedAt;o.cloudSettings=JSON.stringify(pl.settings);delete pl.settings;o.payload=JSON.stringify(pl);
  return o;}"""
# ── Firestore FAKE compartido (sincronización entre dispositivos) ──
STUB2=r"""window.firebase={initializeApp(){},auth(){return{onAuthStateChanged(cb){setTimeout(()=>cb({uid:'demo'}),30)},signOut(){},signInWithEmailAndPassword(){return Promise.reject()}}},
firestore(){const mk=p=>({collection(n){return {doc(i){return mk(p+'/'+n+'/'+i)}}},
  get:async()=>{if(/\/data\/main$/.test(p)){const t=await window.__fsGet();return {exists:t!=null,data:()=>JSON.parse(t)};}return {exists:true,data:()=>JSON.parse(JSON.stringify(window.__DATA))};},
  set:async(v,o)=>{if(/\/data\/main$/.test(p))await window.__fsSet(JSON.stringify(v),!!(o&&o.merge));},update:async()=>{},delete:async()=>{},onSnapshot(){return()=>{}}});
  return {collection(n){return {doc(i){return mk(n+'/'+i)}}},enablePersistence:async()=>{},
    runTransaction:async fn=>{const W=[];const r=await fn({get:x=>x.get(),set:(x,v,o)=>W.push([x,v,o])});for(const [x,v,o] of W)await x.set(v,o);return r;}};}};"""
STORE={'doc':None,'writes':0}
def fs_merge(dst,src):  # set(...,{merge:true}) de Firestore: los mapas no vacíos se mezclan campo a campo; el resto sustituye
    for k,v in src.items():
        if isinstance(v,dict) and v and isinstance(dst.get(k),dict): fs_merge(dst[k],v)
        else: dst[k]=v
def fs_get(): return None if STORE['doc'] is None else json.dumps(STORE['doc'])
def fs_set(t,merge):
    v=json.loads(t);STORE['writes']+=1
    if merge and STORE['doc'] is not None: fs_merge(STORE['doc'],v)
    else: STORE['doc']=v
def device(br,local_company=None):
    ctx=H.new_context(br,viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True,is_mobile=True)
    ctx.route('**/*',lambda r:r.fulfill(body=STUB2,content_type='text/javascript') if 'firebase-app-compat' in r.request.url else route(r))
    ctx.expose_function('__fsGet',fs_get);ctx.expose_function('__fsSet',fs_set)
    ctx.add_init_script("window.__DATA=%s;localStorage.setItem('wg_theme','dark');localStorage.setItem('deiros_lastBackupAt',new Date().toISOString());window.alert=m=>{(window.__AL=window.__AL||[]).push(String(m))};window.confirm=()=>true;"%json.dumps(D0))
    ctx.add_init_script(FAKE)
    if local_company is not None: ctx.add_init_script("if(!sessionStorage.getItem('__lc')){sessionStorage.setItem('__lc','1');localStorage.setItem('deiros_company',%s);}"%json.dumps(json.dumps(local_company)))
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append('sync: '+str(e)))
    pg.goto('file://'+os.path.abspath(HTML));pg.wait_for_timeout(2000)
    return ctx,pg
def sync(br):
    print('── Sincronización entre dispositivos (Firestore FAKE compartido) ──')
    STORE['doc']=json.loads(json.dumps(D0));STORE['doc'].pop('settings',None)
    L1='https://g.page/r/SYNC111/review';L2='https://g.page/r/OTRO222/review';LL='https://g.page/r/LOCAL333/review'
    def typ(pg,val):
        pg.evaluate("v=>{openReviewSettings();const i=document.getElementById('rvUrl');i.value=v;i.dispatchEvent(new Event('input',{bubbles:true}));_rvSave();}",val);pg.wait_for_timeout(1800)
    rev=lambda:STORE['doc'].get('rev')
    cA,A=device(br);cB,B=device(br)
    st=A.evaluate("({u:_rvUrl(),ok:_loadedOK,h:_holdCloudWrite,v:V.length})")
    chk(st['u']=='' and st['ok'] and not st['h'],'Documento antiguo sin settings: carga bien y sin enlace',st)
    r0=rev() or 0;nv=len(STORE['doc']['vehicles'])
    typ(A,'  g.page/r/SYNC111/review?utm_source=qr ')
    chk(STORE['doc'].get('settings')=={'resenasUrl':L1} and rev()==r0+1 and len(STORE['doc']['vehicles'])==nv,'Dispositivo A guarda → data/main.settings.resenasUrl limpio, rev+1, el resto intacto',[STORE['doc'].get('settings'),rev()])
    chk('resenasUrl' not in json.loads(A.evaluate("localStorage.getItem('deiros_company')")),'A: nada en localStorage')
    cC,C=device(br)
    sc=C.evaluate("(()=>{openReviewSettings();const r={u:_rvUrl(),i:document.getElementById('rvUrl').value};closeSheet();_waPick('b','b41');r.tx=document.getElementById('waTx').value;r.p=[...document.querySelectorAll('.wa-p button')].map(b=>b.textContent);_waClose();return r;})()")
    chk(sc['u']==L1 and sc['i']==L1,'Dispositivo B (nuevo) lo ve en Ajustes',sc)
    chk('Gracias + reseña' in sc['p'] and L1 in sc['tx'],'B: «Gracias + reseña» con el enlace de A',sc['p'])
    # Conflicto: un dispositivo cargado antes (rev viejo) intenta guardar → aviso de siempre y la nube no cambia
    typ(B,L2)
    cf=B.evaluate("({d:!!document.getElementById('cloudConflict'),t:(document.getElementById('cloudConflict')||{}).textContent||''})")
    chk(cf['d'] and 'Hay cambios hechos desde otro dispositivo' in cf['t'] and STORE['doc']['settings']=={'resenasUrl':L1},'Conflicto: el dispositivo desfasado ve el aviso de siempre y no pisa la nube',[cf['d'],STORE['doc']['settings']])
    # Quitar en C → vacío para todos
    typ(C,'')
    cD,Dd=device(br)
    chk(STORE['doc']['settings']=={'resenasUrl':''} and Dd.evaluate("_rvUrl()")=='','Quitar en un dispositivo: la nube queda «» y otro dispositivo lo ve vacío',STORE['doc']['settings'])
    for c in (cA,cB,cC,cD):c.close()
    # Migración desde localStorage (nube vacía)
    base=json.loads(J0_COMPANY)
    cE,E=device(br,dict(base,resenasUrl='  g.page/r/LOCAL333/review?utm_source=x'));E.wait_for_timeout(1200)
    le=json.loads(E.evaluate("localStorage.getItem('deiros_company')"))
    chk(STORE['doc']['settings']=={'resenasUrl':LL} and E.evaluate("_rvUrl()")==LL,'Migración: el enlace local sube limpio a la nube (estaba vacía)',STORE['doc']['settings'])
    chk('resenasUrl' not in le and le.get('nombre')=='DEIROS' and le.get('ciudad')=='Pinto','Migración: tras subirlo se borra la copia local; el resto de datos de empresa sigue',le)
    E.reload();E.wait_for_timeout(2200);w0=STORE['writes']
    chk(E.evaluate("_rvUrl()")==LL and STORE['writes']==w0,'Al volver a abrir: sin migrar otra vez')
    cF,Fp=device(br);chk(Fp.evaluate("_rvUrl()")==LL,'Otro dispositivo ve el enlace migrado')
    # La nube ya tiene enlace: la copia local de otro dispositivo no lo pisa y se borra al guardar
    cG,G=device(br,dict(base,resenasUrl=L2));G.wait_for_timeout(1200)
    chk(G.evaluate("_rvUrl()")==LL and STORE['doc']['settings']=={'resenasUrl':LL},'Nube con enlace: la copia local no la pisa',G.evaluate("_rvUrl()"))
    G.evaluate("save()");G.wait_for_timeout(1800)
    lg=json.loads(G.evaluate("localStorage.getItem('deiros_company')"))
    chk('resenasUrl' not in lg and STORE['doc']['settings']=={'resenasUrl':LL},'…y tras el primer guardado se borra la copia local',lg)
    for c in (cE,cF,cG):c.close()
def run():
  with sync_playwright() as p:
    br=H.launch(p)
    # Textos y pestañas esperados (antes se sacaban de main)
    FZ='Hola Bruno, ya te hemos devuelto la fianza del Fiat: 200,00 €.\n\nGracias por alquilar con Deiros. Aquí nos tienes para la próxima.\n\nDeiros · deiros.net'
    refT={'fz':FZ,'waB':[['fz','Fianza devuelta',FZ]]}
    refPk={'gD':['Confirmación','Recordatorio','En blanco'],'gE':['Confirmación','Recordatorio','Fianza devuelta','En blanco'],'b3':['Confirmación','Recordatorio','En blanco']}
    ctx,pg=ctxpage(br,HTML);J=lambda js,a=None:pg.evaluate(js,a);W=lambda ms=400:pg.wait_for_timeout(ms)
    J(SETUP)
    def tap(loc):
        try: loc.click(timeout=3000)
        except Exception as e: chk(False,'Toque',str(e).split('\n')[0][:160])
    co=lambda:json.loads(J("localStorage.getItem('deiros_company')") or '{}')
    aj=lambda:J("JSON.parse(JSON.stringify(AJ))")
    CO0=co()
    # ── 0. Sin enlace y sin tocar nada ──
    T=J(TXT)
    chk(T['settings']=='{"resenasUrl":""}' and T['cloudSettings']=='{"resenasUrl":""}','Sin enlace: la copia v4 y data/main llevan settings {resenasUrl:""}',[T['settings'],T['cloudSettings']])
    chk('resenasUrl' not in (T['company'] or ''),'Los datos de empresa (localStorage) no llevan el enlace',T['company'])
    chk(H.N(T['fz'])==FZ,'«Fianza devuelta» de Bruno: texto exacto',T['fz'])
    chk('WhatsApp Nuevo alquiler Presupuesto' in T['ficha'],'Ficha del cliente: «WhatsApp», «Nuevo alquiler» y «Presupuesto»',T['ficha'][:160])
    # ── 1. Ficha del cliente → Nuevo alquiler (varios coches: selector, sin coche preelegido) ──
    J("nav('clients');_clientDetail='c1';renderClientDetail(document.getElementById('PC'))");W()
    bs=pg.locator('.cl-nw button');chk(bs.count()==2,'Ficha: 2 botones',bs.count())
    hs=J("[...document.querySelectorAll('.cl-nw button')].map(b=>[Math.round(b.getBoundingClientRect().height),Math.round(b.getBoundingClientRect().top),b.scrollWidth<=b.clientWidth])")
    chk(all(h[0]>=44 and h[2] for h in hs) and hs[0][1]==hs[1][1],'Botones de la ficha ≥ 44 px, en una fila y sin cortar el texto (390 px)',hs)
    pg.set_viewport_size({'width':340,'height':844});W(200)
    hs=J("[...document.querySelectorAll('.cl-nw button')].map(b=>[Math.round(b.getBoundingClientRect().height),Math.round(b.getBoundingClientRect().top),b.scrollWidth<=b.clientWidth,Math.round(b.getBoundingClientRect().right)<=innerWidth])")
    chk(all(h[0]>=44 and h[2] and h[3] for h in hs),'340 px: sin desbordar (uno debajo del otro si no caben)',hs)
    pg.set_viewport_size({'width':390,'height':844});W(200)
    if SHOTS:J("document.querySelectorAll('.d-toast').forEach(e=>e.remove())");pg.screenshot(path=SHOTS+'/d2-1-ficha-cliente.png')
    tap(pg.locator('.cl-nw button',has_text='Nuevo alquiler'));W()
    sub=J("document.querySelector('#SC .ssub').textContent");chk(sub=='¿Para qué vehículo? · Alejandro José Martínez de la Fuente','Selector: subtítulo con el cliente',sub)
    chk(J("document.querySelectorAll('#nrPickList .nr-pick').length")==J("V.filter(v=>!v.archived).length"),'Selector: todos los coches activos, ninguno elegido')
    tap(pg.locator('#nrPickList .nr-pick').nth(1));W(600)
    st=J("(()=>{const i=document.getElementById('rClientPicker'),g=id=>(document.getElementById(id)||{}).value;return {n:i&&i.value,id:i&&i.dataset.clId,ph:g('rCPvis'),dni:g('rCDNIvis'),m:[g('rCN'),g('rCP'),g('rCDNI')],addr:g('rClAddr'),st:document.getElementById('rClStatus').textContent,av:AV,t:document.querySelector('#SC .stitle').textContent};})()")
    chk(st['t']=='Nuevo alquiler' and st['n']=='Alejandro José Martínez de la Fuente' and st['id']=='c1','Alta: cliente ya elegido (nombre y ficha)',st)
    chk(st['ph']=='600 000 002' and st['dni']=='00000001R' and st['m']==['Alejandro José Martínez de la Fuente','600 000 002','00000001R'] and st['addr'].startswith('C/ Ejemplo'),'Alta: teléfono, DNI, copias ocultas y «Más datos» como el buscador')
    chk('Ficha completa' in st['st'],'Alta: estado de la ficha',st['st'])
    vid=st['av'];n0=J("id=>V.find(v=>v.id===id).bookings.length",vid)
    J("document.getElementById('rSD').value=addDays(todayStr(),40);document.getElementById('rED').value=addDays(todayStr(),43);document.getElementById('rAmt').value='120';_rwGo(2);_rwGo(3);submitRental()");W(600)
    nb=J("([id,n])=>{const v=V.find(x=>x.id===id);if(v.bookings.length<=n)return null;const b=v.bookings[v.bookings.length-1];return {c:b.clientName,p:b.clientPhone,d:b.clientDni,l:CL.find(c=>c.id==='c1').bookingIds.includes(b.id),n:CL.filter(c=>c.name===b.clientName).length};}",[vid,n0])
    chk(nb and nb['c']=='Alejandro José Martínez de la Fuente' and nb['p']=='600 000 002' and nb['d']=='00000001R' and nb['l'] and nb['n']==1,'Registrar: alquiler con el cliente, enlazado a su ficha y sin duplicarla',nb)
    chk(J("CV")=='clients' and not J("AV"),'Tras registrar vuelve a Clientes (como desde Alquileres)')
    # Un solo coche activo: directo al alta con el cliente
    J("window.__arch=V.filter(v=>!v.archived&&v.id!=='v4').map(v=>v.id);V.forEach(v=>{if(__arch.includes(v.id))v.archived=true;});openNewRentalPicker('k9')");W(500)
    s1=J("({t:document.querySelector('#SC .stitle').textContent,av:AV,n:document.getElementById('rClientPicker').value,id:document.getElementById('rClientPicker').dataset.clId,ph:document.getElementById('rCPvis').value})")
    chk(s1['t']=='Nuevo alquiler' and s1['av']=='v4' and s1['n']=='Gema Gracias' and s1['id']=='k9' and s1['ph']=='600 000 010','Un solo coche: alta directa con el cliente',s1)
    J("closeSheet();V.forEach(v=>{if(__arch.includes(v.id))v.archived=false;})");W()
    # Sin cliente (botón de siempre): nada preelegido
    J("openNewRentalPicker()");chk(J("document.querySelector('#SC .ssub').textContent")=='¿Para qué vehículo?','Selector sin cliente: como siempre')
    tap(pg.locator('#nrPickList .nr-pick').first);W(500)
    chk(J("document.getElementById('rClientPicker').value===''&&document.getElementById('rClientPicker').dataset.clId===''"),'Alta sin cliente: buscador vacío')
    J("closeSheet()");W()
    J("openNewRentalPicker('no-existe')");chk(J("document.querySelector('#SC .ssub').textContent")=='¿Para qué vehículo?','Ficha inexistente: como sin cliente');J("closeSheet()");W()
    # ── 2. Ficha del cliente → Presupuesto ──
    J("nav('clients');_clientDetail='c1';renderClientDetail(document.getElementById('PC'))");W()
    tap(pg.locator('.cl-nw button',has_text='Presupuesto'));W(500)
    q=J("({t:document.querySelector('#SC .stitle').textContent,n:document.getElementById('qClient').value,id:document.getElementById('qClient').dataset.clId,v:document.getElementById('qVehicle').value})")
    chk(q['t']=='Nuevo presupuesto' and q['n']=='Alejandro José Martínez de la Fuente' and q['id']=='c1' and q['v']=='','Presupuesto: cliente ya elegido, sin coche',q)
    J("document.getElementById('qVehicle').value='v1';_loadQuoteExtrasUpdate();document.getElementById('qStart').value=addDays(todayStr(),50);document.getElementById('qEnd').value=addDays(todayStr(),53);_calcQuoteTotal();_saveQuote()");W(500)
    qq=J("({n:QT[0].clientName,id:QT[0].clientId,f:QT[0].fianza})");chk(qq['n']=='Alejandro José Martínez de la Fuente' and qq['id']=='c1' and qq['f']==200,'Presupuesto guardado con clientId de la ficha',qq)
    # ── 3. Ajustes → Reseñas de Google ──
    J("nav('dashboard')");W()
    J("openHamburger()");W(400);tap(pg.locator('.hmenu-item',has_text='Reseñas de Google'));W(500)
    chk(J("document.querySelector('#SC .stitle').textContent.trim()")=='Reseñas de Google','Menú → hoja «Reseñas de Google»')
    chk('En tu Perfil de Empresa de Google → Pedir reseñas → copia el enlace corto.' in J("document.getElementById('SC').textContent"),'Ayuda corta')
    chk(J("({t:document.getElementById('rvUrl').type,m:document.getElementById('rvUrl').inputMode})")=={'t':'url','m':'url'},'Teclado de enlaces')
    def save(val):
        J("v=>{const i=document.getElementById('rvUrl');i.value=v;i.dispatchEvent(new Event('input',{bubbles:true}));}",val);W(150)
        stt=J("({c:document.getElementById('rvSt').className,t:document.getElementById('rvSt').textContent})")
        J("document.querySelectorAll('.d-toast').forEach(e=>e.remove());_rvSave()");W(150)
        tt=J("[...document.querySelectorAll('.d-toast')].map(e=>e.className+'|'+e.textContent)")
        return stt,aj(),tt
    stt,c,tt=save('  https://g.page/r/CAbc123XYZ/review?utm_source=qr&utm_medium=print  ')
    chk(c=={'resenasUrl':'https://g.page/r/CAbc123XYZ/review'} and co()==CO0,'Guarda limpio (sin espacios ni utm_*) en los ajustes (AJ); los datos de empresa no cambian',[c,co()])
    chk('Se guarda en la nube: lo verás en todos tus dispositivos y va en la copia de seguridad.' in J("(openReviewSettings(),document.getElementById('SC').textContent)"),'Ayuda: se guarda en la nube');J("closeSheet()")
    chk(stt['c']=='rv-st ok' and 'Enlace de Google' in stt['t'] and 'Se guardará: https://g.page/r/CAbc123XYZ/review' in stt['t'],'Estado en el momento: Google + cómo quedará',stt)
    chk(len(tt)==1 and ' ok|' in tt[0] and 'Enlace de reseñas guardado' in tt[0],'Aviso: guardado',tt)
    if SHOTS:
        J("openReviewSettings()");J("v=>{const i=document.getElementById('rvUrl');i.value=v;i.dispatchEvent(new Event('input',{bubbles:true}));}",'g.page/r/CAbc123XYZ/review?utm_source=qr');W(300);J("document.querySelectorAll('.d-toast').forEach(e=>e.remove())");pg.screenshot(path=SHOTS+'/d2-2-ajustes-resenas.png');J("closeSheet()")
    J("openReviewSettings()");chk(J("document.getElementById('rvUrl').value")=='https://g.page/r/CAbc123XYZ/review','Al volver a abrir: el enlace guardado');J("closeSheet()")
    for raw,exp in [('g.page/r/ CAbc 123/review','https://g.page/r/CAbc123/review'),
                    ('maps.app.goo.gl/AbCdEf123?g_st=ic','https://maps.app.goo.gl/AbCdEf123'),
                    ('https://search.google.com/local/writereview?placeid=ChIJ_abc123&utm_campaign=x&fbclid=y','https://search.google.com/local/writereview?placeid=ChIJ_abc123'),
                    ('https://www.google.com/maps/place/Deiros/@40.2,-3.7,17z?entry=ttu&g_ep=EgoyMDI2&gclid=z','https://www.google.com/maps/place/Deiros/@40.2,-3.7,17z'),
                    ('https://www.google.es/search?q=deiros+pinto&sxsrf=AB&ved=0x#lrd=0x0:0x1,3','https://www.google.es/search?q=deiros+pinto#lrd=0x0:0x1,3'),
                    ('http://g.page/r/X/review','http://g.page/r/X/review')]:
        J("openReviewSettings()");stt,c,tt=save(raw)
        chk(c.get('resenasUrl')==exp and stt['c']=='rv-st ok' and ' ok|' in (tt or [''])[0],'Limpieza y Google: '+raw,c.get('resenasUrl'))
    for raw,exp in [('bit.ly/deiros','https://bit.ly/deiros'),('https://evil-google.com/r','https://evil-google.com/r'),('https://google.com.example.io/x','https://google.com.example.io/x')]:
        J("openReviewSettings()");stt,c,tt=save(raw)
        chk(c.get('resenasUrl')==exp and stt['c']=='rv-st w' and 'No parece un enlace de Google' in stt['t'] and len(tt)==1 and ' warn|' in tt[0],'No es de Google: avisa y guarda · '+raw,[c.get('resenasUrl'),tt])
    J("openReviewSettings()");stt,c,tt=save('   ')
    chk(c=={'resenasUrl':''} and co()==CO0 and 'quitado' in (tt or [''])[0],'Vacío: quita el enlace (queda «» en los ajustes)',[c,tt])
    J("openReviewSettings()");stt,c,_=save('https://g.page/r/CAbc123XYZ/review')
    chk('resenasUrl' not in co() and 'resenasUrl' not in J("_backupObject().company"),'El enlace no va en los datos de empresa (company) ni en localStorage')
    chk(J("(()=>{const o=AJ;AJ={resenasUrl:42};const r=_rvUrl();AJ=o;return r;})()")=='','Valor raro (no texto): se ignora')
    # ── 4. Copia v4 ──
    bo=J("(()=>{const b=_backupObject();return {v:b.version,s:b.settings,c:'resenasUrl' in b.company,e:_validateBackup(JSON.parse(JSON.stringify(b))),k:Object.keys(b).join(',')};})()")
    chk(bo['v']==4 and bo['s']=={'resenasUrl':'https://g.page/r/CAbc123XYZ/review'} and not bo['c'] and bo['e']=='' and bo['k']=='version,exportedAt,vehicles,bizFinances,owners,clients,recurring,quotes,settings,company,photos','Copia v4: las claves de siempre + settings con el enlace, y valida',bo)
    def restore(settings,label):
        J("""st=>{const b=_backupObject();b.company={nombre:'DEIROS COPIA',ciudad:'Pinto'};if(st==='__sin__')delete b.settings;else b.settings=st;const f=new File([JSON.stringify(b)],'copia.json',{type:'application/json'});
          window.__CF=[];importData({target:{files:[f],value:''}});}""",settings);W(1500)
        return aj(),J("window.__AL||[]")
    J("window.__AL=[]")
    c,al=restore({'resenasUrl':'https://g.page/r/NUEVO/review'},'con')
    chk(c=={'resenasUrl':'https://g.page/r/NUEVO/review'} and co().get('nombre')=='DEIROS COPIA' and 'resenasUrl' not in co(),'Restaurar copia con settings: se usa el enlace de la copia',[c,co()])
    c,al=restore('__sin__','sin')
    chk(c=={'resenasUrl':'https://g.page/r/NUEVO/review'},'Restaurar copia antigua sin settings: válida y se conserva el enlace actual',c)
    c,al=restore({},'objeto vacío')
    chk(c=={'resenasUrl':'https://g.page/r/NUEVO/review'},'Restaurar copia con settings sin resenasUrl: se conserva',c)
    c,al=restore({'resenasUrl':''},'vacío')
    chk(c=={'resenasUrl':''} and J("_rvUrl()")=='','Restaurar copia con el enlace vacío: queda vacío',c)
    chk(not [a for a in al if 'inválido' in a.lower()],'Sin «Fichero inválido» en las copias buenas',al)
    for bad_,lbl in [('"texto"','settings no objeto'),('{"resenasUrl":42}','enlace no texto')]:
        J("window.__AL=[]");J("x=>{const b=_backupObject();b.settings=JSON.parse(x);const f=new File([JSON.stringify(b)],'copia.json',{type:'application/json'});importData({target:{files:[f],value:''}});}",bad_);W(800)
        al=J("window.__AL||[]");chk(any('Fichero inválido' in a and 'settings' in a for a in al) and J("_rvUrl()")=='','Copia con '+lbl+': «Fichero inválido» y no se restaura',al)
    chk(J("_validateBackup({vehicles:[],settings:null})")=='','settings: null = sin ajustes (válida)')
    J("AJ={resenasUrl:'https://g.page/r/CAbc123XYZ/review'}")
    J(SETUP) if J("!V.some(v=>v.bookings.some(b=>b.id==='gA'))") else None
    # ── 5. Plantilla «Gracias + reseña» ──
    LINK='https://g.page/r/CAbc123XYZ/review'
    r=J("__waT('gA')");_=J("_waClose()")
    vA=J("V.find(v=>v.bookings.some(b=>b.id==='gA')).name")
    EXP=('Hola Gema, gracias por alquilar con Deiros. Esperamos que el '+vA+' te haya ido genial.\n\n'
         'Si te ha gustado el servicio, ¿nos dejas una reseña en Google? Son 30 segundos y nos ayuda mucho:\n'+LINK+'\n\n'
         'Aquí nos tienes para la próxima.\n\nDeiros · deiros.net')
    chk([x[0] for x in r['pills']]==['Confirmación','Recordatorio','Gracias + reseña','En blanco'],'Devuelto sin fianza: pestañas',r['pills'])
    chk(r['pills'][2][1]=='true' and r['tx']==EXP,'Por defecto «Gracias + reseña» con nombre, coche, enlace y firma',r['tx'])
    chk(r['nt']=='none','Con enlace: sin aviso')
    if SHOTS:
        J("document.querySelectorAll('.d-toast').forEach(e=>e.remove());_waPick('b','gA')");W(500);pg.screenshot(path=SHOTS+'/d2-3-whatsapp-gracias.png');J("_waClose()")
    href=J("(()=>{_waPick('b','gA');const h=document.getElementById('waGo').href;_waClose();return h;})()")
    chk(href.startswith('https://wa.me/34600000010?text=') and 'g.page%2Fr%2FCAbc123XYZ%2Freview' in href,'Abrir WhatsApp: número y texto con el enlace',href[:90])
    rB=J("__waT('gB')");J("_waClose()")
    chk([x[0] for x in rB['pills']]==['Confirmación','Recordatorio','Fianza devuelta','Gracias + reseña','En blanco'] and rB['pills'][2][1]=='true','Fianza devuelta: sigue por defecto y se ofrece «Gracias + reseña»',rB['pills'])
    chk(H.N(rB['tx'])==refT['fz'] and LINK not in rB['tx'],'Con enlace: «Fianza devuelta» con su texto de siempre (sin reseña)',rB['tx'])
    chk([[t[0],H.N(t[1])] for t in rB['T'] if t[0]=='fz']==[t for t in [[x[0],x[2]] for x in refT['waB']] if t[0]=='fz'],'«Fianza devuelta» (plantilla de la hoja): texto exacto')
    for bid,pl in [('gD','Amovens'),('gE','Getaround')]:
        rp=J("__waT('%s')"%bid);J("_waClose()")
        chk([x[0] for x in rp['pills']]==refPk[bid] and 'Gracias + reseña' not in [x[0] for x in rp['pills']] and LINK not in rp['tx'] and rp['nt']=='none','%s devuelto: sin «Gracias + reseña» (pestañas fijas) ni enlace'%pl,[rp['pills'],refPk[bid]])
    rF=J("__waT('gF')");J("_waClose()")
    chk([x[0] for x in rF['pills']]==['Confirmación','Recordatorio','Gracias + reseña','En blanco'] and rF['pills'][2][1]=='true' and LINK in rF['tx'],"'direct' (Sin app antiguo): «Gracias + reseña» por defecto",rF['pills'])
    rC=J("__waT('gC')");J("_waClose()")
    chk('Gracias + reseña' not in [x[0] for x in rC['pills']],'Cancelado: sin «Gracias + reseña»',rC['pills'])
    rI=J("__waT('b3')");J("_waClose()")
    chk([x[0] for x in rI['pills']]==refPk['b3'],'En curso: Confirmación, Recordatorio y En blanco',rI['pills'])
    # Desde la ficha del cliente (WhatsApp de la ficha): último alquiler devuelto
    J("_waPick('c','k9')");rk=J("({p:[...document.querySelectorAll('.wa-p button')].map(b=>[b.textContent,b.getAttribute('aria-pressed')]),t:document.getElementById('waTx').value})");J("_waClose()")
    chk(['Gracias + reseña','true'] in rk['p'] and rk['t']==EXP,'Ficha del cliente → WhatsApp: «Gracias + reseña» por defecto',rk['p'])
    # Sin enlace
    J("AJ={resenasUrl:''}")
    r0=J("__waT('gA')")
    EXP0=EXP.replace('nos ayuda mucho:\n'+LINK+'\n','nos ayuda mucho.\n')
    chk(r0['tx']==EXP0 and LINK not in r0['tx'],'Sin enlace: sin la línea del enlace',r0['tx'])
    chk(r0['nt']=='flex' and 'Añade tu enlace de reseñas en Ajustes' in J("document.getElementById('waNt').textContent"),'Sin enlace: la hoja avisa',r0['nt'])
    nh=J("Math.round(document.getElementById('waNt').getBoundingClientRect().height)");chk(nh>=44,'Aviso ≥ 44 px',nh)
    J("_waSel(0)");chk(J("getComputedStyle(document.getElementById('waNt')).display")=='none','El aviso solo con «Gracias + reseña»')
    J("_waSel(2)");tap(pg.locator('#waNt'));W(500)
    chk(J("!document.querySelector('.wa-sh')&&document.querySelector('#SC .stitle').textContent.trim()==='Reseñas de Google'"),'Tocar el aviso abre Ajustes → Reseñas de Google')
    J("closeSheet()")
    rB0=J("__waT('gB')");J("_waClose()")
    chk(H.N(rB0['tx'])==refT['fz'],'Sin enlace: «Fianza devuelta» con su texto de siempre')
    vis=J("(()=>{_waPick('b','gA');const P=document.querySelector('.wa-p'),b=P.querySelector('[aria-pressed=true]'),r=b.getBoundingClientRect(),q=P.getBoundingClientRect();_waClose();return r.left>=q.left-1&&r.right<=q.right+1;})()")
    chk(vis,'La pestaña elegida queda a la vista')
    ctx.close()
    sync(br)
    chk(not errs,'Sin errores JS',errs)
    br.close()
run()
H.fin()
