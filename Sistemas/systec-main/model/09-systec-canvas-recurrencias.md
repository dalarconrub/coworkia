
# MAR — Canvas de Recurrencias y Filtros Temporales

---

## 🧭 Capa 1 · Ontología temporal (lo que define el tipo)

> **Esta capa decide QUÉ ES cada cosa.**  
> No admite excepciones.

```

┌──────────────────────────────┐
│ ¿Tiene hora fija?            │
└──────────────┬───────────────┘
│
┌──────┴───────┐
│              │
SÍ             NO
│              │
EVENTO     ┌─────────────────────┐
│ ¿Tiene deadline?     │
└──────────┬──────────┘
│
┌───────┴───────┐
│               │
SÍ              NO
│               │
TAREA     ┌───────────────────┐
│ ¿Es recurrente?   │
└────────┬──────────┘
│
┌───────┴───────┐
│               │
SÍ              NO
│               │
HÁBITO           META

(Si no tiene fecha ni deadline → IDEA)

```

---

## ⏱️ Capa 2 · Filtros canónicos en Todoist (estructura)

> **Esta capa es técnica.**  
> Usa solo propiedades nativas de Todoist.

| Tipo | Filtro |
|-----|--------|
| **Idea** | `no date & no deadline` |
| **Meta** | `!recurring & no time & no deadline` |
| **Hábito** | `recurring & no time & no deadline` |
| **Tarea** | `no time & !no deadline` |
| **Evento** | `!no time` |

---

## 🔁 Capa 3 · Ritmo de ejecución (marcadores humanos)

> **Esta capa NO define el tipo.**  
> Describe el *ritmo esperado*.

```

@d  → Diario
@s  → Semanal
@m  → Mensual
@a  → Anual

```

### Ejemplos
```

Ensayar clarinete @d
Revisión bibliografía @s
Backup archivos @m
Declaración IRPF @a

```

---

## 🧠 Capa 4 · Qué significan (y qué NO)

### ✔️ Sí significan
- Carga cognitiva
- Ritmo natural
- Guía para revisión

### ❌ NO significan
- Tipo de acción
- Prioridad
- Deadline
- Sustituto de `recurring`

---

## 🔎 Capa 5 · Vistas útiles (opcional)

```

search:@d        → Rutinas diarias
search:@s        → Mantenimiento semanal
search:@m | @a   → Largo plazo

```
```

recurring & search:@d

```
→ Hábitos diarios bien definidos

---

## 🧱 Reglas de coherencia MAR

1. El **tipo** lo decide el árbol, no los marcadores  
2. El **deadline** solo se usa para presión externa real  
3. La **meta no lleva deadline** (la fecha ya es el compromiso)  
4. Los marcadores **no corrigen** una mala clasificación  

---

## 🏁 Regla final del canvas

> **MAR separa tres planos:**
>
> - Ontología temporal → filtros  
> - Presión externa → deadline  
> - Ritmo humano → @d @s @m @a
>
> Mezclarlos rompe el sistema.
