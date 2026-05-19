from __future__ import annotations

from collections import Counter
from typing import Any

RACE_KR = {
    "Protoss": "프로토스",
    "Terran": "테란",
    "Zerg": "저그",
    "Random": "랜덤",
    "Unknown": "미상",
}

MATCHUP_KR = {
    "PvT": "프테전",
    "PvZ": "프저전",
    "PvP": "프프전",
    "TvP": "테프전",
    "TvZ": "테저전",
    "TvT": "테테전",
    "ZvP": "저프전",
    "ZvT": "저테전",
    "ZvZ": "저저전",
}

IMPORTANT_UPGRADES = {
    "BlinkTech",
    "Charge",
    "PsiStormTech",
    "ProtossGroundWeaponsLevel1",
    "ProtossGroundArmorsLevel1",
    "ProtossGroundWeaponsLevel2",
    "ProtossGroundArmorsLevel2",
    "Stimpack",
    "ShieldWall",
    "PunisherGrenades",
    "TerranInfantryWeaponsLevel1",
    "TerranInfantryArmorsLevel1",
    "TerranInfantryWeaponsLevel2",
    "TerranInfantryArmorsLevel2",
    "TerranInfantryWeaponsLevel3",
    "TerranInfantryArmorsLevel3",
    "ZerglingMovementSpeed",
    "BanelingSpeed",
    "OverlordSpeed",
    "GlialReconstitution",
    "CentrifugalHooks",
}

IMPORTANT_TECH = {
    "RoboticsFacility",
    "TemplarArchive",
    "WarpPrism",
    "Phoenix",
    "Observer",
    "Colossus",
    "Stargate",
    "GhostAcademy",
    "Ghost",
    "SiegeTankSieged",
    "WidowMine",
    "Medivac",
    "LiberatorAG",
    "Factory",
    "Starport",
    "RoachWarren",
    "BanelingNest",
    "Lair",
    "HydraliskDen",
    "LurkerDenMP",
    "SporeCrawler",
    "SpineCrawler",
}

TERM_KR = {
    "BlinkTech": "점멸",
    "Charge": "돌진",
    "PsiStormTech": "사이오닉 폭풍",
    "ProtossGroundWeaponsLevel1": "지상 공업 1단계",
    "ProtossGroundArmorsLevel1": "지상 방업 1단계",
    "ProtossGroundWeaponsLevel2": "지상 공업 2단계",
    "ProtossGroundArmorsLevel2": "지상 방업 2단계",
    "Stimpack": "자극제",
    "ShieldWall": "전투방패",
    "PunisherGrenades": "충격탄",
    "TerranInfantryWeaponsLevel1": "보병 공업 1단계",
    "TerranInfantryArmorsLevel1": "보병 방업 1단계",
    "TerranInfantryWeaponsLevel2": "보병 공업 2단계",
    "TerranInfantryArmorsLevel2": "보병 방업 2단계",
    "TerranInfantryWeaponsLevel3": "보병 공업 3단계",
    "TerranInfantryArmorsLevel3": "보병 방업 3단계",
    "ZerglingMovementSpeed": "저글링 발업",
    "BanelingSpeed": "맹독충 속업",
    "OverlordSpeed": "대군주 속업",
    "GlialReconstitution": "바퀴 속업",
    "CentrifugalHooks": "맹독충 갈고리",
    "RoboticsFacility": "로봇공학 시설",
    "TemplarArchive": "기사단 기록보관소",
    "WarpPrism": "분광기",
    "Phoenix": "불사조",
    "Observer": "관측선",
    "Colossus": "거신",
    "Stargate": "우주관문",
    "GhostAcademy": "유령 사관학교",
    "Ghost": "유령",
    "SiegeTankSieged": "공성전차",
    "WidowMine": "지뢰",
    "Medivac": "의료선",
    "LiberatorAG": "해방선",
    "Factory": "군수공장",
    "Starport": "우주공항",
    "RoachWarren": "바퀴 소굴",
    "BanelingNest": "맹독충 둥지",
    "Lair": "번식지",
    "HydraliskDen": "히드라리스크 굴",
    "LurkerDenMP": "가시지옥 굴",
    "SporeCrawler": "포자 촉수",
    "SpineCrawler": "가시 촉수",
}


