from __future__ import annotations

import anyio
import tomllib
from pathlib import Path
import typer
from typer import BadParameter

from yowon.agent import DEFAULT_MODEL, create_agent, ChatSession
from yowon.server import demo_main

cli = typer.Typer(no_args_is_help=True)

CONFIG_PATH = Path.home() / ".yowon" / "config.toml"


def load_config() -> dict[str, object]:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("rb") as fh:
            return tomllib.load(fh)
    return {}


def parse_headers(values: list[str]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for item in values:
        if ":" not in item:
            raise BadParameter(f"Invalid header '{item}'. Use NAME:VALUE format.")
        name, value = item.split(":", 1)
        headers[name.strip()] = value.strip()
    return headers


def apply_config(ctx: typer.Context, value: object | None, key: str, default: object) -> object:
    config = ctx.obj or {}
    if value is not None:
        return value
    return config.get(key, default)


@cli.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """CLI entry point for yowon."""
    ctx.obj = load_config()
    if ctx.invoked_subcommand is None:
        typer.echo("Use --help for usage information.")


@cli.command()
def run(
        ctx: typer.Context,
        prompt: str = typer.Argument(...),
        model: str | None = typer.Option(None, "--model"),
        api_key: str | None = typer.Option(None, "--api-key", envvar="OPENAI_API_KEY"),
        api_base: str | None = typer.Option(None, "--api-base", envvar="OPENAI_API_BASE"),
        header: list[str] = typer.Option(
            [], "--header", "-H", help="Extra HTTP header (NAME:VALUE)", show_default=False
        ),
        temperature: float | None = typer.Option(None, "--temperature", help="Sampling temperature"),
        reasoning_effort: str | None = typer.Option(None, "--reasoning-effort", help="Reasoning effort"),
        wire: str | None = typer.Option(None, "--wire", help="Wire mode"),
        top_p: float | None = typer.Option(None, "--top-p", help="Nucleus sampling"),
        max_tokens: int | None = typer.Option(None, "--max-tokens", help="Maximum tokens"),
) -> None:
    """Run the agent once with PROMPT."""
    config_model = apply_config(ctx, model, "model", DEFAULT_MODEL)
    config_api_key = apply_config(ctx, api_key, "api_key", None)
    config_api_base = apply_config(ctx, api_base, "api_base", None)
    config_headers = {**ctx.obj.get("headers", {}), **parse_headers(header)}
    config_temperature = apply_config(ctx, temperature, "temperature", None)
    config_reasoning = apply_config(ctx, reasoning_effort, "reasoning_effort", None)
    config_wire = apply_config(ctx, wire, "wire", None)
    config_top_p = apply_config(ctx, top_p, "top_p", None)
    config_max_tokens = apply_config(ctx, max_tokens, "max_tokens", None)
    agent = create_agent(
        model_id=config_model,
        api_key=config_api_key,
        api_base=config_api_base,
        headers=config_headers,
        temperature=config_temperature,
        reasoning_effort=config_reasoning,
        wire=config_wire,
        top_p=config_top_p,
        max_tokens=config_max_tokens,
    )
    result = agent.run(prompt)
    print(result)


@cli.command()
def chat(
        ctx: typer.Context,
        model: str | None = typer.Option(None, "--model"),
        api_key: str | None = typer.Option(None, "--api-key", envvar="OPENAI_API_KEY"),
        api_base: str | None = typer.Option(None, "--api-base", envvar="OPENAI_API_BASE"),
        header: list[str] = typer.Option(
            [], "--header", "-H", help="Extra HTTP header (NAME:VALUE)", show_default=False
        ),
        temperature: float | None = typer.Option(None, "--temperature", help="Sampling temperature"),
        reasoning_effort: str | None = typer.Option(None, "--reasoning-effort", help="Reasoning effort"),
        wire: str | None = typer.Option(None, "--wire", help="Wire mode"),
        top_p: float | None = typer.Option(None, "--top-p", help="Nucleus sampling"),
        max_tokens: int | None = typer.Option(None, "--max-tokens", help="Maximum tokens"),
) -> None:
    """Run an interactive chat session."""
    config_model = apply_config(ctx, model, "model", DEFAULT_MODEL)
    config_api_key = apply_config(ctx, api_key, "api_key", None)
    config_api_base = apply_config(ctx, api_base, "api_base", None)
    config_headers = {**ctx.obj.get("headers", {}), **parse_headers(header)}
    config_temperature = apply_config(ctx, temperature, "temperature", None)
    config_reasoning = apply_config(ctx, reasoning_effort, "reasoning_effort", None)
    config_wire = apply_config(ctx, wire, "wire", None)
    config_top_p = apply_config(ctx, top_p, "top_p", None)
    config_max_tokens = apply_config(ctx, max_tokens, "max_tokens", None)
    session = ChatSession(
        model_id=config_model,
        api_key=config_api_key,
        api_base=config_api_base,
        headers=config_headers,
        temperature=config_temperature,
        reasoning_effort=config_reasoning,
        wire=config_wire,
        top_p=config_top_p,
        max_tokens=config_max_tokens,
    )
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
def serve(
        ctx: typer.Context,
        port: int | None = typer.Option(None, "--port", help="Ignored for now"),
        model: str | None = typer.Option(None, "--model"),
        api_key: str | None = typer.Option(None, "--api-key", envvar="OPENAI_API_KEY"),
        api_base: str | None = typer.Option(None, "--api-base", envvar="OPENAI_API_BASE"),
        header: list[str] = typer.Option(
            [], "--header", "-H", help="Extra HTTP header (NAME:VALUE)", show_default=False
        ),
        temperature: float | None = typer.Option(None, "--temperature", help="Sampling temperature"),
        reasoning_effort: str | None = typer.Option(None, "--reasoning-effort", help="Reasoning effort"),
        wire: str | None = typer.Option(None, "--wire", help="Wire mode"),
        top_p: float | None = typer.Option(None, "--top-p", help="Nucleus sampling"),
        max_tokens: int | None = typer.Option(None, "--max-tokens", help="Maximum tokens"),
) -> None:
    """Launch the MCP server over stdio."""
    config_model = apply_config(ctx, model, "model", DEFAULT_MODEL)
    config_api_key = apply_config(ctx, api_key, "api_key", None)
    config_api_base = apply_config(ctx, api_base, "api_base", None)
    config_headers = {**ctx.obj.get("headers", {}), **parse_headers(header)}
    config_temperature = apply_config(ctx, temperature, "temperature", None)
    config_reasoning = apply_config(ctx, reasoning_effort, "reasoning_effort", None)
    config_wire = apply_config(ctx, wire, "wire", None)
    config_top_p = apply_config(ctx, top_p, "top_p", None)
    config_max_tokens = apply_config(ctx, max_tokens, "max_tokens", None)
    anyio.run(
        lambda: serve_main(
            model=config_model,
            api_key=config_api_key,
            api_base=config_api_base,
            headers=config_headers,
            temperature=config_temperature,
            reasoning_effort=config_reasoning,
            wire=config_wire,
            top_p=config_top_p,
            max_tokens=config_max_tokens,
        )
    )


@cli.command()
def demo_serve(ctx: typer.Context) -> None:
    """Start the MCP server exposing demo agents."""
    config_api_key = apply_config(ctx, None, "api_key", None)
    config_api_base = apply_config(ctx, None, "api_base", None)
    config_headers = ctx.obj.get("headers", {})
    anyio.run(
        lambda: demo_main(
            api_key=config_api_key,
            api_base=config_api_base,
            headers=config_headers,
            config=ctx.obj,
        )
    )


@cli.command()
def tui(
        ctx: typer.Context,
        model: str | None = typer.Option(None, "--model"),
        api_key: str | None = typer.Option(None, "--api-key", envvar="OPENAI_API_KEY"),
        api_base: str | None = typer.Option(None, "--api-base", envvar="OPENAI_API_BASE"),
        header: list[str] = typer.Option(
            [], "--header", "-H", help="Extra HTTP header (NAME:VALUE)", show_default=False
        ),
        temperature: float | None = typer.Option(None, "--temperature", help="Sampling temperature"),
        reasoning_effort: str | None = typer.Option(None, "--reasoning-effort", help="Reasoning effort"),
        wire: str | None = typer.Option(None, "--wire", help="Wire mode"),
        top_p: float | None = typer.Option(None, "--top-p", help="Nucleus sampling"),
        max_tokens: int | None = typer.Option(None, "--max-tokens", help="Maximum tokens"),
) -> None:
    """Run the Textual chat interface."""
    config_model = apply_config(ctx, model, "model", DEFAULT_MODEL)
    config_api_key = apply_config(ctx, api_key, "api_key", None)
    config_api_base = apply_config(ctx, api_base, "api_base", None)
    config_headers = {**ctx.obj.get("headers", {}), **parse_headers(header)}
    config_temperature = apply_config(ctx, temperature, "temperature", None)
    config_reasoning = apply_config(ctx, reasoning_effort, "reasoning_effort", None)
    config_wire = apply_config(ctx, wire, "wire", None)
    config_top_p = apply_config(ctx, top_p, "top_p", None)
    config_max_tokens = apply_config(ctx, max_tokens, "max_tokens", None)
    tui_main(
        model=config_model,
        api_key=config_api_key,
        api_base=config_api_base,
        headers=config_headers,
        temperature=config_temperature,
        reasoning_effort=config_reasoning,
        wire=config_wire,
        top_p=config_top_p,
        max_tokens=config_max_tokens,
    )


@cli.command()
def demo(ctx: typer.Context) -> None:
    """Launch the demo interface exposing several agents."""
    config_api_key = apply_config(ctx, None, "api_key", None)
    config_api_base = apply_config(ctx, None, "api_base", None)
    config_headers = ctx.obj.get("headers", {})
    demo_tui(
        api_key=config_api_key,
        api_base=config_api_base,
        headers=config_headers,
        config=ctx.obj,
    )


if __name__ == "__main__":
    cli()
