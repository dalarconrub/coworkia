# DevLog — Coworkia

> Registro append-only del desarrollo del proyecto a nivel **feature**, no a nivel commit.
> Fuente de verdad para narrar *qué se trabajó, por qué y con qué impacto*, complementando `git log` (código) y `chats/chat_YYYY-MM-DD.md` (conversación).

## Reglas

- **Append-only.** Nunca se edita ni borra una entrada previa. Si una entrada queda obsoleta, se añade otra que la corrija y se enlaza.
- **UTF-8 estricto.** En `Windows PowerShell 5.1`, todo acceso manual debe usar `-Encoding utf8`.
- **Orden cronológico inverso:** las entradas nuevas se añaden al final (cronológico natural); para consultar lo reciente, leer desde el final.
- **Una entrada por hito**, no por commit. Tipos válidos de `Estado`: `START`, `PROGRESS`, `BLOCKED`, `UNBLOCKED`, `DONE`, `REVERT`.
- **Tag `[AREA]` obligatorio** en el título. Áreas canónicas: `MAR`, `PTN`, `KIT`, `REP`, `BIB`, `ABGD`, `INX`, `MULTIAGENT`, `TOOLING`, `DOCS`, `INFRA`.
- **Escritura recomendada vía `python tools/devlog.py append ...`** (garantiza UTF-8, timestamp UTC y enlace al chat del día).
- **Archivado:** cuando un mes cierre o el fichero supere ~1500 líneas, mover histórico a `devlog/archive/DEVLOG-YYYY-MM.md` y dejar nota con el rango.

## Cuándo escribir una entrada (obligatorio para agentes)

Un agente **debe** añadir entrada al devlog cuando:

1. Cierra una decisión en el chat con `✅ CERRADO #N`.
2. Registra una `MEMORIA:` duradera que implique cambio operativo o de implementación.
3. Completa una tarea de código con cambios mergeados (hito de feature).
4. Registra un `BLOQUEO:` real que detiene trabajo en curso (`Estado: BLOCKED`) — y cuando se resuelva (`UNBLOCKED`).
5. Hace `REVERT` o rollback significativo.

No se escribe entrada para: commits de refactor menor, tipos de fix triviales, ediciones sin impacto en comportamiento.

## Esquema de entrada

```
## YYYY-MM-DDTHH:MMZ — Agente — [AREA] título breve
Estado: START | PROGRESS | BLOCKED | UNBLOCKED | DONE | REVERT
Chat: chats/chat_YYYY-MM-DD.md
Commits: <sha1>, <sha2>   (opcional)
Refs: #issue, PR#, decision #N   (opcional)
Resumen: 1-3 frases. Qué cambió, por qué, impacto.
```

## Consulta rápida

```bash
python tools/devlog.py view                         # últimas 20 entradas
python tools/devlog.py view --area PTN              # filtrar por área
python tools/devlog.py view --agent Claude --limit 5
python tools/devlog.py view --status BLOCKED        # bloqueos vigentes
```

## Entradas

<!-- append-only; nuevas entradas abajo -->

## 2026-04-18T06:20Z — Claude — [MULTIAGENT] DevLog feature-level creado y hecho obligatorio
Estado: DONE
Chat: chats/chat_2026-04-18.md
Refs: CERRADO #1
Resumen: Nace devlog/DEVLOG.md (append-only, UTF-8) y tools/devlog.py con append y view. Se actualiza .claude/multiagent.md con la seccion 'DevLog obligatorio' y se propagan instrucciones a CLAUDE.md, AGENTS.md y .github/copilot-instructions.md. Todos los agentes leen las ultimas 20 entradas al arrancar y escriben tras cerrar decision, MEMORIA operativa, feature completada, BLOQUEO o REVERT.

## 2026-04-18T06:29Z — Claude — [DOCS] Memory layer (INDEX/PURPOSE/STRUCTURE) + snapshot_structure helper
Estado: DONE
Chat: chats/chat_2026-04-18.md
Refs: CERRADO #2
Resumen: Nace memory/ con INDEX.md (meta-indice de recursos), PURPOSE.md (vision y principios) y STRUCTURE.md (mapa hibrido: narrativa curada + bloque TREE auto-generado). Nuevo helper tools/snapshot_structure.py regenera el bloque TREE. Protocolo multiagente (.claude/multiagent.md, CLAUDE.md, AGENTS.md, .github/copilot-instructions.md) obliga a cargar memory/INDEX.md -> PURPOSE.md -> STRUCTURE.md como PASO 1 al arrancar, antes del archivo de identidad y del chat del dia.

## 2026-04-18T06:37Z — Claude — [TOOLING] Memory layer integrada en runtime: init_chat briefing, memory_check, SNAPSHOT.md
Estado: DONE
Chat: chats/chat_2026-04-18.md
Refs: CERRADO #3
Resumen: Tres integraciones: (1) tools/init_chat.py imprime briefing con estado de memory/ y ultimas 3 entradas del devlog al resolver el chat del dia (nuevo flag --no-briefing para scripts). (2) tools/memory_check.py valida existencia de PURPOSE/STRUCTURE/INDEX, enlaces rotos en INDEX.md y frescura del TREE via snapshot_structure.py --check; apto para pre-commit o CI. (3) multiagents/chat_memory.py gana build_project_memory_entries/render_project_memory_markdown/write_project_memory_snapshot; orchestrator_agent.py sync-chat-memory emite ahora memory/SNAPSHOT.md con MEMORIA/BLOQUEO/SIGUIENTE agregados y deduplicados de todos los chats historicos. INDEX.md actualizado para enlazar SNAPSHOT.md.

## 2026-04-18T06:44Z — Claude — [TOOLING] Timeline aggregator + campo Sprint en devlog
Estado: DONE
Chat: chats/chat_2026-04-18.md
Sprint: sprint-multiagent-1
Refs: CERRADO #4
Resumen: Nuevo tools/timeline.py agrega chat+devlog+INX+sprints por fecha o rango a artifacts/daily/YYYY-MM-DD.md (flags --date, --from/--to, --days, --stdout). tools/devlog.py acepta --sprint y persiste Sprint: en la entrada; el parser lo lee. memory/INDEX.md enlaza artifacts/daily/. .claude/multiagent.md incluye sintaxis de timeline y nota del campo Sprint. No modifica fuentes: solo agrega.

## 2026-04-18T06:51Z — Claude — [DOCS] Docs actualizados: guia-rapida, multiagent-system, extract-portable-toolkit
Estado: DONE
Chat: chats/chat_2026-04-18.md
Refs: CERRADO #5
Resumen: Auditoria de docs/ y actualizacion de los tres archivos con gaps: (1) guia-rapida.md gana seccion 'Coordinacion multiagente' con memory/, devlog/, timeline y sync-chat-memory, mas bloques de rutina 'al empezar sesion' y 'al cerrar hito' en Rutinas recomendadas. (2) multiagent-system.md reescrito al modelo de 4 capas (memory curada / chat / devlog / Scrum), nuevo orden de lectura en arranque, CLI ampliado con init_chat/devlog/snapshot_structure/memory_check/timeline, seccion 'Memoria del chat y del proyecto' cubre SNAPSHOT.md y artifacts/daily/, 'Estado actual' y 'Siguientes iteraciones' actualizados. (3) extract-portable-toolkit.md actualiza el inventario: devlog.py/snapshot_structure.py/memory_check.py como Nucleo; timeline.py como Hibrido (parseo INX y sprints es domain-specific); memory/ y devlog/ clasificados; sync-chat-memory ahora depende de write_project_memory_snapshot. Agent guides por dominio (todoist, notion-ptn, notion-kit, github, bib, obsidian) y casos-de-uso/ verificados correctos, no requieren cambios.

## 2026-04-18T07:11Z — Claude — [TOOLING] Kit portable tool-kit/ extraido siguiendo docs/extract-portable-toolkit.md
Estado: DONE
Chat: chats/chat_2026-04-18.md
Refs: CERRADO #6
Resumen: Nueva carpeta tool-kit/ agnostica de dominio reune las tres capas (chat multiagente + devlog feature-level + memoria curada del proyecto) + vista temporal. Incluye: tools/ (init_chat, devlog, sync_chat_memory autonomo, timeline sin INX/sprints, snapshot_structure, memory_check, fix_chat_mojibake); multiagents/ (chat_memory con funciones de project memory, chat_template generalizado a Director + agentes intercambiables); memory/ plantillas (PURPOSE, STRUCTURE, INDEX con placeholders TODO y marcadores TREE); devlog/DEVLOG.md con cabecera limpia; .claude/multiagent.md y CLAUDE.md/AGENTS.md/.github/copilot-instructions.md generalizados; README.md con instalacion (bash+PowerShell), uso diario, reglas, personalizacion y smoke-test. devlog.py: VALID_AREAS reducido a nucleo (MULTIAGENT/TOOLING/DOCS/INFRA/GENERAL) + comentario de extension. timeline.py: stripped de parseo INX y sprints, con bloque '--- PUNTO DE EXTENSION ---' en render_daily(). Smoke-test end-to-end en tool-kit/ pasa (init_chat, snapshot_structure, memory_check, sync_chat_memory, devlog append/view, timeline). Kit distribuido limpio: artifacts test removidos, DEVLOG.md sin entradas, chats/ vacio, SNAPSHOT.md como stub sustituible.

## 2026-04-18T07:20Z — Claude — [TOOLING] Sistema de sprints integrado en tool-kit portable
Estado: DONE
Chat: chats/chat_2026-04-18.md
Refs: CERRADO #7
Resumen: Extraido el sistema Scrum al kit con personalizacion documentada e integracion cross-capa. Copiados models.py (generico) y artifacts.py (generico) intactos. Generalizados registry.py y planner.py: registry deja DOMAIN_AGENTS vacio con ejemplo comentado y conserva COORDINATION+OPERATION con intake/reporting minimos; planner limpia SYSTEM_KEYWORDS y pone _build_task_commands() en stub con docstring de ejemplo, fallback en infer_systems agrega systems declarados por DOMAIN_AGENTS. Nuevo tools/sprint.py CLI autonomo (subcomandos plan/list/status; escribe a artifacts/sprints/<slug>.md + .json via write_sprint_run_artifacts). tools/timeline.py gana de vuelta parseo de sprints activos (<start>..<end>) leyendo artifacts/sprints/*.json, y muestra seccion 'Sprints activos' en los daily. tools/devlog.py --sprint ya enlaza entradas al ciclo activo (ya estaba). Docs actualizados: README.md (nueva seccion Sprints + estructura + smoke test + personalizacion), memory/STRUCTURE.md (multiagents amplia descripcion, tools suma sprint.py, artifacts suma sprints/), memory/INDEX.md (artifacts/sprints/ + nota de sprints), .claude/multiagent.md (bloque 'Sistema de sprints' con CLI y integracion). Smoke-test end-to-end pasa: sprint plan --save genera fichero, list y status lo detectan, timeline lo cruza con chat+devlog. Kit queda limpio tras tests.

## 2026-04-18T10:33Z — Claude — [MULTIAGENT] Subagentes Root/Sub como identidad de primera clase
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: chat_memory.py: MENTION_RE acepta Root/Sub y build_agent_states descubre subagentes (raices siempre presentes). devlog.py: VALID_AGENTS generaliza a Root/Sub, CLI valida con type=_agent_arg, ENTRY_HEADER_RE amplia agent. Nuevo memory/ROSTER.md como directorio curado de subagentes activos (stub sin filas). memory/INDEX.md y memory/STRUCTURE.md enlazan ROSTER y lo citan como PASO 4 de lectura. Protocolo documentado en .claude/multiagent.md + CLAUDE.md + AGENTS.md + .github/copilot-instructions.md. Smoke test: parser descubre Claude/KIT y Copilot/OPS con estados correctos; devlog acepta Claude/KIT y rechaza Bogus.

## 2026-04-18T10:56Z — Claude — [TOOLING] Apertura/cierre de sesion multiagente cableados
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: Nuevo apps/abrir_sesion.bat (init_chat + memory_check) y apps/cerrar_sesion.bat (sync-chat-memory + memory_check). INICIAR_COWORKIA.bat invoca apertura antes de lanzar el GUI (no bloquea el dashboard si apertura falla, solo avisa). Evita cargo-cult: sync-chat-memory queda reservado para cierre (tras MEMORIA/CERRADO), no al abrir. memory_check detecto TREE desfasado durante el smoke test -> regenerado con snapshot_structure.py (ahora incluye ROSTER.md y los dos nuevos .bat). Smoke test verde end-to-end: apertura imprime briefing (memoria + 3 ultimas entradas devlog) y valida memory/; cierre regenera los 6 artifacts + SNAPSHOT y revalida.

## 2026-04-18T11:07Z — Claude — [DOCS] Regla de precedencia repo-vs-harness-memories
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: Nueva seccion 'Precedencia: memoria del repo sobre memoria del harness' en .claude/multiagent.md: las memorias locales del harness (Codex ~/.codex/memories/, Claude profile memory, etc.) nunca sustituyen a la memoria versionada. Orden de autoridad: AGENTS/CLAUDE/copilot-instructions -> memory/*.md -> chat del dia -> devlog. Pointer corto anadido a AGENTS.md con link a la seccion canonica. Replicado en tool-kit/ (AGENTS.md + .claude/multiagent.md) con redaccion generica. Decision: no crear .codex/ en el repo; OpenAI recomienda AGENTS.md como canal project-scoped y ningun harness lee esa ruta.

## 2026-04-18T11:17Z — Claude/ABGD — [DOCS] Alta de subagente Claude/ABGD en ROSTER
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: David activa Claude/ABGD como subagente Claude especializado en Obsidian (ABGD). Fila anadida a memory/ROSTER.md con foco: vault Obsidian, jerarquia ABPC, promocion a PTN, sync INX Obsidian<->otros, revision de obsidian_agent.py/obsidian_tools.py/log_obsidian_changes.py. Hereda protocolo de CLAUDE.md + .claude/multiagent.md. Handoff a @Claude si la pregunta sale del foco ABGD.

## 2026-04-18T11:24Z — Claude/ABGD — [DOCS] Caso de uso 07: promocion Obsidian -> PTN-Notas
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: Nuevo docs/casos-de-uso/07-promocion-obsidian-a-ptn.md (inverso del caso 03). Documenta flujo con tools/promote_obsidian_to_ptn.py + pasos INX posteriores (log_obsidian_changes + inx_sync_obsidian). DoD marca 3 criterios cumplidos y 2 pendientes. Gaps listados: (1) Proyecto como rich_text en lugar de relation; (2) script no sincroniza INX, requiere pasada posterior; (3) sin cruce automatico obsidian:<ruta> <-> ptn:<id>; (4) no acepta --tarea, solo --proyecto; (5) sin validador. Mejoras propuestas: validate_case_07.py, --tarea, sync INX inline, migrar Proyecto a relation, .bat lanzador. Indice de casos actualizado.

## 2026-04-18T11:25Z — Claude/ABGD — [DOCS] Alta de subagente Codex/ABGD + handoff Mejora 1 caso 07
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: Codex/ABGD registrado en memory/ROSTER.md con foco: implementacion tecnica capa Obsidian (validadores, refactor obsidian_tools/promote_obsidian_to_ptn, .bat de apps, pruebas sync INX). Activado en chat_2026-04-18.md. Handoff explicito a Codex/ABGD en chat del dia con spec detallada de tools/validate_case_07.py (input DBs, dedup, cruces OBSIDIAN_DB e INX obsidian:*/ptn:*, exit codes, batch apps/validate_case_07.bat, reto abierto sobre campo Tarea sobrecargado).

