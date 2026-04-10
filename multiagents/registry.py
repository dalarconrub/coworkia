from __future__ import annotations

from multiagents.models import AgentCapability, AgentSpec, ScrumRole


SCRUM_ROLES: list[ScrumRole] = [
    ScrumRole(
        name="Product Owner",
        mission="Mantener la visión del sprint, priorizar backlog y validar valor de negocio.",
        owned_artifacts=["Product Goal", "Product Backlog", "Sprint Goal"],
    ),
    ScrumRole(
        name="Scrum Master",
        mission="Facilitar el flujo del sprint, coordinar dependencias y eliminar bloqueos.",
        owned_artifacts=["Sprint Plan", "Daily Sync", "Retrospective"],
    ),
    ScrumRole(
        name="Developer",
        mission="Entregar incrementos verificables mediante cambios, sincronización o catalogación.",
        owned_artifacts=["Increment", "Task Board", "Definition of Done"],
    ),
]


DOMAIN_AGENTS: list[AgentSpec] = [
    AgentSpec(
        key="todoist_mar_agent",
        name="Todoist MAR Agent",
        kind="domain",
        scope="Dominio Todoist/MAR",
        owned_systems=["MAR", "Todoist"],
        owned_operations=["capture", "classify", "schedule", "dashboard"],
        responsibilities=[
            "Clasificar acciones según MAR",
            "Crear ideas, metas, hábitos, tareas y eventos",
            "Construir vistas operativas de hoy, pendientes e inbox",
        ],
        interfaces=["agents/todoist_agent.py", "apps/dashboard.py"],
        cli_entrypoint="python agents/todoist_agent.py",
        capabilities=[
            AgentCapability("resumen_hoy", "Resume acciones vigentes para hoy"),
            AgentCapability("crear_accion", "Crea acciones Todoist según tipología MAR"),
        ],
    ),
    AgentSpec(
        key="notion_ptn_agent",
        name="Notion PTN Agent",
        kind="domain",
        scope="Dominio PTN/Notion",
        owned_systems=["PTN", "Notion"],
        owned_operations=["create", "query", "relate", "status"],
        responsibilities=[
            "Gestionar proyectos, tareas y notas",
            "Consultar data sources PTN",
            "Crear registros relacionados entre proyectos y tareas",
        ],
        interfaces=["agents/notion_agent.py"],
        cli_entrypoint="python agents/notion_agent.py",
    ),
    AgentSpec(
        key="notion_kit_agent",
        name="Notion KIT Agent",
        kind="domain",
        scope="Dominio KIT/Notion",
        owned_systems=["KIT", "Notion"],
        owned_operations=["capture", "query", "search", "curate"],
        responsibilities=[
            "Gestionar conocimiento interno, información externa y herramientas",
            "Buscar y crear entradas por categoría",
        ],
        interfaces=["agents/kit_agent.py"],
        cli_entrypoint="python agents/kit_agent.py",
    ),
    AgentSpec(
        key="github_rep_agent",
        name="GitHub REP Agent",
        kind="domain",
        scope="Dominio REP/GitHub->Notion",
        owned_systems=["REP", "GitHub", "Notion"],
        owned_operations=["import", "sync", "catalog", "explore"],
        responsibilities=[
            "Importar repositorios desde GitHub",
            "Sincronizar metadata técnica",
            "Catalogar repositorios en Notion",
        ],
        interfaces=["agents/github_agent.py", "apps/github_gui.py", "apps/catalogar_repos.py"],
        cli_entrypoint="python agents/github_agent.py",
    ),
    AgentSpec(
        key="paperpile_bib_agent",
        name="Paperpile BIB Agent",
        kind="domain",
        scope="Dominio BIB/Paperpile->Notion",
        owned_systems=["BIB", "Paperpile", "Notion"],
        owned_operations=["import", "sync", "catalog", "explore"],
        responsibilities=[
            "Importar biblioteca BibTeX desde Paperpile",
            "Sincronizar papers y enriquecer metadata",
            "Catalogar estado de lectura y relevancia",
        ],
        interfaces=["agents/bib_agent.py", "apps/bib_gui.py"],
        cli_entrypoint="python agents/bib_agent.py",
    ),
    AgentSpec(
        key="obsidian_abgd_agent",
        name="Obsidian ABGD Agent",
        kind="domain",
        scope="Dominio ABGD/Obsidian",
        owned_systems=["ABGD", "Obsidian"],
        owned_operations=["map", "query", "search", "write"],
        responsibilities=[
            "Navegar la jerarquía del vault",
            "Buscar y leer notas",
            "Crear notas en contexto",
        ],
        interfaces=["agents/obsidian_agent.py"],
        cli_entrypoint="python agents/obsidian_agent.py",
    ),
]


