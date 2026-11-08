"""Build a grounded prompt from retrieved chunks."""

from app.core.config import get_settings
from app.rag.retriever import RetrievedChunk


def build_prompt(question: str, results: list[RetrievedChunk]) -> str:
    budget = get_settings().context_max_tokens * 4
    blocks: list[str] = []
    used = 0

    for index, result in enumerate(results, start=1):
        content = result.chunk.content.strip()
        remaining = budget - used
        if remaining <= 0:
            break
        content = content[:remaining]
        blocks.append(f"[{index}] {result.document.filename}\n{content}")
        used += len(content)

    context = "\n\n".join(blocks)
    return (
        "Answer the question using only the numbered context below. "
        "Cite the passage number in square brackets, for example [1]. "
        "If the answer is not in the context, say so plainly and do not guess.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )
