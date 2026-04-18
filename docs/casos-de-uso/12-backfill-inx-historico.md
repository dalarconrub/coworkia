# Caso de uso: Backfill INX de notas históricas del vault

## Objetivo

Garantizar que **todas** las notas `.md` del vault Obsidian tengan fila en `OBSIDIAN_DB` (y, por extensión, en `INX-ENLACES` como `obsidian:<ruta>`), independientemente de si su `mtime` ha cambiado desde que se instaló el sistema de logging. Cubre el gap dejado por `log_obsidian_changes.py`, que solo procesa archivos con `mtime > last_mtime` guardado en `artifacts/obsidian_log_state.json`.

## Actores

- **Usuario**: David
- **Sistema(s)**: Obsidian (vault), Notion (`OBSIDIAN_DB`, `INX-ENLACES`).

## Trigger

1. **Instalación inicial / migración**: al adoptar Coworkia sobre un vault preexistente, las notas antiguas nunca pasan por el `mtime` check.
2. **Corrupción de `obsidian_log_state.json`**: si el fichero se borra o se fuerza a futuro, notas reales quedan sin registrar.
3. **Auditoría periódica**: verificar que no hay drift entre vault y `OBSIDIAN_DB`.

## Precondiciones

- `.env` con `OBSIDIAN_DB`, `NOTION_DB_INX`, `OBSIDIAN_ALPHA_PATH`.

## Fuente de verdad (autoridad)

- **Vault**: primera fuente, siempre manda.
- **OBSIDIAN_DB**: espejo auditable de los `.md`.
- **INX-ENLACES**: derivado de `OBSIDIAN_DB` vía `sync_inx_links --source obsidian`.

## Contrato

- Por cada `.md` detectado por `get_todas_notas()` (bajo `OBSIDIAN_ALPHA_PATH`): debe existir fila en `OBSIDIAN_DB` con `Ruta = <ruta_relativa>`.
- Por cada fila en `OBSIDIAN_DB` con `Ruta`: debe existir fila en `INX-ENLACES` con `Clave = obsidian:<Ruta>`.
- Caso simétrico: filas `OBSIDIAN_DB` cuya `Ruta` ya no existe en vault son **orphan DB rows** (se reportan como info, no bloquean).

## Flujo principal (happy path)

1. Previsualizar gap:
   ```bat
   python tools/backfill_obsidian_to_inx.py --dry-run
   ```
2. Aplicar backfill + sync:
   ```bat
   python tools/backfill_obsidian_to_inx.py --sync
   ```
3. Validar cobertura 100%:
   ```bat
   apps\validate_case_12.bat --no-pause
   ```

## Variantes

- **A. Solo backfill sin sync**: omite `--sync` si prefieres correr `sync_inx_links` manualmente después.
- **B. Con `orchestrator inx-sync`**: si también quieres incluir PTN/Todoist/otros en la misma pasada.

## Checklist ejecutable

### Paso 1 — Dry-run

```bat
.\.venv\Scripts\python.exe tools\backfill_obsidian_to_inx.py --dry-run
```

Lectura esperada:
- `[scan] vault_notas=N, OBSIDIAN_DB con Ruta=M, a backfillear=N-M`.
- Lista de hasta 5 ejemplos de rutas a crear.

### Paso 2 — Aplicar

```bat
.\.venv\Scripts\python.exe tools\backfill_obsidian_to_inx.py --sync
```

- [ ] Output: `[backfill] creadas OK: K`.
- [ ] Luego: `INX enlaces sincronizados: obsidian=N`.

### Paso 3 — Validar

```bat
apps\validate_case_12.bat --no-pause
```

- [ ] `Cobertura vault -> OBSIDIAN_DB: N/N`.
- [ ] `Cobertura OBSIDIAN_DB -> INX: N/N`.
- [ ] `OK: cobertura 100% vault -> OBSIDIAN_DB -> INX.`

