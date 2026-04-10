# Sprint Multiagent 1

**Sprint Goal:** Implementar sistema multiagente para GitHub REP, Paperpile BIB y sincronización con sprints Scrum
**Fechas:** 2026-04-10 -> 2026-04-23
**Estado:** planned

## Scrum Roles

- `Product Owner`: Mantener la visión del sprint, priorizar backlog y validar valor de negocio.
  Artefactos: Product Goal, Product Backlog, Sprint Goal
- `Scrum Master`: Facilitar el flujo del sprint, coordinar dependencias y eliminar bloqueos.
  Artefactos: Sprint Plan, Daily Sync, Retrospective
- `Developer`: Entregar incrementos verificables mediante cambios, sincronización o catalogación.
  Artefactos: Increment, Task Board, Definition of Done

## Squad

- `Scrum Master Orchestrator` [coordination]
  Scope: Orquestación global del sistema multiagente
  Systems: MAR, PTN, KIT, REP, BIB, ABGD
  Operations: plan, coordinate, sprint
  CLI: `python agents/orchestrator_agent.py`
- `Intake & Triage Agent` [operation]
  Scope: Clasificación de solicitudes y derivación al dominio correcto
  Systems: Transversal
  Operations: triage, routing
- `Reporting & Retro Agent` [operation]
  Scope: Artefactos Scrum, seguimiento y retrospectiva
  Systems: Transversal
  Operations: report, inspect, retro
- `GitHub REP Agent` [domain]
  Scope: Dominio REP/GitHub->Notion
  Systems: REP, GitHub, Notion
  Operations: import, sync, catalog, explore
  CLI: `python agents/github_agent.py`
- `Paperpile BIB Agent` [domain]
  Scope: Dominio BIB/Paperpile->Notion
  Systems: BIB, Paperpile, Notion
  Operations: import, sync, catalog, explore
  CLI: `python agents/bib_agent.py`

## Sprint Backlog

### PB-001 - Definir objetivo y criterios de aceptación
- Priority: `high`
- Estimate: `3`
- Systems: REP, BIB
- Operations: plan
- Description: Traducir la petición a backlog operativo y Definition of Done.
- Acceptance Criteria:
  - Existe sprint goal explícito
  - Cada sistema afectado tiene dueño
  - Cada resultado tiene criterio verificable

### PB-002 - Diseñar squad multiagente por dominio y operación
- Priority: `high`
- Estimate: `5`
- Systems: REP, BIB
- Operations: plan
- Description: Asignar agentes especializados por app y por tipo de trabajo.
- Acceptance Criteria:
  - Hay un agente de dominio por sistema implicado
  - Hay agentes transversales para triage, calidad y reporting
  - Se documentan dependencias entre agentes

### PB-003 - Preparar incremento del sprint
- Priority: `high`
- Estimate: `8`
- Systems: REP, BIB
- Operations: plan
- Description: Convertir el objetivo en entregables ejecutables sobre el repo actual.
- Acceptance Criteria:
  - Cada entregable se puede mapear a un archivo o comando
  - Cada cambio tiene owner agente
  - Se puede inspeccionar el incremento al final del sprint

## Task Board

- `ST-001` Triage de objetivo y composición del squad
  Owner Agent: `scrum_master_orchestrator`
  Scrum Role: `Scrum Master`
  Depends On: None
  Deliverable: Sprint Goal, squad matrix y secuencia inicial
- `ST-002` Preparar incremento en Dominio REP/GitHub->Notion
  Owner Agent: `github_rep_agent`
  Scrum Role: `Developer`
  Depends On: ST-001
  Deliverable: Entregable verificable en agents/github_agent.py, apps/github_gui.py, apps/catalogar_repos.py
- `ST-003` Preparar incremento en Dominio BIB/Paperpile->Notion
  Owner Agent: `paperpile_bib_agent`
  Scrum Role: `Developer`
  Depends On: ST-001
  Deliverable: Entregable verificable en agents/bib_agent.py, apps/bib_gui.py
- `ST-004` Cierre del sprint y retrospectiva
  Owner Agent: `reporting_retro_agent`
  Scrum Role: `Scrum Master`
  Depends On: ST-001, ST-002, ST-003
  Deliverable: Sprint Review, métricas y acciones de mejora

## Scrum Events

- Sprint Planning
- Daily Scrum
- Backlog Refinement
- Sprint Review
- Sprint Retrospective

## Required Artifacts

- Product Goal
- Sprint Goal
- Sprint Backlog
- Increment
- Definition of Done
