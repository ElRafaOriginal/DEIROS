# Teclado del móvil en las hojas (#108): al enfocar un campo y abrirse el teclado (tres emulaciones: A «resizes-visual» de
# Android, B «resizes-content» y C como iOS con la vista desplazada), el campo y el pie de la hoja quedan a la vista en
# WhatsApp, alta de alquiler, gasto del alquiler, gasto del coche y devolución; hojas apiladas; arrastrar para cerrar (con y
# sin teclado; aviso de descartar cambios) y sin listeners acumulados.
# Origen: specs/teclado/test_t108.py. Quitado «main reproduce el fallo»; «arrastre igual que main» → comportamiento fijo.
# Uso: python3 tests/test_teclado.py
import sys,os,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import harness as H
from playwright.sync_api import sync_playwright
NEW=H.INDEX;SHOTS=H.CAPTURAS
D=H.datos();FAKE=H.FAKE;route=H.route
VVFAKE=r"""window.__L={vv:0,fi:0};
(function(){const A=EventTarget.prototype.addEventListener;EventTarget.prototype.addEventListener=function(ty,f,op){
 if(ty==='focusin'&&this===document)window.__L.fi++;if((ty==='resize'||ty==='scroll')&&this===window.__vvT)window.__L.vv++;return A.call(this,ty,f,op);};})();
(function(){
 if(!window.__FAKEVV)return;
 const t=new EventTarget();window.__vvT=t;let h=null,ot=0;
 const o={get width(){return innerWidth},get height(){return h==null?innerHeight:h},get offsetTop(){return ot},offsetLeft:0,pageTop:0,pageLeft:0,scale:1,
  addEventListener:t.addEventListener.bind(t),removeEventListener:t.removeEventListener.bind(t),dispatchEvent:t.dispatchEvent.bind(t)};
 Object.defineProperty(window,'visualViewport',{configurable:true,get:()=>o});
 window.__kb=function(x,y){h=x;ot=y||0;o.dispatchEvent(new Event('resize'));if(y)o.dispatchEvent(new Event('scroll'));};
})();
"""
ERR=H.ERRS
def ok(n,c,i=''):H.chk(c,n,i)
CASES=[ # nombre, js para abrir, selector del campo (None = el último campo visible de la hoja)
 ('WhatsApp (textarea, sobre la ficha)',"nav('rentals');showBookingById('b3');setTimeout(()=>_waPick('b','b3'),400)",'#waTx'),
 ('Alta de alquiler (último campo, paso 1)',"openV('v3');openNewRental()",None),
 ('Gasto del alquiler (último campo)',"openV('v3');openBookingFinance('b3','expense')",None),
 ('Gasto del vehículo (último campo)',"openV('v3');openAddEntry()",None),
 ('Devolución (último campo)',"openV('v3');openReturnModal('b3')",None),
]
LAST="""()=>{const s=document.querySelector('.wa-sh.open')||document.getElementById('SH');
 const L=[...s.querySelectorAll('input:not([type=hidden]):not([type=checkbox]):not([type=radio]):not([type=file]):not([disabled]),textarea,select')].filter(e=>e.offsetParent&&e.getBoundingClientRect().height>0);
 const e=L[L.length-1];e.setAttribute('data-t108','1');return e.id||e.name||e.tagName;}"""
GEO="""()=>{const a=document.activeElement,sh=a&&a.closest&&a.closest('.sheet');const r=a.getBoundingClientRect(),s=sh.getBoundingClientRect();
 return {tag:a.tagName,id:a.id,top:Math.round(r.top),bottom:Math.round(r.bottom),shTop:Math.round(s.top),shBottom:Math.round(s.bottom),vvH:Math.round(visualViewport.height),vvT:Math.round(visualViewport.offsetTop),kb:getComputedStyle(document.documentElement).getPropertyValue('--kb')}}"""
def ctx_page(b,html,fake):
    ctx=H.new_context(b,has_touch=True,is_mobile=True)
    ctx.add_init_script("window.__FAKEVV=%s;window.__DATA=%s;localStorage.setItem('wg_theme','dark');localStorage.setItem('deiros_lastBackupAt',new Date().toISOString());window.alert=()=>{};window.__CF=[];window.confirm=m=>{window.__CF.push(m);return window.__CFR!==false};"%('true' if fake else 'false',json.dumps(D)))
    ctx.add_init_script(FAKE);ctx.add_init_script(VVFAKE)
    pg=ctx.new_page();tag=('nuevo' if html==NEW else 'main')
    pg.on('pageerror',lambda e:ERR.append(tag+': '+str(e)))
    pg.goto('file://'+os.path.abspath(html));pg.wait_for_timeout(2000);return ctx,pg
def run_case(pg,mode,name,js,sel):
    pg.evaluate("try{_waClose()}catch(e){};try{closeSheet()}catch(e){};document.activeElement&&document.activeElement.blur&&document.activeElement.blur()")
    pg.set_viewport_size({'width':390,'height':844})
    if mode in('A','C'):pg.evaluate("__kb(null)")
    pg.wait_for_timeout(400);pg.evaluate(js);pg.wait_for_timeout(900)
    if sel is None:pg.evaluate(LAST);sel='[data-t108]'
    pg.locator(sel).first.click();pg.wait_for_timeout(150)          # foco (toque) con el teclado aún cerrado
    if mode=='A':pg.evaluate("__kb(480)")                                # teclado: visualViewport 844 -> 480
    elif mode=='C':pg.evaluate("__kb(480,200)")                          # como iOS: visualViewport 480 px desplazado 200 px hacia abajo
    else:pg.set_viewport_size({'width':390,'height':480})             # teclado con resizes-content
    pg.wait_for_timeout(500);gm=pg.evaluate(GEO)
    pg.evaluate("document.querySelectorAll('[data-t108]').forEach(e=>e.removeAttribute('data-t108'))")
    vis=gm['top']>=gm['vvT'] and gm['bottom']<=gm['vvT']+gm['vvH'] and gm['shBottom']<=gm['vvT']+gm['vvH']+1
    return vis,gm
