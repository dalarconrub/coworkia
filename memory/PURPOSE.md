# PURPOSE — Coworkia

> Qué es Coworkia, para qué existe y cuáles son sus funcionalidades canónicas.
> Documento **curado a mano**. Actualizar cuando cambie visión, división operativa o principios no negociables. Cualquier cambio deja entrada `[DOCS]` en el devlog.

## Qué es

Coworkia es un sistema multiagente en Python para **gestión personal y de conocimiento** operado por David con la asistencia coordinada de tres agentes IA (Claude, Copilot, Codex). Integra seis sistemas externos bajo una taxonomía compartida (ABC) y un lenguaje de entidades común, con sincronización cruzada vía INX.

Objetivo: eliminar fricción entre *ejecutar*, *dirigir* y *almacenar*, manteniendo una sola fuente de verdad por dominio y trazabilidad total entre ellos.

## División canónica de sistemas

Cada sistema tiene un rol funcional fijo y un código de entidad que lo identifica en toda la documentación y en el código:

| Código  | Sistema externo  | Rol operativo                                            | Agente             |
| ------- | ---------------- | -------------------------------------------------------- | ------------------ |
| `MAR`   | Todoist          | **Ejecuta** — tareas, eventos, hábitos, logros, ideas   | `todoist_agent.py` |
| `PTN`   | Notion           | **Dirige** — proyectos, tareas formales, notas         | `notion_agent.py`  |
| `KIT`   | Notion           | Catálogo único de conocimiento (Knowledge / Information / Tool) | `kit_agent.py`     |
| `GIT`   | GitHub           | Catálogo de repositorios propios y de referencia        | `github_agent.py`  |
| `BIB`   | Paperpile → Notion | Catálogo bibliográfico (artículos, libros, tesis)      | `bib_agent.py`     |
| `ABGD`  | Obsidian (vault local) | **Almacena** — notas y jerarquía viva del conocimiento | `obsidian_agent.py` |
| `INX`   | Cross-system     | Enlaces de trazabilidad entre los anteriores            | coordinado por `orchestrator_agent.py` |

Principio mnemotécnico:

- **Todoist ejecuta** — lo accionable vive ahí.
- **Notion dirige** — las decisiones y la estructura formal viven ahí.
- **Obsidian almacena** — el pensamiento vivo y la memoria a largo plazo viven ahí.

## Taxonomía ABC

La estructura organizativa transversal a todos los sistemas es **Área → Bloque → Contexto**:

- `A0..A4` Áreas (p. ej. `A0-GTD`).
- `B0..B9` Bloques dentro de cada Área.
- `C0..C9` Contextos dentro de cada Bloque.

Ejemplos canónicos: `A0-GTD`, `B0C-PLA`, `C0C7-PROYECTOS`.

Obsidian extiende a **ABPC**: Área → Bloque → Contexto → Proyecto → Tarea → Nota.

## Funcionalidades principales

### 1. Captura y ejecución diaria (MAR)
- Clasificación automática en Idea / Logro / Hábito / Tarea / Evento.
- Dashboard del día con prioridad y contexto.
- Sincronización opcional hacia Notion (`TODOIST-TAREAS`).

### 2. Dirección de proyectos y tareas (PTN)
- Tres data sources en Notion: Proyectos, Tareas, Notas.
- Jerarquía ABC respetada en cada entidad.
- Logs de cambios auditados (`log_ptn_changes.py`).

### 3. Base de conocimiento (KIT)
- Catálogo único con campo `Tipo`: Knowledge, Information, Tool.
- Subtipos: Concepto, Paper, App, etc.
- Consultable por agente y por GUI.
- **Fuentes externas que alimentan KIT** (no son catálogos separados, viven dentro de KIT con propiedades dedicadas):
  - **Google Keep** (notas exportadas vía Takeout) → `Subtipo=Nota`, clave `Google Keep ID`.
  - **Inoreader** (artículos tageados con `kit-import` — `starred` NO entra porque es "Read later") → `Tipo=Information`, `Subtipo` ∈ {`Artículo`, `Newsletter`, `Blog`, `Vídeo`, `Podcast`}, claves `Inoreader ID` + `Inoreader Tags`. Ver [docs/inoreader-agent.md](../docs/inoreader-agent.md) y caso 15.
  - **Raindrop.io** (bookmarks tageados con `kit-import` o búsqueda `RAINDROP_SEARCH_KIT`) → `Tipo=Information`, `Subtipo` ∈ {`Artículo`, `Newsletter`, `Blog`, `Vídeo`, `Podcast`, `Paper`}, claves `Raindrop ID` + `Raindrop Tags`. Ver [docs/raindrop-agent.md](../docs/raindrop-agent.md) y caso 16.

