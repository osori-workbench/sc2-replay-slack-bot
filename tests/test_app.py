from pathlib import Path
from types import SimpleNamespace

import pytest

from sc2_replay_slack_bot.app import run_once
from sc2_replay_slack_bot.config import AppConfig


class FakeTeam:
    def __init__(self, number, result, players):
        self.number = number
        self.result = result
        self.players = players


class FakePlayer:
    def __init__(self, name, pick_race, play_race, avg_apm):
        self.name = name
        self.pick_race = pick_race
        self.play_race = play_race
        self.avg_apm = avg_apm



def test_run_once_dry_run_processes_new_replay_with_hermes_analysis(tmp_path: Path, monkeypatch) -> None:
    replay_dir = tmp_path / "replays"
    replay_dir.mkdir()
    replay_path = replay_dir / "sample.SC2Replay"
    replay_path.write_bytes(b"replay")

    guides_dir = tmp_path / "guides"
    guides_dir.mkdir()
    (guides_dir / "protoss.md").write_text("# Guide\nhello", encoding="utf-8")

    config = AppConfig(
        replay_dir=replay_dir,
        state_path=tmp_path / "state.json",
        guides_dir=guides_dir,
        slack_webhook_url="",
        analyzer_mode="heuristic",
        min_replay_mtime=None,
        llm_api_key="",
        llm_api_base_url="http://127.0.0.1:8787",
        llm_model="hermes",
    )

    replay = SimpleNamespace(
        map_name="Abyssal Reef",
        game_length=SimpleNamespace(seconds=321),
        date="2026-05-19",
        real_type="1v1",
        category="Ladder",
        expansion="LotV",
        release_string="5.0.14",
        speed="Faster",
        type="1v1",
        is_ladder=True,
        teams=[
            FakeTeam(1, "Win", [FakePlayer("Alpha", "Protoss", "Protoss", 200)]),
            FakeTeam(2, "Loss", [FakePlayer("Bravo", "Terran", "Terran", 180)]),
        ],
        players=[
            FakePlayer("Alpha", "Protoss", "Protoss", 200),
            FakePlayer("Bravo", "Terran", "Terran", 180),
        ],
        tracker_events=[],
    )

    monkeypatch.setattr("sc2_replay_slack_bot.app.load_config", lambda: config)
    monkeypatch.setattr("sc2_replay_slack_bot.app.sc2reader.load_replay", lambda *_args, **_kwargs: replay)

    captured: dict = {}

    def fake_analyze(self, prompt: str, context: dict | None = None) -> str:
        captured["prompt"] = prompt
        captured["context"] = context
        return "경기 요약\n- Hermes 분석 결과\n승패 핵심 이유\n- 타이밍 우위\n핵심 피드백 3개\n- 정찰"

    monkeypatch.setattr("sc2_replay_slack_bot.app.LLMClient.analyze", fake_analyze)
    monkeypatch.setattr(
        "sc2_replay_slack_bot.app.build_manual_analysis",
        lambda *_args, **_kwargs: pytest.fail("manual analysis should not be used in heuristic mode"),
    )

    results = run_once(dry_run=True, max_files=5)

    assert len(results) == 1
    assert results[0]["facts"]["matchup"] == "PvT"
    assert results[0]["analysis"].startswith("경기 요약")
    assert "sample.SC2Replay" in results[0]["slack_text"]
    assert captured["context"]["replay_facts"]["matchup"] == "PvT"
    assert captured["context"]["replay_facts"]["replay_metadata"]["release_string"] == "5.0.14"
    assert "Read these local guide files" in captured["context"]["guide_context"]
    assert any(path.endswith('protoss.md') for path in captured["context"]["guide_file_paths"])
    assert all(not path.endswith('terran.md') for path in captured["context"]["guide_file_paths"])
    assert captured["context"]["focus_player"] is None


