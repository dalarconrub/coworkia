# Migración de MAR a Notion

## 🎯 Objetivo

Migrar el sistema de productividad MAR (basado en propiedades temporales de Todoist) a Notion usando **una única base de datos** con **múltiples fuentes (linked databases)** para mantener la lógica temporal y la clasificación automática.

---

## 📊 Arquitectura: Una Base de Datos, Múltiples Fuentes

### Concepto Clave: Linked Databases

En Notion, puedes crear **múltiples fuentes** de la misma base de datos. Cada fuente es una "vista vinculada" que puede tener:
- Sus propios filtros
- Su propio ordenamiento
- Su propia agrupación
- Su propia visualización (tabla, kanban, calendario, etc.)

**Ventaja:** Todos los cambios se sincronizan automáticamente entre todas las fuentes.

---

## 🗄️ Base de Datos Única: **Acciones**

Esta es la **única base de datos** que necesitas crear. Todas las vistas serán fuentes vinculadas de esta base de datos.

#### Propiedades Requeridas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| **Título** | Title | Nombre de la acción |
| **Tipo** | Select | IDEA, META, HÁBITO, TAREA, EVENTO (calculado) |
| **Fecha** | Date | Fecha de ejecución/compromiso |
| **Hora** | Date (con hora) | Hora específica (solo para eventos) |
| **Deadline** | Date | Fecha límite (solo para tareas) |
| **Recurrente** | Checkbox | Si es una acción recurrente |
| **Frecuencia** | Select | @d (diario), @s (semanal), @m (mensual), @a (anual) |
| **Tipo Manual** | Select | Override manual del tipo (opcional) |
| **Horizonte Temporal** | Formula | +Ayer, +Hoy, +Semana, +Mes, +Año (calculado) |
| **Estado** | Select | Activa, Completada, Cancelada |
| **Proyecto** | Relation | Relación con base de datos "Proyectos" |
| **Notas** | Text | Información adicional |

#### Fórmulas Clave

##### 1. Tipo (Clasificación Automática)

```notion
if(
  prop("Tipo Manual") != empty(),
  prop("Tipo Manual"),
  if(
    prop("Hora") != empty(),
    "EVENTO",
    if(
      prop("Deadline") != empty(),
      "TAREA",
      if(
        prop("Recurrente"),
        "HÁBITO",
        if(
          prop("Fecha") == empty() and prop("Deadline") == empty(),
          "IDEA",
          "META"
        )
      )
    )
  )
)
```

**Lógica de precedencia:**
1. Si tiene `Tipo Manual` → usar ese
2. Si tiene `Hora` → EVENTO
3. Si tiene `Deadline` → TAREA
4. Si es `Recurrente` → HÁBITO
5. Si no tiene fecha ni deadline → IDEA
6. Resto → META

##### 2. Horizonte Temporal

```notion
if(
  prop("Fecha") < dateSubtract(now(), 1, "days"),
  "+Ayer",
  if(
    prop("Fecha") == dateSubtract(now(), 0, "days"),
    "+Hoy",
    if(
      prop("Fecha") <= dateAdd(now(), 7, "days"),
      "+Semana",
      if(
        prop("Fecha") <= dateAdd(now(), 30, "days"),
        "+Mes",
        "+Año"
      )
    )
  )
)
```

---

## 🔗 Base de Datos Relacionada: **Proyectos**

Para gestionar proyectos y exclusiones (equivalente a `!#Z-*` en Todoist).

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| **Nombre** | Title | Nombre del proyecto |
| **Excluido** | Checkbox | Si está fuera del sistema MAR |
| **Acciones** | Relation | Relación con "Acciones" |

---

## 📋 Crear Múltiples Fuentes de la Base de Datos "Acciones"

### Cómo Crear una Fuente Vinculada

1. Ve a la base de datos "Acciones"
2. Click en los `...` (tres puntos) en la esquina superior derecha
3. Selecciona "Copy link"
4. En la página donde quieres la vista, escribe `/linked` y selecciona "Create linked database"
5. Pega el link de la base de datos
6. Configura los filtros, orden y visualización específicos

**Resultado:** Tienes la misma base de datos mostrada en múltiples lugares, cada una con su propia configuración.

---

## 📋 Fuentes por Tipo (Múltiples Fuentes de "Acciones")

### Fuente: **IDEA**

**Tipo:** Linked Database (fuente de "Acciones")

**Configuración:**
- **Filtros:**
  - `Tipo` = "IDEA"
  - `Estado` = "Activa"
  - `Proyecto.Excluido` ≠ true
- **Orden:**
  - Por fecha de creación (más recientes primero)
- **Visualización:** Tabla o Lista

**Dónde crear:** En la página "Dashboard MAR" → Sección "Por Tipo"

---

### Fuente: **META**

