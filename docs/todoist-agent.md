# Todoist Agent - Guia de uso

Agente para gestion de tareas en Todoist siguiendo el sistema **MAR (Meta-Accion-Resultado)**.

---

## Tipos MAR

| Tipo | Regla temporal | Ejemplo |
|------|----------------|---------|
| **Idea** | Sin fecha ni deadline | Captura de pensamiento |
| **Meta** | Fecha sin hora, no recurrente | Compromiso puntual de un dia |
| **Habito** | Recurrente, sin deadline | Rutina diaria |
| **Tarea** | Deadline o compromiso flexible con fecha | Trabajo con vencimiento |
| **Evento** | Hora fija | Reunion, cita |

---

## Comandos

### Ver estado del sistema

```bash
python agents/todoist_agent.py hoy
python agents/todoist_agent.py estado
```

### Explorar y buscar

```bash
python agents/todoist_agent.py listar idea
python agents/todoist_agent.py listar meta
python agents/todoist_agent.py listar habito
python agents/todoist_agent.py listar tarea
python agents/todoist_agent.py listar evento
python agents/todoist_agent.py proyectos
python agents/todoist_agent.py buscar "tesis"
python agents/todoist_agent.py ver <TASK_ID>
```

Para listar el inbox operativo normal desde script, usa el proyecto Todoist `Inbox`
(`project_id=6Crfvj4MWg6GfVq6`). Los proyectos `Z-*` no forman parte del arranque
diario normal.

### Crear acciones

```bash
python agents/todoist_agent.py idea "Explorar integracion con Zotero"
python agents/todoist_agent.py meta "Entregar informe borrador" 2026-03-20
python agents/todoist_agent.py habito "Revisar bandeja de entrada" "every day"
python agents/todoist_agent.py tarea "Corregir examenes" 2026-03-25
python agents/todoist_agent.py evento "Reunion con Christian" 2026-03-18T10:00:00
python agents/todoist_agent.py capturar "Nueva entrada rapida"
```

### Gestionar acciones existentes

```bash
python agents/todoist_agent.py completar <TASK_ID>
python agents/todoist_agent.py borrar <TASK_ID>
python agents/todoist_agent.py mover <TASK_ID> <PROJECT_ID>

python agents/todoist_agent.py editar <TASK_ID> --content "Nuevo titulo"
python agents/todoist_agent.py editar <TASK_ID> --due-date 2026-04-15
python agents/todoist_agent.py editar <TASK_ID> --due-datetime 2026-04-15T10:00:00
python agents/todoist_agent.py editar <TASK_ID> --deadline-date 2026-04-20
python agents/todoist_agent.py editar <TASK_ID> --clear-due --clear-deadline

python agents/todoist_agent.py reclasificar <TASK_ID> idea
python agents/todoist_agent.py reclasificar <TASK_ID> meta --valor 2026-04-15
python agents/todoist_agent.py reclasificar <TASK_ID> habito --valor "every day"
python agents/todoist_agent.py reclasificar <TASK_ID> tarea --valor 2026-04-20
python agents/todoist_agent.py reclasificar <TASK_ID> evento --valor 2026-04-15T10:00:00

python agents/todoist_agent.py procesar <TASK_ID> meta <PROJECT_ID> --valor 2026-04-15
```

### Flujo operativo diario recomendado

```bash
python agents/todoist_agent.py estado
python -c "from tools.todoist_tools import get_tasks; tasks=get_tasks(project_id='6Crfvj4MWg6GfVq6'); print(f'Inbox: {len(tasks)}'); [print(f\"{t['id']} | {t['content']}\") for t in tasks]"
python agents/todoist_agent.py ver <TASK_ID>
python agents/todoist_agent.py mover <TASK_ID> <PROJECT_ID>
python tools/sync_todoist_to_notion.py --limit 200
python tools/sync_inx_links.py --source todoist --limit 200
```

Lectura del pipeline:

1. `estado` da el volumen MAR activo.
2. El inbox normal de Todoist se revisa como cola de entrada diaria.
3. Cada entrada se deja en un proyecto A/B liviano (`B12-LAB`, `B13-PUB`, etc.).
4. `sync_todoist_to_notion.py` actualiza el espejo `TODOIST-TAREAS`.
5. `sync_inx_links.py --source todoist` actualiza `INX-ENLACES` desde ese espejo.

---

## Nota de modelo

Coworkia aplica la clasificacion MAR localmente a partir de los datos de Todoist. Esto evita depender de filtros ambiguos de la API y mantiene el control conceptual del sistema dentro del proyecto.

---

## Estructura alineada con Notion

Todoist mantiene una estructura mínima para **alinear nombres** con la taxonomía ABC,
pero la clasificación fina se hace en Notion.

Reglas:

- **Todoist ejecuta** (MAR y tiempo).
- **Notion clasifica** (Área/Bloque/Contexto).

### Proyectos A/B en Todoist

Usa los proyectos `A*` y `B*` solo como contenedores livianos para agrupar ejecución
por grandes áreas. No dupliques taxonomía fina allí.

Proyectos activos esperados:

- Áreas: `A0-GTD`, `A1-INV`, `A2-UNI`, `A3-VIT`, `A4-ARX`
- Bloques: `B00-GTD`, `B0A-INX`, `B0B-ABC`, `B0C-PLA`,
  `B10-INV`, `B11-CVT`, `B12-LAB`, `B13-PUB`,
  `B20-UNI`, `B24-DOC`, `B25-FOR`, `B26-GES`,
  `B30-VIT`, `B37-ORG`, `B38-TEC`, `B39-DES`,
  `B40-REF`, `B4X-BIB`, `B4Y-KIT`, `B4Z-GIT`

### Secciones C en A0

Dentro de los bloques `A0` (B00/B0A/B0B/B0C) se crean secciones C:

- `B00-GTD`: `C000-GTD`
- `B0A-INX`: `C0A1-TODOIST`, `C0A2-NOTION`, `C0A3-OBSIDIAN`
- `B0B-ABC`: `C0B4-AREA`, `C0B5-BLOQUE`, `C0B6-CONTEXTO`
- `B0C-PLA`: `C0C7-PROYECTOS`, `C0C8-TAREAS`, `C0C9-NOTAS`

### Zonas Z-*

Los proyectos `Z-*` son buffers de entrada y limpieza.
Por defecto se ignoran en análisis operativos (salvo que se pida explícitamente).
No se usan como "inbox" diario: `Z-INBOX` y el resto de `Z-*` son back/staging.

### Sync a Notion (B0A-INX)

Espejo operativo normal:

```bash
python tools/sync_todoist_to_notion.py --limit 200
```

El sync hace upsert en `TODOIST-TAREAS` por `Todoist ID`, actualiza propiedades
disponibles en el schema y excluye `Z-*`.

Propagación a INX:

```bash
python tools/sync_inx_links.py --source todoist --limit 200
```

Para marcar completadas por diferencia contra un snapshot de activos se usa el
modo batch avanzado `--save-active` / `--finalize-completed`; no forma parte del
sync diario simple.

---

## API usada

- **Todoist API v1** - `https://api.todoist.com/api/v1/`
- Token en `.env` -> `TODOIST_API_KEY`
