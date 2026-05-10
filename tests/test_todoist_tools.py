from tools import todoist_tools
from agents import todoist_agent


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


def test_classify_mar_type_recurrent_with_time_is_habito():
    task = {"due": {"date": "2026-05-10T09:00:00", "is_recurring": True}}

    assert todoist_tools.classify_mar_type(task) == "habito"


def test_classify_mar_type_non_recurrent_with_time_is_evento():
    task = {"due": {"date": "2026-05-10T09:00:00", "is_recurring": False}}

    assert todoist_tools.classify_mar_type(task) == "evento"


def test_classify_mar_type_deadline_is_logro():
    task = {"due": None, "deadline": {"date": "2026-05-10"}}

    assert todoist_tools.classify_mar_type(task) == "logro"


def test_classify_mar_type_due_date_without_deadline_is_tarea():
    task = {"due": {"date": "2026-05-10", "is_recurring": False}}

    assert todoist_tools.classify_mar_type(task) == "tarea"


def test_classify_mar_type_without_dates_is_idea():
    assert todoist_tools.classify_mar_type({}) == "idea"


def test_normalize_mar_type_maps_meta_to_logro():
    assert todoist_tools.normalize_mar_type("meta") == "logro"


def test_reclassify_tarea_sets_due_without_deadline():
    assert todoist_agent._reclassify_payload("tarea", "2026-05-10") == {
        "due_string": "no date",
        "due_date": "2026-05-10",
        "due_datetime": None,
        "deadline_date": None,
    }


def test_reclassify_meta_alias_sets_logro_deadline():
    assert todoist_agent._reclassify_payload("meta", "2026-05-10") == {
        "due_string": "no date",
        "due_date": None,
        "due_datetime": None,
        "deadline_date": "2026-05-10",
    }
