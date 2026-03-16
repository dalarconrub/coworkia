# Tablas canónicas

## Tipos de acción

| Tipo  | Rasgo discriminante                              |
|------|--------------------------------------------------|
| Evento | Con hora                                       |
| Hábito | Recurrente, sin hora, sin deadline             |
| Meta   | No recurrente, sin hora, con deadline          |
| Tarea  | Sin hora, sin deadline, no recurrente, con fecha |
| Idea   | Sin fecha ni deadline                          |

## Filtros canónicos en Todoist

| Tipo  | Filtro base (simplificado)                  |
|------|----------------------------------------------|
| Evento | !no time                                   |
| Hábito | recurring & no time & no deadline          |
| Meta   | !recurring & !!no time & !no deadline<sup>1</sup>        |
| Tarea  | !recurring & no time & no deadline & !no date |
| Idea   | no date & no deadline                      |

<sup>1</sup> **Nota sobre Meta:** Se usa **doble negación `!!no time`** por un comportamiento específico del parser de filtros de Todoist. Lógicamente es equivalente a `no time`, pero **debe escribirse así** para que siempre funcione como se espera.

> Para versiones avanzadas con etiquetas (`@evento`, `@habito`, `@meta`, `@tarea`, `@idea`) y prefiltros de archivo/ búsqueda, consulta `model/04-filtros-todoist.md`.
