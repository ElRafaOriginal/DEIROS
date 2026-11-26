# Textos de TODOS los PDF (#pdfsolape): ningún glifo mal codificado, ninguna palabra encima de otra y nada fuera de los márgenes.
# Causa del fallo: Helvetica (WinAnsi) y las fuentes de marca no tienen todos los caracteres; si una cadena lleva uno que falta
# («→» de «26/10→01/11», ✓, emojis, ș/ł de nombres extranjeros…), jsPDF la escribe entera en 2 bytes y el visor del móvil (pdfium)
# la separa letra a letra encima de la columna IMPORTE. El arreglo (_pdfTxt) cambia esos caracteres antes de medir y escribir.
# Genera con datos INVENTADOS (nombres largos, alquiler que cruza de mes, ampliaciones, notas con símbolos) los PDF de liquidación,
# informe del coche, recibos, anexos, contratos (alquiler y gestión), mantenimientos, negocio, analítica, presupuestos y actas, y los
# revisa con pdftotext -bbox y leyendo el contenido del PDF. Uso: python3 tests/test_pdf_textos.py
# DEIROS_PDF_OUT=/carpeta guarda ahí los PDF generados (para verlos o renderizarlos).
import sys,os,re,json,base64,subprocess,html,tempfile
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
chk=H.chk
OUT=os.environ.get('DEIROS_PDF_OUT') or tempfile.mkdtemp(prefix='deiros_pdftextos_')
M,PM=H.MES,H.MES_ANT
D=H.datos()  # datos de siempre + casos difíciles (todo inventado)
o=D['owners'][0];o['name']='Ana Ștefania Propietaria Ejemplo de la Fuente y Santamaría'
v2=[v for v in D['vehicles'] if v['id']=='v2'][0]
v2['name']='Fiat Fiorino Combi Maxi Adaptada';v2['model']='Fiorino Combi 1.3 Multijet Largo'
v2['finances']+= [{'id':'e53','type':'expense','amount':48.5,'date':M+'-12','category':'Limpieza','desc':'Limpieza integral de tapicería — “urgente” ✓ factura 2026/1187 del taller Lavados Express Pinto Sur, con recogida','description':'Limpieza integral de tapicería — “urgente” ✓ factura 2026/1187 del taller Lavados Express Pinto Sur, con recogida'},
                  {'id':'e54','type':'expense','amount':1234.56,'date':M+'-13','category':'Combustible','desc':'Repostaje ⛽ 45 L','description':'Repostaje ⛽ 45 L'}]
b2=v2['bookings'][0];b2['clientName']='Ștefan Mărculescu-Țăranu Popescu';b2['notes']='Entrega en aeropuerto ✈ T4 — “cliente VIP” ✓ llamar 30′ antes ≥ 1 h'
b2['deliveryPlace']='Aeropuerto Adolfo Suárez Madrid-Barajas, Terminal 4, planta de llegadas, puerta 10 → parking P4'
v2['bookings']+=[H._bk(21,-25,-19,'Ioana Rădulescu',120,'amovens','10:00','10:00'),
  dict(H._bk(22,-15,-3,'Bartłomiej Wójcik-Łukasiewicz',200,'sinapp','09:00','09:00',fianza=200,delivered=True,clientPhone='600 000 009',notes='Furgoneta para mudanza larguísima con varias paradas por la Comunidad de Madrid'),
       finance=[{'id':'amp22','type':'income','concept':'Ampliación alquiler ('+H.d(-10)+' → '+H.d(-3)+')','amount':120,'date':H.d(-10),'notes':'Total anterior: 200 · Nuevo total: 320'}])]
# alquiler que cruza de mes: 26 del mes anterior → 1 de este (como en el caso real)
v2['bookings'][1]['startDate']=PM+'-26';v2['bookings'][1]['endDate']=M+'-01'
# coche propio con nombres largos y combustible faltante
v3=[v for v in D['vehicles'] if v['id']=='v3'][0]
b3=v3['bookings'][0];b3['clientName']='Alejandro José Martínez de la Fuente y Rodríguez-Santamaría'
b3['finance']=[{'id':'T_amp','type':'income','concept':'Ampliación alquiler ('+b3['endDate']+' → '+H.d(30)+')','amount':60,'date':H.d(0),'notes':'Total anterior: 414.99 · Nuevo total: 474.99'},
               {'id':'fu1','type':'income','concept':'Combustible faltante','amount':31.2,'date':H.d(0),'notes':'Faltan 12 L (Lleno (100%) → 1/4) · 2,60 €/L'}]
