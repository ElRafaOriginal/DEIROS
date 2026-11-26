# Pruebas automáticas de DEIROS Fleet

Estas pruebas abren la app de verdad (`index.html` de este repo) en un Chrome sin pantalla, del tamaño de un móvil
(390 px, modo oscuro), y comprueban que lo importante sigue funcionando. No tocan la base de datos real ni salen a
internet: Firebase está **simulado en memoria**, los datos son **inventados** (ningún cliente real) y la fecha está
**fijada al 20/11/2026 a las 10:00 (Madrid)**, para que los resultados sean siempre los mismos.

## Cuándo ejecutarlas

- **Antes de abrir cada PR** que toque `index.html`: `python3 tests/run_all.py` tiene que terminar en `RESULTADO: TODO OK`.
- **QA** las ejecuta al revisar cada PR (junto con la comprobación del diff contra la especificación). Para un arreglo
  pequeño basta `--rapido` más la prueba del tema tocado (por ejemplo `python3 tests/run_all.py test_cobros`).
- Si un cambio es **intencionado** y cambia un texto o un importe esperado, se actualiza la prueba en la misma PR y se
  explica en la descripción (no se quita una comprobación sin decirlo).

## Instalación (una vez)

```bash
pip install playwright pillow
playwright install chromium
# Linux: utilidades de PDF (pdftotext, pdfinfo, pdfimages) y node (lo usa check_index.py)
sudo apt-get install -y poppler-utils nodejs
```

En Mac: `brew install poppler node`. Python 3.9 o superior.

## Cómo ejecutarlas

```bash
python3 tests/run_all.py            # todas: unos 4 min (3 pruebas a la vez); --serie: una detrás de otra, unos 12 min
python3 tests/run_all.py --rapido   # lo esencial (dinero, copia, edad, PDF y pantallas clave): 1 min aprox.
python3 tests/run_all.py test_cobros test_copia   # solo esas
python3 tests/test_cobros.py        # una sola, viendo cada comprobación
```

`run_all.py` primero pasa `.claude/scripts/check_index.py` (finales de línea CRLF y sintaxis de los `<script>`) y luego
las pruebas. Al final da una tabla con OK y fallos por fichero; la salida completa de cada una queda en
`tests/.resultados/<prueba>.log`. Cada prueba falla también si hay **cualquier error JS** en la página.

Opciones útiles:

- `DEIROS_INDEX=/ruta/a/otro/index.html python3 tests/run_all.py` prueba otra copia (por ejemplo, la de una rama).
- `DEIROS_CAPTURAS=/tmp/capturas` hace que algunas pruebas guarden capturas de pantalla.
- `DEIROS_CHROME=/ruta/a/chrome` usa otro Chrome/Chromium en vez del de Playwright.
- `--jobs N` cambia cuántas pruebas van a la vez.

## Red

La app carga jsPDF, xlsx y las fuentes (Syne, JetBrains Mono, Doto) desde internet. Las pruebas las sirven desde
`tests/.cache/` (no se sube al repo). **La primera vez hace falta red**: `vendor.py` las descarga de la misma URL que usa
`index.html` (cdnjs), de jsDelivr o, si no, con `npm pack` (registro de npm: hace falta `npm`). Después todo funciona sin
red. Se puede preparar a mano con `python3 tests/vendor.py`. Los precios de carburante (`precios.json`) son de prueba.

## Qué cubre

