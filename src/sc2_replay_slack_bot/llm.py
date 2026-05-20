from __future__ import annotations

from typing import Any

import requests


class LLMClient:
    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def analyze(self, prompt: str, context: dict[str, Any] | None = None) -> str:
        response = requests.post(
            _ask_url(self.base_url),
            headers={
                "Content-Type": "application/json",
            },
            json={
                "prompt": prompt,
                "context": context or {},
                "options": {"timeout_sec": 60},
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        answer = (data.get("answer") or "").strip()
        if not answer:
            raise ValueError(f"Hermes ask API returned empty answer: {data}")
        return answer


def _ask_url(base_url: str) -> str:
    if base_url.endswith("/ask"):
        return base_url
    return f"{base_url}/ask"