**Tipo:** Linked Database (fuente de "Acciones")

**Configuración:**
- **Filtros:**
  - `Tipo` = "META"
  - `Estado` = "Activa"
  - `Recurrente` ≠ true
  - `Hora` = empty
  - `Deadline` = empty
  - `Proyecto.Excluido` ≠ true
- **Orden:**
  - Por `Fecha` (ascendente)
- **Visualización:** Tabla o Calendario

**Dónde crear:** En la página "Dashboard MAR" → Sección "Por Tipo"

---

### Fuente: **HÁBITO**

**Tipo:** Linked Database (fuente de "Acciones")

**Configuración:**
- **Filtros:**
  - `Tipo` = "HÁBITO"
  - `Estado` = "Activa"
  - `Recurrente` = true
  - `Hora` = empty
  - `Deadline` = empty
  - `Proyecto.Excluido` ≠ true
- **Orden:**
  - Por `Frecuencia` (diario, semanal, mensual, anual)
- **Visualización:** Tabla o Lista

**Dónde crear:** En la página "Dashboard MAR" → Sección "Por Tipo"

---

### Fuente: **TAREA**

**Tipo:** Linked Database (fuente de "Acciones")

**Configuración:**
- **Filtros:**
  - `Tipo` = "TAREA"
  - `Estado` = "Activa"
  - `Hora` = empty
  - `Deadline` ≠ empty
  - `Proyecto.Excluido` ≠ true
- **Orden:**
  - Por `Deadline` (ascendente)
- **Visualización:** Tabla o Kanban (por Deadline)

**Dónde crear:** En la página "Dashboard MAR" → Sección "Por Tipo"

---

### Fuente: **EVENTO**

**Tipo:** Linked Database (fuente de "Acciones")

**Configuración:**
- **Filtros:**
  - `Tipo` = "EVENTO"
  - `Estado` = "Activa"
  - `Hora` ≠ empty
  - `Proyecto.Excluido` ≠ true
- **Orden:**
  - Por `Fecha` y `Hora` (ascendente)
- **Visualización:** Calendario o Timeline

**Dónde crear:** En la página "Dashboard MAR" → Sección "Por Tipo"

---

## ⏱️ Fuentes por Horizonte Temporal (Múltiples Fuentes)

### Fuente: **+Ayer** (Deuda)

**Tipo:** Linked Database (fuente de "Acciones")

**Configuración:**
- **Filtros:**
  - `Horizonte Temporal` = "+Ayer"
  - `Estado` = "Activa"
  - `Proyecto.Excluido` ≠ true
- **Orden:**
  - Por `Fecha` (ascendente - más antiguas primero)
- **Visualización:** Tabla

**Dónde crear:** En la página "Dashboard MAR" → Sección "Por Horizonte"

---

### Fuente: **+Hoy** (Compromiso Activo)

**Tipo:** Linked Database (fuente de "Acciones")

**Configuración:**
- **Filtros:**
  - `Horizonte Temporal` = "+Hoy"
  - `Estado` = "Activa"
  - `Proyecto.Excluido` ≠ true
- **Orden:**
  - Por `Hora` (ascendente), luego por `Tipo`
- **Visualización:** Tabla o Lista

**Dónde crear:** En la página "Dashboard MAR" → Sección "Por Horizonte"

---

### Fuente: **+Semana** (Corto Plazo)

**Tipo:** Linked Database (fuente de "Acciones")

**Configuración:**
- **Filtros:**
  - `Horizonte Temporal` = "+Semana"
  - `Estado` = "Activa"
  - `Proyecto.Excluido` ≠ true
- **Orden:**
  - Por `Fecha` (ascendente)
- **Visualización:** Tabla o Calendario

**Dónde crear:** En la página "Dashboard MAR" → Sección "Por Horizonte"

---

### Fuente: **+Mes** (Medio Plazo)

**Tipo:** Linked Database (fuente de "Acciones")

**Configuración:**
- **Filtros:**
  - `Horizonte Temporal` = "+Mes"
  - `Estado` = "Activa"
  - `Proyecto.Excluido` ≠ true
- **Orden:**
  - Por `Fecha` (ascendente)
- **Visualización:** Tabla o Calendario

**Dónde crear:** En la página "Dashboard MAR" → Sección "Por Horizonte"

---

### Fuente: **+Año** (Largo Plazo)

**Tipo:** Linked Database (fuente de "Acciones")

**Configuración:**
- **Filtros:**
  - `Horizonte Temporal` = "+Año"
  - `Estado` = "Activa"
  - `Proyecto.Excluido` ≠ true
- **Orden:**
  - Por `Fecha` (ascendente)
- **Visualización:** Tabla o Timeline

**Dónde crear:** En la página "Dashboard MAR" → Sección "Por Horizonte"

