from tools.obsidian_note_metadata import (
    inx_note_metadata_props,
    inx_note_route_props,
    note_metadata_from_frontmatter,
    obsidian_db_metadata_props,
    obsidian_db_route_props,
    route_metadata_from_relative_path,
)


def test_note_metadata_from_frontmatter_supports_aliases_and_lists():
    fm = {
        "status": "activa",
        "project": "JA-Linea-1-2026",
        "task": "lectura",
        "tags": ["#paper", "lectura"],
        "people": ["David"],
        "source": "Paperpile",
        "aliases": ["Nombre alternativo"],
        "type": "paper",
    }

    assert note_metadata_from_frontmatter(fm) == {
        "tipo": "paper",
        "estado": "activa",
        "proyecto": "JA-Linea-1-2026",
        "tarea": "lectura",
        "tags": ["paper", "lectura"],
        "personas": ["David"],
        "fuente": "Paperpile",
        "alias": "Nombre alternativo",
    }


def test_obsidian_db_metadata_props_only_writes_existing_schema_fields():
    metadata = {
        "tipo": "nota",
        "estado": "activa",
        "tags": ["lectura"],
        "personas": ["David"],
        "fuente": "Paperpile",
        "proyecto": "Proyecto X",
        "tarea": "Tarea Y",
        "alias": "Alias Z",
    }

    props = obsidian_db_metadata_props(metadata, {"Tipo", "Estado", "Tags", "Fuente"})

    assert set(props) == {"Tipo", "Estado", "Tags", "Fuente"}
    assert props["Tipo"]["select"]["name"] == "nota"
    assert props["Estado"]["select"]["name"] == "activa"
    assert props["Tags"]["multi_select"][0]["name"] == "lectura"
    assert props["Fuente"]["rich_text"][0]["text"]["content"] == "Paperpile"


def test_inx_note_metadata_props_maps_to_prefixed_fields():
    source_props = {
        "Estado": {"value": "activa"},
        "Tags": {"value": "lectura, paper"},
        "Fuente": {"value": "Paperpile"},
        "Tipo": {"value": "nota"},
    }

    props = inx_note_metadata_props(
        source_props,
        lambda raw: raw.get("value", ""),
        {"Nota Estado", "Nota Tags", "Nota Fuente", "Nota Tipo"},
    )

    assert set(props) == {"Nota Estado", "Nota Tags", "Nota Fuente", "Nota Tipo"}
    assert props["Nota Estado"]["select"]["name"] == "activa"
    assert [item["name"] for item in props["Nota Tags"]["multi_select"]] == ["lectura", "paper"]
    assert props["Nota Fuente"]["rich_text"][0]["text"]["content"] == "Paperpile"
    assert props["Nota Tipo"]["select"]["name"] == "nota"


def test_route_metadata_from_relative_path_derives_abpc_segments():
    metadata = route_metadata_from_relative_path(
        "A1-INV/B13-PUB/C137-ART/P137.01-LMS/T13701.03-Revision/N260510-nota.md"
    )

    assert metadata == {
        "area": "A1-INV",
        "bloque": "B13-PUB",
        "contexto": "C137-ART",
        "proyecto": "P137.01-LMS",
        "tarea": "T13701.03-Revision",
        "nota": "N260510-nota",
        "nivel": "nota",
    }


def test_obsidian_db_route_props_only_writes_existing_schema_fields():
    metadata = route_metadata_from_relative_path("A0-GTD/B0A-INX/C0C9-Notas/N260510-inx.md")

    props = obsidian_db_route_props(metadata, {"Ruta Area", "Ruta Bloque", "Ruta Nota"})

    assert set(props) == {"Ruta Area", "Ruta Bloque", "Ruta Nota"}
    assert props["Ruta Area"]["rich_text"][0]["text"]["content"] == "A0-GTD"
    assert props["Ruta Bloque"]["rich_text"][0]["text"]["content"] == "B0A-INX"
    assert props["Ruta Nota"]["rich_text"][0]["text"]["content"] == "N260510-inx"


def test_inx_note_route_props_maps_to_obsidian_prefixed_fields():
    source_props = {
        "Ruta Area": {"value": "A1-INV"},
        "Ruta Contexto": {"value": "C137-ART"},
        "Ruta Proyecto": {"value": "P137.01-LMS"},
    }

    props = inx_note_route_props(
        source_props,
        lambda raw: raw.get("value", ""),
        {"Obsidian Area", "Obsidian Contexto", "Obsidian Proyecto"},
    )

    assert set(props) == {"Obsidian Area", "Obsidian Contexto", "Obsidian Proyecto"}
    assert props["Obsidian Area"]["rich_text"][0]["text"]["content"] == "A1-INV"
    assert props["Obsidian Contexto"]["rich_text"][0]["text"]["content"] == "C137-ART"
    assert props["Obsidian Proyecto"]["rich_text"][0]["text"]["content"] == "P137.01-LMS"
