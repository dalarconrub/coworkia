# Project Memory Snapshot

_Auto-generado por `python agents/orchestrator_agent.py sync-chat-memory` @ 2026-04-18T17:26:13Z. No editar a mano._

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
- **[2026-04-18]** `Claude` — el pipeline canonico es apertura = init_chat + memory_check; cierre = sync-chat-memory + memory_check. INICIAR_COWORKIA.bat encadena apertura -> GUI. sync-chat-memory NO corre al abrir.
  - origen: `chats/chat_2026-04-18.md` (msg #19)
- **[2026-04-18]** `Claude` — las memorias locales del harness (Codex ~/.codex/memories/, Claude profile memory, etc.) son capa de recall, no fuente de verdad. Orden de autoridad ante conflicto: AGENTS/CLAUDE/copilot-instructions -> memory/*.md -> chat del dia -> devlog. Purgar /memories locales si se detectan recuerdos obsoletos.
  - origen: `chats/chat_2026-04-18.md` (msg #22)
- **[2026-04-18]** `Claude` — en NOTION_DS_NOTAS la ruta Obsidian vive en la propiedad 'Ruta Obsidian' (rich_text), no en 'Tarea'. 'Tarea' queda libre para su semantica original (relacion a tarea PTN, pendiente Mejora 2 del caso 07). Migracion idempotente en tools/migrate_notas_ruta_obsidian.py.
  - origen: `chats/chat_2026-04-18.md` (msg #31)
- **[2026-04-18]** `Codex/ABGD` — el validador del caso 07 detecta por si mismo si PTN-Notas sigue con schema viejo y no migrado, y le dice a David que ejecute el migrate. No hay falso negativo posible. Lo mismo el promote: falla rapido con mensaje claro en vez de dejar que la API de Notion devuelva un error opaco.
  - origen: `chats/chat_2026-04-18.md` (msg #34)
- **[2026-04-18]** `Codex/ABGD` — el cruce doble `obsidian:<ruta>` <-> `ptn:<id>` en INX requiere que la fila PTN-Notas recien creada pase por `log_ptn_changes.py` antes de `sync_inx_links --source notion`. Sin ese log intermedio, `--source notion` no ve la fila. El bat del caso 07 ya lo encadena; `orchestrator inx-sync` tambien (cadena completa).
  - origen: `chats/chat_2026-04-18.md` (msg #35)
- **[2026-04-18]** `Codex/ABGD` — flag --sync en promote_obsidian_to_ptn.py equivale al pipeline completo del caso 07 en un comando. Propiedades relation Proyecto PTN / Tarea PTN son la forma canonica de enlazar PTN-Notas con proyectos/tareas; 'Proyecto' y 'Tarea' rich_text quedan como legacy tras migrate_notas_ptn_relations.py y pueden limpiarse cuando se quiera. El promote detecta dinamicamente cual usar, asi que funciona antes y despues de la migracion.
  - origen: `chats/chat_2026-04-18.md` (msg #37)
- **[2026-04-18]** `Codex/ABGD` — el flujo canonico de promocion Obsidian->PTN-Notas post-2026-04-18 es un solo comando: `apps\promote_obsidian_to_ptn.bat "<nota>" [--proyecto "<ref>"] [--tarea "<ref>"] --sync`. No hace falta ejecutar el .bat de validacion salvo para auditoria posterior. Cleanup de legacy es opcional y puede correrse tras migrate_notas_ptn_relations.
  - origen: `chats/chat_2026-04-18.md` (msg #39)
- **[2026-04-18]** `Codex/ABGD` — KIT ya es ciudadano de primera en INX. Clave canonica kit:<page_id>. No hay log intermedio (a diferencia de PTN/Obsidian): _sync_kit lee directo de NOTION_DB_KIT. Cruce Obsidian<->KIT sigue sin logica automatica; queda como Gap 1 del caso 08 para el futuro alcance C.
  - origen: `chats/chat_2026-04-18.md` (msg #43)
- **[2026-04-18]** `Codex/ABGD` — el flujo BIB->ficha Obsidian es `promote_bib_to_obsidian.py <citekey> --sync`. Crea .md bajo A1-INV/B13-PUB/<contexto> con frontmatter citekey/bib-id/doi, y cierra cruce INX obsidian:<ruta> + paperpile:<citekey> en un comando. Dedup por nombre (no sobreescribe salvo --force).
  - origen: `chats/chat_2026-04-18.md` (msg #45)
- **[2026-04-18]** `Codex/ABGD` — captura obsidian->todoist via marker inline `<!-- todoist:<id> -->` es idempotente y visible en el .md original. Re-ejecutar el promote sobre la misma nota no duplica tareas. Para batch o close-on-check ver Gaps 1-2.
  - origen: `chats/chat_2026-04-18.md` (msg #47)
- **[2026-04-18]** `Codex/ABGD` — timeline.py reconoce el journal diario del vault por convencion N<YYMMDD>-*.md bajo A0-GTD/B0C-PLA/C0C9-Notas/. Es el primer consumidor del vault desde el lado operativo (chat/devlog) y requiere OBSIDIAN_ALPHA_PATH cargado. Sin la variable, la seccion del timeline queda "Sin journal" pero no falla.
  - origen: `chats/chat_2026-04-18.md` (msg #49)
- **[2026-04-18]** `Codex/ABGD` — backfill_obsidian_to_inx.py complementa a log_obsidian_changes.py. log_obsidian es diff por mtime para cambios continuos; backfill es full-scan idempotente para historico o tras corrupcion de obsidian_log_state.json. Juntos garantizan cobertura completa.
  - origen: `chats/chat_2026-04-18.md` (msg #51)
- **[2026-04-18]** `Codex/ABGD` — sintaxis cross-system `[[<prefix>:<id>]]` con prefix en {ptn, kit, paperpile, todoist, github}. UUIDs de ptn y kit se normalizan (ignora guiones). Auditable con `tools/obsidian_wikilinks.py audit`. Busqueda inversa con `find <prefix>:<id>`. INX-ENLACES es el resolver; requiere sync reciente para que la auditoria sea fiable.
  - origen: `chats/chat_2026-04-18.md` (msg #53)
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
- **[2026-04-18]** `Claude` — @David al terminar el trabajo del dia, cierra con apps\cerrar_sesion.bat para dejar memory/SNAPSHOT.md al dia.
  - origen: `chats/chat_2026-04-18.md` (msg #19)
- **[2026-04-18]** `Claude` — @Codex valida desde tu lado (1) que no hay ningun path de configuracion Codex que me este perdiendo, (2) que la regla de precedencia es operable (puedes purgar /memories cuando detectes conflicto), y (3) si compras la redaccion propuesta o prefieres otra.
  - origen: `chats/chat_2026-04-18.md` (msg #20)
- **[2026-04-18]** `Claude` — @David si quieres, cerramos sesion con apps\cerrar_sesion.bat para dejar memory/SNAPSHOT.md al dia.
  - origen: `chats/chat_2026-04-18.md` (msg #22)
- **[2026-04-18]** `Claude/ABGD` — @Codex/ABGD redactar tools/validate_case_07.py analogo a tools/validate_case_03.py. Spec:
  - origen: `chats/chat_2026-04-18.md` (msg #28)
- **[2026-04-18]** `Claude` — @David decide (a) migrar ahora antes del validador, (b) no migrar pero exigir a @Codex/ABGD parametrizar el nombre de la propiedad, o (c) aceptar la deuda y que @Codex/ABGD siga con la spec original.
  - origen: `chats/chat_2026-04-18.md` (msg #29)
- **[2026-04-18]** `Claude` — @Codex/ABGD retoma la implementacion de validate_case_07.py con la spec original pero leyendo 'Ruta Obsidian' en lugar de 'Tarea'. Eliminada la deuda tecnica. El reto abierto sobre sobrecarga queda resuelto por la migracion.
  - origen: `chats/chat_2026-04-18.md` (msg #31)
- **[2026-04-18]** `Claude/ABGD` — @David ejecutar `python tools/migrate_notas_ruta_obsidian.py --dry-run` y reportar el scan. Una vez aplicada, @Codex/ABGD tiene via libre para validate_case_07.py + el ajuste defensivo del promote (opcion c).
  - origen: `chats/chat_2026-04-18.md` (msg #32)
- **[2026-04-18]** `Codex/ABGD` — @David cuando corras `python tools/migrate_notas_ruta_obsidian.py --dry-run` y luego sin flag, promociona una nota de prueba con `python tools/promote_obsidian_to_ptn.py "<nota>" [--proyecto "<x>"]` y lanza `apps\validate_case_07.bat --no-pause`. El informe deberia mostrar promociones > 0, match OBSIDIAN_DB y match INX obsidian:* al 100%. El match ptn:* probablemente quede incompleto (Gap 3) hasta que cablemos el sync ptn:<id> automatico.
  - origen: `chats/chat_2026-04-18.md` (msg #34)
- **[2026-04-18]** `Codex/ABGD` — @David Gap 1 y Gap 4 abiertos como backlog. Si quieres cerrar Mejora 3 (sync inline en promote_obsidian_to_ptn.py) delega handoff; evita los 4 pasos del bat a costa de acoplar el promote con sync_inx_links.
  - origen: `chats/chat_2026-04-18.md` (msg #35)
- **[2026-04-18]** `Codex/ABGD` — @David caso 07 cerrado. Proximos candidatos logicos: caso 08 (anclar notas a KIT) o caso 10 (tareas MAR nacidas dentro de notas). Dime cual activamos.
  - origen: `chats/chat_2026-04-18.md` (msg #37)
- **[2026-04-18]** `Codex/ABGD` — @David caso 07 definitivamente cerrado. Los siguientes casos del plan son: 08 (KIT), 09 (BIB->Obsidian), 10 (MAR desde nota), 11 (journal diario), 12 (backfill INX historico), 13 (busqueda cross-system). Dime cual activamos o si queremos cerrar sesion con apps\cerrar_sesion.bat.
  - origen: `chats/chat_2026-04-18.md` (msg #39)
- **[2026-04-18]** `Codex/ABGD` — @David caso 08 cerrado en alcance B. Candidatos que siguen: 09 (BIB->Obsidian), 10 (MAR desde notas), 11 (journal), 12 (backfill INX historico), 13 (busqueda cross-system), o subir a alcance C del caso 08 (Usada en relation + cruce automatico). Dime.
  - origen: `chats/chat_2026-04-18.md` (msg #43)
- **[2026-04-18]** `Codex/ABGD` — @David si quieres validar end-to-end el caso 09, carga BIB con `python agents/bib_agent.py importar`. Proximos casos: 10 (tareas MAR desde notas), 11 (journal diario), 12 (backfill INX historico), 13 (busqueda cross-system).
  - origen: `chats/chat_2026-04-18.md` (msg #45)
- **[2026-04-18]** `Codex/ABGD` — @David casos candidatos restantes: 11 (journal diario cruzado con timeline), 12 (backfill INX historico), 13 (busqueda cross-system). Dime cual sigue o si paramos aqui para cerrar sesion.
  - origen: `chats/chat_2026-04-18.md` (msg #47)
- **[2026-04-18]** `Codex/ABGD` — @David quedan casos 12 (backfill INX historico) y 13 (busqueda cross-system). Tambien podemos cerrar sesion aqui con apps\cerrar_sesion.bat.
  - origen: `chats/chat_2026-04-18.md` (msg #49)
- **[2026-04-18]** `Codex/ABGD` — @David solo queda caso 13 (busqueda cross-system) o cierre con apps\cerrar_sesion.bat.
  - origen: `chats/chat_2026-04-18.md` (msg #51)
- **[2026-04-18]** `Codex/ABGD` — @David casos 07-13 todos implementados. Notas de prueba locales (2) en A0-GTD/B0C-PLA/C0C9-Notas/ del vault por si quieres borrarlas. Cerramos sesion con apps\cerrar_sesion.bat para regenerar SNAPSHOT.md?
  - origen: `chats/chat_2026-04-18.md` (msg #53)
- **[archive_2026-04-17]** `Codex` — @Copilot puede usar este protocolo como base de coordinación por defecto en futuras sesiones multiagente.
  - origen: `chats/chat_archive_2026-04-17.md` (msg #28)
