# Presupuestos (Rafael, 26/11/2026): (1) «Convertido» se ve como «Aceptado» (KPI, chips, selector de estado); el valor guardado
# sigue siendo 'convertido' y los 'aceptado' antiguos se ven y cuentan igual. (2) Rechazo automático: al abrir la app (y al
# restaurar una copia) todo «Pendiente» cuyo inicio es anterior a hoy (fecha de Madrid) pasa a «Rechazado» y se guarda en la
# nube por el camino de siempre (rev + transacción). Hoy y mañana siguen pendientes; aceptados, rechazados y sin fecha válida
# no se tocan; sin nada que rechazar no se escribe; dos móviles a la vez sin aviso de conflicto; nube lenta; correcciones
# retenidas; volver a «Pendiente» avisa y se rechaza otra vez al abrir. Uso: python3 tests/test_presupuestos_estado.py
# Con DEIROS_CAPTURAS=<carpeta> guarda la lista de Presupuestos (390 px, oscuro).
import sys,os,json,copy
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
chk=H.chk;d=H.d
def qt(i,st,start,**k):
    q={'id':i,'num':'PRE-2026-%s'%i.upper(),'vehicleId':'v4','clientName':'Cliente '+i.upper(),'clientId':'','createdAt':d(-3)+'T10:00:00',
       'startDate':start,'startTime':'10:00','endDate':d(20),'endTime':'10:00','dur':3,'baseAmount':90,'extras':[],'discount':0,'fianza':200,'status':st,'totalAmount':90}
    q.update(k)
    if start is None:q.pop('startDate')
    return q
def datos(extra_q=True):
    D=H.datos()
    if extra_q:
        D['quotes']+=[qt('qa','pendiente',d(-1)),qt('qb','pendiente',d(0)),qt('qc','pendiente',d(1)),qt('qd','convertido',d(-5),bookingId='b4'),
                      qt('qe','aceptado',d(-4)),qt('qf','rechazado',d(3)),qt('qg','pendiente',''),qt('qh','pendiente',None),qt('qi','pendiente',d(-30))]
    return D
