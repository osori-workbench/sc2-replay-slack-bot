from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path


def find_replay_files(replay_dir: Path, min_mtime: datetime | None = None) -> list[Path]:
    replay_dir = Path(replay_dir)
    found: list[Path] = []

    def _ignore_walk_error(_error: OSError) -> None:
        return None

    for root, dirs, files in os.walk(replay_dir, onerror=_ignore_walk_error, followlinks=False):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if not Path(root_path, d).is_symlink()]
        for filename in files:
            if not filename.endswith('.SC2Replay'):
                continue
            path = root_path / filename
            try:
                if not path.is_file():
                    continue
                if min_mtime is not None:
                    modified_at = datetime.fromtimestamp(path.stat().st_mtime)
                    if modified_at < min_mtime:
                        continue
                found.append(path)
            except OSError:
                continue

    return sorted(found, key=lambda path: (path.name, str(path.parent)))
