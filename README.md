# (Code)yowon

`(Code)yowon` is a tiny Python project built with [smallagents](https://github.com/huggingface/smolagents). It exposes a
CLI
and an MCP server that used to be supported by OpenAI via [`codex`](https://github.com/openai/codex).

This program uses `Typer` and `Rich` to keep CLI look "ok", but tries to stay responsive.

## Usage

### CLI

```bash
yowon run "Hello"
```

For an interactive conversation that keeps context between prompts:

```bash
yowon
```

### MCP Server

```bash
yowon serve
```

This will start an MCP server over stdio so it can cooperate with other agents.

## Development

### Test

`uv run pytest`
