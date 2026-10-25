from types import SimpleNamespace

import pytest

import review


class FakeClient:
    """Same call shape as the Groq client, no network."""

    def __init__(self, text="Great week."):
        self.text = text
        self.calls = 0
        self.prompts = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, model, messages):
        self.calls += 1
        self.prompts.append(messages[0]["content"])
        message = SimpleNamespace(content=self.text)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def test_second_call_uses_stored_review(conn):
    client = FakeClient()
    first = review.generate_review(conn, client, "2026-10-12")
    second = review.generate_review(conn, client, "2026-10-12")
    assert first == second == "Great week."
    assert client.calls == 1


def test_prompt_contains_computed_stats(conn):
    client = FakeClient()
    review.generate_review(conn, client, "2026-10-12")
    prompt = client.prompts[0]
    assert "legs: 1100" in prompt
    assert "-360" in prompt
    assert "Squat: 128.3" in prompt


def test_week_without_workouts_raises_and_makes_no_api_call(conn):
    client = FakeClient()
    with pytest.raises(review.ReviewError):
        review.generate_review(conn, client, "2026-01-05")
    assert client.calls == 0


def test_missing_key_raises(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    with pytest.raises(review.ReviewError):
        review.make_client()