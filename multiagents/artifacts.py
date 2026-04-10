from __future__ import annotations

from pathlib import Path

from multiagents.models import SprintPlan


def render_sprint_markdown(plan: SprintPlan) -> str:
    lines: list[str] = []
    lines.append(f"# {plan.sprint_name}")
    lines.append("")
    lines.append(f"**Sprint Goal:** {plan.objective}")
    lines.append(f"**Fechas:** {plan.start_date.isoformat()} -> {plan.end_date.isoformat()}")
    lines.append(f"**Estado:** {plan.status}")
    lines.append("")

    lines.append("## Scrum Roles")
    lines.append("")
    for role in plan.scrum_roles:
        lines.append(f"- `{role.name}`: {role.mission}")
        lines.append(f"  Artefactos: {', '.join(role.owned_artifacts)}")
    lines.append("")

    lines.append("## Squad")
    lines.append("")
    for agent in plan.squad_agents:
        systems = ", ".join(agent.owned_systems) if agent.owned_systems else "Transversal"
        operations = ", ".join(agent.owned_operations)
        lines.append(f"- `{agent.name}` [{agent.kind}]")
        lines.append(f"  Scope: {agent.scope}")
        lines.append(f"  Systems: {systems}")
        lines.append(f"  Operations: {operations}")
        if agent.cli_entrypoint:
            lines.append(f"  CLI: `{agent.cli_entrypoint}`")
    lines.append("")

    lines.append("## Sprint Backlog")
    lines.append("")
    for item in plan.backlog:
        lines.append(f"### {item.key} - {item.title}")
        lines.append(f"- Priority: `{item.priority}`")
        lines.append(f"- Estimate: `{item.estimate_points}`")
        lines.append(f"- Systems: {', '.join(item.systems)}")
        lines.append(f"- Operations: {', '.join(item.operations)}")
        lines.append(f"- Description: {item.description}")
        lines.append("- Acceptance Criteria:")
        for criterion in item.acceptance_criteria:
            lines.append(f"  - {criterion}")
        lines.append("")

    lines.append("## Task Board")
    lines.append("")
    for task in plan.tasks:
        depends = ", ".join(task.depends_on) if task.depends_on else "None"
        lines.append(f"- `{task.key}` {task.title}")
        lines.append(f"  Owner Agent: `{task.owner_agent}`")
        lines.append(f"  Scrum Role: `{task.scrum_role}`")
        lines.append(f"  Depends On: {depends}")
        lines.append(f"  Deliverable: {task.deliverable}")
    lines.append("")

    lines.append("## Scrum Events")
    lines.append("")
    for event in plan.events:
        lines.append(f"- {event}")
    lines.append("")

    lines.append("## Required Artifacts")
    lines.append("")
    for artifact in plan.artifacts:
        lines.append(f"- {artifact}")
    lines.append("")

    return "\n".join(lines)


def write_sprint_artifact(plan: SprintPlan, output_dir: str = "artifacts/sprints") -> Path:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{plan.sprint_name.lower().replace(' ', '-')}.md"
    target = target_dir / filename
    target.write_text(render_sprint_markdown(plan), encoding="utf-8")
    return target