def extract_summary_metrics(replay: Any) -> dict[str, Any]:
    players = list(getattr(replay, "players", []) or [])
    if not players:
        return {}

    tracker_events = list(getattr(replay, "tracker_events", []) or [])
    summary: dict[str, Any] = {"economy": {}, "upgrades": {}, "tech": {}, "army": {}}

    for player in players:
        stats = [
            event
            for event in tracker_events
            if type(event).__name__ == "PlayerStatsEvent" and getattr(event, "pid", None) == getattr(player, "pid", None)
        ]
        if stats:
            final = stats[-1]
            summary["economy"][player.name] = {
                "race": player.play_race,
                "workers_max": max(getattr(event, "workers_active_count", 0) for event in stats),
                "resources_lost": getattr(final, "resources_lost", 0),
                "resources_killed": getattr(final, "resources_killed", 0),
                "food_used_final": getattr(final, "food_used", 0),
                "food_made_final": getattr(final, "food_made", 0),
            }

        upgrades: list[str] = []
        seen_upgrades: set[str] = set()
        tech_events: list[str] = []
        seen_tech: set[str] = set()

        for event in tracker_events:
            event_type = type(event).__name__
            if event_type == "UpgradeCompleteEvent" and getattr(event, "player", None) == player:
                name = getattr(event, "upgrade_type_name", "")
                if name in IMPORTANT_UPGRADES and name not in seen_upgrades:
                    upgrades.append(f"{_format_time(getattr(event, 'second', 0))} {_localize_term(name)}")
                    seen_upgrades.add(name)
            elif event_type in {"UnitDoneEvent", "UnitBornEvent"}:
                unit = getattr(event, "unit", None)
                if getattr(unit, "owner", None) != player:
                    continue
                name = getattr(unit, "name", "")
                if name in IMPORTANT_TECH and name not in seen_tech:
                    tech_events.append(f"{_format_time(getattr(event, 'second', 0))} {_localize_term(name)}")
                    seen_tech.add(name)

        summary["upgrades"][player.name] = upgrades[:6]
        summary["tech"][player.name] = tech_events[:6]

        built = Counter(
            _localize_term(getattr(unit, "name", ""))
            for unit in getattr(player, "units", [])
            if getattr(unit, "name", "")
        )
        summary["army"][player.name] = built.most_common(8)

    return summary


