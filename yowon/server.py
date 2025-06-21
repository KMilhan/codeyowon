from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .agent import (
    DEFAULT_MODEL,
    ChatSession,
)

server = FastMCP(name="yowon")

session: ChatSession | None = None


@server.tool
def chat(prompt: str) -> str:
    """Generate a reply from the assistant."""
    if session is None:
        msg = "Session not initialized"
        raise RuntimeError(msg)
    return session.ask(prompt)



def main(  # noqa: PLR0913
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
    api_base: str | None = None,
    headers: dict[str, str] | None = None,
    temperature: float | None = None,
    reasoning_effort: str | None = None,
    wire: str | None = None,
    top_p: float | None = None,
    max_tokens: int | None = None,
) -> None:
    global session  # noqa: PLW0603
    session = ChatSession(
        model_id=model,
        api_key=api_key,
        api_base=api_base,
        headers=headers,
        temperature=temperature,
        reasoning_effort=reasoning_effort,
        wire=wire,
        top_p=top_p,
        max_tokens=max_tokens,
    )
    server.run("stdio")




if __name__ == "__main__":
    main()
