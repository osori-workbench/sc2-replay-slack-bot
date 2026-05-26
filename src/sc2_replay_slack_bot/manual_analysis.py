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
    # Protoss
    "WarpGateResearch",
    "BlinkTech",
    "Charge",
    "PsiStormTech",
    "AdeptPiercingAttack",
    "ExtendedThermalLance",
    "ProtossGroundWeaponsLevel1",
    "ProtossGroundArmorsLevel1",
    "ProtossGroundWeaponsLevel2",
    "ProtossGroundArmorsLevel2",
    "ProtossGroundWeaponsLevel3",
    "ProtossGroundArmorsLevel3",
    "ProtossAirWeaponsLevel1",
    "ProtossAirWeaponsLevel2",
    "ProtossAirWeaponsLevel3",
    # Terran
    "Stimpack",
    "ShieldWall",
    "PunisherGrenades",
    "TerranInfantryWeaponsLevel1",
    "TerranInfantryArmorsLevel1",
    "TerranInfantryWeaponsLevel2",
    "TerranInfantryArmorsLevel2",
    "TerranInfantryWeaponsLevel3",
    "TerranInfantryArmorsLevel3",
    "InfernalPreigniter",
    "DrillingClaws",
    "BansheeCloak",
    "BattlecruiserEnableSpecializations",
    # Zerg
    "ZerglingMovementSpeed",
    "ZerglingAttackSpeed",
    "BanelingSpeed",
    "OverlordSpeed",
    "GlialReconstitution",
    "TunnelingClaws",
    "CentrifugalHooks",
    "Burrow",
    "MuscularAugments",
    "GroovedSpines",
}

IMPORTANT_TECH = {
    # Protoss structures / core tech
    "TwilightCouncil",
    "DarkShrine",
    "TemplarArchive",
    "RoboticsFacility",
    "RoboticsBay",
    "Stargate",
    "FleetBeacon",
    # Protoss signature units / deliveries
    "Observer",
    "WarpPrism",
    "Immortal",
    "Colossus",
    "Disruptor",
    "HighTemplar",
    "DarkTemplar",
    "Oracle",
    "Phoenix",
    "VoidRay",
    "Carrier",
    "Tempest",
    "Mothership",
    # Terran structures / core tech
    "Factory",
    "Starport",
    "FusionCore",
    "GhostAcademy",
    "Armory",
    # Terran signature units
    "Ghost",
    "SiegeTank",
    "SiegeTankSieged",
    "WidowMine",
    "Medivac",
    "Liberator",
    "LiberatorAG",
    "Banshee",
    "Raven",
    "VikingFighter",
    "Thor",
    "Battlecruiser",
    # Zerg structures / core tech
    "RoachWarren",
    "BanelingNest",
    "Lair",
    "Hive",
    "HydraliskDen",
    "LurkerDenMP",
    "InfestationPit",
    "Spire",
    "GreaterSpire",
    "UltraliskCavern",
    "NydusNetwork",
    # Zerg signature units / static defense
    "Mutalisk",
    "Corruptor",
    "BroodLord",
    "LurkerMP",
    "SwarmHostMP",
    "Ultralisk",
    "Viper",
    "Infestor",
    "NydusWorm",
    "Overseer",
    "SporeCrawler",
    "SpineCrawler",
}

SIGNATURE_TRANSITION_EVENTS = {
    "DarkShrine",
    "TemplarArchive",
    "RoboticsFacility",
    "RoboticsBay",
    "Stargate",
    "FleetBeacon",
    "WarpPrism",
    "Observer",
    "Immortal",
    "Colossus",
    "Disruptor",
    "HighTemplar",
    "DarkTemplar",
    "Oracle",
    "Phoenix",
    "VoidRay",
    "Carrier",
    "Tempest",
    "Mothership",
    "GhostAcademy",
    "FusionCore",
    "Ghost",
    "SiegeTank",
    "SiegeTankSieged",
    "WidowMine",
    "Medivac",
    "Liberator",
    "LiberatorAG",
    "Banshee",
    "Raven",
    "VikingFighter",
    "Thor",
    "Battlecruiser",
    "Hive",
    "HydraliskDen",
    "LurkerDenMP",
    "InfestationPit",
    "Spire",
    "GreaterSpire",
    "UltraliskCavern",
    "NydusNetwork",
    "Mutalisk",
    "Corruptor",
    "BroodLord",
    "LurkerMP",
    "SwarmHostMP",
    "Ultralisk",
    "Viper",
    "Infestor",
    "NydusWorm",
}