def build_manual_analysis(replay_facts: dict[str, Any], guide_context: str = "") -> str:
    players = replay_facts.get("players", [])
    winner = replay_facts.get("winner", "Unknown")
    matchup = replay_facts.get("matchup", "Unknown")
    map_name = replay_facts.get("map_name", "Unknown")
    game_length = replay_facts.get("game_length", "Unknown")
    matchup_kr = _localize_matchup(matchup)
    summary_metrics = replay_facts.get("summary_metrics", {}) or {}
    economy = summary_metrics.get("economy", {}) or {}
    upgrades = summary_metrics.get("upgrades", {}) or {}
    tech = summary_metrics.get("tech", {}) or {}

    winner_player = next((player for player in players if player.get("name") == winner), players[0] if players else {})
    loser_player = next((player for player in players if player.get("name") != winner), players[-1] if players else {})
    winner_name = winner_player.get("name", winner)
    loser_name = loser_player.get("name", "상대")
    winner_race_kr = _race_kr(winner_player.get("race"))
    loser_race_kr = _race_kr(loser_player.get("race"))

    winner_metrics = _metrics_for_player(economy, winner_player)
    loser_metrics = _metrics_for_player(economy, loser_player)
    winner_upgrades = _events_for_player(upgrades, winner_player)
    loser_upgrades = _events_for_player(upgrades, loser_player)
    winner_tech = _events_for_player(tech, winner_player)
    loser_tech = _events_for_player(tech, loser_player)

    summary_lines = [
        f"- {map_name}에서 열린 {matchup_kr} 경기이며, 총 {game_length} 만에 {winner_name}({winner_race_kr})가 승리했습니다.",
    ]
    if winner_metrics and loser_metrics:
        summary_lines.append(
            f"- 자원 교환비는 {winner_name} 쪽이 더 좋았습니다. {winner_name}은 자원 피해 {winner_metrics.get('resources_killed', 0)}, 자원 손실 {winner_metrics.get('resources_lost', 0)}였고, {loser_name}은 자원 피해 {loser_metrics.get('resources_killed', 0)}, 자원 손실 {loser_metrics.get('resources_lost', 0)}였습니다."
        )
        if loser_metrics.get("workers_max", 0) >= winner_metrics.get("workers_max", 0):
            summary_lines.append(
                f"- 다만 {loser_name}가 일꾼 최대치 {loser_metrics.get('workers_max', 0)}로 더 크게 짼 구간이 있어, 운영 기반 자체는 나쁘지 않았던 경기로 보입니다."
            )
    if loser_upgrades:
        summary_lines.append(f"- 패배한 쪽 핵심 업그레이드는 {', '.join(loser_upgrades[:3])} 순으로 확인됩니다.")
    if winner_upgrades:
        summary_lines.append(f"- 승리한 쪽 핵심 업그레이드는 {', '.join(winner_upgrades[:3])} 순으로 확인됩니다.")

    reasons: list[str] = []
    if winner_metrics and loser_metrics:
        reasons.append(
            f"- 가장 큰 차이는 교환 효율이었습니다. {winner_name}은 손실보다 피해를 크게 앞세운 반면, {loser_name}은 잘 큰 구간 이후 교환이 비싸게 일어났습니다."
        )
    if loser_tech:
        reasons.append(
            f"- {loser_name}의 체제 연결은 {', '.join(loser_tech[:3])} 흐름이었는데, 이 중 보조 테크가 늦어진 구간이 교전 완성도를 떨어뜨렸을 가능성이 큽니다."
        )
    if winner_tech or winner_upgrades:
        reasons.append(
            f"- {winner_name}은 {', '.join((winner_tech + winner_upgrades)[:4])}처럼 핵심 전투 수단을 먼저 갖추며 교전 설계를 더 쉽게 했습니다."
        )

    feedback = _matchup_feedback_bundle(
        matchup=matchup,
        loser_name=loser_name,
        loser_race_kr=loser_race_kr,
        winner_name=winner_name,
        winner_race_kr=winner_race_kr,
        loser_upgrades=loser_upgrades,
        loser_tech=loser_tech,
        winner_metrics=winner_metrics,
        loser_metrics=loser_metrics,
        guide_context=guide_context,
    )

    checklist = _checklist_bundle(
        matchup=matchup,
        loser_metrics=loser_metrics,
        loser_upgrades=loser_upgrades,
        loser_tech=loser_tech,
    )

    sections = [
        "경기 요약",
        *summary_lines,
        "",
        "승패 핵심 이유",
        *(reasons or ["- 메타데이터와 추적 이벤트 기준으로만 판단했으므로 세부 교전 해석은 제한적입니다."]),
        "",
        "핵심 피드백 3개",
        *feedback,
        "",
        "바로 연습할 체크리스트 3개",
        *checklist,
    ]
    return "\n".join(sections)


