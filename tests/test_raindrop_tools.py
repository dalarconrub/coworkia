from tools.raindrop_tools import merge_raindrops, normalize_raindrop


def test_normalize_raindrop_maps_core_fields():
    raw = {
        "_id": 123,
        "title": "Example bookmark",
        "link": "https://example.com/post",
        "domain": "example.com",
        "excerpt": "Short excerpt",
        "note": "Personal note",
        "tags": ["kit-import", "ai"],
        "type": "article",
        "created": "2026-05-14T10:00:00.000Z",
        "lastUpdate": "2026-05-14T11:00:00.000Z",
        "collection": {"$id": 42, "title": "Research"},
    }

    item = normalize_raindrop(raw)

    assert item["raindrop_id"] == "123"
    assert item["title"] == "Example bookmark"
    assert item["url"] == "https://example.com/post"
    assert item["tags"] == ["kit-import", "ai"]
    assert item["collection_id"] == "42"
    assert item["collection_title"] == "Research"
    assert item["summary_text"] == "Short excerpt\n\nPersonal note"
    assert item["updated_date"] == "2026-05-14"


def test_normalize_raindrop_infers_video():
    item = normalize_raindrop({
        "_id": 1,
        "title": "Video",
        "link": "https://youtube.com/watch?v=abc",
        "type": "link",
    })

    assert item["subtipo"] == "Vídeo"


def test_merge_raindrops_dedupes_by_url_and_merges_tags():
    merged = merge_raindrops([
        {"raindrop_id": "1", "url": "https://example.com", "tags": ["kit-import"]},
        {"raindrop_id": "2", "url": "https://example.com", "tags": ["ai"]},
    ])

    assert len(merged) == 1
    assert merged[0]["tags"] == ["ai", "kit-import"]
