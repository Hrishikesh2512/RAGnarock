from app.ingestion.chunker import chunk_text


def test_empty_text_produces_no_chunks() -> None:
    assert chunk_text("   \n\n  ") == []


def test_short_paragraphs_are_combined() -> None:
    chunks = chunk_text("First paragraph.\n\nSecond paragraph.", max_chars=100)

    assert chunks == ["First paragraph.\n\nSecond paragraph."]


def test_long_paragraph_is_split_with_overlap() -> None:
    text = "x" * 250

    chunks = chunk_text(text, max_chars=100, overlap=20)

    assert len(chunks) > 1
    assert all(len(chunk) <= 100 for chunk in chunks)
    assert chunks[0][-20:] == chunks[1][:20]