def test_run_once_sets_focus_player_from_parent_directory(tmp_path: Path, monkeypatch) -> None:
    replay_dir = tmp_path / "replays" / "Undead"
    replay_dir.mkdir(parents=True)
    replay_path = replay_dir / "sample.SC2Replay"
    replay_path.write_bytes(b"replay")

    guides_dir = tmp_path / "guides"
    guides_dir.mkdir()
    (guides_dir / "protoss.md").write_text("# Guide\nhello", encoding="utf-8")

    config = AppConfig(
        replay_dir=tmp_path / "replays",
        state_path=tmp_path / "state.json",
        guides_dir=guides_dir,
        slack_webhook_url="",
        analyzer_mode="heuristic",
        min_replay_mtime=None,
        llm_api_key="",
        llm_api_base_url="http://127.0.0.1:8787",
        llm_model="hermes",
    )

    replay = SimpleNamespace(
        map_name="Abyssal Reef",
        game_length=SimpleNamespace(seconds=321),
        date="2026-05-19",
        real_type="1v1",
        category="Ladder",
        expansion="LotV",
        release_string="5.0.14",
        speed="Faster",
        type="1v1",
        is_ladder=True,
        teams=[
            FakeTeam(1, "Loss", [FakePlayer("Undead", "Protoss", "Protoss", 200)]),
            FakeTeam(2, "Win", [FakePlayer("Bravo", "Terran", "Terran", 180)]),
        ],
        players=[
            FakePlayer("Undead", "Protoss", "Protoss", 200),
            FakePlayer("Bravo", "Terran", "Terran", 180),
        ],
        tracker_events=[],
    )

    monkeypatch.setattr("sc2_replay_slack_bot.app.load_config", lambda: config)
    monkeypatch.setattr("sc2_replay_slack_bot.app.sc2reader.load_replay", lambda *_args, **_kwargs: replay)

    captured: dict = {}

    def fake_analyze(self, prompt: str, context: dict | None = None) -> str:
        captured["prompt"] = prompt
        captured["context"] = context
        return "경기 요약\n- Hermes 분석 결과\n승패 핵심 이유\n- 타이밍 우위\n핵심 피드백 3개\n- 정찰"

    monkeypatch.setattr("sc2_replay_slack_bot.app.LLMClient.analyze", fake_analyze)

    results = run_once(dry_run=True, max_files=5)

    assert len(results) == 1
    assert captured["context"]["focus_player"]["name"] == "Undead"
    assert captured["context"]["focus_player"]["race"] == "Protoss"
    assert "빌드오더" in captured["prompt"]
    assert "유닛구성" in captured["prompt"]


def test_run_once_processes_first_new_replay_even_if_it_sorts_after_processed_files(tmp_path: Path, monkeypatch) -> None:
    replay_dir = tmp_path / "replays"
    replay_dir.mkdir()
    for index in range(1, 25):
        (replay_dir / f"{index:02d}.SC2Replay").write_bytes(f"old-{index}".encode())
    new_replay = replay_dir / "25.SC2Replay"
    new_replay.write_bytes(b"new")

    guides_dir = tmp_path / "guides"
    guides_dir.mkdir()
    config = AppConfig(
        replay_dir=replay_dir,
        state_path=tmp_path / "state.json",
        guides_dir=guides_dir,
        slack_webhook_url="",
        analyzer_mode="manual",
        min_replay_mtime=None,
        llm_api_key="",
        llm_api_base_url="https://api.openai.com/v1",
        llm_model="gpt-4.1-mini",
    )
    processed_state = {
        str((replay_dir / f"{index:02d}.SC2Replay").resolve()): __import__("hashlib").sha256(f"old-{index}".encode()).hexdigest()
        for index in range(1, 25)
    }
    config.state_path.write_text(__import__("json").dumps(processed_state), encoding="utf-8")

    monkeypatch.setattr("sc2_replay_slack_bot.app.load_config", lambda: config)
    monkeypatch.setattr(
        "sc2_replay_slack_bot.app.sc2reader.load_replay",
        lambda *_args, **_kwargs: SimpleNamespace(
            map_name="Post-Youth",
            game_length=SimpleNamespace(seconds=600),
            date="2026-05-19",
            real_type="1v1",
            category="Ladder",
            expansion="LotV",
            teams=[
                FakeTeam(1, "Win", [FakePlayer("Alpha", "Protoss", "Protoss", 200)]),
                FakeTeam(2, "Loss", [FakePlayer("Bravo", "Terran", "Terran", 180)]),
            ],
            players=[
                FakePlayer("Alpha", "Protoss", "Protoss", 200),
                FakePlayer("Bravo", "Terran", "Terran", 180),
            ],
            tracker_events=[],
        ),
    )
    monkeypatch.setattr(
        "sc2_replay_slack_bot.app.build_manual_analysis",
        lambda *_args, **_kwargs: "경기 요약\n- manual\n승패 핵심 이유\n- manual\n핵심 피드백 3개\n- manual",
    )

    results = run_once(dry_run=True, max_files=1)

    assert len(results) == 1
    assert results[0]["replay"] == "25.SC2Replay"



