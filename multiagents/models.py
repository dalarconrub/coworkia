from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Literal


AgentKind = Literal["domain", "operation", "coordination"]
SprintStatus = Literal["planned", "active", "completed"]
Priority = Literal["high", "medium", "low"]


@dataclass(frozen=True)
class AgentCapability:
    name: str
    description: str


@dataclass(frozen=True)
class AgentSpec:
    key: str
    name: str
    kind: AgentKind
    scope: str
    owned_systems: list[str]
    owned_operations: list[str]
    responsibilities: list[str]
    interfaces: list[str]
    cli_entrypoint: str | None = None
    capabilities: list[AgentCapability] = field(default_factory=list)


@dataclass(frozen=True)
class ScrumRole:
    name: str
    mission: str
    owned_artifacts: list[str]


@dataclass(frozen=True)
class BacklogItem:
    key: str
    title: str
    description: str
    systems: list[str]
    operations: list[str]
    acceptance_criteria: list[str]
    priority: Priority = "medium"
    estimate_points: int = 3


@dataclass(frozen=True)
class SprintTask:
    key: str
    title: str
    owner_agent: str
    scrum_role: str
    depends_on: list[str]
    deliverable: str


@dataclass(frozen=True)
class SprintPlan:
    sprint_name: str
    objective: str
    start_date: date
    end_date: date
    status: SprintStatus
    scrum_roles: list[ScrumRole]
    squad_agents: list[AgentSpec]
    backlog: list[BacklogItem]
    tasks: list[SprintTask]
    events: list[str]
    artifacts: list[str]