### 4. Catálogo de repositorios (GIT)
- Importación desde GitHub a Notion.
- Metadatos: lenguaje, estrellas, actividad, estado, proceso.

### 5. Bibliografía (BIB)
- Import desde Paperpile vía BibTeX.
- Catalogación por estado, relevancia, tipo, proyecto.
- Citekey canónica: `paperpile:<citekey>`.

### 6. Almacén de notas (ABGD)
- Vault Obsidian local con jerarquía ABPC. Desde 2026-05-09, el vault primario debe vivir en almacenamiento local del PC; Google Drive/nube y discos externos son réplicas o backups, no la ubicación operativa principal.
- Carpetas internas del vault: `1.ALPHA` = conocimiento vivo indexable por Coworkia; `2.BETA` = staging/inbox de procesamiento; `3.GAMMA` = productos generados; `4.DELTA` = archivos/media/documentos pesados; `5.EPSILON` = histórico frío/legacy.
- Creación, navegación y promoción a PTN cuando procede.

### 7. INX — integración y trazabilidad
- Una entidad en un sistema puede estar enlazada a entidades de otros.
- Logs diarios en `artifacts/inx/`.
- Health check vía `apps/inx_doctor.py`.

### 8. Orquestación multiagente
- Chat del día compartido (`chats/chat_YYYY-MM-DD.md`).
- Planificación por sprints con roles Scrum (`orchestrator_agent.py plan-sprint`).
- Memoria estructurada derivada (`artifacts/multiagent/`).
- Devlog feature-level (`devlog/DEVLOG.md`).

## Roles y agentes IA

- **David** — director único del sistema. Única autoridad para delegar `🎯 ESPECIALIDAD` y cerrar decisiones definitivas.
- **Cursor** — asistente operando desde el IDE Cursor en esta repo. Firma por defecto en el chat del día salvo petición explícita de usar `Claude`/`Copilot`/`Codex`.
- **Claude** — análisis profundo, revisión crítica, evaluación de alternativas, coherencia lógica.
- **Copilot** — orquestación, síntesis, integración en VS Code, visión de conjunto.
- **Codex** — generación de código, refactoring, tests, implementación técnica.

Los roles son intercambiables por petición explícita de David, pero cada agente mantiene su identidad por defecto.

## Principios no negociables

1. **Append-only en hilos compartidos.** Nunca se reescribe pasado (`chats/`, `devlog/`).
2. **UTF-8 estricto** en toda la capa de texto plano (chats, devlog, memory).
3. **Notion es la autoridad canónica** de proyectos (PTN).
4. **Todoist es la capa ejecutiva**, no de planificación.
5. **Obsidian no reemplaza a Notion**: almacena pensamiento vivo, no estructura formal.
6. **El chat del día es la única fuente de conversación viva.** Todo lo demás es derivado.
7. **Toda decisión que altere operativa o implementación genera entrada en el devlog** el mismo turno.
8. **La memoria del proyecto (`memory/`) se lee antes que cualquier otra cosa** al arrancar un agente.

## Interfaces

- **CLI** — cada agente tiene comandos directos (`python agents/<agent>.py <cmd>`).
- **Apps** — GUIs y dashboards en `apps/` (Tkinter/batch).
- **Chat multiagente** — hilo markdown diario en `chats/`.
- **Windows** — lanzadores `.bat` en raíz y `apps/` (entorno principal de David).

## Fuera de alcance

- No es un sistema de gestión de equipos. David es único usuario.
- No es un SaaS. Todo corre en local con APIs externas bajo credenciales propias.
- No sustituye a Todoist, Notion, Obsidian ni GitHub: orquesta y enlaza, no reimplementa.
