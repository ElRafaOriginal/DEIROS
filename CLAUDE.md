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
- Combustible faltante: **precio medio de mercado en el municipio donde se devuelve el coche + 2 €/litro**. Los litros se calculan con la capacidad del depósito del coche y la diferencia entre el nivel de entrega y el de devolución.
- Km extra contratados al reservar: 0,15 €/km. Km excedidos a la devolución: **0,19 €/km para todos los vehículos** (también furgonetas).
- Edad mínima del conductor: **mayor de 25 años** (a partir de 26; con 25 cumplidos no se alquila). No es configurable. Fianza por defecto: **200 €** (contrato y presupuesto).

## Autorizaciones expresas de Rafael (15/11/2026)

- Campo nuevo en cada vehículo: **capacidad del depósito en litros** (en `V`, con su normalización y su sitio en la copia de seguridad v4 sin romper copias antiguas).
- Un workflow **nuevo** en `.github/workflows/` que descarga cada día los precios oficiales de carburantes del Ministerio (datos abiertos) y publica las medias por municipio para la app. El workflow existente `claude.yml` sigue sin tocarse.
- Campo nuevo en cada presupuesto: **`clientId`** (`QT[].clientId`, texto: id de la ficha de cliente elegida en el buscador; vacío si no se eligió ficha). Viaja en Firestore y en la copia v4 dentro de `quotes`; los presupuestos y copias antiguas sin él siguen funcionando (por nombre). Es el único campo nuevo de la «ficha única de cliente»: **no** se autorizan `licenseIssued` ni `extraDriverId`.

## Marca

Paleta: fondos `#0D0D0D #141414 #1C1C1C`, morado `#6A0DAD #8B1FD4`, dorado `#FFD700 #D4A800`, texto `#FFFFFF #AAAAAA`.
Tipografías: Syne y JetBrains Mono. Botones táctiles de al menos 44 px de alto.

## Equipo de desarrollo

Mismo equipo que Rafael tenía en Grok Bot. El coordinador es **Deiros Fleet** (comando `/fleet`, en `.claude/commands/fleet.md`), que reparte el trabajo entre cuatro agentes (en `.claude/agents/`):

1. **auditor** — fallos: revisa la app o investiga un fallo, encuentra la causa raíz y especifica la corrección exacta.
2. **producto** — mejoras: estudia la ergonomía, la apariencia y las funcionalidades, propone mejoras priorizadas y especifica las que Rafael aprueba.
3. **desarrollador** — aplica la especificación en una rama `claude/…` con el diff mínimo y abre la PR.
4. **qa** — revisa el diff contra la especificación y estas reglas, ejecuta la comprobación y aprueba o devuelve cambios.

Flujo: auditor (fallos) o producto (mejoras) → Rafael elige/aprueba (siempre en las mejoras y si el riesgo es alto) → desarrollador → qa → PR lista para que Rafael la fusione.
Las PR y las issues se escriben en español; la descripción de la PR termina en `Closes #N` cuando haya issue.

También sigue funcionando el flujo antiguo: una issue o comentario de Rafael con `@claude` lanza la GitHub Action (`.github/workflows/claude.yml`).

## Ahorro de recursos (decidido por Rafael, 15/11/2026)

- **Modelo según la tarea:** auditor y producto usan Opus (razonar, diseñar, especificar); desarrollador y qa usan Sonnet (aplicar especificaciones exactas y comprobar). Las dudas que QA marque como «DUDA PARA OPUS» las revisa el coordinador.
- **Capturas mínimas:** 2–3 pantallas o páginas clave por PR, en un solo modo (oscuro por defecto); ambos modos solo si el cambio depende del tema.
- **Repasos cortos:** tras un arreglo pequeño, QA revisa solo ese commit, no la PR entera.
- **Sin paralelismo innecesario:** un agente a la vez salvo que Rafael tenga prisa o las tareas sean independientes y cortas.
- **Lotes:** agrupar cambios pequeños relacionados en una sola especificación y una sola PR.
- **Reutilizar:** continuar el mismo agente (con su contexto) en vez de lanzar uno nuevo para seguir la misma tarea; reutilizar pruebas y scripts ya hechos.
- **Arreglos triviales** (una o dos líneas que QA ya ha especificado exactamente): los aplica el coordinador directamente, con check_index y las pruebas, sin un ciclo completo.

## Convivencia con Grok Bot

Rafael también trabaja en este repo con su equipo de Grok Bot (Deiros Fleet, Auditor, Producto, Desarrollador, QA). No compartís conversaciones: **GitHub es el único sitio común**, así que todo lo importante debe quedar escrito en issues y PR.

Antes de empezar cualquier trabajo:

1. Actualiza `main` (`git fetch --depth=50 origin main`) y parte siempre de la última versión.
2. Revisa las PR y las issues abiertas: `gh api 'repos/ElRafaOriginal/DEIROS/pulls?state=open'` y `gh api 'repos/ElRafaOriginal/DEIROS/issues?state=open'`. Lee su título, descripción y comentarios recientes.
3. Si una PR abierta (de Grok, de Claude o de Rafael) ya toca la misma función o zona de `index.html`, **no trabajes en paralelo sobre ella**: díselo a Rafael y propón esperar a que se fusione, o continuar sobre esa misma rama si él lo autoriza.
4. Si una issue abierta ya describe lo que se va a hacer, trabaja sobre ella (enlázala y termina la PR con `Closes #N`) en vez de duplicarla.
5. Respeta las decisiones que Rafael haya dejado escritas en issues y PR, vengan de quien vengan, salvo que contradigan estas reglas; en ese caso pregúntale.
