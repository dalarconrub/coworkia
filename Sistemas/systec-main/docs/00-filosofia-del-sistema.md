# Filosofía del sistema

Este sistema parte de una premisa simple:

> **No organizamos tareas por lo que son, sino por cómo existen en el tiempo.**

Todoist no modela intención ni significado; modela:
- hora
- recurrencia
- fecha de inicio
- fecha límite (deadline)

El sistema acepta estas limitaciones y las convierte en una ventaja:
usamos cada propiedad **solo como rasgo discriminante**, no como descripción total.

## Principios

1. Una acción pertenece a un solo tipo.
2. La hora implica rigidez.
3. El deadline implica presión externa.
4. La recurrencia implica rutina.
5. Lo no decidido aún es una idea, no una tarea.

El sistema es estable porque **no depende del día actual** ni de etiquetas manuales.

---

## Filtros temporales

MAR utiliza dos tipos de filtros temporales que complementan la clasificación por tipo:

### Horizontes temporales (mutuamente excluyentes)

Los horizontes temporales clasifican acciones según **cuándo deben atenderse**, de forma **mutuamente excluyente**. Una acción solo puede pertenecer a un horizonte a la vez:

- **+->Hoy**: Deuda temporal y compromiso inmediato
  - Filtro: `(!#Z-* & !search:*) & (overdue | due before: +1 day)`
- **-+>1 Día**: Compromiso de mañana
  - Filtro: `(!#Z-* & !search:*) & due after: yesterday & due before: +2day`
- **+->1 Semana**: Corto plazo
  - Filtro: `(!#Z-* & !search:*) & due after: today & due before: +7day`
- **+->1 Mes**: Medio plazo
  - Filtro: `(!#Z-* & !search:*) & (due after: +7 days & due before: +30 days)`
- **+->1 Año**: Largo plazo
  - Filtro: `(!#Z-* & !search:*) & (due after: +30 days & due before: +365 days)`

**Principio:** Los horizontes ayudan a **decidir prioridad** basándose en la urgencia temporal real.

### Bandejas de entrada (vistas acumulativas)

Las bandejas de entrada son **vistas operativas** que muestran todo lo que vence en un periodo, **sin exclusión mutua**. Son útiles para revisión y planificación:

- **Para Ayer**: `(!#Z-* & !search:*) & overdue`
- **Para Hoy**: `(!#Z-* & !search:*) & today`
- **Esta Semana**: `(!#Z-* & !search:*) & due before: next week`
- **Este Mes**: `(!#Z-* & !search:*) & due before: end of month`
- **Este Año**: `(!#Z-* & !search:*) & due after: end of month & due before: new year's eve`

**Principio:** Las bandejas ayudan a **revisar contexto completo** de un periodo, independientemente de la clasificación por tipo o horizonte.

### Relación con los principios

Los filtros temporales refuerzan los principios fundamentales:

1. **No dependen del día actual**: Los horizontes usan rangos relativos estables (`+1 day`, `+7 days`, etc.)
2. **No dependen de etiquetas manuales**: Se basan únicamente en propiedades temporales de Todoist
3. **Complementan la clasificación por tipo**: Los filtros de tipo dicen **qué es** una acción; los filtros temporales dicen **cuándo vive**

> **En MAR, los filtros de tipo dicen qué es una acción.  
> Los filtros temporales dicen cuándo vive.  
> Nunca se mezclan, pero se usan en conjunto para una visión completa.**
