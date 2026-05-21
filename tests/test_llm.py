from sc2_replay_slack_bot.llm import LLMClient


class DummyResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def test_llm_client_calls_hermes_ask_api_and_returns_answer(monkeypatch) -> None:
    captured: dict = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return DummyResponse({"status": "completed", "answer": "경기 요약\n- Hermes 분석 결과"})

    monkeypatch.setattr("sc2_replay_slack_bot.llm.requests.post", fake_post)

    client = LLMClient(api_key="", base_url="http://127.0.0.1:8787", model="hermes")
    answer = client.analyze(
        prompt="분석 지침",
        context={"replay_facts": {"map_name": "Abyssal Reef"}, "guide_context": "Guide summary"},
    )

    assert answer == "경기 요약\n- Hermes 분석 결과"
    assert captured["url"] == "http://127.0.0.1:8787/ask"
    assert captured["headers"]["Content-Type"] == "application/json"
    assert captured["json"]["prompt"] == "분석 지침"
    assert captured["json"]["context"]["replay_facts"]["map_name"] == "Abyssal Reef"
    assert captured["json"]["context"]["guide_context"] == "Guide summary"
    assert captured["json"]["options"]["timeout_sec"] == 120
    assert captured["timeout"] == 120
