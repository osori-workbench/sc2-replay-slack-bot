from sc2_replay_slack_bot.slack import build_slack_text


def test_build_slack_text_contains_block_style_sections() -> None:
    facts = {
        "map_name": "Site Delta",
        "matchup": "ZvT",
        "winner": "osori",
        "game_length": "09:10",
        "players": [
            {"name": "Alpha", "race": "Zerg"},
            {"name": "Bravo", "race": "Terran"},
        ],
        "summary_metrics": {
            "upgrades": {
                "Alpha": ["6:20 대군주 속업", "8:10 맹독충 둥지"],
                "Bravo": ["5:00 자극제", "6:40 전투방패"],
            }
        },
    }
    analysis = "경기 요약\n- 운영 우위\n\n승패 핵심 이유\n- 정찰 우위\n"

    text = build_slack_text(facts, analysis, replay_name="sample.SC2Replay")

    assert "🎮" in text
    assert "sample.SC2Replay" in text
    assert "저그 vs 테란" in text
    assert "핵심 타이밍" in text
    assert "경기 요약" in text
    assert "━━━━━━━━" in text