---

## 🔧 Fuentes Operativas (Filtros Combinados)

### Fuente: **Tareas con Deadline Próximo**

**Tipo:** Linked Database (fuente de "Acciones")

**Configuración:**
- **Filtros:**
  - `Tipo` = "TAREA"
  - `Estado` = "Activa"
  - `Deadline` <= dateAdd(now(), 3, "days")
  - `Proyecto.Excluido` ≠ true
- **Orden:**
  - Por `Deadline` (ascendente)
- **Visualización:** Tabla

**Dónde crear:** En la página "Dashboard MAR" → Sección "Operativas"

---

### Fuente: **Eventos de Hoy**

**Tipo:** Linked Database (fuente de "Acciones")

**Configuración:**
- **Filtros:**
  - `Tipo` = "EVENTO"
  - `Estado` = "Activa"
  - `Fecha` = today()
  - `Proyecto.Excluido` ≠ true
- **Orden:**
  - Por `Hora` (ascendente)
- **Visualización:** Lista o Timeline

**Dónde crear:** En la página "Dashboard MAR" → Sección "Operativas"

---

### Fuente: **Hábitos Diarios**

**Tipo:** Linked Database (fuente de "Acciones")

**Configuración:**
- **Filtros:**
  - `Tipo` = "HÁBITO"
  - `Estado` = "Activa"
  - `Frecuencia` = "@d"
  - `Proyecto.Excluido` ≠ true
- **Orden:**
  - Por nombre (alfabético)
- **Visualización:** Tabla o Lista

**Dónde crear:** En la página "Dashboard MAR" → Sección "Operativas"

---

## 📐 Estructura de Página Principal con Múltiples Fuentes

### Dashboard MAR

**Todas las secciones usan fuentes vinculadas (linked databases) de la misma base de datos "Acciones".**

```
📊 MAR Dashboard
│
├── 🎯 Por Tipo (5 fuentes vinculadas)
│   ├── 📝 Ideas → Fuente de "Acciones" con filtro Tipo=IDEA
│   ├── 🎯 Metas → Fuente de "Acciones" con filtro Tipo=META
│   ├── 🔁 Hábitos → Fuente de "Acciones" con filtro Tipo=HÁBITO
│   ├── ✅ Tareas → Fuente de "Acciones" con filtro Tipo=TAREA
│   └── 📅 Eventos → Fuente de "Acciones" con filtro Tipo=EVENTO
│
├── ⏱️ Por Horizonte (5 fuentes vinculadas)
│   ├── ⏪ +Ayer → Fuente de "Acciones" con filtro Horizonte=+Ayer
│   ├── 📌 +Hoy → Fuente de "Acciones" con filtro Horizonte=+Hoy
│   ├── 📆 +Semana → Fuente de "Acciones" con filtro Horizonte=+Semana
│   ├── 📅 +Mes → Fuente de "Acciones" con filtro Horizonte=+Mes
│   └── 🗓️ +Año → Fuente de "Acciones" con filtro Horizonte=+Año
│
├── 🔧 Operativas (3 fuentes vinculadas)
│   ├── Tareas Urgentes → Fuente con filtros combinados
│   ├── Eventos de Hoy → Fuente con filtros combinados
│   └── Hábitos Diarios → Fuente con filtros combinados
│
└── 📁 Proyectos
    └── [Base de datos relacionada "Proyectos"]
```

**Total: 13 fuentes vinculadas de la misma base de datos "Acciones"**

Cada fuente muestra los mismos datos pero con diferentes filtros, orden y visualización. Todos los cambios se sincronizan automáticamente.

---

## 🔄 Flujo de Trabajo Diario

### 1. Captura (IDEA)

- Crear nueva acción en base de datos "Acciones"
- Dejar `Fecha`, `Hora`, `Deadline` vacíos
- Sistema automáticamente la clasifica como **IDEA**

### 2. Decisión

- Agregar `Fecha` → se convierte en **META**
- Agregar `Hora` → se convierte en **EVENTO**
- Agregar `Deadline` → se convierte en **TAREA**
- Marcar `Recurrente` → se convierte en **HÁBITO**

### 3. Ejecución

- Usar vistas filtradas por tipo o horizonte
- Marcar como completada cuando termine

### 4. Revisión Semanal

- Vista "+Ayer" para liquidar deuda
- Vista "+Semana" para planificar próxima semana
- Revisar y ajustar tipos si es necesario

---

## 🎨 Templates de Notion

### Template: Nueva Acción

**Propiedades predefinidas:**
- `Estado` = "Activa"
- `Tipo Manual` = empty (para clasificación automática)
- `Proyecto` = [seleccionar si aplica]

### Template: Evento

**Propiedades predefinidas:**
- `Tipo Manual` = "EVENTO"
- `Hora` = [requerido]
- `Fecha` = [requerido]

