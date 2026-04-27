# Protocolo Multiagente Compartido

Este archivo define la capa de coordinación entre Claude, Copilot y Codex (agentes **raíz**) y sus **subagentes** (`Root/Sub`).

## Memoria del proyecto — PASO 1 al arrancar

Antes de leer nada más, todo agente debe cargar la memoria curada del proyecto:

1. `memory/INDEX.md` — mapa de todos los recursos.
2. `memory/PURPOSE.md` — qué es Coworkia y qué hace.
3. `memory/STRUCTURE.md` — organización de carpetas y lógica.

Solo después se lee el archivo de identidad propio (`CLAUDE.md` / `AGENTS.md` / `.github/copilot-instructions.md`) y esta misma guía.

Si detectas desalineación entre `memory/*.md` y el estado real del repo, corrígelo en el mismo turno y deja entrada `[DOCS]` en el devlog. `memory/STRUCTURE.md` se regenera con `python tools/snapshot_structure.py` (el bloque TREE, la narrativa se edita a mano).

## Precedencia: memoria del repo sobre memoria del harness

Las memorias locales del harness (Codex memories en `~/.codex/memories/`, Claude profile memory, caches similares de otros harnesses) **nunca sustituyen** a la memoria versionada del repo. Son una capa auxiliar de recall, no una fuente de verdad.

Ante conflicto entre lo que "recuerda" tu harness y lo que dice el repo, **mandan** (en orden):

1. `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` (identidad y protocolo).
2. `memory/*.md` (`INDEX`, `PURPOSE`, `STRUCTURE`, `ROSTER`, `SNAPSHOT`).
3. Chat del día (`chats/chat_YYYY-MM-DD.md`).
4. `devlog/DEVLOG.md`.

Si el harness expone gestión de memorias (p. ej. `/memories` en Codex), limpia o ignora recuerdos locales obsoletos cuando los detectes. No hace falta crear `.codex/` ni carpetas paralelas: el contrato project-scoped ya vive en `AGENTS.md` + este protocolo.

## Fuente de verdad

- Hay un chat por día en `chats/chat_YYYY-MM-DD.md`.
- Para resolver la ruta del chat del día (creándolo desde plantilla si no existe):
  `python tools/init_chat.py` → imprime la ruta activa.
- La plantilla canónica es `multiagents/chat_template.md`.
- Los chats de días anteriores se preservan en `chats/` como histórico.
- Cada agente debe leer el chat del día completo antes de responder.
- El hilo es append-only: nunca se editan ni borran mensajes previos.
- Todos los chats deben mantenerse en `UTF-8`.
- En `Windows PowerShell 5.1`, cualquier lectura o escritura manual sobre los ficheros de `chats/` debe usar `-Encoding utf8`.
- Los scripts que escriban en un chat deben declarar `encoding="utf-8"` explícitamente.
- Si aparece mojibake, repararlo con `python tools/fix_chat_mojibake.py <ruta>`.

## Cuándo responde un agente

Un agente responde solo si se cumple alguna:

1. David lo menciona directamente como `**David [@Agente]:**` (la raíz o un subagente).
2. Hay una decisión abierta esperando su evaluación o voto.
3. Otro agente lo menciona explícitamente (`@Root` o `@Root/Sub`).

Si David dirige a un subagente (`@Claude/KIT`), solo responde ese subagente; la raíz no asume el turno salvo nueva mención.

Un agente no debe responder dos veces a la misma decisión abierta salvo que:

- haya nueva información relevante
- David lo vuelva a mencionar
- otro agente le pida una réplica concreta

## Formato común

```md
**David [@Destinatario]:** mensaje
**Cursor:** mensaje
**Copilot:** mensaje
**Claude:** mensaje
**Codex:** mensaje
```

`Destinatario` puede ser una raíz (`Claude`/`Copilot`/`Codex`) o un subagente (`Claude/KIT`, `Codex/INX`, ...). Las menciones laterales `@Root` y `@Root/Sub` funcionan igual.

### Identidad `Cursor`

`Cursor` es una identidad operativa para cuando el asistente está actuando desde el IDE Cursor en esta repo.

Regla: **si no hay una petición explícita de firmar como `Claude`/`Copilot`/`Codex`, la firma por defecto en `chats/` será `**Cursor:**`** para evitar confusión entre el rol del harness y el rol multiagente del proyecto.

Regla de estilo:

- mensajes cortos
- una intención por mensaje
- mención explícita al siguiente owner cuando proceda

## Subagentes (`Root/Sub`)

Un subagente es una variante especializada de una raíz. Hereda su protocolo y se dirige a un dominio o tarea concreta.

