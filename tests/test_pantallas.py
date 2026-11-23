# Barrido de TODAS las pantallas, hojas y avisos de la app a 390 px (oscuro): sin errores JS y sin nada que se salga
# por la derecha (ni campos que se pasen de su caja). Origen: specs/auditoria/render_app.py + uiC/render_C.py («todas»).
# Uso: python3 tests/test_pantallas.py [--rapido] [--claro]
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
RAPIDO='--rapido' in sys.argv;THEME='light' if '--claro' in sys.argv else 'dark'
def page(n,js):return (n,js,'page')
def sheet(n,js):return (n,js,'sheet')
def over(n,js):return (n,js,'over')
S=[
 page('01-resumen',"nav('dashboard')"),
 over('01-menu',"nav('dashboard');openHamburger()"),
 page('02-alquileres',"nav('rentals')"),
 sheet('02a-hoja-vehiculo',"nav('rentals');openNewRentalPicker()"),
 sheet('02b-ficha-alquiler',"nav('rentals');showBookingById('b3')"),
 sheet('02c-asistente-1-datos',"openV('v3');openNewRental()"),
 sheet('02d-asistente-2-extras',"openV('v3');openNewRental();document.getElementById('rAmt').value='120';_rwGo(2)"),
 sheet('02e-asistente-3-resumen',"openV('v3');openNewRental();document.getElementById('rAmt').value='120';_rwGo(2);_rwGo(3)"),
 sheet('02f-devolucion',"openV('v3');openReturnModal('b3')"),
 sheet('02g-ampliacion',"openV('v3');openExtendBooking('b3')"),
 sheet('02h-cobros',"openV('v3');openBookingFinance('b3')"),
 sheet('02i-cancelar',"openV('v3');openCancelBooking('b3')"),
 sheet('02j-editar-alquiler',"openV('v3');editBooking('b3')"),
 sheet('02k-fianzas',"nav('dashboard');openPendingDeposits()"),
 sheet('02l-entregar-coche',"openV('v3');_fxDeliver('b31')"),
 page('03-flota-lista',"nav('vehicles')"),
 page('03a-flota-tarjetas',"nav('vehicles');_vListMode='extended';renderListBody()"),
 page('03b-flota-cuadricula',"nav('vehicles');_vListMode='grid';renderListBody()"),
 page('03c-coche-alquileres',"_vListMode='compact';openV('v3')"),
 page('03d-coche-finanzas',"openV('v3');switchTab('finances')"),
 page('03e-coche-info',"openV('v3');switchTab('info')"),
 sheet('03f-editar-vehiculo',"openV('v3');openEditV('v3')"),
 sheet('03g-nuevo-vehiculo',"nav('vehicles');openAddV()"),
 sheet('03h-nuevo-gasto-coche',"openV('v3');openAddEntry()"),
 sheet('03i-recurrentes-coche',"openV('v3');openVehicleRecurring('v3')"),
 sheet('03j-informe-coche',"openV('v3');openReport('v3')"),
 page('04-agenda-lista',"nav('agenda')"),
 page('04a-agenda-semana',"nav('agenda');agMobSetMode('week')"),
 page('05-negocio',"agMobSetMode&&agMobSetMode('list');nav('biz')"),
 sheet('05a-nuevo-movimiento',"nav('biz');openAddBiz()"),
 sheet('05b-informe-negocio',"nav('biz');openBizReportPicker()"),
 page('06-analitica',"nav('analytics')"),
 page('07-presupuestos',"nav('quotes')"),
 sheet('07a-presupuesto-form',"nav('quotes');openNewQuote()"),
 page('07b-presupuesto-detalle',"nav('quotes');_quoteEditId='q1';showQuoteDetail(document.getElementById('PC'))"),
 sheet('07c-presupuesto-estado',"nav('quotes');openQuoteStatusMenu('q1')"),
 sheet('07d-coches-libres',"nav('dashboard');openFreeVehiclesSearch()"),
 page('08-contratos',"nav('contracts')"),
 sheet('08a-contrato-asistente',"nav('contracts');openContractWizard()"),
 sheet('08b-contrato-paso1',"openContractForm('v3','b3')"),
 sheet('08c-contrato-paso2',"openContractForm('v3','b3');_ctGo(2)"),
 sheet('08d-contrato-paso3',"openContractForm('v3','b3');_ctGo(3)"),
 sheet('08e-contrato-paso4',"openContractForm('v3','b3');_ctGo(4)"),
 sheet('08f-contrato-gestion',"openMgmtContractForm('o1','v2')"),
 page('09-clientes',"nav('clients')"),
 page('09a-cliente-ficha',"nav('clients');_clientDetail='c1';renderClientDetail(document.getElementById('PC'))"),
 sheet('09b-cliente-editar',"nav('clients');openEditClient('c1')"),
 sheet('09c-cliente-nuevo',"nav('clients');openAddClient()"),
 page('10-propietarios',"nav('owners')"),
 page('10a-propietario-perfil',"openOwnerProfile('o1')"),
 sheet('10b-propietario-nuevo',"nav('owners');openAddOwner()"),
 sheet('10c-propietario-informe',"nav('owners');openOwnerReport('o1')"),
 page('11-archivo',"nav('archive')"),
 page('12-recurrentes',"nav('recurring')"),
 sheet('12a-recurrente-nuevo',"nav('recurring');openAddRecurring()"),
 sheet('13-notificaciones',"nav('dashboard');openNotifSettings()"),
 sheet('13a-copia-seguridad',"nav('dashboard');openBackup()"),
 sheet('13b-informe-analitica',"nav('analytics');openAnalyticsReportPicker()"),
 sheet('13c-resenas',"nav('dashboard');openReviewSettings()"),
 over('13d-whatsapp',"nav('dashboard');_waPick('b','b3')"),
 over('14-toast-error',"nav('dashboard');_saveToast('Error al guardar: sin conexión')"),
 over('14a-aviso-copia',"nav('dashboard');localStorage.removeItem('deiros_lastBackupAt');localStorage.removeItem('deiros_lastBackupRemindAt');checkBackupReminder()"),
 over('14b-aviso-normalizacion',"nav('dashboard');_showNormNotice(3,'import')"),
 page('15-vacio-archivo',"nav('archive')"),
 over('00-carga',"showLoading(true)"),over('00-login',"showLoading(false);showLogin(true)"),over('00-error-carga',"showLogin(false);_showLoadError()"),
]
ESENCIAL={'01-resumen','02-alquileres','02b-ficha-alquiler','02c-asistente-1-datos','02f-devolucion','03-flota-lista','03c-coche-alquileres','03d-coche-finanzas',
          '05-negocio','06-analitica','07-presupuestos','08b-contrato-paso1','09a-cliente-ficha','10a-propietario-perfil','13a-copia-seguridad'}