SIGNATURE_UNITS = {
    "HighTemplar",
    "DarkTemplar",
    "Immortal",
    "Colossus",
    "Disruptor",
    "Oracle",
    "Phoenix",
    "VoidRay",
    "Carrier",
    "Tempest",
    "Mothership",
    "Ghost",
    "SiegeTank",
    "SiegeTankSieged",
    "WidowMine",
    "Medivac",
    "Liberator",
    "LiberatorAG",
    "Banshee",
    "Raven",
    "VikingFighter",
    "Thor",
    "Battlecruiser",
    "Mutalisk",
    "Corruptor",
    "BroodLord",
    "LurkerMP",
    "SwarmHostMP",
    "Ultralisk",
    "Viper",
    "Infestor",
    "NydusWorm",
}

TERM_KR = {
    "Zealot": "광전사",
    "Stalker": "추적자",
    "Adept": "사도",
    "Sentry": "파수기",
    "HighTemplar": "고위 기사",
    "DarkTemplar": "암흑 기사",
    "Immortal": "불멸자",
    "Disruptor": "분열기",
    "Colossus": "거신",
    "Archon": "집정관",
    "Observer": "관측선",
    "WarpPrism": "분광기",
    "Oracle": "예언자",
    "Phoenix": "불사조",
    "VoidRay": "공허 포격기",
    "Carrier": "우주모함",
    "Tempest": "폭풍함",
    "Mothership": "모선",
    "Probe": "탐사정",
    "Marine": "해병",
    "Marauder": "불곰",
    "SCV": "건설로봇",
    "Ghost": "유령",
    "WidowMine": "지뢰",
    "WidowMineBurrowed": "지뢰",
    "SiegeTank": "공성전차",
    "SiegeTankSieged": "공성전차",
    "Medivac": "의료선",
    "Liberator": "해방선",
    "LiberatorAG": "해방선",
    "Banshee": "밴시",
    "Raven": "밤까마귀",
    "VikingFighter": "바이킹",
    "Thor": "토르",
    "Battlecruiser": "전투순양함",
    "Zergling": "저글링",
    "Baneling": "맹독충",
    "Roach": "바퀴",
    "Hydralisk": "히드라리스크",
    "Ravager": "궤멸충",
    "Mutalisk": "뮤탈리스크",
    "Corruptor": "타락귀",
    "BroodLord": "무리 군주",
    "LurkerMP": "가시지옥",
    "SwarmHostMP": "군단 숙주",
    "Ultralisk": "울트라리스크",
    "Viper": "살모사",
    "Infestor": "감염충",
    "Overseer": "감시군주",
    "NydusWorm": "땅굴벌레",
    "BlinkTech": "점멸",
    "Charge": "돌진",
    "PsiStormTech": "사이오닉 폭풍",
    "WarpGateResearch": "차원 관문 연구",
    "AdeptPiercingAttack": "공명파열포",
    "ExtendedThermalLance": "열 광선 사거리 업그레이드",
    "ProtossGroundWeaponsLevel1": "지상 공업 1단계",
    "ProtossGroundArmorsLevel1": "지상 방업 1단계",
    "ProtossGroundWeaponsLevel2": "지상 공업 2단계",
    "ProtossGroundArmorsLevel2": "지상 방업 2단계",
    "ProtossGroundWeaponsLevel3": "지상 공업 3단계",
    "ProtossGroundArmorsLevel3": "지상 방업 3단계",
    "ProtossAirWeaponsLevel1": "공중 공업 1단계",
    "ProtossAirWeaponsLevel2": "공중 공업 2단계",
    "ProtossAirWeaponsLevel3": "공중 공업 3단계",
    "Stimpack": "자극제",
    "ShieldWall": "전투방패",
    "PunisherGrenades": "충격탄",
    "TerranInfantryWeaponsLevel1": "보병 공업 1단계",
    "TerranInfantryArmorsLevel1": "보병 방업 1단계",
    "TerranInfantryWeaponsLevel2": "보병 공업 2단계",
    "TerranInfantryArmorsLevel2": "보병 방업 2단계",
    "TerranInfantryWeaponsLevel3": "보병 공업 3단계",
    "TerranInfantryArmorsLevel3": "보병 방업 3단계",
    "InfernalPreigniter": "화염차 파란불꽃",
    "DrillingClaws": "지뢰 잠복 발톱",
    "BansheeCloak": "밴시 은폐",
    "BattlecruiserEnableSpecializations": "전술 차원 도약",
    "ZerglingMovementSpeed": "저글링 발업",
    "ZerglingAttackSpeed": "아드레날린 분비선",
    "BanelingSpeed": "맹독충 속업",
    "OverlordSpeed": "대군주 속업",
    "GlialReconstitution": "바퀴 속업",
    "TunnelingClaws": "바퀴 잠복 이동",
    "CentrifugalHooks": "맹독충 갈고리",
    "Burrow": "잠복",
    "MuscularAugments": "히드라 속업",
    "GroovedSpines": "히드라 사거리 업그레이드",
    "TwilightCouncil": "황혼 의회",
    "DarkShrine": "암흑 성소",
    "RoboticsFacility": "로봇공학 시설",
    "RoboticsBay": "로봇공학 지원소",
    "TemplarArchive": "기사단 기록보관소",
    "Stargate": "우주관문",
    "FleetBeacon": "함대 신호소",
    "GhostAcademy": "유령 사관학교",
    "Factory": "군수공장",
    "Starport": "우주공항",
    "FusionCore": "융합로",
    "Armory": "무기고",
    "RoachWarren": "바퀴 소굴",
    "BanelingNest": "맹독충 둥지",
    "Lair": "번식지",
    "Hive": "군락",
    "HydraliskDen": "히드라리스크 굴",
    "LurkerDenMP": "가시지옥 굴",
    "InfestationPit": "감염 구덩이",
    "Spire": "둥지탑",
    "GreaterSpire": "거대 둥지탑",
    "UltraliskCavern": "울트라리스크 동굴",
    "NydusNetwork": "땅굴망",
    "SporeCrawler": "포자 촉수",
    "SpineCrawler": "가시 촉수",
}

