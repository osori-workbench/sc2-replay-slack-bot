from pathlib import Path

from sc2_replay_slack_bot.replay_store import ReplayStore


def test_new_file_is_reported_once_and_persisted(tmp_path: Path) -> None:
    replay_path = tmp_path / "game.SC2Replay"
    replay_path.write_bytes(b"hello-replay")
    store = ReplayStore(tmp_path / "state.json")

    first = store.classify(replay_path)
    second = store.classify(replay_path)

    assert first.is_new is True
    assert second.is_new is False
    assert second.reason == "unchanged"


def test_changed_file_is_reported_again(tmp_path: Path) -> None:
    replay_path = tmp_path / "game.SC2Replay"
    replay_path.write_bytes(b"v1")
    store = ReplayStore(tmp_path / "state.json")
    store.classify(replay_path)

    replay_path.write_bytes(b"v2")
    result = store.classify(replay_path)

    assert result.is_new is True
    assert result.reason == "content_changed"
