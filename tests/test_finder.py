from pathlib import Path

from sc2_replay_slack_bot.finder import find_replay_files


def test_find_replay_files_returns_sorted_sc2replay_files(tmp_path: Path) -> None:
    a = tmp_path / "b.SC2Replay"
    b = tmp_path / "a.SC2Replay"
    c = tmp_path / "ignore.txt"
    a.write_text("1", encoding="utf-8")
    b.write_text("2", encoding="utf-8")
    c.write_text("x", encoding="utf-8")

    files = find_replay_files(tmp_path)

    assert files == [b, a]