def _matchup_feedback_bundle(
    matchup: str,
    loser_name: str,
    loser_race_kr: str,
    winner_name: str,
    winner_race_kr: str,
    loser_upgrades: list[str],
    loser_tech: list[str],
    winner_metrics: dict[str, Any],
    loser_metrics: dict[str, Any],
    guide_context: str,
) -> list[str]:
    if matchup == "PvT":
        first = "- PvT 가이드 기준으로 점멸 이후 관측선·거신·분광기 같은 보조 체제를 늦추지 않는 것이 중요합니다. 이번 경기도 점멸-고위기사는 갖췄지만 로봇공학 시설 연결이 늦어 한타 마무리 수단이 부족해졌을 가능성이 큽니다."
        second = f"- {loser_name} 입장에서는 {', '.join((loser_upgrades + loser_tech)[:4]) or '주요 타이밍'} 이후에 무엇을 바로 붙였는지가 중요했습니다. 업그레이드가 좋아도 관측선/분광기/거신 같은 후속 수단이 비면 교전 효율이 급격히 떨어집니다."
        third = _economy_feedback_line(loser_name, loser_metrics, winner_name, winner_metrics)
        return [first, second, third]
    if matchup == "ZvT":
        first = "- 저테전에서는 4~5분 정찰 확정, 점막 연결, 여왕 위치가 핵심입니다. 저글링·맹독충 단계에서 드랍 경로와 테란의 첫 타이밍을 얼마나 빨리 읽었는지가 경기 흐름을 크게 좌우합니다."
        second = f"- {loser_name} 입장에서는 {', '.join((loser_upgrades + loser_tech)[:4]) or '핵심 타이밍'} 이후의 병력 전환이 더 중요했습니다. 저글링 발업이나 맹독충 둥지 타이밍이 보여도 점막·여왕·후속 라인 연결이 비면 교환비가 쉽게 무너집니다."
        third = _economy_feedback_line(loser_name, loser_metrics, winner_name, winner_metrics, prefer_phrase="잘 짼 뒤 교환을 비싸게 한 경기")
        return [first, second, third]
    if matchup == "TvZ":
        first = "- 테저전에서는 사신 정찰 뒤 화염차/바이킹으로 점막과 3베이스를 늦추는 흐름이 중요합니다. 테란이 이 루프를 놓치면 저그의 드론 최적화와 테크 전환을 너무 편하게 허용하게 됩니다."
        second = f"- {loser_name} 입장에서는 {', '.join((loser_upgrades + loser_tech)[:4]) or '핵심 타이밍'} 이후의 진출 타이밍이 어긋났을 수 있습니다. 자극제·의료선·공성전차 같은 스파이크를 한 번에 묶어야 압박 가치가 큽니다."
        third = _economy_feedback_line(loser_name, loser_metrics, winner_name, winner_metrics)
        return [first, second, third]
    if matchup == "PvZ":
        first = "- 프저전에서는 우주관문 정찰 이후 트리플 판단과 방어 타워 선행 여부가 핵심입니다. 저그의 3부화장 타이밍과 병력 쥐어짜기를 놓치면 멀티 욕심이 바로 약점이 됩니다."
        second = f"- {loser_name} 입장에서는 {', '.join((loser_upgrades + loser_tech)[:4]) or '핵심 타이밍'} 이후에 관문 수와 로보/고위기사 연결이 충분했는지 다시 볼 필요가 있습니다."
        third = _economy_feedback_line(loser_name, loser_metrics, winner_name, winner_metrics)
        return [first, second, third]
    if matchup == "ZvP":
        first = "- 저프전에서는 우관·황혼·로공·3넥 타이밍 판별이 핵심입니다. 프로토스가 2베이스 가스를 많이 먹고 3넥이 늦으면 저그는 드론 중단과 병력 전환 타이밍을 분명히 잡아야 합니다."
        second = f"- {loser_name} 입장에서는 {', '.join((loser_upgrades + loser_tech)[:4]) or '핵심 타이밍'} 뒤에 여왕·포자촉수·바퀴/맹독충 전환이 충분했는지 복기해보면 좋습니다."
        third = _economy_feedback_line(loser_name, loser_metrics, winner_name, winner_metrics)
        return [first, second, third]
    return [
        f"- {MATCHUP_KR.get(matchup, matchup)}에서는 핵심 테크 타이밍과 정찰 정보 갱신을 같은 템포로 맞추는 것이 우선입니다.",
        f"- {loser_name} 입장에서는 {', '.join((loser_upgrades + loser_tech)[:4]) or '핵심 타이밍'} 이후의 후속 연결을 더 촘촘하게 설계할 필요가 있습니다.",
        _economy_feedback_line(loser_name, loser_metrics, winner_name, winner_metrics),
    ]


