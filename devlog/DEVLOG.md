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
