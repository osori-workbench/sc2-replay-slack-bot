from __future__ import annotations

from collections import Counter
from typing import Any

IMPORTANT_UPGRADES = {
    "BlinkTech",
    "Charge",
    "PsiStormTech",
    "Stimpack",
    "ShieldWall",
    "PunisherGrenades",
    "TerranInfantryWeaponsLevel1",
    "TerranInfantryArmorsLevel1",
    "TerranInfantryWeaponsLevel2",
    "TerranInfantryArmorsLevel2",
    "TerranInfantryWeaponsLevel3",
    "TerranInfantryArmorsLevel3",
    "ProtossGroundWeaponsLevel1",
    "ProtossGroundArmorsLevel1",
    "ProtossGroundWeaponsLevel2",
    "ProtossGroundArmorsLevel2",
}

IMPORTANT_TECH = {
    "RoboticsFacility",
    "TemplarArchive",
    "WarpPrism",
    "Phoenix",
    "Observer",
    "Colossus",
    "GhostAcademy",
    "Ghost",
    "SiegeTankSieged",
    "WidowMine",
    "Medivac",
    "LiberatorAG",
    "Factory",
    "Starport",
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
                    upgrades.append(f"{_format_time(getattr(event, 'second', 0))} {name}")
                    seen_upgrades.add(name)
            elif event_type in {"UnitDoneEvent", "UnitBornEvent"}:
                unit = getattr(event, "unit", None)
                if getattr(unit, "owner", None) != player:
                    continue
                name = getattr(unit, "name", "")
                if name in IMPORTANT_TECH and name not in seen_tech:
                    tech_events.append(f"{_format_time(getattr(event, 'second', 0))} {name}")
                    seen_tech.add(name)

        summary["upgrades"][player.name] = upgrades[:6]
        summary["tech"][player.name] = tech_events[:6]

        built = Counter(
            getattr(unit, "name", "")
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
    summary_metrics = replay_facts.get("summary_metrics", {}) or {}
    economy = summary_metrics.get("economy", {}) or {}
    upgrades = summary_metrics.get("upgrades", {}) or {}
    tech = summary_metrics.get("tech", {}) or {}

    winner_player = next((player for player in players if player.get("name") == winner), players[0] if players else {})
    loser_player = next((player for player in players if player.get("name") != winner), players[-1] if players else {})

    winner_metrics = _metrics_for_player(economy, winner_player)
    loser_metrics = _metrics_for_player(economy, loser_player)
    winner_upgrades = _events_for_player(upgrades, winner_player)
    loser_upgrades = _events_for_player(upgrades, loser_player)
    winner_tech = _events_for_player(tech, winner_player)
    loser_tech = _events_for_player(tech, loser_player)

    summary_lines = [
        f"- {map_name}에서 열린 {matchup} 경기이며, 총 {game_length} 만에 {winner}가 승리했습니다.",
    ]
    if winner_metrics and loser_metrics:
        summary_lines.append(
            "- 최종 자원 교환은 "
            f"{winner} 쪽이 killed {winner_metrics.get('resources_killed', 0)} / lost {winner_metrics.get('resources_lost', 0)}로, "
            f"{loser_player.get('name', '상대')}의 killed {loser_metrics.get('resources_killed', 0)} / lost {loser_metrics.get('resources_lost', 0)}보다 효율이 좋았습니다."
        )
        if loser_metrics.get("workers_max", 0) > winner_metrics.get("workers_max", 0):
            summary_lines.append(
                f"- 다만 {loser_player.get('name', '패자')}가 일꾼 최대치 {loser_metrics.get('workers_max', 0)}로 더 크게 짼 구간이 있어, 운영 기반은 나쁘지 않았던 경기로 보입니다."
            )
    if loser_upgrades:
        summary_lines.append(f"- 패자 쪽 핵심 업그레이드는 {', '.join(loser_upgrades[:3])} 순으로 확인됩니다.")
    if winner_upgrades:
        summary_lines.append(f"- 승자 쪽 핵심 업그레이드는 {', '.join(winner_upgrades[:3])} 순으로 확인됩니다.")

    reasons = []
    if winner_metrics and loser_metrics:
        reasons.append(
            f"- 교환비가 {winner} 쪽으로 기울었습니다. 승자 최종 손익은 {winner_metrics.get('resources_killed', 0)} / {winner_metrics.get('resources_lost', 0)}였고, 패자는 {loser_metrics.get('resources_killed', 0)} / {loser_metrics.get('resources_lost', 0)}였습니다."
        )
    if loser_tech:
        reasons.append(f"- 패자 체제 연결은 {', '.join(loser_tech[:3])} 흐름이었는데, 보조 테크 완성 타이밍이 교전 전환 속도를 제한했을 가능성이 큽니다.")
    if winner_tech or winner_upgrades:
        reasons.append(
            f"- 승자는 {', '.join((winner_tech + winner_upgrades)[:4])}처럼 핵심 전투 수단을 먼저 갖추며 교전 설계를 더 쉽게 했습니다."
        )

    feedback = [
        _matchup_feedback(matchup, guide_context),
        _timing_feedback(loser_player, loser_upgrades, loser_tech),
        _economy_feedback(winner, loser_player, winner_metrics, loser_metrics),
    ]

    checklist = [
        _checklist_item_for_matchup(matchup),
        _checklist_item_for_timings(loser_upgrades, loser_tech),
        _checklist_item_for_economy(loser_metrics),
    ]

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


def _metrics_for_player(metrics: dict[str, Any], player: dict[str, Any]) -> dict[str, Any]:
    for key in filter(None, [player.get("name"), player.get("race")]):
        if key in metrics:
            return metrics[key]
    return {}


def _events_for_player(events: dict[str, list[str]], player: dict[str, Any]) -> list[str]:
    for key in filter(None, [player.get("name"), player.get("race")]):
        if key in events:
            return events[key]
    return []


def _format_time(seconds: int) -> str:
    minutes, remain = divmod(int(seconds), 60)
    return f"{minutes}:{remain:02d}"


def _matchup_feedback(matchup: str, guide_context: str) -> str:
    if matchup == "PvT":
        if "관측선" in guide_context or "거신" in guide_context:
            return "- PvT 가이드 기준으로 점멸 이후 관측선/거신 같은 보조 체제를 늦추지 않는 것이 중요합니다. 이번 경기도 주력 업그레이드 뒤 보조 테크 연결 속도가 승패에 큰 영향을 준 것으로 보입니다."
        return "- PvT에서는 점멸 타이밍만큼이나 관측/로보 보조 체제를 같이 붙여 교전 설계를 안정화하는 연습이 필요합니다."
    if matchup == "ZvT":
        return "- ZvT에서는 4~5분 정찰 확정과 점막/여왕 위치가 핵심입니다. 분석 결과도 정찰-대응 전환 속도를 중심으로 다시 볼 가치가 있습니다."
    if matchup == "TvZ":
        return "- TvZ에서는 화염차/바이킹으로 저그 확장을 늦추고 3사령부를 안정화하는 루틴을 반복 연습하는 것이 좋습니다."
    return "- 이 매치업은 핵심 테크 타이밍과 정찰 정보 업데이트를 함께 맞추는 연습이 우선입니다."


def _timing_feedback(loser_player: dict[str, Any], upgrades: list[str], tech: list[str]) -> str:
    name = loser_player.get("name", "패자")
    timing_bits = ", ".join((upgrades + tech)[:4]) or "핵심 타이밍 정보"
    return f"- {name} 입장에서는 {timing_bits} 이후의 후속 연결이 더 중요했습니다. 업그레이드가 좋아도 후속 유닛/보조 테크가 늦으면 교전 효율이 급격히 떨어질 수 있습니다."


def _economy_feedback(winner: str, loser_player: dict[str, Any], winner_metrics: dict[str, Any], loser_metrics: dict[str, Any]) -> str:
    if winner_metrics and loser_metrics and loser_metrics.get("workers_max", 0) >= winner_metrics.get("workers_max", 0):
        return f"- {loser_player.get('name', '패자')}는 경제 최대치는 뒤지지 않았습니다. 그래서 문제는 '못 큰 경기'라기보다 '잘 큰 뒤 교환을 비싸게 한 경기'에 가깝습니다."
    return f"- {winner} 쪽이 경제/교전 전환을 더 매끄럽게 했습니다. 다음 분석에서도 일꾼 최대치와 손실 자원 비율을 같이 보며 판단하는 습관을 추천합니다."


def _checklist_item_for_matchup(matchup: str) -> str:
    if matchup == "PvT":
        return "- 다음 PvT 리플레이 3개를 골라 점멸 완료 시점, 로보 완성 시점, 첫 관측/프리즘 시점을 따로 적어보세요."
    return "- 같은 매치업 리플레이 3개를 다시 보며 첫 정찰 정보와 첫 핵심 테크 완성 시점을 메모해보세요."


def _checklist_item_for_timings(upgrades: list[str], tech: list[str]) -> str:
    joined = ", ".join((upgrades + tech)[:3])
    if joined:
        return f"- 이번 경기 기준 핵심 타이밍({joined}) 이후에 무엇을 바로 붙였는지 체크해서, 업그레이드-유닛-확장 연결이 끊긴 지점을 찾으세요."
    return "- 핵심 업그레이드가 눌린 직후 어떤 생산 건물/유닛을 붙였는지 추적해보세요."


def _checklist_item_for_economy(metrics: dict[str, Any]) -> str:
    workers = metrics.get("workers_max")
    if workers:
        return f"- 일꾼 최대치 {workers}를 찍은 뒤 자원 손실이 커졌다면, 그 구간 전후의 교전 위치와 보조 유닛 구성을 다시 확인하세요."
    return "- 교전 직전 자원 은행과 일꾼 수를 함께 보면서 '잘 큰 뒤 왜 못 이겼는지'를 복기해보세요."
