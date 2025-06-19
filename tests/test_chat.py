from yowon import agent


class FakeAgent:
    def __init__(self):
        self.calls = []

    def run(self, prompt, reset=True, **kwargs):
        self.calls.append((prompt, reset))
        return f"echo:{prompt}-{reset}"


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