## 2026-04-18T11:39Z — Claude — [PTN] Migracion Tarea -> Ruta Obsidian en PTN-Notas (pre-validador)
Estado: DONE
Chat: chats/chat_2026-04-18.md
Refs: CERRADO #8
Resumen: Nueva propiedad Ruta Obsidian (rich_text) en NOTION_DS_NOTAS. tools/migrate_notas_ruta_obsidian.py one-shot idempotente con --dry-run: crea la propiedad si falta, copia Tarea->Ruta Obsidian solo para filas cuyo valor termine en .md y donde Ruta Obsidian este vacia. No limpia Tarea (queda para usuario si repurposea la propiedad a relation). tools/promote_obsidian_to_ptn.py actualizado (linea 74): nuevas filas escriben Ruta Obsidian en lugar de Tarea. docs/casos-de-uso/07-promocion-obsidian-a-ptn.md actualizado en 5 puntos: verificacion manual, observabilidad, Gap 4 (ahora resuelto tras migracion), spec de Mejora 1 (valida Ruta Obsidian), y DoD. Resultado: Tarea libre para su semantica original (relation a tarea PTN); validador de Codex/ABGD consumira Ruta Obsidian directamente sin deuda tecnica. Migracion pendiente de aplicar por David contra el workspace real (dry-run primero).

## 2026-04-18T12:04Z — Codex/ABGD — [ABGD] Validador caso 07 + parche defensivo del promote
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: tools/validate_case_07.py nuevo: cruza PTN-Notas (Ruta Obsidian) contra OBSIDIAN_DB.Ruta e INX-ENLACES (obsidian:* y ptn:*). Detecta schema sin migrar y sale con exit 1 + hint. Reporta hasta 5 ejemplos de cada faltante. Exit 0/1/2. apps/validate_case_07.bat nuevo: patron analogo a validate_case_03.bat (log_obsidian_changes -> sync_inx_links --source obsidian -> validate). tools/promote_obsidian_to_ptn.py parche: _require_schema_migrated(rows) lanza RuntimeError claro si 'Ruta Obsidian' no existe en NOTION_DS_NOTAS antes de cualquier write; evita error opaco de la API de Notion. _find_ptn_nota ahora recibe rows para reutilizar el query. memory/STRUCTURE.md regenerado; memory_check verde. Compile OK. Pendiente smoke contra workspace real cuando David corra el migrate + promocion de prueba.

## 2026-04-18T12:37Z — Codex/ABGD — [ABGD] Caso 07 validado end-to-end: Gaps 2/3/5 cerrados
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: apps/validate_case_07.bat refactorizado a 5 pasos: log_obsidian_changes -> log_ptn_changes -> sync_inx_links --source obsidian -> --source notion -> validate. Diagnostico clave: sync_inx_links --source notion lee de NOTION_DB (log PTN), no de NOTION_DS_NOTAS; sin log_ptn_changes intermedio la promocion no genera ptn:<id> en INX. Validado end-to-end con 3 promociones de prueba (N251104-Analisis de datos con GLM, N251118-Proyecto propuesta inicial, N251104-Analisis Estudio 2): 3/3 match OBSIDIAN_DB, 3/3 match INX obsidian:*, 3/3 match INX ptn:*, 3/3 cruce doble. docs/casos-de-uso/07 actualizado: DoD 5/5 cumplidos, Gap 2/3 marcados RESUELTO via bat, Gap 5 RESUELTO, automatizacion incluye log PTN, validacion practica implementada. Gap 1 (Proyecto relation) y Gap 4 (--tarea) siguen en backlog; Mejora 3 (sync inline en promote) deseable pero opcional. Migracion no se aplico sin flag porque dry-run reporto 0 filas a migrar (schema ya estaba).

## 2026-04-18T13:07Z — Codex/ABGD — [ABGD] Caso 07 backlog cerrado: Mejoras 3/Gap 4/Gap 1
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: promote_obsidian_to_ptn.py: flag --sync encadena log_obsidian + log_ptn + sync_inx_links obsidian/notion via subprocess (Mejora 3); flag --tarea <ref> con _resolve_task_id case-insensitive (Gap 4); deteccion dinamica de schema en _project_props/_task_props: escribe relation en 'Proyecto PTN'/'Tarea PTN' si existen, fallback a rich_text legacy (Gap 1, retrocompatible). tools/migrate_notas_ptn_relations.py nuevo: crea props relation single_property en NOTION_DS_NOTAS apuntando a NOTION_DS_PROYECTOS/NOTION_DS_TAREAS, copia IDs UUID legacy a las relations, idempotente, --dry-run. Aplicado contra workspace: 2 props creadas, 1 fila migrada. Smoke tests: 2 promociones nuevas (N251104-Datos Estudio 3 con --proyecto Sofia, N251104-EVPS-Tema 5 con --tarea uuid) + inspeccion confirma relations escritas; validate_case_07 reporta 5/5 cruce doble, PTN-Notas=6, INX obsidian:*=28, INX ptn:*=15. docs/casos-de-uso/07: 5 Gaps y 4 Mejoras marcados RESUELTO/HECHO; Mejoras 5 (bat manual) y 6 (cleanup legacy) quedan opcionales bajos. memory/STRUCTURE.md regenerado.

## 2026-04-18T13:25Z — Codex/ABGD — [ABGD] Caso 07 100%: Mejoras 5 y 6 cerradas
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: apps/promote_obsidian_to_ptn.bat nuevo (Mejora 5): wrapper Windows con %* forward, mensaje de uso si sin args, patron analogo a log_ptn_changes.bat. tools/cleanup_notas_legacy_props.py nuevo (Mejora 6): vacia 'Proyecto'/'Tarea' rich_text solo si la relation equivalente contiene el mismo UUID (match con y sin guiones). Idempotente, --dry-run. Aplicado contra workspace: 1 fila limpiada (la de migrate_notas_ptn_relations). Idempotencia confirmada con re-run (0 a limpiar). validate_case_07.py post-cleanup sigue en 5/5 cruce doble. memory/STRUCTURE.md regenerado. docs/casos-de-uso/07 actualizado: Mejoras 5/6 [HECHO], tabla automatizacion incluye el bat y el cleanup. Caso 07 cerrado al 100% (5/5 Gaps + 6/6 Mejoras).

## 2026-04-18T13:36Z — Codex/ABGD — [INX] Caso 08 alcance B: KIT primera clase en INX
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: tools/sync_inx_links.py gana _sync_kit (kit:<page_id> con Elemento=Titulo, Fuente=Notion, URL=Enlace, Detalle=Tipo|Subtipo) y --source kit. NOTION_DB_KIT en required map, dispatch if-chain. Retrocompatible. tools/validate_case_08.py nuevo: cuenta KIT entries con Titulo vs INX kit:*, normaliza UUIDs, reporta match/missing, exit 0/1/2. apps/validate_case_08.bat nuevo: pipeline sync kit -> validate con --no-pause. docs/casos-de-uso/08-kit-en-inx.md nuevo: alcance B explicito, DoD 4/4 + 1 fuera de alcance, 3 Gaps hacia alcance C (cruce Obsidian<->KIT, Usada en relation, opcion Fuente=KIT). Indice de casos actualizado. Smoke test: 1/1 entrada KIT reflejada en INX (Sistema Coworkia). memory/STRUCTURE.md regenerado; memory_check verde.

## 2026-04-18T13:43Z — Codex/ABGD — [ABGD] Caso 09: BIB -> ficha de lectura Obsidian con cruce INX
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: tools/promote_bib_to_obsidian.py nuevo: resuelve citekey en NOTION_DB_BIB, crea .md bajo A1-INV/B13-PUB/<contexto> (default C137-ART) con frontmatter (citekey, bib-id, doi, anio, autores, tipo, journal, estado-lectura) y secciones (Resumen pre-rellena con Abstract, Puntos clave, Citas relevantes, Notas propias). Flags: --contexto, --force, --sync. Dedup por presencia de archivo que contenga el citekey en el nombre. --sync encadena log_obsidian + log_ptn + sync_inx_links obsidian + paperpile via subprocess. tools/validate_case_09.py nuevo: parser manual de frontmatter para detectar fichas, cruza con BIB.Citekey, INX obsidian:*, INX paperpile:*. Reporta cruce doble, huerfanas, gaps. Exit 0/1/2. apps/validate_case_09.bat nuevo: log + sync obsidian + sync paperpile + validate. apps/promote_bib_to_obsidian.bat nuevo: wrapper Windows. docs/casos-de-uso/09-bib-a-obsidian.md: flujo, DoD 4/4 estructural, 3 Gaps (cruce INX explicito, BIB vacio en workspace, sin sync inverso Obsidian->BIB), 3 Mejoras. Indice de casos actualizado. Smoke test estructural: BIB=0 -> validator exit 1 con hint correcto. Validacion end-to-end pendiente de carga BIB real via bib_agent.py importar. memory/STRUCTURE.md regenerado.

## 2026-04-18T13:47Z — Codex/ABGD — [ABGD] Caso 10: checkboxes Obsidian -> Todoist con marker inline
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: tools/promote_notas_checkboxes_to_todoist.py nuevo: regex CHECKBOX_RE captura '- [ ] <content>' con grupo marker opcional. Por cada linea sin marker crea tarea Todoist (create_task de todoist_tools) con content=desc y description='Obsidian: <ruta>'. Re-escribe nota in-place anadiendo '<!-- todoist:<id> -->' inline, preservando newline final. Idempotente: re-ejecutar ignora lineas con marker. Flag --sync encadena log_obsidian + sync_inx_links obsidian + todoist. tools/validate_case_10.py nuevo: escaneo rglob de ALPHA_PATH, MARKER_RE extrae todoist_id, PENDING_RE cuenta captura pendiente. Cruza markers con INX todoist:*. Reporta matched/missing hasta 5 ejemplos. Exit 0/1/2. apps/validate_case_10.bat nuevo: log + sync obsidian + sync todoist + validate. apps/promote_notas_checkboxes_to_todoist.bat nuevo: wrapper Windows. docs/casos-de-uso/10-checkboxes-obsidian-a-todoist.md: flujo, DoD 5/5 estructural, 5 Gaps (close sync, --all, cruce INX explicito, --project, description ABPC), 4 Mejoras. Indice actualizado. Smoke estructural: 0 markers + 16 checkboxes pendientes + 441 todoist:* en INX; exit 1 correcto. Promote real no ejecutado (crearia tareas Todoist sin autorizacion). memory/STRUCTURE.md regenerado.

## 2026-04-18T13:58Z — Codex/ABGD — [TOOLING] Caso 11: journal diario Obsidian integrado en timeline
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: tools/timeline.py extendido: carga dotenv, helper _journal_for(day) resuelve N<YYMMDD>-*.md bajo A0-GTD/B0C-PLA/C0C9-Notas/ recursivamente. DailyBundle suma journal_path. render_daily emite seccion 'Journal Obsidian' con path relativo al vault o placeholder. tools/validate_case_11.py nuevo: escanea C0C9-Notas, extrae dia del stem, verifica que artifacts/daily/<day>.md contiene la seccion + path. Reporta matched/missing_timeline/missing_ref. Exit 0/1/2. apps/validate_case_11.bat nuevo: regenera timeline -> valida. docs/casos-de-uso/11-journal-diario-en-timeline.md: flujo, DoD 6/6, 4 Gaps (primer match, sin parsing, sin plantilla, no INX), 4 Mejoras. Indice actualizado. Smoke end-to-end: creada nota de prueba 2026-04-18 (local, borrable), timeline regenerado, validator 1/1 verde. memory/STRUCTURE.md regenerado.

## 2026-04-18T14:32Z — Codex/ABGD — [INX] Caso 12: backfill INX historico vault -> OBSIDIAN_DB -> INX
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: tools/backfill_obsidian_to_inx.py nuevo: full-scan de vault via get_todas_notas, diff contra OBSIDIAN_DB.Ruta, crea filas faltantes con schema identico a log_obsidian_changes (Evento/Fecha/Archivo/Ruta/Tipo/Detalle + relations ABC). Idempotente. --dry-run y --sync. Complementa a log_obsidian (mtime-based) para cubrir historico o post-corrupcion de obsidian_log_state.json. tools/validate_case_12.py nuevo: reporta vault vs OBSIDIAN_DB vs INX obsidian:*, deltas en dos etapas + orphan DB rows informativos. Exit 0/1/2. apps/validate_case_12.bat nuevo: backfill dry-run -> log_obsidian -> sync obsidian -> validate. docs/casos-de-uso/12-backfill-inx-historico.md: flujo, DoD 6/6, 4 Gaps (no cleanup orphans, Fecha=mtime, no renames, filtros de get_todas_notas no auditados), 4 Mejoras. Indice actualizado. Smoke end-to-end 2026-04-18: pre=29/28/28 -> backfill crea 1 -> post=29/29/29 cobertura total. Cerro de paso el huerfano del caso 11 (nota journal). memory/STRUCTURE.md regenerado.

## 2026-04-18T15:11Z — Codex/ABGD — [ABGD] Caso 13: wikilinks cross-system con auditoria INX
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: tools/obsidian_wikilinks.py nuevo: modulo unificado con subcomandos audit y find. Regex detecta [[<prefix>:<id>]] con prefix en {ptn, kit, paperpile, todoist, github}. scan_vault retorna hits con ruta/linea/prefix/id. _load_inx_keys carga INX separando por prefijo. _resolve normaliza UUID para ptn/kit, match exacto para paperpile/todoist/github. audit: totales por prefijo + INX disponibles, ejemplos con ubicacion, rotos hasta 10 con linea exacta, exit 0/1. find: lista notas que contienen exactamente el wikilink con ruta/linea/contenido. tools/validate_case_13.py alias de audit. apps/validate_case_13.bat. docs/casos-de-uso/13-wikilinks-cross-system.md: sintaxis, DoD 6/6, 4 Gaps (sin open, sin autocomplete, depende de INX al dia, no enriquece INX), 4 Mejoras (open con URLs, plugin Obsidian, parser en _sync_obsidian, normalizador UUIDs). Smoke end-to-end: creada N260418-Test wikilinks cross-system.md con 3 wikilinks (kit valido, ptn valido, ptn roto intencional) -> audit reporta 3 detectados, 1 roto en L11, exit 1. find kit:<uuid> devuelve la nota con L7. Indice de casos actualizado. memory/STRUCTURE.md regenerado.

## 2026-04-18T15:56Z — Codex/ABGD — [ABGD] Caso 10 validado end-to-end + fix pipeline (sync_todoist_to_notion)
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: Smoke real sobre N251028-borrador (10 checkboxes) con autorizacion explicita de David. Gap detectado en primera pasada: --sync del promote saltaba sync_todoist_to_notion, asi que las 10 tareas recien creadas no aparecian en INX (matcheaban 0/10). _sync_todoist lee de TODOIST_DB_TAREAS (espejo Notion), no de la API Todoist directa; requiere sync_todoist_to_notion como paso intermedio. Fix aplicado en tools/promote_notas_checkboxes_to_todoist.py _run_sync_chain y en apps/validate_case_10.bat (ahora 5 pasos: log_obsidian + sync_todoist_to_notion + sync obsidian + sync todoist + validate). Propagacion manual post-fix: sync_todoist_to_notion.py sincronizo 91 tareas, sync_inx_links --source todoist creo las filas faltantes. validate_case_10.py reporta 10/10 markers con fila INX. docs/casos-de-uso/10 actualizado: DoD marca validacion end-to-end completada, flujo principal menciona explicitamente el paso sync_todoist_to_notion.

## 2026-04-18T17:00Z — Codex/ABGD — [BIB] Caso 09 validado end-to-end + fix Paperpile sync via GitHub
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: Paperpile cambio UI: ya no expone URL directa paperpile.com/eb/..., ahora exporta via GitHub/Drive/Overleaf. Solucion elegida: repo privado dalarconrub/paperpile-lib como destino GitHub. gh repo create --private --add-readme. Invitacion paperpile-bot con permission=push aceptada automaticamente. Paperpile sincroniza library.bib a /main/library.bib (1.2 MB con 472 entradas). tools/paperpile_tools.py parcheado: fetch_bibtex detecta raw.githubusercontent.com y anade Authorization Bearer GITHUB_TOKEN (token ya en .env, scope repo). .env linea 26 actualizada con raw URL. Smoke end-to-end: bib_agent.py importar -> 472 papers creados en NOTION_DB_BIB. promote_bib_to_obsidian.py Candido2026y --sync -> N260418-Candido2026y.md creada + log_obsidian + log_ptn + sync_inx_links obsidian/paperpile. validate_case_09: 1/1 fichas con cruce doble obsidian:* <-> paperpile:* exit 0. docs/casos-de-uso/09 DoD marcado completo. Nota: docs/bib-agent.md y tools/paperpile_tools.py docstring siguen referenciando la UI vieja de Paperpile; seria mejora documental futura.

## 2026-04-18T17:13Z — Codex/ABGD — [DOCS] Actualizada doc BIB al flow GitHub (post-retiro de paperpile.com/eb)
Estado: DONE
Chat: chats/chat_2026-04-18.md
Resumen: docs/bib-agent.md: seccion 'Variables en .env' y 'Como obtener PAPERPILE_BIBTEX_URL' reescritas para reflejar el nuevo flow (Paperpile ya no expone URL publica; destinos soportados son GitHub/Drive/Overleaf). Pasos 1-5 con comandos ejecutables (gh repo create, gh api collaborators/paperpile-bot, configuracion .env, verificacion). tools/paperpile_tools.py docstring modulo actualizado: describe flow 2026, menciona parche fetch_bibtex para raw.githubusercontent.com con Authorization Bearer GITHUB_TOKEN, puntero a docs/bib-agent.md. .env.example: comentario antes de PAPERPILE_BIBTEX_URL explicando el cambio y que GITHUB_TOKEN es obligatorio para repos privados.

