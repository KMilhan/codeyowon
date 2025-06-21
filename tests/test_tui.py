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
