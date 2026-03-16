# Filtros en Todoist

## Idea
no date & no deadline

## Meta

> **Nota:** Se usa **doble negación `!!no time`** por un comportamiento específico del parser de filtros de Todoist. Lógicamente es equivalente a `no time`, pero **debe escribirse así** para que siempre funcione como se espera.

!recurring & !!no time & !no deadline

## Hábito
recurring & no time & no deadline

## Tarea
no time & !no deadline

## Evento
!no time


## Filtro de contenidos guardados o categorias no revisables
(!#Z-* & !search:*) 

Por ejemplo en Tarea:
(!#Z-* & !search:*) & (no time & !no deadline)



# MAR - Filtros temporales de horizonte

---

## 1. Objetivo de los filtros temporales

MAR define **filtros temporales de horizonte** para responder a una única pregunta operativa:

> **¿Cuándo debe atenderse esta acción?**

Estos filtros **no clasifican el tipo** de acción  
(eso lo hacen los filtros MAR: Idea, Meta, Tarea, Hábito, Evento).

Son **vistas de tiempo**, no de ontología.

---

## 2. Horizontes temporales definidos

MAR utiliza cinco horizontes temporales, **mutuamente excluyentes**:

- **+->Hoy** → deuda temporal y compromiso inmediato  
- **-+>1 Día** → compromiso de mañana  
- **+->1 Semana** → corto plazo  
- **+->1 Mes** → medio plazo  
- **+->1 Año** → largo plazo  

---

## 3. Principio de exclusividad

Una acción **solo puede pertenecer a un horizonte a la vez**.

Jerarquía temporal:

```

+->Hoy → -+>1 Día → +->1 Semana → +->1 Mes → +->1 Año

````

Cada filtro **excluye implícitamente** a los anteriores.

---

## 4. Filtro +->Hoy

### Definición
Acciones que **debían haberse realizado antes de hoy** o que deben ejecutarse **hoy o antes de mañana**.

### Filtro Todoist

```text
(!#Z-* & !search:*) & (overdue | due before: +1 day)
```

### Lectura MAR

> Deuda temporal y compromiso inmediato. No se planifica, se liquida.

---

## 5. Filtro -+>1 Día

### Definición

Acciones previstas para **mañana** (desde ayer hasta pasado mañana).

### Filtro Todoist

```text
(!#Z-* & !search:*) & due after: yesterday & due before: +2day
```

### Lectura MAR

> Compromiso de corto plazo, aún flexible pero próximo.

---

## 6. Filtro +->1 Semana

### Definición

Acciones previstas para los **próximos 7 días**, excluyendo hoy y mañana.

### Filtro Todoist

```text
(!#Z-* & !search:*) & due after: today & due before: +7day
```

### Lectura MAR

> Compromisos cercanos, aún flexibles.

---

## 7. Filtro +->1 Mes

### Definición

Acciones previstas para el **resto del mes**, excluyendo esta semana.

### Filtro Todoist

```text
(!#Z-* & !search:*) & (due after: +7 days & due before: +30 days)
```

### Lectura MAR

> Trabajo planificable sin presión inmediata.

---

## 8. Filtro +->1 Año

### Definición

Acciones de **horizonte largo**, sin urgencia operativa.

### Filtro Todoist

```text
(!#Z-* & !search:*) & (due after: +30 days & due before: +365 days)
```

### Lectura MAR

> Intención estratégica, no acción inmediata.

---

## 9. Tabla resumen

| Horizonte     | Filtro Todoist                                                                    | Significado                    |
| ------------- | ---------------------------------------------------------------------------------- | ------------------------------ |
| +->Hoy        | `(!#Z-* & !search:*) & (overdue \| due before: +1 day)`                            | Deuda y compromiso inmediato   |
| -+>1 Día      | `(!#Z-* & !search:*) & due after: yesterday & due before: +2day`                    | Compromiso de mañana           |
| +->1 Semana   | `(!#Z-* & !search:*) & due after: today & due before: +7day`                       | Corto plazo                    |
| +->1 Mes      | `(!#Z-* & !search:*) & (due after: +7 days & due before: +30 days)`                | Medio plazo                    |
| +->1 Año      | `(!#Z-* & !search:*) & (due after: +30 days & due before: +365 days)`              | Largo plazo                    |

---

## 10. Relación con MAR

El uso correcto es siempre:

1. **Clasificar por tipo** (MAR)
2. **Visualizar por horizonte** (+->Hoy / -+>1 Día / +->1 Semana / +->1 Mes / +->1 Año)

Ejemplos:

* *Tareas +->Hoy*
* *Eventos +->1 Semana*
* *Hábitos +->1 Mes*

---

## 11. Regla final

> **En MAR, los filtros de tipo dicen qué es una acción.
> Los filtros temporales dicen cuándo vive.**

Nunca se mezclan.

---

# MAR - Bandejas de entrada (vistas operativas)

Los filtros de bandejas de entrada son **vistas simples** que muestran todo lo que vence en un periodo determinado, sin clasificar por tipo. Son útiles para revisión rápida y gestión operativa diaria.

---

## 1. Para Ayer

Muestra todas las acciones vencidas (deuda temporal).

### Filtro Todoist

```text
(!#Z-* & !search:*) & overdue
```

### Uso

Revisión de deuda acumulada. No se planifica, se liquida.

---

## 2. Para Hoy

Muestra todas las acciones que vencen hoy.

### Filtro Todoist

```text
(!#Z-* & !search:*) & today
```

### Uso

Vista operativa del día actual. Incluye eventos, tareas, metas y hábitos programados para hoy.

---

## 3. Esta Semana

Muestra todas las acciones que vencen antes del próximo lunes (o inicio de la próxima semana).

### Filtro Todoist

```text
(!#Z-* & !search:*) & due before: next week
```

### Uso

Vista semanal completa. Útil para planificación y revisión semanal.

---

## 4. Este Mes

Muestra todas las acciones que vencen antes del final del mes actual.

### Filtro Todoist

```text
(!#Z-* & !search:*) & due before: end of month
```

### Uso

Vista mensual completa. Útil para planificación y revisión mensual.

---

## 5. Este Año

Muestra todas las acciones que vencen después del final del mes actual y antes del próximo año.

### Filtro Todoist

```text
(!#Z-* & !search:*) & due after: end of month & due before: new year's eve
```

### Uso

Vista de horizonte largo. Útil para planificación estratégica y revisión anual.

---

## 6. Tabla resumen de bandejas

| Bandeja      | Filtro Todoist                                                              | Uso                    |
| ------------ | --------------------------------------------------------------------------- | ---------------------- |
| Para Ayer    | `(!#Z-* & !search:*) & overdue`                                            | Deuda temporal         |
| Para Hoy     | `(!#Z-* & !search:*) & today`                                              | Vista del día          |
| Esta Semana  | `(!#Z-* & !search:*) & due before: next week`                              | Vista semanal          |
| Este Mes     | `(!#Z-* & !search:*) & due before: end of month`                           | Vista mensual          |
| Este Año     | `(!#Z-* & !search:*) & due after: end of month & due before: new year's eve`   | Vista anual            |

---

## 7. Diferencia con horizontes temporales

Los **horizontes temporales** (+->Hoy, -+>1 Día, etc.) son **mutuamente excluyentes** y se usan para clasificación.

Las **bandejas de entrada** son **vistas acumulativas** que muestran todo lo que vence en un periodo, sin exclusión mutua.

**Ejemplo:**
- Una acción puede estar en **+->Hoy** (horizonte) Y en **Esta Semana** (bandeja) simultáneamente
- Los horizontes ayudan a decidir prioridad
- Las bandejas ayudan a revisar contexto completo


