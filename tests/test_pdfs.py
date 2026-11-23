# Todos los PDF de la app se generan sin errores (con jsPDF real) y con su contenido: analítica, recibos, anexo de
# ampliación, contrato de alquiler, contrato de gestión, libro de mantenimientos, informe de negocio, liquidación del
# propietario, informe del coche, presupuestos y actas de entrega/devolución. Se comprueba cada fichero con pdfinfo/pdftotext.
# Además, el informe de mantenimientos (#144) con gastos con y sin datos del taller, recurrentes y coche sin mantenimientos.
# Origen: specs/fotos105/test_pr2.py (sección 7, que comparaba con main: ahora textos fijos esperados), specs/b2/test_b2.py
# (lista de PDF) y specs/m144/test_m144.js (era en node con un jsPDF falso; ahora con la app real).
# Uso: python3 tests/test_pdfs.py
import sys,os,json,base64,subprocess,tempfile,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
chk=H.chk
TMP=tempfile.mkdtemp(prefix='deiros_pdfs_')
M,PM=H.MES,H.MES_ANT
def pdfinfo(p):
    o=subprocess.run(['pdfinfo',p],capture_output=True,text=True).stdout;m=re.search(r'Pages:\s+(\d+)',o);return int(m.group(1)) if m else 0
def pdftext(p):return re.sub(r'\s+',' ',subprocess.run(['pdftotext','-layout',p,'-'],capture_output=True,text=True).stdout.replace('\xa0',' ').replace(' ',' '))
# Escenario: ampliación en b3 (para el anexo), mantenimientos con datos del taller en v3, cliente con nacimiento para el contrato
SCEN=r"""(()=>{const h=todayStr();
 const b3=V.find(v=>v.id==='v3').bookings.find(b=>b.id==='b3');b3.finance=(b3.finance||[]).filter(f=>f.id!=='T_amp');
 b3.finance.push({id:'T_amp',type:'income',concept:'Ampliación '+b3.endDate+' → '+addDays(h,30),amount:60,date:h,notes:'Total anterior: 300 · Nuevo total: 360'});
 const v3=V.find(v=>v.id==='v3');v3.finances.push({id:'m1',type:'expense',date:'2026-03-10',category:'Mantenimiento periódico',amount:180,description:'Revisión',maint:{work:'Aceite y filtros',km:140000,nextKm:155000,nextDate:'2027-03-10',shop:'Taller Prueba'}});
 window.__PDF={};window.__AL=[];window.alert=m=>window.__AL.push(String(m));window.confirm=()=>true;
 // Los PDF salen por _savePDF (la mayoría) o _pdfDownload (liquidación e informe del coche): se capturan los dos
 _savePDF=_pdfDownload=function(doc,fn){window.__PDF[window.__K]={name:fn,u:doc.output('datauristring')};};
 return true;})()"""
JOBS=[('analitica',["generateAnalyticsPDF('%s','%s')"%(PM,M)],['INFORME']),
      ('recibo-b3',["generateReceiptPDF('b3')"],['Recibo','Alejandro José Martínez de la Fuente','2222CCC']),
      ('recibo-b2',["generateReceiptPDF('b2')"],['Recibo','María Fernanda Castillo Rodríguez']),
      ('recibo-b41',["generateReceiptPDF('b41')"],['Recibo','Marta Ruiz']),
      ('anexo-b3',["showBookingById('b3')","generateExtensionPDF('b3')"],['Anexo','2222CCC']),
      ('contrato-b3',["openContractForm('v3','b3')","document.getElementById('ctClNac').value='1990-05-14';_ctGo(4)","generateContractPDF('v3','b3')"],['CONTRATO','26 años cumplidos','0,19 €/km','Alejandro José Martínez de la Fuente']),
      ('contrato-gestion',["openMgmtContractForm('o1','v2')","generateMgmtContractPDF('o1','v2')"],['Ana Propietaria Ejemplo','1111BBB']),
      ('mantenimiento-v3',["dlMaintReport('v3')"],['Aceite y filtros','Taller Prueba']),
      ('negocio',["dlBizReport('%s','%s','Periodo')"%(PM,M)],['DEIROS']),
      ('liquidacion',["dlOwnerReport('o1','%s')"%M],['LIQUIDACIÓN MENSUAL','Ana Propietaria Ejemplo','TOTAL A PAGAR']),
      ('informe-coche',["dlReport('v3','%s')"%M],['2222CCC']),
      ('presupuesto-q1',["generateQuotePDF('q1')"],['PRE-2026-0042','Lucía Herrera Gómez','26 años cumplidos']),
      ('presupuesto-q3',["generateQuotePDF('q3')"],['PRE-2026-0039','Mudanzas Ejemplo S.L.'])]
