from __future__ import annotations

from typing import Any

RACE_CODE = {
    "Protoss": "P",
    "Terran": "T",
    "Zerg": "Z",
    "Random": "R",
}


def replay_to_facts(replay: Any) -> dict[str, Any]:
    players: list[dict[str, Any]] = []
    winner = "Unknown"
    matchup_parts: list[str] = []

    for team in getattr(replay, "teams", []) or []:
        for player in getattr(team, "players", []) or []:
            play_race = getattr(player, "play_race", None) or getattr(player, "pick_race", None) or "Unknown"
            player_info = {
                "name": getattr(player, "name", "Unknown"),
                "race": play_race,
                "picked_race": getattr(player, "pick_race", play_race),
                "apm": getattr(player, "avg_apm", None),
                "team": getattr(team, "number", None),
                "result": getattr(team, "result", None),
            }
            players.append(player_info)
            matchup_parts.append(RACE_CODE.get(str(play_race), "?"))
            if str(getattr(team, "result", "")).lower() == "win" and winner == "Unknown":
                winner = player_info["name"]

    length_seconds = int(getattr(getattr(replay, "game_length", None), "seconds", 0) or 0)
    minutes, seconds = divmod(length_seconds, 60)

    facts = {
        "map_name": getattr(replay, "map_name", "Unknown"),
        "game_length": f"{minutes}:{seconds:02d}",
        "game_length_seconds": length_seconds,
        "played_at": str(getattr(replay, "date", "Unknown")),
        "game_type": getattr(replay, "real_type", "Unknown"),
        "category": getattr(replay, "category", "Unknown"),
        "expansion": getattr(replay, "expansion", "Unknown"),
        "winner": winner,
        "matchup": "v".join(matchup_parts) if len(matchup_parts) == 2 else " vs ".join(matchup_parts),
        "players": players,
        "replay_metadata": _serialize_replay_metadata(replay),
        "notes": [
            "리플레이 메타데이터만으로는 세부 교전 판단이 제한될 수 있다.",
            "APM은 참고치일 뿐이며 의사결정 품질을 직접 의미하지 않는다.",
        ],
    }
    return facts


def _serialize_replay_metadata(replay: Any) -> dict[str, Any]:
    return {
        "filename": getattr(replay, "filename", None),
        "gateway": getattr(replay, "gateway", None),
        "region": getattr(replay, "region", None),
        "speed": getattr(replay, "speed", None),
        "release_string": getattr(replay, "release_string", None),
        "build": getattr(replay, "build", None),
        "type": getattr(replay, "type", None),
        "real_type": getattr(replay, "real_type", None),
        "category": getattr(replay, "category", None),
        "expansion": getattr(replay, "expansion", None),
        "is_ladder": bool(getattr(replay, "is_ladder", False)),
        "teams": [_serialize_team(team) for team in getattr(replay, "teams", []) or []],
        "players": [_serialize_player(player) for player in getattr(replay, "players", []) or []],
        "observers": [_serialize_player(observer) for observer in getattr(replay, "observers", []) or []],
    }


def _serialize_team(team: Any) -> dict[str, Any]:
    return {
        "number": getattr(team, "number", None),
        "result": getattr(team, "result", None),
        "players": [_serialize_player(player) for player in getattr(team, "players", []) or []],
    }


def _serialize_player(player: Any) -> dict[str, Any]:
    return {
        "name": getattr(player, "name", None),
        "pick_race": getattr(player, "pick_race", None),
        "play_race": getattr(player, "play_race", None),
        "avg_apm": getattr(player, "avg_apm", None),
        "region": getattr(player, "region", None),
        "result": getattr(player, "result", None),
        "uid": getattr(player, "uid", None),
        "url": getattr(player, "url", None),
    }
