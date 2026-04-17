# Sistema Multiagente de Coworkia

## Objetivo

Coordinar Claude, Codex y Copilot con dos capas complementarias:

1. `chat.md` como canal humano compartido y append-only
2. `multiagents/*` como capa operativa para planificación, ejecución, estado y memoria

El objetivo no es solo conversar entre agentes, sino dejar trazabilidad y memoria reutilizable.

## Principios

- `chat.md` es la fuente de verdad del diálogo.
- El diálogo debe ser breve, explícito y con handoffs claros.
- La memoria útil no debe quedar enterrada en el hilo.
- Las decisiones, bloqueos y siguientes pasos deben persistirse como logs estructurados.
- El orquestador debe poder reconstruir estado a partir del hilo y de los artifacts.
- `chat.md` se mantiene en `UTF-8`; en `Windows PowerShell 5.1` toda lectura/escritura manual debe usar `-Encoding utf8`.

## Protocolo de comunicación

### Formato base

```md
**David [@Destinatario]:** mensaje
**Copilot:** respuesta
**Claude:** respuesta
**Codex:** respuesta
```

### Reglas de participación

Cada agente responde solo si:

1. David lo menciona directamente
2. hay una decisión abierta que requiere su participación
3. otro agente lo menciona explícitamente

Además:

- no se reescriben mensajes anteriores
- no se responde dos veces a la misma decisión sin nueva información
- los mensajes deben cerrar con owner o siguiente acción cuando sea útil

### Marcadores estructurados

El hilo soporta tres marcadores canónicos:

```md
MEMORIA: acuerdo o hecho duradero
BLOQUEO: impedimento concreto
SIGUIENTE: siguiente acción recomendada
```

Estos marcadores se extraen a memoria estructurada.

## Capa de memoria

Inspirada en sistemas con coordinator + memory layer, esta implementación genera logs persistentes del chat:

- `conversation_records.jsonl`: historial estructurado de mensajes
- `decision_log.json`: decisiones abiertas y cerradas
- `agent_state.json`: estado resumido por agente
- `memory_records.json`: extracción de `MEMORIA`, `BLOQUEO` y `SIGUIENTE`
- `chat_memory_snapshot.json`: snapshot consolidado
- `chat_memory.md`: resumen legible para humanos

Salida por defecto:

```text
artifacts/multiagent/
```

## CLI

Generar memoria del chat:

```bash
python agents/orchestrator_agent.py sync-chat-memory
```

Planificar sprint:

```bash
python agents/orchestrator_agent.py plan-sprint "Objetivo" --nombre "Sprint X" --guardar
```

Consultar estado del sprint:

```bash
python agents/orchestrator_agent.py status "Sprint X"
```

Ejecutar tarea:

```bash
python agents/orchestrator_agent.py run-task "Sprint X" ST-003
```

Ejecutar sprint:

```bash
python agents/orchestrator_agent.py run-sprint "Sprint X"
```

## Encaje con la arquitectura actual

- `chat.md` resuelve coordinación humana entre servicios de agentes
- `multiagents/planner.py` compone squads y tareas
- `multiagents/artifacts.py` persiste sprints y estados de ejecución
- `multiagents/chat_memory.py` construye memoria estructurada del hilo
- `agents/orchestrator_agent.py` expone planning, ejecución y memoria por CLI

## Flujo recomendado

1. David abre una instrucción en `chat.md`
2. el agente destinatario responde
3. cuando haya acuerdo, bloqueo o handoff, se usan `MEMORIA:`, `BLOQUEO:` o `SIGUIENTE:`
4. periódicamente, o al cerrar una sesión relevante, se ejecuta:

```bash
python agents/orchestrator_agent.py sync-chat-memory
```

5. si la conversación deriva en trabajo ejecutable, se usa el orquestador de sprint

## Siguiente iteración útil

1. auto-resumen incremental por sesión
2. búsqueda semántica sobre `memory_records.json`
3. asociación entre decisiones del chat y tareas del sprint
4. artifacts por sesión además de snapshot global
