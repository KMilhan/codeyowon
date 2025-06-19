from __future__ import annotations

import anyio
import click

from .agent import create_agent, DEFAULT_MODEL, ChatSession
from .server import main as serve_main


@click.group()
def cli() -> None:
    """CLI entry point for yowon."""


@cli.command()
@click.argument("prompt")
@click.option("--model", default=DEFAULT_MODEL, show_default=True)
@click.option("--api-key", envvar="OPENAI_API_KEY", help="OpenAI API key")
def run(prompt: str, model: str, api_key: str | None) -> None:
    """Run the agent once with PROMPT."""
    agent = create_agent(model_id=model, api_key=api_key)
    result = agent.run(prompt)
    print(result)


@cli.command()
@click.option("--model", default=DEFAULT_MODEL, show_default=True)
@click.option("--api-key", envvar="OPENAI_API_KEY", help="OpenAI API key")
def chat(model: str, api_key: str | None) -> None:
    """Run an interactive chat session."""
    session = ChatSession(model_id=model, api_key=api_key)
    while True:
        try:
            prompt = input("\u003e ")
        except EOFError:
            break
        if not prompt:
            continue
        if prompt.strip().lower() in {"exit", "quit"}:
            break
        answer = session.ask(prompt)
        print(answer)


@cli.command()
@click.option("--port", type=int, default=None, help="Ignored for now")
def serve(port: int | None) -> None:
    """Launch the MCP server over stdio."""
    anyio.run(serve_main)


if __name__ == "__main__":
    cli()
