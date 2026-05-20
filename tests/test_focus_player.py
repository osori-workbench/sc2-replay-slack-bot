from pathlib import Path

from sc2_replay_slack_bot.focus_player import detect_focus_player
from sc2_replay_slack_bot.prompting import build_analysis_context, build_analysis_prompt


def test_detect_focus_player_from_parent_directory_when_name_matches_player() -> None:
    replay_facts = {
        "players": [
            {"name": "Undead", "race": "Protoss", "result": "Loss"},
            {"name": "Bravo", "race": "Terran", "result": "Win"},
        ]
    }

    focus = detect_focus_player(
        Path("/tmp/star2-replay/Undead/Old Republic LE (9).SC2Replay"),
        replay_facts,
    )

    assert focus is not None
    assert focus["name"] == "Undead"
    assert focus["race"] == "Protoss"
    assert focus["directory_name"] == "Undead"


def test_detect_focus_player_returns_none_when_directory_does_not_match() -> None:
    replay_facts = {
        "players": [
            {"name": "Alpha", "race": "Zerg"},
            {"name": "Bravo", "race": "Terran"},
        ]
    }

    focus = detect_focus_player(
        Path("/tmp/star2-replay/Undead/Old Republic LE (9).SC2Replay"),
        replay_facts,
    )

    assert focus is None


def test_prompt_and_context_instruct_player_specific_feedback_when_focus_player_exists() -> None:
    replay_facts = {
        "matchup": "PvZ",
        "players": [
            {"name": "Undead", "race": "Protoss", "result": "Loss"},
            {"name": "Bravo", "race": "Zerg", "result": "Win"},
        ],
        "summary_metrics": {
            "composition": {
                "Undead": [("추적자", 14), ("광전사", 6)],
                "Bravo": [("저글링", 40), ("바퀴", 14)],
            }
        },
    }
    focus_player = {"name": "Undead", "race": "Protoss", "result": "Loss", "directory_name": "Undead"}

    prompt = build_analysis_prompt(
        replay_facts,
        guide_context="Read guides first",
        focus_player=focus_player,
    )
    context = build_analysis_context(
        replay_facts,
        guide_context="Read guides first",
        guide_file_paths=["/tmp/protoss.md", "/tmp/zerg.md"],
        focus_player=focus_player,
    )

    assert "Undead" in prompt
    assert "프로토스" in prompt
    assert "빌드오더" in prompt
    assert "유닛구성" in prompt
    assert "다른 플레이어를 위한 조언" in prompt
    assert context["focus_player"]["name"] == "Undead"
    assert context["focus_player"]["race"] == "Protoss"
