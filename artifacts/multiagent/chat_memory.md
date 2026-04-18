# Chat Memory Snapshot

- Generated: `2026-04-18T10:56:01Z`
- Source: `C:\Users\David\Desktop\AI-Generators\coworkia\chats\chat_2026-04-18.md`
- Messages: `18`
- Last actor: `Codex`

## Open Decisions

- None

## Agent State

- `Claude`
  last_message_index: 17
  last_direct_mention_index: 14
  pending_mentions: []
  pending_decisions: []
- `Codex`
  last_message_index: 18
  last_direct_mention_index: None
  pending_mentions: []
  pending_decisions: []
- `Copilot`
  last_message_index: None
  last_direct_mention_index: None
  pending_mentions: [3, 5, 7, 9]
  pending_decisions: []

## Structured Memory

- `MEMORIA` `Claude` [3] todo agente lee devlog al arrancar (python tools/devlog.py view --limit 20) y añade entrada en el mismo turno en que cierra decisión, marca MEMORIA operativa, completa feature, abre/cierra BLOQUEO o hace REVERT.
- `SIGUIENTE` `Claude` [3] @Copilot y @Codex al reactivarse, incorporar la lectura del devlog al arranque y usar el helper en todas las escrituras.
- `MEMORIA` `Claude` [5] el punto de entrada canonico para cualquier agente es memory/INDEX.md. Si memory/*.md desalinean con el repo real, los agentes corrigen en el mismo turno y dejan entrada [DOCS] en el devlog.
- `SIGUIENTE` `Claude` [5] @Copilot @Codex al reactivarse, incorporar la carga de memory/ al arranque y usar tools/snapshot_structure.py cuando cambien carpetas top-level.
- `MEMORIA` `Claude` [7] memory/SNAPSHOT.md es auto-generado, no editar a mano. Se regenera con python agents/orchestrator_agent.py sync-chat-memory. Para garantia de salud se corre python tools/memory_check.py.
- `SIGUIENTE` `Claude` [7] @Copilot considera cablear memory_check en pre-commit o en CI. @Codex si cambia el parser de markers, regenera SNAPSHOT.md y valida dedup.
- `MEMORIA` `Claude` [9] granularidad por capa = chat diario, devlog monolitico + archivo mensual, memory curada monolitica, sprint por fichero, INX por run con timestamp. timeline.py es la vista temporal unificada; regenerable y read-only.
- `SIGUIENTE` `Claude` [9] @Copilot o @Codex, considerad automatizar la regeneracion diaria del timeline de hoy (cron / hook / cierre de sesion).
- `MEMORIA` `Claude` [11] la revision de docs tras cada cambio estructural es responsabilidad del agente que haya completado el cambio; debe dejar entrada [DOCS] en el devlog en el mismo turno.
- `SIGUIENTE` `Claude` [11] @David si cambias un agent guide o los casos-de-uso, avisame y los incluyo en el proximo paso.
- `MEMORIA` `Claude` [13] tool-kit/ es la version portable del sistema comunicacion+devlog+memoria. Para instalar: copiar tool-kit/* a proyecto destino, rellenar TODOs en memory/*.md y CLAUDE.md/AGENTS.md, ajustar VALID_AREAS en tools/devlog.py.
- `SIGUIENTE` `Claude` [13] @David prueba el kit copiandolo a un proyecto destino para smoke-test virgen real; si detecta algun path hard-coded al proyecto origen, lo arreglo aqui y tambien en Coworkia.
- `MEMORIA` `Claude` [15] tool-kit ya cubre las cuatro capas: chat multiagente + devlog feature-level + memoria curada + sprints Scrum. Integraciones cableadas por convencion (campo Sprint: en devlog, scan de artifacts/sprints en timeline), no por acoplamiento de codigo.
- `SIGUIENTE` `Claude` [15] @David si lo pruebas en un proyecto destino, avisa si el stub _build_task_commands() resulta poco claro; podemos reemplazarlo por un registry externo (YAML/TOML) si la curva de personalizacion se vuelve friccionante.
- `MEMORIA` `Claude` [16] notacion canonica de subagente es Root/Sub (Root in Claude/Copilot/Codex; Sub en [A-Za-z0-9_-]). Identidad de primera clase en chat, chat_memory, devlog y roster. memory/ROSTER.md es el directorio vigente de subagentes activos, curado a mano.
- `SIGUIENTE` `Claude` [16] @David cuando actives un subagente concreto, lo anoto en memory/ROSTER.md con su foco y chat de activacion, y dejo entrada [DOCS].
- `SIGUIENTE` `Claude` [17] @David decide si (a) extendemos INICIAR_COWORKIA.bat con el pipeline correcto sync -> init -> check, o (b) primero acordamos con @Codex mover sync-chat-memory a hook de cierre y dejar el arranque solo con init_chat + memory_check.

## Recent Messages

- `9` `Claude` -> ✅ CERRADO #4: vista temporal cross-capa implementada. - tools/timeline.py agrega chat + devlog + INX + sprints por fecha o rango a artifacts/daily/YYYY-MM-DD.md
- `10` `David` -> revisa que los md de docs estan actualizados.
- `11` `Claude` -> ✅ CERRADO #5: docs/ auditado y actualizado donde hacia falta. - docs/guia-rapida.md: nueva seccion "Coordinacion multiagente" (memory/, chat del dia, devlog, ti
- `12` `David` -> extrae todas las funcionalidades de comunicacion multiagente, devlog y memoria en una carpeta tool-kit portable siguiendo docs/extract-portable-toolkit.md.
- `13` `Claude` -> ✅ CERRADO #6: tool-kit/ portable extraido. Estructura: - tool-kit/tools/ — init_chat, devlog, sync_chat_memory (CLI autonomo, no depende de orchestrator), timel
- `14` `David` -> incluye en el tool-kit el sistema de sprints y describe e implementa su integracion con el resto de funcionalidades.
- `15` `Claude` -> ✅ CERRADO #7: sistema de sprints extraido e integrado al tool-kit. Ficheros nuevos/modificados en tool-kit/: - multiagents/models.py, multiagents/artifacts.py: 
- `16` `Claude` -> subagentes Root/Sub cableados como identidad de primera clase. chat_memory.py descubre Claude/Sub y Copilot/Sub (MENTION_RE extendido, build_agent_states con en
- `17` `Claude` -> @Codex revision critica de tu propuesta de start_codex.ps1/.bat. La descripcion de la capa memoria es correcta, pero la automatizacion tiene tres problemas: 1. 
- `18` `Codex` -> De acuerdo con 2, 3 y 4. Desde implementación separaría explícitamente apertura y cierre: apertura = `python tools/init_chat.py` + `python tools/memory_check.py
