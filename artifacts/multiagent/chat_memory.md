# Chat Memory Snapshot

- Generated: `2026-04-19T17:15:17Z`
- Source: `C:\Users\David\Desktop\AI-Generators\coworkia\chats\chat_2026-04-19.md`
- Messages: `30`
- Last actor: `Codex`

## Open Decisions

- None

## Agent State

- `Claude`
  last_message_index: 16
  last_direct_mention_index: 15
  pending_mentions: []
  pending_decisions: []
- `Codex`
  last_message_index: 30
  last_direct_mention_index: None
  pending_mentions: []
  pending_decisions: []
- `Copilot`
  last_message_index: None
  last_direct_mention_index: None
  pending_mentions: []
  pending_decisions: []

## Structured Memory

- `MEMORIA` `Claude` [2] cualquier cambio estructural del pipeline (nuevo dominio, nuevo caso, nuevo tool transversal) actualiza docs/pipeline-atlas.md y apps/pipeline_gui.py (_build_atlas), y regenera memory/STRUCTURE.md TREE. Deja entrada [DOCS] en devlog.
- `SIGUIENTE` `Claude` [2] @David cuando lo abras (apps\pipeline_gui.bat), si detectas que algun nodo pierde contexto o un script queda sin listar, lo corrijo.
- `MEMORIA` `Claude` [4] botones de la GUI por nivel de impacto: Copiar (no toca nada), Abrir (lectura), Ejecutar (lanza en terminal nueva). Para args (--sync, --dry-run, --limit, etc.) usar Copiar y editar en terminal; Ejecutar corre sin argumentos.
- `SIGUIENTE` `Claude` [4] @David avisa si en macOS el .command no abre Terminal (quiza porque el SO bloquea tempfiles no firmados) — si pasa, cambio a AppleScript osascript directo.
- `MEMORIA` `Claude` [6] sistema de reseteo por fases. Fase 1 = Todoist (hecha). Fase 2 = Notion (schema Estado Activo/Archivado/Finalizado por decidir: field nuevo vs reusar Estado existente). Fase 3 = Obsidian (rotar vault, politica INX obsidian:* por decidir). Fase 4 = orquestador general que ejecuta las tres en orden con snapshot previo.
- `SIGUIENTE` `Claude` [6] @David prueba 'python tools/reset_mar.py reset-all --dry-run' o 'reset-by-type idea --dry-run' sin --limit para ver volumen real y decidir umbral. Cuando quieras arrancar Fase 2 (Notion), necesito decision sobre schema Estado.
- `MEMORIA` `Claude` [8] el campo Archivo es Checkbox PARALELO al Estado existente, nunca lo sobrescribe. Para filtrar vistas operativas hay que anadir manualmente en Notion el filtro 'Archivo != true' a cada vista canonica (no lo hace el script).
- `BLOQUEO` `Claude` [8] ensure_archivo_field.py necesita autorizacion explicita para modificar schemas en Notion. Hasta que lo ejecutes en real, reset_notion.py aborta con mensaje claro pidiendo bootstrap.
- `SIGUIENTE` `Claude` [8] @David (a) ejecutas 'python tools/ensure_archivo_field.py' para crear la propiedad en los 4 DS, (b) luego 'python tools/reset_notion.py reset-ptn-proyectos --dry-run --snapshot --limit 5' para ver comportamiento sin escribir, (c) cuando te convenza, quitas --dry-run. Fases 3 (Obsidian vault) y 4 (orquestador general) siguen en cola.
- `SIGUIENTE` `Claude` [10] @David cuando quieras archivar de verdad, quita --dry-run. Si quieres limpiar los 2 proyectos 'ejemplo A3/A4' del workspace y arrancar solo con los 3 reales, ejecuta 'python tools/reset_notion.py reset-ptn-proyectos --limit 2' (sin dry-run) tras verificar en Notion cuales son los ids ejemplo. Alternativa mas conservadora: 'reset-ptn-proyectos --dry-run' sin limit para ver el total antes de decidir.
- `MEMORIA` `Claude` [12] Reset Obsidian (Fase 3) usa estrategia C fija: vault viejo nunca se renombra ni mueve; el nuevo nace donde David decida via --new-vault-path obligatorio. El cambio de OBSIDIAN_ABGD_ROOT en .env es manual siempre (el CLI lo imprime, David lo pega). Esto protege el control del usuario sobre rutas y credenciales.
- `SIGUIENTE` `Claude` [12] @David cuando quieras rotar el vault, (a) decide ruta destino (ej. C:/GDrive/dalarconrub/ABGD/ABGD-26.04.19); (b) corre 'python tools/reset_obsidian.py rotate --new-vault-path <ruta> --dry-run --snapshot' para confirmar; (c) quita --dry-run cuando te convenza; (d) edita .env con la linea que el CLI imprime; (e) abre el vault nuevo en Obsidian desktop. Queda Fase 4: orquestador general que ejecuta las 3 en orden con snapshot completo previo. ¿Arrancamos ya o pausamos?
- `MEMORIA` `Claude` [14] sistema de reseteo completo en 4 fases. Fase 1 (MAR, marker reversible), Fase 2 (Notion Checkbox Archivo + propagacion INX), Fase 3 (Obsidian rotar vault estrategia C), Fase 4 (reset_all.py orquesta las 3). Reset general skipea Obsidian por defecto por seguridad; para incluirlo pasa --obsidian-new-vault-path explicito.
- `SIGUIENTE` `Claude` [14] @David (a) si quieres ver plan completo: 'python tools/reset_all.py --dry-run --obsidian-new-vault-path <ruta_destino>'; (b) si te convence: '--yes --obsidian-new-vault-path <ruta>' para ejecutar. Sistema de reseteo queda cerrado. ¿Siguiente objetivo o hacemos commit y cerramos la sesion?
- `MEMORIA` `Claude` [16] bateria validate_case_14.py es la referencia oficial para probar el sistema de reseteo. Correrla siempre tras tocar cualquier tools/reset_*.py o apps/reset_*.bat. Si aparece un FAIL nuevo, lo arreglamos en el mismo turno (no cerrar la ficha con fallos vivos) salvo que sea manual documentado en Gaps.
- `SIGUIENTE` `Claude` [16] @David sistema de reseteo completo, documentado y validado. ¿commit y cerramos sesion, o siguiente objetivo?
- `MEMORIA` `Codex` [21] prueba end-to-end real de 08C completada con la nota `A0-GTD\B0A-INX\N260419-Test-08C-kit-link.md`, que contiene `[[kit:340622cf-315b-814b-bf50-e20378365646]]`. Backfill cre? 1 fila nueva en `OBSIDIAN_DB`, `sync_inx_links --source obsidian` dej? `obsidian=32`, y `validate_case_08.py --scope c` termin? OK con `Filas OBSIDIAN_DB con KIT IDs: 1` y `mismatch: 0`. SIGUIENTE: @David decide si dejamos esta nota como fixture manual del vault o si prefieres borrarla tras la validaci?n.
- `MEMORIA` `Codex` [22] la nota fixture `A0-GTD\B0A-INX\N260419-Test-08C-kit-link.md` se elimin? tras la validaci?n y tambi?n se archivaron sus filas derivadas en `OBSIDIAN_DB` e `INX-ENLACES`, as? que el caso 08C queda validado sin basura operativa persistente. SIGUIENTE: @David si quieres cerrar este frente, el siguiente objetivo natural sigue siendo caso 10 o caso 09 seg?n el ranking fijado en #16.
- `MEMORIA` `Codex` [27] ejecutado batch real `--all-pending --limit 5 --contexto C137-ART --sync` del caso 09. Se crearon 5 fichas nuevas (`Abad2021c`, `Abedishargh2021d`, `Abril2024i`, `Agras2021q`, `Ahmed2018t`). El primer intento fall? por dependencia vieja de `python-dotenv` en `tools/log_ptn_changes.py`; se corrigi? en el mismo turno y se relanz? la sincronizaci?n. Para que la validaci?n cerrara 6/6 hizo falta ampliar `sync_inx_links --source paperpile` al cat?logo completo: ahora `INX-ENLACES` contiene `paperpile:* = 472` y el caso 09 queda verde con cruce doble y `Paperpile Citekey` expl?cito. SIGUIENTE: @David si quieres seguir expandiendo BIB, el siguiente paso natural es otro batch acotado (por ejemplo 10 o 25 papers) o a?adir filtros m?s finos a `--all-pending`.

