# Copia de seguridad v4: exportar (claves, versión, fichero, copia previa al importar) e importar (vuelta completa idéntica,
# subida a data/main) y compatibilidad con copias ANTIGUAS: sin settings, sin clientId en presupuestos, sin lugares de
# entrega/devolución, sin depósito (tankL), sin «version» y la copia muy antigua «solo vehículos y finanzas». Ficheros no
# válidos: se rechazan sin tocar nada. (La copia «con fotos» está en test_copia_fotos.py y settings en test_resenas.py.)
# Nuevo (reúne comprobaciones sueltas de specs/d2, specs/tests/test_bloque2.js y specs/clientes). Uso: python3 tests/test_copia.py
import sys,os,json,copy
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
chk=H.chk
KEYS='version,exportedAt,vehicles,bizFinances,owners,clients,recurring,quotes,settings,company,photos'
IMP=r"""o=>{window.__AL=[];window.__CF=[];const f=new File([typeof o==='string'?o:JSON.stringify(o)],'copia.json',{type:'application/json'});importData({target:{files:[f],value:''}});}"""
STATE="(()=>{const o=_backupObject();delete o.exportedAt;return JSON.parse(JSON.stringify(o));})()"
with H.playwright() as p:
    br=H.launch(p)
    ctx,pg=H.open_app(br,extra="window.alert=m=>{(window.__AL=window.__AL||[]).push(String(m))};window.__CFR=true;window.confirm=m=>{(window.__CF=window.__CF||[]).push(String(m));return window.__CFR};",accept_downloads=True)
    J=lambda js,a=None:pg.evaluate(js,a);W=lambda ms=400:pg.wait_for_timeout(ms)
    def imp(o,ms=1800):J(IMP,o);W(ms)
    # ── 1. Exportar ──
    bo=J("JSON.parse(JSON.stringify(_backupObject()))")
    chk(','.join(bo)==KEYS and bo['version']==4,'Copia v4: claves y orden de siempre (%s)'%KEYS,','.join(bo))
    chk(J("_validateBackup(_backupObject())")=='','La copia que exporta la app es válida')
    chk(len(bo['vehicles'])==6 and len(bo['clients'])==3 and len(bo['quotes'])==3 and len(bo['owners'])==1 and len(bo['recurring'])==3 and len(bo['bizFinances'])==5,'Lleva todos los datos (6 coches, 3 clientes, 3 presupuestos, propietario, recurrentes y negocio)')
    chk(bo['company'].get('nombre')=='DEIROS' and bo['settings']=={'resenasUrl':''},'Lleva los datos de empresa y settings',[bo['company'].get('nombre'),bo['settings']])
    with pg.expect_download() as dl:J("exportData()")
    W(300);FN=dl.value.suggested_filename;EXP=json.load(open(dl.value.path(),encoding='utf-8'))
    chk(FN.startswith('DEIROS_backup_') and FN.endswith('.json'),'Exportar descarga «DEIROS_backup_….json»',FN)
    e2=dict(EXP);e2.pop('exportedAt',None)
    chk(e2==J(STATE),'El fichero descargado es la copia v4 del estado actual')
    chk(J("localStorage.getItem('deiros_lastBackupAt')") is not None,'Guarda la fecha de la última copia (aviso de copia)')
    # ── 2. Vuelta completa: cambiar cosas e importar la copia → todo como estaba ──
    S0=J(STATE)
    J("V=V.filter(v=>v.id!=='v5');CL[0].name='Cambiado';QT.pop();OW[0].phone='699 999 999';BF.push({id:'zz',type:'income',amount:1,date:todayStr(),category:'Otros'})")
    with pg.expect_download() as pre:imp(EXP)
    chk(pre.value.suggested_filename.startswith('DEIROS_backup_'),'Antes de importar descarga una copia del estado actual',pre.value.suggested_filename)
    cf=J("window.__CF")
    chk(cf and cf[-1].startswith('Esto reemplazará vehículos, finanzas, propietarios, clientes, gastos recurrentes, presupuestos, datos de empresa y fotos.'),'Pide confirmación con lo que se va a sustituir',cf[-1:])
    chk(J(STATE)==S0,'Tras importar, todo queda exactamente como en la copia')
    mn=J("JSON.parse(JSON.stringify(window.__FS['users/demo/data/main']))")
    chk(len(mn['vehicles'])==6 and [v['id'] for v in mn['vehicles']]==[v['id'] for v in S0['vehicles']] and mn['clients'][0]['name']==S0['clients'][0]['name'],'…y se sube a la nube (data/main con los 6 coches y los clientes de la copia)')
    chk(not J("window.__AL"),'Sin avisos de error',J("window.__AL"))
    # Cancelar la confirmación: no cambia nada
    J("window.__CFR=false");imp(dict(EXP,vehicles=EXP['vehicles'][:1]))
    chk(J(STATE)==S0,'Si se cancela la confirmación, no cambia nada');J("window.__CFR=true")
    # ── 3. Copias antiguas ──
    old=copy.deepcopy(EXP);old.pop('settings');old.pop('exportedAt');old.pop('version')
    for q in old['quotes']:q.pop('clientId',None)
    for v in old['vehicles']:
        v.pop('tankL',None)
        for b in v.get('bookings',[]):b.pop('deliveryPlace',None);b.pop('returnPlace',None)
    old['quotes'][0]['clientName']='Alejandro José Martínez de la Fuente'
    chk(J("o=>_validateBackup(o)",old)=='','Copia antigua (sin version, settings, clientId, lugares ni depósito): válida')
    J("AJ={resenasUrl:'https://g.page/r/ACTUAL/review'}")
    imp(old)
    st=J(STATE)
    chk(len(st['vehicles'])==6 and not J("window.__AL"),'Copia antigua: se importa sin avisos',J("window.__AL"))
    chk(st['settings']=={'resenasUrl':'https://g.page/r/ACTUAL/review'},'Copia antigua sin settings: se conserva el enlace de reseñas actual',st['settings'])
    for scr in ("nav('dashboard')","nav('rentals')","nav('quotes');_quoteEditId='q1';showQuoteDetail(document.getElementById('PC'))","openV('v3');showBookingById('b3')","openContractForm('v3','b3')","openV('v3');openReturnModal('b3')","_waPick('b','b3');_waClose()"):
        e0=len(H.ERRS);J("try{closeSheet()}catch(e){}");J(scr);W(500)
        chk(len(H.ERRS)==e0,'Copia antigua: «%s» funciona sin errores'%scr,H.ERRS[e0:])
    J("try{closeSheet()}catch(e){}")
    chk(J("_bookingClientTotal(V.find(v=>v.id==='v3').bookings.find(b=>b.id==='b3'))")==414.99,'Copia antigua: importes de los alquileres intactos (b3 414,99 €)')
    # Depósito (tankL): número en la copia; los datos cargados se normalizan («50» → 50, «abc» → null, sin campo → sin campo)
    o2=copy.deepcopy(EXP);o2['vehicles'][0]['tankL']=55
    imp(o2);chk(J("V[0].tankL")==55 and not J("window.__AL"),'Copia con depósito 55 L: se importa',J("V[0].tankL"))
    nz=J("(()=>{V[0].tankL='50';V[1].tankL='abc';delete V[2].tankL;_normalizeState();return [V[0].tankL,V[1].tankL,'tankL' in V[2]];})()")
    chk(nz==[50,None,False],'Normalización del depósito: «50» → 50, «abc» → null, sin campo → sin campo',nz)
    J("window.__AL=[]");s1=J(STATE)
    o3=copy.deepcopy(EXP);o3['vehicles'][0]['tankL']='x'
    imp(o3,900);al=J("window.__AL")
    chk(al and al[0].startswith('Fichero inválido') and 'depósito' in al[0] and J(STATE)==s1,'Depósito no numérico: «Fichero inválido» (depósito) y no se toca nada',al)
    # Copia muy antigua: solo vehículos y finanzas del negocio
    vo={'vehicles':copy.deepcopy(EXP['vehicles'][:2]),'bizFinances':copy.deepcopy(EXP['bizFinances'][:1])}
    imp(vo)
    cf=J("window.__CF");al=J("window.__AL")
    chk(cf and cf[-1].startswith('Este fichero es una copia antigua (solo vehículos y finanzas).'),'Copia muy antigua: avisa de que solo sustituye vehículos y finanzas',cf[-1:])
    chk(al==['Copia antigua: solo se han restaurado vehículos y finanzas del negocio. El resto de datos se mantiene.'],'Copia muy antigua: aviso al terminar',al)
    st=J(STATE)
    chk(len(st['vehicles'])==2 and len(st['bizFinances'])==1 and len(st['owners'])==1 and len(st['clients'])==3 and len(st['quotes'])==3,'Copia muy antigua: 2 coches y 1 movimiento; propietarios, clientes y presupuestos se conservan')
    # ── 4. Ficheros no válidos: no se toca nada ──
    s2=J(STATE)
    for raw,txt,lbl in [('no es json','Error al leer el fichero.','texto que no es JSON'),('[1,2]','Fichero inválido','una lista en vez de un objeto'),
                        (json.dumps({'vehicles':'x'}),'Fichero inválido','vehicles no es una lista'),(json.dumps({'version':'4','vehicles':[]}),'Fichero inválido','version en texto'),
                        (json.dumps(dict(EXP,fotosActas={})),'Fichero inválido','fotosActas no es una lista'),(json.dumps(dict(EXP,settings='x')),'Fichero inválido','settings no es un objeto')]:
        imp(raw,900);al=J("window.__AL")
        chk(al and al[0].startswith(txt) and J(STATE)==s2,'No válido (%s): «%s…» y nada cambia'%(lbl,txt),al)
    br.close()
H.fin()