CANONICAL_TERM_BY_LOWER = {
    name.lower(): name
    for name in IMPORTANT_UPGRADES | IMPORTANT_TECH | SIGNATURE_TRANSITION_EVENTS | SIGNATURE_UNITS | set(TERM_KR)
}


def extract_summary_metrics(replay: Any) -> dict[str, Any]:
    players = list(getattr(replay, "players", []) or [])
    if not players:
        return {}

    tracker_events = list(getattr(replay, "tracker_events", []) or [])
    speed_factor = _speed_factor(getattr(replay, "speed", None))
    summary: dict[str, Any] = {
        "economy": {},
        "upgrades": {},
        "tech": {},
        "army": {},
        "composition": {},
        "signature_units": {},
        "signature_transitions": {},
        "worker_trends": {},
        "combat_swings": [],
    }

    for player in players:
        stats = [
            event
            for event in tracker_events
            if type(event).__name__ == "PlayerStatsEvent" and getattr(event, "pid", None) == getattr(player, "pid", None)
        ]
        if stats:
            final = stats[-1]
            resources_lost = getattr(final, "resources_lost", 0)
            resources_killed = getattr(final, "resources_killed", 0)
            summary["economy"][player.name] = {
                "race": player.play_race,
                "workers_max": max(getattr(event, "workers_active_count", 0) for event in stats),
                "resources_lost": resources_lost,
                "resources_killed": resources_killed,
                "food_used_final": getattr(final, "food_used", 0),
                "food_made_final": getattr(final, "food_made", 0),
                "resource_efficiency_ratio": round(resources_killed / max(resources_lost, 1), 2),
            }
            summary["worker_trends"][player.name] = [
                {
                    "time": _format_time(_to_real_seconds(getattr(event, "second", 0), speed_factor)),
                    "workers": getattr(event, "workers_active_count", 0),
                    "resources_killed": getattr(event, "resources_killed", 0),
                    "resources_lost": getattr(event, "resources_lost", 0),
                }
                for event in stats[:8]
            ]

        upgrades: list[str] = []
        seen_upgrades: set[str] = set()
        tech_events: list[str] = []
        seen_tech: set[str] = set()
        signature_transitions: list[str] = []
        seen_signature_transitions: set[str] = set()

        for event in tracker_events:
            event_type = type(event).__name__
            if event_type == "UpgradeCompleteEvent" and getattr(event, "player", None) == player:
                raw_name = getattr(event, "upgrade_type_name", "")
                name = _canonical_term(raw_name)
                if name in IMPORTANT_UPGRADES and name not in seen_upgrades:
                    upgrades.append(f"{_format_time(_to_real_seconds(getattr(event, 'second', 0), speed_factor))} {_localize_term(name)}")
                    seen_upgrades.add(name)
            elif event_type in {"UnitInitEvent", "UnitDoneEvent", "UnitBornEvent"}:
                unit = getattr(event, "unit", None)
                if getattr(unit, "owner", None) != player:
                    continue
                name = getattr(unit, "name", "")
                real_seconds = _to_real_seconds(getattr(event, "second", 0), speed_factor)
                if real_seconds <= 0:
                    continue
                if name in IMPORTANT_TECH and name not in seen_tech:
                    tech_events.append(f"{_format_time(real_seconds)} {_localize_term(name)}")
                    seen_tech.add(name)
                if name in SIGNATURE_TRANSITION_EVENTS and name not in seen_signature_transitions:
                    signature_transitions.append(f"{_format_time(real_seconds)} {_localize_term(name)}")
                    seen_signature_transitions.add(name)

        summary["upgrades"][player.name] = upgrades[:8]
        summary["tech"][player.name] = tech_events[:8]
        summary["signature_transitions"][player.name] = signature_transitions[:8]

        built = Counter(
            _localize_term(getattr(unit, "name", ""))
            for unit in getattr(player, "units", [])
            if getattr(unit, "name", "")
        )
        top_units = built.most_common(8)
        summary["army"][player.name] = top_units
        summary["composition"][player.name] = top_units
        summary["signature_units"][player.name] = [
            (name, count)
            for name, count in top_units + [( _localize_term(raw_name), built[_localize_term(raw_name)] ) for raw_name in SIGNATURE_UNITS if built.get(_localize_term(raw_name), 0) > 0]
            if count > 0
        ]

    summary["combat_swings"] = _extract_combat_swings(tracker_events, players, speed_factor=speed_factor)

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
    composition = summary_metrics.get("composition", {}) or summary_metrics.get("army", {}) or {}
    worker_trends = summary_metrics.get("worker_trends", {}) or {}
    combat_swings = summary_metrics.get("combat_swings", []) or []

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
    winner_composition = _composition_for_player(composition, winner_player)
    loser_composition = _composition_for_player(composition, loser_player)
    winner_worker_trend = _worker_trend_for_player(worker_trends, winner_player)
    loser_worker_trend = _worker_trend_for_player(worker_trends, loser_player)

    summary_lines = [
        f"- {map_name}에서 열린 {matchup_kr} 경기이며, 총 {game_length} 만에 {winner_name}({winner_race_kr})가 승리했습니다.",
    ]
    if winner_metrics and loser_metrics:
        summary_lines.append(
            f"- {winner_name}이 자원 교환과 마무리 효율에서 앞섰습니다. 피해 {winner_metrics.get('resources_killed', 0)} / 손실 {winner_metrics.get('resources_lost', 0)}였고, {loser_name}는 일꾼 수 최대치 {loser_metrics.get('workers_max', 0)}까지는 잘 찍었지만 그 운영 이득을 승리로 잇지 못했습니다."
        )
    if loser_composition or winner_composition:
        summary_lines.append(
            f"- 유닛 조합은 {loser_name}이 {', '.join(_format_composition(loser_composition)) or '정보 부족'}, {winner_name}이 {', '.join(_format_composition(winner_composition)) or '정보 부족'} 중심이었습니다."
        )

    reasons: list[str] = []
    if loser_tech or winner_tech or loser_upgrades or winner_upgrades:
        reasons.append(
            _build_timing_reason(
                loser_name=loser_name,
                winner_name=winner_name,
                loser_tech=loser_tech,
                winner_tech=winner_tech,
                loser_upgrades=loser_upgrades,
                winner_upgrades=winner_upgrades,
            )
        )
    if combat_swings:
        reasons.append(_build_combat_swing_reason(combat_swings, loser_name=loser_name, winner_name=winner_name))
    if loser_composition or winner_composition:
        reasons.append(
            _build_composition_reason(
                loser_name=loser_name,
                winner_name=winner_name,
                loser_composition=loser_composition,
                winner_composition=winner_composition,
            )
        )
    if winner_metrics and loser_metrics:
        reasons.append(
            f"- 자원 지표도 이를 뒷받침합니다. {winner_name}은 피해 {winner_metrics.get('resources_killed', 0)} / 손실 {winner_metrics.get('resources_lost', 0)}로 이득을 남겼고, {loser_name}은 잘 큰 구간 뒤 교전을 비싸게 치렀습니다."
        )
    if loser_worker_trend or winner_worker_trend:
        reasons.append(_build_worker_trend_reason(loser_name, loser_worker_trend, winner_name, winner_worker_trend))

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

    sections = [
        "경기 요약",
        *summary_lines[:3],
        "",
        "승패 핵심 이유",
        *((reasons or ["- 메타데이터와 추적 이벤트 기준으로만 판단했으므로 세부 교전 해석은 제한적입니다."])[:2]),
        "",
        "핵심 피드백 3개",
        *feedback[:3],
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
    upgrade_line = _upgrade_timing_feedback_line(loser_name, loser_upgrades, loser_tech)
    if matchup == "PvT":
        first = "- PvT 가이드 기준으로 점멸 이후 관측선·거신·분광기 같은 보조 체제를 늦추지 않는 것이 중요합니다. 이번 경기도 점멸-고위기사는 갖췄지만 로봇공학 시설 연결이 늦어 한타 마무리 수단이 부족해졌을 가능성이 큽니다."
        second = upgrade_line
        third = _economy_feedback_line(loser_name, loser_metrics, winner_name, winner_metrics)
        return [first, second, third]
    if matchup == "ZvT":
        first = "- 저테전에서는 4~5분 정찰 확정, 점막 연결, 여왕 위치가 핵심입니다. 저글링·맹독충 단계에서 드랍 경로와 테란의 첫 타이밍을 얼마나 빨리 읽었는지가 경기 흐름을 크게 좌우합니다."
        second = upgrade_line
        third = _economy_feedback_line(loser_name, loser_metrics, winner_name, winner_metrics, prefer_phrase="잘 짼 뒤 교환을 비싸게 한 경기")
        return [first, second, third]
    if matchup == "TvZ":
        first = "- 테저전에서는 사신 정찰 뒤 화염차/바이킹으로 점막과 3베이스를 늦추는 흐름이 중요합니다. 테란이 이 루프를 놓치면 저그의 드론 최적화와 테크 전환을 너무 편하게 허용하게 됩니다."
        second = upgrade_line
        third = _economy_feedback_line(loser_name, loser_metrics, winner_name, winner_metrics)
        return [first, second, third]
    if matchup == "PvZ":
        first = "- 프저전에서는 우주관문 정찰 이후 트리플 판단과 방어 타워 선행 여부가 핵심입니다. 저그의 3부화장 타이밍과 병력 쥐어짜기를 놓치면 멀티 욕심이 바로 약점이 됩니다."
        second = upgrade_line
        third = _economy_feedback_line(loser_name, loser_metrics, winner_name, winner_metrics)
        return [first, second, third]
    if matchup == "ZvP":
        first = "- 저프전에서는 우관·황혼·로공·3넥 타이밍 판별이 핵심입니다. 프로토스가 2베이스 가스를 많이 먹고 3넥이 늦으면 저그는 드론 중단과 병력 전환 타이밍을 분명히 잡아야 합니다."
        second = upgrade_line
        third = _economy_feedback_line(loser_name, loser_metrics, winner_name, winner_metrics)
        return [first, second, third]
    return [
        f"- {MATCHUP_KR.get(matchup, matchup)}에서는 핵심 테크 타이밍과 정찰 정보 갱신을 같은 템포로 맞추는 것이 우선입니다.",
        upgrade_line,
        _economy_feedback_line(loser_name, loser_metrics, winner_name, winner_metrics),
    ]



def _upgrade_timing_feedback_line(loser_name: str, loser_upgrades: list[str], loser_tech: list[str]) -> str:
    first_upgrade = loser_upgrades[0] if loser_upgrades else "공방업 타이밍"
    first_tech = loser_tech[0] if loser_tech else "핵심 tech 건물 타이밍"
    return (
        f"- {loser_name} 입장에서는 {first_upgrade} 같은 공방업이 빠르거나 늦었는지 꼭 따로 보셔야 합니다. "
        f"{first_tech}처럼 핵심 건물을 지을 때 공업·방업 버튼도 같이 눌러 체제 완성 시점을 맞추는 습관이 중요합니다."
    )



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


def _composition_for_player(composition: dict[str, list[tuple[str, int]]], player: dict[str, Any]) -> list[tuple[str, int]]:
    for key in filter(None, [player.get("name"), player.get("race")]):
        if key in composition:
            return [(str(name), int(count)) for name, count in composition[key]]
    return []


def _worker_trend_for_player(worker_trends: dict[str, list[dict[str, Any]]], player: dict[str, Any]) -> list[dict[str, Any]]:
    for key in filter(None, [player.get("name"), player.get("race")]):
        if key in worker_trends:
            return worker_trends[key]
    return []


def _format_composition(units: list[tuple[str, int]]) -> list[str]:
    return [f"{name} {count}" for name, count in units[:3]]


def _build_timing_reason(
    loser_name: str,
    winner_name: str,
    loser_tech: list[str],
    winner_tech: list[str],
    loser_upgrades: list[str],
    winner_upgrades: list[str],
) -> str:
    loser_flow = ", ".join((loser_upgrades + loser_tech)[:4]) or "핵심 체제 연결"
    winner_flow = ", ".join((winner_upgrades + winner_tech)[:4]) or "핵심 전투 수단"
    return (
        f"- 빌드와 체제 선점부터 차이가 났습니다. {loser_name}은 {loser_flow} 흐름이었지만 후속 연결이 늦었고, "
        f"{winner_name}은 {winner_flow}를 더 매끄럽게 맞추며 먼저 싸움 각을 만들었습니다."
    )


def _build_composition_reason(
    loser_name: str,
    winner_name: str,
    loser_composition: list[tuple[str, int]],
    winner_composition: list[tuple[str, int]],
) -> str:
    loser_units = ", ".join(_format_composition(loser_composition)) or "병력 정보 부족"
    winner_units = ", ".join(_format_composition(winner_composition)) or "병력 정보 부족"
    return (
        f"- 유닛 조합과 싸움 구도도 중요했습니다. {loser_name}은 {loser_units} 중심이었고, "
        f"{winner_name}은 {winner_units} 중심으로 교전을 열어 조합상 더 편한 전투를 만들었습니다."
    )


def _build_worker_trend_reason(
    loser_name: str,
    loser_worker_trend: list[dict[str, Any]],
    winner_name: str,
    winner_worker_trend: list[dict[str, Any]],
) -> str:
    loser_peak = max(loser_worker_trend, key=lambda item: item.get("workers", 0), default={})
    winner_peak = max(winner_worker_trend, key=lambda item: item.get("workers", 0), default={})
    loser_peak_time = loser_peak.get("time", "알 수 없음")
    winner_peak_time = winner_peak.get("time", "알 수 없음")
    return (
        f"- 일꾼 수 증감 기준으로 보면 {loser_name}는 {loser_peak_time}에 {loser_peak.get('workers', 0)}기, "
        f"{winner_name}은 {winner_peak_time}에 {winner_peak.get('workers', 0)}기까지 확보했습니다. "
        f"이후 전투 교환비가 어느 쪽으로 기울었는지 함께 보면 운영 우위를 언제 잃었는지 더 분명하게 보입니다."
    )


def _build_combat_swing_reason(combat_swings: list[dict[str, Any]], loser_name: str, winner_name: str) -> str:
    top = combat_swings[0]
    swing_winner = top.get("winner", "Unknown")
    delta = top.get("resource_delta", 0)
    window = top.get("window", "알 수 없음")
    if swing_winner == winner_name:
        return f"- 가장 큰 전투 스윙은 {window} 교전이었고, 이 구간에서 {winner_name}가 자원 격차 {delta}만큼 이득을 보며 승기를 굳혔습니다."
    if swing_winner == loser_name:
        return f"- 가장 큰 전투 스윙은 {window} 교전이었고, 이 구간에서는 {loser_name}가 자원 격차 {delta}만큼 이득을 봤지만 이후 후속 교환을 지키지 못한 것으로 보입니다."
    return f"- 가장 큰 전투 스윙은 {window} 교전이었고, 자원 격차는 {delta} 정도였습니다."


def _extract_combat_swings(tracker_events: list[Any], players: list[Any], speed_factor: float = 1.0) -> list[dict[str, Any]]:
    windows: dict[int, dict[str, int]] = {}
    player_names = {player: getattr(player, "name", "Unknown") for player in players}

    for event in tracker_events:
        if type(event).__name__ != "UnitDiedEvent":
            continue
        killer = getattr(event, "killing_player", None)
        if killer is None:
            continue
        unit = getattr(event, "unit", None)
        resource_value = int(getattr(unit, "minerals", 0) or 0) + int(getattr(unit, "vespene", 0) or 0)
        if resource_value <= 0:
            continue
        bucket = _to_real_seconds(int(getattr(event, "second", 0) or 0), speed_factor) // 60
        name = player_names.get(killer)
        if not name:
            continue
        windows.setdefault(bucket, {})
        windows[bucket][name] = windows[bucket].get(name, 0) + resource_value

    swings: list[dict[str, Any]] = []
    for bucket, by_player in windows.items():
        if len(by_player) < 2:
            winner, score = next(iter(by_player.items()))
            delta = score
        else:
            ordered = sorted(by_player.items(), key=lambda item: item[1], reverse=True)
            winner, score = ordered[0]
            delta = score - ordered[1][1]
        if delta <= 0:
            continue
        swings.append(
            {
                "window": f"{bucket}:00-{bucket + 1}:00",
                "winner": winner,
                "resource_delta": delta,
                "resources_killed": by_player,
            }
        )

    swings.sort(key=lambda item: item.get("resource_delta", 0), reverse=True)
    return swings[:5]


def _localize_event_text(event_text: str) -> str:
    localized = str(event_text)
    for raw, kr in sorted(TERM_KR.items(), key=lambda item: len(item[0]), reverse=True):
        localized = localized.replace(raw, kr)
        localized = localized.replace(raw.lower(), kr)
    return localized


def _canonical_term(name: str) -> str:
    raw = str(name or "")
    return CANONICAL_TERM_BY_LOWER.get(raw.lower(), raw)


def _format_time(seconds: int) -> str:
    minutes, remain = divmod(int(seconds), 60)
    return f"{minutes}:{remain:02d}"


def _to_real_seconds(seconds: int, speed_factor: float) -> int:
    return int(round(int(seconds) / max(speed_factor, 0.01)))


def _speed_factor(speed: str | None) -> float:
    mapping = {
        "Slower": 0.6,
        "Slow": 0.8,
        "Normal": 1.0,
        "Fast": 1.2,
        "Faster": 1.4,
    }
    return mapping.get(str(speed or "Normal"), 1.0)


def _localize_term(name: str) -> str:
    canonical = _canonical_term(name)
    return TERM_KR.get(canonical, canonical)


def _localize_matchup(matchup: str) -> str:
    return MATCHUP_KR.get(matchup, matchup)


def _race_kr(race: str | None) -> str:
    return RACE_KR.get(race or "Unknown", race or "미상")
