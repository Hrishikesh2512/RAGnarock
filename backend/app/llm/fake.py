"""A deterministic, keyless answer for development and tests."""

import re


class FakeProvider:
    name = "fake"

    def generate(self, prompt: str, *, api_key: str | None) -> str:
        del api_key
        match = re.search(
            r"\[1\] ([^\n]+)\n(.+?)(?:\n\n\[2\]|\n\nQuestion:|\Z)",
            prompt,
            re.DOTALL,
        )
        if not match:
            return "I could not find a relevant passage in the uploaded documents."

        source, passage = match.group(1).strip(), match.group(2).strip()
        passage = re.sub(r"\s+", " ", passage)[:600]
        return f"Based on {source}: {passage}"