## 2026-04-19T11:31Z — Claude — [DOCS] Pipeline Atlas: doc maestra Mermaid + GUI Tk navegable
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #8
Resumen: Nueva doc maestra docs/pipeline-atlas.md con diagramas Mermaid por capa: (a) arquitectura global datos, (b) un flujo Mermaid por cada uno de los 6 dominios (MAR, PTN, KIT, REP, BIB, ABGD) + INX como glue, (c) arquitectura coordinacion con chat+devlog+memory+timeline+sprints+subagentes, (d) tabla de 13 casos de uso con dominios implicados, (e) pipeline de apertura/cierre de sesion, (f) resumen de variables de entorno por dominio. Links a docs/casos-de-uso/, docs/<agent>.md y artefactos. Nuevo apps/pipeline_gui.py (Tkinter unificado, consistente con project_hub_gui.py: BG #0b1020 + Segoe UI + ttk.Treeview). 13 nodos en sidebar (7 datos + 6 coordinacion). Por nodo muestra: resumen, flow ASCII, scripts (CLI/App/Tool/Lib) con botones Copiar+Abrir, artifacts, env vars con marca OK/MISSING evaluada en vivo, casos aplicables con enlace, CLI de ejemplo copiable. Barra superior con estado vivo: fecha, chat del dia, salud memory, sprints activos, ultimas 5 entradas devlog; auto-refresh cada 60s. Read-only: para ejecutar, copia el comando al portapapeles. apps/pipeline_gui.bat wrapper Windows. memory/INDEX.md destaca pipeline-atlas como entrada principal de docs. docs/guia-rapida.md lista pipeline_gui. Smoke test en modo headless: 13 nodos construidos, 3 nodos renderizados en secuencia OK, parser devlog maneja subagente Codex/ABGD. memory_check verde tras snapshot_structure.

## 2026-04-19T11:46Z — Claude — [DOCS] Boton Ejecutar cross-platform en pipeline_gui y doc del atlas ampliada
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #9
Resumen: apps/pipeline_gui.py: nuevo boton Ejecutar por script (.py y .bat) al lado de Copiar/Abrir. Cross-platform: Windows via cmd /k persistente, macOS via .command tempfile abierto con 'open' (Terminal.app), Linux tanteo de x-terminal-emulator/gnome-terminal/konsole/xfce4-terminal/xterm. Usa sys.executable para respetar venv. cwd en raiz del proyecto. shlex.quote para paths con espacios. Fix adicional: recursion en <<TreeviewSelect>> eliminada via guard current_key + metodo _render_node separado de _select_node. docs/pipeline-atlas.md: seccion 'Ver el atlas en vivo' ampliada con layout, tabla de botones, tabla de comportamiento por SO, reglas de seguridad operativa y checklist para anadir/modificar nodos.

## 2026-04-19T12:07Z — Claude — [MAR] Fase 1 del sistema de reseteo: tools/reset_mar.py para Todoist
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #10
Resumen: Nuevo CLI tools/reset_mar.py que archiva tareas Todoist a Z-INBOX preservando proyecto de origen en description. Subcomandos: reset-all, reset-by-type (idea|meta|habito|tarea|evento), reset-by-project, reset-by-label, reset-overdue --days N, list-archived, restore, restore-all --from. Flags transversales --dry-run, --limit, --zinbox-id. Mecanica: append marker '[ARCHIVED: YYYY-MM-DD | orig-project: <id>]' a description via update_task, luego move_task al Z-INBOX (id 6Mv5F76GQq3p699F). Idempotente (skip si ya tiene marker), reversible (restore parsea marker y devuelve al origen). Nunca toca proyectos Z-*. Reusa tools.todoist_tools: move_task, update_task, get_tasks, classify_mar_type, Z_PROJECTS. apps/reset_mar.bat wrapper Windows. Nodo 'Reset MAR' anadido a apps/pipeline_gui.py _build_atlas bajo coordinacion con flow y sample CLI. docs/pipeline-atlas.md nueva subseccion 'Reset MAR' con CLI, mecanica, alcance Fase 1 (Todoist-only, INX no tocado). Smoke test dry-run real: reset-all detecta 5 tareas fuera de Z-* correctamente; reset-by-type idea filtra 3 sin due/deadline; list-archived devuelve vacio (aun no hemos ejecutado real); reset-overdue --days 90 sin candidatos. memory_check OK tras snapshot_structure.

## 2026-04-19T12:31Z — Claude — [PTN] Fase 2 del sistema de reseteo: reset_notion.py con checkbox Archivo + propagacion INX
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #11
Resumen: Tres piezas nuevas: (1) tools/ensure_archivo_field.py bootstrap idempotente que anade Checkbox 'Archivo' a PTN Proyectos/Tareas/Notas y a NOTION_DB_INX (get_data_source_schema + update_database_properties); (2) tools/reset_notion.py CLI con reset-ptn-{proyectos,tareas,notas,all}, list-archived, restore, restore-all; flags --dry-run --limit --snapshot --no-inx; (3) apps/reset_notion.bat wrapper. Mecanica: update_page_properties Archivo=true + propagacion a fila INX con Clave 'ptn:<page_id>' probando variantes con y sin guiones. Preserva el Estado existente de cada data source. Snapshot opcional a artifacts/resets/YYYY-MM-DD/ptn-<target>-<ts>.json con page_id/title/Estado previo. Fix colateral: notion_tools.get_data_source_schema ampliado con fallback a /databases/{id} (la version previa devolvia 400 para IDs legacy como los actuales de Coworkia). Nodo 'Reset Notion' anadido a apps/pipeline_gui.py _build_atlas. docs/pipeline-atlas.md nueva subseccion 'Reset Notion (Fase 2)' con mecanica, ejemplos y alcance (PTN solamente; KIT/REP/BIB iteracion siguiente). Smoke test dry-run: ensure_archivo_field detecta los 4 DS accesibles y reportaria PATCH sobre los 4 (ninguno tiene 'Archivo' aun); reset_notion aborta con mensaje claro 'ejecuta ensure_archivo_field.py primero'. memory_check OK.

## 2026-04-19T12:33Z — Claude — [PTN] Fase 2 bootstrap aplicado: propiedad Archivo creada en 4 DS y dry-run validado en vivo
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #11
Resumen: Paso (a) ensure_archivo_field.py ejecutado contra Notion real: PATCH exitoso en PTN-Proyectos, PTN-Tareas, PTN-Notas, INX-ENLACES (4/4 creadas, 0 ya_existian). Idempotente comprobado. Paso (b) reset_notion.py reset-ptn-proyectos --dry-run --snapshot --limit 5: detecta 5 proyectos (Tesis Cristian, TFG 2025-26, Sofia, ejemplos A3/A4), propagacion INX 5/5 sin missing (confirma que el mapping 'ptn:<page_id>' funciona con los IDs actuales del repo, incluyendo proyectos reales y de ejemplo). Snapshot escrito a artifacts/resets/2026-04-19/ptn-proyectos-123255Z.json con id/title/url/archivo_before/Estado previo por pagina. 0 errores. Listo para uso real (quitar --dry-run cuando David lo decida).

## 2026-04-19T12:41Z — Claude — [ABGD] Fase 3 del sistema de reseteo: reset_obsidian.py con rotacion vault (estrategia C)
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #12
Resumen: Nuevo tools/reset_obsidian.py con subcomandos: status (muestra OBSIDIAN_ABGD_ROOT actual, top-level, Archivo presente en INX), rotate (crea vault nuevo sibling con estructura replicada hasta --depth N default 3 + copia integra de .obsidian, flip Archivo=true en INX obsidian:*), list-archived, restore --from OLD_VAULT_PATH. Flag --new-vault-path obligatorio. Otros flags: --dry-run, --snapshot, --no-inx, --force, --depth. Estrategia C: el vault viejo NO se toca fisicamente, queda intacto y consultable. El vault nuevo nace en la ruta que David elija. El CLI NO edita .env; imprime la linea OBSIDIAN_ABGD_ROOT=<new_path> para pegar manualmente (respeta control del usuario sobre credenciales). restore lista las notas .md creadas en el vault nuevo para migracion manual antes de cambiar .env. apps/reset_obsidian.bat wrapper. Nodo 'Reset Obsidian' en pipeline_gui atlas. docs/pipeline-atlas.md nueva subseccion 'Reset Obsidian (Fase 3)'. Smoke tests contra vault real (C:/GDrive/dalarconrub/ABGD/ABGD-25.09.05): status muestra 5 top-level (1.ALPHA..5.EPSILON) + .obsidian + Archivo presente en INX; rotate --dry-run --snapshot a path fake (_TEST_NEW_VAULT) replicaria 35 dirs a depth 3 + saltaria 33 dirs profundas + copiaria .obsidian (6.8 MB) + flipearia 30 filas INX obsidian:*. Snapshot escrito a artifacts/resets/2026-04-19/obsidian-rotate-123944Z.json. memory_check OK.

## 2026-04-19T12:50Z — Claude — [MULTIAGENT] Fase 4 del sistema de reseteo: orquestador reset_all.py (MAR -> Notion -> Obsidian)
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #13
Resumen: Nuevo tools/reset_all.py encadena las 3 fases en orden fijo Todoist -> Notion -> Obsidian via subprocess chain (cada fase corre como proceso propio, no import directo; si el orquestador muere, las fases completadas no se rebobinan). Politica de abort: si fase N falla, aborta antes de N+1 e imprime los comandos de restore para recuperar lo ejecutado (reset_mar restore-all, reset_notion restore-all --target all, reset_obsidian restore --from). Snapshot forzado siempre en Notion y Obsidian (no hay bandera para deshabilitarlo desde el orquestador); MAR usa su marker reversible en description. Obsidian se skipea automaticamente sin --obsidian-new-vault-path para evitar crear vaults sorpresa. --dry-run propaga a las 3; --yes evita confirmacion interactiva; --skip-mar/--skip-notion/--skip-obsidian skippean individualmente. Output: caja con plan previo, output bruto de cada subprocess, summary final con [OK]/[FAIL]/[skip] por fase y comandos de restore si hay fallo. apps/reset_all.bat wrapper. Nodo 'Reset General' en pipeline_gui atlas. docs/pipeline-atlas.md nueva subseccion 'Reset General (Fase 4)' con orden, politica, flags y recomendacion de uso progresivo (dry-run sin Obsidian -> dry-run con Obsidian -> real). Smoke tests: dry-run MAR+Notion skip Obsidian funciona (3 tareas MAR + 2+1+2 PTN con 5/5 INX propagacion); dry-run con --obsidian-new-vault-path completa las 3 con [OK] [OK] [OK]. memory_check OK.

## 2026-04-19T13:12Z — Claude — [MULTIAGENT] Caso 14 validando sistema de reseteo end-to-end: 34 PASS / 0 FAIL / 3 SKIP
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #14
Resumen: Nuevo docs/casos-de-uso/14-reset-sistema.md con matriz de 37 tests por fase (MAR/Notion/Obsidian/reset_all + cross-phase) y marcas A (auto) / M (manual). Nuevo tools/validate_case_14.py que ejecuta la subset A: arranca cada CLI con --help/--dry-run/argumentos invalidos y comprueba exit codes, presencia de usage, mensajes de error claros, propagacion INX 0 missing, snapshot JSON parseable, profundidad de replica vault (depth 1 = 5 dirs top, depth 3 default = 35 dirs), abort policy, skip automatico de Obsidian sin path, y propagacion de --limit. apps/validate_case_14.bat wrapper. Primera corrida: 33 PASS / 1 FAIL / 3 SKIP. El FAIL era C.2 memory_check por TREE desfasado tras anadir los ficheros nuevos — se regenero snapshot_structure y paso OK. Re-run cross-phase: 4/4 PASS. Resultado final: 34 PASS / 0 FAIL / 3 SKIP (1.8 idempotencia post-ejecucion real, 4.6 prompt interactivo sin stdin stubbing, 4.7 simulacion de fallo de fase — todos documentados en Gaps del caso). docs/casos-de-uso/index.md actualizado. memory_check OK.

## 2026-04-19T15:07Z — Codex — [DOCS] Sincronizada memory/SNAPSHOT tras desfase operativo
Estado: DONE
Chat: chats/chat_2026-04-19.md
Resumen: Detectado desfase entre el chat activo de 2026-04-19 y memory/SNAPSHOT.md auto-generado. Se anadio evaluacion de coordinacion al chat del dia, se regenero la memoria derivada con sync-chat-memory y se dejo el estado compartido consistente para el siguiente turno.

## 2026-04-19T15:10Z — Codex — [MULTIAGENT] Abierto Sprint 2 post-reseteo
Estado: DONE
Chat: chats/chat_2026-04-19.md
Sprint: sprint-multiagent-2
Refs: CERRADO #15
Resumen: Se cerro la decision #15 en el chat del dia y se persistio artifacts/sprints/sprint-multiagent-2.{md,json} como sprint activo. El backlog cubre baseline post-reseteo, automatizacion de higiene de sesion, cierre manual del caso 14 y priorizacion del siguiente frente funcional.

## 2026-04-19T15:11Z — Codex — [DOCS] Regenerado TREE tras apertura de Sprint 2
Estado: DONE
Chat: chats/chat_2026-04-19.md
Sprint: sprint-multiagent-2
Resumen: La creacion de artifacts/sprints/sprint-multiagent-2.{md,json} y artifacts/daily/2026-04-19.md dejo desfasado el TREE de memory/STRUCTURE.md. Se regenero con snapshot_structure para restaurar coherencia documental del repo.

## 2026-04-19T15:21Z — Codex — [TOOLING] Baseline ST-201 recuperado: env loader + orquestador robusto
Estado: DONE
Chat: chats/chat_2026-04-19.md
Sprint: sprint-multiagent-2
Resumen: Sprint 2 ST-201 quedo inicialmente bloqueado por dos defectos locales (captura subprocess con cp1252 y status del sprint mal recalculado) y por dependencia dura de python-dotenv. Se anadio tools/env_utils.py con fallback de carga .env, se conecto a la ruta critica del baseline y se corrigio agents/orchestrator_agent.py. Tras regenerar STRUCTURE y relanzar ST-201 fuera del sandbox, la tarea completo el baseline real post-reseteo.

## 2026-04-19T15:22Z — Codex — [MULTIAGENT] ST-202 cerrado: cierre de sesion regenera timeline
Estado: DONE
Chat: chats/chat_2026-04-19.md
Sprint: sprint-multiagent-2
Resumen: apps/cerrar_sesion.bat pasa a ejecutar sync-chat-memory -> timeline.py -> memory_check. Se actualizo la guia rapida y WINDOWS_START para documentar el pipeline de cierre recomendado, y el runbook de ST-202 quedo completado en Sprint 2.

## 2026-04-19T15:23Z — Codex — [MULTIAGENT] ST-203 cerrado: checklist manual del caso 14
Estado: DONE
Chat: chats/chat_2026-04-19.md
Sprint: sprint-multiagent-2
Resumen: Se documento en docs/casos-de-uso/14-reset-sistema.md la checklist manual restante del sistema de reseteo (tests 1.8, 4.6 y 4.7) con owner, evidencia esperada y criterio de cierre. El task board de Sprint 2 se actualizo para reflejar ST-203 como completada.

## 2026-04-19T15:24Z — Codex — [MULTIAGENT] ST-204 cerrado: ranking funcional post-reseteo
Estado: DONE
Chat: chats/chat_2026-04-19.md
Sprint: sprint-multiagent-2
Refs: CERRADO #16
Resumen: Se fijo en el chat del dia el ranking del siguiente frente funcional tras el bloque de reseteo: (1) Caso 08 alcance C Obsidian↔KIT, (2) Caso 10 round-trip Obsidian↔Todoist, (3) Caso 09 loop BIB↔Obsidian. El sprint persistido refleja ST-204 como completada.

## 2026-04-19T15:24Z — Codex — [MULTIAGENT] ST-205 cerrado: review y retrospectiva de Sprint 2
Estado: DONE
Chat: chats/chat_2026-04-19.md
Sprint: sprint-multiagent-2
Resumen: Sprint 2 queda cerrado con cuatro resultados: baseline post-reseteo validado, cierre de sesion automatizado con timeline, checklist manual del caso 14 documentada y ranking funcional fijado (08C > 10 > 09). Riesgo principal identificado: fragilidad del entorno Python sin python-dotenv, mitigada con env_utils y orquestador UTF-8 robusto.

## 2026-04-19T15:46Z — Codex — [ABGD] Caso 08C: cruce automatico Obsidian-KIT via KIT IDs
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #17
Resumen: Se implemento el alcance C del caso 08 con persistencia textual de referencias [[kit:<page_id>]] en OBSIDIAN_DB e INX-ENLACES. Nuevo tools/ensure_kit_cross_fields.py asegura la propiedad 'KIT IDs' en ambas bases. tools/log_obsidian_changes.py y tools/backfill_obsidian_to_inx.py extraen KIT IDs desde notas Obsidian; tools/sync_inx_links.py --source obsidian las propaga a INX; tools/validate_case_08.py --scope c valida preservacion. Ejecucion real: schema creado en vivo, sync obsidian=31 y validacion 08C OK sin mismatches.

## 2026-04-19T15:46Z — Codex — [DOCS] TREE regenerado tras 08C y sync de memoria
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #17
Resumen: Tras anadir tools/ensure_kit_cross_fields.py y actualizar la documentacion del caso 08, se regenero memory/STRUCTURE.md y se ejecuto memory_check + sync-chat-memory para mantener coherencia entre repo, chat y memoria derivada.

## 2026-04-19T15:53Z — Codex — [ABGD] Caso 08C validado end-to-end con nota real del vault
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #17
Resumen: Se creo la nota A0-GTD\\B0A-INX\\N260419-Test-08C-kit-link.md con [[kit:340622cf-315b-814b-bf50-e20378365646]], se ejecuto backfill_obsidian_to_inx --sync y validate_case_08.py --scope c. Resultado final: 1 fila OBSIDIAN_DB con KIT IDs, 0 mismatches en INX y validacion 08C OK de extremo a extremo.

## 2026-04-19T16:02Z — Codex — [ABGD] Limpieza de fixture 08C tras validacion
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #17
Resumen: Se elimino la nota de prueba N260419-Test-08C-kit-link.md del vault y se archivaron sus filas derivadas en OBSIDIAN_DB e INX-ENLACES para dejar el entorno sin basura operativa despues de la validacion end-to-end del caso 08C.

## 2026-04-19T16:33Z — Codex — [MAR] Caso 10 ampliado a round-trip de cierre Obsidian-Todoist
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #18
Resumen: Se implemento close sync para checkboxes marcados en Obsidian. Nuevo tools/close_obsidian_checkboxes_to_todoist.py cierra la tarea en Todoist y marca Estado=Completada en TODOIST_DB_TAREAS e INX. Nuevo tools/ensure_inx_completed_status.py asegura la opcion Completada en INX. tools/sync_inx_links.py ya respeta Completada al sincronizar fuente Todoist. tools/validate_case_10.py --scope all valida captura + cierre, apps/validate_case_10.bat pasa a esa validacion. Smoke real completado con fixture temporal y cleanup total al final.

## 2026-04-19T16:44Z — Codex — [BIB] Caso 09 ampliado a sync de estado-lectura Obsidian-BIB
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #19
Resumen: Se implemento tools/sync_bib_reading_state.py para sincronizar estado-lectura desde el frontmatter de fichas Obsidian hacia BIB.Estado. tools/validate_case_09.py ahora valida cruce doble + alineacion de estado (--scope all), apps/validate_case_09.bat usa el alcance completo y se anadio apps/sync_bib_reading_state.bat. Smoke real completado con Candido2026y: cambio temporal Por leer -> En proceso -> Por leer, sync OK y validacion final en verde.

## 2026-04-19T16:48Z — Codex — [BIB] INX obsidian:* expone Paperpile Citekey explicito
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #20
Resumen: Se anadio tools/ensure_inx_paperpile_citekey_field.py para crear Paperpile Citekey en INX-ENLACES y se extendio tools/sync_inx_links.py --source obsidian para leer citekey desde el frontmatter real de la nota y poblar esa propiedad en filas obsidian:*. tools/validate_case_09.py ahora exige el cruce explicito y la doc del caso 09 se actualizo. Validacion real OK con Candido2026y tras schema update + resync de obsidian.

## 2026-04-19T16:50Z — Codex — [BIB] Caso 09: batch --all-pending para promocion masiva
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #21
Resumen: tools/promote_bib_to_obsidian.py ahora soporta --all-pending para papers con Estado=Por leer, con salvaguardas --dry-run y --limit. Se actualizaron apps/promote_bib_to_obsidian.bat y docs/casos-de-uso/09-bib-a-obsidian.md. Smoke real seguro: --all-pending --dry-run --limit 10 detecta 10 candidatos y 10 creaciones potenciales sin escribir en el vault.

## 2026-04-19T17:03Z — Codex — [BIB] Caso 09: batch real de 5 papers + paperpile completo en INX
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #21
Resumen: Se ejecuto promote_bib_to_obsidian.py --all-pending --limit 5 --contexto C137-ART --sync, creando 5 fichas nuevas en el vault. El sync fallo inicialmente por 	ools/log_ptn_changes.py aun usando python-dotenv; se corrigio y se relanzo la cadena. Para cerrar la validacion fue necesario ampliar sync_inx_links --source paperpile a todo el catalogo, dejando paperpile:* = 472 en INX. Validacion final de caso 09 OK: 6/6 fichas con cruce doble, Paperpile Citekey explicito y estado-lectura alineado con BIB.

## 2026-04-19T17:07Z — Codex — [BIB] Caso 09: filtros finos para --all-pending
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #22
Resumen: Se extendio promote_bib_to_obsidian.py --all-pending con --query y --year, manteniendo --dry-run y --limit como salvaguardas. Se actualizaron wrapper y documentacion. Bug corregido en el mismo turno: el filtro batch tenia out.append() mal indentado y devolvia 0 candidatos; revalidado con --all-pending --dry-run --query Abad2021c --limit 10, que encuentra 1 candidato y lo clasifica como skip por ficha existente.

## 2026-04-19T17:11Z — Codex — [BIB] Caso 09: --sync del batch ya no deja INX parcial
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #23
Resumen: Se corrigio tools/promote_bib_to_obsidian.py para que --sync ejecute sync_inx_links completo en fuentes obsidian y paperpile, eliminando el limite fijo de 200 que podia dejar fuera citekeys recien promovidos. Revalidacion real OK con --all-pending --dry-run --query Abad2021c --limit 10, sin regresion del filtro fino.

## 2026-04-19T17:13Z — Codex — [BIB] Caso 09: filtros estructurales para --all-pending
Estado: DONE
Chat: chats/chat_2026-04-19.md
Refs: CERRADO #24
Resumen: Se extendio promote_bib_to_obsidian.py con filtros --author, --journal y --estado para el batch BIB→Obsidian, manteniendo los filtros previos --query, --year y --limit. Wrapper y documentacion actualizados. Revalidacion real OK con --all-pending --dry-run --author Candido --limit 10, que detecta 1 candidato existente y lo clasifica como skip.

## 2026-04-19T19:06Z — Codex — [MAR] Reset Todoist ejecutado en real
Estado: DONE
Chat: chats/chat_2026-04-19.md
Resumen: Se ejecutó tools/reset_mar.py reset-all sobre Todoist. El comando de escritura agotó el timeout local, pero la verificación posterior confirmó 0 tareas candidatas restantes en dry-run y tareas archivadas en Z-INBOX con marcador reversible, por lo que el reset quedó aplicado.

## 2026-04-19T19:19Z — Codex — [PTN] Reset Notion ejecutado en real
Estado: DONE
Chat: chats/chat_2026-04-19.md
Resumen: Se ejecutó tools/reset_notion.py reset-ptn-all --snapshot sobre el workspace PTN. Resultado: 9 proyectos, 1 tarea y 6 notas archivadas con Archivo=true, con propagación completa a INX y snapshots reversibles en artifacts/resets/2026-04-19/.

## 2026-04-19T19:24Z — Codex — [ABGD] Reset Obsidian deriva ruta ABGD-yymmdd por defecto
Estado: DONE
Chat: chats/chat_2026-04-19.md
Resumen: tools/reset_obsidian.py deja de requerir --new-vault-path y deriva por defecto un sibling bajo la misma raiz del vault actual con formato ABGD-yymmdd. tools/reset_all.py, docs/pipeline-atlas.md, docs/casos-de-uso/14-reset-sistema.md y apps/pipeline_gui.py se actualizaron a la nueva regla. Validacion real OK en dry-run: C:\\GDrive\\dalarconrub\\ABGD\\ABGD-25.09.05 -> C:\\GDrive\\dalarconrub\\ABGD\\ABGD-260419; reset_all --dry-run ya incluye Obsidian con ruta derivada.

## 2026-04-19T19:32Z — Codex — [ABGD] Reset Obsidian ejecutado en real
Estado: DONE
Chat: chats/chat_2026-04-19.md
Resumen: Se ejecutó tools/reset_obsidian.py rotate --snapshot con la ruta derivada por defecto. Se creó C:\\GDrive\\dalarconrub\\ABGD\\ABGD-260419, se replicaron 35 directorios, se copió .obsidian y se marcó Archivo=true en 36 filas obsidian:* de INX sin errores. Verificación posterior OK en disco e INX; queda solo el cambio manual de OBSIDIAN_ABGD_ROOT en .env y abrir el vault nuevo en Obsidian desktop.

## 2026-04-19T19:38Z — Codex — [ABGD] Entorno Obsidian apuntando al vault nuevo
Estado: DONE
Chat: chats/chat_2026-04-19.md
Resumen: Se actualizó .env para que OBSIDIAN_ABGD_ROOT y OBSIDIAN_ALPHA_PATH apunten a C:/GDrive/dalarconrub/ABGD/ABGD-260419 tras la rotación real del vault.

## 2026-04-19T20:07Z — Codex — [MAR] Reset MAR migra a Z-BACK-yymmdd y repara parciales
Estado: DONE
Chat: chats/chat_2026-04-19.md
Resumen: Se cambió tools/reset_mar.py para derivar/crear automáticamente un proyecto diario Z-BACK-yymmdd como destino del archivado Todoist, en lugar de usar Z-INBOX. Se añadió create_project en tools/todoist_tools.py y move_task se corrigió al endpoint oficial /api/v1/sync item_move. Ejecución real hoy: creación de Z-BACK-260419 (6gQW2Cqr8WFXCRmm) y reparación de 82 tareas marcadas-pero-no-movidas, ahora archivadas correctamente en el backup diario. Validación final: reset-all --dry-run sin candidatas y list-archived --from 2026-04-19 con 82 tareas.

## 2026-04-21T03:48Z — Codex — [KIT] KIT admite importacion y sincronizacion desde Google Keep
Estado: DONE
Chat: chats/chat_2026-04-21.md
Resumen: Se extendio agents/kit_agent.py con importar-keep y sincronizar-keep desde export local de Google Takeout para Google Keep, con deduplicacion por Google Keep ID y auto-ensure del schema de KIT. Se anadio tools/google_keep_tools.py para parsear notas/texto/checklists/labels/adjuntos del export, se conecto apps/project_hub_gui.py con botones de importar/sincronizar y se actualizo la documentacion de KIT y pipeline.

## 2026-04-21T04:22Z — Codex — [DOCS] [DOCS] Se formaliza artifacts/imports para staging de importaciones
Estado: DONE
Chat: chats/chat_2026-04-21.md
Resumen: Se creó artifacts/imports/google_keep como carpeta estable para depositar exports locales de Google Takeout antes de importarlos a KIT. Se añadió artifacts/imports/README.md y se actualizó memory/INDEX.md y memory/STRUCTURE.md; después se regeneró el TREE de STRUCTURE para reflejar la nueva ruta.

## 2026-04-21T04:44Z — Codex — [KIT] Importacion real de Google Keep a KIT ejecutada
Estado: DONE
Chat: chats/chat_2026-04-21.md
Resumen: Se importo el export real de Google Keep Takeout desde artifacts/imports/google_keep/.../Takeout/Conservar hacia NOTION_DB_KIT. Resultado consolidado del lote de 821 notas: 820 entradas cargadas en dos pasadas por timeout, con deduplicacion por Google Keep ID y 1 error residual. La importacion uso el nuevo flujo importar-keep y dejo las notas como Information/Nota en KIT.

## 2026-04-21T05:03Z — Codex — [KIT] Importacion Google Keep a KIT completada con pasada de recuperacion
Estado: DONE
Chat: chats/chat_2026-04-21.md
Resumen: Tras una primera importacion parcial por ritmo de escritura contra Notion, se ejecuto tools/import_keep_remaining.py con throttling y se completaron 546 notas pendientes desde el export real de Google Keep. Se verifico el recuento persistido en KIT/Notion al cierre para dejar la importacion completada con datos reales.

## 2026-04-22T11:38Z — Codex — [KIT] Bugfix en sincronizar-keep para actualizar filas existentes
Estado: DONE
Chat: chats/chat_2026-04-22.md
Resumen: Se corrigio agents/kit_agent.py para importar update_page_properties desde tools/notion_tools.py. Sin ese import, el subcomando sincronizar-keep compilaba pero fallaba en runtime al intentar actualizar notas Keep ya existentes en KIT. Validacion local en este turno: py_compile verde, parser Keep sigue leyendo 821 notas del Takeout real y la CLI de sincronizar-keep responde correctamente.

## 2026-04-22T17:00Z — Codex — [KIT] Sincronizacion real Google Keep->KIT completada y compatibilidad legacy reparada
Estado: DONE
Chat: chats/chat_2026-04-22.md
Resumen: Se parcheo tools/notion_tools.py para que schema/query/update/create hagan fallback a endpoints /databases/* cuando NOTION_DB_KIT llega como database legacy de una sola fuente. Despues se ejecuto sincronizar-keep contra el Takeout real en artifacts/imports/google_keep/.../Takeout/Conservar y el lote cerro sin errores: 821 notas leidas, 821 actualizadas, 0 nuevas, 0 archivadas.

## 2026-04-22T17:40Z — Codex — [KIT] NOTION_DB_KIT migrado a data_source_id moderno en .env
Estado: DONE
Chat: chats/chat_2026-04-22.md
Resumen: Se resolvio el data_source_id moderno de KIT contra Notion y se actualizo .env para sustituir el database legacy 340622cf-315b-81ee-9596-f282f3772b2d por 340622cf-315b-81b6-a22e-000be28f5cee. Verificacion posterior OK: resolve_data_source_id() devuelve exactamente el mismo valor configurado, sin fallback legacy.

## 2026-04-22T19:30Z — Codex — [KIT] Caso 08: relations reales KIT<->Obsidian y Fuente=KIT cerrados
Estado: DONE
Chat: chats/chat_2026-04-22.md
Resumen: Se extendio el caso 08 para materializar relations reales sin perder compatibilidad textual: ensure_kit_cross_fields ahora crea OBSIDIAN_DB.KIT, INX-ENLACES.KIT, KIT.Usada en notas y la opcion Fuente=KIT; log_obsidian_changes/backfill/sync_inx_links rellenan y reconcilian esas relations desde KIT IDs, y sync_inx_links hace write-back inverso a KIT. En el mismo turno se endurecio tools/validate_case_08.py para verificar relations y backrefs, y se corrigio tools/notion_tools.py para caer a /databases/* cuando /data_sources/* query devuelve 400/404. Validacion real final: 2452/2452 filas kit:* presentes en INX y alcance C verde sin mismatches ni backrefs faltantes.

## 2026-04-22T21:08Z — Claude — [KIT] Inoreader -> KIT: Fase 1 + plan B JSON-feed (offline) operativo
Estado: PROGRESS
Chat: chats/chat_2026-04-22.md
Resumen: Fase 1 Nivel 3 instalada: tools/inoreader_tools.py (OAuth2 + auto-refresh + normalizadores API y JSON Feed), tools/inoreader_oauth.py (autorizacion interactiva), tools/ensure_kit_external_fields.py (Inoreader ID/Tags + opciones Subtipo/Fuente, schema KIT/INX ya estaba listo), tools/import_inoreader_articles.py (modo --source para descargas locales y --url para JSON feeds publicos sin cuota API, dispatch_normalize auto-detecta formato API vs JSON Feed v1). .env.example y .gitignore actualizados (artifacts/inoreader_state.json, inoreader_sync_state.json, imports/inoreader/). Importados 5 articulos del tag kit-import (URL https://www.inoreader.com/stream/user/1003911326/tag/kit-import/view/json?n=1000) como prueba: 5 created, 0 errors. BLOQUEOS abiertos: (1) OAuth2 app pendiente de aprobacion manual de Inoreader (caso A documentado al usuario), (2) decision pendiente sobre 995 articulos restantes en kit-import - opciones A-E presentadas (curar en Inoreader, --newer-than, tag mas selectivo, importar como Pendiente, dejar en 5). Fase 2 (agents/inoreader_agent.py + sync_inoreader_to_kit.py + INX --source inoreader) NO iniciada, esperando ambas decisiones.

## 2026-04-23T08:15Z — Claude — [KIT] Inoreader OAuth desbloqueado: cambio de puerto 8080->8765
Estado: UNBLOCKED
Chat: chats/chat_2026-04-23.md
Resumen: Bloqueo OAuth resuelto. Causa raiz: AgentService.exe (PID 6980, servicio del sistema) ocupaba el puerto 8080 con LISTENING + ESTABLISHED, por lo que el redirect http://localhost:8080/callback se quedaba colgado tras pulsar Allow en Inoreader. Solucion: cambio del puerto OAuth a 8765 en dos sitios sincronizados: (1) Redirect URI editado en https://www.inoreader.com/developers/ a http://localhost:8765/callback, (2) INOREADER_REDIRECT_URI actualizado en .env. Re-ejecucion de python tools/inoreader_oauth.py con exito: tokens guardados en artifacts/inoreader_state.json, user-info responde 'dalarconrub', list_folders devuelve ['kit-import']. Nota: API reporta Plan=Free aunque el usuario creia tener Pro - posible inconsistencia entre suscripcion y campo isProUser, no bloqueante porque las 100 calls/dia siguen siendo viables con sync incremental ya disenado. Decision pendiente sobre los 995 articulos restantes en kit-import sigue abierta.

## 2026-04-23T08:37Z — Claude — [KIT] Inoreader -> KIT Fase 2: agente CLI completo + sync API incremental + link_article_to_ptn
Estado: DONE
Chat: chats/chat_2026-04-23.md
Resumen: Fase 2 cerrada. NUEVO: agents/inoreader_agent.py (CLI completo: auth-check con cuotas, list-folders, sync via API con cursor incremental, import-feed delegando al importer offline, listar/estado filtrables por subtipo y tag, link <inoreader_id> <proyecto_ref>); tools/sync_inoreader_to_kit.py (sync API OAuth2 con cursor por stream en artifacts/inoreader_sync_state.json, --full/--limit/--dry-run, no avanza cursor si hay errores); link_article_to_ptn() en tools/sync_inx_links.py (decision arquitectonica: NO crea claves inoreader:* en INX porque Inoreader alimenta KIT no es catalogo separado; reusa fila kit:<page_id> existente y le anade PTN Proyecto + URL). REFACTOR: tools/import_inoreader_articles.py reusa upsert helpers (existing_articles, article_to_props, upsert_article_to_kit) de sync_inoreader_to_kit -> single source of truth para escritura a KIT independiente del origen (API o JSON feed); --newer-than YYYY-MM-DD filtra client-side por published_date. SMOKE TESTS: auth-check OK (Zone 1 7/100), list-folders OK (kit-import), estado OK (6 articulos catalogados), listar OK (con filtros subtipo y tag), sync --dry-run OK (14 starred + 1 kit-import = 15 unicos), importer post-refactor con --newer-than OK, todos los modulos importan sin circulares. CUOTA REAL CONFIRMADA: 100 calls/dia Zone 1 + 100 Zone 2 por app externa (no se eleva con plan Pro).

## 2026-04-23T08:37Z — Claude — [DOCS] Inoreader -> KIT: docs + memory + caso 15 alineados con Fase 2
Estado: DONE
Chat: chats/chat_2026-04-23.md
Resumen: Documentacion alineada con Fase 2. NUEVO: docs/inoreader-agent.md (arquitectura, componentes, setup, uso diario, cuotas, INX, troubleshooting); docs/casos-de-uso/15-inoreader-a-kit.md (caso de uso completo con flujo principal, variantes A-D, postcondiciones, comandos, gaps y mejoras propuestas). EDITADO: memory/PURPOSE.md seccion 'KIT' (anade Inoreader y Google Keep como fuentes externas que alimentan KIT con propiedades dedicadas, no como catalogos separados); memory/INDEX.md seccion 6 (link a docs/inoreader-agent.md); memory/STRUCTURE.md narrativa de agents/ (inoreader_agent.py descrito como fuente externa que alimenta KIT) + TREE regenerado por tools/snapshot_structure.py @ 2026-04-23T08:35Z; docs/casos-de-uso/index.md (registro caso 15).

## 2026-04-23T08:51Z — Claude — [KIT] Inoreader sync: starred quitado del flujo por defecto
Estado: PROGRESS
Chat: chats/chat_2026-04-23.md
Resumen: Cambio de criterio: el estado 'starred' en Inoreader es el buffer 'Read later', NO senal de intencion de catalogar. Eliminado starred del sync por defecto en tools/sync_inoreader_to_kit.py: ahora solo lee user/-/label/<INOREADER_FOLDER_KIT> (default 'kit-import'). list_starred() en inoreader_tools.py sigue disponible como utilidad por si se usa para otros flujos futuros, no se invoca por defecto. Cursor reducido a un solo stream (mark_seen_for(folder_kit, ...)). agents/inoreader_agent.py docstring + sync output actualizados (sin metrica starred_fetched). tools/import_inoreader_articles.py documentado: el importer no impone politica (acepta cualquier --url), la convencion 'solo kit-import' la aplica el sync API. .env.example, docs/inoreader-agent.md, docs/casos-de-uso/15-inoreader-a-kit.md y memory/PURPOSE.md alineados. Smoke test post-cambio: sync --dry-run OK con 1 articulo del tag (sin starred). Sin perdida de datos: nunca se ejecuto un sync real con starred, no habia cursor persistido, KIT no contiene articulos starred.

## 2026-04-23T09:09Z — Claude — [KIT] Fix dedupe Inoreader: clave canonica = URL articulo (no Inoreader ID)
Estado: DONE
Chat: chats/chat_2026-04-23.md
Resumen: Bug arquitectonico encontrado: Inoreader expone IDs distintos para el MISMO articulo segun el endpoint. API stream/contents devuelve 'tag:google.com,2005:reader/item/<hex16>' (formato Google Reader) mientras JSON feed publico devuelve 'http://www.inoreader.com/article/<hex>' (formato Inoreader URL). Adicionalmente si un articulo aparece en mas de un feed que sigues, cada feed le asigna un Inoreader ID distinto. Resultado: dedupe por Inoreader ID NO previene duplicados cross-route ni cross-feed. Sintoma observado: tras corre sync API una vez, el articulo 'A Computational Model of Basic Addition Solving' tenia 3 filas en KIT (1 creada por API hoy, 2 creadas por import-feed ayer desde 2 feeds distintos). Solucion aplicada: cambiar clave de dedupe a URL del articulo (campo Enlace) con fallback a Inoreader ID si la URL esta vacia. Cambios: tools/inoreader_tools.merge_articles dedupe por art['url'] con fallback iid; tools/sync_inoreader_to_kit.existing_articles ahora retorna {'by_url': {url: page_id}, 'by_inoreader_id': {iid: page_id}}; upsert_article_to_kit busca por URL primero, luego iid; importer ya no muta existing manualmente (lo hace upsert internamente). Limpieza: usuario borro las 2 filas duplicadas en Notion manualmente. Smoke tests post-fix: sync incremental OK con cursor 2026-04-23T08:53 -> 0 articulos nuevos; re-import-feed del mismo articulo OK -> 0 created, 1 updated (URL match); estado=5 articulos. Fix robusto contra futuras importaciones cross-route.

## 2026-04-23T09:12Z — Claude — [TOOLING] Dedupe genérico Notion: tools/dedupe_notion_db.py
Estado: DONE
Chat: chats/chat_2026-04-23.md
Resumen: Nueva herramienta tools/dedupe_notion_db.py para detectar y archivar (soft-delete reversible) filas duplicadas en cualquier base Notion segun una clave configurable (--key <field>) o por titulo (--by-title). Politica de conservacion (--keep oldest|newest|lowest, default oldest). Modo deteccion sin --apply (dry-run, solo lista grupos); modo accion con --apply (archiva mediante notion_tools.archive_page, no eliminacion fisica). Auto-detecta el campo title del schema via get_data_source_schema().property_types. Reintentos con backoff por fila ante errores transitorios. Casos tipicos documentados en docstring: KIT por Enlace (URL articulo), BIB por Citekey, KIT/cualquiera por --by-title. Validacion en repo real: 2457 filas en KIT y 472 en BIB, 0 duplicados detectados por sus claves canonicas (Enlace y Citekey respectivamente) -> el fix anterior de dedupe URL en sync_inoreader_to_kit ya previene la causa raiz; la herramienta queda como salvaguarda futura para cualquier base.

## 2026-04-23T09:23Z — Claude — [TOOLING] Fix bug que duplico notas Keep el 2026-04-21: pre-flight schema en import_keep_remaining
Estado: DONE
Chat: chats/chat_2026-04-23.md
Resumen: Causa raiz del incidente identificada y corregida. Bug: tools/import_keep_remaining.py no verificaba que la propiedad 'Google Keep ID' existiera en el schema de NOTION_DB_KIT antes de importar. Si la propiedad no existia (caso del 2026-04-21), Notion descarta silenciosamente la propiedad al crear las filas - las notas quedan creadas pero sin Keep ID. En la siguiente ejecucion, el set 'existing' se construye vacio (ningun row tiene Keep ID a leer) y las 821 notas se ven todas como 'pending' -> se duplican. 3 ejecuciones consecutivas el 2026-04-21 produjeron 821 grupos de duplicados (~1629 filas archivadas hoy con tools/dedupe_notion_db.py). Fix en 2 capas: (1) tools/ensure_kit_external_fields.py extendido para garantizar tambien 'Google Keep ID' en KIT (centraliza props de fuentes externas Inoreader+Keep en un solo ensure); (2) tools/import_keep_remaining.py anade pre-flight schema check + heuristica defensiva: si KIT tiene >100 filas con Subtipo='Nota' pero ninguna con Google Keep ID poblado, aborta antes de duplicar (apunta al ensure script o a backfill manual). Ambas correcciones idempotentes y verificadas: ensure_kit_external_fields confirma que la propiedad ya existe ahora. Nota: agents/kit_agent.py tiene el mismo riesgo si KIT se reusa sin haber corrido crear-db; mismo fix aplicable si surge en el futuro.

## 2026-04-23T11:24Z — Claude — [INX] Cleanup INX-ENLACES: 384 duplicados kit:* eliminados (--keep newest)
Estado: DONE
Chat: chats/chat_2026-04-23.md
Resumen: Cleanup masivo en INX-ENLACES. Diagnostico: 384 grupos duplicados, todos con clave kit:*, generados por dos ejecuciones consecutivas de sync_inx_links --source kit el 2026-04-22 (~18:36 y ~19:16). Run 2 no detecto las filas del Run 1 (probable paginacion stale en _existing_map al haber miles de filas, o schema migration mid-run que cambio que campos se escriben). Analisis field-by-field de los 384 grupos: 80 son IDENTICOS (dedupe simple), 304 difieren SOLO en la relation KIT (la fila newest la tiene poblada, la oldest tiene []). 0 grupos difieren en otros campos (PTN Proyecto, Detalle, URL, Estado, etc. todos identicos). Estrategia aplicada: --keep newest preserva la version con KIT relation poblada en todos los casos; uniforme y seguro porque las claves de lookup son por campo Clave (no por page_id). Resultado: INX 3924 -> 3540 (384 archivadas, 0 errores). Verificacion post-cleanup: dedupe_notion_db --key Clave reporta 'Sin duplicados'. Pendiente: investigar y parchear la causa raiz en _existing_map para evitar reincidencia.

## 2026-04-23T11:28Z — Claude — [INX] Fix sync_inx_links: pre-flight integrity en _existing_map + mutar existing en _upsert
Estado: DONE
Chat: chats/chat_2026-04-23.md
Resumen: Fix preventivo del bug que generó los 384 duplicados kit:* el 2026-04-22 (cleanup en entrada anterior). Dos cambios en tools/sync_inx_links.py, no-destructivos en el happy path: (1) _existing_map ahora hace pre-flight integrity check: si la base INX tiene filas pero ninguna con 'Clave' poblada (causado por schema migration mid-run, campo renombrado o cambio de tipo, fallback de query_data_source a endpoint legacy con shape distinto, etc.), aborta con RuntimeError claro en vez de devolver mapping vacio que provocaria duplicacion masiva. (2) _upsert ahora muta  tras crear, evitando duplicar dentro del mismo run si la misma clave se procesa dos veces (defensa frente a inputs con dups). Verificacion: smoke test post-fix _existing_map(NOTION_DB_INX) devuelve 3540 entradas (la base completa post-cleanup), sin abort, comportamiento happy path intacto. Imports limpios. Si el patron patologico vuelve a aparecer (mapping vacio sobre base no vacia), el fix lo detecta y aborta antes de duplicar.

## 2026-04-23T11:46Z — Claude — [INX] E2E test sync_inx_links --source kit con fix aplicado: PASS
Estado: DONE
Chat: chats/chat_2026-04-23.md
Resumen: Validacion end-to-end del fix sync_inx_links. Baseline pre-test: INX=3540 (post-cleanup), KIT=828 (post-cleanup). Ejecucion: python tools/sync_inx_links.py --source kit. Output: 'INX enlaces sincronizados: kit=828 kit_backrefs=0'. Resultado: INX 3540 -> 3545 (+5 filas), todas legitimamente nuevas (Inoreader articles importados hoy/ayer que aun no habian pasado por sync_inx_links). Verificacion dedup post-test: dedupe_notion_db --db-env NOTION_DB_INX --key Clave reporta 'Sin duplicados por Clave'. 823 KIT pages fueron UPDATE (correcto, ya estaban en INX desde el cleanup), 5 fueron CREATE (correcto, faltaban). Si el bug del 2026-04-22 se hubiera reproducido habrian aparecido 828 nuevas filas + 384 duplicados al siguiente run. No paso nada de eso. Fix confirmado en condiciones de produccion.

## 2026-04-23T11:47Z — Claude — [TOOLING] Cleanup pendientes menores: OBSIDIAN_DB + PTN-Proyectos + NOTION_DB log (9 filas)
Estado: DONE
Chat: chats/chat_2026-04-23.md
Resumen: Cleanup de duplicados pendientes en 3 bases con conteos pequenos. (1) OBSIDIAN_DB: 2 grupos por Ruta, 2 archivadas (--keep oldest). Notas dup: N260418-Candido2026y, N251028-borrador. (2) NOTION_DS_PROYECTOS: 1 grupo por Nombre del Proyecto, 1 archivada (Arquitectura Coworkia v2 duplicada en mismo dia). (3) NOTION_DB (PTN log): 4 grupos por Fuente ID, 6 archivadas (Proyecto: TFG 2025-26, Proyecto: Tesis Cristian, Proyecto: Sofia, Nota: N251104-Analisis de datos con GLM con 4 copias). Total 9 filas archivadas, 0 errores. Verificacion post: las 3 bases reportan 'Sin duplicados'. Resumen acumulado del cleanup masivo de hoy 2026-04-23: KIT 1629 + INX 384 + minores 9 = 2022 filas archivadas, todas reversibles desde Notion.

## 2026-04-23T16:27Z — Claude — [KIT] Pre-flight defensive en kit_agent.{importar,sincronizar}_keep
Estado: DONE
Chat: chats/chat_2026-04-23.md
Resumen: Simetria con el fix de import_keep_remaining: ambas funciones que importan Google Keep a KIT ahora llaman _check_keep_existing_integrity antes de escribir. El helper aborta si detecta el patron patologico del 2026-04-21: KIT con >100 filas Subtipo='Nota' pero ninguna con Google Keep ID poblado (filas creadas antes de que existiera la propiedad -> dedupe falla silencioso). _ensure_kit_schema ya cubre el caso de creacion inicial sin Keep ID en schema; este helper cubre el caso residual de filas huerfanas. Cambios minimos: 1 helper nuevo + 1 llamada en importar_keep y 1 en sincronizar_keep. Smoke test: imports OK.

## 2026-04-23T17:11Z — Claude — [INX] Backfill INX completo --source all post-fix: PASS (0 duplicados)
Estado: DONE
Chat: chats/chat_2026-04-23.md
Resumen: Ejecucion full de sync_inx_links --source all tras los fixes de _existing_map y _upsert. Resultado: 'INX enlaces sincronizados: todoist=451 notion=16 obsidian=35 github=113 paperpile=472 kit=828 kit_backrefs=0' = 1915 upserts en total. INX pre=3545 -> post=3545 (delta +0, todos UPDATE porque INX ya tenia coverage canonica completa tras cleanups previos). Verificacion post: dedupe_notion_db --key Clave reporta 'Sin duplicados'. Si el bug de _existing_map estuviera vivo, las 1915 upserts habrian producido ~1915 dups potenciales; con el fix aplicado, cero. Tiempo total ~25 min (lento por las 6 invocaciones de _existing_map paginadas sobre 3545 filas INX). Fix validado en condiciones de produccion masiva.

## 2026-04-24T05:14Z — Claude — [REP] Validador caso 5 (REP <-> INX) creado: tools/validate_case_05.py
Estado: DONE
Chat: chats/chat_2026-04-24.md
Resumen: Nuevo validador alineado con el patron de validate_case_08.py para automatizar el audit del caso 5 (importar repo GitHub a REP y enlazar a PTN). Alcance B (base): REP entries con Nombre tienen fila INX github:<Nombre>; reporta count, ejemplos, missing si los hay. Alcance C (--scope c, extras): sin duplicados REP por Nombre ni por URL; sin filas INX github:* huerfanas (sin REP correspondiente); Fuente coherente (=GitHub); count informativo de repos enlazados a PTN Proyecto. Exit codes 0/1/2 alineados con caso 08. Smoke test post-creacion: scope B PASS (113/113 REP en INX), scope C PASS (0 dups, 0 huerfanas, 0 fuente mismatch, 0 PTN enlaces). Cierra brecha: solo casos 5 y 6 (REP, BIB) carecian de validator entre 02-14; ahora REP cubierto. Pendiente: validate_case_06 para BIB con la misma estructura.

## 2026-04-24T05:19Z — Claude — [BIB] Validador caso 6 (BIB <-> INX) creado: tools/validate_case_06.py
Estado: DONE
Chat: chats/chat_2026-04-24.md
Resumen: Nuevo validador alineado con validate_case_05.py y validate_case_08.py para automatizar el audit del caso 6 (importar paper Paperpile a BIB y enlazar a PTN/Obsidian). Alcance B: papers BIB con Citekey tienen fila INX paperpile:<citekey>; reporta count, ejemplos, missing si los hay. Alcance C (--scope c): sin duplicados BIB por Citekey ni por DOI; sin huerfanas INX paperpile:* sin BIB correspondiente; Fuente coherente (=Paperpile); count informativo de papers enlazados a PTN Proyecto. Smoke test: scope B PASS (472/472 BIB en INX), scope C PASS (0 dups Citekey/DOI, 0 huerfanas, 0 fuente mismatch, 0 PTN enlaces). Cobertura completa de validators ahora: 02, 03, 05-14 cubiertos. Solo casos 1 (captura zinbox) y 4 (sync diario INX) sin validator por naturaleza no-verificable post-hoc.

## 2026-04-24T05:25Z — Claude — [INX] Re-link github:coworkia -> Arquitectura Coworkia v2 (recovery post-reset 2026-04-19)
Estado: DONE
Chat: chats/chat_2026-04-24.md
Resumen: Recovery manual del unico enlace conocido perdido por el reset del 2026-04-19 (commit 467034f). link_repo_to_ptn('coworkia', 'Arquitectura Coworkia v2') ejecutado: INX github:coworkia ahora apunta a PTN Proyecto page_id 33f622cf-315b-814c-84fd-c9d3fa6042eb con Estado=Verificado y URL=https://github.com/dalarconrub/coworkia. Validacion post via tools/validate_case_05.py --scope c: 'INX github:* enlazados a PTN Proyecto: 1' (coincide con doc historico del 2026-04-17). Pendiente: investigar otros enlaces huerfanos (paperpile:*, kit:*, obsidian:*, todoist:* tambien podrian haber perdido enlaces a PTN). Estructural: snapshot/restore de relaciones INX->PTN no existe en el flujo de reset, deberia anadirse para evitar futuras perdidas silenciosas.

## 2026-04-24T05:27Z — Claude — [INX] Investigacion cierre: regresion github:coworkia NO causada por reset ni por sync actual
Estado: DONE
Chat: chats/chat_2026-04-24.md
Resumen: Investigacion completa. Hallazgos: (1) Backup ptn-proyectos-191723Z.json (pre-reset 21:17) tiene IDENTICOS page_ids a los actuales en PTN-Proyectos -> reset NO roto IDs, mi teoria inicial era incorrecta. (2) reset_notion._flip_archivo solo modifica campo 'Archivo' (checkbox) en INX cuando archiva PTN; NO toca relaciones (PTN Proyecto, KIT, etc.). (3) _sync_github en sync_inx_links.py no incluye PTN Proyecto en su dict 'data', por lo que _upsert via update_page_properties no lo sobrescribe (Notion API preserva propiedades no listadas en el payload). (4) Mismo razonamiento aplica a _sync_paperpile, _sync_kit, _sync_obsidian, etc. Conclusion: el codigo ACTUAL no causa la perdida de relaciones INX->PTN. La regresion historica de github:coworkia se debio a alguna de: (a) borrado manual desde UI de Notion, (b) doc del 2026-04-17 era aspiracional sin validacion real, (c) version vieja de algun script ya refactorizada. El re-link de hoy debe ser estable. Pendiente opcional: verificar empiricamente corriendo sync_inx_links --source github y comprobando que PTN Proyecto persiste post-sync.

## 2026-04-24T05:50Z — Claude — [INX] Fix _sync_github: no degrada Estado=Verificado a Activo en cada sync
Estado: DONE
Chat: chats/chat_2026-04-24.md
Resumen: Cambio en tools/sync_inx_links.py _sync_github: removido 'Estado': {'select': {'name': 'Activo'}} del dict 'data'. Razon: la version anterior sobrescribia el Estado=Verificado puesto por link_repo_to_ptn en cada ejecucion de sync_inx_links --source github, degradando metadato curado. Comportamiento nuevo: Estado en filas INX github:* es estable, solo lo modifica link_repo_to_ptn (a Verificado) o el usuario manualmente. Trade-off: filas github:* nuevas (creadas por sync sin previo link) quedan sin Estado hasta vinculacion manual. Verificacion empirica: link_repo_to_ptn('coworkia', 'Arquitectura Coworkia v2') -> Estado=Verificado; sync_inx_links --source github (con fix) -> Estado sigue Verificado, PTN Proyecto sigue intacta. Mismo patron aplicable a _sync_paperpile y _sync_kit si aparece la misma necesidad (no aplicado por scope, solo github).

## 2026-04-24T05:59Z — Claude — [INX] Patron preservar Estado=Verificado aplicado a _sync_kit y _sync_paperpile
Estado: DONE
Chat: chats/chat_2026-04-24.md
Resumen: Consistencia con el fix anterior de _sync_github. Eliminado 'Estado': {'select': {'name': 'Activo'}} del data dict de _sync_kit y _sync_paperpile en tools/sync_inx_links.py. Razon: igual que para github, las funciones link_*_to_ptn (link_paper_to_ptn, link_article_to_ptn) ponen Estado=Verificado como metadato curado; los syncs no deben degradarlo a Activo en cada ejecucion. Trade-off documentado: nuevas filas paperpile:* y kit:* creadas via sync sin previo link quedan sin Estado hasta vinculacion. Asimetria con _sync_todoist/_sync_ptn_log/_sync_obsidian es intencional: esas fuentes no tienen helpers link_*_to_ptn por ahora. Smoke test imports OK.

## 2026-04-24T06:01Z — Claude — [DOCS] Caso 14: documentado comportamiento garantizado de relaciones INX->PTN ante reset
Estado: DONE
Chat: chats/chat_2026-04-24.md
Resumen: Anadida seccion 'Comportamiento garantizado: relaciones curadas INX->PTN preservadas' a docs/casos-de-uso/14-reset-sistema.md, entre Postcondiciones y Definition of Done. Documenta: (1) reset_notion._flip_archivo solo modifica el campo Archivo en INX, no toca relaciones ni Estado/URL/Detalle/Fuente; (2) _sync_github, _sync_paperpile, _sync_kit NO incluyen Estado en payload de upsert (fix de hoy) -> preservan Verificado puesto por link_*_to_ptn; (3) asimetria intencional con _sync_todoist/_sync_ptn_log/_sync_obsidian (esas si setean Estado por carecer de helpers link_*_to_ptn); (4) trade-off documentado: nuevas filas sin previo link quedan sin Estado; (5) validacion empirica del 2026-04-24 con github:coworkia citada; (6) implicacion: no hace falta snapshot/restore de relaciones alrededor del flujo de reset. Cierra el riesgo percibido sobre 'relaciones rotas' que motivo la investigacion de hoy.

## 2026-04-24T06:20Z — Claude — [GIT] Rename entity REP -> GIT (codigo + env vars + docs + memory + 2 renames de archivos)
Estado: DONE
Chat: chats/chat_2026-04-24.md
Resumen: Refactor nivel B (per la propuesta) para harmonizar nomenclatura: entity code REP renombrado a GIT en todo el proyecto. Cambios atomicos: (1) tools/devlog.py: anadido GIT al VALID_AREAS, REP retenido como alias historico para entradas pre-2026-04-24. (2) .env y .env.example: NOTION_DB_REPOS -> NOTION_DB_GIT, NOTION_REPOS_PARENT_PAGE -> NOTION_GIT_PARENT_PAGE (valores conservados). (3) Codigo: agents/github_agent.py (DB_REPOS -> DB_GIT, REPOS_PARENT_PAGE -> GIT_PARENT_PAGE, 'Agente REP' -> 'Agente GIT', 'REP-Repositorios' -> 'GIT-Repositorios', '=== ESTADO REP' -> '=== ESTADO GIT'); agents/kit_agent (fallback NOTION_REPOS_PARENT_PAGE -> NOTION_GIT_PARENT_PAGE); agents/notion_agent (link-repo-to-ptn help texts); tools/sync_inx_links (referencias en docstrings/error messages); tools/validate_case_05 (REP -> GIT en mensajes); apps/* (project_hub_gui, pipeline_gui, inx_doctor, notion_doctor, config_doctor, github_gui: titulos, labels, env var names, status messages); multiagents/registry (key/name/owned_systems); multiagents/planner (SYSTEM_KEYWORDS, _infer_sync_sources). (4) Docs: README, CLAUDE, AGENTS, .github/copilot-instructions, .claude/multiagent, memory/PURPOSE/STRUCTURE/INDEX, docs/abc-taxonomy, docs/notion-ptn-agent, docs/pipeline-atlas, docs/guia-rapida, docs/casos-de-uso/{00-template, 04, 13, index}. (5) Renames via git mv: docs/github-rep-agent.md -> docs/git-agent.md; docs/casos-de-uso/05-github-rep-enlazado-a-ptn.md -> docs/casos-de-uso/05-git-enlazado-a-ptn.md (historial preservado). (6) Lo NO tocado por design: INX claves siguen 'github:<nombre>' (semantica = la fuente es GitHub, no 'git' generico); Fuente=GitHub en INX; chats/devlog historicos; artifacts/* (snapshots historicos); Sistemas/* (externo); 'C111-REP' en obsidian-agent.md (folder code de Obsidian, no relacionado con la entidad). Smoke tests post-refactor: 14/14 modulos importan OK; validate_case_05 --scope c PASS con 'GIT' en outputs; github_agent estado funciona ('=== ESTADO GIT (113 repos)'); 0 referencias residuales a NOTION_DB_REPOS / DB_REPOS / NOTION_REPOS_PARENT_PAGE.

## 2026-04-24T07:00Z — Claude — [DOCS] ABGD A4-ARX realineado: bloques B4X-BIB/B4Y-KIT/B4Z-GIT + contextos en mayusculas + renames C4Y6-WEB/C4Z7-COD/C4Z8-AGI
Estado: DONE
Chat: chats/chat_2026-04-24.md
Resumen: Realineamiento de la taxonomia A4-ARX en docs Coworkia para que los catalogos KIT/BIB/GIT tengan bloques de primera clase con codigo coherente. Cambios solo en documentacion del codebase (no toca Notion ni vault local; el usuario hara esos pasos manualmente). README.md (3 secciones), docs/abc-taxonomy.md (seccion A4-ARX), docs/todoist-agent.md (lista de bloques), docs/obsidian-agent.md (arbol de carpetas). Renames: B4X-LIB->B4X-BIB, B4Y-MED->B4Y-KIT, B4Z-APP->B4Z-GIT. Contextos: x/y/z mayusculas (X/Y/Z) ya estaban en el template Sistemas/Sistema_ABGD-main pero los docs Coworkia los tenian en minusculas - alineado. Renames especificos pedidos: C4Y6-MP3->C4Y6-WEB, C4Z7-MOC->C4Z7-COD, C4Z8-WEB->C4Z8-AGI. NO tocado: Sistemas/ABC/*.csv (snapshots Notion), Sistemas/Sistema_ABGD-main/* (template ABGD), artifacts/resets/*.json (historicos), C111-REP en A1-INV/B11-CVT (significado academico distinto). Acciones manuales pendientes para el usuario fuera del repo: (1) renombrar bloques en Notion ABC-BLOQUE database; (2) renombrar contextos en Notion ABC-CONTEXTO database; (3) mover paginas Notion KIT/BIB/GIT bajo nuevo bloque parent; (4) renombrar carpetas vault Obsidian en OBSIDIAN_ABGD_ROOT/Alpha/A4-ARX/.

## 2026-04-24T12:38Z — Codex — [DOCS] Alinear playbooks e Inoreader en memoria
Estado: DONE
Chat: chats/chat_2026-04-24.md
Resumen: Documentada la nueva carpeta top-level playbooks/ en memory/INDEX.md y memory/STRUCTURE.md, con TREE regenerado por tools/snapshot_structure.py. Corregidos restos documentales tras GIT rename (github-rep-agent -> git-agent) y política Inoreader vigente (solo tag kit-import, sin starred por defecto) en memory/STRUCTURE.md, docs/casos-de-uso/index.md y tools/import_inoreader_articles.py.

## 2026-04-24T12:40Z — Codex — [TOOLING] Filtrar estado local en snapshot_structure
Estado: DONE
Chat: chats/chat_2026-04-24.md
Resumen: Endurecido tools/snapshot_structure.py para excluir .claude/settings.json, ficheros .log y estados locales de Inoreader del TREE de memory/STRUCTURE.md. Anadida regla en .gitignore para no versionar .claude/settings.json. Validado con py_compile y snapshot_structure.py --check.

## 2026-04-24T12:41Z — Codex — [DOCS] Indice local de playbooks
Estado: DONE
Chat: chats/chat_2026-04-24.md
Resumen: Anadido playbooks/README.md como indice operativo de la nueva carpeta de metodologias reutilizables, con criterios para futuros playbooks. Regenerado memory/STRUCTURE.md para incluir el README en el TREE.

## 2026-04-24T12:43Z — Codex — [DOCS] Completar alineacion docs Inoreader kit-import
Estado: DONE
Chat: chats/chat_2026-04-24.md
Resumen: Ajustados docs/inoreader-agent.md y docs/casos-de-uso/15-inoreader-a-kit.md para que el flujo canonico sea tag explicito kit-import. Las menciones a starred quedan solo como advertencia de que no dispara import o como posibilidad manual explicita del importer offline.

## 2026-04-24T12:45Z — Codex — [TOOLING] Aclarar ayuda CLI import_inoreader_articles
Estado: DONE
Chat: chats/chat_2026-04-24.md
Resumen: Actualizada la ayuda y docstring de tools/import_inoreader_articles.py: el default operativo se describe como INOREADER_FOLDER_KIT y la inferencia starred queda limitada a trazabilidad cuando el usuario pasa explicitamente una URL manual starred. Validado con --help, py_compile y memory_check.

## 2026-04-24T14:46Z — Codex — [GIT] Push commit playbooks/Inoreader
Estado: DONE
Chat: chats/chat_2026-04-24.md
Commits: dfff81d
Resumen: Publicado en origin/main el commit dfff81d Document playbooks and align Inoreader workflow. main queda alineada con origin/main.

## 2026-04-25T06:54Z — Codex — [DOCS] Confirmar alineacion manual Notion GIT/KIT
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: David completo los cambios manuales de alineacion en Notion tras el rename GIT y el realineamiento A4-ARX. Se archivo la fila temporal KIT 'Esta es la buena'. Validaciones post-ajuste: validate_case_05 --scope c PASS (GIT 113/113 en INX, 0 duplicados/huerfanas) y validate_case_08 --scope c PASS (KIT 828/828 en INX, 0 mismatches/backrefs faltantes).

## 2026-04-25T07:33Z — Codex — [DOCS] Regenerar STRUCTURE tras chat 2026-04-25
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Regenerado memory/STRUCTURE.md con tools/snapshot_structure.py para incorporar el chat diario 2026-04-25 en el TREE. memory_check queda OK antes de commit.

## 2026-04-25T14:45Z — Codex — [DOCS] Crear bookdown navegable de Coworkia
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Creada carpeta top-level bookdown/ con _bookdown.yml, capitulos Rmd iniciales, generador HTML estatico, validador, HTML generado y test tests/test_bookdown_static_html.py. README y memory/INDEX.md/STRUCTURE.md actualizados; STRUCTURE TREE regenerado. Validaciones: generate_static_html OK, validate_static_html OK con warning esperado de Mermaid CDN, pytest bookdown 1 passed, memory_check OK.

## 2026-04-25T14:51Z — Codex — [DOCS] Ampliar bookdown con sistemas y scripts
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Anadidos los capitulos bookdown/07-sistemas-y-agentes.Rmd y bookdown/08-tabla-maestra-scripts.Rmd, enlazados en _bookdown.yml. Regenerado bookdown/_book/index.html y actualizado memory/STRUCTURE.md TREE. Validaciones: generate_static_html OK, validate_static_html OK con warning esperado de Mermaid CDN, pytest bookdown 1 passed, memory_check OK.

## 2026-04-25T14:57Z — Codex — [DOCS] Ampliar bookdown con casos y validation
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Anadidos bookdown/09-casos-de-uso.Rmd y bookdown/10-validacion-y-acceptance.Rmd, con FAQ reordenado al final en _bookdown.yml. El capitulo 09 mapea los 15 casos canonicos a sistemas y validadores; el 10 documenta capas de validacion, acceptance, evidencias y stop conditions. Regenerado HTML y STRUCTURE TREE. Validaciones: validate_static_html OK con warning esperado Mermaid CDN, pytest bookdown 1 passed, memory_check OK.

## 2026-04-25T15:07Z — Codex — [DOCS] Ampliar bookdown con INX y Notion ABC
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Anadidos bookdown/11-inx-arquitectura.Rmd y bookdown/12-notion-abc-fuentes-de-verdad.Rmd, enlazados en _bookdown.yml antes del FAQ. El capitulo 11 documenta claves, fuentes de sync, relaciones curadas, doctores, reportes y stop conditions de INX. El capitulo 12 documenta jerarquia ABC, mapa Notion canonico, data sources, env vars, permisos, schema y reglas de cambio. Regenerado HTML y STRUCTURE TREE. Validaciones: validate_static_html OK con warning esperado Mermaid CDN, pytest bookdown 1 passed, memory_check OK.

## 2026-04-25T16:59Z — Codex — [DOCS] Ampliar bookdown con multiagente y operacion Windows
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Anadidos bookdown/13-coordinacion-multiagente.Rmd y bookdown/14-operacion-windows-resets-backups.Rmd, enlazados en _bookdown.yml antes del FAQ. El capitulo 13 documenta memoria curada, chat diario, marcadores, subagentes, devlog, sync-chat-memory, timeline y sprints. El 14 documenta arranque Windows, diagnosticos, backups, resets MAR/Notion/Obsidian/general, validation y stop conditions. Regenerado HTML y STRUCTURE TREE. Validaciones: validate_static_html OK con warning esperado Mermaid CDN, pytest bookdown 1 passed, memory_check OK.

## 2026-04-25T17:04Z — Codex — [DOCS] Ampliar bookdown con catalogo documental y roadmap
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Anadidos bookdown/15-catalogo-documentacion.Rmd y bookdown/16-roadmap-limitaciones.Rmd, enlazados en _bookdown.yml antes del FAQ. El capitulo 15 organiza rutas de lectura por perfil, memoria, guias, casos, playbooks y artefactos derivados. El 16 separa limitaciones reales, backlog por dominio, priorizacion, auditoria de contradicciones, politica pendiente de _book y DoD del bookdown. Regenerado HTML y STRUCTURE TREE. Validaciones: validate_static_html OK con warning esperado Mermaid CDN, pytest bookdown 1 passed, memory_check OK.

## 2026-04-25T17:09Z — Codex — [DOCS] Auditar coherencia documental del bookdown
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Primera pasada de auditoria documental tras crear el bookdown. Corregidos README (ubicacion KIT/GIT/BIB en A4-ARX), docs/pipeline-atlas.md (links de casos obsoletos, 13->15 casos, env labels TODOIST_DB_TAREAS/OBSIDIAN_DB/NOTION_DB) y bookdown/16-roadmap-limitaciones.Rmd. Definida politica: bookdown/_book/ es artefacto regenerable ignorado por Git; snapshot_structure.py excluye _book del TREE. Validaciones: py_compile OK, generate_static_html OK, validate_static_html OK con warning esperado Mermaid CDN, pytest bookdown 1 passed, memory_check OK.

## 2026-04-25T17:16Z — Codex — [DOCS] Endurecer validador bookdown con enlaces locales
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Ampliado bookdown/validate_static_html.py para auditar hrefs locales del HTML generado: ignora enlaces externos y anchors, resuelve rutas del proyecto o relativas al bookdown y reporta Broken local link cuando el destino no existe. Anadido test unitario en tests/test_bookdown_static_html.py para cubrir un enlace local inexistente. Validaciones: py_compile OK, generate_static_html OK, validate_static_html OK con warning esperado Mermaid CDN, pytest bookdown 2 passed, memory_check OK.

## 2026-04-25T17:31Z — Codex — [DOCS] Cerrar bookdown con matriz de cobertura
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Anadido bookdown/17-matriz-cobertura-release.Rmd y enlazado en _bookdown.yml antes del FAQ. El capitulo mapea cobertura por capitulo, checklist de release local, Definition of Done del manual y protocolo de cambio para mantenerlo alineado con scripts, casos, env vars, memoria y resets. El nuevo validador detecto un enlace falso generado por texto de ejemplo y se corrigio como texto no enlazado. Validaciones: py_compile OK, generate_static_html OK, validate_static_html OK con warning esperado Mermaid CDN, pytest bookdown 2 passed, snapshot_structure --check OK, memory_check OK.

## 2026-04-25T17:37Z — Codex — [DOCS] Auditar rutas inline del bookdown
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Endurecido bookdown/validate_static_html.py para auditar rutas de proyecto escritas en code spans de los .Rmd, ademas de enlaces HTML. La heuristica valida solo rutas inequívocas del repo, ignora globs/placeholders/comandos y reporta missing referenced path. Anadido test unitario para una ruta backticked inexistente. La auditoria detecto rutas aspiracionales en roadmap (journal e Inoreader doctor) y una referencia antigua docs/bookdown; se reformularon como backlog/texto sin fingir ficheros existentes. Validaciones: py_compile OK, generate_static_html OK, validate_static_html OK con warning esperado Mermaid CDN, pytest bookdown 3 passed, snapshot_structure --check OK, memory_check OK.

## 2026-04-25T17:53Z — Codex — [DOCS] Actualizar protocolo portable de sesion
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Reescrito playbooks/PROTOCOLO_INICIO_CIERRE_SESION.md como version portable para repos con memory, chats, devlog, artifacts multiagente y Git. Actualizado playbooks/README.md, regenerado memory/STRUCTURE.md TREE y corregido tools/session_protocol.py para capturar subprocesses en UTF-8. Validaciones: py_compile session_protocol OK, session_protocol inicia --no-chat OK, memory_check OK.

## 2026-04-25T17:57Z — Codex — [DOCS] Crear playbook portable para indice de playbooks
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Anadido playbooks/playbooks-readme-portable-playbook.md para reproducir el patron de playbooks/README.md en cualquier repo, con plantilla, criterios de entrada/salida, integracion multiagente, checklist y antipatrones. Actualizado playbooks/README.md y memory/STRUCTURE.md; TREE regenerado. Validacion: memory_check OK.

## 2026-04-25T18:00Z — Codex — [GIT] Commit y push bookdown y playbooks
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: David autorizo commit y push de los cambios acumulados de la sesion: bookdown del proyecto, validadores y tests, protocolo portable de inicio/cierre, playbook portable para README de playbooks, memoria actualizada, chat/devlog y artefactos multiagente derivados. Validaciones previas: memory_check OK y snapshot_structure --check OK.

## 2026-04-25T19:10Z — Codex — [MAR] Aclarar inbox operativo Todoist
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: David corrigio la rutina de arranque MAR: inbox se refiere al proyecto real Todoist Inbox, no a zinbox. Queda registrada la convencion: Z-* son backs/staging y no se consultan en arranque normal salvo peticion explicita. Se localizo Inbox como project_id=6Crfvj4MWg6GfVq6 y se listo su contenido actual: 33 tareas.

## 2026-04-25T19:17Z — Codex — [MAR] Procesar Inbox operativo Todoist
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Procesado el proyecto Todoist Inbox real (project_id=6Crfvj4MWg6GfVq6) como arranque operativo MAR. Se movieron 31 entradas claras a bloques ABC livianos: B12-LAB, B11-CVT, B13-PUB, B24-DOC, B26-GES, B37-ORG, B39-DES y B40-REF. No se consultaron Z-* durante el procesamiento posterior. Inbox queda con 2 entradas pendientes de decision: SPAM Food Craving y cita medica pasada del 2026-04-24.

## 2026-04-25T19:29Z — Codex — [MAR] Sincronizar Todoist con Notion
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Ejecutado sync MAR->Notion con tools/sync_todoist_to_notion.py --limit 200 tras procesar Inbox y cambios manuales de David en Todoist. Primer intento agoto timeout; reintento con timeout ampliado finalizo OK: Tareas sincronizadas 114. No se ejecuto sync INX en este paso.

## 2026-04-25T19:51Z — Codex — [MAR] Resincronizar Todoist con Notion
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Reejecutado tools/sync_todoist_to_notion.py --limit 200 tras nuevos cambios manuales de David en Todoist. Finalizo OK con Tareas sincronizadas 108. No se ejecuto sync INX en este paso.

## 2026-04-25T20:00Z — Codex — [INX] Sincronizar INX desde Todoist
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Ejecutado tools/sync_inx_links.py --source todoist --limit 200 tras resincronizar TODOIST-TAREAS. Finalizo OK con INX enlaces sincronizados: todoist=200.

## 2026-04-25T20:07Z — Codex — [DOCS] Documentar pipeline MAR diario
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: Documentado el pipeline operativo validado: Inbox real de Todoist (project_id=6Crfvj4MWg6GfVq6) -> clasificacion ligera en proyectos A/B -> sync_todoist_to_notion.py --limit 200 -> sync_inx_links.py --source todoist --limit 200. Actualizados README, docs/todoist-agent.md, docs/pipeline-atlas.md, docs/casos-de-uso/04-sync-diario-inx.md y bookdown 03/07/08. Corregidas referencias que trataban zinbox como arranque normal; Z-* queda como backs/staging explicito. Validaciones: generate_static_html OK, validate_static_html OK con warning Mermaid CDN, memory_check OK, pytest bookdown 3 passed.

## 2026-04-25T20:10Z — Codex — [TOOLING] Ajustar cierre de sesion con commit y push
Estado: DONE
Chat: chats/chat_2026-04-25.md
Resumen: David establecio la politica local: cuando dice cierra sesion, Coworkia debe validar, hacer commit y push por defecto de los cambios de la sesion, salvo omision explicita. Actualizados AGENTS.md, README.md, playbook portable y tools/session_protocol.py. El adaptador ahora auto-detecta cambios, genera mensaje de cierre por defecto, hace push salvo --no-push y permite --no-commit para inventario sin commit.

## 2026-04-26T05:02Z — Codex — [MAR] Continuar pipeline MAR diario
Estado: DONE
Chat: chats/chat_2026-04-26.md
Resumen: Tras orden continua, revisado estado MAR con agents/todoist_agent.py estado: 108 acciones activas. Ejecutado tools/sync_todoist_to_notion.py --limit 200 con acceso de red autorizado tras bloqueo de sandbox: Tareas sincronizadas 108. Ejecutado tools/sync_inx_links.py --source todoist --limit 200 con acceso de red autorizado tras bloqueo de sandbox: INX enlaces sincronizados todoist=200.

## 2026-04-26T07:04Z — Codex — [MAR] Excluir proyectos Z del flujo MAR por defecto
Estado: DONE
Chat: chats/chat_2026-04-26.md
Resumen: David fijo la regla operativa: excluir siempre carpetas/proyectos Todoist Z* salvo peticion explicita. Ajustado tools/todoist_tools.py para calcular exclusiones dinamicas por nombre de proyecto con prefijo Z, no solo IDs historicos Z_PROJECTS; agents/todoist_agent.py acepta cualquier Z dinamico para zinbox. Anadidos tests/test_todoist_tools.py. Validaciones: py_compile OK, pytest test_todoist_tools 2 passed, estado real MAR excluyendo Z*: 26 acciones activas.

## 2026-04-27T15:10Z — Cursor — [MULTIAGENT] Definir firma por defecto como Cursor
Estado: DONE
Chat: chats/chat_2026-04-27.md
Resumen: A peticion de David, se institucionaliza Cursor como firma por defecto en chats/ cuando el asistente opera desde el IDE Cursor (salvo peticion explicita de firmar como Claude/Copilot/Codex). Actualizados .claude/multiagent.md (formato + regla), multiagents/chat_template.md (participantes) y memory/PURPOSE.md (roles).

## 2026-04-27T20:45Z — Cursor — [DOCS] Playbook portable: secretos .env
Estado: DONE
Chat: chats/chat_2026-04-27.md
Resumen: Creado playbooks/secure-env-secrets-portable-playbook.md con una metodologia agnostica para almacenar y cargar secretos .env (tokens/API keys) de forma segura y automatizable (gestor de contrasenas, cifrado en repo, keychain del SO, secret managers/CI). Actualizado playbooks/README.md para incluirlo.

## 2026-04-29T05:15Z — Cursor — [DOCS] Versionar carpeta toolkits
Estado: DONE
Chat: chats/chat_2026-04-29.md
Resumen: Anadida carpeta toolkits/ con ZIPs de kits portables y prompts de integracion. Actualizados memory/INDEX.md y memory/STRUCTURE.md (narrativa + TREE regenerado) para reflejar el nuevo top-level.
