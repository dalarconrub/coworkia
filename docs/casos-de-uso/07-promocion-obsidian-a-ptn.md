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
- [x] Ruta presente en `INX-ENLACES` con prefijo `obsidian:` tras paso 3.
- [ ] La nota PTN recién creada aparece en `INX-ENLACES` con clave `ptn:<id>` (hoy requiere pasada extra de sync desde PTN; ver Gap 2).
- [ ] Cruce `obsidian:<ruta>` ↔ `ptn:<id>` es navegable en INX en un solo salto (ver Gap 3).

## Automatización actual

| Acción | Comando |
| --- | --- |
| Promoción Obsidian → PTN-Notas | `python tools/promote_obsidian_to_ptn.py <nombre> [--proyecto <ref>]` |
| Log Obsidian → Notion | `python tools/log_obsidian_changes.py` |
| INX solo desde Obsidian | `apps\inx_sync_obsidian.bat` |
| Cadena INX completa | `python agents/orchestrator_agent.py inx-sync` |

## Observabilidad

- `NOTION_DS_NOTAS` — filas con `Título` + `Ruta Obsidian` (ruta relativa en vault) + `Proyecto`.
- `artifacts/obsidian_log_state.json` — estado de `last_mtime` del log.
- `INX-ENLACES` — filas `obsidian:<ruta>` y (si se dispara sync PTN) `ptn:<id>`.

## Gaps (pendientes)

- **Gap 1 — Proyecto como `rich_text`, no `relation`**: el script guarda `pid` como texto plano en la propiedad `Proyecto`. Esto evita depender del schema relacional de Notion pero rompe navegación nativa Notion. Decisión pendiente: ¿migrar a `relation` real contra `NOTION_DS_PROYECTOS`?
- **Gap 2 — No sincroniza INX en el mismo paso**: el script promociona pero no crea fila `ptn:<id>` en `INX-ENLACES`. Hoy hace falta una pasada posterior (`orchestrator_agent.py inx-sync` o sync desde fuente PTN-Notas).
- **Gap 3 — Falta el cruce bidireccional automático**: no existe lógica que, al detectar `obsidian:<ruta>` y una nueva fila `ptn:<id>` derivada de esa misma ruta, las enlace entre sí en INX. Mismo gap que caso 03 lista como "comando único `link-obsidian-to-ptn`".
- **Gap 4 — Solo acepta `--proyecto`, no `--tarea`**: una nota puede promocionarse asociada a una tarea PTN, no solo a un proyecto. Desde 2026-04-18 la ruta relativa vive en `Ruta Obsidian` (no en `Tarea`), así que `Tarea` queda libre para su semántica original de relación a tarea PTN. Falta implementar `--tarea` en `promote_obsidian_to_ptn.py` (Mejora 2).
- **Gap 5 — Sin validador**: no existe `tools/validate_case_07.py` análogo al del caso 03.

## Mejoras propuestas

- **Mejora 1 — `validate_case_07.py`**: contar filas PTN-Notas con `Ruta Obsidian` no vacía, cruzar contra `OBSIDIAN_DB.Ruta` y `INX-ENLACES` (`obsidian:*` + `ptn:*` con esa ruta). Reportar rutas promocionadas sin cruce INX. La propiedad a leer es `Ruta Obsidian` (tras migración `tools/migrate_notas_ruta_obsidian.py`), no `Tarea`.
- **Mejora 2 — `--tarea <T-code>`** en `promote_obsidian_to_ptn.py`, resolviendo contra `NOTION_DS_TAREAS` (si existe) con el mismo patrón que `_resolve_project_id`.
- **Mejora 3 — Sync INX inline**: tras crear/actualizar la fila en PTN-Notas, el script puede disparar un upsert directo a `INX-ENLACES` con clave `ptn:<id>` y propiedad `Obsidian Ruta = <ruta>`, eliminando la necesidad del paso 3 manual.
- **Mejora 4 — Relación real a proyecto**: convertir `Proyecto` en `relation` si David confirma. Implica migración de filas existentes.
- **Mejora 5 — `apps/promote_obsidian_to_ptn.bat`**: lanzador análogo a `log_ptn_changes.bat` para el flujo manual desde Windows.

## Fallos típicos

- **Nota no encontrada**: nombre escrito con `.md` sobrando, tildes mal codificadas, o nota fuera de `OBSIDIAN_ALPHA_PATH`. Usar `python agents/obsidian_agent.py buscar "<fragmento>"` para localizar.
- **Proyecto no encontrado**: `--proyecto` con substring demasiado genérico → devuelve el primer match; pasar ID exacto si hay ambigüedad.
- **INX no refleja la nota**: se saltó paso 2 o paso 3. El script de promoción **no** toca `OBSIDIAN_DB` ni `INX-ENLACES`.
- **Duplicado aparente**: PTN-Notas muestra dos filas con `Título` igual → una fue creada antes del dedup actual, o con capitalización distinta. Limpiar manualmente antes de re-promover.

## Validación práctica (pendiente de implementar)

Cuando exista la Mejora 1:

```bat
apps\validate_case_07.bat --no-pause
```

El caso 07 quedará **validado** cuando el informe muestre:
- `PTN-Notas con Ruta Obsidian=<ruta>` coincide con `obsidian:*` en INX.
- Opcionalmente: fila `ptn:<id>` en INX por cada promoción.
