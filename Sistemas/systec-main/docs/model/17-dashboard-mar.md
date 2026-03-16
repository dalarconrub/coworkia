# 📊 DASHBOARD MAR

## Control Operativo y Estratégico

---

## 1. Función del dashboard

> **El dashboard no sirve para motivar.  
> Sirve para ver la verdad del sistema.**

Debe responder, de un vistazo, a 5 preguntas:

1. ¿Qué metas están activas?
2. ¿Qué acciones se están ejecutando?
3. ¿En qué se ha ido el tiempo?
4. ¿Qué resultados se han producido?
5. ¿Dónde está fallando el sistema?

---

## 2. Principios de diseño (no negociables)

* Vista **única** (una pantalla / una página)
* Jerarquía visual MAR estricta
* Colores semánticos, no decorativos
* Datos **reales**, no intenciones
* Lectura en menos de 30 segundos

---

## 3. Estructura general del dashboard

```text
┌───────────────────────────────────┐
│ 🟠 METAS ACTIVAS                  │
├───────────────────────────────────┤
│ 🔵 ACCIONES EN CURSO              │
├───────────────────────────────────┤
│ ⏳ BLOQUES DE TIEMPO (HOY / SEMANA)│
├───────────────────────────────────┤
│ ⚪ RESULTADOS                     │
├───────────────────────────────────┤
│ 📈 INDICADORES CLAVE              │
└───────────────────────────────────┘
```

El orden **no se altera**.

---

## 4. Sección 1 — 🟠 Metas activas (dirección)

### Objetivo

Ver **hacia dónde va el sistema**, no qué se hace hoy.

### Contenido

* Máx. 3–5 metas activas
* Fecha límite
* Estado sintético

### Diseño

```md
## 🟠 Metas activas

| Modalidad | Meta | Límite | Estado |
|-----------|------|--------|--------|
| 🟥 must | Artículo imagen corporal | 30/04 | 🟢 |
| 🟧 should | Sistema MAR v1 | 15/03 | 🟡 |
| 🟨 would | Curso metodología | 10/05 | 🔴 |
```

**Reglas de visualización:**

* Las metas *must* se muestran **siempre primero**
* Las *should* solo después
* Las *would* nunca ocupan la parte superior del dashboard

Estados:

* 🟢 avanza
* 🟡 riesgo
* 🔴 bloqueada

---

## 5. Sección 2 — 🔵 Acciones en curso (ejecución)

### Objetivo

Detectar **qué se está ejecutando realmente**.

### Contenido

* Acciones con bloques asignados
* Meta asociada
* Estado

### Diseño

```md
## 🔵 Acciones en curso

| Acción | Meta | Bloques | Estado |
|------|------|---------|--------|
| 🔵 Redactar discusión | Artículo | 2/3 | ▶ |
| 🔵 Revisar referencias | Artículo | 1/1 | ✔ |
| 🔵 Ajustar plantillas | MAR | 1/2 | ▶ |
```

Lectura clave:

* Muchas acciones abiertas → dispersión
* Acciones sin meta → error de sistema

---

## 6. Sección 3 — ⏳ Bloques de tiempo (coste real)

### Objetivo

Ver **en qué se ha ido el tiempo**, no en qué "querías" trabajar.

### Vista diaria (mínima)

```md
## ⏳ Bloques de hoy

| Tipo | Bloques |
|----|---------|
| 🔵 Acciones | 6 |
| 🟠 Metas (indirecto) | — |
| ⚪ Resultados | — |
| ❌ Cancelados | 1 |
| 🔁 Migrados | 2 |
```

### Vista semanal (recomendada)

```md
## ⏳ Bloques de la semana

| Día | ✔ | ↺ | ✕ |
|---|---|---|---|
| L | 6 | 1 | 0 |
| M | 5 | 2 | 1 |
| X | 7 | 0 | 0 |
```

Lectura clave:

* ↺ alto → sobreestimación
* ✕ alto → interrupciones no controladas

---

## 7. Sección 4 — ⚪ Resultados (impacto)

### Objetivo

Cerrar el ciclo MAR.

### Contenido

* Resultados recientes
* Acciones origen
* Valor generado

### Diseño

```md
## ⚪ Resultados

| Resultado | Acciones origen | Valor |
|---------|----------------|-------|
| ⚪ Discusión redactada | 3 acciones | Alto |
| ⚪ Sistema MAR definido | 5 acciones | Muy alto |
```

Regla:

> **Si esta sección está vacía, el sistema está fallando.**

---

## 8. Sección 5 — 📈 Indicadores clave (diagnóstico)

### Objetivo

Detectar **patrones**, no detalles.

### KPIs mínimos

```md
## 📈 Indicadores clave

- % bloques completados: 72%
- Tasa de migración: 18%
- Acciones cerradas / semana: 9
- Resultados / semana: 3
```

### Semáforo interpretativo

* 🟢 >70% completado → sistema sano
* 🟡 50–70% → ajuste necesario
* 🔴 <50% → rediseñar carga

---

## 9. Lectura diagnóstica rápida (muy importante)

| Lo que ves       | Diagnóstico                 |
| ---------------- | --------------------------- |
| Mucho 🔵 sin ⚪   | Ejecutas pero no consolidas |
| Mucho 🟠 sin 🔵  | Planificas pero no haces    |
| Muchos ↺         | Sobrecarga                  |
| Muchos ✕         | Interferencias              |
| Pocos resultados | Falta de cierre             |

---

## 10. Versión mínima (si quieres empezar simple)

```md
# 📊 Dashboard MAR

## 🟠 Metas activas
## 🔵 Acciones en curso
## ⏳ Bloques de la semana
## ⚪ Resultados
## 📈 KPIs
```

Eso ya es suficiente para que el sistema funcione.

---

## 11. Regla final del dashboard

> **El dashboard no se consulta para sentirse bien.  
> Se consulta para decidir qué ajustar mañana.**
