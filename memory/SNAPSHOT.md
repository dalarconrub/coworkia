# Project Memory Snapshot

_Auto-generado por `python agents/orchestrator_agent.py sync-chat-memory` @ 2026-04-18T10:56:01Z. No editar a mano._

Agregado de marcadores `MEMORIA:`, `BLOQUEO:` y `SIGUIENTE:` de todos los chats en `chats/`.
Cada entrada enlaza al chat donde aparecio por ultima vez (dedup por contenido normalizado).

## MEMORIA (acuerdos duraderos)

- **[2026-04-18]** `Claude` — todo agente lee devlog al arrancar (python tools/devlog.py view --limit 20) y añade entrada en el mismo turno en que cierra decisión, marca MEMORIA operativa, completa feature, abre/cierra BLOQUEO o hace REVERT.
  - origen: `chats/chat_2026-04-18.md` (msg #3)
- **[2026-04-18]** `Claude` — el punto de entrada canonico para cualquier agente es memory/INDEX.md. Si memory/*.md desalinean con el repo real, los agentes corrigen en el mismo turno y dejan entrada [DOCS] en el devlog.
  - origen: `chats/chat_2026-04-18.md` (msg #5)
- **[2026-04-18]** `Claude` — memory/SNAPSHOT.md es auto-generado, no editar a mano. Se regenera con python agents/orchestrator_agent.py sync-chat-memory. Para garantia de salud se corre python tools/memory_check.py.
  - origen: `chats/chat_2026-04-18.md` (msg #7)
- **[2026-04-18]** `Claude` — granularidad por capa = chat diario, devlog monolitico + archivo mensual, memory curada monolitica, sprint por fichero, INX por run con timestamp. timeline.py es la vista temporal unificada; regenerable y read-only.
  - origen: `chats/chat_2026-04-18.md` (msg #9)
- **[2026-04-18]** `Claude` — la revision de docs tras cada cambio estructural es responsabilidad del agente que haya completado el cambio; debe dejar entrada [DOCS] en el devlog en el mismo turno.
  - origen: `chats/chat_2026-04-18.md` (msg #11)
- **[2026-04-18]** `Claude` — tool-kit/ es la version portable del sistema comunicacion+devlog+memoria. Para instalar: copiar tool-kit/* a proyecto destino, rellenar TODOs en memory/*.md y CLAUDE.md/AGENTS.md, ajustar VALID_AREAS en tools/devlog.py.
  - origen: `chats/chat_2026-04-18.md` (msg #13)
- **[2026-04-18]** `Claude` — tool-kit ya cubre las cuatro capas: chat multiagente + devlog feature-level + memoria curada + sprints Scrum. Integraciones cableadas por convencion (campo Sprint: en devlog, scan de artifacts/sprints en timeline), no por acoplamiento de codigo.
  - origen: `chats/chat_2026-04-18.md` (msg #15)
- **[2026-04-18]** `Claude` — notacion canonica de subagente es Root/Sub (Root in Claude/Copilot/Codex; Sub en [A-Za-z0-9_-]). Identidad de primera clase en chat, chat_memory, devlog y roster. memory/ROSTER.md es el directorio vigente de subagentes activos, curado a mano.
  - origen: `chats/chat_2026-04-18.md` (msg #16)
- **[archive_2026-04-17]** `Codex` — los marcadores canónicos del hilo son `MEMORIA:`, `BLOQUEO:` y `SIGUIENTE:`.
  - origen: `chats/chat_archive_2026-04-17.md` (msg #28)
- **[archive_2026-04-17]** `Codex` — la causa de los acentos rotos en chat.md es el uso de Windows PowerShell 5.1 sobre un archivo UTF-8 sin indicar codificación explícita. Regla fija del sistema: cualquier lectura/escritura manual de chat.md en PowerShell debe usar -Encoding utf8.
  - origen: `chats/chat_archive_2026-04-17.md` (msg #30)

## BLOQUEO (impedimentos)

- Ninguno.

## SIGUIENTE (handoffs pendientes)

- **[2026-04-18]** `Claude` — @Copilot y @Codex al reactivarse, incorporar la lectura del devlog al arranque y usar el helper en todas las escrituras.
  - origen: `chats/chat_2026-04-18.md` (msg #3)
- **[2026-04-18]** `Claude` — @Copilot @Codex al reactivarse, incorporar la carga de memory/ al arranque y usar tools/snapshot_structure.py cuando cambien carpetas top-level.
  - origen: `chats/chat_2026-04-18.md` (msg #5)
- **[2026-04-18]** `Claude` — @Copilot considera cablear memory_check en pre-commit o en CI. @Codex si cambia el parser de markers, regenera SNAPSHOT.md y valida dedup.
  - origen: `chats/chat_2026-04-18.md` (msg #7)
- **[2026-04-18]** `Claude` — @Copilot o @Codex, considerad automatizar la regeneracion diaria del timeline de hoy (cron / hook / cierre de sesion).
  - origen: `chats/chat_2026-04-18.md` (msg #9)
- **[2026-04-18]** `Claude` — @David si cambias un agent guide o los casos-de-uso, avisame y los incluyo en el proximo paso.
  - origen: `chats/chat_2026-04-18.md` (msg #11)
- **[2026-04-18]** `Claude` — @David prueba el kit copiandolo a un proyecto destino para smoke-test virgen real; si detecta algun path hard-coded al proyecto origen, lo arreglo aqui y tambien en Coworkia.
  - origen: `chats/chat_2026-04-18.md` (msg #13)
- **[2026-04-18]** `Claude` — @David si lo pruebas en un proyecto destino, avisa si el stub _build_task_commands() resulta poco claro; podemos reemplazarlo por un registry externo (YAML/TOML) si la curva de personalizacion se vuelve friccionante.
  - origen: `chats/chat_2026-04-18.md` (msg #15)
- **[2026-04-18]** `Claude` — @David cuando actives un subagente concreto, lo anoto en memory/ROSTER.md con su foco y chat de activacion, y dejo entrada [DOCS].
  - origen: `chats/chat_2026-04-18.md` (msg #16)
- **[2026-04-18]** `Claude` — @David decide si (a) extendemos INICIAR_COWORKIA.bat con el pipeline correcto sync -> init -> check, o (b) primero acordamos con @Codex mover sync-chat-memory a hook de cierre y dejar el arranque solo con init_chat + memory_check.
  - origen: `chats/chat_2026-04-18.md` (msg #17)
- **[archive_2026-04-17]** `Codex` — @Copilot puede usar este protocolo como base de coordinación por defecto en futuras sesiones multiagente.
  - origen: `chats/chat_archive_2026-04-17.md` (msg #28)
