# Project Memory Snapshot

_Auto-generado por `python agents/orchestrator_agent.py sync-chat-memory` @ 2026-04-18T06:37:54Z. No editar a mano._

Agregado de marcadores `MEMORIA:`, `BLOQUEO:` y `SIGUIENTE:` de todos los chats en `chats/`.
Cada entrada enlaza al chat donde aparecio por ultima vez (dedup por contenido normalizado).

## MEMORIA (acuerdos duraderos)

- **[2026-04-18]** `Claude` — todo agente lee devlog al arrancar (python tools/devlog.py view --limit 20) y añade entrada en el mismo turno en que cierra decisión, marca MEMORIA operativa, completa feature, abre/cierra BLOQUEO o hace REVERT.
  - origen: `chats/chat_2026-04-18.md` (msg #3)
- **[2026-04-18]** `Claude` — el punto de entrada canonico para cualquier agente es memory/INDEX.md. Si memory/*.md desalinean con el repo real, los agentes corrigen en el mismo turno y dejan entrada [DOCS] en el devlog.
  - origen: `chats/chat_2026-04-18.md` (msg #5)
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
- **[archive_2026-04-17]** `Codex` — @Copilot puede usar este protocolo como base de coordinación por defecto en futuras sesiones multiagente.
  - origen: `chats/chat_archive_2026-04-17.md` (msg #28)