| Fichero | Qué comprueba |
|---|---|
| `test_comision.py` | Comisión del gestor antes y desde 11/2026 (`COMM_RULE_FROM`), gastos 5.2 / 5.3, Franquicia y Daño cliente, mes malo y déficit, suma de meses, sin propietario; PDF de liquidación de octubre y noviembre con importes fijos. |
| `test_dinero_cancelados.py` | Cancelados: «Por cobrar» del coche, Clientes (lista, cuadrícula, ficha), «Top alquileres» y €/día del informe; «En X d» en hora local (00:30 y 12:00 en Madrid); liquidación, comisiones, negocio y Resumen con importes fijos. |
| `test_cifras_cancelados.py` | Cifras sin cancelados: Resumen (mes, año, plataformas con penalización), «Revisión» en Alertas, Flota, avisos de devolución, contrato, propietario, Excel, informe de negocio y días ocupados; también a 1280 px. |
| `test_rentabilidad_plataforma.py` | **Rentabilidad · plataforma** del Resumen: en Mes, Trimestre y Año (y el histórico a 1280 px) la suma de las filas es igual a los ingresos del periodo («INGRESOS MES», «INGRESOS 2026»), con alquileres que cruzan meses, ampliación, extras, cobros de devolución, depósitos (no cuentan), cancelados con penalización, coche en gestión, coche archivado e ingresos sin plataforma («Otros ingresos»). |
| `test_inicio.py` | **Inicio (Resumen)**: orden en el móvil (Resultado flota → Disponibilidad → Alertas → Hoy → En alquiler ahora → Próximos → Año → Evolución → Rentabilidad) y en escritorio; el **ojo** oculta resultado, margen, ingresos y gastos del mes («••••»), lo recuerda al recargar y funciona en tema claro; **Alertas** plegable que recuerda si se deja abierta y se abre sola con una vencida nueva (número en rojo); las cifras son las de siempre (con `DEIROS_BASE=<index anterior>`, idénticas una a una a 390 y 1280 px). |
| `test_fianzas_porcobrar.py` | **Fianzas y Por cobrar del Inicio** (#162): en el móvil, juntas en una fila de 64 px **sin cifras** (ni en el texto ni en el `aria-label`), con «→» y borde y título dorados si hay algo pendiente (neutros si no); al tocarlas abren la **hoja de siempre** (idéntica a `openPendingDeposits` / `openPorCobrar`: filtros y total), «Ver alquiler» → cobrar «Todo» / fianza «Devuelta» → una fila menos; sin desplegable aunque el móvil tenga las claves antiguas de #163; tema claro; escritorio sin cambios (con sus cifras). |
| `test_ampliacion.py` | **Ampliar alquiler** (#153): «+N días» con horas de reloj (mismo criterio que `calcRentalPrice`), Precio/día ⇄ Diferencia (manda la última escrita, también al cambiar fechas), total del alquiler, negativo / texto / fecha anterior / sin coste, Amovens y alquiler sin horas; lo guardado y el anexo, con valores fijos (iguales a escribir el total a mano antes de #153). |
| `test_cobros.py` | Cobros en la ficha (cantidad, «Todo», «Solo alquiler», deshacer con confirmación), «Por cobrar» en Inicio y en el coche, plataformas y cancelados, y el **recibo** en PDF con el mismo estado que la ficha (fianza aparte). |
| `test_devolucion.py` | **Fianza en la devolución** (devolver, retener con motivo, «Más tarde», cargos mayores que la fianza, daños, plataformas, validaciones), «Antes de entregar» (cobro, fianza, carnet, edad), km a 0,19 €/km y combustible = litros × (precio del municipio + 2 €/L). |
| `test_entrega_extra.py` | **Extra de entrega**: un solo «Entrega» con importe libre (50 € por defecto, decimales) en alta, edición, presupuesto, contrato y recibo; alquileres y presupuestos antiguos (49 € / 59 €, en `datos/`) siguen igual. |
| `test_edad.py` | **Edad mínima 26 años cumplidos**: reglas, contrato (formulario fijo y PDF), presupuesto, alta (con 25 no se guarda), ficha del cliente. |
| `test_fotos_actas.py` | **Fotos y actas** de entrega/devolución: guardado **fuera de data/main**, compresión, **cola sin conexión** que se sube sola, daños, Comparar, **borrado** con el alquiler, limpieza a 6 meses con «Conservar», error de reglas de Firebase. |
| `test_actas_pdf.py` | Actas en PDF con 0, 3 y 8 fotos (textos, páginas, < 1 MB), Generar y Enviar acta, acta sin red, avisos al confirmar, borrar alquiler o coche avisa de cuántas fotos (nube lenta y sin red). |
| `test_galeria.py` | **Galería** de 8 fotos por coche: huecos, cámara/galería, visor, Enviar fotos con sello, portada en Flota, migración de la foto antigua, cola sin red, borrar coche, nube que no responde, reglas. |
| `test_copia_fotos.py` | **Copia con fotos**: incluye galería y actas, importar en otro móvil sin duplicar, sobre una galería existente, copia con fotos antigua, sin red. |
| `test_copia.py` | **Copia v4**: exportar (claves de siempre), importar (vuelta completa idéntica y subida a la nube), **copias antiguas** (sin settings, clientId, lugares, depósito, version; «solo vehículos y finanzas») y ficheros no válidos. |
| `test_resenas.py` | **Reseñas en settings**: Ajustes, limpieza del enlace, sincronización entre «móviles» (Firestore compartido, conflicto, migración desde localStorage), copia v4 con y sin settings, WhatsApp «Gracias + reseña». |
| `test_enviar.py` | **WhatsApp y Enviar**: teléfonos, mensajes exactos y enlaces wa.me, botones en ficha, Hoy, cliente, propietario y presupuesto; «Enviar» de cada PDF con el menú de compartir (idéntico al PDF de siempre); lugar de entrega y devolución. |
| `test_teclado.py` | **Teclado en las hojas**: el campo y el pie quedan a la vista (Android, iOS y redimensionado), hojas apiladas, arrastrar para cerrar, sin listeners acumulados. |
| `test_pdfs.py` | **Todos los PDF** se generan sin errores y con su contenido (analítica, recibos, anexo, contratos, mantenimientos, negocio, liquidación, informe del coche, presupuestos, actas) e **informe de mantenimientos** con gastos sin datos del taller (#144). |
| `test_pantallas.py` | **Barrido de todas las pantallas**, hojas y avisos (67): sin errores JS y nada que se salga a 390 px. |

Ficheros de apoyo: `harness.py` (arnés: Firebase falso con subcolecciones, `where`, `FieldPath`, `documentId`, modo lento
y sin red; datos ficticios; fecha fija; red simulada; fotos sintéticas), `galeria_comun.py` (utilidades de la galería),
`vendor.py` (caché de librerías), `datos/entrega121_antiguos.json` (alquileres y presupuestos guardados con la app de antes
de #121, inventados) y `run_all.py`.

## De dónde salen

Son las pruebas que se hicieron para cada PR (#90, #94, #96, #100, #105, #108, #121, #123, #126, #137, #138, #139, #144, #153, #162…),
reunidas aquí sin depender de copias en `/tmp` ni de versiones antiguas de `main`: donde comparaban «igual que main», ahora
comprueban valores fijos escritos en la prueba (o se han quitado si solo tenían sentido comparando; cada fichero lo dice en
su cabecera).