b3['deliveryPlace']='Calle de la Constitución Española de 1978, 123, portal 4 → Pinto (Madrid)'
b3['extras']=[{'id':'x1','label':'Silla infantil grupo 2/3 con respaldo “premium” ✓','amount':25},{'id':'x2','label':'Entrega a domicilio','amount':50}]
c1=D['clients'][0];c1['name']=b3['clientName'];c1['address']='Calle de la Constitución Española de 1978, 123, portal 4, escalera B, 3º izquierda, 28320 Pinto (Madrid)'
q=D['quotes'][0];q['clientName']='Ștefan Mărculescu-Țăranu Popescu';q['extras']=[{'id':'x1','label':'Silla infantil grupo 2/3 con respaldo “premium” ✓ → incluida','amount':25,'price':25}]
q['notes']='Precio especial → válido 7 días ✓'
D['bizFinances'].append({'id':'f9','type':'expense','amount':12.5,'date':M+'-08','category':'Suscripción','desc':'Software de flota → plan “Pro” ✓ (renovación anual con descuento por pago adelantado)'})
SCEN=r"""(()=>{window.__PDF={};window.__AL=[];window.alert=m=>window.__AL.push(String(m));window.confirm=()=>true;
 _savePDF=_pdfDownload=function(doc,fn){window.__PDF[window.__K]={name:fn,u:doc.output('datauristring')};};return true;})()"""
JOBS=[('analitica',["generateAnalyticsPDF('%s','%s')"%(PM,M)]),
      ('recibo-b3',["generateReceiptPDF('b3')"]),('recibo-b2',["generateReceiptPDF('b2')"]),('recibo-b22',["generateReceiptPDF('b22')"]),
      ('anexo-b3',["showBookingById('b3')","generateExtensionPDF('b3')"]),('anexo-b22',["showBookingById('b22')","generateExtensionPDF('b22')"]),
      ('contrato-b3',["openContractForm('v3','b3')","document.getElementById('ctClNac').value='1990-05-14';_ctGo(4)","generateContractPDF('v3','b3')"]),
      ('contrato-b2',["openContractForm('v2','b2')","document.getElementById('ctClNac').value='1985-02-03';_ctGo(4)","generateContractPDF('v2','b2')"]),
      ('contrato-gestion',["openMgmtContractForm('o1','v2')","generateMgmtContractPDF('o1','v2')"]),
      ('mantenimiento-v3',["dlMaintReport('v3')"]),
      ('negocio',["dlBizReport('%s','%s','Periodo')"%(PM,M)]),
      ('liquidacion',["dlOwnerReport('o1','%s')"%M]),('liquidacion-ant',["dlOwnerReport('o1','%s')"%PM]),
      ('informe-coche-v2',["dlReport('v2','%s')"%M]),('informe-coche-v3',["dlReport('v3','%s')"%M]),
      ('presupuesto-q1',["generateQuotePDF('q1')"]),('presupuesto-q3',["generateQuotePDF('q3')"])]

MM=72/25.4
def words(p):
    o=subprocess.run(['pdftotext','-bbox',p,'-'],capture_output=True,text=True).stdout
    pages=[];cur=None
    for l in o.splitlines():
        if '<page ' in l:cur=[];pages.append(cur)
        m=re.search(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*)</word>',l)
        if m and cur is not None:cur.append((float(m[1]),float(m[2]),float(m[3]),float(m[4]),html.unescape(m[5])))
    return pages
def _streams(b):
    import zlib
    for m in re.finditer(rb'stream\r?\n(.*?)\r?\nendstream',b,re.S):
        try:yield zlib.decompress(m.group(1))
        except Exception:yield m.group(1)
