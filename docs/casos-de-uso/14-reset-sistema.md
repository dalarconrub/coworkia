# Caso de uso 14: Sistema de reseteo (Fases 1-4) — validación

## Objetivo

Validar que el sistema de reseteo — MAR Todoist / Notion PTN / Obsidian vault / orquestador general — funciona como especificado, no destruye datos, es idempotente y reversible. Deja una batería ejecutable (`tools/validate_case_14.py`) que comprueba el comportamiento sin tocar datos reales.

## Actores

- **Usuario**: David
- **Sistema(s)**: Todoist (MAR), Notion (PTN + INX), Obsidian (vault)

## Trigger

- Quieres vaciar el esqueleto operativo conservando todo para consulta (saturación, cambio de ciclo, reset de proyecto).
- Antes de invertir en una rotación real, quieres garantía de que los scripts hacen lo que dicen.

## Precondiciones

- `.env` con `TODOIST_API_KEY`, `NOTION_TOKEN`, los cuatro `NOTION_DS_*`, `NOTION_DB_INX`, `OBSIDIAN_ABGD_ROOT`.
- Propiedad `Archivo: Checkbox` ya creada en los 4 data sources (ejecuta `tools/ensure_archivo_field.py` una vez si no).
- `OBSIDIAN_ABGD_ROOT` apunta a un vault existente.

## Contrato (superficie bajo test)

| Script | Responsabilidad | Mutaciones |
| --- | --- | --- |
| `tools/reset_mar.py` | archivar tareas Todoist a `Z-INBOX` con marker reversible | `update_task`, `move_task` |
| `tools/ensure_archivo_field.py` | garantiza `Archivo: Checkbox` en 4 DS Notion | `PATCH /data_sources/{id}` |
| `tools/reset_notion.py` | flip `Archivo=true` en PTN + propagación INX | `PATCH /pages/{id}` |
| `tools/reset_obsidian.py` | rotar vault (estrategia C) + flip INX `obsidian:*` | `mkdir`, `copytree`, `PATCH /pages/{id}` |
| `tools/reset_all.py` | orquestar las 3 fases con abort-on-fail | subprocess chain |

## Matriz de tests

Marcas: **A**uto = cubierto por `validate_case_14.py`; **M**anual = requiere interacción o mutación real.

### Fase 1 — MAR

| # | Test | Tipo | Expectativa |
| --- | --- | --- | --- |
| 1.1 | `reset_mar.py --help` exit 0 | A | usage visible |
| 1.2 | `reset-all --dry-run --limit 2` | A | lista ≤2 candidatas, 0 escrituras, 0 errores |
| 1.3 | `reset-by-type idea --dry-run --limit 2` | A | todas clasificadas como Idea |
| 1.4 | `reset-overdue --days 3650 --dry-run` | A | sin candidatas (10 años = imposible en workspace limpio) o finito |
| 1.5 | `reset-by-project "__NO_EXISTE__" --dry-run` | A | exit !=0 con mensaje "Proyecto no encontrado" |
| 1.6 | `list-archived` | A | salida coherente (0 o N) |
| 1.7 | `restore NO_EXISTE` | A | exit !=0, mensaje "no encontrada en Z-INBOX" |
| 1.8 | Idempotencia: reset real → repetir reset → 2º run skip | M | verificable tras ejecución real |

### Fase 2 — Notion

| # | Test | Tipo | Expectativa |
| --- | --- | --- | --- |
| 2.1 | `ensure_archivo_field.py --dry-run` | A | 4 DS accesibles |
| 2.2 | `ensure_archivo_field.py` (real, idempotente) | A | `ya_existian=4` (si ya bootstrap) |
| 2.3 | `reset_notion.py --help` exit 0 | A | usage visible |
| 2.4 | `reset-ptn-proyectos --dry-run --limit 2` | A | plan sin escrituras + INX propagación reportada |
| 2.5 | `reset-ptn-tareas --dry-run --limit 2` | A | idem |
| 2.6 | `reset-ptn-notas --dry-run --limit 2` | A | idem |
| 2.7 | `list-archived --target all` | A | salida coherente |
| 2.8 | `reset-ptn-proyectos --dry-run --snapshot --limit 1` | A | JSON snapshot escrito y parseable |
| 2.9 | `restore <uuid-inventado>` | A | exit !=0 con mensaje "no encontrada" |
| 2.10 | INX propagación 100% (0 missing en dry-run) | A | `inx_missing=0` en el report |

### Fase 3 — Obsidian

