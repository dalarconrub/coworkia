
# MAR — Recurrencias y filtros temporales

---

## 1. Por qué MAR explicita las recurrencias

MAR clasifica acciones según su **estructura temporal real** en Todoist  
(hora, recurrencia y deadline), no según etiquetas manuales.

Sin embargo, **no toda recurrencia es equivalente**:

- diario ≠ semanal ≠ mensual ≠ anual  
- cada 2 días ≠ cada 7 días  
- no tienen el mismo coste cognitivo  
- no se revisan con la misma frecuencia  

Por ello, MAR introduce **marcadores de recurrencia explícitos y paramétricos**.

---

## 2. Marcadores de recurrencia en MAR

MAR utiliza los siguientes marcadores base:

- `@d` → diario  
- `@s` → semanal  
- `@m` → mensual  
- `@a` → anual  

Estos marcadores pueden **parametrizarse con un número**:

- `@d2` → cada 2 días  
- `@d3` → cada 3 días  
- `@s2` → cada 2 semanas  
- `@m3` → cada 3 meses  
- `@a2` → cada 2 años  

### Regla general

```

@[unidad][n]

```

donde:
- `unidad` ∈ { d, s, m, a }
- `n` = número entero ≥ 2  
- ausencia de número ⇒ frecuencia 1 (por defecto)

---

## 3. Qué significan estos marcadores

Los marcadores de recurrencia en MAR:

- ❌ **NO son etiquetas de tipo**
- ❌ **NO definen si algo es tarea, hábito o meta**
- ❌ **NO participan en el árbol de decisión**
- ❌ **NO sustituyen a `recurring`**
- ✅ **Describen el ritmo esperado de ejecución**
- ✅ **Hacen explícita la granularidad temporal**

Son **anotaciones operativas**, no estructurales.

---

## 4. Qué NO hacen estos marcadores

Es importante dejarlo claro:

- No crean categorías nuevas
- No corrigen una mala clasificación
- No fuerzan prioridades
- No introducen presión temporal (eso es el deadline)

> En MAR, **la ontología la definen los filtros**,  
> los marcadores solo describen el *ritmo humano*.

---

## 5. Para qué SÍ se usan

### 5.1 Lectura cognitiva inmediata

Ejemplos:

```

Ensayar clarinete @d
Meditación @d2
Revisión bibliografía @s
Backup archivos @m
Limpieza profunda estudio @m3
Declaración IRPF @a

````

Antes de abrir la tarea sabes:
- la frecuencia esperada
- la regularidad real
- el peso cognitivo acumulado
- su lugar natural en tu semana, mes o año

---

### 5.2 Vistas de carga temporal

Permiten crear vistas útiles sin romper el sistema:

```text
search:@d
````

Rutinas diarias (incluye @d, @d2, @d3…)

```text
search:@s
```

Mantenimiento semanal (incluye @s2, @s3…)

```text
search:@m | search:@a
```

Trabajo de baja frecuencia y alto impacto

---

### 5.3 Revisión periódica guiada

En revisiones:

* `@d`, `@d2` → ¿es sostenible a este ritmo?
* `@s`, `@s2` → ¿sigue siendo necesario este mantenimiento?
* `@m`, `@m3` → ¿aporta valor real o es inercia?
* `@a` → ¿sigue teniendo sentido este compromiso anual?

Los marcadores **orientan la revisión**, no la ejecución diaria.

---

## 6. Relación con los tipos MAR

Los marcadores **cruzan** los tipos, no los sustituyen.

| Tipo MAR | ¿Puede llevar @d/@s/@m/@a?                   |
| ----------- | -------------------------------------------- |
| Idea        | ❌ No                                         |
| Meta        | ⚠️ Raro                                      |
| Hábito      | ✅ Sí (uso principal)                         |
| Tarea       | ⚠️ A veces (tareas recurrentes con deadline) |
| Evento      | ❌ No (la hora ya manda)                      |

---

## 7. Ejemplos correctos

### Hábito diario

```
Ensayar clarinete @d
recurring
no deadline
```

### Hábito cada 2 días

```
Ejercicio fuerza @d2
recurring
no deadline
```

### Tarea recurrente semanal con deadline

```
Preparar clase próxima semana @s
recurring
deadline: domingo
```

### Tarea mensual cada 3 meses

```
Revisión cuentas proyecto @m3
recurring
deadline: fin de trimestre
```

### Meta puntual (sin marcador)

```
Enviar propuesta proyecto
!recurring
no deadline
```

---

## 8. Relación con los filtros canónicos MAR

Los filtros estructurales **no cambian**:

```text
Idea    → no date & no deadline
Meta    → !recurring & no time & no deadline
Hábito  → recurring & no time & no deadline
Tarea   → no time & !no deadline
Evento  → !no time
```

Los marcadores se usan **solo como capa adicional de lectura y revisión**:

```text
recurring & search:@d
```

```text
search:@m | search:@a
```

---

## 9. Regla de uso (crítica)

> **Nunca uses @d @s @m @a (ni @d2, @m3, etc.) para decidir el tipo.**
> Primero clasifica con MAR.
> Después, si aporta valor cognitivo, añade el marcador.

---

## 10. Por qué este diseño es coherente

* No rompe la ontología
* No añade campos ficticios
* No depende del día actual
* No fuerza a Todoist a inferir intención
* Escala desde lo diario hasta lo plurianual

MAR separa deliberadamente:

* **estructura temporal** (filtros)
* **ritmo humano de ejecución** (marcadores paramétricos)

---

## 11. Regla final

> **En MAR, la recurrencia define la existencia en el tiempo.
> Los marcadores (`@d`, `@d2`, `@m3`…) definen el ritmo humano.**

Son capas distintas.