def test_run_once_skips_unreadable_replay_and_continues(tmp_path: Path, monkeypatch) -> None:
    replay_dir = tmp_path / "replays"
    replay_dir.mkdir()
    bad_replay = replay_dir / "bad.SC2Replay"
    good_replay = replay_dir / "good.SC2Replay"
    bad_replay.write_bytes(b"bad")
    good_replay.write_bytes(b"good")

    guides_dir = tmp_path / "guides"
    guides_dir.mkdir()
    config = AppConfig(
        replay_dir=replay_dir,
        state_path=tmp_path / "state.json",
        guides_dir=guides_dir,
        slack_webhook_url="",
        analyzer_mode="manual",
        min_replay_mtime=None,
        llm_api_key="",
        llm_api_base_url="https://api.openai.com/v1",
        llm_model="gpt-4.1-mini",
    )

    monkeypatch.setattr("sc2_replay_slack_bot.app.load_config", lambda: config)

    def fake_load_replay(path: str, **_kwargs):
        if path.endswith('bad.SC2Replay'):
            raise OSError('Resource deadlock avoided')
        return SimpleNamespace(
            map_name="Post-Youth",
            game_length=SimpleNamespace(seconds=600),
            date="2026-05-19",
            real_type="1v1",
            category="Ladder",
            expansion="LotV",
            teams=[
                FakeTeam(1, "Win", [FakePlayer("Alpha", "Protoss", "Protoss", 200)]),
                FakeTeam(2, "Loss", [FakePlayer("Bravo", "Terran", "Terran", 180)]),
            ],
            players=[
                FakePlayer("Alpha", "Protoss", "Protoss", 200),
                FakePlayer("Bravo", "Terran", "Terran", 180),
            ],
            tracker_events=[],
        )

    monkeypatch.setattr("sc2_replay_slack_bot.app.sc2reader.load_replay", fake_load_replay)

    results = run_once(dry_run=True, max_files=10)

    assert len(results) == 1
    assert results[0]["replay"] == "good.SC2Replay"


def test_run_once_does_not_mark_replay_processed_when_analysis_fails(tmp_path: Path, monkeypatch) -> None:
    replay_dir = tmp_path / "replays"
    replay_dir.mkdir()
    replay_path = replay_dir / "sample.SC2Replay"
    replay_path.write_bytes(b"replay")

    guides_dir = tmp_path / "guides"
    guides_dir.mkdir()
    (guides_dir / "protoss.md").write_text("# Guide\nhello", encoding="utf-8")

    config = AppConfig(
        replay_dir=replay_dir,
        state_path=tmp_path / "state.json",
        guides_dir=guides_dir,
        slack_webhook_url="",
        analyzer_mode="heuristic",
        min_replay_mtime=None,
        llm_api_key="",
        llm_api_base_url="http://127.0.0.1:8787",
        llm_model="hermes",
    )

    replay = SimpleNamespace(
        map_name="Abyssal Reef",
        game_length=SimpleNamespace(seconds=321),
        date="2026-05-19",
        real_type="1v1",
        category="Ladder",
        expansion="LotV",
        release_string="5.0.14",
        speed="Faster",
        type="1v1",
        is_ladder=True,
        teams=[
            FakeTeam(1, "Win", [FakePlayer("Alpha", "Protoss", "Protoss", 200)]),
            FakeTeam(2, "Loss", [FakePlayer("Bravo", "Terran", "Terran", 180)]),
        ],
        players=[
            FakePlayer("Alpha", "Protoss", "Protoss", 200),
            FakePlayer("Bravo", "Terran", "Terran", 180),
        ],
        tracker_events=[],
    )

    monkeypatch.setattr("sc2_replay_slack_bot.app.load_config", lambda: config)
    monkeypatch.setattr("sc2_replay_slack_bot.app.sc2reader.load_replay", lambda *_args, **_kwargs: replay)

    def failing_analyze(self, prompt: str, context: dict | None = None) -> str:
        raise TimeoutError("Hermes timed out")

    monkeypatch.setattr("sc2_replay_slack_bot.app.LLMClient.analyze", failing_analyze)

    results = run_once(dry_run=True, max_files=5)

    assert results == []
    state_text = config.state_path.read_text(encoding="utf-8") if config.state_path.exists() else "{}"
    assert replay_path.resolve().as_posix() not in state_text