## Postcondiciones / Resultado verificable

- Tras `--sync`: `|vault| == |OBSIDIAN_DB con Ruta| == |INX obsidian:*|`.
- `artifacts/obsidian_log_state.json` no se toca (backfill no afecta el estado mtime; `log_obsidian_changes` sigue funcionando normal).

## Criterios de aceptación (Definition of Done)

- [x] `tools/backfill_obsidian_to_inx.py` detecta notas vault sin fila `OBSIDIAN_DB` por diff de `Ruta`.
- [x] Idempotente: re-ejecutar sobre cobertura 100% no crea duplicados.
- [x] `--dry-run` previsualiza sin escribir.
- [x] `--sync` encadena `sync_inx_links --source obsidian`.
- [x] `tools/validate_case_12.py` reporta ambos deltas (vault→DB y DB→INX) + orphan DB rows (info).
- [x] Smoke end-to-end validado 2026-04-18: vault=29, OBSIDIAN_DB=28 → backfill +1 → 29/29/29 cobertura total.

## Automatización actual

| Acción | Comando |
| --- | --- |
| Backfill dry-run | `python tools/backfill_obsidian_to_inx.py --dry-run` |
| Backfill + sync | `python tools/backfill_obsidian_to_inx.py --sync` |
| Validación | `apps\validate_case_12.bat --no-pause` |

## Observabilidad

- `OBSIDIAN_DB` — espejo de notas.
- `INX-ENLACES` con prefijo `obsidian:`.
- Salida del validador muestra los tres totales (vault/DB/INX) y los deltas.

## Gaps (pendientes)

- **Gap 1 — No limpia orphan DB rows**: si una nota se borra del vault, la fila `OBSIDIAN_DB` queda. El validador la reporta como info pero no la toca. Para limpieza automática haría falta script `cleanup_obsidian_orphans.py` que marque como "Archivado" o borre la fila.
- **Gap 2 — `Fecha` usa mtime del fichero, no fecha real del journal**: para notas tipo `N<YYMMDD>-*` podríamos extraer la fecha del nombre. Hoy usamos `mtime`.
- **Gap 3 — No refleja renombrados**: si renombras una nota en el vault, backfill crea fila nueva (la ruta cambió) y la vieja queda huérfana. Para tracking de renames haría falta hash de contenido.
- **Gap 4 — No detecta notas fuera de `get_todas_notas`**: si `obsidian_tools.get_todas_notas` tiene filtros (p.ej. excluye subcarpetas sin ABC), backfill no las ve. Hoy no sabemos si hay filtros; habría que auditarlo.

## Mejoras propuestas

- **Mejora 1 — `tools/cleanup_obsidian_orphans.py`**: marca o borra filas `OBSIDIAN_DB` cuya `Ruta` ya no existe en vault. Con `--dry-run`.
- **Mejora 2 — Fecha desde nombre**: si stem matchea `N<YYMMDD>-*`, usar esa fecha en lugar de `mtime`.
- **Mejora 3 — Track renames**: detectar por similaridad de nombre entre orphan y nueva ruta, y actualizar fila existente.
- **Mejora 4 — `apps/backfill_obsidian.bat`**: wrapper Windows con flags `--dry-run` / `--sync`.

## Fallos típicos

- **`[scan] a backfillear=0`**: vault ya está 100% cubierto, caso validado. Normal en uso diario.
- **Muchos errores durante backfill**: suele ser rate limit de Notion. Re-ejecuta (es idempotente).
- **Orphan DB rows crecientes**: indica que estás borrando notas en vault sin limpiar `OBSIDIAN_DB`. Considerar Mejora 1.

## Validación práctica

```bat
apps\validate_case_12.bat --no-pause
```

El caso 12 queda **validado** cuando:
- `Cobertura vault -> OBSIDIAN_DB: N/N`.
- `Cobertura OBSIDIAN_DB -> INX: N/N`.
- Exit 0.
