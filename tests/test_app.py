from pathlib import Path
from types import SimpleNamespace

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



def test_run_once_dry_run_processes_new_replay(tmp_path: Path, monkeypatch) -> None:
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
        llm_api_key="",
        llm_api_base_url="https://api.openai.com/v1",
        llm_model="gpt-4.1-mini",
    )

    monkeypatch.setattr("sc2_replay_slack_bot.app.load_config", lambda: config)
    monkeypatch.setattr(
        "sc2_replay_slack_bot.app.sc2reader.load_replay",
        lambda *_args, **_kwargs: SimpleNamespace(
            map_name="Abyssal Reef",
            game_length=SimpleNamespace(seconds=321),
            date="2026-05-19",
            real_type="1v1",
            category="Ladder",
            expansion="LotV",
            teams=[
                FakeTeam(1, "Win", [FakePlayer("Alpha", "Protoss", "Protoss", 200)]),
                FakeTeam(2, "Loss", [FakePlayer("Bravo", "Terran", "Terran", 180)]),
            ],
        ),
    )

    results = run_once(dry_run=True, max_files=5)

    assert len(results) == 1
    assert results[0]["facts"]["matchup"] == "PvT"
    assert "sample.SC2Replay" in results[0]["slack_text"]