def glifos(p):
    """Texto con fuente estándar (Helvetica/Times/Courier, WinAnsi) escrito en 2 bytes (\\x00: jsPDF pasa la cadena entera a UTF-16
    si lleva un carácter fuera de WinAnsi) o con fuente propia (Identity-H) con el glifo 0. Ojo: si a la fuente de marca le falta un carácter,
    jsPDF 2.5.1 lo omite sin más («Ștefania» → «tefania»): eso lo comprueban los textos esperados del final."""
    b=open(p,'rb').read();std=set();cid=set()
    objs={m.group(1):m.group(2) for m in re.finditer(rb'(\d+) 0 obj(.*?)endobj',b,re.S)}
    for m in re.finditer(rb'/(F\d+) (\d+) 0 R',b):
        o=objs.get(m.group(2),b'')
        if b'/Type /Font' in o or b'/Type/Font' in o:(std if b'/Type1' in o else cid).add(m.group(1).decode())
    out=[];font=''
    for s in _streams(b):
        if b' Tf' not in s:continue
        for t in re.finditer(rb'/(F\d+) [\d.]+ Tf|\((?:\\.|[^\\)])*\)|<([0-9A-Fa-f]+)>',s,re.S):
            g=t.group(0)
            if g.startswith(b'/'):font=t.group(1).decode();continue
            if g.startswith(b'(') and font in std and b'\x00' in g:
                out.append('texto en 2 bytes con fuente estándar: «%s»'%g[1:-1].replace(b'\x00',b'').decode('cp1252','replace')[:70])
            elif g.startswith(b'<') and font in cid:
                h=t.group(2).decode()
                if any(h[i:i+4]=='0000' for i in range(0,len(h),4)):out.append('glifo que falta en la fuente %s'%font)
    return out
def analiza(p,margen=12):
    prob=['glifo mal codificado: '+x for x in glifos(p)]
    t=subprocess.run(['pdftotext',p,'-'],capture_output=True).stdout.decode('utf-8','replace')
    for pat,qu in (('\x00','byte nulo (texto en UTF-16 con fuente estándar)'),('!’','«!’» (flecha → mal codificada)'),('�','carácter de sustitución')):
        if pat in t:
            i=t.index(pat);prob.append('glifo mal codificado: %s · …%s…'%(qu,t[max(0,i-25):i+15].replace('\x00','').replace('\n',' ')))
    cc=[c for c in t if ord(c)<32 and c not in '\n\t\f\r' and c!='\x00']
    if cc:prob.append('caracteres de control en el texto: %s'%sorted(set('U+%04X'%ord(c) for c in cc)))
    for n,ws in enumerate(words(p),1):
        for w in ws:
            if w[0]<margen*MM-0.5 or w[2]>595.28-margen*MM+0.5:prob.append('p%d fuera de márgenes: «%s» x=%.1f..%.1f mm'%(n,w[4][:40],w[0]/MM,w[2]/MM))
        ws=sorted(ws,key=lambda w:w[0])
        for i,a in enumerate(ws):
            for b in ws[i+1:]:
                if b[0]>=a[2]:break
                ox=min(a[2],b[2])-max(a[0],b[0]);oy=min(a[3],b[3])-max(a[1],b[1])
                if ox>0.8 and oy>0.5*min(a[3]-a[1],b[3]-b[1]):prob.append('p%d solape: «%s» con «%s» (%.1f mm)'%(n,a[4][:30],b[4][:30],ox/MM))
    return prob
