# Sistema Multiagente Scrum Para Coworkia

## Resumen

Coworkia coordina a David (director) con tres agentes IA — Claude, Copilot y Codex — sobre cuatro capas complementarias:

1. **Memoria curada** (`memory/*.md`) — identidad, propósito y estructura del proyecto.
2. **Hilo compartido** (`chats/chat_YYYY-MM-DD.md`) — conversación viva diaria.
3. **DevLog** (`devlog/DEVLOG.md`) — hitos feature-level append-only.
4. **Orquestación Scrum** (`multiagents/*`, `agents/orchestrator_agent.py`) — sprints, ejecución, memoria estructurada derivada.

La memoria curada define *qué es el proyecto hoy*, el chat registra *qué se habla*, el devlog narra *qué se ha hecho*, y la capa Scrum planifica *qué se va a hacer*.

## Orden de lectura al arrancar (todo agente)

1. `memory/INDEX.md` — mapa de recursos.
2. `memory/PURPOSE.md` — qué es Coworkia.
3. `memory/STRUCTURE.md` — cómo está organizado.
4. Archivo de identidad según agente: `CLAUDE.md`, `AGENTS.md`, o `.github/copilot-instructions.md`.
5. `.claude/multiagent.md` — protocolo compartido.
6. Chat del día (resuelto con `python tools/init_chat.py`).
7. Últimas entradas del devlog (`python tools/devlog.py view --limit 20`).

`init_chat.py` imprime un briefing que cubre los pasos 6 y 7 de un tirón.

## Protocolo común

- `chats/chat_YYYY-MM-DD.md` es **append-only** y siempre **UTF-8 estricto**.
- Cada agente lo lee completo antes de responder.
- Cada agente responde solo cuando se le menciona o hay una decisión abierta que requiere su participación.
- Mensajes breves, una intención por mensaje.

Marcadores canónicos:

```md
MEMORIA: acuerdo o contexto duradero
BLOQUEO: impedimento concreto
SIGUIENTE: siguiente acción recomendada
```

## CLI — orquestador

```bash
python agents/orchestrator_agent.py plan-sprint "Objetivo" --nombre "Sprint X" --guardar
python agents/orchestrator_agent.py status "Sprint X"
python agents/orchestrator_agent.py run-task "Sprint X" ST-003
python agents/orchestrator_agent.py run-sprint "Sprint X"
python agents/orchestrator_agent.py sync-chat-memory
python agents/orchestrator_agent.py inx-sync --limit 200
```

## CLI — coordinación y memoria

```bash
# Chat del día + briefing (memory + últimas entradas devlog)
python tools/init_chat.py
python tools/init_chat.py --quiet        # solo la ruta (para scripts)

# DevLog feature-level
python tools/devlog.py view                                    # últimas 20
python tools/devlog.py view --area PTN --status BLOCKED
python tools/devlog.py append \
    --agent Claude --area PTN --status DONE \
    --title "..." --summary "..." \
    [--commits sha1,sha2] [--refs "CERRADO #N"] [--sprint "<nombre>"]

# Memoria curada del proyecto
python tools/snapshot_structure.py                # regenera el TREE de STRUCTURE.md
python tools/snapshot_structure.py --check        # CI: sale 1 si desfasado
python tools/memory_check.py                      # valida ficheros + enlaces INDEX + frescura TREE
python tools/memory_check.py --fix-tree           # idem, regenera TREE si desfasado

# Vista temporal agregada (chat + devlog + INX + sprints)
python tools/timeline.py                          # hoy
python tools/timeline.py --date 2026-04-18
python tools/timeline.py --from 2026-04-15 --to 2026-04-18
python tools/timeline.py --days 7
```

## Memoria del chat y del proyecto

### Derivada — `artifacts/multiagent/`

`sync-chat-memory` parsea el chat activo y genera:

- `conversation_records.jsonl` — log estructurado mensaje a mensaje.
- `decision_log.json` — decisiones (`VOTO`, `EVAL`, `CERRADO`) con estado, autor y participantes.
- `agent_state.json` — índice último mensaje, menciones y decisiones pendientes por agente.
- `memory_records.json` — marcadores `MEMORIA:`, `BLOQUEO:`, `SIGUIENTE:` del chat.
- `chat_memory_snapshot.json` / `chat_memory.md` — snapshot completo del chat.

### Agregada a nivel proyecto — `memory/SNAPSHOT.md`

El mismo comando también emite `memory/SNAPSHOT.md`, agregando `MEMORIA/BLOQUEO/SIGUIENTE` de **todos** los chats en `chats/` con dedup por contenido normalizado y enlace al chat origen. Es la vista vigente de acuerdos duraderos a lo largo de toda la historia.

### Temporal — `artifacts/daily/YYYY-MM-DD.md`

`tools/timeline.py` cruza por fecha: chat (link, recuento, decisiones cerradas), entradas del devlog con `Sprint:` si aplica, INX runs (`artifacts/inx/inx-daily-YYYYMMDD-*.md`) y sprints activos esa fecha. Read-only sobre las fuentes.

## DevLog — obligatorio para agentes

Todo agente **debe** añadir entrada en `devlog/DEVLOG.md` en el mismo turno en que:

1. Cierra una decisión (`✅ CERRADO #N`).
2. Registra una `MEMORIA:` con impacto operativo.
3. Completa una tarea de código (hito feature).
4. Abre o cierra un `BLOQUEO:`.
5. Hace `REVERT` o rollback.

Reglas y detalle en `.claude/multiagent.md` sección "DevLog obligatorio".

## Estado actual

1. Sprint planning persistido en Markdown y JSON en `artifacts/sprints/`.
2. Ejecución básica de tareas con estado (`run-task`, `run-sprint`).
3. Memoria estructurada del chat y memoria agregada del proyecto (`SNAPSHOT.md`).
4. Extracción automática de decisiones, handoffs y bloqueos desde el hilo.
5. DevLog feature-level append-only, obligatorio para los tres agentes IA.
6. Memoria curada (`memory/`) con `PURPOSE`, `STRUCTURE`, `INDEX`, cargada como paso 1 al arrancar.
7. Vista temporal cross-capa (`tools/timeline.py` → `artifacts/daily/`).
8. Integridad validable (`tools/memory_check.py`).

## Siguientes iteraciones

1. Asociar decisiones del chat con tareas del sprint explícitamente (hoy solo vía convención del campo `Sprint:` en devlog).
2. Búsqueda semántica sobre memoria (`SNAPSHOT.md` + `DEVLOG.md`).
3. Resúmenes incrementales por sesión generados al cerrar el día.
4. Cablear `memory_check.py` y `snapshot_structure.py --check` a pre-commit o CI.
5. Regeneración automática del timeline del día al cerrar sesión.
