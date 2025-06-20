from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .agent import (
    ChatSession,
    DEFAULT_MODEL,
    MultiChatSession,
    OrchestratorSession,
    create_demo_session,
    create_multi_session,
    create_orchestrated_session,
)

server = FastMCP(name="yowon")

session: ChatSession | None = None
demo: MultiChatSession | OrchestratorSession | None = None


@server.tool
def chat(prompt: str) -> str:
    """Generate a reply from the assistant."""
    assert session is not None
    return session.ask(prompt)


@server.tool
def chat_demo(prompt: str, agent: str | None = None) -> str:
    """Generate a reply from one of the demo agents."""
    assert demo is not None
    if isinstance(demo, OrchestratorSession):
        return demo.ask(prompt)
    assert agent is not None
    return demo.ask(prompt, agent)


def main(
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
    global session
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


def demo_main(
    api_key: str | None = None,
    api_base: str | None = None,
    headers: dict[str, str] | None = None,
    config: dict[str, object] | None = None,
) -> None:
    """Run the FastMCP server with the demo multi-agent."""
    global demo
    if config and config.get("orchestrator"):
        demo = create_orchestrated_session(
            config,
            api_key=api_key,
            api_base=api_base,
            headers=headers,
        )
    elif config and config.get("agents"):
        demo = create_multi_session(
            config,
            api_key=api_key,
            api_base=api_base,
            headers=headers,
        )
    else:
        demo = create_demo_session(
            api_key=api_key,
            api_base=api_base,
            headers=headers,
        )
    server.run("stdio")


if __name__ == "__main__":
    main()