def ptext(f):return re.sub(r'\s+',' ',subprocess.run(['pdftotext','-layout',f,'-'],capture_output=True,text=True).stdout.replace('\xa0',' '))
PDFS={}
with H.playwright() as p:
    br=H.launch(p);ctx,pg=H.open_app(br,data=D)
    J=lambda js,a=None:pg.evaluate(js,a);W=lambda ms=400:pg.wait_for_timeout(ms)
    J(SCEN)
    v3m=[{'id':'m1','type':'expense','date':'2026-03-10','category':'Mantenimiento periódico','amount':180,'description':'Revisión completa con cambio de aceite y filtros → próxima en 15.000 km ✓','maint':{'work':'Aceite y filtros + revisión de frenos “completa”','km':140000,'nextKm':155000,'nextDate':'2027-03-10','shop':'Taller Mecánico Hermanos Ejemplo de Pinto Sur'}}]
    J("f=>{V.find(v=>v.id==='v3').finances.push(...f);V.forEach(v=>(v.bookings||[]).forEach(b=>_syncBookingToVFinances(v,b)));}",v3m)
    for name,steps in JOBS:
        J("k=>{window.__K=k;window.__AL=[];try{closeSheet()}catch(e){}}",name);W(200);err=''
        for s in steps:
            try:J("async()=>{await (async()=>{return %s})();}"%s);W(450)
            except Exception as e:err=str(e).split('\n')[0][:200]
        W(300);r=J("k=>window.__PDF[k]||null",name)
        if not r:chk(False,'PDF «%s»: se genera'%name,{'error':err,'alertas':J("window.__AL")});continue
        f=os.path.join(OUT,name+'.pdf');open(f,'wb').write(base64.b64decode(r['u'].split(',',1)[1]));PDFS[name]=f
    J("try{closeSheet()}catch(e){}")
    for bid in ('b3','b2'):
      for fase in ('entrega','devolucion'):
        J("b=>{const B=V.flatMap(v=>v.bookings).find(x=>x.id===b);B.kmStart=46000;B.kmEnd=46200;B.deliveredFuelLevel='Lleno (100%)';B.returnedFuelLevel='1/4';B.returnPlace='Gasolinera de la Avenida Ejemplo → junto al centro comercial';}",bid)
        name='acta-%s-%s'%(bid,fase)
        try:
            r=J("([b,f])=>_actaPDF(b,f).then(r=>({name:r.name,u:r.doc.output('datauristring')}))",[bid,fase])
            f=os.path.join(OUT,name+'.pdf');open(f,'wb').write(base64.b64decode(r['u'].split(',',1)[1]));PDFS[name]=f
        except Exception as e:chk(False,'PDF «%s»: se genera'%name,str(e)[:200])
    br.close()
chk(len(PDFS)==len(JOBS)+4,'Se generan los %d PDF'%(len(JOBS)+4),sorted(PDFS))
for name,f in sorted(PDFS.items()):
    pr=analiza(f)
    for tipo,txt in (('glifo','sin glifos mal codificados (ni texto en 2 bytes con Helvetica ni huecos en las fuentes de marca)'),
                     ('solape','sin palabras encima de otras'),('márgenes','sin texto fuera de los márgenes')):
        mal=[x for x in pr if tipo in x]
        chk(not mal,'PDF «%s»: %s'%(name,txt),mal[:4])
# Lo que se ve en lugar del carácter que faltaba (texto equivalente, sin perder el resto)
T={k:ptext(v) for k,v in PDFS.items()}
chk('Amovens · 26/10 a 01/11 (6d, 1d en Noviembre 2026)' in T.get('liquidacion',''),'Liquidación: «26/10→01/11» sale como «26/10 a 01/11»')
chk('04/11 a 20/11' in T.get('informe-coche-v2','') and 'Entrega en aeropuerto T4' in T.get('informe-coche-v2',''),'Informe del coche: fechas con «a» y la nota sin el emoji')
chk('Stefan Marculescu-Taranu Popescu' in T.get('recibo-b2','') and 'Stefan Marculescu-Taranu Popescu' in T.get('contrato-b2',''),'Recibo y contrato: «Ștefan Mărculescu-Țăranu» sale como «Stefan Marculescu-Taranu»')
chk('Bartlomiej Wójcik-Lukasiewicz' in T.get('recibo-b22',''),'Recibo: «ł/Ł» salen como «l/L» y las tildes españolas se quedan (ó)')
chk('“premium”' in T.get('presupuesto-q1','') and '—' in T.get('liquidacion',''),'Comillas tipográficas y raya larga se mantienen (están en la fuente)')
chk('26 años cumplidos' in T.get('contrato-b3','') and '0,19 €/km' in T.get('contrato-b3',''),'Contrato: el texto del contrato sigue igual (edad y km)')
chk('Ana Stefania Propietaria' in T.get('liquidacion','') and 'Ana Stefania Propietaria' in T.get('contrato-gestion',''),'Liquidación y contrato de gestión: el nombre con «ș» sale con «s» también en las fuentes de marca (cabecera y título)')
H.fin()
