from pathlib import Path

from sc2_replay_slack_bot.replay_store import ReplayStore


def test_new_file_is_reported_once_and_persisted_after_mark_processed(tmp_path: Path) -> None:
    replay_path = tmp_path / "game.SC2Replay"
    replay_path.write_bytes(b"hello-replay")
    store = ReplayStore(tmp_path / "state.json")

    first = store.classify(replay_path)
    second = store.classify(replay_path)
    store.mark_processed(replay_path, first.sha256)
    third = store.classify(replay_path)

    assert first.is_new is True
    assert second.is_new is True
    assert second.reason == "new_file"
    assert third.is_new is False
    assert third.reason == "unchanged"


def test_changed_file_is_reported_again_until_marked_processed(tmp_path: Path) -> None:
    replay_path = tmp_path / "game.SC2Replay"
    replay_path.write_bytes(b"v1")
    store = ReplayStore(tmp_path / "state.json")
    first = store.classify(replay_path)
    store.mark_processed(replay_path, first.sha256)

    replay_path.write_bytes(b"v2")
    result = store.classify(replay_path)
    repeated = store.classify(replay_path)
    store.mark_processed(replay_path, result.sha256)
    final = store.classify(replay_path)

    assert result.is_new is True
    assert result.reason == "content_changed"
    assert repeated.is_new is True
    assert repeated.reason == "content_changed"
    assert final.is_new is False
