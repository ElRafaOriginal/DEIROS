# Edad mínima del conductor: 26 años cumplidos (con 25 no se alquila), fija y no configurable: contrato (formulario y PDF),
# presupuesto (PDF), alta del alquiler (bloquea), edición del cliente, «Antes de entregar» y conductor adicional.
# Origen: specs/edad25/test_edad25.js (era en node con funciones extraídas; ahora con la app real en el navegador).
# Uso: python3 tests/test_edad.py
import sys,os,json,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
chk=H.chk
with H.playwright() as p:
    br=H.launch(p)
    # Escenario hostil: edadMin '18' guardado en los datos de empresa del móvil
    ctx,pg=H.open_app(br,extra="window.alert=m=>{(window.__AL=window.__AL||[]).push(String(m))};window.confirm=()=>true;"
                      "localStorage.setItem('deiros_company',JSON.stringify({nombre:'DEIROS',nif:'B00000000',direccion:'C/ Ejemplo 12, 28320 Pinto',telefono:'600 000 000',ciudad:'Pinto',fianza:'200',edadMin:'18'}));",company=False)
    J=lambda js,a=None:pg.evaluate(js,a);W=lambda ms=400:pg.wait_for_timeout(ms)
    J(H.PDFTEXT)
    # ── Reglas: _clAge y _clAgeGate (26 cumplidos el día de inicio) ──
    chk(J("_clAge('2000-11-20','2026-11-20')")==26 and J("_clAge('2000-11-21','2026-11-20')")==25,'Edad en la fecha de inicio: 26 el día del cumpleaños, 25 el día antes')
    chk(J("_clAgeGate('2000-11-20','2026-11-20',false)")=='','26 años cumplidos: se puede alquilar')
    chk(J("_clAgeGate('2000-11-21','2026-11-20',false)")=='Menor de 26 en la fecha de inicio: no se puede alquilar','25 años (cumple 26 al día siguiente): no se puede alquilar',J("_clAgeGate('2000-11-21','2026-11-20',false)"))
    chk(J("_clAgeGate('2006-01-01','2026-11-20',true)")=='Conductor adicional: menor de 26 en la fecha de inicio: no se puede alquilar','Conductor adicional de 20 años: tampoco')
    chk('obligatoria' in J("_clAgeGate('','2026-11-20',false)"),'Sin fecha de nacimiento: es obligatoria')
    # ── Contrato: formulario con la edad fija y PDF ──
    J("openContractForm('v3','b3')");W(500)
    f=J("(()=>{const sc=document.getElementById('SC');const i=[...sc.querySelectorAll('input[readonly]')].find(e=>e.value==='26 años cumplidos');return {fijo:!!i,campo:!!document.getElementById('ctEdadMin'),html:sc.innerHTML.includes('edadMin')};})()")
    chk(f['fijo'] and not f['campo'],'Formulario del contrato: «Edad mínima: 26 años cumplidos» fijo (sin campo editable)',f)
    J("(()=>{const g=id=>document.getElementById(id);g('ctClNac').value='1990-05-14';if(g('ctSaveDefaults'))g('ctSaveDefaults').checked=true;_ctGo(4);})()");W(300)
    t=' '.join(J("__pdfText(()=>generateContractPDF('v3','b3'),true)"))
    ages=re.findall(r'(\S+\s+\S+\s+)?(\d+)\s*años',t)
    chk('Todos con 26 años cumplidos' in t,'Contrato (PDF): «Todos con 26 años cumplidos y permiso válido en vigor»')
    chk(not re.search(r'edad m[ií]nima|\b(18|21|23|25)\s*años',t,re.I),'Contrato (PDF): sin 18/21/23/25 años aunque el móvil tenga guardado 18',[m for m in re.findall(r'\b\d+\s*años',t)])
    chk(not [x for x in J("window.__AL||[]") if 'ERROR' in x.upper()],'Contrato generado sin alertas de error',J("window.__AL||[]"))
    co=json.loads(J("localStorage.getItem('deiros_company')"))
    chk(co.get('edadMin') in (None,'25','26'),'Guardar predeterminados no deja una edad menor: edadMin = %r'%co.get('edadMin'))
    J("closeSheet()")
    # ── Presupuesto (PDF) ──
    t=' '.join(J("__pdfText(()=>generateQuotePDF('q1'),true)"))
    chk('Conductor con 26 años cumplidos' in t,'Presupuesto (PDF): «Conductor con 26 años cumplidos»')
    chk(not re.search(r'\b(18|21|23|25)\s*años',t),'Presupuesto (PDF): sin otras edades')
    # ── Alta: con 25 años no se guarda; con 26 sí ──
    def alta(nac,dias):
        J("window.__AL=[];closeSheet();openV('v4');openNewRental()");W(500)
        J("([s,e,n])=>{const g=id=>document.getElementById(id);g('rSD').value=s;g('rED').value=e;g('rAmt').value='90';g('rClientPicker').value='Edad Prueba';g('rCN').value='Edad Prueba';g('rClBirth').value=n;}",[H.d(dias),H.d(dias+2),nac])
        n0=J("V.find(v=>v.id==='v4').bookings.length");J("submitRental()");W(500)
        return J("V.find(v=>v.id==='v4').bookings.length")-n0,J("window.__AL")
    sd=H.HOY+__import__('datetime').timedelta(days=30)
    n25=sd.replace(year=sd.year-26)+__import__('datetime').timedelta(days=1)   # cumple 26 el día después del inicio
    n,al=alta(n25.isoformat(),30)
    chk(n==0 and any('Menor de 26' in a for a in al),'Alta con 25 años cumplidos el día de inicio: aviso «Menor de 26» y no se guarda',al)
    n,al=alta(sd.replace(year=sd.year-26).isoformat(),40)
    chk(n==1 and not al,'Alta con 26 años cumplidos: se guarda',al)
    J("closeSheet()")
    # ── Ficha del cliente: el texto de ayuda ──
    J("nav('clients');openEditClient('c1')");W(400)
    chk('Edad mínima para alquilar: 26 años' in J("document.getElementById('SC').textContent"),'Editar cliente: «Edad mínima para alquilar: 26 años cumplidos»')
    J("closeSheet()")
    br.close()
H.fin()
