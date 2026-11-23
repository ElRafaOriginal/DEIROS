# Copia «con fotos» (#126): incluye la galería de cada coche (también fotos aún en la cola del móvil) y las actas, no escribe
# nada al exportar, sin red no se puede; al importar en otro móvil se restaura todo sin duplicar, sobre una galería con
# fotos se conservan las de la nube, una copia «con fotos» antigua (sin galería) se restaura como siempre, y sin red las
# fotos esperan en la cola y al subir no pisan lo que haya llegado a la nube. data/main sin rastro de la galería.
# Origen: specs/c126/test_c126.py. «Igual que main» → copia v4 de siempre y valores fijos. Uso: python3 tests/test_copia_fotos.py
import sys,os,json,copy,time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from galeria_comun import *
TMPD=TMP
def ph(i):return BIG.crop((i*150,80+i*20,i*150+2400,1880+i*20)).resize((1280,960))
def gfoto(vid,fid,pos,i,seed,at='2026-11-02T09:00:00.000Z'):
    im=ph(i);seed['users/demo/vehiculos/%s/fotos/%s'%(vid,fid)]={'v':1,'vid':vid,'pos':pos,'at':at,'kb':150+i,'img':durl(im,65)}
    return {'id':fid,'pos':pos,'at':at,'kb':150+i,'th':th(im)}
def gidx(vid,F,seed):seed['users/demo/vehiculos/'+vid]={'v':1,'vid':vid,'kb':sum(f['kb'] for f in F),'fotos':F,'subida':{'seconds':1}}
def acta(bid,vid,fase,n,seed,i0):
    F=[]
    for k in range(n):
        im=ph(i0+k);fid='%s%s%d'%(bid,fase[:3],k);tipo=['frontal','trasera','lat_der'][k]
        seed['users/demo/actas/%s__%s/fotos/%s'%(bid,fase,fid)]={'v':1,'bid':bid,'fase':fase,'tipo':tipo,'at':'2026-11-03T10:00:00.000Z','kb':120,'img':durl(im,65)}
        F.append({'id':fid,'tipo':tipo,'at':'2026-11-03T10:00:00.000Z','kb':120,'th':th(im)})
    seed['users/demo/actas/%s__%s'%(bid,fase)]={'v':1,'bid':bid,'vid':vid,'fase':fase,'at':'2026-11-03T10:00:00.000Z','km':12000,'combustible':'1/2','lugar':'Pinto','nota':'','keep':False,'kb':120*n,'fotos':F,'subida':{'seconds':1}}
# Cuenta A (la que exporta): galería de v1 (1 y 3) y v5 (1 y 2), un índice huérfano de un coche que ya no existe (v9) y actas de b2 y b4
SA={}
gidx('v1',[gfoto('v1','g1a',1,1,SA),gfoto('v1','g1c',3,2,SA)],SA)
S1,S2=gfoto('v5','seed1',1,3,SA),gfoto('v5','seed2',2,4,SA);gidx('v5',[S1,S2],SA)
gidx('v9',[gfoto('v9','g9',1,5,SA)],SA)
acta('b2','v2','entrega',2,SA,6);acta('b4','v4','devolucion',1,SA,8)
# Cuenta C (ya tiene galería): v1 con «nube3» en la 3; v5 con «nube1» en la 1 y la misma «seed2» en la 2
def seed_c():
    S={};gidx('v1',[gfoto('v1','nube3',3,9,S)],S);N1=gfoto('v5','nube1',1,10,S);S2c=copy.deepcopy(S2);S['users/demo/vehiculos/v5/fotos/seed2']=copy.deepcopy(SA['users/demo/vehiculos/v5/fotos/seed2']);gidx('v5',[N1,S2c],S);return S
TOASTS="window.__toasts||[]"
def toasts(pg):return pg.evaluate(TOASTS)
def until_empty(pg,ms=20000):
    t=time.time()
    while time.time()-t<ms/1000:
        if qn(pg)==0 and not pg.evaluate("_fx.busy"):return True
        pg.evaluate("_fxKick(true)");wait(pg,700)
    return False
