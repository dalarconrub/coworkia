
# MAR — Filtros temporales sin solapamientos (versión refinada)

---

## 1. Objetivo de esta revisión

Estos filtros temporales han sido **ajustados deliberadamente** para cumplir un requisito clave en MAR:

> **Un elemento no puede aparecer en más de un horizonte temporal.**

A diferencia de los filtros “naturales” de Todoist, aquí se prioriza:
- exclusividad estricta,
- lectura clara,
- y coherencia lógica entre vistas.

---

## 2. Principio de no solapamiento

Los horizontes temporales se definen como **tramos consecutivos y disjuntos**:

```

Antes de Ayer → Ayer y Hoy → Esta Semana → Este Mes → Este Año

````

Cada filtro:
- **incluye solo su tramo**
- **excluye explícitamente** los anteriores y los siguientes

---

## 3. Antes de Ayer

### Nombre MAR
**Antes de Ayer**

### Filtro Todoist
```text
overdue & !yesterday
````

### Definición

Incluye todas las acciones vencidas **anteriores a ayer**.

### Lectura MAR

> Deuda histórica acumulada.

### Uso recomendado

* Revisión semanal o mensual
* Detección de tareas obsoletas
* Limpieza del sistema

---

## 4. Ayer y Hoy

### Nombre MAR

**Ayer y Hoy**

### Filtro Todoist

```text
yesterday | today
```

### Definición

Incluye las acciones asignadas **a ayer o al día actual**.

### Incluye

* Acciones completadas tarde
* Compromisos activos inmediatos

### Lectura MAR

> Zona caliente de ejecución y ajuste.

---

## 5. Esta Semana

### Nombre MAR

**Esta Semana**

### Filtro Todoist

```text
due after last week & due before: next week
```

### Definición

Incluye las acciones planificadas para la **semana natural en curso**
(excluyendo ayer y hoy).

### Lectura MAR

> Horizonte semanal limpio, sin pasado inmediato.

---

## 6. Este Mes

### Nombre MAR

**Este Mes**

### Filtro Todoist

```text
due after: next week & due before: end of month
```

### Definición

Incluye las acciones previstas para **el resto del mes actual**,
excluyendo la semana en curso.

### Lectura MAR

> Planificación mensual sin presión semanal.

---

## 7. Este Año

### Nombre MAR

**Este Año**

### Filtro Todoist

```text
due after: end of month & due before: next year
```

### Definición

Incluye las acciones previstas para **el resto del año natural**,
excluyendo el mes actual.

### Lectura MAR

> Horizonte estratégico anual.

---

## 8. Tabla resumen (sin solapamientos)

| Horizonte MAR | Filtro Todoist                                    |        |
| ---------------- | ------------------------------------------------- | ------ |
| Antes de Ayer    | `overdue & !yesterday`                            |        |
| Ayer y Hoy       | `yesterday                                        | today` |
| Esta Semana      | `due after last week & due before: next week`     |        |
| Este Mes         | `due after: next week & due before: end of month` |        |
| Este Año         | `due after: end of month & due before: next year` |        |

---

## 9. Regla de uso en MAR

El flujo correcto es siempre:

1. **Clasificar por tipo** (Idea, Meta, Tarea, Hábito, Evento)
2. **Visualizar por horizonte temporal exclusivo**

Ejemplos:

* *Tareas · Ayer y Hoy*
* *Eventos · Esta Semana*
* *Metas · Este Año*

---

## 10. Regla final

> **En MAR, los horizontes temporales no se pisan.
> Cada acción vive en un único tramo del tiempo.**

Si aparece en dos, el filtro está mal definido.

