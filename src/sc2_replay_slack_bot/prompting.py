from __future__ import annotations

import json
from textwrap import dedent


SYSTEM_ANALYSIS_INSTRUCTIONS = dedent(
    """
    당신은 스타크래프트 II 코치입니다.
    리플레이 메타데이터와 참고 가이드를 바탕으로 다음을 한국어로 분석하세요.
    1. 경기 요약
    2. 승패 핵심 이유
    3. 종족/매치업 관점 핵심 피드백 3개
    4. 바로 연습할 체크리스트 3개
    불확실한 내용은 추정이라고 명시하세요.
    """
).strip()


def build_analysis_prompt(replay_facts: dict, guide_context: str = "") -> str:
    payload = json.dumps(replay_facts, ensure_ascii=False, indent=2)
    pieces = [SYSTEM_ANALYSIS_INSTRUCTIONS]
    if guide_context:
        pieces.append(guide_context)
    pieces.append(f"REPLAY_FACTS_JSON\n{payload}")
    return "\n\n".join(pieces)
