from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReplayStatus:
    is_new: bool
    reason: str
    sha256: str


class ReplayStore:
    def __init__(self, state_path: Path) -> None:
        self.state_path = Path(state_path)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self._state = self._load()

    def classify(self, replay_path: Path) -> ReplayStatus:
        replay_path = Path(replay_path)
        sha256 = _sha256_file(replay_path)
        key = str(replay_path.resolve())
        previous = self._state.get(key)

        if previous == sha256:
            return ReplayStatus(is_new=False, reason="unchanged", sha256=sha256)

        reason = "new_file" if previous is None else "content_changed"
        self._state[key] = sha256
        self.state_path.write_text(
            json.dumps(self._state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return ReplayStatus(is_new=True, reason=reason, sha256=sha256)

    def _load(self) -> dict[str, str]:
        if not self.state_path.exists():
            return {}
        return json.loads(self.state_path.read_text(encoding="utf-8"))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()
