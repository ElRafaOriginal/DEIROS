# Librerías y fuentes que index.html carga desde internet (CDN) y que las pruebas sirven desde una copia local
# en tests/.cache/ (no se sube al repo). La primera vez se descargan; después las pruebas no necesitan red.
#   python3 tests/vendor.py          → prepara la caché y dice qué hay
# Orden de búsqueda de cada fichero: caché → la misma URL del CDN que usa index.html → jsDelivr → `npm pack` (registro de npm).
import os,sys,shutil,subprocess,tarfile,tempfile,urllib.request

CACHE=os.path.join(os.path.dirname(os.path.abspath(__file__)),'.cache')
LIBS={  # nombre en caché: (URL de index.html, paquete npm, fichero dentro del paquete)
 'jspdf.umd.min.js':('https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js','jspdf@2.5.1','dist/jspdf.umd.min.js'),
 'xlsx.full.min.js':('https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js','xlsx@0.18.5','dist/xlsx.full.min.js'),
}
FONTS={  # fuentes de la app (Google Fonts) desde los paquetes @fontsource, mismas familias y pesos
 'syne-400.woff2':('@fontsource/syne@5.3.0','files/syne-latin-400-normal.woff2'),
 'syne-500.woff2':('@fontsource/syne@5.3.0','files/syne-latin-500-normal.woff2'),
 'syne-600.woff2':('@fontsource/syne@5.3.0','files/syne-latin-600-normal.woff2'),
 'syne-700.woff2':('@fontsource/syne@5.3.0','files/syne-latin-700-normal.woff2'),
 'syne-800.woff2':('@fontsource/syne@5.3.0','files/syne-latin-800-normal.woff2'),
 'jbm-400.woff2':('@fontsource/jetbrains-mono@5.3.0','files/jetbrains-mono-latin-400-normal.woff2'),
 'jbm-500.woff2':('@fontsource/jetbrains-mono@5.3.0','files/jetbrains-mono-latin-500-normal.woff2'),
 'jbm-600.woff2':('@fontsource/jetbrains-mono@5.3.0','files/jetbrains-mono-latin-600-normal.woff2'),
 'doto-900.woff2':('@fontsource/doto@5.3.0','files/doto-latin-900-normal.woff2'),
}
def path(name):return os.path.join(CACHE,name)
def have(name):p=path(name);return os.path.isfile(p) and os.path.getsize(p)>0
def _get(url):
    try:
        with urllib.request.urlopen(url,timeout=30) as r:
            data=r.read()
        return data if data else None
    except Exception:
        return None
_PACKS={}
def _npm(pkg):
    if pkg in _PACKS:return _PACKS[pkg]
    out=None
    if shutil.which('npm'):
        tmp=tempfile.mkdtemp(prefix='deiros_npm_')
        r=subprocess.run(['npm','pack',pkg,'--silent','--pack-destination',tmp],capture_output=True,text=True,timeout=180)
        tgz=[f for f in os.listdir(tmp) if f.endswith('.tgz')]
        if r.returncode==0 and tgz:out=os.path.join(tmp,tgz[0])
    _PACKS[pkg]=out;return out
def _from_npm(pkg,inner):
    tgz=_npm(pkg)
    if not tgz:return None
    with tarfile.open(tgz) as t:
        try:return t.extractfile('package/'+inner).read()
        except KeyError:return None
def _store(name,data):
    os.makedirs(CACHE,exist_ok=True)
    with open(path(name),'wb') as f:f.write(data)
def ensure(verbose=True):
    """Prepara la caché. Devuelve la lista de ficheros que faltan."""
    falta=[]
    for name,(cdn,pkg,inner) in LIBS.items():
        if have(name):continue
        data=_get(cdn) or _get('https://cdn.jsdelivr.net/npm/%s/%s'%(pkg,inner)) or _from_npm(pkg,inner)
        if data:_store(name,data)
        else:falta.append(name)
    for name,(pkg,inner) in FONTS.items():
        if have(name):continue
        data=_get('https://cdn.jsdelivr.net/npm/%s/%s'%(pkg,inner)) or _from_npm(pkg,inner)
        if data:_store(name,data)
        else:falta.append(name)
    if verbose:
        if falta:print('AVISO · no se han podido descargar: '+', '.join(falta)+' (hace falta red la primera vez: ver tests/README.md)')
        else:print('Caché de librerías y fuentes lista en tests/.cache/')
    return falta
if __name__=='__main__':
    sys.exit(1 if ensure() else 0)
