from __future__ import annotations

from datetime import date, timedelta

from multiagents.models import BacklogItem, SprintPlan, SprintTask, TaskCommand
from multiagents.registry import (
    COORDINATION_AGENTS,
    DOMAIN_AGENTS,
    OPERATION_AGENTS,
    SCRUM_ROLES,
)


SYSTEM_KEYWORDS = {
    "Todoist": ["todoist", "mar", "tarea", "tareas", "evento", "meta", "habito", "hábito"],
    "PTN": ["ptn", "proyecto", "proyectos", "notion", "nota", "notas"],
    "KIT": ["kit", "knowledge", "information", "tools", "conocimiento", "herramienta"],
    "REP": ["rep", "github", "repo", "repositorio", "repositorios"],
    "BIB": ["bib", "paperpile", "paper", "papers", "bibliografia", "bibliografía"],
    "ABGD": ["abgd", "obsidian", "vault", "nota", "notas", "documento"],
}

OPERATION_KEYWORDS = {
    "capture": ["crear", "capturar", "alta", "añadir", "agregar"],
    "query": ["listar", "consultar", "ver", "buscar", "estado"],
    "import": ["importar"],
    "sync": ["sincronizar", "actualizar"],
    "catalog": ["catalogar", "clasificar", "curar"],
    "backup": ["backup", "exportar", "respaldo"],
    "plan": ["plan", "sprint", "backlog", "scrum", "roadmap"],
}


def infer_systems(goal: str) -> list[str]:
    goal_lower = goal.lower()
    systems: list[str] = []
    for system, keywords in SYSTEM_KEYWORDS.items():
        if any(keyword in goal_lower for keyword in keywords):
            systems.append(system)
    return systems or ["MAR", "PTN", "KIT", "REP", "BIB", "ABGD"]


def infer_operations(goal: str) -> list[str]:
    goal_lower = goal.lower()
    operations: list[str] = []
    for operation, keywords in OPERATION_KEYWORDS.items():
        if any(keyword in goal_lower for keyword in keywords):
            operations.append(operation)
    return operations or ["plan", "query", "catalog", "sync"]


def select_domain_agents(systems: list[str]) -> list:
    selected = []
    for agent in DOMAIN_AGENTS:
        if any(system in agent.owned_systems for system in systems):
            selected.append(agent)
    return selected


def select_operation_agents(operations: list[str]) -> list:
    selected = []
    for agent in OPERATION_AGENTS:
        if any(operation in agent.owned_operations for operation in operations):
            selected.append(agent)
    if not any(agent.key == "intake_triage_agent" for agent in selected):
        selected.insert(0, next(agent for agent in OPERATION_AGENTS if agent.key == "intake_triage_agent"))
    if not any(agent.key == "reporting_retro_agent" for agent in selected):
        selected.append(next(agent for agent in OPERATION_AGENTS if agent.key == "reporting_retro_agent"))
    return selected


def build_backlog(goal: str, systems: list[str], operations: list[str]) -> list[BacklogItem]:
    items = [
        BacklogItem(
            key="PB-001",
            title="Definir objetivo y criterios de aceptación",
            description="Traducir la petición a backlog operativo y Definition of Done.",
            systems=systems,
            operations=["plan"],
            acceptance_criteria=[
                "Existe sprint goal explícito",
                "Cada sistema afectado tiene dueño",
                "Cada resultado tiene criterio verificable",
            ],
            priority="high",
            estimate_points=3,
        ),
        BacklogItem(
            key="PB-002",
            title="Diseñar squad multiagente por dominio y operación",
            description="Asignar agentes especializados por app y por tipo de trabajo.",
            systems=systems,
            operations=["plan"],
            acceptance_criteria=[
                "Hay un agente de dominio por sistema implicado",
                "Hay agentes transversales para triage, calidad y reporting",
                "Se documentan dependencias entre agentes",
            ],
            priority="high",
            estimate_points=5,
        ),
        BacklogItem(
            key="PB-003",
            title="Preparar incremento del sprint",
            description="Convertir el objetivo en entregables ejecutables sobre el repo actual.",
            systems=systems,
            operations=operations,
            acceptance_criteria=[
                "Cada entregable se puede mapear a un archivo o comando",
                "Cada cambio tiene owner agente",
                "Se puede inspeccionar el incremento al final del sprint",
            ],
            priority="high",
            estimate_points=8,
        ),
    ]

    if "sync" in operations or "import" in operations or "backup" in operations:
        items.append(
            BacklogItem(
                key="PB-004",
                title="Orquestar flujo de importación y sincronización",
                description="Secuenciar operaciones entre sistemas externos y el catálogo interno.",
                systems=systems,
                operations=[op for op in operations if op in {"import", "sync", "backup"}],
                acceptance_criteria=[
                    "Las dependencias están ordenadas",
                    "Los pasos tienen artefacto de salida",
                    "Los riesgos de fallo externo están anotados",
                ],
                priority="medium",
                estimate_points=5,
            )
        )

    if "catalog" in operations or "query" in operations:
        items.append(
            BacklogItem(
                key="PB-005",
                title="Definir calidad de clasificación y revisión",
                description="Normalizar estados, etiquetas y propiedades para resultados consistentes.",
                systems=systems,
                operations=[op for op in operations if op in {"catalog", "query"}],
                acceptance_criteria=[
                    "Existe criterio de consistencia semántica",
                    "Se identifican taxonomías críticas",
                    "Hay revisión final del incremento",
                ],
                priority="medium",
                estimate_points=3,
            )
        )

    return items