| # | Test | Tipo | Expectativa |
| --- | --- | --- | --- |
| 3.1 | `reset_obsidian.py status` | A | muestra path + top-level + `Archivo` presente en INX |
| 3.2 | `rotate --dry-run --snapshot` | A | plan sin escrituras; usa ruta derivada `ABGD-yymmdd`; snapshot JSON escrito |
| 3.3 | `rotate --dry-run --new-vault-path <tmp>` | A | override explícito aceptado |
| 3.4 | `rotate --new-vault-path <misma ruta que OBSIDIAN_ABGD_ROOT>` | A | exit !=0, mensaje "no puede coincidir" |
| 3.5 | `rotate --new-vault-path <existente no vacía>` sin `--force` | A | exit !=0, mensaje "ya existe y no esta vacia" |
| 3.6 | `list-archived` | A | lista filas `obsidian:*` con `Archivo=true` |
| 3.7 | `restore --from NO_EXISTE` | A | exit !=0, mensaje "no existe" |
| 3.8 | `rotate --depth 1 --dry-run` | A | ≤5 dirs replicadas (solo top-level áreas) |
| 3.9 | `rotate --depth 3 --dry-run` (default) | A | 30-100 dirs replicadas (orden de magnitud correcto) |

### Fase 4 — reset_all (orquestador)

| # | Test | Tipo | Expectativa |
| --- | --- | --- | --- |
| 4.1 | `reset_all.py --help` exit 0 | A | usage visible |
| 4.2 | `reset_all --dry-run --mar-limit 1 --notion-limit 1` | A | `[OK] MAR`, `[OK] Notion`, `[OK] Obsidian` con ruta derivada |
| 4.3 | `reset_all --dry-run ... --obsidian-new-vault-path <tmp>` | A | las 3 fases `[OK]` usando override explícito |
| 4.4 | `reset_all --dry-run --skip-mar --skip-obsidian --notion-limit 1` | A | solo Notion corre |
| 4.5 | Límites se propagan correctamente | A | output de cada fase refleja el limit |
| 4.6 | Sin `--yes` y sin `--dry-run` → pide confirmación interactiva | M | difícil de automatizar |
| 4.7 | Política abort: si fase N falla, N+1 no corre | M | requiere simular fallo |

### Cross-phase

| # | Test | Tipo | Expectativa |
| --- | --- | --- | --- |
| C.1 | Sintaxis de los 5 scripts (py_compile) | A | 0 errores |
| C.2 | `memory_check.py` OK antes y después de la batería | A | exit 0 |
| C.3 | Conteo de filas INX invariante (dry-run no muta) | A | counts iguales antes/después |
| C.4 | Nodos del atlas presentes en `pipeline_gui.py _build_atlas()` | A | 4 nodos reset_* localizados |

## Flujo principal (uso del validador)

```bash
python tools/validate_case_14.py
```

- Ejecuta la batería **A** completa (~20 tests) contra tu `.env`.
- Usa siempre `--dry-run` para las operaciones mutativas; `ensure_archivo_field` sí se ejecuta en real porque es idempotente.
- Exit 0 si todos pasan, 1 si alguno falla.
- Output: tabla `[PASS]/[FAIL]` por test + `[SKIP]` para los manuales no automatizables.

### Wrapper Windows

```
apps\validate_case_14.bat
```

## Postcondiciones

- Ningún fichero de datos modificado.
- INX no muta (dry-run en todo lo mutativo excepto `ensure_archivo_field` que es idempotente).
- Snapshots dry-run sí se crean en `artifacts/resets/YYYY-MM-DD/` (son auto-limpiables por convención; no afectan producción).
- Vaults / Todoist / Notion quedan **idénticos al estado pre-test**.

## Comportamiento garantizado: relaciones curadas INX→PTN preservadas

**Lo que SÍ hace `reset_notion.py` en INX:** flip del campo `Archivo: Checkbox` (true cuando archiva la fuente PTN, false al restaurar). Una sola propiedad. Línea de referencia: `_flip_archivo` en [tools/reset_notion.py](../../tools/reset_notion.py).

**Lo que NO toca:** ninguna `relation` (`PTN Proyecto`, `PTN Tarea`, `PTN Nota`, `KIT`, `Area`, `Bloque`, `Contexto`), ni `URL`, ni `Detalle`, ni `Fuente`, ni `Estado`. Las relaciones curadas vía `link_repo_to_ptn` / `link_paper_to_ptn` / `link_article_to_ptn` quedan intactas tras cualquier reset.

**Comportamiento de los syncs post-reset:** las funciones `_sync_github`, `_sync_paperpile` y `_sync_kit` en [tools/sync_inx_links.py](../../tools/sync_inx_links.py) **NO incluyen `Estado` en el payload de upsert** — esto preserva `Estado=Verificado` puesto por los helpers `link_*_to_ptn`. Las relaciones tampoco están en el payload, así que se preservan (Notion API no toca propiedades omitidas).

**Asimetría intencional:** `_sync_todoist`, `_sync_ptn_log`, `_sync_obsidian` SÍ setean `Estado` porque no tienen helper `link_*_to_ptn` asociado — su Estado es derivado del origen o placeholder. Si se añade un `link_*_to_ptn` para esas fuentes, aplicar el mismo patrón.

