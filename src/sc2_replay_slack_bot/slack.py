from __future__ import annotations

import requests

RACE_KR = {
    "Protoss": "프로토스",
    "Terran": "테란",
    "Zerg": "저그",
    "Random": "랜덤",
}

MATCHUP_DISPLAY = {
    "PvT": "프로토스 vs 테란",
    "PvZ": "프로토스 vs 저그",
    "PvP": "프로토스 미러전",
    "TvP": "테란 vs 프로토스",
    "TvZ": "테란 vs 저그",
    "TvT": "테란 미러전",
    "ZvP": "저그 vs 프로토스",
    "ZvT": "저그 vs 테란",
    "ZvZ": "저그 미러전",
}


def build_slack_text(replay_facts: dict, analysis: str, replay_name: str) -> str:
    map_name = replay_facts.get("map_name", "Unknown")
    matchup = _display_matchup(replay_facts)
    winner = replay_facts.get("winner", "Unknown")
    game_length = replay_facts.get("game_length", "Unknown")
    timings = _summarize_timings(replay_facts)
    formatted_analysis = _format_analysis_for_slack(analysis)

    lines = [
        "🎮 *SC2 리플레이 분석 리포트*",
        "━━━━━━━━━━━━━━━━━━",
        f"• 파일: `{replay_name}`",
        f"• 맵: *{map_name}*",
        f"• 매치업: *{matchup}*",
        f"• 승자: *{winner}*",
        f"• 경기 시간: *{game_length}*",
    ]

    if timings:
        lines.extend([
            "",
            "🕒 *핵심 타이밍*",
            *[f"• {item}" for item in timings],
        ])

    lines.extend([
        "",
        "📝 *분석 본문*",
        formatted_analysis,
        "",
        "━━━━━━━━━━━━━━━━━━",
    ])
    return "\n".join(lines)


def post_to_slack(webhook_url: str, text: str) -> requests.Response:
    response = requests.post(webhook_url, json={"text": text}, timeout=30)
    response.raise_for_status()
    return response


def _display_matchup(replay_facts: dict) -> str:
    matchup = replay_facts.get("matchup")
    if matchup in MATCHUP_DISPLAY:
        return MATCHUP_DISPLAY[matchup]

    players = replay_facts.get("players", []) or []
    if len(players) == 2:
        left = RACE_KR.get(players[0].get("race"), players[0].get("race", "미상"))
        right = RACE_KR.get(players[1].get("race"), players[1].get("race", "미상"))
        return f"{left} vs {right}"
    return str(matchup or "Unknown")


def _summarize_timings(replay_facts: dict) -> list[str]:
    summary_metrics = replay_facts.get("summary_metrics", {}) or {}
    upgrades = summary_metrics.get("upgrades", {}) or {}
    items: list[str] = []
    for player_name, events in upgrades.items():
        if not events:
            continue
        items.append(f"{player_name}: {', '.join(events[:2])}")
        if len(items) >= 2:
            break
    return items


def _format_analysis_for_slack(analysis: str) -> str:
    headings = {"경기 요약", "승패 핵심 이유", "핵심 피드백 3개"}
    formatted_lines: list[str] = []
    for line in analysis.strip().splitlines():
        stripped = line.strip()
        normalized = stripped.removeprefix("- ").strip()
        if normalized in headings:
            formatted_lines.append(f"*{normalized}*")
        else:
            formatted_lines.append(line)
    return "\n".join(formatted_lines)
