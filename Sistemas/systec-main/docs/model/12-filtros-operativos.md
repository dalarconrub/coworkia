````markdown
# MAR — Filtros canónicos de tipo (versión operativa completa)

Este documento explica **los filtros finales de clasificación por tipo en MAR**, tal y como han quedado **implementados y probados en Todoist**.  
Incluye la lógica de **precedencia por etiqueta**, las **exclusiones necesarias** y los **filtros de higiene del sistema**.

---

## 1. Principios generales del diseño

Todos los filtros de tipo en MAR comparten **tres principios estructurales**:

### 1.1 Exclusión de contenedores no operativos
```text
!#Z-*
````

Excluye proyectos de archivo, referencia o no ejecutables.

### 1.2 Exclusión de búsquedas globales

```text
!search:*
```

Evita duplicados y tareas “arrastradas” por búsquedas generales.

### 1.3 Precedencia explícita de etiquetas de tipo

* Si existe una etiqueta de tipo (`@idea`, `@tarea`, etc.), **esta manda siempre**
* Si no existe, se aplica la **inferencia temporal**
* En todos los casos se excluyen las demás etiquetas de tipo para evitar ambigüedad

---

## 2. Filtro IDEA

### Filtro completo

```text
(!#Z-* & !search:*) &
(
  ((no date & no deadline) & (@idea & !@tarea & !@meta & !@habito & !@evento))
  | (@idea & !@tarea & !@meta & !@habito & !@evento)
)
```

### Lógica

Una acción es **IDEA** si:

* está explícitamente marcada como `@idea`, **o**
* no tiene fecha ni deadline y además está marcada como `@idea`

> En MAR, **una idea siempre requiere decisión explícita**
> para evitar que el backlog crezca de forma pasiva.

---

## 3. Filtro TAREA

### Filtro completo

```text
(!#Z-* & !search:*) &
(
  ((no time & !no deadline) & (!@idea & !@meta & !@habito & !@evento))
  | (!@idea & @tarea & !@meta & !@habito & !@evento)
)
```

### Lógica

Una acción es **TAREA** si:

* tiene deadline pero no hora (presión externa flexible), **o**
* está explícitamente marcada como `@tarea`

Siempre que **no esté marcada como otro tipo**.

---

## 4. Filtro META

### Filtro completo

```text
(!#Z-* & !search:*) &
(
  (!@idea & !@tarea & @meta & !@habito & !@evento)
  | (( !recurring & no time & no deadline) & (!@idea & !@tarea & !@habito & !@evento))
)
```

### Lógica

Una acción es **META** si:

* está explícitamente marcada como `@meta`, **o**
* no es recurrente, no tiene hora ni deadline (la fecha es el compromiso)

---

## 5. Filtro HÁBITO

### Filtro completo

```text
(!#Z-* & !search:*) &
(
  (!@idea & !@tarea & !@meta & @habito & !@evento)
  | (recurring & no time & no deadline & (!@idea & !@tarea & !@meta & !@evento))
)
```

### Lógica

Una acción es **HÁBITO** si:

* está explícitamente marcada como `@habito`, **o**
* es recurrente, sin hora ni deadline

> Los hábitos **no tienen presión externa**
> y no se gestionan como deuda.

---

## 6. Filtro EVENTO

### Filtro completo

```text
(!#Z-* & !search:*) &
(
  (!no time & (!@idea & !@tarea & !@meta & !@habito))
  | (!@idea & !@tarea & !@meta & !@habito & @evento)
)
```

### Lógica

Una acción es **EVENTO** si:

* tiene hora fija (rigidez temporal), **o**
* está explícitamente marcada como `@evento`

Siempre excluyendo otros tipos.

---

## 7. Resumen lógico de precedencia

El orden real de evaluación es:

1. **¿Está en un proyecto excluido?** → fuera del sistema
2. **¿Tiene etiqueta de tipo?** → se clasifica por ella
3. **Si no**, se aplica inferencia temporal:

   * hora → EVENTO
   * deadline → TAREA
   * recurrencia → HÁBITO
   * resto → META
4. **IDEA** solo existe por decisión explícita

---

## 8. Qué garantizan estos filtros

* No hay solapamientos entre tipos
* No hay ambigüedad semántica
* El sistema es estable en el tiempo
* La excepción humana siempre gana
* El backlog está controlado

---

## 9. Regla final MAR

> **Si una acción está mal clasificada,
> no se arregla con fechas:
> se arregla con una decisión explícita.**

Estos filtros convierten esa decisión en estructura.

```markdown
# MAR — Documento maestro (TODO)

Este documento integra **todo el sistema MAR** en una única referencia operativa:
- Filosofía
- Ontología (tipos)
- Precedencia por etiquetas
- Filtros canónicos (implementados y probados)
- Horizontes temporales sin solapamientos
- Etiquetas operativas
- Reglas de uso
- Tablas resumen y canvas

---

## 1. Filosofía MAR

> **MAR clasifica acciones por su relación con el tiempo,  
> no por su significado.**

Todoist modela tiempo (hora, fecha, recurrencia, deadline).  
MAR acepta ese modelo y lo convierte en estructura estable.

Principios:
1. Una acción pertenece a un solo tipo
2. La hora implica rigidez
3. El deadline implica presión externa
4. La recurrencia implica rutina
5. La decisión explícita tiene precedencia

---

## 2. Capas del sistema

```

┌────────────────────────────────────┐
│ Capa 1 · Ontología (TIPO)           │
│ Idea · Meta · Tarea · Hábito · Evento│
└────────────────────────────────────┘
┌────────────────────────────────────┐
│ Capa 2 · Horizonte temporal         │
│ Antes de Ayer · Ayer/Hoy · Semana…  │
└────────────────────────────────────┘
┌────────────────────────────────────┐
│ Capa 3 · Ritmo (@d @s @m @a @d2…)   │
└────────────────────────────────────┘
┌────────────────────────────────────┐
│ Capa 4 · Ejecución (etiquetas)      │
│ Persona · Lugar · Recurso · Tiempo  │
└────────────────────────────────────┘

````

---

## 3. Etiquetas de tipo (precedencia)

Etiquetas:
- `@idea`
- `@meta`
- `@tarea`
- `@habito`
- `@evento`

**Regla**  
Si existe una etiqueta de tipo, **manda siempre**.  
Si no existe, se aplica inferencia temporal.

Nunca puede haber más de una etiqueta de tipo.

---

## 4. Filtros canónicos de TIPO (operativos)

### Exclusiones comunes
```text
!#Z-* & !search:*
````

---

### IDEA

```text
(!#Z-* & !search:*) &
(
  (no date & no deadline & !@tarea & !@meta & !@habito & !@evento)
  | (@idea & !@tarea & !@meta & !@habito & !@evento)
)
```

---

### TAREA

```text
(!#Z-* & !search:*) &
(
  (no time & !no deadline & !@idea & !@meta & !@habito & !@evento)
  | (!@idea & @tarea & !@meta & !@habito & !@evento)
)
```

---

### META

```text
(!#Z-* & !search:*) &
(
  (!@idea & !@tarea & @meta & !@habito & !@evento)
  | (!recurring & no time & no deadline & !@idea & !@tarea & !@habito & !@evento)
)
```

---

### HÁBITO

```text
(!#Z-* & !search:*) &
(
  (!@idea & !@tarea & !@meta & @habito & !@evento)
  | (recurring & no time & no deadline & !@idea & !@tarea & !@meta & !@evento)
)
```

---

### EVENTO

```text
(!#Z-* & !search:*) &
(
  (!no time & !@idea & !@tarea & !@meta & !@habito)
  | (!@idea & !@tarea & !@meta & !@habito & @evento)
)
```

---

## 5. Inferencia temporal (cuando no hay etiqueta)

| Rasgo                       | Resultado |
| --------------------------- | --------- |
| Tiene hora                  | EVENTO    |
| No hora + deadline          | TAREA     |
| Recurrente                  | HÁBITO    |
| No recurrente, sin deadline | META      |
| Sin fecha ni deadline       | IDEA      |

---

## 6. Horizontes temporales (sin solapamientos)

| Horizonte         | Filtro                                            |        |
| ----------------- | ------------------------------------------------- | ------ |
| **Antes de Ayer** | `overdue & !yesterday`                            |        |
| **Ayer y Hoy**    | `yesterday                                        | today` |
| **Esta Semana**   | `due after last week & due before: next week`     |        |
| **Este Mes**      | `due after: next week & due before: end of month` |        |
| **Este Año**      | `due after: end of month & due before: next year` |        |

**Regla**
Una acción solo puede vivir en **un horizonte**.

---

## 7. Ritmo de ejecución (marcadores)

Sintaxis:

```
@d  @s  @m  @a
@d2 @s3 @m6 @a2
```

Ejemplos:

```
Ensayar clarinete @d
Ejercicio fuerza @d2
Revisión cuentas @m3
```

No definen tipo. Solo ritmo humano.

---

## 8. Etiquetas operativas (ejecución)

### Persona

```
@sofia @juan @upo
```

### Lugar

```
@casa @upo @oficina
```

### Recursos

```
@pc @e @coche @clarinete
```

### Tiempo ejecutado

```
@t30m @t1h @t1.45h
```

---

## 9. Reglas de oro

1. El tipo **no se decide con etiquetas operativas**
2. El deadline solo expresa presión externa
3. Los hábitos no generan deuda
4. Las ideas no se ejecutan
5. Si al quitar etiquetas el tipo no está claro, el modelado es incorrecto

---

## 10. Uso recomendado (flujo)

1. Captura → IDEA
2. Decide tipo (o etiqueta si hay excepción)
3. Asigna horizonte temporal
4. Ejecuta
5. Revisa semanalmente:

   * Antes de Ayer
   * Esta Semana
   * Este Mes

---

## 11. Canvas de decisión (resumen)

```
¿Etiqueta de tipo?
 ├─ Sí → ese tipo
 └─ No
     ¿Tiene hora?
     ├─ Sí → EVENTO
     └─ No
         ¿Tiene deadline?
         ├─ Sí → TAREA
         └─ No
             ¿Es recurrente?
             ├─ Sí → HÁBITO
             └─ No → META
(Sin fecha ni deadline → IDEA)
```

---

## 12. Regla final MAR

> **La estructura decide por defecto.
> La decisión humana corrige cuando hace falta.**

Ese equilibrio es MAR.