def test_run_once_skips_short_games_under_one_minute_without_review(tmp_path: Path, monkeypatch) -> None:
    replay_dir = tmp_path / "replays"
    replay_dir.mkdir()
    replay_path = replay_dir / "short.SC2Replay"
    replay_path.write_bytes(b"replay")

    guides_dir = tmp_path / "guides"
    guides_dir.mkdir()

    config = AppConfig(
        replay_dir=replay_dir,
        state_path=tmp_path / "state.json",
        guides_dir=guides_dir,
        slack_webhook_url="",
        analyzer_mode="heuristic",
        min_replay_mtime=None,
        llm_api_key="",
        llm_api_base_url="http://127.0.0.1:8787",
        llm_model="hermes",
    )

    replay = SimpleNamespace(
        map_name="Abyssal Reef",
        game_length=SimpleNamespace(seconds=59),
        date="2026-05-19",
        real_type="1v1",
        category="Ladder",
        expansion="LotV",
        release_string="5.0.14",
        speed="Faster",
        type="1v1",
        is_ladder=True,
        teams=[
            FakeTeam(1, "Win", [FakePlayer("Alpha", "Protoss", "Protoss", 200)]),
            FakeTeam(2, "Loss", [FakePlayer("Bravo", "Terran", "Terran", 180)]),
        ],
        players=[
            FakePlayer("Alpha", "Protoss", "Protoss", 200),
            FakePlayer("Bravo", "Terran", "Terran", 180),
        ],
        tracker_events=[],
    )

    monkeypatch.setattr("sc2_replay_slack_bot.app.load_config", lambda: config)
    monkeypatch.setattr("sc2_replay_slack_bot.app.sc2reader.load_replay", lambda *_args, **_kwargs: replay)
    monkeypatch.setattr(
        "sc2_replay_slack_bot.app.LLMClient.analyze",
        lambda *_args, **_kwargs: pytest.fail("short games should not be analyzed"),
    )
    monkeypatch.setattr(
        "sc2_replay_slack_bot.app.build_manual_analysis",
        lambda *_args, **_kwargs: pytest.fail("short games should not be manually analyzed"),
    )
    monkeypatch.setattr(
        "sc2_replay_slack_bot.app.post_to_slack",
        lambda *_args, **_kwargs: pytest.fail("short games should not be posted to Slack"),
    )

    results = run_once(dry_run=False, max_files=5)

    assert results == []
    state_text = config.state_path.read_text(encoding="utf-8")
    assert replay_path.resolve().as_posix() in state_text



def test_run_once_skips_replays_with_cheater_or_ai_player_names(tmp_path: Path, monkeypatch) -> None:
    replay_dir = tmp_path / "replays"
    replay_dir.mkdir()
    replay_path = replay_dir / "cheater.SC2Replay"
    replay_path.write_bytes(b"replay")

    guides_dir = tmp_path / "guides"
    guides_dir.mkdir()

    config = AppConfig(
        replay_dir=replay_dir,
        state_path=tmp_path / "state.json",
        guides_dir=guides_dir,
        slack_webhook_url="",
        analyzer_mode="heuristic",
        min_replay_mtime=None,
        llm_api_key="",
        llm_api_base_url="http://127.0.0.1:8787",
        llm_model="hermes",
    )

    replay = SimpleNamespace(
        map_name="Abyssal Reef",
        game_length=SimpleNamespace(seconds=600),
        date="2026-05-19",
        real_type="1v1",
        category="Ladder",
        expansion="LotV",
        release_string="5.0.14",
        speed="Faster",
        type="1v1",
        is_ladder=True,
        teams=[
            FakeTeam(1, "Win", [FakePlayer("Alpha", "Protoss", "Protoss", 200)]),
            FakeTeam(2, "Loss", [FakePlayer("인공지능 칸 (정예)", "Terran", "Terran", 180)]),
        ],
        players=[
            FakePlayer("Alpha", "Protoss", "Protoss", 200),
            FakePlayer("인공지능 칸 (정예)", "Terran", "Terran", 180),
        ],
        tracker_events=[],
    )

    monkeypatch.setattr("sc2_replay_slack_bot.app.load_config", lambda: config)
    monkeypatch.setattr("sc2_replay_slack_bot.app.sc2reader.load_replay", lambda *_args, **_kwargs: replay)
    monkeypatch.setattr(
        "sc2_replay_slack_bot.app.LLMClient.analyze",
        lambda *_args, **_kwargs: pytest.fail("cheater/AI replays should not be analyzed"),
    )
    monkeypatch.setattr(
        "sc2_replay_slack_bot.app.build_manual_analysis",
        lambda *_args, **_kwargs: pytest.fail("cheater/AI replays should not be manually analyzed"),
    )
    monkeypatch.setattr(
        "sc2_replay_slack_bot.app.post_to_slack",
        lambda *_args, **_kwargs: pytest.fail("cheater/AI replays should not be posted to Slack"),
    )

    results = run_once(dry_run=False, max_files=5)

    assert results == []
    state_text = config.state_path.read_text(encoding="utf-8")
    assert replay_path.resolve().as_posix() in state_text
