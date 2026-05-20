from __future__ import annotations

from pathlib import Path
from typing import Any

RACE_GUIDE_FILES = {
    "Protoss": "protoss.md",
    "Terran": "terran.md",
    "Zerg": "zerg.md",
}


def load_guide_context(guides_dir: Path, replay_facts: dict[str, Any] | None = None, max_chars: int = 4000) -> str:
    guide_paths = select_guide_files(guides_dir, replay_facts=replay_facts)
    if not guide_paths:
        return ""

    lines = [
        "Read these local guide files with the file tool before writing the analysis.",
        "Prefer matchup-specific sections first, then fall back to general race principles.",
        "Do not quote the guides verbatim unless short terminology is needed; use them as coaching context.",
    ]
    matchup = (replay_facts or {}).get("matchup")
    if matchup:
        lines.append(f"Current matchup: {matchup}")

    players = (replay_facts or {}).get("players", []) or []
    if players:
        race_summary = ", ".join(f"{p.get('name', 'Unknown')}={p.get('race', 'Unknown')}" for p in players)
        lines.append(f"Players/races: {race_summary}")

    lines.append("Guide files:")
    lines.extend(f"- {path}" for path in guide_paths)
    text = "\n".join(lines)
    return text[:max_chars]


def select_guide_files(guides_dir: Path, replay_facts: dict[str, Any] | None = None) -> list[str]:
    guides_dir = Path(guides_dir)
    if not guides_dir.exists():
        return []

    selected: list[Path] = []
    seen: set[Path] = set()

    players = (replay_facts or {}).get("players", []) or []
    for player in players:
        guide_name = RACE_GUIDE_FILES.get(player.get("race"))
        if not guide_name:
            continue
        path = guides_dir / guide_name
        if path.exists() and path not in seen:
            selected.append(path)
            seen.add(path)

    notes_path = guides_dir / "korean-reference-notes.md"
    if notes_path.exists() and notes_path not in seen:
        selected.append(notes_path)
        seen.add(notes_path)

    if not selected:
        for path in sorted(guides_dir.glob("*.md")):
            if path not in seen:
                selected.append(path)

    return [str(path) for path in selected]
