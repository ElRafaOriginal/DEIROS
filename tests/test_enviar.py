# WhatsApp y «Enviar» (#96): normalización de teléfonos, Llamar/WhatsApp en la ficha del alquiler, Hoy, cliente,
# propietario y presupuesto; mensajes exactos (confirmación, recordatorio, fianza devuelta, presupuesto) y enlaces wa.me
# bien escapados; «Enviar» de cada PDF con el menú de compartir (navigator.share con un File PDF) y, si no se puede, lo de
# siempre; lugar de entrega y devolución en el alquiler (alta, edición, contrato, WhatsApp; alquileres antiguos sin ellos).
# Origen: specs/bloqueC/test_bloqueC.py. La referencia «main» se ha cambiado por una SEGUNDA pestaña con la misma app:
# el PDF de «Enviar» debe ser idéntico, byte a byte, al del botón de siempre. Quitado: «main no tiene los botones del propietario».
# Uso: python3 tests/test_enviar.py
import sys,os,json,re,datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
from urllib.parse import quote
HTML=H.INDEX;SHOTS=H.CAPTURAS
route,D0,FAKE=H.route,H.datos(),H.FAKE
g={'P':"document.getElementById('mainPage')",'D':D0,'route':route,'FAKE':FAKE}
from playwright.sync_api import sync_playwright
errs=H.ERRS;chk=H.chk
hoy=H.HOY;dd=lambda n:(hoy+datetime.timedelta(days=n)).isoformat()
DIAS=['lunes','martes','miércoles','jueves','viernes','sábado','domingo'];MESES=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
def dia(n):x=hoy+datetime.timedelta(days=n);return f'{DIAS[x.weekday()]}, {x.day} de {MESES[x.month-1]}'
E=' €'
encURI=lambda s:quote(s,safe="-_.!~*'()")
# Escenario: datos raros (& ? # " tildes y eñes) en coche y cliente; teléfonos en varios formatos; sin teléfono
SCEN=r"""(()=>{const h=todayStr(),A=n=>addDays(h,n),bk=(id,s,e,x)=>Object.assign({id,startDate:s,startTime:'10:00',endDate:e,endTime:'18:30',platform:'sinapp',amount:120,clientName:'',clientPhone:'',clientDni:'',finance:[],extras:[]},x||{});
 const P=(vid,b)=>{const v=V.find(x=>x.id===vid);v.bookings=v.bookings||[];v.bookings.push(b);};
 V.forEach(v=>{v.bookings=(v.bookings||[]).filter(x=>!String(x.id).startsWith('T_'));});
 V.find(v=>v.id==='v4').name='Peugeot 208 "GT" & Co #1?';
 P('v4',bk('T_wa',A(2),A(5),{clientName:'José Ñúñez & Hijos? #1',clientPhone:'+34 600-111-222',fianza:200}));        // próximo, con fianza
 P('v4',bk('T_cur',A(-2),A(1),{clientName:'Ana',clientPhone:'0034 600 333 444',delivered:true}));                      // en curso, sin fianza
 P('v4',bk('T_fz',A(-9),A(-6),{clientName:'Eva Ruiz',clientPhone:'611222333',delivered:true,returned:true,fianza:200,fianzaStatus:'partial',fianzaRetainedAmount:50,fianzaRetainedReason:'Limpieza & olor #2'}));
 P('v4',bk('T_fzr',A(-19),A(-16),{clientName:'Leo',clientPhone:'611222334',delivered:true,returned:true,fianza:200,fianzaStatus:'retained',fianzaRetainedAmount:200}));
 P('v4',bk('T_fzok',A(-29),A(-26),{clientName:'Mar',clientPhone:'611222335',delivered:true,returned:true,fianza:200,fianzaStatus:'returned'}));
 P('v4',bk('T_none',A(10),A(12),{clientName:'Persona Sin Ficha Ninguna'}));                                              // sin teléfono ni ficha
 P('v4',bk('T_short',A(14),A(15),{clientName:'Corto',clientPhone:'12345'}));                                             // número no válido
 P('v1',bk('T_hoy',h,A(3),{clientName:'Hoy Con Tel',clientPhone:'(+58) 412-555-1234',startTime:'09:00'}));             // Hoy, extranjero
 P('v5',bk('T_hoy2',h,A(2),{clientName:'Hoy Sin Ficha Nadie',startTime:'11:00'}));                                    // Hoy sin teléfono
 CL.push({id:'c8',name:'Pepe Sinalquiler',phone:'699 88 77 66',bookingIds:[]},{id:'c9',name:'Rosa Sintel',phone:'',bookingIds:['T_wa']});
 const q=QT.find(x=>x.id==='q2');q.clientId='c2';q.clientName='María & Cía? #3';q.totalAmount=175;q.fianza=200;q.dur=7;q.vehicleId='v4';
 QT.find(x=>x.id==='q1').clientId='';QT.find(x=>x.id==='q1').totalAmount=116;
 const b3=V.find(v=>v.id==='v3').bookings.find(b=>b.id==='b3');b3.finance=(b3.finance||[]).filter(f=>f.id!=='T_amp');b3.finance.push({id:'T_amp',type:'income',concept:'Ampliación '+b3.endDate+' → '+A(30),amount:60,date:h,notes:'Total anterior: 300 · Nuevo total: 360'});
 _invalidateRsCache&&_invalidateRsCache();return true;})()"""
INIT="""window.__DATA=%s;localStorage.setItem('wg_theme','dark');localStorage.setItem('deiros_lastBackupAt',new Date().toISOString());
window.alert=m=>{(window.__AL=window.__AL||[]).push(m);};window.confirm=m=>true;
window.__OPEN=[];window.open=function(u,t,f){window.__OPEN.push([String(u),t||'',f||'']);return {document:{write(){}}};};
window.__AC=[];HTMLAnchorElement.prototype.click=function(){window.__AC.push({href:this.href,download:this.getAttribute('download')||'',target:this.target||''});};
window.__BL={};const _cou=URL.createObjectURL.bind(URL);URL.createObjectURL=function(b){const u=_cou(b);window.__BL[u]=b;return u;};
window.__SH=[];window.__shRes='ok';window.__can=true;
window.__shareOn=function(){navigator.share=function(d){window.__SH.push(d);return window.__shRes==='ok'?Promise.resolve():Promise.reject(new DOMException('x',window.__shRes));};navigator.canShare=function(d){return window.__can&&!!(d&&d.files&&d.files.length);};};
window.__shareOff=function(){navigator.share=undefined;navigator.canShare=undefined;};
window.__hash=async function(b){const h=await crypto.subtle.digest('SHA-256',await b.arrayBuffer());return [...new Uint8Array(h)].map(x=>x.toString(16).padStart(2,'0')).join('');};
window.__fixPDF=function(){if(window.jspdf.__fixed)return;const O=window.jspdf.jsPDF;const W=function(...a){const d=new O(...a);d.setCreationDate(new Date(Date.UTC(2026,0,1)));d.setFileId('0123456789ABCDEF0123456789ABCDEF');return d;};Object.assign(W,O);W.API=O.API;window.jspdf.jsPDF=W;window.jspdf.__fixed=1;};
"""
def page(b,html):
    ctx=H.new_context(b,viewport={'width':390,'height':844},device_scale_factor=1);ctx.route('**/*',route)
    ctx.add_init_script(INIT%json.dumps(D0));ctx.add_init_script(FAKE)
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(os.path.basename(html)+': '+str(e)))
    pg.goto('file://'+os.path.abspath(html));pg.wait_for_timeout(1800)
    pg.evaluate(SCEN);pg.evaluate("ensureLib('jspdf')");pg.evaluate("__fixPDF()")
    return pg
