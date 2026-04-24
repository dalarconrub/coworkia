# Caso de uso: Wikilinks cross-system en notas Obsidian (con auditoría INX)

## Objetivo

Permitir que una nota Obsidian cite entidades de **otros sistemas** (`PTN`, `KIT`, `Paperpile`, `Todoist`, `GitHub`) usando una sintaxis `[[<prefix>:<id>]]` homóloga a los wikilinks internos, y **auditar** que todos los IDs referenciados existan en `INX-ENLACES`. Cierra el gap operativo: Obsidian no resuelve nativamente wikilinks fuera del vault, y hasta hoy no había forma de detectar referencias rotas cross-system.

## Actores

- **Usuario**: David
- **Sistema(s)**: Obsidian (vault), Notion (`INX-ENLACES`).

## Trigger

Estás escribiendo una nota de proyecto/diario/revisión y quieres dejar una referencia formal a una entidad externa: un proyecto PTN, una entrada KIT, un paper BIB, una tarea Todoist o un repo GitHub — sin copiar URLs ni IDs sueltos.

## Precondiciones

- `.env` con `NOTION_DB_INX`, `OBSIDIAN_ALPHA_PATH`.
- `INX-ENLACES` sincronizado (`orchestrator inx-sync` reciente).

## Fuente de verdad (autoridad)

- **Referencias en prosa**: Obsidian.
- **Existencia de la entidad**: INX-ENLACES (proxy de todas las bases origen).

## Contrato (sintaxis)

Dentro del markdown de una nota:

```markdown
[[ptn:<page_id>]]           # proyecto/tarea/nota PTN (Notion)
[[kit:<page_id>]]           # entrada KIT
[[paperpile:<citekey>]]     # paper BIB
[[todoist:<task_id>]]       # tarea Todoist
[[github:<nombre_repo>]]    # repo GIT
```

- Se aceptan UUIDs con o sin guiones para `ptn` y `kit` (matching normalizado).
- `paperpile`, `todoist` y `github` hacen match exacto de string.
- Se diferencian de los wikilinks nativos de Obsidian (`[[Nota]]`) por el prefijo `<sistema>:`.

## Contrato (resolución)

- **Válido**: la `Clave` `<prefix>:<id>` existe en `INX-ENLACES`.
- **Roto**: el id no está en INX. Puede ser porque la entidad no existe, o porque su sistema no se ha sincronizado aún contra INX (`sync_inx_links --source <x>` pendiente).

## Flujo principal (happy path)

1. Escribe tu nota y añade referencias con la sintaxis `[[<prefix>:<id>]]`.
2. Guarda.
3. Audita el vault:
   ```bat
   python tools/obsidian_wikilinks.py audit
   ```
4. Si hay rotos: o (a) corre el sync del sistema afectado, o (b) corrige el id en la nota.
5. Busca notas que mencionan un link concreto:
   ```bat
   python tools/obsidian_wikilinks.py find ptn:343622cf-315b-80d4-8b0f-e8a0c71808bd
   ```

## Subcomandos de `tools/obsidian_wikilinks.py`

| Comando | Descripción |
| --- | --- |
| `audit` | Escanea todo el vault, lista wikilinks por prefijo, valida contra INX, reporta rotos con ubicación. |
| `find <prefix>:<id>` | Lista las notas que mencionan un wikilink específico (útil para "¿quién cita este proyecto?"). |

## Checklist ejecutable

### Paso 1 — Inserta wikilinks en tus notas

```markdown
Este análisis se apoya en la metodología [[kit:340622cf-315b-814b-bf50-e20378365646]]
y pertenece al proyecto [[ptn:343622cf-315b-80d4-8b0f-e8a0c71808bd]].
```

### Paso 2 — Audita

```bat
.\.venv\Scripts\python.exe tools\obsidian_wikilinks.py audit
```

Lectura esperada:
- Totales por prefijo.
- Hasta 3 ejemplos por prefijo con ubicación `(ruta L<n>)`.
- Lista de rotos con ubicación exacta.
- Exit 0 si nada roto; 1 si hay rotos.

### Paso 3 — Validación como caso

