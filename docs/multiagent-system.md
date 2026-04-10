# Sistema Multiagente Scrum Para Coworkia

## Objetivo

Añadir una capa de coordinación por encima de los agentes existentes para que Coworkia deje de ser solo una colección de CLIs y pase a funcionar como un sistema multiagente organizado por:

- dominio o app
- tipo de operación
- roles Scrum
- producción por sprints

## Principios

- Cada agente tiene un `scope` explícito.
- Los agentes de dominio son dueños de un sistema.
- Los agentes de operación son dueños de una clase de trabajo transversal.
- La coordinación se hace con artefactos Scrum y no con improvisación.
- El incremento de cada sprint debe mapearse a cambios verificables en el repo o a resultados ejecutables sobre los sistemas externos.

## Tipos De Agentes

### Agentes de dominio

- `Todoist MAR Agent`
- `Notion PTN Agent`
- `Notion KIT Agent`
- `GitHub REP Agent`
- `Paperpile BIB Agent`
- `Obsidian ABGD Agent`

Son responsables de entender el modelo del sistema concreto y ejecutar trabajo especializado sobre su app.

### Agentes de operación

- `Intake & Triage Agent`
- `Catalog Quality Agent`
- `Sync Operations Agent`
- `Reporting & Retro Agent`

Son responsables de trabajo transversal: triage, calidad semántica, sincronización, reporting y retrospectiva.

### Agente de coordinación

- `Scrum Master Orchestrator`

Es responsable de construir squads, secuenciar dependencias y producir el sprint plan.

## Roles Scrum

### Product Owner

- mantiene la visión del objetivo
- prioriza backlog
- valida valor del incremento

### Scrum Master

- facilita la coordinación
- elimina bloqueos
- mantiene los eventos y artefactos del sprint

### Developer

- ejecuta el trabajo de dominio u operación
- produce entregables verificables

## Artefactos

Cada sprint debe producir:

- `Product Goal`
- `Sprint Goal`
- `Sprint Backlog`
- `Increment`
- `Definition of Done`

## Flujo Operativo

1. Se recibe un objetivo.
2. El `Intake & Triage Agent` detecta sistemas y operaciones implicadas.
3. El `Scrum Master Orchestrator` construye el squad.
4. Se genera un sprint plan con backlog, tareas, dependencias, eventos y artefactos.
5. Los agentes de dominio ejecutan su parte del incremento.
6. Los agentes transversales validan calidad, coherencia y reporting.
7. El sprint cierra con review y retrospective.

## CLI Disponible

Listado de agentes:

```bash
python agents/orchestrator_agent.py agentes
```

Listado de roles:

```bash
python agents/orchestrator_agent.py roles
```

Generar sprint:

```bash
python agents/orchestrator_agent.py plan-sprint "Implementar sincronización GitHub y catalogación REP con control de calidad" --nombre "Sprint REP 1" --guardar
```

## Encaje Con El Repo Actual

La implementación actual no sustituye los agentes existentes. Los envuelve.

- `agents/*.py` siguen siendo ejecutores de dominio.
- `multiagents/registry.py` define catálogo y ownership.
- `multiagents/planner.py` compone squads y sprints.
- `multiagents/artifacts.py` genera artefactos Markdown.
- `agents/orchestrator_agent.py` expone el sistema por CLI.

## Siguiente Nivel Recomendado

La siguiente iteración útil sería:

1. conectar el orquestador con ejecución real de comandos de agentes
2. persistir backlog y sprints en Notion
3. registrar estado de tareas por agente
4. añadir Definition of Done por sistema
5. incorporar una capa LLM para planificación y reasignación dinámica

