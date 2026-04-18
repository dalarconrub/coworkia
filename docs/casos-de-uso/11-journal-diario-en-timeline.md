# Caso de uso: Journal diario ABGD integrado en timeline

## Objetivo

Que las **notas del journal personal** (`A0-GTD/B0C-PLA/C0C9-Notas/N<YYMMDD>-*.md`) aparezcan automáticamente como sección en el timeline diario (`artifacts/daily/YYYY-MM-DD.md`), al lado del chat multiagente, devlog, INX runs y sprints activos. Así un día cualquiera lee de un solo vistazo: _conversación operativa + desarrollos + pensamiento personal_.

## Actores

- **Usuario**: David
- **Sistema(s)**: Obsidian (vault ABGD), `tools/timeline.py`, `artifacts/daily/*.md`.

## Trigger

David escribe una entrada de journal en Obsidian (`C0C9-Notas`) y quiere que forme parte de la vista diaria agregada sin copiarla a ningún otro sitio.

## Precondiciones

- `.env` con `OBSIDIAN_ALPHA_PATH` (si falta, el timeline muestra `Sin journal` pero no falla).
- Estructura `A0-GTD/B0C-PLA/C0C9-Notas/` en el vault.
- Notas de journal con convención `N<YYMMDD>-<descripcion>.md`.

## Fuente de verdad (autoridad)

- **Reflexión personal**: Obsidian (el vault es el origen; nadie más escribe ahí).
- **Vista agregada temporal**: `artifacts/daily/YYYY-MM-DD.md` (regenerable, read-only).

## Contrato

- El timeline busca journals por **patrón de nombre** (`N<YYMMDD>-*.md`) dentro de `A0-GTD/B0C-PLA/C0C9-Notas/` recursivamente. Toma el primer match por día.
- La sección generada es:
  ```markdown
  ## Journal Obsidian (A0-GTD/B0C-PLA/C0C9-Notas)

  - `A0-GTD/B0C-PLA/C0C9-Notas/N<YYMMDD>-...md`
  ```
- Si hay varias notas con el mismo `YYMMDD`, solo se muestra una (primer match de `rglob`). Para un día con múltiples entradas de journal, se puede consolidar en una sola nota o crear subcarpetas.

## Flujo principal (happy path)

1. Escribir una entrada de journal:
   ```bat
   python agents/obsidian_agent.py nueva-nota A0-GTD B0C-PLA C0C9-Notas "Reflexion 2026-04-18" --fecha 2026-04-18
   ```
2. Regenerar el timeline de ese día:
   ```bat
   python tools/timeline.py --date 2026-04-18
   ```
3. Abrir `artifacts/daily/2026-04-18.md` y verificar que aparece la sección **Journal Obsidian** apuntando a la nota.
4. Validar con:
   ```bat
   apps\validate_case_11.bat --no-pause
   ```

## Checklist ejecutable

### Paso 1 — Crear (o editar) la entrada de journal

Convención de nombre: `N<YYMMDD>-<descripcion>.md`. La `descripcion` es libre.

### Paso 2 — Regenerar timeline

```bat
.\.venv\Scripts\python.exe tools\timeline.py --date <YYYY-MM-DD>
```

- [ ] Output: `escrito .../artifacts/daily/<day>.md`.

### Paso 3 — Validar

```bat
apps\validate_case_11.bat --no-pause
```

- [ ] Output: `OK: todos los journals detectados estan referenciados en su timeline.`

## Postcondiciones / Resultado verificable

- Cada nota bajo `C0C9-Notas` con formato `N<YYMMDD>-*` aparece en el timeline del día correspondiente.
- Si no hay journal, la sección sigue presente en el timeline con `- Sin journal para esta fecha.` (grácil, no rompe).

## Criterios de aceptación (Definition of Done)

- [x] `tools/timeline.py` carga `.env` (dotenv), resuelve `OBSIDIAN_ALPHA_PATH`, y tiene helper `_journal_for(day)` que devuelve `Path | None`.
- [x] `DailyBundle` extendido con `journal_path`.
- [x] `render_daily` emite la sección **Journal Obsidian**.
- [x] `tools/validate_case_11.py` cuenta journals en el vault, cruza con `artifacts/daily/*.md`, reporta gaps.
- [x] `apps/validate_case_11.bat` regenera timeline de hoy y valida.
- [x] Smoke end-to-end validado 2026-04-18: 1/1 journal detectado y referenciado tras crear nota de prueba.

## Automatización actual

| Acción | Comando |
| --- | --- |
| Crear entrada journal | `python agents/obsidian_agent.py nueva-nota A0-GTD B0C-PLA C0C9-Notas "<desc>" --fecha <YYYY-MM-DD>` |
| Regenerar timeline | `python tools/timeline.py [--date <YYYY-MM-DD> | --from ... --to ... | --days N]` |
| Validar | `apps\validate_case_11.bat --no-pause` |

## Observabilidad

- Vault `A0-GTD/B0C-PLA/C0C9-Notas/` — fuente.
- `artifacts/daily/<day>.md` — vista agregada.
- Regenerable en cualquier momento; no hay estado intermedio.

## Gaps (pendientes)

- **Gap 1 — Solo primer match por día**: si tienes varias notas con el mismo `YYMMDD` (ej. diario de mañana + tarde), solo aparece una. Para batch multi-journal habría que iterar todos los matches.
- **Gap 2 — Sin parsing de contenido**: el timeline solo lista el path. No extrae tags (`#foo`), encabezados, ni contenido. Para preview habría que leer el `.md` y resumir.
- **Gap 3 — No hay plantilla ni comando específico**: crear journal hoy requiere `obsidian_agent.py nueva-nota` con args. Podría existir `python tools/journal_new.py` con plantilla pre-rellenada (fecha, secciones tipo "Hoy hice / Pendientes / Reflexión").
- **Gap 4 — No cruza con INX**: el journal no genera fila `obsidian:<ruta>` en INX automáticamente (requiere `log_obsidian_changes` + sync obsidian, no encadenado por timeline). El timeline es solo visual.

## Mejoras propuestas

- **Mejora 1 — `tools/journal_new.py`**: crea entrada del día en `C0C9-Notas` con plantilla (Hoy hice / Pendientes / Reflexión / Enlaces relevantes) y, opcional `--sync`, encadena log + sync obsidian para que INX lo refleje.
- **Mejora 2 — Preview inline en timeline**: render del primer párrafo del journal como `blockquote` en la sección.
- **Mejora 3 — Multi-journal por día**: listar todos los matches en lugar del primero.
- **Mejora 4 — Tags del journal**: extraer `#foo` y listar en el timeline.

## Fallos típicos

- **Sección vacía**: no hay nota `N<YYMMDD>-*.md` para el día. Crear una o verificar el nombre.
- **`OBSIDIAN_ALPHA_PATH` no configurado**: timeline muestra `Sin journal` en todos los días. Verificar `.env`.
- **Journal en subcarpeta honda**: `rglob` lo encuentra igual; no es problema.

## Validación práctica

```bat
apps\validate_case_11.bat --no-pause
```

El caso 11 queda **validado** cuando:
- `Journals detectados` ≥ 1.
- `Con timeline y referencia correcta: N/N`.
- Exit 0 con `OK: todos los journals detectados estan referenciados en su timeline.`.
