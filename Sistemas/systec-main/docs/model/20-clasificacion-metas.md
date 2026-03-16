# Clasificación de Metas Importantes

## Sistema de Importancia y Urgencia en MAR

---

## 1. Principio fundamental

En el sistema MAR, las metas se clasifican mediante **dos dimensiones independientes**:

1. **Importancia** → Definida por la **modalidad** (must > should > would)
2. **Urgencia** → Definida por el **marco temporal** (micro-macro)

> **Importante:** La importancia y la urgencia son **conceptos distintos** y se evalúan de forma independiente.

---

## 2. Importancia: Definida por Modalidad

La **importancia** de una meta se determina exclusivamente por su **modalidad**, siguiendo un orden jerárquico fijo e inalterable.

### 2.1 Tipología de metas por modalidad

Toda meta pertenece **obligatoriamente** a una de estas tres categorías:

| Modalidad       | Etiqueta | Definición                                                                                                                                    | Importancia |
| --------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| **Debes**       | must     | Obligaciones ineludibles. No realizarlas tiene consecuencias negativas claras (académicas, profesionales, legales o personales).              | 🟥 Máxima   |
| **Deberías**    | should   | Compromisos importantes para el progreso, la calidad o la coherencia del sistema, aunque su incumplimiento no tenga consecuencias inmediatas. | 🟧 Media    |
| **Te gustaría** | would    | Aspiraciones deseables, mejoras o proyectos de valor añadido, sin obligación directa.                                                         | 🟨 Baja     |

> **Todo lo que no entra en alguna de estas tres categorías no es una meta MAR.**

---

### 2.2 Orden jerárquico de importancia (inalterable)

El orden de importancia es **fijo** y se basa únicamente en la modalidad:

```
🟥 must (Debes)     → Importancia MÁXIMA
    ↓
🟧 should (Deberías) → Importancia MEDIA
    ↓
🟨 would (Te gustaría) → Importancia BAJA
```

**Reglas innegociables:**

* Una meta *would* **nunca** puede tener más importancia que una meta *must*
* Una meta *should* **nunca** puede tener más importancia que una meta *must*
* El orden de importancia es **independiente** del contenido concreto de la meta

---

### 2.3 Implicaciones de la importancia

La importancia determina:

* **Prioridad en el dashboard** → Las metas *must* siempre aparecen primero
* **Orden de activación** → Solo se activan metas *should* cuando las *must* están controladas
* **Orden de ejecución** → Las acciones de metas *must* tienen prioridad absoluta
* **Evaluación de fallos** → Fallar una meta *must* es un fallo del sistema; posponer una *would* no lo es

---

## 3. Urgencia: Definida por Marco Temporal

La **urgencia** de una meta se determina por su **marco temporal** en el sistema de timeboxing bidimensional (micro-macro).

### 3.1 Marcos temporales en MAR

El sistema MAR utiliza dos niveles de timeboxing:

| Marco      | Escala        | Función                    |
| ---------- | ------------- | -------------------------- |
| **Micro**  | Diaria        | Ejecución en bloques       |
| **Macro**  | Semanal/Mensual/Anual | Planificación y revisión |

---

### 3.2 Urgencia según marco temporal

La urgencia se evalúa según el **horizonte temporal** en el que debe atenderse la meta:

#### Urgencia en marco micro (diario)

| Horizonte     | Urgencia | Significado                    |
| ------------- | -------- | ------------------------------ |
| +->Hoy        | 🔴 Alta  | Debe ejecutarse hoy            |
| -+>1 Día      | 🟠 Media | Debe ejecutarse mañana         |
| +->1 Semana   | 🟡 Baja  | Debe ejecutarse esta semana    |

#### Urgencia en marco macro (estratégico)

| Horizonte     | Urgencia | Significado                    |
| ------------- | -------- | ------------------------------ |
| Este Mes      | 🔴 Alta  | Meta con deadline este mes     |
| Este Año      | 🟠 Media | Meta con deadline este año     |
| Largo plazo   | 🟡 Baja  | Meta sin deadline inmediato    |

