from __future__ import annotations

from pathlib import Path


def find_replay_files(replay_dir: Path) -> list[Path]:
    replay_dir = Path(replay_dir)
    return sorted(replay_dir.glob("*.SC2Replay"), key=lambda path: path.name)
