import re,sys,subprocess,tempfile,os
p=sys.argv[1]; raw=open(p,'rb').read()
lf=raw.count(b'\n'); crlf=raw.count(b'\r\n')
print(f"Líneas: {lf} · CRLF: {crlf} · LF sueltos: {lf-crlf}")
html=raw.decode('utf-8')
blocks=re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>',html,re.S)
ok=True
for i,b in enumerate(blocks):
    with tempfile.NamedTemporaryFile('w',suffix='.js',delete=False) as f: f.write(b); n=f.name
    r=subprocess.run(['node','--check',n],capture_output=True,text=True); os.unlink(n)
    if r.returncode: ok=False; print(f"Bloque <script> {i}: ERROR\n{r.stderr[:800]}")
print(f"{len(blocks)} bloques <script> revisados:", "OK" if ok else "CON ERRORES")
sys.exit(0 if ok and lf==crlf else 1)
