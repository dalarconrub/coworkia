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
