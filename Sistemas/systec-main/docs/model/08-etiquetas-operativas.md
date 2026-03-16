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

- `@juan` → Juan ejecuta esta acción
- `@maria` → María ejecuta esta acción
- `@equipo` → El equipo ejecuta esta acción

### Reglas

- Una acción puede tener **múltiples etiquetas de persona** si es colaborativa
- Si no hay etiqueta de persona, **tú eres el responsable**
- Las etiquetas de persona **no cambian el tipo** de acción

---

## 📍 Etiquetas de LUGAR (contexto espacial)

### Sintaxis
```

@lugar

```

### Uso
Indican **dónde se ejecuta** la acción, no el tipo.

### Ejemplos

- `@casa` → Se ejecuta en casa
- `@oficina` → Se ejecuta en la oficina
- `@universidad` → Se ejecuta en la universidad
- `@online` → Se ejecuta online

### Reglas

- Una acción puede tener **una o varias etiquetas de lugar**
- Las etiquetas de lugar **no cambian el tipo** de acción
- Útiles para **filtrar por contexto** cuando planificas

---

## ⏰ Etiquetas de TIEMPO (duración estimada)

### Sintaxis
```

@tiempo

```

### Uso
Indican **cuánto tiempo se estima** que tomará la acción.

### Ejemplos

- `@5min` → 5 minutos
- `@15min` → 15 minutos
- `@30min` → 30 minutos (1 bloque)
- `@1h` → 1 hora (2 bloques)
- `@2h` → 2 horas (4 bloques)

### Reglas

- Las etiquetas de tiempo **complementan** el timeboxing
- No reemplazan la estimación en bloques
- Útiles para **filtros rápidos** de acciones cortas

---

## 🛠️ Etiquetas de RECURSO (herramientas y materiales)

### Sintaxis
```

@recurso

```

### Uso
Indican **con qué se ejecuta** la acción.

### Ejemplos

- `@ordenador` → Requiere ordenador
- `@telefono` → Requiere teléfono
- `@libro` → Requiere libro específico
- `@internet` → Requiere conexión a internet

### Reglas

- Una acción puede tener **múltiples etiquetas de recurso**
- Las etiquetas de recurso **no cambian el tipo** de acción
- Útiles para **planificar** qué recursos necesitas tener disponibles

---

## 🔄 Combinación de etiquetas

### Ejemplo completo

```
Revisar artículo con Juan en la oficina usando el ordenador (30 min)
```

**Etiquetas:**
- `@juan` (persona)
- `@oficina` (lugar)
- `@ordenador` (recurso)
- `@30min` (tiempo)

**Tipo:** Determinado por filtros temporales (Meta, Tarea, etc.)

---

## 📊 Filtros con etiquetas operativas

### Filtro por persona
```
@juan
```

### Filtro por lugar
```
@oficina
```

### Filtro por recurso
```
@ordenador
```

### Filtro combinado
```
@juan & @oficina & @ordenador
```

---

## ⚠️ Reglas importantes

1. **Las etiquetas operativas NO definen el tipo** de acción
2. **El tipo se define por filtros temporales** (hora, recurrencia, deadline, fecha)
3. **Las etiquetas son capas adicionales** de información
4. **Puedes combinar múltiples etiquetas** en una misma acción
5. **Las etiquetas ayudan a filtrar y planificar**, no a clasificar

---

## 🎯 Casos de uso

### Caso 1: Delegación
```
Meta: Preparar informe trimestral
  └─ Acción: Revisar datos financieros @juan @oficina @ordenador
```

### Caso 2: Contexto espacial
```
Tarea: Leer artículo
  └─ Acción: Leer capítulo 3 @casa @libro @30min
```

### Caso 3: Recursos necesarios
```
Meta: Publicar artículo
  └─ Acción: Revisar referencias @ordenador @internet @1h
```

---

## 📝 Resumen

| Etiqueta | Función | Ejemplo |
|----------|---------|---------|
| **Persona** | Responsable de ejecución | `@juan` |
| **Lugar** | Contexto espacial | `@oficina` |
| **Tiempo** | Duración estimada | `@30min` |
| **Recurso** | Herramientas necesarias | `@ordenador` |

**Principio clave:** Las etiquetas operativas **enriquecen** la información de las acciones, pero **no las clasifican**. La clasificación por tipo (Idea, Meta, Tarea, Hábito, Evento) la hacen **exclusivamente los filtros temporales**.