def _infer_sync_sources(systems: list[str]) -> list[str]:
    sources: list[str] = []
    if any(system in {"MAR", "Todoist"} for system in systems):
        sources.append("todoist")
    if "REP" in systems:
        sources.append("github")
    if "BIB" in systems:
        sources.append("paperpile")
    return sources


def _build_task_commands(agent_key: str, systems: list[str], operations: list[str]) -> list[TaskCommand]:
    commands: list[TaskCommand] = []

    if "sync" not in operations:
        return commands

    if agent_key == "todoist_mar_agent" and any(system in {"MAR", "Todoist"} for system in systems):
        commands.append(
            TaskCommand(
                label="Todoist -> TODOIST-TAREAS",
                script_path="tools/sync_todoist_to_notion.py",
                accepts_limit=True,
            )
        )
    elif agent_key == "notion_ptn_agent" and "PTN" in systems:
        commands.append(
            TaskCommand(
                label="PTN -> log changes",
                script_path="tools/log_ptn_changes.py",
            )
        )
    elif agent_key == "obsidian_abgd_agent" and "ABGD" in systems:
        commands.append(
            TaskCommand(
                label="Obsidian -> log changes",
                script_path="tools/log_obsidian_changes.py",
            )
        )
    elif agent_key == "sync_operations_agent":
        sources = _infer_sync_sources(systems)
        if len(sources) == 1:
            commands.append(
                TaskCommand(
                    label=f"Upsert INX from {sources[0]}",
                    script_path="tools/sync_inx_links.py",
                    args=["--source", sources[0]],
                    accepts_limit=True,
                )
            )
        elif len(sources) > 1:
            commands.append(
                TaskCommand(
                    label="Upsert INX from all sources",
                    script_path="tools/sync_inx_links.py",
                    args=["--source", "all"],
                    accepts_limit=True,
                )
            )

    return commands


def build_tasks(goal: str, squad_agents: list, backlog: list[BacklogItem], systems: list[str], operations: list[str]) -> list[SprintTask]:
    coordination_agent = COORDINATION_AGENTS[0]
    tasks: list[SprintTask] = [
        SprintTask(
            key="ST-001",
            title="Triage de objetivo y composición del squad",
            owner_agent=coordination_agent.key,
            scrum_role="Scrum Master",
            depends_on=[],
            deliverable="Sprint Goal, squad matrix y secuencia inicial",
        )
    ]

    domain_agents = [agent for agent in squad_agents if agent.kind == "domain"]
    operation_agents = [agent for agent in squad_agents if agent.kind == "operation"]

    task_index = 2
    for agent in domain_agents:
        tasks.append(
            SprintTask(
                key=f"ST-{task_index:03d}",
                title=f"Preparar incremento en {agent.scope}",
                owner_agent=agent.key,
                scrum_role="Developer",
                depends_on=["ST-001"],
                deliverable=f"Entregable verificable en {', '.join(agent.interfaces)}",
                commands=_build_task_commands(agent.key, systems, operations),
            )
        )
        task_index += 1

    for agent in operation_agents:
        if agent.key in {"intake_triage_agent", "reporting_retro_agent"}:
            continue
        tasks.append(
            SprintTask(
                key=f"ST-{task_index:03d}",
                title=f"Control transversal: {agent.name}",
                owner_agent=agent.key,
                scrum_role="Developer",
                depends_on=["ST-001"],
                deliverable=f"Criterios y soporte transversal para {agent.scope.lower()}",
                commands=_build_task_commands(agent.key, systems, operations),
            )
        )
        task_index += 1

    tasks.append(
        SprintTask(
            key=f"ST-{task_index:03d}",
            title="Cierre del sprint y retrospectiva",
            owner_agent="reporting_retro_agent",
            scrum_role="Scrum Master",
            depends_on=[task.key for task in tasks],
            deliverable="Sprint Review, métricas y acciones de mejora",
        )
    )

    return tasks


def plan_sprint(
    goal: str,
    sprint_name: str = "Sprint 1",
    start_date: date | None = None,
    duration_days: int = 14,
) -> SprintPlan:
    sprint_start = start_date or date.today()
    sprint_end = sprint_start + timedelta(days=duration_days - 1)
    systems = infer_systems(goal)
    operations = infer_operations(goal)

    squad_agents = [COORDINATION_AGENTS[0], *select_operation_agents(operations), *select_domain_agents(systems)]

    seen = set()
    deduped_agents = []
    for agent in squad_agents:
        if agent.key not in seen:
            deduped_agents.append(agent)
            seen.add(agent.key)

    backlog = build_backlog(goal, systems, operations)
    tasks = build_tasks(goal, deduped_agents, backlog, systems, operations)

    events = [
        "Sprint Planning",
        "Daily Scrum",
        "Backlog Refinement",
        "Sprint Review",
        "Sprint Retrospective",
    ]
    artifacts = [
        "Product Goal",
        "Sprint Goal",
        "Sprint Backlog",
        "Increment",
        "Definition of Done",
    ]

    return SprintPlan(
        sprint_name=sprint_name,
        objective=goal,
        start_date=sprint_start,
        end_date=sprint_end,
        status="planned",
        scrum_roles=SCRUM_ROLES,
        squad_agents=deduped_agents,
        backlog=backlog,
        tasks=tasks,
        events=events,
        artifacts=artifacts,
    )
