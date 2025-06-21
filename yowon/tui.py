from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Input, Static

from yowon.agent import (
    DEFAULT_MODEL,
    ChatSession,
)


class ChatView(Container):
    messages: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        yield Static(self.messages, id="log")
        yield Input(placeholder="Ask something...", id="input")

    def on_mount(self) -> None:
        self.query_one("#input").focus()

    def add_message(self, text: str) -> None:
        log = self.query_one("#log", Static)
        log.update(log.renderable + f"\n{text}")
        self.query_one("#input").focus()


class YowonApp(App):
    CSS = """
    #log {
        height: 1fr;
        overflow-y: auto;
    }
    #input {
        height: auto;
    }
    """

    def __init__(  # noqa: PLR0913
        self,
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
        super().__init__()
        self.session = ChatSession(
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

    def compose(self) -> ComposeResult:
        yield ChatView()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if not event.value.strip():
            return
        prompt = event.value
        self.query_one(Input).value = ""
        self.query_one(ChatView).add_message(f"> {prompt}")
        answer = self.session.ask(prompt)
        self.query_one(ChatView).add_message(answer)




def main(  # noqa: PLR0913
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
    YowonApp(
        model=model,
        api_key=api_key,
        api_base=api_base,
        headers=headers,
        temperature=temperature,
        reasoning_effort=reasoning_effort,
        wire=wire,
        top_p=top_p,
        max_tokens=max_tokens,
    ).run()



if __name__ == "__main__":
    main()
