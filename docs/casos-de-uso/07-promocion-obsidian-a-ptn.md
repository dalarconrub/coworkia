# Caso de uso: Promover nota Obsidian a PTN-Notas (opcional enlace a proyecto)

## Objetivo

Tomar una nota `.md` que ya vive en el vault Obsidian y **formalizarla como fila en PTN-Notas** (Notion), opcionalmente enlazada a un **proyecto PTN**, dejando la nota trazada por `OBSIDIAN_DB` + `INX-ENLACES` con clave `obsidian:<ruta>` y — deseablemente — con cruce a la fila `ptn:<id>` creada.

Es el **inverso** del caso 03: allí PTN lanza una nota, aquí Obsidian (pensamiento vivo) promociona a PTN cuando la nota deja de ser solo borrador.

## Actores

- **Usuario**: David
- **Sistema(s)**: Obsidian (fuente), Notion (PTN — `NOTION_DS_NOTAS`, `NOTION_DS_PROYECTOS`, `OBSIDIAN_DB`, `INX-ENLACES`)

## Trigger

Una nota en `B*/C*` del vault ha madurado: deja de ser exploración y pasa a ser **documento asociado a un proyecto/tarea formal**. No necesariamente cambia su contenido; cambia su estatus.

Ejemplos:
- Nota `N260316-Reunión con Enrique.md` en `A1-INV/B12-LAB/C126-DIR/P126.01-Tesis Fran/` pasa a ser acta oficial del proyecto.
- Nota exploratoria en `C0C9-Notas` que deja de ser inbox y se asigna a un proyecto PTN existente.

## Precondiciones

- `.env` con:
  - `OBSIDIAN_ABGD_ROOT`, `OBSIDIAN_ALPHA_PATH` (vault accesible)
  - `NOTION_DS_NOTAS` (obligatorio)
  - `NOTION_DS_PROYECTOS` (solo si se usa `--proyecto`)
  - `OBSIDIAN_DB`, `NOTION_DB_INX` (para cerrar trazabilidad en paso 3)
- La nota existe en el vault y está guardada (mtime reciente).

## Fuente de verdad (autoridad)

- **Contenido y ruta del documento**: Obsidian.
- **Existencia formal como nota de proyecto**: Notion PTN (`NOTION_DS_NOTAS`).
- **Trazabilidad cruzada**: `INX-ENLACES`.

## Contrato INX (claves canónicas)

| Sistema | Clave canónica |
| --- | --- |
| Nota Obsidian | `obsidian:<ruta_relativa_al_vault>` |
| Nota PTN (recién creada) | `ptn:<page_id>` (formato con guiones) |
| Proyecto PTN | `ptn:<proyecto_id>` |

El caso 07 **produce** las dos primeras y **cruza** con la tercera si hay `--proyecto`.

## Flujo principal (happy path)

1. Identificar la nota en el vault (nombre sin `.md` o nombre completo).
2. (Opcional) Identificar el proyecto PTN destino por ID o nombre/substring.
3. Ejecutar la promoción:
   ```bat
   .\.venv\Scripts\python.exe tools\promote_obsidian_to_ptn.py "N260316-Reunión con Enrique" --proyecto "P126.01-Tesis Fran"
   ```
   El script dedupa por `Título`: si ya existe, actualiza `Fecha` + `Proyecto`; si no, crea la fila.
4. Cerrar trazabilidad en INX (paso del caso 03):
   ```bat
   .\.venv\Scripts\python.exe tools\log_obsidian_changes.py
   apps\inx_sync_obsidian.bat 200 --no-pause
   ```
5. Verificar en Notion: fila en `NOTION_DS_NOTAS`, fila `obsidian:<ruta>` en `INX-ENLACES`, y — si aplica — relación al proyecto.

## Variantes

- **A. Sin proyecto**: omitir `--proyecto`. La nota queda en PTN-Notas sin vínculo; útil para ingesta masiva antes de decidir destino.
- **B. Por ID de proyecto**: `--proyecto 2a5622cf315b80229da5c5ac1de348b4`. Más rápido y sin ambigüedad si hay nombres similares.
- **C. Ya existe en PTN-Notas**: el script entra en rama `updated` y refresca `Fecha` + `Proyecto`. No crea duplicado.

## Checklist ejecutable

### Paso 1 — Promover

