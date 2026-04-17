from __future__ import annotations

import json
import re
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from multiagents.models import (
    AgentCapability,
    AgentSpec,
    BacklogItem,
    CommandExecution,
    ScrumRole,
    SprintPlan,
    SprintRun,
    SprintTask,
    TaskCommand,
    TaskExecution,
)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "sprint"


def utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def render_sprint_markdown(plan: SprintPlan, task_states: dict[str, TaskExecution] | None = None) -> str:
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
        task_state = task_states.get(task.key) if task_states else None
        lines.append(f"- `{task.key}` {task.title}")
        lines.append(f"  Owner Agent: `{task.owner_agent}`")
        lines.append(f"  Scrum Role: `{task.scrum_role}`")
        lines.append(f"  Depends On: {depends}")
        lines.append(f"  Deliverable: {task.deliverable}")
        if task_state:
            lines.append(f"  Status: `{task_state.status}`")
        if task.commands:
            lines.append("  Runbook:")
            for command in task.commands:
                rendered = " ".join([command.script_path, *command.args]).strip()
                lines.append(f"  - {command.label}: `{rendered}`")
        if task_state and task_state.notes:
            lines.append("  Notes:")
            for note in task_state.notes:
                lines.append(f"  - {note}")
        if task_state and task_state.artifacts:
            lines.append("  Artifacts:")
            for artifact in task_state.artifacts:
                lines.append(f"  - `{artifact}`")
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


def sprint_paths(sprint_name: str, output_dir: str = "artifacts/sprints") -> tuple[Path, Path]:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(sprint_name)
    return target_dir / f"{slug}.md", target_dir / f"{slug}.json"


def create_sprint_run(plan: SprintPlan) -> SprintRun:
    now = utc_now_iso()
    task_states = [TaskExecution(task_key=task.key) for task in plan.tasks]
    return SprintRun(plan=plan, task_states=task_states, created_at=now, updated_at=now)


def write_sprint_artifact(plan: SprintPlan, output_dir: str = "artifacts/sprints") -> Path:
    target, _ = sprint_paths(plan.sprint_name, output_dir=output_dir)
    target.write_text(render_sprint_markdown(plan), encoding="utf-8")
    return target


def write_sprint_run_artifacts(run: SprintRun, output_dir: str = "artifacts/sprints") -> tuple[Path, Path]:
    markdown_path, json_path = sprint_paths(run.plan.sprint_name, output_dir=output_dir)
    state_map = {state.task_key: state for state in run.task_states}
    markdown_path.write_text(render_sprint_markdown(run.plan, state_map), encoding="utf-8")
    json_path.write_text(json.dumps(asdict(run), ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return markdown_path, json_path


def _load_task_command(data: dict) -> TaskCommand:
    return TaskCommand(
        label=data["label"],
        script_path=data["script_path"],
        args=list(data.get("args", [])),
        accepts_limit=bool(data.get("accepts_limit", False)),
    )


def _load_sprint_task(data: dict) -> SprintTask:
    return SprintTask(
        key=data["key"],
        title=data["title"],
        owner_agent=data["owner_agent"],
        scrum_role=data["scrum_role"],
        depends_on=list(data.get("depends_on", [])),
        deliverable=data["deliverable"],
        commands=[_load_task_command(item) for item in data.get("commands", [])],
    )


def _load_backlog_item(data: dict) -> BacklogItem:
    return BacklogItem(
        key=data["key"],
        title=data["title"],
        description=data["description"],
        systems=list(data.get("systems", [])),
        operations=list(data.get("operations", [])),
        acceptance_criteria=list(data.get("acceptance_criteria", [])),
        priority=data.get("priority", "medium"),
        estimate_points=int(data.get("estimate_points", 3)),
    )


def _load_scrum_role(data: dict) -> ScrumRole:
    return ScrumRole(
        name=data["name"],
        mission=data["mission"],
        owned_artifacts=list(data.get("owned_artifacts", [])),
    )


def _load_agent_spec(data: dict) -> AgentSpec:
    return AgentSpec(
        key=data["key"],
        name=data["name"],
        kind=data["kind"],
        scope=data["scope"],
        owned_systems=list(data.get("owned_systems", [])),
        owned_operations=list(data.get("owned_operations", [])),
        responsibilities=list(data.get("responsibilities", [])),
        interfaces=list(data.get("interfaces", [])),
        cli_entrypoint=data.get("cli_entrypoint"),
        capabilities=[
            AgentCapability(name=item["name"], description=item["description"])
            for item in data.get("capabilities", [])
        ],
    )


def _load_command_execution(data: dict) -> CommandExecution:
    return CommandExecution(
        label=data["label"],
        command=list(data.get("command", [])),
        status=data.get("status", "pending"),
        started_at=data.get("started_at"),
        finished_at=data.get("finished_at"),
        exit_code=data.get("exit_code"),
        note=data.get("note"),
    )


def _load_task_execution(data: dict) -> TaskExecution:
    return TaskExecution(
        task_key=data["task_key"],
        status=data.get("status", "pending"),
        started_at=data.get("started_at"),
        finished_at=data.get("finished_at"),
        exit_code=data.get("exit_code"),
        artifacts=list(data.get("artifacts", [])),
        notes=list(data.get("notes", [])),
        command_results=[_load_command_execution(item) for item in data.get("command_results", [])],
    )


def load_sprint_run(sprint_name: str, output_dir: str = "artifacts/sprints") -> SprintRun:
    _, json_path = sprint_paths(sprint_name, output_dir=output_dir)
    data = json.loads(json_path.read_text(encoding="utf-8"))
    plan_data = data["plan"]
    plan = SprintPlan(
        sprint_name=plan_data["sprint_name"],
        objective=plan_data["objective"],
        start_date=datetime.fromisoformat(plan_data["start_date"]).date(),
        end_date=datetime.fromisoformat(plan_data["end_date"]).date(),
        status=plan_data["status"],
        scrum_roles=[_load_scrum_role(item) for item in plan_data.get("scrum_roles", [])],
        squad_agents=[_load_agent_spec(item) for item in plan_data.get("squad_agents", [])],
        backlog=[_load_backlog_item(item) for item in plan_data.get("backlog", [])],
        tasks=[_load_sprint_task(item) for item in plan_data.get("tasks", [])],
        events=list(plan_data.get("events", [])),
        artifacts=list(plan_data.get("artifacts", [])),
    )
    return SprintRun(
        plan=plan,
        task_states=[_load_task_execution(item) for item in data.get("task_states", [])],
        created_at=data["created_at"],
        updated_at=data["updated_at"],
    )
