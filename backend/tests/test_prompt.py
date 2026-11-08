from types import SimpleNamespace

from app.rag.prompt import build_prompt
from app.rag.retriever import RetrievedChunk


def _result(filename: str, content: str, score: float = 0.9) -> RetrievedChunk:
    return RetrievedChunk(
        chunk=SimpleNamespace(content=content),
        document=SimpleNamespace(filename=filename),
        score=score,
    )


def test_prompt_numbers_context_blocks() -> None:
    prompt = build_prompt("What is RAG?", [_result("a.txt", "RAG is retrieval.")])

    assert "[1] a.txt" in prompt
    assert "RAG is retrieval." in prompt
    assert "Question: What is RAG?" in prompt
    assert "only the numbered context" in prompt
