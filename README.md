# (Code)yowon

`(Code)yowon` is a tiny Python project built with [smallagents](https://github.com/huggingface/smolagents). It is heavily inspired by Codex CLI and exposes a
CLI and an MCP server that used to be supported by OpenAI via [`codex`](https://github.com/openai/codex)

This program uses `Typer` and `Rich` to keep CLI look "ok", and `Textual` for TUI, but tries to stay responsive.

## Features

- CLI interface for interacting with AI models
- Terminal user interface powered by Textual
- MCP server for agent coordination
- Flexible configuration system
- Support for multiple AI models and endpoints
- Python and shell command execution capabilities
- Role-based agent orchestration

## Usage

### CLI

```bash
yowon run "Hello"
```

For an interactive conversation that keeps context between prompts:

```bash
yowon
```

For a terminal user interface powered by Textual:

```bash
yowon tui
```

For a playground with multiple agents:

```bash
yowon demo
```

### MCP Server

```bash
yowon serve
```

A demo server with multiple agents can be launched with:

```bash
yowon demo-serve
```

This will start a FastMCP server over stdio so it can cooperate with other agents.

All commands accept `--api-base` to specify an alternative OpenAI-compatible endpoint.
To pass extra HTTP headers (for Enterprise or custom deployments), repeat `--header NAME:VALUE`:

```bash
yowon run --header "X-My-Header: 1" "Hello"
```

You can tweak model behavior as well:

* `--temperature` sets the sampling temperature.
* OpenAI models starting with `o` accept `--reasoning-effort`.
* Other models can choose a wire type via `--wire`.
* `--top-p` adjusts nucleus sampling.
* `--max-tokens` limits the response length.

### Configuration file

Default values for these options can be stored in `~/.yowon/config.toml`:

```toml
model = "codex-mini-latest"
api_key = "sk-..."
api_base = "https://api.example.com/v1"
[headers]
X-Org = "42"

[agents.o3-cold]
model = "o3"
temperature = 0.0
role = "Careful reasoning"

[agents.python]
type = "python"
role = "Run Python snippets"
```
