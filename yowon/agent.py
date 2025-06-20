from __future__ import annotations

import os
import importlib.resources
import yaml
from smolagents import CodeAgent, OpenAIServerModel
import subprocess
import sys

DEFAULT_MODEL = "codex-mini-latest"

PROMPT_PATH = importlib.resources.files("smolagents.prompts").joinpath("code_agent.yaml")
BASE_PROMPTS: dict[str, str] = yaml.safe_load(PROMPT_PATH.read_text())


class ChatSession:
    """Keep conversation state across multiple agent runs."""

    def __init__(
        self,
        model_id: str = DEFAULT_MODEL,
        api_key: str | None = None,
        api_base: str | None = None,
        headers: dict[str, str] | None = None,
        temperature: float | None = None,
        reasoning_effort: str | None = None,
        wire: str | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        self._agent = create_agent(
            model_id=model_id,
            api_key=api_key,
            api_base=api_base,
            headers=headers,
            temperature=temperature,
            reasoning_effort=reasoning_effort,
            wire=wire,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        self._reset = True

    def ask(self, prompt: str) -> str:
        result = self._agent.run(prompt, reset=self._reset)
        self._reset = False
        return result

    def reset(self) -> None:
        self._reset = True


def create_agent(
    model_id: str = DEFAULT_MODEL,
    api_key: str | None = None,
    api_base: str | None = None,
    headers: dict[str, str] | None = None,
    temperature: float | None = None,
    reasoning_effort: str | None = None,
    wire: str | None = None,
    top_p: float | None = None,
    max_tokens: int | None = None,
    role: str | None = None,
) -> CodeAgent:
    """Return a `CodeAgent` using the OpenAI model."""
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    client_kwargs = {"default_headers": headers} if headers else None
    model_kwargs = {}
    if temperature is not None:
        model_kwargs["temperature"] = temperature
    if top_p is not None:
        model_kwargs["top_p"] = top_p
    if max_tokens is not None:
        model_kwargs["max_tokens"] = max_tokens
    if model_id.startswith("o"):
        if reasoning_effort is not None:
            model_kwargs["reasoning_effort"] = reasoning_effort
    elif wire is not None:
        model_kwargs["wire"] = wire

    model = OpenAIServerModel(
        model_id=model_id,
        api_key=api_key,
        api_base=api_base,
        client_kwargs=client_kwargs,
        **model_kwargs,
    )
    return CodeAgent(model=model, tools=[], prompt_templates=BASE_PROMPTS)


class MultiChatSession:
    """Hold several chat sessions and dispatch queries by name."""

    def __init__(self, sessions: dict[str, ChatSession], roles: dict[str, str] | None = None):
        self.sessions = sessions
        self.roles = roles or {}

    def ask(self, prompt: str, target: str) -> str:
        if target not in self.sessions:
            raise KeyError(target)
        return self.sessions[target].ask(prompt)

    def options(self) -> list[str]:
        return list(self.sessions)

    def get_role(self, name: str) -> str | None:
        return self.roles.get(name)


class PythonAgent:
    """Execute Python snippets and return their output."""

    def __init__(self) -> None:
        self._globals: dict[str, object] = {}

    def ask(self, prompt: str) -> str:
        try:
            result = subprocess.run(
                [sys.executable, "-c", prompt], capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip() or result.stderr.strip()
        except Exception as exc:  # pragma: no cover - subprocess errors
            return str(exc)


class ShellAgent:
    """Execute shell commands and return their output."""

    def ask(self, prompt: str) -> str:
        try:
            result = subprocess.run(prompt, shell=True, capture_output=True, text=True, timeout=10)
            return result.stdout.strip() or result.stderr.strip()
        except Exception as exc:  # pragma: no cover - subprocess errors
            return str(exc)

def create_multi_session(
    config: dict[str, object],
    *,
    api_key: str | None = None,
    api_base: str | None = None,
    headers: dict[str, str] | None = None,
) -> MultiChatSession:
    """Build a ``MultiChatSession`` from configuration."""

    agents = config.get("agents", {})
    sessions: dict[str, ChatSession | PythonAgent | ShellAgent] = {}
    roles: dict[str, str] = {}
    for name, opts in agents.items():
        agent_type = opts.get("type", "openai")
        if agent_type == "python":
            sessions[name] = PythonAgent()
            if "role" in opts:
                roles[name] = opts["role"]
            continue
        if agent_type == "shell":
            sessions[name] = ShellAgent()
            if "role" in opts:
                roles[name] = opts["role"]
            continue
        sessions[name] = ChatSession(
            model_id=opts.get("model", DEFAULT_MODEL),
            api_key=opts.get("api_key", api_key),
            api_base=opts.get("api_base", api_base),
            headers={**(headers or {}), **opts.get("headers", {})},
            temperature=opts.get("temperature"),
            reasoning_effort=opts.get("reasoning_effort"),
            wire=opts.get("wire"),
            top_p=opts.get("top_p"),
            max_tokens=opts.get("max_tokens"),
        )
        if "role" in opts:
            roles[name] = opts["role"]

    return MultiChatSession(sessions, roles)


class OrchestratorSession:
    """Use one agent to route prompts to a multi-agent setup."""

    def __init__(self, orchestrator: ChatSession, multi: MultiChatSession) -> None:
        self.orchestrator = orchestrator
        self.multi = multi

    def ask(self, prompt: str) -> str:
        summary = "\n".join(
            f"{name}: {role}" for name, role in self.multi.roles.items()
        )
        choice = self.orchestrator.ask(
            f"Agents:\n{summary}\nUser:{prompt}\nPick agent name"
        ).strip()
        return self.multi.ask(prompt, choice)

    def options(self) -> list[str]:
        return self.multi.options()


def create_orchestrated_session(
    config: dict[str, object],
    *,
    api_key: str | None = None,
    api_base: str | None = None,
    headers: dict[str, str] | None = None,
) -> OrchestratorSession:
    """Build an ``OrchestratorSession`` from configuration."""

    orchestrator_cfg = config.get("orchestrator", {})
    orchestrator = ChatSession(
        model_id=orchestrator_cfg.get("model", DEFAULT_MODEL),
        api_key=orchestrator_cfg.get("api_key", api_key),
        api_base=orchestrator_cfg.get("api_base", api_base),
        headers={**(headers or {}), **orchestrator_cfg.get("headers", {})},
        temperature=orchestrator_cfg.get("temperature"),
        reasoning_effort=orchestrator_cfg.get("reasoning_effort"),
        wire=orchestrator_cfg.get("wire"),
        top_p=orchestrator_cfg.get("top_p"),
        max_tokens=orchestrator_cfg.get("max_tokens"),
    )

    multi = create_multi_session(
        config,
        api_key=api_key,
        api_base=api_base,
        headers=headers,
    )

    return OrchestratorSession(orchestrator, multi)


def create_demo_session(
    *, api_key: str | None = None, api_base: str | None = None, headers: dict[str, str] | None = None
) -> MultiChatSession:
    """Return a ``MultiChatSession`` with a selection of models."""

    spec = {
        "agents": {
            "o3-cold": {"model": "o3", "temperature": 0.0, "role": "Careful reasoning"},
            "o3-hot": {"model": "o3", "temperature": 0.7, "role": "Creative ideas"},
            "codex-mini-latest": {"model": "codex-mini-latest"},
            "codex1": {"model": "codex1"},
            "llama": {"model": "llama"},
            "python": {"type": "python", "role": "Run Python snippets"},
            "shell": {"type": "shell", "role": "Execute shell commands"},
        }
    }

    return create_multi_session(spec, api_key=api_key, api_base=api_base, headers=headers)

