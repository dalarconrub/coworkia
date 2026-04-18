# Chat Memory Snapshot

- Generated: `2026-04-18T17:26:13Z`
- Source: `C:\Users\David\Desktop\AI-Generators\coworkia\chats\chat_2026-04-18.md`
- Messages: `53`
- Last actor: `Codex/ABGD`

## Open Decisions

- None

## Agent State

- `Claude`
  last_message_index: 31
  last_direct_mention_index: 30
  pending_mentions: []
  pending_decisions: []
- `Codex`
  last_message_index: 21
  last_direct_mention_index: None
  pending_mentions: [22]
  pending_decisions: []
- `Copilot`
  last_message_index: None
  last_direct_mention_index: None
  pending_mentions: [3, 5, 7, 9]
  pending_decisions: []
- `Claude/ABGD`
  last_message_index: 41
  last_direct_mention_index: 25
  pending_mentions: []
  pending_decisions: []
- `Codex/ABGD`
  last_message_index: 53
  last_direct_mention_index: 52
  pending_mentions: []
  pending_decisions: []

## Structured Memory

- `MEMORIA` `Codex/ABGD` [34] el validador del caso 07 detecta por si mismo si PTN-Notas sigue con schema viejo y no migrado, y le dice a David que ejecute el migrate. No hay falso negativo posible. Lo mismo el promote: falla rapido con mensaje claro en vez de dejar que la API de Notion devuelva un error opaco.
- `SIGUIENTE` `Codex/ABGD` [34] @David cuando corras `python tools/migrate_notas_ruta_obsidian.py --dry-run` y luego sin flag, promociona una nota de prueba con `python tools/promote_obsidian_to_ptn.py "<nota>" [--proyecto "<x>"]` y lanza `apps\validate_case_07.bat --no-pause`. El informe deberia mostrar promociones > 0, match OBSIDIAN_DB y match INX obsidian:* al 100%. El match ptn:* probablemente quede incompleto (Gap 3) hasta que cablemos el sync ptn:<id> automatico.
- `MEMORIA` `Codex/ABGD` [35] el cruce doble `obsidian:<ruta>` <-> `ptn:<id>` en INX requiere que la fila PTN-Notas recien creada pase por `log_ptn_changes.py` antes de `sync_inx_links --source notion`. Sin ese log intermedio, `--source notion` no ve la fila. El bat del caso 07 ya lo encadena; `orchestrator inx-sync` tambien (cadena completa).
- `SIGUIENTE` `Codex/ABGD` [35] @David Gap 1 y Gap 4 abiertos como backlog. Si quieres cerrar Mejora 3 (sync inline en promote_obsidian_to_ptn.py) delega handoff; evita los 4 pasos del bat a costa de acoplar el promote con sync_inx_links.
- `MEMORIA` `Codex/ABGD` [37] flag --sync en promote_obsidian_to_ptn.py equivale al pipeline completo del caso 07 en un comando. Propiedades relation Proyecto PTN / Tarea PTN son la forma canonica de enlazar PTN-Notas con proyectos/tareas; 'Proyecto' y 'Tarea' rich_text quedan como legacy tras migrate_notas_ptn_relations.py y pueden limpiarse cuando se quiera. El promote detecta dinamicamente cual usar, asi que funciona antes y despues de la migracion.
- `SIGUIENTE` `Codex/ABGD` [37] @David caso 07 cerrado. Proximos candidatos logicos: caso 08 (anclar notas a KIT) o caso 10 (tareas MAR nacidas dentro de notas). Dime cual activamos.
- `MEMORIA` `Codex/ABGD` [39] el flujo canonico de promocion Obsidian->PTN-Notas post-2026-04-18 es un solo comando: `apps\promote_obsidian_to_ptn.bat "<nota>" [--proyecto "<ref>"] [--tarea "<ref>"] --sync`. No hace falta ejecutar el .bat de validacion salvo para auditoria posterior. Cleanup de legacy es opcional y puede correrse tras migrate_notas_ptn_relations.
- `SIGUIENTE` `Codex/ABGD` [39] @David caso 07 definitivamente cerrado. Los siguientes casos del plan son: 08 (KIT), 09 (BIB->Obsidian), 10 (MAR desde nota), 11 (journal diario), 12 (backfill INX historico), 13 (busqueda cross-system). Dime cual activamos o si queremos cerrar sesion con apps\cerrar_sesion.bat.
- `MEMORIA` `Codex/ABGD` [43] KIT ya es ciudadano de primera en INX. Clave canonica kit:<page_id>. No hay log intermedio (a diferencia de PTN/Obsidian): _sync_kit lee directo de NOTION_DB_KIT. Cruce Obsidian<->KIT sigue sin logica automatica; queda como Gap 1 del caso 08 para el futuro alcance C.
- `SIGUIENTE` `Codex/ABGD` [43] @David caso 08 cerrado en alcance B. Candidatos que siguen: 09 (BIB->Obsidian), 10 (MAR desde notas), 11 (journal), 12 (backfill INX historico), 13 (busqueda cross-system), o subir a alcance C del caso 08 (Usada en relation + cruce automatico). Dime.
- `MEMORIA` `Codex/ABGD` [45] el flujo BIB->ficha Obsidian es `promote_bib_to_obsidian.py <citekey> --sync`. Crea .md bajo A1-INV/B13-PUB/<contexto> con frontmatter citekey/bib-id/doi, y cierra cruce INX obsidian:<ruta> + paperpile:<citekey> en un comando. Dedup por nombre (no sobreescribe salvo --force).
- `SIGUIENTE` `Codex/ABGD` [45] @David si quieres validar end-to-end el caso 09, carga BIB con `python agents/bib_agent.py importar`. Proximos casos: 10 (tareas MAR desde notas), 11 (journal diario), 12 (backfill INX historico), 13 (busqueda cross-system).
- `MEMORIA` `Codex/ABGD` [47] captura obsidian->todoist via marker inline `<!-- todoist:<id> -->` es idempotente y visible en el .md original. Re-ejecutar el promote sobre la misma nota no duplica tareas. Para batch o close-on-check ver Gaps 1-2.
- `SIGUIENTE` `Codex/ABGD` [47] @David casos candidatos restantes: 11 (journal diario cruzado con timeline), 12 (backfill INX historico), 13 (busqueda cross-system). Dime cual sigue o si paramos aqui para cerrar sesion.
- `MEMORIA` `Codex/ABGD` [49] timeline.py reconoce el journal diario del vault por convencion N<YYMMDD>-*.md bajo A0-GTD/B0C-PLA/C0C9-Notas/. Es el primer consumidor del vault desde el lado operativo (chat/devlog) y requiere OBSIDIAN_ALPHA_PATH cargado. Sin la variable, la seccion del timeline queda "Sin journal" pero no falla.
- `SIGUIENTE` `Codex/ABGD` [49] @David quedan casos 12 (backfill INX historico) y 13 (busqueda cross-system). Tambien podemos cerrar sesion aqui con apps\cerrar_sesion.bat.
- `MEMORIA` `Codex/ABGD` [51] backfill_obsidian_to_inx.py complementa a log_obsidian_changes.py. log_obsidian es diff por mtime para cambios continuos; backfill es full-scan idempotente para historico o tras corrupcion de obsidian_log_state.json. Juntos garantizan cobertura completa.
- `SIGUIENTE` `Codex/ABGD` [51] @David solo queda caso 13 (busqueda cross-system) o cierre con apps\cerrar_sesion.bat.
- `MEMORIA` `Codex/ABGD` [53] sintaxis cross-system `[[<prefix>:<id>]]` con prefix en {ptn, kit, paperpile, todoist, github}. UUIDs de ptn y kit se normalizan (ignora guiones). Auditable con `tools/obsidian_wikilinks.py audit`. Busqueda inversa con `find <prefix>:<id>`. INX-ENLACES es el resolver; requiere sync reciente para que la auditoria sea fiable.
- `SIGUIENTE` `Codex/ABGD` [53] @David casos 07-13 todos implementados. Notas de prueba locales (2) en A0-GTD/B0C-PLA/C0C9-Notas/ del vault por si quieres borrarlas. Cerramos sesion con apps\cerrar_sesion.bat para regenerar SNAPSHOT.md?