```bat
.\.venv\Scripts\python.exe tools\promote_obsidian_to_ptn.py "<nombre-nota>" [--proyecto "<ID o nombre>"]
```

- [ ] Output: `created: <titulo> (fecha=...) id=...` **o** `updated: ...`.
- [ ] Si `ValueError: Nota '<x>' no encontrada`: revisar que la nota exista bajo `OBSIDIAN_ALPHA_PATH`.
- [ ] Si `ValueError: Proyecto PTN '<x>' no encontrado`: usar ID exacto o nombre completo.

### Paso 2 — Log Obsidian → `OBSIDIAN_DB`

```bat
.\.venv\Scripts\python.exe tools\log_obsidian_changes.py
```

Necesario si la nota es nueva en el vault o su `mtime` cambió desde la última sync.

### Paso 3 — Sync a `INX-ENLACES`

```bat
apps\inx_sync_obsidian.bat 200 --no-pause
```

### Paso 4 — (Opcional) Cadena INX completa

```bat
.\.venv\Scripts\python.exe agents\orchestrator_agent.py inx-sync --limit 200
```

### Paso 5 — Verificación manual en Notion

- [ ] En **`NOTION_DS_NOTAS`**: fila con `Título = <nombre-sin-md>`, `Fecha = <mtime>`, `Ruta Obsidian = <ruta_relativa>`, y — si se pasó `--proyecto` — el campo `Proyecto` con el `page_id` resuelto.
- [ ] En **`OBSIDIAN_DB`**: fila con `Ruta = <ruta_relativa>`.
- [ ] En **`INX-ENLACES`**: fila con `Clave = obsidian:<ruta>`.

## Postcondiciones / Resultado verificable

- La nota PTN existe en `NOTION_DS_NOTAS` (creada o actualizada) y es idempotente por `Título`.
- La ruta Obsidian aparece tanto en `OBSIDIAN_DB` como en `INX-ENLACES` (`obsidian:<ruta>`).
- Si hubo `--proyecto`: el `page_id` del proyecto está persistido en la propiedad `Proyecto` de la nota PTN (como `rich_text`, no como `relation` — ver Gap 1).

## Criterios de aceptación (Definition of Done)

- [x] `promote_obsidian_to_ptn.py` retorna `created` o `updated` sin excepción.
- [x] Re-ejecutar el comando sobre la misma nota **no duplica** fila en PTN-Notas.
- [x] Ruta presente en `INX-ENLACES` con prefijo `obsidian:` tras el sync Obsidian.
- [x] La nota PTN recién creada aparece en `INX-ENLACES` con clave `ptn:<id>` tras `log_ptn_changes.py` + `sync_inx_links --source notion` (encadenado en `apps/validate_case_07.bat`).
- [x] Cruce `obsidian:<ruta>` ↔ `ptn:<id>` es navegable en INX en un solo salto — verificado el 2026-04-18 con 3/3 promociones en cruce doble tras ejecutar el bat.

## Automatización actual

| Acción | Comando |
| --- | --- |
| Promoción + cruce INX completo en un comando | `python tools/promote_obsidian_to_ptn.py <nombre> [--proyecto <ref>] [--tarea <ref>] --sync` |
| Promoción desde Windows (wrapper con pause) | `apps\promote_obsidian_to_ptn.bat "<nombre>" [--proyecto "<ref>"] [--tarea "<ref>"] [--sync]` |
| Promoción sin sync (solo escribe PTN-Notas) | `python tools/promote_obsidian_to_ptn.py <nombre> [--proyecto <ref>] [--tarea <ref>]` |
| Migración schema: Ruta Obsidian | `python tools/migrate_notas_ruta_obsidian.py` |
| Migración schema: Proyecto PTN / Tarea PTN (relations) | `python tools/migrate_notas_ptn_relations.py` |
| Limpieza legacy Proyecto/Tarea (rich_text) | `python tools/cleanup_notas_legacy_props.py` |
| Log Obsidian → Notion | `python tools/log_obsidian_changes.py` |
| Log PTN → NOTION_DB | `python tools/log_ptn_changes.py` |
| INX solo desde Obsidian | `apps\inx_sync_obsidian.bat` |
| Pipeline completo del caso 07 (validación) | `apps\validate_case_07.bat --no-pause` |
| Cadena INX completa multi-sistema | `python agents/orchestrator_agent.py inx-sync` |

## Observabilidad