OPERATION_AGENTS: list[AgentSpec] = [
    AgentSpec(
        key="intake_triage_agent",
        name="Intake & Triage Agent",
        kind="operation",
        scope="Clasificación de solicitudes y derivación al dominio correcto",
        owned_systems=[],
        owned_operations=["triage", "routing"],
        responsibilities=[
            "Analizar la intención de la solicitud",
            "Asignar agentes de dominio y dependencias",
            "Detectar si la acción es captura, importación, sincronización, consulta o backup",
        ],
        interfaces=["multiagents/planner.py"],
    ),
    AgentSpec(
        key="catalog_quality_agent",
        name="Catalog Quality Agent",
        kind="operation",
        scope="Calidad de catalogación y consistencia semántica",
        owned_systems=["REP", "BIB", "KIT", "PTN"],
        owned_operations=["catalog", "review", "normalize"],
        responsibilities=[
            "Validar propiedades, etiquetas y estados",
            "Comprobar coherencia de taxonomías",
            "Definir criterios de aceptación para catalogación",
        ],
        interfaces=["agents/github_agent.py", "agents/bib_agent.py", "agents/kit_agent.py", "agents/notion_agent.py"],
    ),
    AgentSpec(
        key="sync_operations_agent",
        name="Sync Operations Agent",
        kind="operation",
        scope="Ejecución y seguimiento de importaciones y sincronizaciones",
        owned_systems=["Todoist", "Notion", "GitHub", "Paperpile", "Obsidian"],
        owned_operations=["import", "sync", "backup"],
        responsibilities=[
            "Coordinar importaciones y sincronizaciones",
            "Encadenar dependencias entre sistemas",
            "Preparar incrementos verificables por sprint",
        ],
        interfaces=["apps/backs_todoist.py", "apps/backs_notion.py", "apps/backs_obsidian.py"],
    ),
    AgentSpec(
        key="reporting_retro_agent",
        name="Reporting & Retro Agent",
        kind="operation",
        scope="Artefactos Scrum, seguimiento y retrospectiva",
        owned_systems=[],
        owned_operations=["report", "inspect", "retro"],
        responsibilities=[
            "Generar backlog, sprint plan y resúmenes",
            "Consolidar hallazgos y bloqueos",
            "Documentar retrospectivas y acciones de mejora",
        ],
        interfaces=["multiagents/artifacts.py"],
    ),
]


COORDINATION_AGENTS: list[AgentSpec] = [
    AgentSpec(
        key="scrum_master_orchestrator",
        name="Scrum Master Orchestrator",
        kind="coordination",
        scope="Orquestación global del sistema multiagente",
        owned_systems=["MAR", "PTN", "KIT", "REP", "BIB", "ABGD"],
        owned_operations=["plan", "coordinate", "sprint"],
        responsibilities=[
            "Construir squads por objetivo",
            "Secuenciar trabajo por sprints",
            "Asignar agentes y definir entregables",
        ],
        interfaces=["agents/orchestrator_agent.py"],
        cli_entrypoint="python agents/orchestrator_agent.py",
    ),
]


ALL_AGENTS: list[AgentSpec] = DOMAIN_AGENTS + OPERATION_AGENTS + COORDINATION_AGENTS


def get_agent(key: str) -> AgentSpec:
    for agent in ALL_AGENTS:
        if agent.key == key:
            return agent
    raise KeyError(f"Agent not found: {key}")

