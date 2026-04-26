from tools import todoist_tools


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_get_tasks_excludes_dynamic_z_projects(monkeypatch):
    monkeypatch.setattr(
        todoist_tools,
        "get_projects",
        lambda: [
            {"id": "normal", "name": "B12-LAB"},
            {"id": "backup", "name": "Z-BACK-260419"},
        ],
    )
    monkeypatch.setattr(
        todoist_tools.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(
            [
                {"id": "task-normal", "project_id": "normal", "content": "Operativa"},
                {"id": "task-z", "project_id": "backup", "content": "Backup"},
            ]
        ),
    )

    assert [task["id"] for task in todoist_tools.get_tasks()] == ["task-normal"]


def test_get_z_tasks_includes_dynamic_z_projects(monkeypatch):
    monkeypatch.setattr(
        todoist_tools,
        "get_projects",
        lambda: [
            {"id": "normal", "name": "B12-LAB"},
            {"id": "backup", "name": "Z-BACK-260419"},
        ],
    )
    monkeypatch.setattr(
        todoist_tools.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(
            [
                {"id": "task-normal", "project_id": "normal", "content": "Operativa"},
                {"id": "task-z", "project_id": "backup", "content": "Backup"},
            ]
        ),
    )

    assert [task["id"] for task in todoist_tools.get_z_tasks()] == ["task-z"]
