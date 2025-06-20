import anyio
from textual.widgets import Input, Static
from yowon import tui

class DummySession:
    def __init__(self, **kwargs):
        pass
    def ask(self, prompt: str) -> str:
        return f"echo:{prompt}"


def test_yowon_app_responds(monkeypatch):
    async def run() -> None:
        monkeypatch.setattr(tui, "ChatSession", lambda **kwargs: DummySession())
        app = tui.YowonApp()
        async with app.run_test() as pilot:
            input_widget = app.query_one(Input)
            input_widget.value = "hello"
            app.on_input_submitted(Input.Submitted(input_widget, "hello"))
            await pilot.pause()
            log = app.query_one("#log", Static)
            assert "echo:hello" in str(log.renderable)

    anyio.run(run)


def test_demo_tui_selects_orchestrator(monkeypatch):
    recorded = {}
    class DummyApp:
        def __init__(self, session):
            recorded["session"] = session
        def run(self):
            recorded["run"] = True
    monkeypatch.setattr(tui, "DemoApp", DummyApp)
    def build(config, **kwargs):
        recorded["config"] = config
        recorded["kwargs"] = kwargs
        return "session"
    monkeypatch.setattr(tui, "create_orchestrated_session", build)
    tui.demo_tui(api_key="k", config={"orchestrator": {"model": "o3"}})
    assert recorded["session"] == "session"
    assert recorded["kwargs"]["api_key"] == "k"
    assert recorded["run"]
