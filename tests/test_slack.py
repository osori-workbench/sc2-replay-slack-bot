from sc2_replay_slack_bot.slack import build_slack_text


def test_build_slack_text_contains_key_sections() -> None:
    facts = {
        "map_name": "Site Delta",
        "matchup": "ZvT",
        "winner": "osori",
        "game_length": "09:10",
    }
    analysis = "경기 요약\n- 운영 우위\n"

    text = build_slack_text(facts, analysis, replay_name="sample.SC2Replay")

    assert "sample.SC2Replay" in text
    assert "ZvT" in text
    assert "경기 요약" in text