- Notación: `Root/Sub` — `Root` ∈ {`Claude`, `Copilot`, `Codex`}, `Sub` = letras/dígitos/`_`/`-`.
- Firma del mensaje: `**Claude/KIT:**`, `**Codex/INX:**`, etc.
- Dirección desde David: `**David [@Claude/KIT]:** ...`.
- Mención lateral: `@Claude/KIT`.
- Identidad de primera clase en `tools/devlog.py` (`--agent Claude/KIT`) y en `multiagents/chat_memory.py` (parser y estado por agente).
- Directorio vigente de subagentes: [`memory/ROSTER.md`](../memory/ROSTER.md). Solo entran subagentes activados por David o confirmados con `✅ CERRADO`.
- Herencia: el subagente aplica el `CLAUDE.md` / `AGENTS.md` / `.github/copilot-instructions.md` de su raíz + este protocolo. No redefine reglas base.
- Handoff: si la pregunta se sale del foco declarado, el subagente hace `SIGUIENTE: @Root` (o @otro subagente) y no fuerza respuesta.

## Marcadores canónicos

Estos marcadores permiten memoria estructurada y logs:

```md
MEMORIA: hecho o acuerdo duradero
BLOQUEO: impedimento concreto
SIGUIENTE: siguiente acción u owner
```

Ejemplo:

```md
**Claude:** 🔍 EVAL #4 desde análisis: C > A > B.
MEMORIA: la autoridad canónica de proyectos sigue siendo PTN en Notion.
SIGUIENTE: @Codex aterriza el cambio de implementación.
```

## Modos de decisión

### 🗳️ VOTO

```md
🗳️ VOTO #N: ✅/❌ [razón breve]
```

### 🔍 EVALUACIÓN

Claude usa:

```md
🔍 EVAL #N desde análisis: [valoración]. Ranking: X > Y > Z
```

Copilot usa:

```md
🔍 EVAL #N desde orquestación: [valoración]. Ranking: X > Y > Z
```

Codex usa:

```md
🔍 EVAL #N desde implementación: [valoración]. Ranking: X > Y > Z
```

### 🎯 ESPECIALIDAD

Solo David puede delegarla.

```md
✅ CERRADO: [decisión adoptada]
```

### 💡 CREATIVIDAD

Formato libre, pero con propuestas concretas.

## Cierre y memoria

Cuando una conversación deja acuerdos o estado operativo relevante, cualquier agente puede recomendar:

```bash
python agents/orchestrator_agent.py sync-chat-memory
```

Ese comando genera:

- `artifacts/multiagent/conversation_records.jsonl`
- `artifacts/multiagent/decision_log.json`
- `artifacts/multiagent/agent_state.json`
- `artifacts/multiagent/memory_records.json`
- `artifacts/multiagent/chat_memory_snapshot.json`
- `artifacts/multiagent/chat_memory.md`

## DevLog obligatorio

El log de desarrollo feature-level vive en `devlog/DEVLOG.md` (append-only, UTF-8). Complementa a `git log` (commits) y al chat del día (conversación): narra *qué se trabajó, por qué y con qué impacto*.

### Lectura inicial

Todos los agentes deben, al arrancar, leer las **últimas ~20 entradas** para tener contexto de trabajo reciente:

```bash
python tools/devlog.py view --limit 20
```

### Escritura obligatoria

Un agente **debe** añadir entrada al devlog cuando, en el mismo turno:

1. Cierra una decisión con `✅ CERRADO #N`.
2. Registra una `MEMORIA:` duradera con impacto operativo.
3. Completa una tarea de código con cambios mergeados (hito de feature).
4. Registra un `BLOQUEO:` real (`Estado: BLOCKED`); al resolverse, otro `UNBLOCKED`.
5. Hace `REVERT` o rollback significativo.

No se escribe entrada para refactors menores, fixes triviales o ediciones sin impacto en comportamiento.

### Cómo escribir

Usar el helper (garantiza UTF-8, timestamp UTC y enlace al chat del día):

```bash
python tools/devlog.py append \
  --agent Claude --area PTN --status DONE \
  --title "Sync INX con Paperpile estabilizado" \
  --summary "Se valida la ruta paperpile:<citekey>; se retira el fallback temporal." \
  --commits d5c6b5c --refs "CERRADO #7" --sprint "sprint-multiagent-1"
```

Tags válidos de `--area`: `MAR`, `PTN`, `KIT`, `GIT`, `BIB`, `ABGD`, `INX`, `MULTIAGENT`, `TOOLING`, `DOCS`, `INFRA`. (`REP` se conserva como alias historico para entradas pre-2026-04-24.)
Estados válidos: `START`, `PROGRESS`, `BLOCKED`, `UNBLOCKED`, `DONE`, `REVERT`.
Campo opcional `Sprint:` para cruzar con `artifacts/sprints/<sprint>.json` — usarlo cuando la tarea pertenezca a un sprint activo.

### Consulta

```bash
python tools/devlog.py view                         # últimas 20
python tools/devlog.py view --area PTN
python tools/devlog.py view --agent Codex --limit 5
python tools/devlog.py view --status BLOCKED        # bloqueos vigentes
```

### Vista temporal (cross-capa)

Para unificar chat + devlog + INX + sprints de una fecha o rango:

```bash
python tools/timeline.py                    # hoy
python tools/timeline.py --date 2026-04-18
python tools/timeline.py --days 7           # ultimos 7 dias
python tools/timeline.py --from 2026-04-15 --to 2026-04-18
```

Escribe `artifacts/daily/YYYY-MM-DD.md` (regenerable, read-only sobre fuentes).
