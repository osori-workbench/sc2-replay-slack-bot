from sc2_replay_slack_bot.prompting import build_analysis_prompt


def test_prompt_includes_match_context_and_richer_replay_facts() -> None:
    replay_facts = {
        "map_name": "Site Delta",
        "matchup": "PvT",
        "game_length": "12:34",
        "winner": "Alpha",
        "players": [
            {"name": "Alpha", "race": "Protoss"},
            {"name": "Bravo", "race": "Terran"},
        ],
        "summary_metrics": {
            "composition": {"Alpha": [("추적자", 12), ("광전사", 8)]},
            "worker_trends": {"Alpha": [{"time": "5:00", "workers": 44, "resources_killed": 400, "resources_lost": 200}]},
            "combat_swings": [{"window": "8:00-9:00", "winner": "Alpha", "resource_delta": 750}],
        },
        "notes": ["APM은 참고치일 뿐이다."],
    }

    prompt = build_analysis_prompt(replay_facts, guide_context="Guide summary here")

    assert "PvT" in prompt
    assert "Guide summary here" in prompt
    assert "Alpha" in prompt
    assert "유닛 조합" in prompt
    assert "일꾼 수 증감" in prompt
    assert "전투 스윙" in prompt
    assert "바로 연습할 체크리스트" not in prompt
    assert "Slack" not in prompt