## Recent Messages

- `44` `David` -> caso 09.
- `45` `Codex/ABGD` -> caso 09 implementado. Contraparte Obsidian del caso 06: un paper BIB se materializa como ficha de lectura .md con frontmatter cruzado. 1. tools/promote_bib_to_o
- `46` `David` -> caso 10.
- `47` `Codex/ABGD` -> caso 10 implementado. Captura de pendientes desde notas Obsidian a Todoist via marker inline idempotente. 1. tools/promote_notas_checkboxes_to_todoist.py: local
- `48` `David` -> caso 11.
- `49` `Codex/ABGD` -> caso 11 implementado y validado end-to-end. 1. tools/timeline.py extendido: carga dotenv al inicio (OBSIDIAN_ALPHA_PATH). Nuevo helper _journal_for(day) que res
- `50` `David` -> caso 12.
- `51` `Codex/ABGD` -> caso 12 implementado y validado 100% cobertura. 1. tools/backfill_obsidian_to_inx.py: recorre todas las notas del vault via get_todas_notas (no filtra por mtime
- `52` `David` -> haz 13.
- `53` `Codex/ABGD` -> caso 13 implementado y validado con nota de prueba. 1. tools/obsidian_wikilinks.py nuevo: modulo unificado con subcomandos `audit` y `find`. Regex WIKILINK_RE m