### Template: Tarea

**Propiedades predefinidas:**
- `Tipo Manual` = "TAREA"
- `Deadline` = [requerido]
- `Hora` = empty

### Template: Hábito

**Propiedades predefinidas:**
- `Tipo Manual` = "HÁBITO"
- `Recurrente` = true
- `Frecuencia` = [seleccionar]
- `Hora` = empty
- `Deadline` = empty

---

## 🔗 Relaciones y Rollups

### Relación: Acciones → Proyectos

**Rollup en Proyectos:**
- **Acciones Activas:** Count de acciones con `Estado` = "Activa"
- **Próxima Acción:** Min de `Fecha` de acciones activas

### Relación: Proyectos → Acciones

**Rollup en Acciones:**
- **Proyecto Excluido:** Checkbox del proyecto relacionado
- Usar en filtros para excluir proyectos del sistema

---

## 📊 Ventajas de Notion vs Todoist

### ✅ Ventajas

1. **Bases de datos relacionadas** - Mejor gestión de proyectos
2. **Fórmulas avanzadas** - Clasificación automática más flexible
3. **Múltiples vistas** - Mismo dato, diferentes perspectivas
4. **Rollups** - Agregaciones automáticas entre bases de datos
5. **Templates** - Captura rápida y consistente
6. **Notas ricas** - Más contexto por acción
7. **Búsqueda avanzada** - Filtros complejos sin sintaxis especial

### ⚠️ Consideraciones

1. **Recurrencias** - Notion no tiene recurrencia nativa como Todoist
   - **Solución:** Usar templates o automatización externa
2. **Sincronización con calendario** - Requiere integración externa
   - **Solución:** Zapier/Make.com o API de Notion
3. **Rapidez de captura** - Notion es más lento que Todoist
   - **Solución:** Usar templates y atajos de teclado

---

## 🚀 Automatizaciones Recomendadas

### Con Zapier/Make.com

1. **Captura desde email** → Crear acción como IDEA
2. **Recordatorios** → Notificaciones para eventos
3. **Sincronización calendario** → Bidireccional con Google Calendar
4. **Revisión semanal** → Recordatorio automático

### Con API de Notion

1. **Clasificación automática** → Script que actualiza tipos
2. **Horizontes temporales** → Actualización diaria de fórmulas
3. **Limpieza de completadas** → Archivar acciones antiguas

---

## 📝 Checklist de Migración

- [ ] Crear **una única** base de datos "Acciones" con todas las propiedades
- [ ] Crear base de datos "Proyectos" (relacionada)
- [ ] Configurar fórmulas de clasificación automática (Tipo, Horizonte Temporal)
- [ ] Crear **13 fuentes vinculadas** de "Acciones" en el Dashboard:
  - [ ] 5 fuentes por Tipo (IDEA, META, HÁBITO, TAREA, EVENTO)
  - [ ] 5 fuentes por Horizonte (+Ayer, +Hoy, +Semana, +Mes, +Año)
  - [ ] 3 fuentes operativas (Tareas Urgentes, Eventos Hoy, Hábitos Diarios)
- [ ] Configurar filtros específicos en cada fuente
- [ ] Configurar orden y visualización en cada fuente
- [ ] Configurar templates para cada tipo
- [ ] Migrar acciones existentes desde Todoist
- [ ] Verificar sincronización automática entre fuentes
- [ ] Probar flujo de captura → decisión → ejecución
- [ ] Configurar automatizaciones (opcional)
- [ ] Documentar proceso para el equipo (si aplica)

## 🎯 Ventaja Clave de Múltiples Fuentes

**Una acción, múltiples vistas, sincronización automática:**

- Editas una acción en cualquier fuente → se actualiza en todas
- Cambias el tipo de una acción → aparece automáticamente en la fuente correcta
- Completas una tarea → desaparece de todas las fuentes activas
- Agregas una fecha → se recalcula el horizonte temporal en todas las fuentes

**No necesitas mantener múltiples bases de datos. Todo está en una, mostrado de diferentes formas.**

---

## 🎯 Principios MAR Mantenidos

✅ **Una acción pertenece a un solo tipo** - Garantizado por fórmula  
✅ **La hora implica rigidez** - EVENTO automático  
✅ **El deadline implica presión externa** - TAREA automática  
✅ **La recurrencia implica rutina** - HÁBITO automático  
✅ **Lo no decidido aún es una idea** - IDEA por defecto  
✅ **Sin etiquetas manuales** - Clasificación automática  
✅ **Filtros atemporales** - Vistas estables  
✅ **Excepción humana siempre gana** - Campo `Tipo Manual`

---

**El sistema MAR funciona perfectamente en Notion manteniendo todos sus principios fundamentales.**