**Trade-off conocido:** filas `github:*`, `paperpile:*`, `kit:*` creadas por sync (sin previo link) quedan **sin `Estado`** hasta que se vinculen vía `link_*_to_ptn` o se establezca manualmente. Estado es metadato curado, no derivado.

**Validación empírica del 2026-04-24** (entrada devlog `[INX] Investigacion cierre: regresion github:coworkia NO causada por reset ni por sync actual`):
- `link_repo_to_ptn('coworkia', 'Arquitectura Coworkia v2')` → `Estado=Verificado`, `PTN Proyecto=[<id>]`
- `python tools/sync_inx_links.py --source github` → ambos campos persisten sin cambios.

**Implicación operativa:** un reset NO destruye los enlaces curados a proyectos PTN. No hace falta un script de "snapshot/restore de relaciones" alrededor del flujo de reset.

## Definition of Done

- [ ] Todos los tests **A** pasan (`validate_case_14.py` exit 0).
- [ ] Los tests **M** ejecutados manualmente al menos una vez con resultado documentado.
- [ ] Los 4 nodos reset en `apps/pipeline_gui.py _build_atlas()` siguen presentes.
- [ ] `memory_check.py` OK al terminar.
- [ ] Si aparece un `[FAIL]` y es un bug del sistema de reseteo, se corrige en el mismo turno antes de cerrar el caso (entrada `[TOOLING]` en devlog).

## Gaps conocidos

- **Gap 1**: los tests 1.8, 4.6, 4.7 no son auto-ejecutables. 1.8 requiere ejecución real. 4.6 requiere stdin interactivo. 4.7 requiere simular un fallo en `reset_mar.py` (vía mock o env inválida).
- **Gap 2**: el validador no comprueba que `restore` funcione end-to-end tras un reset real. Eso requiere ciclo ejecutivo completo (reset → restore → verificar). Planteado para iteración futura.
- **Gap 3**: los snapshots dry-run se acumulan en `artifacts/resets/YYYY-MM-DD/` — no hay limpieza automática. Si quieres ordenar, borra la carpeta del día tras validar.

## Checklist manual pendiente — Sprint 2 / ST-203

Estos son los tres checks manuales que siguen abiertos tras la batería automática. La idea no es ejecutarlos siempre, sino dejar un protocolo claro para cuando David decida cerrar la validación manual del sistema de reseteo.

| Test | Owner | Cuándo ejecutarlo | Comando / acción | Evidencia a guardar | Criterio de cierre |
| --- | --- | --- | --- | --- | --- |
| 1.8 Idempotencia MAR | David | Cuando haya un subconjunto pequeño y seguro de tareas reales que pueda moverse a `Z-INBOX` sin riesgo operativo | 1. `python tools/reset_mar.py reset-all --limit 1` 2. repetir el mismo comando 3. `python tools/reset_mar.py list-archived` | salida de ambos runs + listado final en chat/devlog | el segundo run no vuelve a archivar la misma tarea; reporta skip/idempotencia y `restore` sigue siendo viable |
| 4.6 Prompt interactivo de `reset_all.py` | David | Antes de una primera ejecución real de `reset_all.py` sin `--yes` | lanzar `python tools/reset_all.py --mar-limit 1 --notion-limit 1` sin `--dry-run` ni `--yes`, responder `n` en el prompt | transcript o captura del prompt en terminal | el orquestador pide confirmación explícita y aborta limpio al responder `n`, sin ejecutar fases posteriores |
| 4.7 Abort-on-fail entre fases | Codex + David | Cuando se quiera demostrar la política de abort sin tocar producción; idealmente en entorno controlado o con credencial inválida temporal en shell hija | ejecutar `reset_all.py` en una shell hija con una credencial inválida solo para la fase 1 o 2 y comprobar que no arranca la siguiente | salida completa del comando + nota en devlog | el summary marca `[FAIL]` en la fase forzada a fallar, no ejecuta la siguiente, e imprime comandos de restore consistentes |

### Protocolo de documentación manual

Cuando cualquiera de estos tres checks se ejecute:

1. Añade el resultado al chat del día con `MEMORIA:` si cambia la operativa.
2. Registra entrada en `devlog/DEVLOG.md` con área `MULTIAGENT` o `TOOLING`.
3. Si el resultado permite cerrar el gap, marca la fila correspondiente en este documento y ajusta la sección `Definition of Done`.

## Mejoras propuestas

- **Mejora 1**: automatizar 4.7 simulando una `TODOIST_API_KEY` vacía en un entorno hijo y verificando que `reset_all.py` aborta tras `[FAIL] MAR` sin correr Notion/Obsidian.
- **Mejora 2**: `validate_case_14.py --cleanup` para borrar snapshots de la fecha tras validación.
- **Mejora 3**: cycle-test (reset real → restore) sobre un workspace de test dedicado, no producción.
