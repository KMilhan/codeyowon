# (Code)yowon Agent Development Guide

## Overview

(Code)yowon is a Python-based agent framework that supports multiple types of conversational/non-conversational agents
and agent
orchestration.

## Development Guide

### Using the Makefile

Main commands available from the Makefile for development:

#### Testing Commands

- `make test` - Run test suite
- `make coverage` - Run tests with coverage report

#### Code Quality Commands

- `make lint` - Run ruff linter
- `make typecheck` - Check types with pyright
- `make fmt` - Format code with ruff
- `make check` - Run all code quality checks

#### Documentation Commands

- `make docs` - Build documentation

#### Development Commands

- `make install` - Install package and dependencies
- `make install-dev` - Install package, dependencies and dev dependencies
- `make clean` - Clean project of build artifacts
- `make all` - Run all checks and tests

## Requirements

- Python >= 3.13
- Core Dependencies:
    - rich >= 14.0.0
    - smolagents >= 1.18.0
    - fastmcp >= 2.8.1
    - typer >= 0.16.0
    - textual >= 0.45.0

## Agent Types

- ChatSession: Base agent for general conversation
- PythonAgent: Specialized agent for Python code execution
- MultiChatSession: Manages multiple agent sessions
- OrchestratorSession: Controls agent selection and routing, handle main tasks. If no main ChatSession, work as a sole
  LLM. When TUI session, modify code and so on.

## Configuration

### Basic Agent Configuration

Agents in (Code)yowon follow a flexible configuration approach that allows customizing behavior through multiple
parameters. The framework supports both simple single-agent setups and complex multi-agent orchestration through
configuration objects.

### Configuration Parameters

- `model_id`: Specifies the model to use (e.g. "codex1", "o-model")
- `role`: Defines agent's specialized role (e.g. "main", "py", "math")
- `type`: Agent type specification ("python", "shell" or default chat)
- `api_key`: Authentication key for model API access
- `headers`: Custom headers for API requests

### Model Configuration

Model-specific parameters can be configured per model, for example,

- `temperature`: Controls randomness in responses
- `top_p`: Nucleus sampling parameter
- `max_tokens`: Maximum response length
- `reasoning_effort`: Reasoning depth ("high"/"low")

### Agent Session Configuration

Sessions can be configured in two ways, but configured behind the scene by (Code)yowon. Based on the user's
configuration, the (Code)yowon should instruct the main LLM how it should interpret/interact with the other LLMs or
non-LLM agents.

- Single agent: Basic configuration with model and role
- Multi-agent: Configuration object with multiple named agents:
