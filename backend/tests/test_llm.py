from app.llm.fake import FakeProvider


def test_fake_provider_uses_the_first_context_block() -> None:
    prompt = "Context:\n[1] notes.txt\nAlpha beta gamma.\n\n[2] other.txt\nDelta."

    answer = FakeProvider().generate(prompt, api_key=None)

    assert "notes.txt" in answer
    assert "Alpha beta gamma." in answer
    assert "Question:" not in answer


def test_fake_provider_handles_missing_context() -> None:
    answer = FakeProvider().generate("No numbered context here.", api_key=None)

    assert "could not find" in answer.lower()
