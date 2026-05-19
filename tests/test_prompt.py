from sc2_replay_slack_bot.prompting import build_analysis_prompt


def test_prompt_includes_match_context_and_replay_facts() -> None:
    replay_facts = {
        "map_name": "Site Delta",
        "matchup": "PvT",
        "game_length": "12:34",
        "winner": "Alpha",
        "players": [
            {"name": "Alpha", "race": "Protoss"},
            {"name": "Bravo", "race": "Terran"},
        ],
        "notes": ["APM은 참고치일 뿐이다."],
    }

    prompt = build_analysis_prompt(replay_facts, guide_context="Guide summary here")

    assert "PvT" in prompt
    assert "Guide summary here" in prompt
    assert "Alpha" in prompt
    assert "Slack" not in prompt