ST="Object.fromEntries(QT.map(q=>[q.id,q.status]))"
MAIN="users/demo/data/main"
NW="window.__FSOPS.filter(p=>p==='%s').length"%MAIN
CLOUD="JSON.parse(JSON.stringify(window.__FS['%s']))"%MAIN
TXT="document.getElementById('PC').innerText"
with H.playwright() as p:
    br=H.launch(p)
    # ── 1. Rechazo automático al abrir ──
    print('── 1. Rechazo automático al abrir la app ──')
    D1=datos()
    ctx,pg=H.open_app(br,data=D1,extra="window.alert=m=>{(window.__AL=window.__AL||[]).push(String(m))};window.confirm=()=>true;",wait=2500)
    J=lambda js,a=None:pg.evaluate(js,a);W=lambda ms=400:pg.wait_for_timeout(ms)
    s=J(ST)
    chk(s['qa']=='rechazado','Pendiente que empezó AYER → «Rechazado»',s['qa'])
    chk(s['qi']=='rechazado','Pendiente que empezó hace 30 días → «Rechazado»',s['qi'])
    chk(s['qb']=='pendiente','Pendiente que empieza HOY → sigue «Pendiente»',s['qb'])
    chk(s['qc']=='pendiente','Pendiente que empieza MAÑANA → sigue «Pendiente»',s['qc'])
    chk(s['q1']=='pendiente','Pendiente futuro de los datos de siempre → sigue «Pendiente»',s['q1'])
    chk(s['qd']=='convertido' and s['qe']=='aceptado' and s['q2']=='aceptado','Convertidos y aceptados antiguos (aunque su inicio ya pasó) no se tocan',[s['qd'],s['qe'],s['q2']])
    chk(s['qf']=='rechazado' and s['q3']=='rechazado','Rechazados (pasados y futuros) no se tocan',[s['qf'],s['q3']])
    chk(s['qg']=='pendiente' and s['qh']=='pendiente','Sin fecha de inicio (vacía o sin el campo) → no se toca',[s['qg'],s['qh']])
    cl=J(CLOUD)
    cs={q['id']:q['status'] for q in cl['quotes']}
    chk(cs==s,'La nube (data/main.quotes) tiene los mismos estados',cs)
    chk(cl['rev']==2 and J(NW)==1 and J("_loadedRev")==2,'Un solo guardado, por el camino de siempre: rev 1 → 2',[cl['rev'],J(NW),J("_loadedRev")])
    chk(len(cl['quotes'])==len(D1['quotes']) and 'qh' in cs and not any('startDate' in q for q in cl['quotes'] if q['id']=='qh'),'Mismos presupuestos; el que no tenía fecha sigue sin ella')
    keys0=sorted(D1['quotes'][3].keys());keys1=sorted([q for q in cl['quotes'] if q['id']=='qa'][0].keys())
    chk(keys0==keys1,'Sin campos nuevos en el presupuesto',keys1)
    chk(len(cl['vehicles'])==6 and cl['clients']==D1['clients'] and cl['owners']==D1['owners'],'El resto de data/main intacto')
    chk(not J("!!document.getElementById('cloudConflict')") and J("document.getElementById('loadingScreen').style.display")=='none','Sin aviso de conflicto y la app abierta')
    # Idempotente: otra pasada no cambia nada ni escribe
    n=J("_qtAutoReject()");r=J("_qtAutoRejectBoot()");W(1200)
    chk(n==0 and r=='ok' and J(NW)==1 and J(ST)==s,'Idempotente: otra pasada no cambia nada ni vuelve a escribir',[n,r,J(NW)])
    # ── 2. Pantalla: «Aceptado» en vez de «Convertido» ──
    print('── 2. «Convertido» se ve como «Aceptado» ──')
    J("nav('quotes')");W(500)
    k=J("[...document.querySelectorAll('#PC .qt-k>div')].map(e=>[e.querySelector('span').textContent,e.querySelector('b').textContent])")
    chk([x[0] for x in k]==['Total','Pendiente','Aceptado','Rechazado'],'KPI: Total · Pendiente · Aceptado · Rechazado',k)
    exp={'Total':12,'Pendiente':5,'Aceptado':3,'Rechazado':4}
    chk({a:int(b) for a,b in k}==exp,'KPI «Aceptado» = convertido + aceptado antiguos (3); los totales cuadran',k)
    chk('Convertido' not in J(TXT),'La lista no dice «Convertido» en ningún sitio')
    chips=J("Object.fromEntries([...document.querySelectorAll('#PC .qt-r')].map(r=>[r.querySelector('.s').textContent.split('· ').pop(),[r.querySelector('.chip').textContent,r.querySelector('.chip').className]]))")
    chk(chips['PRE-2026-QD']==['Aceptado','chip chip-blue'] and chips['PRE-2026-QE']==['Aceptado','chip chip-blue'] and chips['PRE-2026-0041']==['Aceptado','chip chip-blue'],"Chip: 'convertido' y 'aceptado' antiguo, iguales («Aceptado», azul)",[chips.get('PRE-2026-QD'),chips.get('PRE-2026-QE')])
    chk(chips['PRE-2026-QA']==['Rechazado','chip chip-red'] and chips['PRE-2026-QB']==['Pendiente','chip chip-amber'],'Chips de rechazado y pendiente como siempre',[chips.get('PRE-2026-QA'),chips.get('PRE-2026-QB')])
    if H.CAPTURAS:
        J("document.querySelectorAll('.d-toast,#saveStatus').forEach(e=>e.remove());window.scrollTo(0,0)");W(300)
        pg.screenshot(path=os.path.join(H.CAPTURAS,'qtacep-01-lista-presupuestos.png'))
    # Ficha y selector de estado de un convertido
    J("_quoteEditId='qd';showQuoteDetail(document.getElementById('PC'))");W(300)
    t=J(TXT)
    chk('Aceptado' in J("document.querySelector('#PC .qt-c .d-ch .chip').textContent") and 'Convertido' not in t,'Ficha de un convertido: chip «Aceptado», sin «Convertido»')
    chk('Ya convertido en alquiler' in t and 'Convertir en alquiler' not in t,'Ficha de un convertido: sigue «Ya convertido en alquiler» (sin botón Convertir)')
    J("openQuoteStatusMenu('qd')");W(400)
    m=J("[...document.querySelectorAll('.qt-so')].map(b=>[b.querySelector('.t').textContent,b.getAttribute('aria-pressed'),b.querySelector('.r').textContent,b.offsetHeight])")
    chk([x[0] for x in m]==['Pendiente','Rechazado','Aceptado'],'Selector de estado: Pendiente · Rechazado · Aceptado (sin «Convertido» ni opción duplicada)',m)
    chk(m[2][1]=='true' and m[2][2]=='Actual' and m[0][1]=='false','El convertido marca «Aceptado» como actual',m)
    chk(all(x[3]>=44 for x in m),'Opciones de al menos 44 px',[x[3] for x in m])
    J("closeSheet()");W(300)
    # Aceptado antiguo: la fila «Aceptado» es la actual; elegirla guarda 'convertido'
    J("_quoteEditId='qe';showQuoteDetail(document.getElementById('PC'))");W(300)
    chk('Convertir en alquiler' in J(TXT),"'aceptado' antiguo: sigue el botón «Convertir en alquiler» (como antes)")
    J("openQuoteStatusMenu('qe')");W(400)
    m=J("[...document.querySelectorAll('.qt-so')].map(b=>[b.querySelector('.t').textContent,b.getAttribute('aria-pressed')])")
    chk(m==[['Pendiente','false'],['Rechazado','false'],['Aceptado','true']],"'aceptado' antiguo: tres opciones y «Aceptado» como actual",m)
    w0=J(NW)
    pg.locator('.qt-so:has-text("Aceptado")').click();W(1500)
    chk(J("QT.find(q=>q.id==='qe').status")=='convertido' and J(NW)==w0+1,"Tocar «Aceptado» guarda 'convertido' (el valor de siempre)",J("QT.find(q=>q.id==='qe').status"))
    # Elegir «Aceptado» en un pendiente → 'convertido'
    J("openQuoteStatusMenu('qc')");W(300);pg.locator('.qt-so:has-text("Aceptado")').click();W(300)
    chk(J("QT.find(q=>q.id==='qc').status")=='convertido','Pendiente → «Aceptado» guarda \'convertido\'')
    # Convertir en alquiler → 'convertido', chip «Aceptado»
    J("CL.push({id:'cz',name:'Cliente QB',dni:'00000009Z',phone:'600 000 099',birthdate:'1980-01-01',bookingIds:[]});QT.find(q=>q.id==='qb').clientId='cz';QT.find(q=>q.id==='qb').vehicleId='v1';QT.find(q=>q.id==='qb').endDate=addDays(todayStr(),2)")
    J("convertQuoteToBooking('qb')");W(900)
    chk(J("QT.find(q=>q.id==='qb').status")=='convertido' and J("!!QT.find(q=>q.id==='qb').bookingId"),'Convertir en alquiler: estado \'convertido\' y bookingId, como siempre')
    J("closeSheet();nav('quotes')");W(400)
    k=J("Object.fromEntries([...document.querySelectorAll('#PC .qt-k>div')].map(e=>[e.querySelector('span').textContent,+e.querySelector('b').textContent]))")
    chk(k=={'Total':12,'Pendiente':3,'Aceptado':5,'Rechazado':4},'KPI tras aceptar dos y convertir uno: Pendiente 3 · Aceptado 5 · Rechazado 4',k)
    # Volver a «Pendiente» con el inicio pasado: aviso
    J("document.querySelectorAll('.d-toast').forEach(e=>e.remove());_quoteEditId='qa';showQuoteDetail(document.getElementById('PC'));openQuoteStatusMenu('qa')");W(300)
    pg.locator('.qt-so:has-text("Pendiente")').click();W(400)
    tt=J("[...document.querySelectorAll('.d-toast')].map(e=>e.textContent).join(' | ')")
    chk(J("QT.find(q=>q.id==='qa').status")=='pendiente' and 'al volver a abrir la app pasará a «Rechazado»' in tt,'Volver a «Pendiente» con el inicio pasado: se guarda y avisa de que se rechazará al abrir',tt)
    J("document.querySelectorAll('.d-toast').forEach(e=>e.remove());openQuoteStatusMenu('q1')");W(300);pg.locator('.qt-so:has-text("Rechazado")').click();W(200)
    J("openQuoteStatusMenu('q1')");W(300);pg.locator('.qt-so:has-text("Pendiente")').click();W(400)
    chk(not J("document.querySelectorAll('.d-toast').length"),'Con el inicio futuro, volver a «Pendiente» no avisa')
    W(1200);cl2=J(CLOUD)
    chk({q['id']:q['status'] for q in cl2['quotes']}['qa']=='pendiente','La nube guarda «Pendiente» (lo que eligió Rafael)')
    # Tema claro: el chip «Aceptado» con su color
    ctx.close()
    # ── 3. Al volver a abrir: se rechaza otra vez; sin nada que rechazar, no se escribe ──
    print('── 3. Volver a abrir ──')
    ctx,pg=H.open_app(br,data=cl2,wait=2500);J=lambda js,a=None:pg.evaluate(js,a)
    chk(J("QT.find(q=>q.id==='qa').status")=='rechazado' and J(CLOUD)['rev']==cl2['rev']+1,'Puesto a mano en «Pendiente» con el inicio pasado: al abrir, «Rechazado» otra vez (y se guarda)',[J("QT.find(q=>q.id==='qa').status"),J(CLOUD)['rev']])
    cl3=J(CLOUD);ctx.close()
    ctx,pg=H.open_app(br,data=cl3,wait=2500,theme='light');J=lambda js,a=None:pg.evaluate(js,a)
    chk(J(NW)==0 and J("_loadedRev")==cl3['rev'],'Abrir sin nada que rechazar: ninguna escritura (sin bucles)',[J(NW),J("_loadedRev")])
    J("nav('quotes')");pg.wait_for_timeout(400)
    c=J("(()=>{const e=[...document.querySelectorAll('#PC .qt-r .chip')].find(x=>x.textContent==='Aceptado');const s=getComputedStyle(e);return [s.color,s.backgroundColor,s.display]})()")
    chk(c and c[2]!='none','Tema claro: chip «Aceptado» visible',c)
    ctx.close()
    # Datos de siempre (sin pendientes pasados): no se escribe nada al abrir
    ctx,pg=H.open_app(br,wait=2500);J=lambda js,a=None:pg.evaluate(js,a)
    chk(J(NW)==0 and J(ST)=={'q1':'pendiente','q2':'aceptado','q3':'rechazado'},'Datos de siempre: nada que rechazar, ninguna escritura',J(ST))
    # Restaurar una copia con un pendiente pasado → rechazado y subido con la copia
    bo=J("JSON.parse(JSON.stringify(_backupObject()))");bo['quotes'].append(qt('qr','pendiente',d(-2)));bo['quotes'].append(qt('qs','pendiente',d(2)))
    J("window.alert=()=>{};window.confirm=()=>true");J(r"""o=>{const f=new File([JSON.stringify(o)],'copia.json',{type:'application/json'});importData({target:{files:[f],value:''}});}""",bo);pg.wait_for_timeout(2200)
    s=J(ST);cs={q['id']:q['status'] for q in J(CLOUD)['quotes']}
    chk(s.get('qr')=='rechazado' and s.get('qs')=='pendiente' and cs.get('qr')=='rechazado' and cs.get('qs')=='pendiente','Restaurar copia: el pendiente pasado entra «Rechazado» (también en la nube); el futuro sigue pendiente',[s.get('qr'),s.get('qs'),cs.get('qr')])
    ctx.close()
    # ── 4. Hora de Madrid ──
    print('── 4. Fecha de Madrid ──')
    Dm=H.datos();Dm['quotes']+=[qt('m19','pendiente','2026-11-19'),qt('m20','pendiente','2026-11-20')]
    ctx,pg=H.open_app(br,data=Dm,wait=2500,fecha='2026-11-20T00:30:00+01:00',tz='America/Caracas');J=lambda js,a=None:pg.evaluate(js,a)
    s=J(ST)
    chk(J("todayStr()")=='2026-11-19' and J("_qtHoyMadrid()")=='2026-11-20','Móvil en otra zona (19/11 allí, 20/11 00:30 en Madrid): hoy = 20/11',[J("todayStr()"),J("_qtHoyMadrid()")])
    chk(s['m19']=='rechazado' and s['m20']=='pendiente','Inicio 19/11 → rechazado; inicio 20/11 (hoy en Madrid) → pendiente',[s['m19'],s['m20']])
    ctx.close()
    Dm=H.datos();Dm['quotes']+=[qt('m19','pendiente','2026-11-19'),qt('m20','pendiente','2026-11-20')]
    ctx,pg=H.open_app(br,data=Dm,wait=2500,fecha='2026-11-20T23:59:00+01:00');J=lambda js,a=None:pg.evaluate(js,a)
    s=J(ST);chk(s['m20']=='pendiente' and s['m19']=='rechazado','A las 23:59 de Madrid, el que empieza hoy sigue pendiente',s)
    ctx.close()
    Dm=H.datos();Dm['quotes']+=[qt('m20','pendiente','2026-11-20')]
    ctx,pg=H.open_app(br,data=Dm,wait=2500,fecha='2026-11-21T00:01:00+01:00');J=lambda js,a=None:pg.evaluate(js,a)
    chk(J(ST)['m20']=='rechazado','A las 00:01 del día siguiente (Madrid), ya rechazado',J(ST))
    ctx.close()
    # ── 5. Correcciones retenidas (_holdCloudWrite): no se sube nada, pero se ve rechazado ──
    print('── 5. Correcciones retenidas ──')
    Dh=datos();Dh['vehicles'][0]['fuel']='Gasoil'
    ctx,pg=H.open_app(br,data=Dh,wait=2500);J=lambda js,a=None:pg.evaluate(js,a)
    chk(J("_holdCloudWrite") and J(NW)==0 and J(ST)['qa']=='rechazado' and J("!!document.getElementById('normNotice')"),'Con correcciones retenidas: no se sube nada (como siempre), el aviso sigue y en pantalla ya sale rechazado',[J("_holdCloudWrite"),J(NW)])
    J("document.querySelector('#normNotice .btn-pri').click()");pg.wait_for_timeout(1500)
    chk({q['id']:q['status'] for q in J(CLOUD)['quotes']}['qa']=='rechazado','«Subir la copia corregida» sube también el rechazo')
    ctx.close()
    # ── 6. Dos móviles a la vez (Firestore compartido) y nube lenta ──
    print('── 6. Dos móviles y nube lenta ──')
    STUB2=r"""window.firebase={initializeApp(){},auth(){return{onAuthStateChanged(cb){setTimeout(()=>cb({uid:'demo'}),30)},signOut(){},signInWithEmailAndPassword(){return Promise.reject()}}},
firestore(){const mk=p=>({collection(n){return {doc(i){return mk(p+'/'+n+'/'+i)}}},
  get:async()=>{if(/\/data\/main$/.test(p)){window.__GETS=(window.__GETS||0)+1;const t=await window.__fsGet();return {exists:t!=null,data:()=>JSON.parse(t)};}return {exists:false,data:()=>undefined};},
  set:async(v,o)=>{if(/\/data\/main$/.test(p))await window.__fsSet(JSON.stringify(v),!!(o&&o.merge));},update:async()=>{},delete:async()=>{},onSnapshot(){return()=>{}},
  where(){return {get:async()=>({docs:[],size:0,empty:true,forEach(){}})}},get docs(){return []}});
  return {collection(n){return {doc(i){return mk(n+'/'+i)},where(){return {get:async()=>({docs:[],size:0,empty:true,forEach(){}})}},get:async()=>({docs:[],size:0,empty:true,forEach(){}})}},enablePersistence:async()=>{},
    runTransaction:async fn=>{await new Promise(r=>setTimeout(r,window.__TXD||0));const W=[];const r=await fn({get:x=>x.get(),set:(x,v,o)=>W.push([x,v,o])});for(const [x,v,o] of W)await x.set(v,o);return r;}};}};
firebase.firestore.FieldValue={serverTimestamp:()=>new Date().toISOString()};firebase.firestore.FieldPath={documentId:()=>'__name__'};"""
    STORE={'doc':None,'writes':0}
    def fs_get():return None if STORE['doc'] is None else json.dumps(STORE['doc'])
    def fs_set(t,merge):
        v=json.loads(t);STORE['writes']+=1
        if merge and STORE['doc'] is not None:STORE['doc'].update(v)
        else:STORE['doc']=v
    def device(txd,tag):
        c=H.new_context(br);c.route('**/*',lambda r:r.fulfill(body=STUB2,content_type='text/javascript') if 'firebase-app-compat' in r.request.url else H.route(r))
        c.expose_function('__fsGet',fs_get);c.expose_function('__fsSet',fs_set)
        c.add_init_script("window.__TXD=%d;localStorage.setItem('wg_theme','dark');localStorage.setItem('deiros_lastBackupAt',new Date().toISOString());window.alert=()=>{};window.confirm=()=>true;"%txd)
        c.add_init_script(H.FAKE)
        g=c.new_page();g.on('pageerror',lambda e:H.ERRS.append(tag+': '+str(e)));g.goto('file://'+H.INDEX);return c,g
    STORE['doc']=datos()
    cA,A=device(1500,'A');cB,B=device(3000,'B')
    A.wait_for_timeout(5000)
    chk(B.evaluate("_loadedRev")==2 and STORE['doc']['rev']==2 and STORE['writes']==1,'A y B abren a la vez: A guarda el rechazo (rev 2); B no escribe encima',[B.evaluate("_loadedRev"),STORE['doc']['rev'],STORE['writes']])
    chk(A.evaluate("window.__GETS")==2 and B.evaluate("window.__GETS")==3,'De verdad a la vez: A lee 2 veces (carga y transacción); B 3 (carga, transacción con conflicto y recarga en silencio)',[A.evaluate("window.__GETS"),B.evaluate("window.__GETS")])
    chk(not A.evaluate("!!document.getElementById('cloudConflict')") and not B.evaluate("!!document.getElementById('cloudConflict')"),'Ninguno de los dos ve «Hay cambios hechos desde otro dispositivo»')
    chk(A.evaluate(ST)['qa']=='rechazado' and B.evaluate(ST)['qa']=='rechazado' and {q['id']:q['status'] for q in STORE['doc']['quotes']}['qa']=='rechazado','Los dos móviles y la nube: «Rechazado»')
    chk(B.evaluate("document.getElementById('loadingScreen').style.display")=='none' and B.evaluate("_loadedOK"),'B termina de abrir con normalidad')
    B.evaluate("window.__TXD=0;setQuoteStatus('q1','rechazado')");B.wait_for_timeout(1500)
    chk(STORE['doc']['rev']==3 and not B.evaluate("!!document.getElementById('cloudConflict')"),'B guarda después un cambio a mano sin conflicto (rev 3)',STORE['doc']['rev'])
    A.evaluate("window.__TXD=0;setQuoteStatus('qc','rechazado')");A.wait_for_timeout(1500)
    chk(A.evaluate("!!document.getElementById('cloudConflict')") and STORE['doc']['rev']==3,'Un cambio a mano desde un móvil desfasado sigue avisando del conflicto (como siempre)')
    cA.close();cB.close()
    # Nube lenta: la pantalla de carga no espera más de 6 s; el guardado termina solo
    STORE['doc']=datos();STORE['writes']=0
    cS,S=device(9000,'lenta');S.wait_for_timeout(7200)
    chk(S.evaluate("document.getElementById('loadingScreen').style.display")=='none' and S.evaluate(ST)['qa']=='rechazado' and STORE['writes']==0,'Nube lenta: a los 6 s la app se abre ya con el rechazo (el guardado sigue en marcha)',[S.evaluate("document.getElementById('loadingScreen').style.display"),STORE['writes']])
    S.wait_for_timeout(3500)
    chk(STORE['writes']==1 and STORE['doc']['rev']==2 and S.evaluate("_loadedRev")==2 and not S.evaluate("!!document.getElementById('cloudConflict')"),'…y cuando la nube responde queda guardado (rev 2), sin avisos',[STORE['writes'],STORE['doc']['rev']])
    cS.close()
    # Sin red al abrir: no se entra (como siempre) y no se escribe nada
    STORE['doc']=datos();STORE['writes']=0
    c=H.new_context(br,offline=False);c.route('**/*',lambda r:r.fulfill(body=STUB2.replace("const t=await window.__fsGet();","throw Object.assign(new Error('offline'),{code:'unavailable'});"),content_type='text/javascript') if 'firebase-app-compat' in r.request.url else H.route(r))
    c.expose_function('__fsGet',fs_get);c.expose_function('__fsSet',fs_set);c.add_init_script(H.FAKE)
    g=c.new_page();g.on('pageerror',lambda e:H.ERRS.append('sinred: '+str(e)));g.goto('file://'+H.INDEX);g.wait_for_timeout(2500)
    chk('Error de carga' in g.evaluate("document.getElementById('loadingScreen').textContent") and STORE['writes']==0,'Sin red al abrir: «Error de carga» de siempre y ninguna escritura')
    c.close()
    br.close()
H.fin()
