# Todoist Agent — Guía de uso

Agente para gestión de tareas en Todoist siguiendo el sistema **MAR (Meta-Acción-Resultado)**.

---

## Tipos MAR

| Tipo | Regla temporal | Ejemplo |
|------|----------------|---------|
| **Idea** | Sin fecha ni deadline | Captura de pensamiento |
| **Meta** | Deadline sin hora, no recurrente | Compromiso puntual de un día |
| **Hábito** | Recurrente, sin deadline | Rutina diaria |
| **Tarea** | Deadline sin hora | Trabajo flexible con fecha límite |
| **Evento** | Hora fija | Reunión, cita |

---

## Comandos

### Ver estado del sistema

```bash
# Resumen de tareas para hoy clasificadas por tipo MAR
python agents/todoist_agent.py hoy

# Conteo de todas las acciones por tipo MAR
python agents/todoist_agent.py estado
```

### Listar por tipo

```bash
python agents/todoist_agent.py listar idea
python agents/todoist_agent.py listar meta
python agents/todoist_agent.py listar habito
python agents/todoist_agent.py listar tarea
python agents/todoist_agent.py listar evento
```

### Crear acciones

```bash
# Idea — sin fecha
python agents/todoist_agent.py idea "Explorar integración con Zotero"

# Meta — compromiso de un día (YYYY-MM-DD)
python agents/todoist_agent.py meta "Entregar informe borrador" 2026-03-20

# Hábito — recurrente
python agents/todoist_agent.py habito "Revisar bandeja de entrada" "every day"
python agents/todoist_agent.py habito "Revisión semanal GTD" "every monday"

# Tarea — trabajo con deadline
python agents/todoist_agent.py tarea "Corregir exámenes" 2026-03-25

# Evento — hora fija (ISO 8601)
python agents/todoist_agent.py evento "Reunión con Christian" "2026-03-18T10:00:00"
```

---

## Filtros MAR en Todoist

Puedes usar estos filtros directamente en Todoist:

| Tipo | Filtro |
|------|--------|
| Idea | `no date & no deadline` |
| Meta | `!recurring & !!no time & !no deadline` |
| Hábito | `recurring & no time & no deadline` |
| Tarea | `no time & !no deadline` |
| Evento | `!no time` |

### Horizontes temporales

| Horizonte | Filtro |
|-----------|--------|
| Hoy | `(!#Z-* & !search:*) & (overdue \| due before: +1 day)` |
| 1 día | `(!#Z-* & !search:*) & due after: yesterday & due before: +2day` |
| 1 semana | `(!#Z-* & !search:*) & due after: today & due before: +7day` |
| 1 mes | `(!#Z-* & !search:*) & (due after: +7 days & due before: +30 days)` |
| 1 año | `(!#Z-* & !search:*) & (due after: +30 days & due before: +365 days)` |

---

## API usada

- **Todoist API v1** — `https://api.todoist.com/api/v1/`
- Token en `.env` → `TODOIST_API_KEY`