LIST=[s for s in S if s[0] in ESENCIAL] if RAPIDO else S
CLEAN=("try{_waClose()}catch(e){};try{closeSheet()}catch(e){};try{closeHamburger()}catch(e){};['normNotice','backupReminder','saveStatus','actaOf','cloudConflict'].forEach(i=>{const e=document.getElementById(i);if(e)e.remove()});"
       "document.querySelectorAll('.d-toast').forEach(e=>e.remove());[...document.body.children].forEach(e=>{if(e.tagName==='DIV'&&!e.id&&e.style.position==='fixed'&&e.style.zIndex==='9999')e.remove()});"
       "try{AV=null}catch(e){};try{_clientDetail=null}catch(e){};try{showLoading(false);showLogin(false)}catch(e){}")
# Elementos visibles que se salen por la derecha (fuera de zonas con scroll horizontal) y campos que se pasan de su caja
CHK=r"""()=>{const sh=document.getElementById('SH');const els=[...document.querySelectorAll('#PC *'),...(sh&&sh.classList.contains('open')?sh.querySelectorAll('*'):[]),...document.querySelectorAll('.topbar *,#hamburgerPanel *,.wa-sh *')];
 const W=document.documentElement.clientWidth;
 return els.filter(e=>{const b=e.getBoundingClientRect();if(!(b.width>0&&b.height>0))return false;if(e.closest('#hamburgerPanel')&&getComputedStyle(document.getElementById('hamburgerMenu')).display==='none')return false;
   let p=e.parentElement;while(p&&p.id!=='PC'&&p.id!=='SC'&&p.id!=='hamburgerPanel'&&p!==document.body){const s=getComputedStyle(p);if(s.overflowX==='auto'||s.overflowX==='scroll'||s.overflowX==='hidden')return false;p=p.parentElement;}
   return b.right>W+1}).concat([...document.querySelectorAll('#PC input,#PC select,#SC input,#SC select')].filter(e=>{const b=e.getBoundingClientRect();if(!(b.width>0&&b.height>0)||e.type==='checkbox'||e.type==='radio')return false;
   let a=e.parentElement;while(a&&a.id!=='PC'&&a.id!=='SC'){const s=getComputedStyle(a);const pr=parseFloat(s.paddingRight)+parseFloat(s.borderRightWidth);const r=a.getBoundingClientRect();
     if(s.overflowX==='auto'||s.overflowX==='scroll'||s.overflowX==='hidden'){if(b.right>r.right-parseFloat(s.borderRightWidth)+1)return true;}
     if(pr>0)return b.right>r.right-pr+1;a=a.parentElement;}return b.right>W+1;})).map(e=>e.tagName+'.'+String(e.className&&e.className.baseVal!==undefined?e.className.baseVal:e.className).slice(0,30)+(e.id?'#'+e.id:'')).slice(0,5)}"""
P="document.getElementById('mainPage')"
with H.playwright() as p:
    br=H.launch(p);cur=['inicio'];errs=[]
    ctx,pg=H.open_app(br,theme=THEME,extra="window.alert=()=>{};window.confirm=()=>false;",errs=errs,wait=1800)
    pg.on('pageerror',lambda e:None)
    n_ok=0
    for n,js,kind in LIST:
        e0=len(errs);cur[0]=n
        if n=='15-vacio-archivo':pg.evaluate("V=V.filter(v=>!v.archived)")
        pg.evaluate(CLEAN);pg.wait_for_timeout(200)
        try:pg.evaluate(js)
        except Exception as e:H.chk(False,n+': se abre sin error',str(e)[:200]);continue
        pg.wait_for_timeout(900 if kind=='page' else 600)
        if kind=='page':pg.evaluate(P+".scrollTop=0")
        if kind=='sheet':pg.evaluate("document.getElementById('SH').scrollTop=0")
        if kind=='sheet':
            if not pg.evaluate("document.getElementById('SH').classList.contains('open')"):H.chk(False,n+': la hoja se abre');continue
        o=pg.evaluate(CHK);je=errs[e0:]
        H.chk(not o and not je,n+': sin errores JS ni desbordes a 390 px',{'desbordes':o,'errores':je[:3]})
        n_ok+=bool(not o and not je)
    print('%d de %d pantallas, hojas y avisos sin errores JS ni desbordes a 390 px'%(n_ok,len(LIST)))
    del errs[:]
    br.close()
H.fin()