```bat
apps\validate_case_13.bat --no-pause
```

Equivalente a `audit` con exit code propagado.

### Paso 4 — Búsqueda inversa

```bat
.\.venv\Scripts\python.exe tools\obsidian_wikilinks.py find ptn:<uuid>
```

## Postcondiciones / Resultado verificable

- El vault puede contener referencias navegables a cualquier entidad de los 5 sistemas.
- Cualquier ruptura (entidad borrada, id mal escrito, sistema sin sync) se detecta en la próxima auditoría.
- `find` devuelve ubicaciones exactas de cada mención.

## Criterios de aceptación (Definition of Done)

- [x] `tools/obsidian_wikilinks.py` con `scan_vault()`, regex `WIKILINK_RE` que matchea los 5 prefijos, `audit` y `find`.
- [x] `audit` resuelve contra INX (con normalización UUID para `ptn`/`kit`).
- [x] `find` imprime ruta + número de línea + contenido de la línea.
- [x] `tools/validate_case_13.py` alias de `audit` con exit code.
- [x] `apps/validate_case_13.bat`.
- [x] Smoke end-to-end validado 2026-04-18: nota de prueba con 3 wikilinks (1 kit válido, 1 ptn válido, 1 ptn roto) → audit reporta 3 detectados, 1 roto con ubicación exacta (L11). `find` por el kit devuelve la nota correcta con L7.

## Automatización actual

| Acción | Comando |
| --- | --- |
| Audit completo | `python tools/obsidian_wikilinks.py audit` |
| Find por id | `python tools/obsidian_wikilinks.py find <prefix>:<id>` |
| Validación como caso | `apps\validate_case_13.bat --no-pause` |

## Observabilidad

- El propio vault es la fuente; cualquier `.md` puede contener wikilinks.
- INX-ENLACES es el resolver.
- Output del `audit` muestra ruta + línea → navegable desde cualquier editor.

## Gaps (pendientes)

- **Gap 1 — No hay comando para convertir a URL / abrir**: `audit` y `find` solo localizan; no abren el navegador en la entidad Notion/Todoist correspondiente. Se podría añadir `tools/obsidian_wikilinks.py open <prefix>:<id>` que mapee a URL conocida.
- **Gap 2 — Sin autocomplete**: al escribir wikilinks en Obsidian no hay sugerencias de IDs válidos. Requiere saber/copiar el UUID.
- **Gap 3 — INX debe estar al día**: un `audit` falsamente "roto" puede deberse a que INX no ha sincronizado. Mitigación: correr `orchestrator inx-sync` antes.
- **Gap 4 — No se extrae contexto a INX**: los wikilinks no generan fila INX de cruce (ej. enlazar `obsidian:<ruta>` ↔ `ptn:<id>` con una relación explícita en INX). Son solo prosa auditable.

## Mejoras propuestas

- **Mejora 1 — Subcomando `open`**: mapea `<prefix>:<id>` a URL (Notion page URL, DOI, GitHub repo URL, Todoist task URL) y lanza navegador.
- **Mejora 2 — Plugin Obsidian** o snippet que autocomplete desde INX.
- **Mejora 3 — Enriquecer `_sync_obsidian`**: que parsee wikilinks en la ruta de la nota y cree filas INX de cruce (obsidian:<ruta> con relations a ptn/kit/etc.).
- **Mejora 4 — `--fix-ptn-unnormalized`**: normaliza UUIDs de ptn/kit (añade guiones) en las notas para consistencia.

## Fallos típicos

- **`Wikilinks detectados: 0`**: el vault no usa todavía la sintaxis. Empieza por insertar uno y reaudita.
- **Roto aunque la entidad existe**: INX sin sync. Corre `orchestrator inx-sync --limit 200`.
- **UUID mal escrito**: error de copia; el audit señala la línea.

## Validación práctica

```bat
apps\validate_case_13.bat --no-pause
```

El caso 13 queda **validado** cuando:
- Wikilinks detectados ≥ 1 (al menos un caso de uso real).
- Rotos = 0.
- Exit 0 con `OK: todos los wikilinks cross-system resuelven contra INX.`.
