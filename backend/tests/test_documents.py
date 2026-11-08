from app.api.routes.documents import _normalize_content_type, _suffix_for


def test_normalize_content_type_standard() -> None:
    assert _normalize_content_type("text/markdown", "readme.md") == "text/markdown"
    assert _normalize_content_type("text/plain", "notes.txt") == "text/plain"


def test_normalize_content_type_inferred_from_markdown_extension() -> None:
    assert _normalize_content_type("application/octet-stream", "doc.md") == "text/markdown"
    assert _normalize_content_type("text/x-markdown", "doc.markdown") == "text/markdown"
    assert _normalize_content_type("", "notes.md") == "text/markdown"
    assert _normalize_content_type(None, "guide.MD") == "text/markdown"


def test_normalize_content_type_inferred_from_text_extension() -> None:
    assert _normalize_content_type("application/octet-stream", "data.txt") == "text/plain"
    assert _normalize_content_type("", "log.TXT") == "text/plain"


def test_suffix_for() -> None:
    assert _suffix_for("text/markdown") == ".md"
    assert _suffix_for("text/plain") == ".txt"