with H.playwright() as p:
    br=H.launch(p)
    ctx,pg=H.open_app(br)
    J=lambda js,a=None:pg.evaluate(js,a);W=lambda ms=400:pg.wait_for_timeout(ms)
    J(SCEN);J(H.PDFTEXT)
    for name,steps,need in JOBS:
        J("k=>{window.__K=k;window.__AL=[];try{closeSheet()}catch(e){}}",name);W(200)
        err=''
        for s in steps:
            try:J("async()=>{await (async()=>{return %s})();}"%s);W(450)
            except Exception as e:err=str(e).split('\n')[0][:200]
        W(300);r=J("k=>window.__PDF[k]||null",name);al=J("window.__AL")
        if not r:chk(False,'PDF «%s»: se genera'%name,{'error':err,'alertas':al});continue
        f=os.path.join(TMP,name+'.pdf');open(f,'wb').write(base64.b64decode(r['u'].split(',',1)[1]))
        n,t=pdfinfo(f),pdftext(f)
        falta=[x for x in need if x not in t]
        chk(not err and not al and n>=1 and len(t)>200 and not falta,'PDF «%s» (%s): %d página(s), %d KB, con su contenido'%(name,r['name'],n,os.path.getsize(f)//1024),{'error':err,'alertas':al,'falta':falta})
    J("try{closeSheet()}catch(e){}")
    # Actas (generadas aparte por _actaPDF, sin fotos en la nube: solo km y combustible)
    for fase in ('entrega','devolucion'):
        J("(()=>{const b=V.find(v=>v.id==='v4').bookings.find(b=>b.id==='b41');b.kmStart=46000;b.kmEnd=46200;b.deliveredFuelLevel='Lleno (100%)';b.returnedFuelLevel='3/4';})()")
        try:
            r=J("f=>_actaPDF('b41',f).then(r=>({name:r.name,u:r.doc.output('datauristring')}))",fase)
            f=os.path.join(TMP,'acta-'+fase+'.pdf');open(f,'wb').write(base64.b64decode(r['u'].split(',',1)[1]));t=pdftext(f)
            chk(pdfinfo(f)>=1 and ('Acta de '+('entrega' if fase=='entrega' else 'devolución')) in t and '3333DDD' in t,'PDF «acta de %s» (%s): se genera con partes, matrícula y km'%(fase,r['name']))
        except Exception as e:chk(False,'PDF «acta de %s»: se genera'%fase,str(e)[:200])
    # ── Informe de mantenimientos (#144): gastos sin datos del taller, recurrentes y coche sin mantenimientos ──
    def maint(fins):
        return J("async f=>{const v=V.find(x=>x.id==='v1');v.finances=f;const L=await __pdfText(()=>dlMaintReport('v1'),true);return L.map(t=>t.replace(/[\\u00a0\\u202f]/g,' '));}",fins)
    conMaint={'id':'g1','type':'expense','date':'2026-03-10','category':'Mantenimiento periódico','amount':180,'description':'Revisión','maint':{'work':'Aceite y filtros','km':40000,'nextKm':55000,'nextDate':'2027-03-10','shop':'Taller Prueba'}}
    conMaint2={'id':'g2','type':'expense','date':'2026-09-02','category':'Mantenimiento','amount':95.5,'description':'','maint':{'work':'','km':52000,'nextKm':None,'nextDate':'','shop':''}}
    sinMaint={'id':'g3','type':'expense','date':'2026-06-15','category':'Mantenimiento','amount':60,'description':'Pastillas de freno'}
    sinMaintNiDesc={'id':'g5','type':'expense','date':'2026-07-01','category':'Mantenimiento periódico','amount':20,'description':''}
    recurrente={'id':'g4','type':'expense','date':'2026-11-01','category':'Mantenimiento','amount':45,'description':'Plan taller (recurrente)','_recurringId':'r1'}
    L=maint([conMaint,conMaint2])
    chk(not any(t.startswith('ERROR') for t in L) and 'Aceite y filtros' in L and 'Taller: Taller Prueba' in L and '40.000 km' in L,'Mantenimientos con datos del taller: trabajo, taller y km en el PDF',[t for t in L if t.startswith('ERROR')])
    L=maint([conMaint,sinMaint,sinMaintNiDesc])
    chk(not any(t.startswith('ERROR') for t in L),'Gasto «Mantenimiento» sin datos del taller: sin error (#144)',[t for t in L if t.startswith('ERROR')])
    chk('3' in L,'Cuenta los 3 mantenimientos (no se excluye ninguno)')
    chk('15/06/2026' in L and '60,00 €' in L and 'Pastillas de freno' in L,'El gasto sin datos sale con fecha, importe y descripción')
    chk('—' in L and 'Taller: —' in L,'«—» en km y taller cuando no hay datos')
    chk('01/07/2026' in L and '20,00 €' in L,'Sin descripción tampoco: sale con fecha e importe')
    chk('260,00 €' in L,'Coste total = 180 + 60 + 20 = 260,00 €')
    L=maint([recurrente])
    chk(not any(t.startswith('ERROR') for t in L) and 'Plan taller (recurrente)' in L and '45,00 €' in L and '01/11/2026' in L,'Recurrente de Mantenimiento: sale sin error')
    L=maint([{'id':'x','type':'expense','date':'2026-05-01','category':'Seguro','amount':300}])
    chk('Sin mantenimientos registrados.' in L,'Coche sin mantenimientos: «Sin mantenimientos registrados.»')
    chk(not J("window.__AL"),'Sin alertas',J("window.__AL"))
    br.close()
H.fin()
