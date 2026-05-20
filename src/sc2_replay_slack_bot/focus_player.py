from __future__ import annotations

from pathlib import Path
from typing import Any
import unicodedata


def detect_focus_player(replay_path: Path, replay_facts: dict[str, Any]) -> dict[str, Any] | None:
    directory_name = replay_path.parent.name
    normalized_directory = _normalize_name(directory_name)
    if not normalized_directory:
        return None

    for player in replay_facts.get("players", []) or []:
        player_name = str(player.get("name", ""))
        if _normalize_name(player_name) == normalized_directory:
            focus = dict(player)
            focus["directory_name"] = directory_name
            return focus
    return None


def _normalize_name(value: str) -> str:
    return unicodedata.normalize("NFC", value).strip().casefold()