def run():
  with sync_playwright() as p:
    b=H.launch(p)
    pm=page(b,HTML);pg=page(b,HTML)
    # ── 1. Normalización del número ──
    CASES=[('600 000 002','34600000002'),('+34 600-000-002','34600000002'),('0034 600 000 002','34600000002'),('(+58) 412-555-1234','584125551234'),
           ('612345678 / 699999999','34612345678'),('912 34 56 78','34912345678'),('+44 7700 900123','447700900123'),('34600000002','34600000002'),
           ('12345',''),('',''),(None,''),('abc','')]
    got=pg.evaluate("c=>c.map(x=>_waNum(x))",[c[0] for c in CASES])
    for (i,e),gv in zip(CASES,got): chk(gv==e,f'Número {i!r} → {gv!r} (esperado {e!r})')
    # ── 2. Ficha del alquiler: Llamar y WhatsApp; hoja de mensajes; enlaces bien escapados ──
    pg.evaluate("window.__co=localStorage.getItem('deiros_company');localStorage.setItem('deiros_company',JSON.stringify(Object.assign(getCompanyData(),{ciudad:'Pinto',ciudadEntrega:'Calle Ejemplo 1, Pinto'})))")
    pg.evaluate("showBookingById('T_wa')");pg.wait_for_timeout(400)
    tel=pg.evaluate("document.querySelector('#SC .wa-two a')?.getAttribute('href')")
    chk(tel=='tel:+34600111222',f'Ficha del alquiler: «Llamar» = tel:+34600111222 ({tel})')
    sz=pg.evaluate("[...document.querySelectorAll('#SC .wa-two>*')].map(e=>[Math.round(e.getBoundingClientRect().height),e.textContent.trim()])")
    chk(len(sz)==2 and all(h>=44 for h,_ in sz) and [t for _,t in sz]==['Llamar','WhatsApp'],f'Dos botones de al menos 44 px: Llamar y WhatsApp ({sz})')
    chk(pg.evaluate("document.querySelectorAll('#SC .btn-pri').length")==1,'La ficha sigue con un solo botón dorado')
    pg.click('#SC .wa-two button');pg.wait_for_timeout(400)
    st=pg.evaluate("[!!_waEl,document.getElementById('SH').classList.contains('open'),[...document.querySelectorAll('.wa-p button')].map(b=>b.textContent+(b.getAttribute('aria-pressed')==='true'?'*':''))]")
    chk(st==[True,True,['Confirmación*','Recordatorio','En blanco']],f'Hoja de WhatsApp encima de la ficha (que sigue abierta); próximo → «Confirmación» elegida; sin «Fianza devuelta» mientras no se ha devuelto el coche ({st})')
    cf=("Hola José, tu reserva con Deiros está confirmada.\n\n"
        f"Coche: Peugeot 208 \"GT\" & Co #1? (3333DDD)\nRecogida: {dia(2)} a las 10:00\nDevolución: {dia(5)} a las 18:30\nLugar de entrega: \n"
        f"Total: 120,00{E} (IVA incluido)\nFianza: 200,00{E}, se devuelve al terminar si todo está correcto.\n\n"
        "Trae tu DNI y el carnet de conducir. Cualquier duda, escríbeme por aquí.\n\nDeiros · deiros.net")
    tx,href=pg.evaluate("[document.getElementById('waTx').value,document.getElementById('waGo').getAttribute('href')]")
    chk(tx==cf,'Texto de confirmación exacto (con & ? # comillas y tildes tal cual)'+('' if tx==cf else f'\n   esperado: {cf!r}\n   obtenido: {tx!r}'))
    chk(href=='https://wa.me/34600111222?text='+encURI(cf),f'Enlace wa.me = número normalizado + encodeURIComponent del texto ({href[:90]}…)')
    chk('Pinto' not in tx and 'Calle Ejemplo' not in tx,'Confirmación: «Lugar de entrega: » vacío aunque los datos de empresa tengan lugar y ciudad (lo escribe Rafael)')
    cur=pg.evaluate("(()=>{const x=document.getElementById('waTx');return [document.activeElement===x,x.selectionStart,x.selectionEnd,x.value.indexOf('Lugar de entrega: ')+'Lugar de entrega: '.length];})()")
    chk(cur[0] and cur[1]==cur[2]==cur[3],f'Al abrir la hoja, el cursor queda al final de «Lugar de entrega: » ({cur})')
    q=href.split('?text=')[1];chk(not any(c in q for c in '&?# "\n'),'El texto codificado no deja & ? # comillas, espacios ni saltos sueltos en el enlace')
    pg.click('.wa-p button:has-text("Recordatorio")');pg.wait_for_timeout(100)
    rd=(f"Hola José, te recuerdo la devolución del Peugeot 208 \"GT\" & Co #1? (3333DDD):\n\nCuándo: {dia(5)} a las 18:30\nDónde: \n\n"
        "Devuélvelo con el mismo nivel de combustible con el que lo recogiste. Si necesitas más días, avísame y lo vemos.\n\nDeiros · deiros.net")
    tx,href=pg.evaluate("[document.getElementById('waTx').value,document.getElementById('waGo').getAttribute('href')]")
    chk(tx==rd and href=='https://wa.me/34600111222?text='+encURI(rd),'Recordatorio de devolución exacto y su enlace')
    cur=pg.evaluate("(()=>{const x=document.getElementById('waTx');return [document.activeElement===x,x.selectionStart,x.selectionEnd,x.value.indexOf('Dónde: ')+'Dónde: '.length];})()")
    chk(cur[0] and cur[1]==cur[2]==cur[3],f'Recordatorio: el cursor queda al final de «Dónde: » ({cur})')
    pg.keyboard.type('Estación de Pinto & #2');pg.wait_for_timeout(100)
    tx,href=pg.evaluate("[document.getElementById('waTx').value,document.getElementById('waGo').getAttribute('href')]")
    rd2=rd.replace('Dónde: \n','Dónde: Estación de Pinto & #2\n')
    chk(tx==rd2 and href=='https://wa.me/34600111222?text='+encURI(rd2),'Escribir el lugar en la hoja lo pone en esa línea y actualiza el enlace')
    pg.fill('#waTx','Hola & adiós? #ñ');pg.wait_for_timeout(100)
    href=pg.evaluate("document.getElementById('waGo').getAttribute('href')")
    chk(href=='https://wa.me/34600111222?text=Hola%20%26%20adi%C3%B3s%3F%20%23%C3%B1',f'Editar el texto actualiza el enlace ({href})')
    pg.click('.wa-p button:has-text("En blanco")');pg.wait_for_timeout(100)
    href=pg.evaluate("document.getElementById('waGo').getAttribute('href')")
    chk(href=='https://wa.me/34600111222' and pg.evaluate("document.getElementById('waTx').value")=='','«En blanco»: sin texto y enlace sin ?text')
    chk(pg.evaluate("[document.getElementById('waGo').target,document.getElementById('waGo').rel,Math.round(document.getElementById('waGo').getBoundingClientRect().height),document.querySelectorAll('.wa-sh .btn-pri').length]")==['_blank','noopener',48,1],'«Abrir WhatsApp»: único botón dorado, 48 px, abre en otra pestaña/app')
    # Atrás del móvil: cierra solo la hoja de WhatsApp
    pg.evaluate("history.back()");pg.wait_for_timeout(500)
    chk(pg.evaluate("[!!_waEl,!!document.querySelector('.wa-sh'),document.getElementById('SH').classList.contains('open')]")==[False,False,True],'Atrás: cierra la hoja de WhatsApp y la ficha del alquiler sigue abierta')
    pg.click('#SC .wa-two button');pg.wait_for_timeout(300);pg.mouse.click(195,40);pg.wait_for_timeout(300)
    chk(pg.evaluate("[!!_waEl,document.getElementById('SH').classList.contains('open')]")==[False,True],'Tocar el velo cierra solo la hoja de WhatsApp')
    pg.evaluate("closeSheet()")
    # En curso → recordatorio por defecto; 0034 → 34
    pg.evaluate("showBookingById('T_cur')");pg.wait_for_timeout(300);pg.click('#SC .wa-two button');pg.wait_for_timeout(300)
    st=pg.evaluate("[document.querySelector('.wa-p [aria-pressed=true]').textContent,document.getElementById('waGo').getAttribute('href').split('?')[0],[...document.querySelectorAll('.wa-p button')].length]")
    chk(st==['Recordatorio','https://wa.me/34600333444',3],f'En curso: «Recordatorio» por defecto; 0034… → 34600333444; sin fianza no hay «Fianza devuelta» ({st})')
    pg.evaluate("_waClose();closeSheet();__co===null?localStorage.removeItem('deiros_company'):localStorage.setItem('deiros_company',__co)") # datos de empresa como en la otra pestaña (el contrato los usa)
    # Fianza devuelta en parte / entera / retenida entera
    pg.evaluate("showBookingById('T_fz')");pg.wait_for_timeout(300);pg.click('#SC .wa-two button');pg.wait_for_timeout(300)
    fz=("Hola Eva, ya te hemos devuelto 150,00"+E+" de la fianza del Peugeot 208 \"GT\" & Co #1? (200,00"+E+"). Hemos retenido 50,00"+E+" por: Limpieza & olor #2.\n\n"
        "Gracias por alquilar con Deiros. Aquí nos tienes para la próxima.\n\nDeiros · deiros.net")
    st=pg.evaluate("[document.querySelector('.wa-p [aria-pressed=true]').textContent,document.getElementById('waTx').value,document.getElementById('waGo').getAttribute('href')]")
    chk(st[0]=='Fianza devuelta' and st[1]==fz and st[2]=='https://wa.me/34611222333?text='+encURI(fz),'Devuelto con fianza retenida en parte: «Fianza devuelta» por defecto con lo devuelto, lo retenido y el motivo'+('' if st[1]==fz else f'\n   {st[1]!r}'))
    pg.evaluate("_waClose();closeSheet();showBookingById('T_fzok')");pg.wait_for_timeout(300);pg.click('#SC .wa-two button');pg.wait_for_timeout(300)
    fz2=("Hola Mar, ya te hemos devuelto la fianza del Peugeot 208 \"GT\" & Co #1?: 200,00"+E+".\n\nGracias por alquilar con Deiros. Aquí nos tienes para la próxima.\n\nDeiros · deiros.net")
    chk(pg.evaluate("document.getElementById('waTx').value")==fz2,'Fianza devuelta entera: texto exacto')
    pg.evaluate("_waClose();closeSheet();showBookingById('T_fzr')");pg.wait_for_timeout(300);pg.click('#SC .wa-two button');pg.wait_for_timeout(300)
    st=pg.evaluate("[...document.querySelectorAll('.wa-p button')].map(b=>b.textContent)")
    chk('Fianza devuelta' not in st,f'Fianza retenida entera: no se ofrece «Fianza devuelta» ({st})')
    pg.evaluate("_waClose();closeSheet()")
    # ── 3. Sin teléfono: ningún botón ──
    for bid,n in (('T_none','sin teléfono ni ficha'),('T_short','con un número de 5 cifras')):
        pg.evaluate(f"showBookingById('{bid}')");pg.wait_for_timeout(300)
        chk(pg.evaluate("!document.querySelector('#SC .wa-two')&&!document.querySelector('#SC a[href^=\"tel:\"]')"),f'Ficha del alquiler {n}: ni Llamar ni WhatsApp')
        pg.evaluate("closeSheet()")
    # ── 4. Fila de «Hoy» ──
    pg.evaluate("nav('dashboard')");pg.wait_for_timeout(400)
    R=pg.evaluate(r"""[...document.querySelectorAll('#PC section.hoy .dh-row')].map(r=>({id:(r.getAttribute('onclick').match(/showBookingById\('([^']+)'/)||[])[1],tel:r.querySelector('.wa-ic a')?.getAttribute('href')||'',oc:r.querySelector('.wa-ic a')?.getAttribute('onclick')||'',wa:!!r.querySelector('.wa-ic button'),sz:[...r.querySelectorAll('.wa-ic>*')].map(e=>Math.round(e.getBoundingClientRect().width)+'x'+Math.round(e.getBoundingClientRect().height))}))""")
    R={r['id']:r for r in R}
    chk(R.get('T_hoy',{}).get('tel')=='tel:+584124555123'.replace('4124555123','4125551234') and R['T_hoy']['wa'] and R['T_hoy']['sz']==['44x44','44x44'] and 'stopPropagation' in R['T_hoy']['oc'],f'Hoy con teléfono extranjero: tel:+584125551234 y WhatsApp, redondos de 44 px, sin abrir la fila ({R.get("T_hoy")})')
    chk('T_hoy2' in R and not R['T_hoy2']['tel'] and not R['T_hoy2']['wa'],'Hoy sin teléfono: sin botones')
    pg.click("#PC section.hoy .wa-ic button[onclick*=\"T_hoy'\"]");pg.wait_for_timeout(400)
    st=pg.evaluate("[!!_waEl,AV,document.getElementById('SH').classList.contains('open'),document.querySelector('.wa-p [aria-pressed=true]')?.textContent,document.getElementById('waGo').getAttribute('href').split('?')[0]]")
    chk(st==[True,None,False,'Confirmación','https://wa.me/584125551234'],f'WhatsApp en Hoy: abre la hoja sin abrir el coche ni el alquiler; entrega sin hacer → «Confirmación» ({st})')
    pg.evaluate("_waClose()")
    # ── 5. Ficha del cliente ──
    pg.evaluate("nav('clients');_clientDetail='c1';renderClientDetail(document.getElementById('PC'))");pg.wait_for_timeout(300)
    chk(pg.evaluate("document.querySelector('#PC .wa-two a')?.getAttribute('href')")=='tel:+34600000002','Ficha del cliente: Llamar con tel:+34600000002')
    pg.click('#PC .wa-two button');pg.wait_for_timeout(300)
    st=pg.evaluate("[...document.querySelectorAll('.wa-p button')].map(b=>b.textContent).slice(0,2).concat([document.querySelector('.wa-sh .d-meta').textContent])")
    chk(st[:2]==['Confirmación','Recordatorio'] and 'Renault' in st[2],f'Cliente con alquiler: mensajes del alquiler de referencia ({st})')
    pg.evaluate("_waClose();_clientDetail='c8';renderClientDetail(document.getElementById('PC'));window.__OPEN=[]");pg.wait_for_timeout(200)
    pg.click('#PC .wa-two button');pg.wait_for_timeout(200)
    st=pg.evaluate("[!!_waEl,__OPEN]")
    chk(st==[False,[['https://wa.me/34699887766','_blank','noopener']]],f'Cliente sin alquileres: WhatsApp directo, sin hoja (un toque) ({st})')
    pg.evaluate("_clientDetail='c9';renderClientDetail(document.getElementById('PC'))");pg.wait_for_timeout(200)
    chk(pg.evaluate("!document.querySelector('#PC .wa-two:not(.cl-nw)')&&!document.querySelector('#PC a[href^=\"tel:\"]')"),'Ficha del cliente sin teléfono: ni Llamar ni WhatsApp (solo «Nuevo alquiler» y «Presupuesto»)')
    # ── 5b. Ficha del propietario: Llamar y WhatsApp directo (sin plantillas) ──
    pg.evaluate("openOwnerProfile('o1')");pg.wait_for_timeout(400)
    sz=pg.evaluate("[...document.querySelectorAll('#PC .ow-hc .wa-two>*')].map(e=>[Math.round(e.getBoundingClientRect().height),e.textContent.trim()])")
    tel=pg.evaluate("document.querySelector('#PC .ow-hc .wa-two a')?.getAttribute('href')")
    chk(tel=='tel:+34600000002' and len(sz)==2 and all(h>=44 for h,_ in sz),f'Ficha del propietario: Llamar tel:+34600000002 y WhatsApp, ≥44 px, en su tarjeta ({tel}, {sz})')
    pg.evaluate("window.__OPEN=[]");pg.click('#PC .ow-hc .wa-two button');pg.wait_for_timeout(300)
    st=pg.evaluate("[!!_waEl,!!document.querySelector('.wa-sh'),__OPEN]")
    chk(st==[False,False,[['https://wa.me/34600000002','_blank','noopener']]],f'Propietario: WhatsApp abre el chat directamente, sin hoja ni plantillas ({st})')
    chk(pg.evaluate("document.querySelectorAll('#PC .btn-pri').length")==1,'Ficha del propietario: sigue un solo botón dorado (Informe PDF)')
    pg.evaluate("window.__ph=OW.find(o=>o.id==='o1').phone;OW.find(o=>o.id==='o1').phone='';renderOwnerProfile(document.getElementById('PC'))");pg.wait_for_timeout(200)
    chk(pg.evaluate("!document.querySelector('#PC .wa-two')"),'Propietario sin teléfono: sin botones')
    pg.evaluate("OW.find(o=>o.id==='o1').phone=window.__ph")
    # ── 6. Presupuesto ──
    pg.evaluate("nav('quotes');_quoteEditId='q2';showQuoteDetail(document.getElementById('PC'))");pg.wait_for_timeout(300)
    chk(pg.evaluate("document.querySelector('#PC .wa-two a')?.getAttribute('href')")=='tel:+34600000001','Presupuesto con ficha de cliente (clientId): Llamar tel:+34600000001')
    pg.click('#PC .wa-two button');pg.wait_for_timeout(300)
    qd=pg.evaluate("[QT.find(q=>q.id==='q2').startDate,QT.find(q=>q.id==='q2').endDate,QT.find(q=>q.id==='q2').num]")
    di=lambda s:(datetime.date.fromisoformat(s)-hoy).days
    qt=(f"Hola María, aquí tienes tu presupuesto de Deiros ({qd[2]}):\n\nCoche: Peugeot 208 \"GT\" & Co #1?\nRecogida: {dia(di(qd[0]))} a las 10:00\n"
        f"Devolución: {dia(di(qd[1]))} a las 10:00 (7 días)\nTotal: 175,00{E} (IVA incluido)\nFianza: 200,00{E}, reembolsable.\n\n"
        "Si te encaja, contéstame por aquí y te lo reservo.\n\nDeiros · deiros.net")
    st=pg.evaluate("[[...document.querySelectorAll('.wa-p button')].map(b=>b.textContent+(b.getAttribute('aria-pressed')==='true'?'*':'')),document.getElementById('waTx').value,document.getElementById('waGo').getAttribute('href')]")
    chk(st[0]==['Presupuesto*','En blanco'] and st[1]==qt and st[2]=='https://wa.me/34600000001?text='+encURI(qt),'Presupuesto: «Presupuesto» elegido, texto y enlace exactos'+('' if st[1]==qt else f'\n   {st[1]!r}\n   {qt!r}'))
    chk(pg.evaluate("document.activeElement!==document.getElementById('waTx')") and 'Lugar' not in st[1],'Presupuesto: sin línea de lugar y sin abrir el teclado')
    pg.evaluate("_waClose();_quoteEditId='q1';showQuoteDetail(document.getElementById('PC'))");pg.wait_for_timeout(200)
    chk(pg.evaluate("!document.querySelector('#PC .wa-two')"),'Presupuesto sin ficha de cliente con teléfono: sin botones')
    # ── 7. «Enviar» PDF: idéntico al del botón de siempre; navigator.share con File PDF; y si no se puede, lo de siempre ──
    pm.evaluate("window.__shareOff()");pg.evaluate("window.__shareOff()")
    PDFS=[('Contrato',"openContractForm('v3','b3');_ctGo(4)","generateContractPDF('v3','b3')",'#SC .al-nav button:has-text("Enviar")',r'^Contrato-2222CCC-\d{4}-\d\d-\d\d\.pdf$'),
          ('Presupuesto',"nav('quotes');_quoteEditId='q2';showQuoteDetail(document.getElementById('PC'))","generateQuotePDF('q2')",'#PC .qt-acts button:has-text("Enviar")',r'^Presupuesto-PRE-2026-0041\.pdf$'),
          ('Anexo (ficha del alquiler)',"showBookingById('b3')","generateExtensionPDF('b3')",'#SC button:has-text("Enviar anexo")',r'^Anexo-ampliacion-2222CCC-\d{4}-\d\d-\d\d\.pdf$'),
          ('Anexo (hoja de ampliación)',"openV('v3');openExtendBooking('b3')","generateExtensionPDF(window._extBookingId)",'#SC button:has-text("Enviar anexo")',r'^Anexo-ampliacion-2222CCC-\d{4}-\d\d-\d\d\.pdf$'),
          ('Recibo',"showBookingById('T_fz')","generateReceiptPDF('T_fz')",'#SC button:has-text("Enviar recibo")',r'^Recibo-3333DDD-\d{4}-\d\d-\d\d\.pdf$'),
          ('Liquidación',"openOwnerReport('o1');genOwnerReport('o1')","dlOwnerReport('o1',_RM())",'#ownerRepOv button[aria-label="Enviar PDF"]',r'^Liquidacion-Ana_Propietaria_Ejemplo-\d{4}-\d\d\.pdf$')]
    import re
    LAST="(async()=>{const a=__AC[__AC.length-1];if(!a)return null;const bl=__BL[a.href];return {download:a.download,n:__AC.length,h:bl?await __hash(bl):null,type:bl?bl.type:null};})()"
    for pgx in (pm,pg): pgx.evaluate("window._RM=()=>{const m=document.querySelector('#ownerRepOv [onclick*=dlOwnerReport]')?.getAttribute('onclick').match(/'([0-9]{4}-[0-9]{2})'/);return m?m[1]:todayStr().slice(0,7);}")
    for name,opn,gen,sel,rx in PDFS:
        def prep(x):
            x.evaluate("document.getElementById('ownerRepOv')?.remove();closeSheet();_waClose&&_waClose()" if x is pg else "document.getElementById('ownerRepOv')?.remove();closeSheet()")
            x.evaluate(opn);x.wait_for_timeout(500);x.evaluate("window.__AC=[];window.__SH=[];window.__OPEN=[]")
        # otra pestaña: el botón de siempre
        prep(pm);pm.evaluate(gen);pm.wait_for_timeout(300);M=pm.evaluate(LAST)
        # copia: el botón de siempre (con share disponible: no lo usa)
        prep(pg);pg.evaluate("__shareOn()");pg.evaluate(gen);pg.wait_for_timeout(300);N=pg.evaluate(LAST)
        chk(M and N and M['h']==N['h'] and M['download']==N['download'] and pg.evaluate("__SH.length")==0,f'{name}: el botón de siempre genera el mismo PDF que el botón de siempre, byte a byte, y no usa compartir ({(N or {}).get("download")}, sha {str((N or {}).get("h"))[:12]})')
        # copia: Enviar con navigator.share → un File PDF idéntico
        prep(pg);pg.evaluate("__shareOn();window.__shRes='ok';window.__can=true");pg.click(sel);pg.wait_for_timeout(400)
        S=pg.evaluate("(async()=>{const d=__SH[0];if(!d)return null;const f=d.files&&d.files[0];return {n:__SH.length,keys:Object.keys(d),isFile:f instanceof File,name:f&&f.name,type:f&&f.type,h:f?await __hash(f):null,ac:__AC.length,op:__OPEN.length};})()")
        chk(S and S['n']==1 and S['isFile'] and S['type']=='application/pdf' and re.match(rx,S['name'] or '') and S['h']==M['h'] and S['ac']==0 and S['op']==0,
            f'{name}: «Enviar» llama a navigator.share con un File PDF «{(S or {}).get("name")}», idéntico al del botón de siempre, sin descargar ni abrir nada ({S})')
        # copia: Enviar sin navigator.share → lo de siempre
        prep(pg);pg.evaluate("__shareOff()");pg.click(sel);pg.wait_for_timeout(400);F=pg.evaluate(LAST)
        chk(F and F['h']==M['h'] and F['download']==M['download'],f'{name}: sin navigator.share, «Enviar» hace lo de siempre (descarga «{(F or {}).get("download")}», mismo PDF)')
        # copia: canShare dice que no → lo de siempre
        prep(pg);pg.evaluate("__shareOn();window.__can=false");pg.click(sel);pg.wait_for_timeout(400);F=pg.evaluate(LAST)
        chk(F and F['h']==M['h'] and pg.evaluate("__SH.length")==0,f'{name}: si canShare no admite ficheros, lo de siempre ({F}, {pg.evaluate("__SH.length")})')
        if name in ('Contrato','Recibo','Liquidación'):
            prep(pg);pg.evaluate("__shareOn();window.__can=true;window.__shRes='NotAllowedError'");pg.click(sel);pg.wait_for_timeout(500);F=pg.evaluate(LAST)
            chk(pg.evaluate("__SH.length")==1 and F and F['h']==M['h'] and F['download']==M['download'],f'{name}: si el móvil rechaza compartir (NotAllowedError), lo de siempre')
            prep(pg);pg.evaluate("__shareOn();window.__shRes='AbortError'");pg.click(sel);pg.wait_for_timeout(500)
            chk(pg.evaluate("[__SH.length,__AC.length,__OPEN.length]")==[1,0,0],f'{name}: si Rafael cierra el menú de compartir (AbortError), no pasa nada más')
        pg.evaluate("window.__shRes='ok';window.__can=true")
        # Después de Enviar, el botón normal ya no comparte
        prep(pg);pg.evaluate("__shareOn()");pg.evaluate(gen);pg.wait_for_timeout(300)
        chk(pg.evaluate("__SH.length")==0 and pg.evaluate("__AC.length")==1,f'{name}: después de «Enviar», el botón de siempre vuelve a descargar (no queda «modo enviar» pegado)')
    # Móvil (abre el PDF en otra pestaña): con NotAllowedError, «Enviar» abre el mismo PDF que el botón de siempre
    for x in (pm,pg): x.evaluate("Object.defineProperty(navigator,'userAgent',{get:()=>'Mozilla/5.0 (Linux; Android 14; Pixel) Mobile'})")
    LO="(async()=>{const o=__OPEN[__OPEN.length-1];if(!o)return null;const bl=__BL[o[0]];return bl?await __hash(bl):null;})()"
    for x in (pm,pg): x.evaluate("document.getElementById('ownerRepOv')?.remove();closeSheet();nav('quotes');_quoteEditId='q2';showQuoteDetail(document.getElementById('PC'));window.__OPEN=[];window.__AC=[];window.__SH=[]")
    pm.evaluate("generateQuotePDF('q2')");pm.wait_for_timeout(300);hm=pm.evaluate(LO)
    pg.evaluate("__shareOn();window.__can=true;window.__shRes='NotAllowedError'");pg.click('#PC .qt-acts button:has-text("Enviar")');pg.wait_for_timeout(500);hn=pg.evaluate(LO)
    chk(hm and hm==hn and pg.evaluate("__SH.length")==1,f'Móvil: si compartir falla, abre el mismo PDF que el botón de siempre en otra pestaña (sha {str(hn)[:12]})')
    pg.evaluate("window.__OPEN=[];window.__SH=[];window.__shRes='ok'");pg.click('#PC .qt-acts button:has-text("Enviar")');pg.wait_for_timeout(400)
    chk(pg.evaluate("[__SH.length,__OPEN.length]")==[1,0],'Móvil: con compartir disponible, «Enviar» no abre ninguna pestaña')
    pg.evaluate("window.__OPEN=[];window.__SH=[]");pg.evaluate("generateQuotePDF('q2')");pg.wait_for_timeout(300)
    chk(pg.evaluate(LO)==hm and pg.evaluate("__SH.length")==0,'Móvil: el botón PDF de siempre abre el PDF como hasta ahora')
    pg.evaluate("window.__shRes='ok'")
    # Enviar que no llega a generar (alerta) no deja el modo pegado
    pg.evaluate("__shareOn();window.__SH=[];window.__AC=[];window.__OPEN=[];window.__AL=[];_pdfSend('ax','b1')");pg.wait_for_timeout(400)  # (los PDF ya son asíncronos: el siguiente toque llega después del aviso)
    pg.evaluate("generateQuotePDF('q2')");pg.wait_for_timeout(400)
    chk(pg.evaluate("[__AL.length>0,__SH.length,__AC.length+__OPEN.length,_pdfSendName]")==[True,0,1,None],'Si el PDF no se genera (alerta), el siguiente PDF normal no se comparte')
    # Botones de Enviar: 44 px y sin segundo dorado
    pg.evaluate("closeSheet();openContractForm('v3','b3');_ctGo(4)");pg.wait_for_timeout(400)
    st=pg.evaluate("[...document.querySelectorAll('#SC .al-nav button')].filter(b=>b.offsetParent).map(b=>[b.textContent.trim(),Math.round(b.getBoundingClientRect().height),b.className.includes('btn-pri')])")
    chk([s[0] for s in st]==['‹ Atrás','Enviar','Generar PDF'] and all(s[1]>=44 for s in st) and [s[2] for s in st]==[False,False,True],f'Contrato paso 4: Atrás · Enviar · Generar PDF (dorado), ≥44 px ({st})')
    # «Enviar recibo» en «Más acciones»: 44 px, junto a «Recibo»; nunca solo a media fila
    pg.evaluate("_waClose()")
    for bid,exp in (('T_wa',['Editar','Ampliar','Recibo','Enviar recibo']),('T_cur',['Editar','Ampliar','Contrato','Recibo','Enviar recibo']),('b3',None)):
        pg.evaluate(f"closeSheet();showBookingById('{bid}')");pg.wait_for_timeout(300)
        L=pg.evaluate(r"""(()=>{const g=document.querySelector('#SC .al-two:not(.al-cq)');const W=g.getBoundingClientRect().width;return [...g.children].filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect();return [e.textContent.trim(),Math.round(r.height),Math.round(r.width/W*10)/10];});})()""")
        er=[x for x in L if x[0]=='Enviar recibo']
        half=[x for x in L if x[2]<0.9];rows=len(half)%2==0
        chk(er and er[0][1]>=44 and (exp is None or [x[0] for x in L]==exp) and rows,f'{bid}: «Enviar recibo» en «Más acciones», ≥44 px, sin huecos en la rejilla ({L})')
    pg.evaluate(f"closeSheet();V.forEach(v=>(v.bookings||[]).forEach(b=>{{if(b.id==='T_fz')b.paid=true;}}));showBookingById('T_fz')");pg.wait_for_timeout(300)
    st=pg.evaluate("[document.querySelector('#SC .btn-pri')?.textContent.trim(),[...document.querySelectorAll('#SC .al-two:not(.al-cq)>*')].map(e=>e.textContent.trim())]")
    chk(st[0]=='Recibo' and 'Enviar recibo' in st[1] and 'Recibo' not in st[1],f'Alquiler terminado: «Recibo» dorado arriba y «Enviar recibo» en «Más acciones» ({st})')
    # ── 8. Lugar de entrega y de devolución en el alquiler (b.deliveryPlace / b.returnPlace, autorización de Rafael 18/11/2026) ──
    RARO='Estación "Pinto" & <b>Sur</b> #1? ñ \\ \' `${x}`'
    RET2='Aeropuerto T4 "Barajas" & #2'
    for x in (pm,pg): x.evaluate("try{closeSheet()}catch(e){};try{_waClose()}catch(e){};document.getElementById('ownerRepOv')?.remove();window.__shareOff();window.__AL=[]")
    CO={'ciudad':'Pinto','ciudadEntrega':'Calle Empresa 1, Pinto'}
    for x in (pm,pg): x.evaluate("c=>localStorage.setItem('deiros_company',JSON.stringify(Object.assign(getCompanyData(),c)))",CO)
    newB="(sd)=>{let r=null;V.find(v=>v.id==='v5').bookings.forEach(b=>{if(b.startDate===sd)r=b;});return r?{id:r.id,d:'deliveryPlace' in r?r.deliveryPlace:'(sin campo)',r:'returnPlace' in r?r.returnPlace:'(sin campo)'}:null;}"
    # 8a. Alta: la devolución copia la entrega mientras no se toque
    pg.evaluate("openV('v5');openNewRental()");pg.wait_for_timeout(400)
    L=pg.evaluate("['rDelP','rRetP'].map(i=>{const e=document.getElementById(i),f=e.closest('.d-f');return [f.querySelector('label').textContent,e.type,e.placeholder,Math.round(e.getBoundingClientRect().height),e.closest('[data-rw]').getAttribute('data-rw'),e.getBoundingClientRect().right<=390]})")
    chk([l[0] for l in L]==['Lugar de entrega','Lugar de devolución'] and all(l[1]=='text' and l[3]>=44 and l[4]=='1' and l[5] for l in L),f'Alta, paso 1: «Lugar de entrega» y «Lugar de devolución» (texto, ≥44 px, sin salirse) tras las fechas ({L})')
    pg.fill('#rSD',dd(200));pg.fill('#rED',dd(203));pg.fill('#rAmt','90');pg.fill('#rDelP',RARO)
    chk(pg.evaluate("document.getElementById('rRetP').value")==RARO,'Alta: escribir la entrega rellena la devolución (mismo valor, caracteres raros incluidos)')
    pg.fill('#rRetP',RET2);pg.fill('#rDelP','Otro sitio')
    chk(pg.evaluate("document.getElementById('rRetP').value")==RET2,'Alta: si se toca la devolución, deja de seguir a la entrega')
    pg.fill('#rRetP','');pg.fill('#rDelP',RARO)
    chk(pg.evaluate("document.getElementById('rRetP').value")==RARO,'Alta: si se vacía la devolución, vuelve a seguir a la entrega')
    pg.evaluate("_rwGo(3)");pg.wait_for_timeout(200)
    S=pg.evaluate("[document.getElementById('rwSummary').textContent,[...document.querySelectorAll('#rwSummary b')].some(e=>e.textContent==='Sur'),document.querySelectorAll('#rwSummary .d-kv').length]")
    chk(('Entrega en'+RARO) in S[0] and 'Devolución en' not in S[0] and not S[1],f'Alta, resumen: «Entrega en» con el texto tal cual (escapado: sin etiquetas), sin repetir la devolución igual ({S})')
    pg.evaluate("document.getElementById('rClBirth').value='1985-01-01';submitRental()");pg.wait_for_timeout(300)
    r1=pg.evaluate(newB,dd(200))
    chk(r1 and r1['d']==RARO and r1['r']==RARO,f'Alta: se guardan deliveryPlace y returnPlace (= entrega) en el alquiler ({r1})')
    pg.evaluate("closeSheet();openV('v5');openNewRental()");pg.wait_for_timeout(400)
    pg.fill('#rSD',dd(210));pg.fill('#rED',dd(212));pg.fill('#rAmt','60');pg.fill('#rDelP','Calle Mayor 1');pg.fill('#rRetP',RET2)
    pg.evaluate("_rwGo(3)");pg.wait_for_timeout(200)
    chk(('Devolución en'+RET2) in pg.evaluate("document.getElementById('rwSummary').textContent"),'Alta, resumen: si la devolución es otra, sale «Devolución en»')
    pg.evaluate("document.getElementById('rClBirth').value='1985-01-01';submitRental()");pg.wait_for_timeout(300);r2=pg.evaluate(newB,dd(210))
    chk(r2 and r2['d']=='Calle Mayor 1' and r2['r']==RET2,f'Alta con devolución distinta: se guardan las dos ({r2})')
    pg.evaluate("closeSheet();openV('v5');openNewRental()");pg.wait_for_timeout(400)
    pg.fill('#rSD',dd(220));pg.fill('#rED',dd(221));pg.fill('#rAmt','30');pg.evaluate("document.getElementById('rClBirth').value='1985-01-01';submitRental()");pg.wait_for_timeout(300);r3=pg.evaluate(newB,dd(220))
    chk(r3 and r3['d']=='' and r3['r']=='',f'Alta sin lugares: los dos vacíos ({r3})')
    # 8b. Editar alquiler: carga lo guardado, la devolución sigue a la entrega si eran iguales, y guarda
    pg.evaluate("i=>{closeSheet();openV('v5');editBooking(i)}",r1['id']);pg.wait_for_timeout(400)
    EV=pg.evaluate("['rDelP','rRetP'].map(i=>document.getElementById(i).value).concat([document.getElementById('rRetP').dataset.same,Math.round(document.getElementById('rDelP').getBoundingClientRect().height)])")
    chk(EV==[RARO,RARO,'1',EV[3]] and EV[3]>=44,f'Editar: los dos campos con lo guardado (sin romper el HTML) y la devolución enlazada ({EV})')
    pg.fill('#rDelP','Plaza de la Constitución, Pinto')
    chk(pg.evaluate("document.getElementById('rRetP').value")=='Plaza de la Constitución, Pinto','Editar: cambiar la entrega cambia la devolución que era igual')
    pg.evaluate("i=>submitEditBooking(i)",r1['id']);pg.wait_for_timeout(300);e1=pg.evaluate(newB,dd(200))
    chk(e1['d']=='Plaza de la Constitución, Pinto' and e1['r']=='Plaza de la Constitución, Pinto',f'Editar: se guardan los dos ({e1})')
    pg.evaluate("i=>{closeSheet();openV('v5');editBooking(i)}",r2['id']);pg.wait_for_timeout(400)
    chk(pg.evaluate("document.getElementById('rRetP').dataset.same")=='0','Editar con devolución distinta: no sigue a la entrega')
    pg.fill('#rDelP','Calle Mayor 2');pg.evaluate("i=>submitEditBooking(i)",r2['id']);pg.wait_for_timeout(300);e2=pg.evaluate(newB,dd(210))
    chk(e2['d']=='Calle Mayor 2' and e2['r']==RET2,f'Editar: la devolución distinta se conserva ({e2})')
    # 8c. Alquiler antiguo sin los campos: se abre, se edita y sigue funcionando (vacío)
    old=pg.evaluate("(()=>{const b=V.find(v=>v.id==='v4').bookings.find(b=>b.id==='T_none');return ['deliveryPlace' in b,'returnPlace' in b];})()")
    chk(old==[False,False],'Escenario: T_none es un alquiler antiguo, sin los campos')
    pg.evaluate("closeSheet();openV('v4');editBooking('T_none')");pg.wait_for_timeout(400)
    EV=pg.evaluate("['rDelP','rRetP'].map(i=>document.getElementById(i).value).concat([document.getElementById('rRetP').dataset.same])")
    chk(EV==['','','1'],f'Editar un alquiler antiguo: campos vacíos ({EV})')
    pg.evaluate("window.__AL=[];submitEditBooking('T_none')");pg.wait_for_timeout(300)
    EV=pg.evaluate("(()=>{const b=V.find(v=>v.id==='v4').bookings.find(b=>b.id==='T_none');return [b.deliveryPlace,b.returnPlace,b.clientName,b.startDate<b.endDate,__AL.length];})()")
    chk(EV==['','','Persona Sin Ficha Ninguna',True,0],f'Guardar un alquiler antiguo sin escribir lugar: quedan vacíos y lo demás igual ({EV})')
    pg.evaluate("closeSheet()")
    # 8d. Contrato: Lugar entrega / devolución desde el alquiler; sin lugar, lo de siempre; el PDF tiene el mismo formato
    C3="(()=>[document.getElementById('ctEntLugar').value,document.getElementById('ctDevLugar').value])()"
    pg.evaluate("closeSheet();const b=V.find(v=>v.id==='v3').bookings.find(b=>b.id==='b3');delete b.deliveryPlace;delete b.returnPlace;openContractForm('v3','b3')");pg.wait_for_timeout(400)
    chk(pg.evaluate(C3)==['Calle Empresa 1, Pinto']*2,f'Contrato de un alquiler sin lugar: lo de siempre (lugar de entrega de la empresa) ({pg.evaluate(C3)})')
    pg.evaluate("p=>{closeSheet();const b=V.find(v=>v.id==='v3').bookings.find(b=>b.id==='b3');b.deliveryPlace=p[0];b.returnPlace=p[1];openContractForm('v3','b3')}",[RARO,RET2]);pg.wait_for_timeout(400)
    chk(pg.evaluate(C3)==[RARO,RET2],f'Contrato: Lugar entrega y Lugar devolución desde el alquiler, caracteres raros tal cual ({pg.evaluate(C3)})')
    pg.evaluate("p=>{closeSheet();const b=V.find(v=>v.id==='v3').bookings.find(b=>b.id==='b3');b.returnPlace='';openContractForm('v3','b3')}",[RARO,RET2]);pg.wait_for_timeout(400)
    chk(pg.evaluate(C3)==[RARO,RARO],'Contrato: si el alquiler solo tiene lugar de entrega, la devolución es la misma')
    # PDF: copia (lugares del alquiler) = otra pestaña (mismos lugares escritos a mano) byte a byte
    pg.evaluate("p=>{closeSheet();const b=V.find(v=>v.id==='v3').bookings.find(b=>b.id==='b3');b.returnPlace=p[1];openContractForm('v3','b3');_ctGo(4)}",[RARO,RET2]);pg.wait_for_timeout(400)
    pm.evaluate("p=>{closeSheet();openContractForm('v3','b3');document.getElementById('ctEntLugar').value=p[0];document.getElementById('ctDevLugar').value=p[1];_ctGo(4)}",[RARO,RET2]);pm.wait_for_timeout(400)
    for x in (pm,pg): x.evaluate("window.__OPEN=[];window.__AC=[]");x.evaluate("generateContractPDF('v3','b3')");x.wait_for_timeout(500)
    LA="(async()=>{const o=__OPEN[__OPEN.length-1],a=__AC[__AC.length-1];const u=o?o[0]:(a?a.href:null);const bl=u&&__BL[u];return bl?await __hash(bl):null;})()"
    hm,hn=pm.evaluate(LA),pg.evaluate(LA)
    chk(hm and hm==hn,f'Contrato con lugares del alquiler: el PDF es idéntico, byte a byte, al de otra pestaña con esos lugares escritos a mano en el contrato (mismo texto legal y formato) (sha {str(hn)[:12]})')
    chk(pg.evaluate("getCompanyData().ciudadEntrega")=='Calle Empresa 1, Pinto','Contrato: el lugar del alquiler no se guarda como lugar de entrega por defecto de la empresa')
    pg.evaluate("closeSheet();const b=V.find(v=>v.id==='v3').bookings.find(b=>b.id==='b3');delete b.deliveryPlace;delete b.returnPlace;openContractForm('v3','b3');document.getElementById('ctEntLugar').value='Nuevo punto';_ctGo(4)");pg.wait_for_timeout(300)
    pg.evaluate("generateContractPDF('v3','b3')");pg.wait_for_timeout(400)
    chk(pg.evaluate("getCompanyData().ciudadEntrega")=='Nuevo punto','Contrato de un alquiler sin lugar: «Guardar como predeterminados» guarda el lugar como siempre')
    pg.evaluate("c=>{closeSheet();localStorage.setItem('deiros_company',JSON.stringify(Object.assign(getCompanyData(),c)))}",CO)
    # 8e. WhatsApp: confirmación y recordatorio con el lugar del alquiler
    pg.evaluate("p=>{const v=V.find(v=>v.id==='v4');v.bookings.push({id:'T_pl',startDate:addDays(todayStr(),40),startTime:'10:00',endDate:addDays(todayStr(),42),endTime:'18:30',platform:'sinapp',amount:120,clientName:'Lola',clientPhone:'600 555 666',clientDni:'',finance:[],extras:[],deliveryPlace:p[0],returnPlace:p[1]});_invalidateRsCache&&_invalidateRsCache();showBookingById('T_pl')}",[RARO,RET2]);pg.wait_for_timeout(400)
    pg.click('#SC .wa-two button');pg.wait_for_timeout(300)
    tx,href,foc=pg.evaluate("[document.getElementById('waTx').value,document.getElementById('waGo').getAttribute('href'),document.activeElement===document.getElementById('waTx')]")
    chk(('\nLugar de entrega: '+RARO+'\n') in tx and href=='https://wa.me/34600555666?text='+encURI(tx),'WhatsApp, confirmación: «Lugar de entrega: » con el lugar del alquiler y enlace codificado'+('' if ('Lugar de entrega: '+RARO) in tx else f'\n   {tx!r}'))
    chk(not foc,'WhatsApp con lugar: no se abre el teclado (no hay nada que completar)')
    pg.click('.wa-p button:has-text("Recordatorio")');pg.wait_for_timeout(100)
    tx,href=pg.evaluate("[document.getElementById('waTx').value,document.getElementById('waGo').getAttribute('href')]")
    chk(('\nDónde: '+RET2+'\n') in tx and href=='https://wa.me/34600555666?text='+encURI(tx),'WhatsApp, recordatorio: «Dónde: » con el lugar de devolución')
    q=href.split('?text=')[1];chk(not any(c in q for c in '&?# "\n<>`\\\''),'Enlace: ningún carácter raro del lugar queda sin codificar')
    pg.evaluate("_waClose();closeSheet();const b=V.find(v=>v.id==='v4').bookings.find(b=>b.id==='T_pl');b.returnPlace='';b.deliveryPlace='Calle\\n  Nueva   3';showBookingById('T_pl')");pg.wait_for_timeout(300)
    pg.click('#SC .wa-two button');pg.wait_for_timeout(300);pg.click('.wa-p button:has-text("Recordatorio")');pg.wait_for_timeout(100)
    tx=pg.evaluate("document.getElementById('waTx').value")
    chk('\nDónde: Calle Nueva 3\n' in tx,'WhatsApp: sin lugar de devolución, «Dónde» usa el de entrega; saltos y espacios de más se juntan en una línea')
    pg.evaluate("p=>{_waClose();closeSheet();const b=V.find(v=>v.id==='v4').bookings.find(b=>b.id==='T_pl');b.deliveryPlace=p[0];b.returnPlace=p[1];}",[RARO,RET2])
    # 8f. Normalización
    N=pg.evaluate("(()=>{const a={startDate:'2026-01-01',endDate:'2026-01-02'},b={startDate:'2026-01-01',endDate:'2026-01-02',deliveryPlace:5,returnPlace:{x:1}},c={startDate:'2026-01-01',endDate:'2026-01-02',deliveryPlace:'A & B',returnPlace:''};_normBooking(a);_normBooking(b);_normBooking(c);return [Object.keys(a).includes('deliveryPlace'),Object.keys(a).includes('returnPlace'),b.deliveryPlace,b.returnPlace,c.deliveryPlace,c.returnPlace];})()")
    chk(N==[False,False,'','','A & B',''],f'Normalización: los antiguos no ganan campos; lo que no es texto queda vacío; el texto no se toca ({N})')
    # 8g. Firestore y copia v4: viajan dentro del alquiler
    F=pg.evaluate("(()=>{const f=b=>b&&[b.deliveryPlace,b.returnPlace,'deliveryPlace' in b];const fv=(L)=>{let r={};L.forEach(v=>(v.bookings||[]).forEach(b=>{if(b.id==='T_pl'||b.id==='T_fz')r[b.id]=f(b);}));return r;};return [fv(_cloudPayload(1).vehicles),fv(_backupObject().vehicles),_backupObject().version];})()")
    exp={'T_pl':[RARO,RET2,True],'T_fz':[None,None,False]}
    chk(F[0]==exp and F[1]==exp and F[2]==4,f'Los lugares viajan a Firestore (_cloudPayload) y en la copia v4 (_backupObject) dentro del alquiler; los antiguos siguen sin ellos ({F})')
    IMP="""async (json)=>{window.__AL=[];importData({target:{files:[new File([json],'copia.json',{type:'application/json'})],value:''}});await new Promise(r=>setTimeout(r,1500));
      const g=id=>{let r=null;V.forEach(v=>(v.bookings||[]).forEach(b=>{if(b.id===id)r=b;}));return r;};const t=g('T_pl'),z=g('T_fz');
      return {pl:t&&[t.deliveryPlace,t.returnPlace,'deliveryPlace' in t],fz:z&&['deliveryPlace' in z,'returnPlace' in z],al:window.__AL.slice(),n:V.length};}"""
    full=pg.evaluate("JSON.stringify(_backupObject())")
    pg.evaluate("V.forEach(v=>(v.bookings||[]).forEach(b=>{if(b.id==='T_pl'){b.deliveryPlace='borrado';b.returnPlace='borrado';}}))")
    I=pg.evaluate(IMP,full)
    chk(I['pl']==[RARO,RET2,True] and I['fz']==[False,False] and not any('inválido' in a or 'Error' in a for a in I['al']),f'Importar la copia exportada CON los campos: se recuperan tal cual ({I})')
    no=json.loads(full)
    for v in no['vehicles']:
        for bk in v.get('bookings') or []: bk.pop('deliveryPlace',None);bk.pop('returnPlace',None)
    I=pg.evaluate(IMP,json.dumps(no))
    chk(I['pl']==[None,None,False] and I['fz']==[False,False] and not I['al'],f'Importar una copia SIN los campos (anterior a este cambio): funciona y los alquileres quedan sin ellos ({I})')
    pg.evaluate("closeSheet();showBookingById('T_pl')");pg.wait_for_timeout(300);pg.click('#SC .wa-two button');pg.wait_for_timeout(300)
    chk('\nLugar de entrega: \n' in pg.evaluate("document.getElementById('waTx').value") and pg.evaluate("document.activeElement===document.getElementById('waTx')"),'Tras importar la copia sin campos: la confirmación deja «Lugar de entrega: » vacío con el cursor, como antes')
    pg.evaluate("_waClose();closeSheet();openContractForm('v4','T_pl')");pg.wait_for_timeout(300)
    chk(pg.evaluate(C3)==['Calle Empresa 1, Pinto']*2,'Tras importar la copia sin campos: el contrato usa lo de siempre')
    pg.evaluate("closeSheet()")
    old={'version':3,'vehicles':no['vehicles'],'bizFinances':no['bizFinances']}
    I=pg.evaluate(IMP,json.dumps(old))
    chk(I['pl'] and I['pl'][2] is False and any('Copia antigua' in a for a in I['al']),f'Importar una copia antigua (solo vehículos) sin los campos: funciona ({I["al"]})')
    I=pg.evaluate(IMP,full)
    chk(I['pl']==[RARO,RET2,True],'Volver a importar la copia con los campos los recupera')
    bad=json.loads(full)
    for v in bad['vehicles']:
        for bk in v.get('bookings') or []:
            if bk['id']=='T_pl': bk['deliveryPlace']=5
    msg=pg.evaluate("j=>_validateBackup(JSON.parse(j))",json.dumps(bad))
    chk('lugar de entrega' in msg and 'texto' in msg,f'Una copia con un lugar que no es texto se rechaza con un mensaje claro ({msg})')
    b.close()
run()
H.fin()
