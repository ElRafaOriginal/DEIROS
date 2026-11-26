#!/usr/bin/env python3
# Ejecuta TODAS las pruebas de DEIROS Fleet contra el index.html del repo y da un resumen por fichero.
#   python3 tests/run_all.py              → todas (unos 6–8 min con 3 a la vez)
#   python3 tests/run_all.py --rapido     → lo esencial (unos 1–2 min)
#   python3 tests/run_all.py test_cobros test_copia   → solo esas
#   opciones: --jobs N (pruebas a la vez; por defecto 3), --serie (una detrás de otra)
# Antes de las pruebas pasa la comprobación de siempre (.claude/scripts/check_index.py: CRLF y sintaxis de los <script>).
# La salida completa de cada prueba queda en tests/.resultados/<prueba>.log. Sale con 0 si todo está OK.
import os,sys,re,time,subprocess,concurrent.futures as cf
T=os.path.dirname(os.path.abspath(__file__));REPO=os.path.dirname(T)
sys.path.insert(0,T)
import vendor
INDEX=os.path.abspath(os.environ.get('DEIROS_INDEX') or os.path.join(REPO,'index.html'))
# (fichero, argumentos, ¿en --rapido?) — de más lenta a más rápida, para repartir mejor
TODAS=[('test_galeria.py',[],False),('test_fotos_actas.py',[],False),('test_pantallas.py',[],False),('test_enviar.py',[],False),
       ('test_actas_pdf.py',[],False),('test_copia_fotos.py',[],False),('test_resenas.py',[],False),('test_entrega_extra.py',[],False),
       ('test_teclado.py',[],False),('test_cobros.py',[],True),('test_devolucion.py',[],True),('test_copia.py',[],True),
       ('test_pdfs.py',[],True),('test_cifras_cancelados.py',[],True),('test_dinero_cancelados.py',[],True),('test_edad.py',[],True),
       ('test_comision.py',[],True),('test_ampliacion.py',[],True),('test_rentabilidad_plataforma.py',[],True),('test_inicio.py',[],False),
       ('test_fianzas_porcobrar.py',[],False),('test_analitica_cifras.py',[],True),('test_analitica_pantalla.py',[],False),('test_presupuestos_estado.py',[],True),('test_presupuesto_convertir.py',[],True)]
RAPIDO=[(f,a,r) for f,a,r in TODAS if r]+[('test_pantallas.py',['--rapido'],True)]
def args():
    a=sys.argv[1:];o={'rapido':'--rapido' in a,'jobs':3,'solo':[]}
    if '--serie' in a:o['jobs']=1
    if '--jobs' in a:o['jobs']=max(1,int(a[a.index('--jobs')+1]))
    o['solo']=[x if x.endswith('.py') else x+'.py' for x in a if x.startswith('test_')]
    return o
def check_index():
    ck=os.path.join(REPO,'.claude','scripts','check_index.py')
    if not os.path.isfile(ck):return None,'(no está .claude/scripts/check_index.py)'
    r=subprocess.run([sys.executable,ck,INDEX],capture_output=True,text=True)
    return r.returncode==0,(r.stdout+r.stderr).strip()
def run(f,extra):
    os.makedirs(os.path.join(T,'.resultados'),exist_ok=True)
    log=os.path.join(T,'.resultados',f[:-3]+('-rapido' if extra else '')+'.log')
    t0=time.time()
    try:
        r=subprocess.run([sys.executable,'-u',os.path.join(T,f)]+extra,capture_output=True,text=True,timeout=480,env=dict(os.environ,DEIROS_INDEX=INDEX),cwd=REPO)
        out=r.stdout+('\n'+r.stderr if r.stderr.strip() else '');code=r.returncode
    except subprocess.TimeoutExpired as e:
        out=(e.stdout or b'').decode('utf-8','replace') if isinstance(e.stdout,bytes) else (e.stdout or '');out+='\nTIEMPO AGOTADO (8 min)';code=-1
    open(log,'w',encoding='utf-8').write(out)
    m=re.search(r'RESUMEN: (\d+) OK, (\d+) fallos',out)
    nok,nbad=(int(m.group(1)),int(m.group(2))) if m else (0,0)
    fallos=[l for l in out.splitlines() if l.startswith('FALLO')]
    if not m:fallos.append('La prueba no terminó (ver %s): %s'%(os.path.relpath(log,REPO),(out.strip().splitlines() or ['sin salida'])[-1][:200]))
    return {'f':f+(' '+' '.join(extra) if extra else ''),'ok':nok,'bad':nbad if m else max(1,nbad),'t':time.time()-t0,'code':code,'fallos':fallos,'log':log}
def main():
    o=args();t0=time.time()
    print('DEIROS Fleet · pruebas contra %s'%os.path.relpath(INDEX,os.getcwd()))
    falta=vendor.ensure(verbose=False)
    if falta:print('AVISO · falta en tests/.cache: %s (ver tests/README.md, «Red»)'%', '.join(falta))
    ok,txt=check_index()
    print('\n── Comprobación de index.html (CRLF y sintaxis) ──\n'+txt)
    lista=RAPIDO if o['rapido'] else TODAS
    if o['solo']:lista=[x for x in TODAS+RAPIDO if x[0] in o['solo']][:len(o['solo'])]
    print('\n── %d pruebas%s, %d a la vez ──'%(len(lista),' (rápidas)' if o['rapido'] else '',o['jobs']),flush=True)
    res=[]
    with cf.ThreadPoolExecutor(max_workers=o['jobs']) as ex:
        fut={ex.submit(run,f,a):f for f,a,_ in lista}
        for x in cf.as_completed(fut):
            r=x.result();res.append(r)
            print('%-5s %-34s %4d OK %3d fallos  %5.0f s'%('OK' if r['bad']==0 and r['code']==0 else 'FALLO',r['f'],r['ok'],r['bad'],r['t']),flush=True)
    orden=[f+(' '+' '.join(a) if a else '') for f,a,_ in lista];res.sort(key=lambda r:orden.index(r['f']))
    tot_ok=sum(r['ok'] for r in res);tot_bad=sum(r['bad'] for r in res)
    print('\n════════ RESUMEN ════════')
    print('%-36s %6s %7s %7s'%('Fichero','OK','Fallos','Tiempo'))
    print('%-36s %6s %7s %7s'%('check_index.py (CRLF y sintaxis)','sí' if ok else ('—' if ok is None else 'NO'),'0' if ok!=False else '1',''))
    for r in res:print('%-36s %6d %7d %6.0fs'%(r['f'],r['ok'],r['bad'],r['t']))
    print('%-36s %6d %7d %6.0fs'%('TOTAL',tot_ok,tot_bad+(1 if ok is False else 0),time.time()-t0))
    malos=[r for r in res if r['bad'] or r['code']!=0]
    if malos or ok is False:
        print('\nFALLOS:')
        if ok is False:print('  check_index.py: '+txt.splitlines()[-1])
        for r in malos:
            for l in r['fallos'][:15]:print('  %s: %s'%(r['f'],l[:300]))
            print('  (salida completa: %s)'%os.path.relpath(r['log'],REPO))
        print('\nRESULTADO: CON FALLOS');sys.exit(1)
    print('\nRESULTADO: TODO OK (%d comprobaciones, sin errores JS)'%tot_ok);sys.exit(0)
if __name__=='__main__':main()