def drag(pg,dy):
    return pg.evaluate("""dy=>{const sh=document.getElementById('SH'),h=sh.querySelector('.sh');const r=h.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+2;
     const T=yy=>new Touch({identifier:1,target:h,clientX:x,clientY:yy});
     h.dispatchEvent(new TouchEvent('touchstart',{touches:[T(y)],changedTouches:[T(y)],bubbles:true}));
     h.dispatchEvent(new TouchEvent('touchmove',{touches:[T(y+dy)],changedTouches:[T(y+dy)],bubbles:true}));
     const mid=sh.style.transform;
     h.dispatchEvent(new TouchEvent('touchend',{touches:[],changedTouches:[T(y+dy)],bubbles:true}));
     return {mid,open:sh.classList.contains('open'),tr:sh.style.transform,cf:window.__CF.length};}""",dy)
with sync_playwright() as p:
    b=H.launch(p)
    res={}
    for html in (NEW,):
        tag='nuevo' if html==NEW else 'main'
        for mode in ('A','B','C'):
            ctx,pg=ctx_page(b,html,mode in('A','C'))
            for name,js,sel in CASES:
                vis,gm=run_case(pg,mode,name,js,sel);res[(tag,mode,name)]=(vis,gm)
                if SHOTS and mode=='A' and name.startswith(('WhatsApp','Alta')):
                    os.makedirs(SHOTS,exist_ok=True);pg.screenshot(path=f"{SHOTS}/{tag}-{'wa' if name.startswith('Wh') else 'alta'}.png")
                if name.startswith('WhatsApp'):
                    res[(tag,mode,'apiladas')]=pg.evaluate("(()=>{const r=document.getElementById('SH').getBoundingClientRect();const o=document.getElementById('SH').classList.contains('open');_waClose();return {fichaAbierta:o&&document.getElementById('SH').classList.contains('open'),waFuera:!document.querySelector('.wa-sh'),shBottom:Math.round(r.bottom)}})()")
            if mode=='A':
                # arrastre para cerrar y aviso de descartar, sin teclado y con teclado abierto
                out=[]
                for kbh in (None,480):
                    pg.evaluate("try{closeSheet()}catch(e){};__kb(null)");pg.wait_for_timeout(300)
                    pg.evaluate("openV('v3');openBookingFinance('b3','expense')");pg.wait_for_timeout(600)
                    if kbh:pg.locator('#bfConcept').click();pg.evaluate("__kb(480)");pg.wait_for_timeout(300)
                    s1=drag(pg,40);pg.wait_for_timeout(350)                      # corto: vuelve
                    pg.locator('#bfConcept').fill('Limpieza');pg.wait_for_timeout(100)
                    pg.evaluate("window.__CFR=false");s2=drag(pg,200);pg.wait_for_timeout(350) # largo con cambios, «Cancelar» en el aviso: sigue abierta
                    pg.evaluate("window.__CFR=true");s3=drag(pg,200);pg.wait_for_timeout(350)  # largo, «Aceptar»: se cierra
                    out.append((s1,s2,s3))
                res[(tag,'drag')]=out
                # listeners: abrir/cerrar 12 hojas no añade ninguno
                l0=pg.evaluate("JSON.stringify(window.__L)")
                for i in range(6):pg.evaluate("openV('v3');openReturnModal('b3');closeSheet();showBookingById('b3');_waPick('b','b3');_waClose();closeSheet()")
                res[(tag,'listeners')]=(l0,pg.evaluate("JSON.stringify(window.__L)"))
            ctx.close()
    b.close()

for name,_,_ in CASES:
    for mode in ('A','B','C'):
        ok(f'[{mode}] nuevo: campo visible · {name}',res[('nuevo',mode,name)][0],res[('nuevo',mode,name)][1])
for mode in ('A','B','C'):ok(f'[{mode}] hojas apiladas: cerrar WhatsApp deja la ficha abierta',res[('nuevo',mode,'apiladas')]['fichaAbierta'] and res[('nuevo',mode,'apiladas')]['waFuera'],res[('nuevo',mode,'apiladas')])
dn=res[('nuevo','drag')]
ok('arrastre sin teclado: corto vuelve, largo con cambios pregunta, Cancelar mantiene, Aceptar cierra',dn[0][0]['open'] and dn[0][0]['tr']=='' and dn[0][1]['open'] and dn[0][1]['cf']>=1 and not dn[0][2]['open'],dn[0])
ok('arrastre con teclado: corto vuelve, largo pregunta, Cancelar mantiene, Aceptar cierra',dn[1][0]['open'] and dn[1][0]['tr']=='' and dn[1][1]['open'] and not dn[1][2]['open'],dn[1])
l0,l1=res[('nuevo','listeners')];ok('sin listeners acumulados (visualViewport/focusin)',l0==l1,(l0,l1))
H.fin()
