from __future__ import annotations

import requests


class LLMClient:
    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def analyze(self, prompt: str) -> str:
        if not self.api_key:
            return _fallback_analysis(prompt)

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()


def _fallback_analysis(prompt: str) -> str:
    lines = [
        "경기 요약",
        "- LLM API 키가 설정되지 않아 로컬 휴리스틱 요약 모드로 동작했습니다.",
        "승패 핵심 이유",
        "- 리플레이 메타데이터 기반 기본 리포트만 생성했습니다.",
        "핵심 피드백 3개",
        "- 실제 전략 피드백을 원하면 LLM_API_KEY와 LLM_MODEL을 설정하세요.",
        "- guides 문서를 prompt context로 함께 넣도록 이미 연결되어 있습니다.",
        "- sc2reader 메타데이터 외 행동 로그 분석은 후속 확장 포인트입니다.",
        "바로 연습할 체크리스트 3개",
        "- 새 리플레이가 감지되는지 먼저 자동화 루프를 검증하세요.",
        "- Slack webhook과 LLM 응답을 분리해서 점검하세요.",
        "- 필요하면 플레이어별 세부 이벤트 분석을 추가하세요.",
    ]
    return "\n".join(lines)
