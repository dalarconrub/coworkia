# Protocolo Multiagente Compartido

Este archivo define la capa de coordinación entre Claude, Copilot y Codex.

## Fuente de verdad

- `chat.md` en la raíz es el hilo conversacional compartido.
- Cada agente debe leerlo completo antes de responder.
- El hilo es append-only: nunca se editan ni borran mensajes previos.
- `chat.md` debe mantenerse en `UTF-8`.
- En `Windows PowerShell 5.1`, cualquier lectura o escritura manual sobre `chat.md` debe usar `-Encoding utf8`.
- Los scripts que escriban en `chat.md` deben declarar `encoding="utf-8"` explícitamente.

## Cuándo responde un agente

Un agente responde solo si se cumple alguna:

1. David lo menciona directamente como `**David [@Agente]:**`
2. Hay una decisión abierta esperando su evaluación o voto.
3. Otro agente lo menciona explícitamente.

Un agente no debe responder dos veces a la misma decisión abierta salvo que:

- haya nueva información relevante
- David lo vuelva a mencionar
- otro agente le pida una réplica concreta

## Formato común

```md
**David [@Destinatario]:** mensaje
**Copilot:** mensaje
**Claude:** mensaje
**Codex:** mensaje
```

Regla de estilo:

- mensajes cortos
- una intención por mensaje
- mención explícita al siguiente owner cuando proceda

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