def do_import(pg,path):
    pg.evaluate("window.__CF=[];window.__toasts=[];openBackup()");wait(pg,300)
    pg.set_input_files('#SC input[type=file][accept=".json"]',path);wait(pg,2500)
def gfs(pg,vid):return fs(pg,'users/demo/vehiculos/'+vid)
def ids(gd):return [(f['pos'],f['id']) for f in (gd or {}).get('fotos',[])]
def strip(o):o=copy.deepcopy(o);[o.pop(k,None) for k in ('exportedAt','fotosActas','fotosGaleria')];return o
with sync_playwright() as p:
    br=H.launch(p)
    # ───────────── 1 · Exportar con 2 coches con galería (nube + una foto aún en la cola) y actas
    ctx,pg=new_page(br,NEW,seed=SA,old=False)
    with pg.expect_download() as d1:pg.evaluate("exportData()")
    j1=json.load(open(d1.value.path(),encoding='utf-8'))
    ok('Copia normal descargada = copia v4 de siempre (sin fotos de la galería ni de las actas)',strip(j1)==strip(json.loads(bko(pg))) and 'fotosGaleria' not in j1 and 'fotosActas' not in j1 and j1.get('version')==4)
    t=[x for x in toasts(pg) if 'Copia descargada' in x][-1:]
    ok('Aviso tras la copia normal: la galería va en la copia con fotos','galería' in (t[0] if t else '') and 'Exportar copia con fotos' in (t[0] if t else '') and 'ninguna copia' not in (t[0] if t else ''),t)
    pg.evaluate("_fx.busy=true;_gxView('v1',4)");wait(pg,300)  # la subida, parada: la foto 4 se queda en la cola
    shoot(pg,'Cámara',FOT[1],'v1',3);pg.evaluate("_gxVClose()")
    q4=pg.evaluate("_fx.A['veh:v1'].fotos.find(f=>f.pos===4).id");img4=pg.evaluate("i=>_fxGet('img',i)",q4)
    ok('Foto 4 de v1 solo en la cola (no en la nube)',fs(pg,'users/demo/vehiculos/v1/fotos/'+q4) is None and pg.evaluate("_fxAll('q').then(L=>L.filter(i=>i.id==='veh:v1').length)")==2)
    pg.evaluate("openBackup()");wait(pg,300)
    bt=pg.locator('#SC button',has_text='Exportar copia con fotos')
    hint=pg.evaluate("[...document.querySelectorAll('#SC .d-hint')].map(e=>e.textContent).join(' | ')")
    ok('Hoja de copia: botón «… con fotos de actas y galería» (≥ 44 px)',bt.inner_text().strip()=='Exportar copia con fotos de actas y galería' and bt.bounding_box()['height']>=44,bt.inner_text())
    ok('Hoja de copia: avisa de que incluye la galería y de su tamaño (≈ MB)','galería de cada coche (unos 2,5 MB por coche' in hint and 'ahora la galería suma ≈' in hint and ' MB)' in hint and 'solo en la copia con fotos' in hint and 'ninguna copia JSON' not in hint,hint[:400])
    sw=pg.evaluate("document.getElementById('SC').scrollWidth<=document.getElementById('SC').clientWidth")
    ok('Hoja de copia sin desborde horizontal a 390 px',sw)
    K0={k:json.dumps(v,sort_keys=True) for k,v in pg.evaluate("JSON.parse(JSON.stringify(window.__FS))").items()};ops0=pg.evaluate("window.__FSOPS.length")
    pg.evaluate("window.__toasts=[]")
    with pg.expect_download(timeout=60000) as dl:bt.click()
    wait(pg,800);FILE=dl.value.path();BK=json.load(open(FILE,encoding='utf-8'));FN=dl.value.suggested_filename
    ok('Fichero DEIROS_backup_fotos_<fecha>.json',FN.startswith('DEIROS_backup_fotos_'),FN)
    ok('Exportar no escribe nada en la nube',pg.evaluate("window.__FSOPS.length")==ops0 and {k:json.dumps(v,sort_keys=True) for k,v in pg.evaluate("JSON.parse(JSON.stringify(window.__FS))").items()}==K0)
    FG=BK.get('fotosGaleria')
    ok('fotosGaleria: v1 y v5 (no el índice huérfano de v9)',isinstance(FG,list) and [e['id'] for e in FG]==['veh:v1','veh:v5'],FG and [e['id'] for e in FG])
    e1,e5=FG[0],FG[1]
    ok('v1: posiciones 1, 3 y 4 (la 4, de la cola) con miniatura y sin imagen grande en el índice',[f['pos'] for f in e1['galeria']['fotos']]==[1,3,4] and all(f['th'].startswith('data:image/jpeg') for f in e1['galeria']['fotos']) and 'img' not in json.dumps(e1['galeria']) and 'subida' not in e1['galeria'] and e1['galeria']['vid']=='v1')
    ok('v1: las 3 fotos grandes (2 de la nube, 1 de la cola del móvil)',e1['imgs'].get('g1a')==SA['users/demo/vehiculos/v1/fotos/g1a']['img'] and e1['imgs'].get('g1c')==SA['users/demo/vehiculos/v1/fotos/g1c']['img'] and e1['imgs'].get(q4)==img4 and len(e1['imgs'])==3)
    ok('v5: seed1 y seed2 con sus fotos de la nube',ids(e5['galeria'])==[(1,'seed1'),(2,'seed2')] and e5['imgs']=={'seed1':SA['users/demo/vehiculos/v5/fotos/seed1']['img'],'seed2':SA['users/demo/vehiculos/v5/fotos/seed2']['img']})
    FA=BK.get('fotosActas') or []
    ok('fotosActas como siempre: b2 entrega (2) y b4 devolución (1)',sorted(e['id'] for e in FA)==['b2__entrega','b4__devolucion'] and sum(len(e['imgs']) for e in FA)==3 and all('veh:' not in e['id'] for e in FA))
    ok('El resto del fichero es la copia v4 de siempre',strip(BK)==strip(json.loads(bko(pg))))
    t=[x for x in toasts(pg) if 'Copia con fotos' in x]
    mb=sum(len(v) for e in FA+FG for v in e['imgs'].values())/1048576
    ok('Aviso: «Copia con fotos descargada (≈%.1f MB): 3 de entrega y devolución y 5 de la galería de 2 coches.»'%mb,t and t[-1].startswith('Copia con fotos descargada (≈') and ': 3 de entrega y devolución y 5 de la galería de 2 coches.' in t[-1] and (('%.1f'%mb).replace('.',',')+' MB') in t[-1],t)
    # Copia «con fotos» antigua (anterior a #126): sin fotosGaleria
    OLDB=copy.deepcopy(BK);OLDB.pop('fotosGaleria');FOLD=os.path.join(TMPD,'antigua.json');json.dump(OLDB,open(FOLD,'w',encoding='utf-8'))
    FNEW=os.path.join(TMPD,'nueva.json');json.dump(BK,open(FNEW,'w',encoding='utf-8'))
    pg.evaluate("closeSheet();_fx.busy=false;_fxKick(true)");ok('Tras exportar, la cola se sube igual',until_empty(pg) and poss(gfs(pg,'v1'))==[1,3,4])
    ctx.close()
    # ───────────── 2 · Sin conexión: exportar no se puede (como siempre)
    ctx,pg=new_page(br,NEW,old=False);ctx.set_offline(True);wait(pg,300);dls=[];pg.on('download',lambda d:dls.append(d))
    pg.evaluate("window.__toasts=[];openBackup()");wait(pg,300);pg.locator('#SC button',has_text='Exportar copia con fotos').click();wait(pg,800)
    ok('Sin red: «Hace falta conexión para incluir las fotos.» y no descarga',not dls and any('Hace falta conexión' in x for x in toasts(pg)))
    ctx.close()
    # ───────────── 3 · Importar en una cuenta vacía (otro móvil): se restaura todo
    ctx,pg=new_page(br,NEW,old=False)
    do_import(pg,FNEW)
    cf=pg.evaluate("window.__CF||[]")
    ok('Aviso al importar: también la galería, sin sustituir lo que ya haya',cf and cf[-1].endswith(' También se restaurarán las fotos de entrega y devolución y de la galería de los coches, sin sustituir las que ya haya en la nube (se subirán a la nube en segundo plano).'),cf[-1:])
    ok('Se sube todo y la cola queda vacía',until_empty(pg))
    ok('Nube: v1 con las mismas 3 fotos (ids y posiciones) y v5 con seed1 y seed2',ids(gfs(pg,'v1'))==ids(e1['galeria']) and ids(gfs(pg,'v5'))==[(1,'seed1'),(2,'seed2')] and gfs(pg,'v9') is None,(ids(gfs(pg,'v1')),ids(gfs(pg,'v5'))))
    okimg=all(fs(pg,'users/demo/vehiculos/%s/fotos/%s'%(e['galeria']['vid'],k)) and fs(pg,'users/demo/vehiculos/%s/fotos/%s'%(e['galeria']['vid'],k))['img']==v for e in FG for k,v in e['imgs'].items())
    ok('Nube: cada foto grande, idéntica a la de la copia, en su documento',okimg and len(fs_keys(pg,'users/demo/vehiculos/v1/fotos/'))==3 and len(fs_keys(pg,'users/demo/vehiculos/v5/fotos/'))==2)
    ok('Índices restaurados con las miniaturas de la copia',[f['th'] for f in gfs(pg,'v1')['fotos']]==[f['th'] for f in e1['galeria']['fotos']] and gfs(pg,'v1')['kb']==sum(f['kb'] for f in e1['galeria']['fotos']))
    ok('Actas restauradas como siempre',sorted(k for k in fs_keys(pg,'users/demo/actas/') if k.count('/')==3)==['users/demo/actas/b2__entrega','users/demo/actas/b4__devolucion'] and len([k for k in fs_keys(pg,'users/demo/actas/') if '/fotos/' in k])==3)
    t=toasts(pg)
    ok('Un solo aviso: «Fotos de entrega y devolución restauradas: 3. Galería: 5 fotos restauradas en 2 coches. Se suben…»',any(x.startswith('Fotos de entrega y devolución restauradas: 3. Galería: 5 fotos restauradas en 2 coches. Se suben a la nube en segundo plano.') for x in t),t)
    M=json.dumps(fs(pg,'users/demo/data/main'))
    ok('data/main sin rastro de la galería (ni campos nuevos en V)','veh:' not in M and 'fotosGaleria' not in M and all(set(v)==set(w) for v,w in zip(fs(pg,'users/demo/data/main')['vehicles'],BK['vehicles'])))
    pg.evaluate("nav('vehicles')");wait(pg,800)
    ok('Flota: la portada de v1 es la foto 1 restaurada',pg.evaluate("(document.querySelector(\".fl-k[onclick=\\\"openV('v1')\\\"] img.fl-cv\")||{}).src")==e1['galeria']['fotos'][0]['th'])
    info(pg,'v1');ok('Ficha de v1: «3 de 8» sin reloj',pg.evaluate("document.querySelector('#gxSec .gx-h .q').textContent")=='3 de 8' and not pg.evaluate("!!document.querySelector('#gxSec .phk.p')"))
    pg.evaluate("closeSheet()")
    K1=fs_keys(pg,'users/demo/vehiculos/')
    do_import(pg,FNEW);until_empty(pg)
    t=toasts(pg)
    ok('Importar otra vez la misma copia: no duplica (5 ya estaban)',fs_keys(pg,'users/demo/vehiculos/')==K1 and ids(gfs(pg,'v1'))==ids(e1['galeria']) and any('Galería: 0 fotos restauradas; 5 ya estaban.' in x for x in t),t)
    ctx.close()
    # ───────────── 4 · Importar sobre una galería que ya tiene fotos: se conserva la de la nube
    SC=seed_c();ctx,pg=new_page(br,NEW,seed=SC,old=False)
    do_import(pg,FNEW);ok('Sobre galería existente: se sube y la cola queda vacía',until_empty(pg))
    ok('v1: restauradas la 1 y la 4; en la 3 se queda «nube3»',ids(gfs(pg,'v1'))==[(1,'g1a'),(3,'nube3'),(4,q4)] and fs(pg,'users/demo/vehiculos/v1/fotos/nube3')['img']==SC['users/demo/vehiculos/v1/fotos/nube3']['img'] and fs(pg,'users/demo/vehiculos/v1/fotos/g1c') is None,ids(gfs(pg,'v1')))
    ok('v5: se quedan «nube1» y «seed2»; seed1 no se sube',ids(gfs(pg,'v5'))==[(1,'nube1'),(2,'seed2')] and fs_keys(pg,'users/demo/vehiculos/v5/fotos/')==['users/demo/vehiculos/v5/fotos/nube1','users/demo/vehiculos/v5/fotos/seed2'])
    ok('Sin fotos sueltas en la nube (3 en v1, 2 en v5)',len(fs_keys(pg,'users/demo/vehiculos/v1/fotos/'))==3)
    t=toasts(pg)
    ok('Aviso: 2 restauradas, 1 ya estaba y 2 no porque ya tenían foto (se conservan)',any('Galería: 2 fotos restauradas en 1 coche; 1 ya estaba; 2 no, porque esas posiciones ya tenían foto (se conservan las que había).' in x for x in t),t)
    ctx.close()
    # ───────────── 5 · Copia «con fotos» antigua (sin galería): se restaura como antes (valores fijos; antes «igual que main»)
    c,pq=new_page(br,NEW,old=False);do_import(pq,FOLD);until_empty(pq)
    cf=pq.evaluate("window.__CF||[]");rs=[x for x in toasts(pq) if 'restaurad' in x]
    ok('Copia antigua: el aviso al importar solo habla de las fotos de entrega y devolución',cf and cf[-1].endswith('¿Continuar? También se restaurarán las fotos de entrega y devolución (se subirán a la nube en segundo plano).'),cf[-1:])
    ok('Copia antigua: «Fotos restauradas: 3. Se suben a la nube en segundo plano.»',rs==['Fotos restauradas: 3. Se suben a la nube en segundo plano.'],rs)
    ok('Copia antigua: actas de b2 (2 fotos) y b4 (1 foto) en la nube, y ninguna galería',fs_keys(pq,'users/demo/actas/')==['users/demo/actas/b2__entrega','users/demo/actas/b2__entrega/fotos/b2ent0','users/demo/actas/b2__entrega/fotos/b2ent1','users/demo/actas/b4__devolucion','users/demo/actas/b4__devolucion/fotos/b4dev0'] and fs_keys(pq,'users/demo/vehiculos/')==[])
    ok('Copia antigua: las fotos restauradas son las de la copia',[fs(pq,k)['img'] for k in fs_keys(pq,'users/demo/actas/') if '/fotos/' in k]==[SA[k]['img'] for k in sorted(SA) if k.startswith('users/demo/actas/') and '/fotos/' in k])
    ok('Copia antigua: tras importar, la copia v4 del móvil es la del fichero',strip(json.loads(bko(pq)))=={k:v for k,v in strip(OLDB).items() if k!='fotosActas'},sorted(k for k in strip(OLDB) if strip(json.loads(bko(pq))).get(k)!=strip(OLDB).get(k)))
    c.close()
    # ───────────── 6 · Sin conexión: la galería espera en la cola y al subir no pisa lo que haya llegado a la nube
    SC=seed_c();ctx,pg=new_page(br,NEW,seed=SC,old=False);wait(pg,500)
    ctx.set_offline(True);wait(pg,300)
    do_import(pg,FNEW);wait(pg,800)
    t=toasts(pg)
    ok('Sin red: aviso «Sin conexión: al subir se unirán con la nube sin sustituir…»',any('Galería: 2 fotos restauradas en 1 coche; 1 ya estaba; 2 no, porque esas posiciones ya tenían foto' in x and 'Sin conexión: al subir se unirán con la nube sin sustituir las fotos que ya tenga.' in x for x in t),t)
    Q=pg.evaluate("_fxAll('q').then(L=>L.filter(i=>i.id==='veh:v1').map(i=>({t:i.t,m:i.m,r:i.r,fid:i.fid})))")
    qa=[x for x in Q if x['t']=='a']
    ok('Sin red: 2 fotos de v1 en la cola y su índice para unirse (m=1, r=[g1a, foto 4])',len([x for x in Q if x['t']=='f'])==2 and qa and qa[0]['m']==1 and sorted(qa[0]['r'])==sorted(['g1a',q4]),Q)
    ok('Sin red: nada escrito aún en la nube',ids(gfs(pg,'v1'))==[(3,'nube3')])
    info(pg,'v1');ok('Sin red: ficha de v1 «3 de 8 · 2 sin subir»',pg.evaluate("document.querySelector('#gxSec .gx-h .q').textContent")=='3 de 8 · 2 sin subir')
    # Mientras, otro móvil sube una foto en la 4 de v1, y aquí se hace una en la 6 (sin red)
    n4=gfoto('v1','nube4',4,11,{});pg.evaluate("f=>{const k='users/demo/vehiculos/v1';window.__FS[k+'/fotos/nube4']={v:1,vid:'v1',pos:4,at:f.at,kb:f.kb,img:'%s'};window.__FS[k].fotos.push(f)}"%fs(pg,'users/demo/vehiculos/v1/fotos/nube3')['img'],n4)
    pg.evaluate("closeSheet();_gxView('v1',6)");wait(pg,300);shoot(pg,'Cámara',FOT[2],'v1',4);pg.evaluate("_gxVClose()")
    q6=pg.evaluate("_fx.A['veh:v1'].fotos.find(f=>f.pos===6).id")
    qa=pg.evaluate("_fxGet('q','demo|a:veh:v1').then(i=>({m:i.m,r:i.r}))")
    ok('Foto nueva sin red: el índice sigue para unirse y con sus restauradas',qa['m']==1 and sorted(qa['r'])==sorted(['g1a',q4]),qa)
    pg.evaluate("window.__toasts=[]");ctx.set_offline(False);wait(pg,500)
    ok('Al volver la red: se sube y la cola queda vacía',until_empty(pg))
    ok('Nube v1: 1 restaurada, 3 «nube3», 4 la del otro móvil (no la restaurada), 6 la nueva',ids(gfs(pg,'v1'))==[(1,'g1a'),(3,'nube3'),(4,'nube4'),(6,q6)],ids(gfs(pg,'v1')))
    ok('La restaurada que cedió se borra de la nube y del móvil',fs(pg,'users/demo/vehiculos/v1/fotos/'+q4) is None and len(fs_keys(pg,'users/demo/vehiculos/v1/fotos/'))==4 and pg.evaluate("i=>_fxGet('img',i).then(x=>!x)",q4))
    ok('Aviso al subir: «Una foto de la copia no se ha restaurado en la galería de … se conserva.»',any(x.startswith('Una foto de la copia no se ha restaurado en la galería de ') and x.endswith(': en la nube ya había foto en esa posición y se conserva.') for x in toasts(pg)),toasts(pg))
    ok('La ficha ve lo mismo que la nube',ids(gal(pg,'v1'))==ids(gfs(pg,'v1')))
    ctx.close()
    br.close()
H.fin()
