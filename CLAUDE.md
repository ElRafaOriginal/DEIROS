# DEIROS Fleet — instrucciones para Claude

App interna de gestión de flota de Deiros (alquiler flexible de vehículos en Pinto, Madrid).
PWA de una sola página: todo el código está en `index.html` (HTML + CSS + JS, ~12.000 líneas),
con Firebase (Auth + Firestore, compat 10.7.1) como backend y publicada con GitHub Pages desde `main`.
Rafael la usa sobre todo **en el móvil y en modo oscuro**.

## Reglas obligatorias (no negociables)

1. **Nunca hagas push a `main` ni fusiones PRs.** Trabaja siempre en una rama `claude/<tema>` y abre una PR contra `main`. Rafael revisa y fusiona.
2. **`index.html` usa finales de línea CRLF.** Consérvalos. Antes de cada commit ejecuta
   `python3 .claude/scripts/check_index.py index.html` (comprueba CRLF y sintaxis de los `<script>`); si falla, no hagas commit.
3. **No cambies el formato de los datos guardados**: ni la estructura de Firestore, ni la copia de seguridad v4 (`_backupObject`),
   ni añadas campos nuevos en `V`, `b`, `b.finance` o `v.finances` sin que Rafael lo autorice expresamente en la issue.
4. **No toques `.github/`**, `firebaseConfig`, ni el texto legal de los contratos (`generateMgmtContractPDF`, cláusula Quinta) salvo orden expresa.
5. **Sin secretos en el código.** Nada de claves, tokens ni datos de clientes reales.
6. **Cambios mínimos.** Nada de refactorizar, renombrar o cambiar estilos fuera del alcance pedido. Una PR = un tema.
7. **Edita con la herramienta Edit**, no con scripts que reescriban el fichero entero.

## Reglas de negocio (confirmadas por Rafael)

- Precios con IVA incluido.
- Comisión del gestor: siempre sobre lo **facturado en el mes** × % de comisión del vehículo, aunque el coche dé pérdidas; si no factura, comisión 0. Al propietario le queda `beneficio − comisión`.
- Combustible faltante: precio de mercado + 1 €/litro. Km extra contratados al reservar: 0,15 €/km; km excedidos a la devolución: 0,19 €/km. Edad mínima del conductor: 25 años.

## Marca

Paleta: fondos `#0D0D0D #141414 #1C1C1C`, morado `#6A0DAD #8B1FD4`, dorado `#FFD700 #D4A800`, texto `#FFFFFF #AAAAAA`.
Tipografías: Syne y JetBrains Mono. Botones táctiles de al menos 44 px de alto.

## Equipo de desarrollo

Para mejorar la app se trabaja con tres agentes (en `.claude/agents/`), coordinados por la sesión principal:

1. **producto** — revisa la app, encuentra fallos y mejoras, localiza la causa raíz con líneas y funciones concretas y redacta la especificación (lo que antes hacía Grok Bot en las issues).
2. **desarrollador** — aplica la especificación en una rama `claude/…` con el diff mínimo y abre la PR.
3. **revisor** — revisa el diff contra la especificación y contra estas reglas, ejecuta la comprobación y aprueba o devuelve cambios.

Flujo: producto → (Rafael aprueba si el cambio es grande o toca dinero/contratos) → desarrollador → revisor → PR lista para que Rafael la fusione.
Las PR y las issues se escriben en español; la descripción de la PR termina en `Closes #N` cuando haya issue.

También sigue funcionando el flujo antiguo: una issue o comentario de Rafael con `@claude` lanza la GitHub Action (`.github/workflows/claude.yml`).