- `NOTION_DS_NOTAS` — filas con `Título` + `Ruta Obsidian` (ruta relativa en vault) + `Proyecto`.
- `artifacts/obsidian_log_state.json` — estado de `last_mtime` del log.
- `INX-ENLACES` — filas `obsidian:<ruta>` y (si se dispara sync PTN) `ptn:<id>`.

## Gaps (pendientes)

- **Gap 1 — [RESUELTO] Proyecto/Tarea como `relation`**: `tools/migrate_notas_ptn_relations.py` añade props `Proyecto PTN` y `Tarea PTN` (relation single_property) y migra los IDs legacy. `promote_obsidian_to_ptn.py` detecta dinámicamente las nuevas props y escribe relations; si el schema no está migrado, cae al legacy `Proyecto` / `Tarea` (rich_text). Validado 2026-04-18 con promoción creando relation contra proyecto "Sofia" y relation contra ID de tarea directo.
- **Gap 2 — [RESUELTO] No sincroniza INX en el mismo paso**: flag `--sync` en `promote_obsidian_to_ptn.py` encadena `log_obsidian_changes` + `log_ptn_changes` + `sync_inx_links --source {obsidian,notion}` vía subprocess. Equivalente al bat pero en un solo comando.
- **Gap 3 — [RESUELTO] Cruce bidireccional automático**: cada promoción con `--sync` produce `obsidian:<ruta>` + `ptn:<id>` en INX-ENLACES. Validado 2026-04-18 con 5/5 cruce doble.
- **Gap 4 — [RESUELTO] `--tarea <T-ref>`**: implementado. Acepta ID directo o nombre (match case-insensitive contra propiedades `Nombre de la tarea`/`Nombre`/`Tarea`/`Título`).
- **Gap 5 — [RESUELTO] Validador**: `tools/validate_case_07.py` + `apps/validate_case_07.bat` implementados el 2026-04-18.

## Mejoras propuestas

- **Mejora 1 — [HECHO] `validate_case_07.py`**: implementado el 2026-04-18.
- **Mejora 2 — [HECHO] `--tarea <T-ref>`**: implementado el 2026-04-18 en `promote_obsidian_to_ptn.py`.
- **Mejora 3 — [HECHO] Sync INX inline**: flag `--sync` en el promote encadena log + sync de obsidian y notion.
- **Mejora 4 — [HECHO] Relación real a proyecto/tarea**: `tools/migrate_notas_ptn_relations.py` crea `Proyecto PTN` / `Tarea PTN` (relation) y migra IDs; el promote detecta y escribe relations.
- **Mejora 5 — [HECHO] `apps/promote_obsidian_to_ptn.bat`**: lanzador Windows implementado el 2026-04-18. Acepta los mismos flags que el CLI (`--proyecto`, `--tarea`, `--sync`). Imprime mensaje de uso si se invoca sin argumentos.
- **Mejora 6 — [HECHO] Limpieza de props legacy `Proyecto` / `Tarea` (rich_text)**: `tools/cleanup_notas_legacy_props.py` vacía las props legacy solo cuando la relation equivalente (`Proyecto PTN` / `Tarea PTN`) ya contiene el mismo UUID. Idempotente, `--dry-run`. Aplicado el 2026-04-18 (1 fila limpiada; re-run confirma 0 a limpiar).

## Fallos típicos

- **Nota no encontrada**: nombre escrito con `.md` sobrando, tildes mal codificadas, o nota fuera de `OBSIDIAN_ALPHA_PATH`. Usar `python agents/obsidian_agent.py buscar "<fragmento>"` para localizar.
- **Proyecto no encontrado**: `--proyecto` con substring demasiado genérico → devuelve el primer match; pasar ID exacto si hay ambigüedad.
- **INX no refleja la nota**: se saltó paso 2 o paso 3. El script de promoción **no** toca `OBSIDIAN_DB` ni `INX-ENLACES`.
- **Duplicado aparente**: PTN-Notas muestra dos filas con `Título` igual → una fue creada antes del dedup actual, o con capitalización distinta. Limpiar manualmente antes de re-promover.

## Validación práctica

Implementada el 2026-04-18:

```bat
apps\validate_case_07.bat --no-pause
```

El caso 07 quedará **validado** cuando el informe muestre:
- `PTN-Notas con Ruta Obsidian=<ruta>` coincide con `obsidian:*` en INX.
- Opcionalmente: fila `ptn:<id>` en INX por cada promoción.
