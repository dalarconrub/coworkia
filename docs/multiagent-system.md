# Sistema Multiagente Scrum Para Coworkia

## Resumen

Coworkia usa dos capas complementarias:

1. `chat.md` como hilo compartido entre David, Copilot, Claude y Codex
2. `multiagents/*` como capa de planificación, ejecución, estado y memoria

La comunicación humana vive en `chat.md`, pero sus decisiones y hechos relevantes se pueden persistir a logs estructurados.

## Protocolo común

- `chat.md` es append-only
- cada agente lo lee completo antes de responder
- cada agente responde solo cuando ha sido mencionado o cuando hay una decisión abierta que requiere su participación
- los mensajes deben ser breves y orientados a acción

Marcadores comunes:

```md
MEMORIA: acuerdo o contexto duradero
BLOQUEO: impedimento concreto
SIGUIENTE: siguiente acción recomendada
```

## CLI principal

```bash
python agents/orchestrator_agent.py plan-sprint "Objetivo" --nombre "Sprint X" --guardar
python agents/orchestrator_agent.py status "Sprint X"
python agents/orchestrator_agent.py run-task "Sprint X" ST-003
python agents/orchestrator_agent.py run-sprint "Sprint X"
python agents/orchestrator_agent.py sync-chat-memory
```

## Memoria del chat

`sync-chat-memory` genera:

- `artifacts/multiagent/conversation_records.jsonl`
- `artifacts/multiagent/decision_log.json`
- `artifacts/multiagent/agent_state.json`
- `artifacts/multiagent/memory_records.json`
- `artifacts/multiagent/chat_memory_snapshot.json`
- `artifacts/multiagent/chat_memory.md`

## Estado actual

La iteración actual ya cubre:

1. sprint planning persistido en Markdown y JSON
2. ejecución básica de tareas con estado
3. memoria estructurada del chat
4. extracción de decisiones, handoffs y bloqueos desde el hilo

## Siguiente iteración útil

1. asociar decisiones del chat con tareas del sprint
2. búsqueda semántica sobre memoria
3. resúmenes incrementales por sesión
