from yowon import agent


class FakeAgent:
    def __init__(self):
        self.calls = []

    def run(self, prompt, reset=True, **kwargs):
        self.calls.append((prompt, reset))
        return f"echo:{prompt}-{reset}"


class DummyModel:
    def __init__(self, *args, client_kwargs=None, **kwargs):
        self.client_kwargs = client_kwargs
        self.kwargs = kwargs


class DummyAgent:
    def __init__(self, *args, prompt_templates=None, **kwargs):
        self.prompt = prompt_templates["system_prompt"] if prompt_templates else ""

    def run(self, prompt, reset=True):
        return self.prompt


def test_passes_headers(monkeypatch):
    captured = {}

    def dummy_model(**kwargs):
        captured.update(kwargs)
        return DummyModel(**kwargs)

    monkeypatch.setattr(agent, "OpenAIServerModel", dummy_model)
    headers = {"X-Test": "42"}
    agent.create_agent(headers=headers)
    assert captured["client_kwargs"]["default_headers"] == headers


def test_model_specific_kwargs(monkeypatch):
    captured = {}

    def dummy_model(**kwargs):
        captured.update(kwargs)
        return DummyModel(**kwargs)

    monkeypatch.setattr(agent, "OpenAIServerModel", dummy_model)
    agent.create_agent(model_id="o-model", reasoning_effort="high", temperature=0.5)
    assert captured["reasoning_effort"] == "high"
    assert captured["temperature"] == 0.5

    agent.create_agent(model_id="x-model", wire="mode2")
    assert captured["wire"] == "mode2"


def test_extra_openai_kwargs(monkeypatch):
    captured = {}

    def dummy_model(**kwargs):
        captured.update(kwargs)
        return DummyModel(**kwargs)

    monkeypatch.setattr(agent, "OpenAIServerModel", dummy_model)
    agent.create_agent(top_p=0.7, max_tokens=50)
    assert captured["top_p"] == 0.7
    assert captured["max_tokens"] == 50


def test_role_in_prompt(monkeypatch):
    def dummy_model(**kwargs):
        return DummyModel(**kwargs)

    monkeypatch.setattr(agent, "OpenAIServerModel", dummy_model)
    monkeypatch.setattr(agent, "CodeAgent", DummyAgent)
    ag = agent.create_agent()
    assert ag.prompt == agent.BASE_PROMPTS["system_prompt"]


def test_maintains_reset_flag():
    original = agent.create_agent
    try:
        agent.create_agent = lambda **kwargs: FakeAgent()
        session = agent.ChatSession()
        first = session.ask("hi")
        second = session.ask("again")
    finally:
        agent.create_agent = original
    assert first == "echo:hi-True"
    assert second == "echo:again-False"


def test_multi_session_dispatch(monkeypatch):
    class Dummy(agent.ChatSession):
        def __init__(self, name):
            self.name = name

        def ask(self, prompt: str) -> str:
            return f"{self.name}:{prompt}"

    sessions = {"a": Dummy("a"), "b": Dummy("b")}
    multi = agent.MultiChatSession(sessions)
    assert multi.ask("hello", "a") == "a:hello"
    assert multi.ask("hey", "b") == "b:hey"


def test_multi_session_from_config(monkeypatch):
    built = {}

    class Dummy(agent.ChatSession):
        def __init__(self, model_id, **kwargs):
            built[model_id] = kwargs

        def ask(self, prompt: str) -> str:  # pragma: no cover - not used
            return prompt

    monkeypatch.setattr(agent, "ChatSession", Dummy)
    config = {
        "agents": {
            "x": {"model": "codex1", "role": "main"},
            "py": {"type": "python", "role": "py"},
            "sh": {"type": "shell"},
        }
    }
    multi = agent.create_multi_session(config, api_key="k")
    assert set(multi.sessions) == {"x", "py", "sh"}
    assert isinstance(multi.sessions["py"], agent.PythonAgent)
    assert built["codex1"]["api_key"] == "k"
    assert multi.get_role("x") == "main"


def test_multi_agent_interaction(monkeypatch):
    class Dummy(agent.ChatSession):
        def __init__(self, model_id="llm", **kwargs):
            self.model_id = model_id

        def ask(self, prompt: str) -> str:
            return f"{self.model_id}:{prompt}"

    monkeypatch.setattr(agent, "ChatSession", Dummy)
    config = {
        "agents": {
            "llm": {"model": "codex1"},
            "py": {"type": "python"},
            "sh": {"type": "shell"},
        }
    }
    multi = agent.create_multi_session(config)
    assert multi.ask("print(2+3)", "py") == "5"
    assert multi.ask("echo hi", "sh") == "hi"
    assert multi.ask("hello", "llm") == "codex1:hello"