## Recent Messages

- `21` `Codex` -> MEMORIA: prueba end-to-end real de 08C completada con la nota `A0-GTD\B0A-INX\N260419-Test-08C-kit-link.md`, que contiene `[[kit:340622cf-315b-814b-bf50-e203783
- `22` `Codex` -> MEMORIA: la nota fixture `A0-GTD\B0A-INX\N260419-Test-08C-kit-link.md` se elimin? tras la validaci?n y tambi?n se archivaron sus filas derivadas en `OBSIDIAN_DB
- `23` `Codex` -> ? CERRADO #18: ampliado el caso 10 a round-trip real Obsidian ? Todoist con cierre de tareas. Entregables: `tools/close_obsidian_checkboxes_to_todoist.py` cierr
- `24` `Codex` -> ? CERRADO #19: ampliado el caso 09 a loop bidireccional m?nimo BIB ? Obsidian mediante sincronizaci?n de `estado-lectura`. Entregables: `tools/sync_bib_reading_
- `25` `Codex` -> ? CERRADO #20: `Paperpile Citekey` queda expl?cito en las filas `obsidian:*` de INX. Entregables: `tools/ensure_inx_paperpile_citekey_field.py` crea el campo en
- `26` `Codex` -> ? CERRADO #21: a?adido `--all-pending` al caso 09 para promoci?n masiva desde BIB. Entregables: `tools/promote_bib_to_obsidian.py` ahora soporta `--all-pending`
- `27` `Codex` -> MEMORIA: ejecutado batch real `--all-pending --limit 5 --contexto C137-ART --sync` del caso 09. Se crearon 5 fichas nuevas (`Abad2021c`, `Abedishargh2021d`, `Ab
- `28` `Codex` -> ? CERRADO #22: refinado `--all-pending` del caso 09 con filtros finos y bugfix. Entregables: `tools/promote_bib_to_obsidian.py` ahora soporta `--query` y `--yea
- `29` `Codex` -> ✅ CERRADO #23: endurecido --sync en la promoción masiva BIB→Obsidian para evitar INX parcial. Ajuste: ools/promote_bib_to_obsidian.py deja de encadenar sync_inx
- `30` `Codex` -> ✅ CERRADO #24: añadidos filtros estructurales al batch --all-pending del caso 09. Entregables: ools/promote_bib_to_obsidian.py ahora soporta --author, --journal
