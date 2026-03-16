# COWORKIA — Contexto para Claude Code

## Qué es este proyecto

Sistema multi-agente IA para gestión personal integrado con el sistema MAR+ABGD de David.

Los agentes deben conocer y respetar la filosofía del sistema: no se improvisa, se clasifica.

---

## Herramientas del usuario

| Herramienta | Propósito | Sistema |
|-------------|-----------|---------|
| Todoist     | Tareas    | MAR (Meta-Acción-Resultado) |
| Notion      | Proyectos | — |
| Obsidian    | Documentos | ABGD (Alpha/Beta/Delta/Gamma) |

---

## Sistema MAR — Clasificación de tareas en Todoist

**Principio:** Las acciones se clasifican por cómo existen en el tiempo, no por lo que son.

### Tipos de acción (filtros Todoist)

| Tipo   | Filtro Todoist                              | Significado |
|--------|---------------------------------------------|-------------|
| Idea   | `no date & no deadline`                     | Sin fecha ni deadline |
| Meta   | `!recurring & !!no time & !no deadline`     | Compromiso puntual de un día |
| Hábito | `recurring & no time & no deadline`         | Rutina recurrente |
| Tarea  | `no time & !no deadline`                    | Trabajo flexible con deadline |
| Evento | `!no time`                                  | Hora fija |

### Horizonte temporal (mutuamente excluyentes)

| Horizonte    | Filtro |
|--------------|--------|
| +->Hoy       | `(!#Z-* & !search:*) & (overdue \| due before: +1 day)` |
| -+>1 Día     | `(!#Z-* & !search:*) & due after: yesterday & due before: +2day` |
| +->1 Semana  | `(!#Z-* & !search:*) & due after: today & due before: +7day` |
| +->1 Mes     | `(!#Z-* & !search:*) & (due after: +7 days & due before: +30 days)` |
| +->1 Año     | `(!#Z-* & !search:*) & (due after: +30 days & due before: +365 days)` |

**Regla de oro:** Los filtros de tipo dicen QUÉ es. Los horizontes dicen CUÁNDO vive. Nunca se mezclan.

---

## Sistema ABGD — Organización de documentos en Obsidian

### Estructura de primer nivel

| Carpeta | Propósito |
|---------|-----------|
| Alpha   | Vault activo (Johnny Decimal: Área → Bloque → Contexto) |
| Beta    | Backups cronológicos |
| Delta   | Archivo clasificado (DOC, LIB, MED, SOF) |
| Gamma   | Almacenamiento temporal |

### Áreas Alpha (nivel 1)

| Código  | Nombre | Descripción |
|---------|--------|-------------|
| A0-GTD  | Getting Things Done | Sistema operativo diario |
| A1-INV  | Investigación | Investigación académica |
| A2-UNI  | Universidad | Docencia y contenido universitario |
| A3-VIT  | Vital | Información personal |
| A4-ARC  | Archivo | Conocimiento consolidado |

---

## Estructura del proyecto

```
coworkia/
├── .env                    ← API keys (NO al repo)
├── CLAUDE.md               ← este archivo
├── Sistemas/               ← documentación de referencia de los sistemas
├── agents/
│   ├── orchestrator.py     ← orquestador principal
│   ├── todoist_agent.py    ← agente MAR/Todoist
│   ├── notion_agent.py     ← agente Notion
│   └── obsidian_agent.py   ← agente ABGD/Obsidian
├── tools/
│   ├── todoist_tools.py    ← wrappers API Todoist REST v2
│   ├── notion_tools.py     ← wrappers API Notion
│   └── obsidian_tools.py   ← lectura/escritura vault local
└── context/
    ├── mar_rules.py        ← lógica de clasificación MAR
    └── abgd_map.py         ← mapa Área/Bloque/Contexto
```

---

## Convenciones de código

- Python 3.10+
- Variables de entorno via `python-dotenv`
- Anthropic SDK para los agentes IA
- API Todoist REST v2: `https://api.todoist.com/rest/v2/`
- Sin frameworks innecesarios — código directo y legible
