from __future__ import annotations

import os
from smolagents import CodeAgent, OpenAIServerModel

DEFAULT_MODEL = "codex-mini-latest"


class ChatSession:
    """Keep conversation state across multiple agent runs."""

    def __init__(
        self, model_id: str = DEFAULT_MODEL, api_key: str | None = None
    ) -> None:
        self._agent = create_agent(model_id=model_id, api_key=api_key)
        self._reset = True

    def ask(self, prompt: str) -> str:
        result = self._agent.run(prompt, reset=self._reset)
        self._reset = False
        return result

    def reset(self) -> None:
        self._reset = True


def create_agent(
    model_id: str = DEFAULT_MODEL, api_key: str | None = None
) -> CodeAgent:
    """Return a `CodeAgent` using the OpenAI model."""
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    model = OpenAIServerModel(model_id=model_id, api_key=api_key)
    return CodeAgent(model=model, tools=[])
