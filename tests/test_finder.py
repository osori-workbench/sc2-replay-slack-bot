from datetime import datetime
from pathlib import Path
import os

from sc2_replay_slack_bot.finder import find_replay_files


def test_find_replay_files_returns_sorted_sc2replay_files_recursively(tmp_path: Path) -> None:
    root_file = tmp_path / "b.SC2Replay"
    nested_dir = tmp_path / "kihoon"
    nested_dir.mkdir()
    nested_file = nested_dir / "a.SC2Replay"
    ignored = tmp_path / "ignore.txt"

    root_file.write_text("1", encoding="utf-8")
    nested_file.write_text("2", encoding="utf-8")
    ignored.write_text("x", encoding="utf-8")

    files = find_replay_files(tmp_path)

    assert files == [nested_file, root_file]


def test_find_replay_files_skips_old_files_before_cutoff(tmp_path: Path) -> None:
    old_file = tmp_path / "old.SC2Replay"
    new_file = tmp_path / "new.SC2Replay"
    old_file.write_text("1", encoding="utf-8")
    new_file.write_text("2", encoding="utf-8")

    old_dt = datetime(2026, 5, 14, 12, 0, 0).timestamp()
    new_dt = datetime(2026, 5, 19, 12, 0, 0).timestamp()
    os.utime(old_file, (old_dt, old_dt))
    os.utime(new_file, (new_dt, new_dt))

    files = find_replay_files(tmp_path, min_mtime=datetime(2026, 5, 18, 0, 0, 0))

    assert files == [new_file]
