from __future__ import annotations

import json
from textwrap import dedent

RACE_KR = {
    "Protoss": "프로토스",
    "Terran": "테란",
    "Zerg": "저그",
    "Random": "랜덤",
    "Unknown": "미상",
}


SYSTEM_ANALYSIS_INSTRUCTIONS = dedent(
    """
    당신은 스타크래프트 II 코치입니다.
    리플레이 메타데이터와 참고 가이드를 바탕으로 다음을 한국어로 분석하세요.
    1. 경기 요약
    2. 승패 핵심 이유
    3. 종족/매치업 관점 핵심 피드백 3개
    아래 정보가 있으면 반드시 적극 활용하세요: 유닛 조합, 시그니처 유닛, 일꾼 수 증감, 자원 효율, 전투 스윙(몇 분 교전에서 누가 이득을 봤는지), 시그니처 전환(예: 뮤탈, 땅굴망, 거신, 의료선, 우주관문/로공/군수공장 계열 핵심 타이밍).
    context에 guide_file_paths가 있으면 파일 도구로 해당 파일들을 먼저 읽고, 현재 매치업과 관련된 섹션을 우선 반영하세요.
    guide는 통째로 인용하지 말고, 복기 판단과 피드백 문장에 필요한 부분만 압축 활용하세요.
    focus_player가 있으면 그 플레이어 관점에서만 리뷰하세요.
    특히 그 플레이어의 빌드오더, 테크 전환, 유닛구성, 타이밍 선택이 상대 조합/테크에 비해 적절했는지에 집중하세요.
    다른 플레이어를 위한 조언이나 상대 입장에서의 조언은 하지 말고, 오직 focus_player에게 실제 도움이 되는 복기만 제공하세요.
    focus_player가 없으면 지금처럼 경기 전반 리뷰를 하세요.
    출력은 반드시 아래 섹션 제목을 그대로 사용하세요.
    - 경기 요약
    - 승패 핵심 이유
    - 핵심 피드백 3개
    체크리스트형 과제는 출력하지 마세요.
    불확실한 내용은 추정이라고 명시하세요.
    """
).strip()


def build_analysis_prompt(replay_facts: dict, guide_context: str = "", focus_player: dict | None = None) -> str:
    payload = json.dumps(replay_facts, ensure_ascii=False, indent=2)
    pieces = [SYSTEM_ANALYSIS_INSTRUCTIONS]
    if guide_context:
        pieces.append(guide_context)
    if focus_player:
        focus_payload = json.dumps(focus_player, ensure_ascii=False, indent=2)
        focus_name = focus_player.get("name", "Unknown")
        focus_race = RACE_KR.get(str(focus_player.get("race", "Unknown")), str(focus_player.get("race", "Unknown")))
        pieces.append(f"FOCUS_PLAYER\n이 리플레이는 {focus_name}({focus_race}) 관점에서만 리뷰하세요.")
        pieces.append(f"FOCUS_PLAYER_JSON\n{focus_payload}")
    pieces.append(f"REPLAY_FACTS_JSON\n{payload}")
    return "\n\n".join(pieces)


def build_analysis_context(
    replay_facts: dict,
    guide_context: str = "",
    guide_file_paths: list[str] | None = None,
    focus_player: dict | None = None,
) -> dict:
    return {
        "guide_context": guide_context,
        "guide_file_paths": guide_file_paths or [],
        "focus_player": focus_player,
        "replay_facts": replay_facts,
    }