def _economy_feedback_line(
    loser_name: str,
    loser_metrics: dict[str, Any],
    winner_name: str,
    winner_metrics: dict[str, Any],
    prefer_phrase: str | None = None,
) -> str:
    if winner_metrics and loser_metrics and loser_metrics.get("workers_max", 0) >= winner_metrics.get("workers_max", 0):
        phrase = prefer_phrase or "잘 큰 뒤 교환을 비싸게 한 경기"
        return f"- {loser_name}는 경제 최대치 자체는 뒤지지 않았습니다. 그래서 이번 경기는 '못 큰 경기'라기보다 '{phrase}'에 더 가깝습니다."
    return f"- {winner_name} 쪽이 경제와 교전 전환을 더 매끄럽게 했습니다. 다음 복기에서는 일꾼 최대치와 자원 손실 비율을 같이 보는 습관을 들이면 좋습니다."


def _checklist_bundle(matchup: str, loser_metrics: dict[str, Any], loser_upgrades: list[str], loser_tech: list[str]) -> list[str]:
    if matchup == "PvT":
        first = "- 다음 프테전 리플레이 3개를 골라 점멸 완료 시점, 로봇공학 시설 완성 시점, 첫 관측선/분광기 시점을 따로 적어보세요."
    elif matchup == "ZvT":
        first = "- 다음 저테전 리플레이 3개를 골라 4~5분 정찰 결과, 점막 연결 상태, 여왕 위치를 한 줄씩 메모해보세요."
    elif matchup == "TvZ":
        first = "- 다음 테저전 리플레이 3개를 골라 사신 정찰, 화염차 첫 출발, 3사령부 타이밍을 나란히 적어보세요."
    else:
        first = "- 같은 매치업 리플레이 3개를 다시 보며 첫 정찰 정보와 첫 핵심 테크 완성 시점을 메모해보세요."

    joined = ", ".join((loser_upgrades + loser_tech)[:3])
    second = (
        f"- 이번 경기 기준 핵심 타이밍({joined}) 이후에 무엇을 바로 붙였는지 체크해서, 업그레이드-유닛-확장 연결이 끊긴 지점을 찾으세요."
        if joined
        else "- 핵심 업그레이드가 눌린 직후 어떤 생산 건물과 유닛을 붙였는지 추적해보세요."
    )

    workers = loser_metrics.get("workers_max")
    third = (
        f"- 일꾼 최대치 {workers}를 찍은 뒤 자원 손실이 커졌다면, 그 구간 전후의 교전 위치와 보조 유닛 구성을 다시 확인하세요."
        if workers
        else "- 교전 직전 자원 은행과 일꾼 수를 함께 보면서 '잘 큰 뒤 왜 못 이겼는지'를 복기해보세요."
    )
    return [first, second, third]


def _metrics_for_player(metrics: dict[str, Any], player: dict[str, Any]) -> dict[str, Any]:
    for key in filter(None, [player.get("name"), player.get("race")]):
        if key in metrics:
            return metrics[key]
    return {}


def _events_for_player(events: dict[str, list[str]], player: dict[str, Any]) -> list[str]:
    for key in filter(None, [player.get("name"), player.get("race")]):
        if key in events:
            return [_localize_event_text(event) for event in events[key]]
    return []


def _localize_event_text(event_text: str) -> str:
    localized = str(event_text)
    for raw, kr in TERM_KR.items():
        localized = localized.replace(raw, kr)
    return localized


def _format_time(seconds: int) -> str:
    minutes, remain = divmod(int(seconds), 60)
    return f"{minutes}:{remain:02d}"


def _localize_term(name: str) -> str:
    return TERM_KR.get(name, name)


def _localize_matchup(matchup: str) -> str:
    return MATCHUP_KR.get(matchup, matchup)


def _race_kr(race: str | None) -> str:
    return RACE_KR.get(race or "Unknown", race or "미상")
