# Chat Memory Snapshot

- Generated: `2026-05-15T20:12:45Z`
- Source: `C:\Users\David\Desktop\REPO\AI-Generators\coworkia\chats\chat_2026-05-15.md`
- Messages: `10`
- Last actor: `Codex`

## Open Decisions

- None

## Agent State

- `Claude`
  last_message_index: None
  last_direct_mention_index: None
  pending_mentions: []
  pending_decisions: []
- `Codex`
  last_message_index: 10
  last_direct_mention_index: None
  pending_mentions: []
  pending_decisions: []
- `Copilot`
  last_message_index: None
  last_direct_mention_index: None
  pending_mentions: []
  pending_decisions: []

## Structured Memory

- `MEMORIA` `Codex` [3] ABGD queda definido con ALPHA como única capa indexada por Coworkia/Obsidian para notas Markdown; BETA, GAMMA, DELTA y EPSILON son capas materiales con jerarquías propias.
- `MEMORIA` `Codex` [4] la semántica ABGD del 2026-05-15 reemplaza la definición anterior del 2026-05-09 donde BETA era staging, GAMMA productos generados, DELTA archivos/media y EPSILON histórico frío. La regla vigente es: ALPHA notas ABC; BETA proyectos hibernados/finalizados AB; GAMMA proyectos activos A; DELTA temporal AÑO/YYYY-MM-DD; EPSILON biblioteca por tipo de fichero.
- `MEMORIA` `Codex` [5] la ruta canónica nueva para vault/carpeta ABGD-E es `ABGDE/ABGDE-YYYY-MM-DD`; `reset_obsidian.py` deriva futuras rotaciones a esa forma y debe imprimir tanto `OBSIDIAN_ABGD_ROOT` como `OBSIDIAN_ALPHA_PATH`.
- `MEMORIA` `Codex` [6] el vault operativo actual es C:/Users/David/Documents/ABGDE/ABGDE-2026-05-15 y la capa indexada es C:/Users/David/Documents/ABGDE/ABGDE-2026-05-15/1.ALPHA.
- `MEMORIA` `Codex` [7] 1.ALPHA del vault operativo ABGDE-2026-05-15 ya contiene subcarpetas ABC completas; .obsidian debe existir solo en la raíz del vault, no dentro de 1.ALPHA.
- `MEMORIA` `Codex` [8] las carpetas estructurales de ABGD-E tienen nota índice homónima; estas notas no usan prefijo NYYMMDD-*, por lo que obsidian_agent.py estado no las cuenta como notas operativas.
- `MEMORIA` `Codex` [9] BETA/GAMMA/DELTA/EPSILON ya tienen contenedores mínimos reales e índices Markdown; no se crean proyectos vacíos, solo los niveles necesarios para clasificar material.
- `MEMORIA` `Codex` [10] toda rotación futura de vault ABGDE debe ejecutar automáticamente la creación de estructura mínima e índices de carpeta, integrada en `tools/reset_obsidian.py rotate`.

## Recent Messages

- `1` `Codex` -> Inicio de sesion ejecutado con `python tools/session_protocol.py inicia`; contexto Git, memoria, chat y devlog revisados.
- `2` `Codex` -> Sync Raindrop -> KIT ejecutado: 1 bookmark kit-import creado (mksglu - Overview) y materializado en INX como kit:361622cf-315b-8172-b004-f3dfd8030d15. También s
- `3` `Codex` -> Implementada la nueva semántica ABGD en memoria/docs/manual: 1.ALPHA solo notas Obsidian ABC; 2.BETA proyectos finalizados o hibernados AB; 3.GAMMA proyectos ac
- `4` `Codex` -> MEMORIA: la semántica ABGD del 2026-05-15 reemplaza la definición anterior del 2026-05-09 donde BETA era staging, GAMMA productos generados, DELTA archivos/medi
- `5` `Codex` -> Ajustada la convención de ruta ABGD-E: la forma canónica pasa a ser `ABGDE/ABGDE-YYYY-MM-DD`, manteniendo `1.ALPHA` como subcarpeta indexada. El vault actual si
- `6` `Codex` -> Corregida la ruta física ABGD-E: copiado el vault legacy a C:/Users/David/Documents/ABGDE/ABGDE-2026-05-15 y actualizado .env para que OBSIDIAN_ABGD_ROOT y OBSI
- `7` `Codex` -> Corregida 1.ALPHA para que tenga jerarquía ABC completa: 5 áreas, 15 bloques y 46 contextos. Eliminada la .obsidian duplicada dentro de 1.ALPHA; la válida queda
- `8` `Codex` -> Creadas 72 notas índice de carpeta en ABGDE-2026-05-15: raíz del vault, capas 1.ALPHA-5.EPSILON y todas las carpetas A/B/C de ALPHA. Cada nota tiene el mismo no
- `9` `Codex` -> Montada la estructura mínima operativa de BETA/GAMMA/DELTA/EPSILON en ABGDE-2026-05-15: BETA con áreas y bloques AB, GAMMA con áreas A, DELTA con 2026/2026-05-1
- `10` `Codex` -> Automatizada la estructura mínima en `reset_obsidian.py rotate`: cada nuevo vault `ABGDE-YYYY-MM-DD` crea por defecto BETA AB, GAMMA A, DELTA fecha actual, EPSI
