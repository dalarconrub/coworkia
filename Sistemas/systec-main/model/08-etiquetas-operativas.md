
# MAR — Canvas de Etiquetas Operativas (Personas, Lugares, Tiempo y Recursos)

---

## 🧭 Principio rector

> **En MAR, las etiquetas NO definen el tipo de acción.**  
> Definen **con quién**, **dónde**, **con qué** y **cuánto** se ejecuta.

La **ontología** (Idea · Meta · Tarea · Hábito · Evento)  
la deciden **los filtros temporales**, no las etiquetas.

Las etiquetas son **capas operativas transversales**.

---

## 🧩 Capas del sistema MAR

```

┌────────────────────────────────────┐
│ Capa 1 · Tipo (filtros temporales)  │
│ Idea / Meta / Tarea / Hábito / Evento│
└────────────────────────────────────┘
┌────────────────────────────────────┐
│ Capa 2 · Ritmo (@d @s @m @a @d2…)   │
└────────────────────────────────────┘
┌────────────────────────────────────┐
│ Capa 3 · Ejecución (etiquetas)      │
│ Persona · Lugar · Tiempo · Recurso  │
└────────────────────────────────────┘

```

---

## 👥 Etiquetas de PERSONA (delegación)

### Sintaxis
```

@nombrepersona

```

### Uso
Indican **responsable real de la ejecución**, no contexto.

### Ejemplos
```

Enviar documentación @sofia
Revisar informe @juan
Confirmar viaje @upo

````

### Lectura correcta
> “Esto no lo ejecuto yo (o no solo yo).”

### Filtro útil
```text
search:@sofia
````

---

## 📍 Etiquetas de LUGAR

### Sintaxis

```
@sitio
```

### Uso

Indican **dónde puede o debe ejecutarse** la acción.

### Ejemplos

```
Imprimir actas @upo
Revisar material @casa
Comprar cañas @tienda
```

### Lectura correcta

> “Esto solo tiene sentido en este contexto espacial.”

### Filtro útil

```text
search:@upo
```

---

## ⏱️ Etiquetas de TIEMPO EJECUTADO

> Estas etiquetas **NO estiman**,
> **registran tiempo real invertido**.

### Sintaxis

```
@t30m
@t45m
@t1h
@t1.45h
```

### Ejemplos

```
Revisión bibliografía @t45m
Ensayo clarinete @t1.45h
```

### Uso correcto

* Se añaden **después de ejecutar**
* Son acumulables a lo largo del tiempo
* Sirven para **auditoría y calibración realista**

### Lectura correcta

> “Esto ya ha consumido este tiempo.”

### Filtro útil

```text
search:@t
```

---

## 🧰 Etiquetas de RECURSOS

### Sintaxis

```
@recurso
```

### Recursos estándar MAR

| Etiqueta     | Recurso              |
| ------------ | -------------------- |
| `@e`         | Dinero               |
| `@pc`        | Ordenador            |
| `@coche`     | Vehículo             |
| `@clarinete` | Instrumento          |
| `@movil`     | Teléfono             |
| `@papel`     | Documentación física |

### Ejemplos

```
Comprar boquillas @e
Preparar presentación @pc
Ir a ensayo @coche
Estudiar pasaje @clarinete
```

### Lectura correcta

> “Sin este recurso, la tarea no puede ejecutarse.”

### Filtro útil

```text
search:@pc
```

---

## 🔁 Convivencia con marcadores de recurrencia

Las etiquetas **conviven** con los marcadores `@d @s @m @a @d2…`:

```
Ensayar clarinete @d @clarinete @t45m
Revisión cuentas @m3 @pc
Enviar informe @juan @pc
```

Cada capa responde a una pregunta distinta:

| Pregunta            | Respuesta       |
| ------------------- | --------------- |
| ¿Qué es?            | Filtros MAR  |
| ¿Cada cuánto?       | @d @s @m @a @d2 |
| ¿Con quién?         | @persona        |
| ¿Dónde?             | @lugar          |
| ¿Con qué?           | @recurso        |
| ¿Cuánto ha costado? | @t              |

---

## 🚫 Qué NO se debe hacer

* ❌ Usar etiquetas para decidir el tipo
* ❌ Usar etiquetas como prioridad
* ❌ Duplicar información temporal en etiquetas
* ❌ Crear etiquetas semánticas vagas (`@importante`, `@urgente`)

---

## 🧱 Regla de coherencia MAR

> **Si al quitar todas las etiquetas
> el tipo deja de estar claro,
> el sistema está mal modelado.**

Las etiquetas **enriquecen**,
los filtros **sostienen**.

---

## 🏁 Regla final del canvas

> **En MAR:**
>
> * Los filtros definen la estructura
> * Los marcadores definen el ritmo
> * Las etiquetas definen la ejecución real
>
> Mezclar estos planos rompe el sistema.

