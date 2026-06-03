from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

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


def build_slack_text(replay_facts: dict, analysis: str, replay_name: str, focus_player: dict | None = None) -> str:
    map_name = replay_facts.get("map_name", "Unknown")
    matchup = _display_matchup(replay_facts)
    winner = replay_facts.get("winner", "Unknown")
    game_length = replay_facts.get("game_length", "Unknown")
    played_at = _format_played_at_kst(replay_facts.get("played_at"))
    timings = _summarize_timings(replay_facts)
    formatted_analysis = _format_analysis_for_slack(analysis)

    lines = [
        "🎮 *SC2 리플레이 분석 리포트*",
        "━━━━━━━━━━━━━━━━━━",
    ]
    focus_title = _focus_player_title(focus_player)
    if focus_title:
        lines.extend([
            focus_title,
            "",
        ])
    lines.extend([
        f"• 파일: `{replay_name}`",
        f"• 맵: *{map_name}*",
        f"• 매치업: *{matchup}*",
        f"• 승자: *{winner}*",
        f"• 경기 시간: *{game_length}*",
    ])
    if played_at:
        lines.append(f"• 경기 시각(KST): *{played_at}*")

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
    signature_transitions = summary_metrics.get("signature_transitions", {}) or {}
    upgrades = summary_metrics.get("upgrades", {}) or {}
    tech = summary_metrics.get("tech", {}) or {}
    items: list[str] = []
    player_names = []
    for bucket in (signature_transitions, upgrades, tech):
        for player_name, events in bucket.items():
            if not events or player_name in player_names:
                continue
            items.append(f"{player_name}: {', '.join(events[:2])}")
            player_names.append(player_name)
            if len(items) >= 2:
                return items
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



def _focus_player_title(focus_player: dict | None) -> str:
    if not focus_player:
        return ""
    name = str(focus_player.get("name") or "").strip()
    if not name:
        return ""
    return f"👤 *{name} 기준으로 리뷰했습니다.*"



def _format_played_at_kst(played_at: object) -> str:
    if not played_at:
        return ""
    text = str(played_at).strip()
    if not text or text == "Unknown":
        return ""

    normalized = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return text

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