---

### 3.3 Combinación de urgencia micro-macro

Una meta puede tener:

* **Urgencia micro alta** (debe ejecutarse hoy) pero **urgencia macro baja** (deadline lejano)
* **Urgencia micro baja** (no es para hoy) pero **urgencia macro alta** (deadline próximo)

**Ejemplo:**

* Meta *must* con deadline en 3 meses → Importancia máxima, urgencia macro media
* Meta *should* con deadline mañana → Importancia media, urgencia micro alta

---

## 4. Matriz de Clasificación Completa

### 4.1 Importancia × Urgencia

| Importancia | Urgencia Micro | Urgencia Macro | Prioridad Final |
| ----------- | -------------- | -------------- | --------------- |
| 🟥 must     | 🔴 Alta        | 🔴 Alta        | **CRÍTICA**     |
| 🟥 must     | 🔴 Alta        | 🟠 Media       | **CRÍTICA**     |
| 🟥 must     | 🟠 Media       | 🔴 Alta        | **ALTA**        |
| 🟥 must     | 🟠 Media       | 🟠 Media       | **ALTA**        |
| 🟧 should   | 🔴 Alta        | 🔴 Alta        | **ALTA**        |
| 🟧 should   | 🔴 Alta        | 🟠 Media       | **MEDIA**       |
| 🟧 should   | 🟠 Media       | 🔴 Alta        | **MEDIA**       |
| 🟨 would    | 🔴 Alta        | 🔴 Alta        | **MEDIA**       |
| 🟨 would    | 🟠 Media       | 🟠 Media       | **BAJA**        |

**Regla de oro:**

> **La importancia (modalidad) siempre tiene precedencia sobre la urgencia.**  
> Una meta *must* con urgencia baja **siempre** tiene prioridad sobre una meta *would* con urgencia alta.

---

## 5. Aplicación Práctica

### 5.1 En el Dashboard

Las metas se ordenan:

1. **Primero por importancia** (must → should → would)
2. **Dentro de cada grupo, por urgencia** (alta → media → baja)

### 5.2 En la Planificación Semanal

* Se planifican primero todas las acciones de metas *must*
* Luego las acciones de metas *should*
* Finalmente, si hay bloques residuales, acciones de metas *would*

### 5.3 En la Revisión

* **Fallo crítico**: Meta *must* con urgencia alta no completada
* **Fallo del sistema**: Meta *must* no completada (independientemente de urgencia)
* **No es fallo**: Meta *would* pospuesta

---

## 6. Representación en Plantillas

### 6.1 Plantilla de Meta

```md
---
tipo: meta
modalidad: must | should | would
urgencia_micro: alta | media | baja
urgencia_macro: alta | media | baja
fecha_limite:
---

# 🟠 META ({{modalidad}}): {{Título}}
```

**Nota:** La urgencia se deriva del marco temporal, pero puede anotarse explícitamente para claridad.

---

## 7. Principio Final

> **La importancia define qué es prioritario.  
> La urgencia define cuándo es prioritario.  
> La importancia siempre gana sobre la urgencia.**

Con esta clasificación, el sistema MAR:

* Elimina la ambigüedad de "prioridades subjetivas"
* Separa claramente importancia de urgencia
* Protege lo importante (must) de lo meramente urgente (would)
* Permite planificación clara y objetiva

---

## 8. Resumen Ejecutivo

| Dimensión | Definida por          | Orden                          |
| --------- | --------------------- | ------------------------------ |
| Importancia | Modalidad (must/should/would) | must > should > would |
| Urgencia  | Marco temporal (micro/macro) | Alta > Media > Baja    |
| Prioridad | Importancia + Urgencia | Importancia tiene precedencia |

**Regla de oro:**

> Una meta *must* con urgencia baja **siempre** tiene prioridad sobre una meta *would* con urgencia alta.
