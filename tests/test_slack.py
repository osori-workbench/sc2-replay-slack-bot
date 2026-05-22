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
    analysis = "- 경기 요약\n- 운영 우위\n\n- 승패 핵심 이유\n- 정찰 우위\n\n- 핵심 피드백 3개\n- 조합 전환"

    text = build_slack_text(facts, analysis, replay_name="sample.SC2Replay")

    assert "🎮" in text
    assert "sample.SC2Replay" in text
    assert "저그 vs 테란" in text
    assert "핵심 타이밍" in text
    assert "*경기 요약*" in text
    assert "*승패 핵심 이유*" in text
    assert "━━━━━━━━" in text


def test_build_slack_text_prefers_signature_transitions_for_key_timings() -> None:
    facts = {
        "map_name": "White Rabbit LE",
        "matchup": "ZvZ",
        "winner": "스탠딩",
        "game_length": "14:38",
        "players": [
            {"name": "스탠딩", "race": "Zerg"},
            {"name": "UMBRO", "race": "Zerg"},
        ],
        "summary_metrics": {
            "signature_transitions": {
                "스탠딩": ["6:08 땅굴망", "6:24 땅굴벌레"],
                "UMBRO": ["6:18 둥지탑", "6:42 뮤탈리스크"],
            },
            "upgrades": {
                "스탠딩": ["5:41 바퀴 속업"],
            },
        },
    }

    text = build_slack_text(facts, "경기 요약\n...", replay_name="sample.SC2Replay")

    assert "스탠딩: 6:08 땅굴망, 6:24 땅굴벌레" in text
    assert "UMBRO: 6:18 둥지탑, 6:42 뮤탈리스크" in text



def test_build_slack_text_adds_focus_player_title_when_present() -> None:
    facts = {
        "map_name": "Ruby Rock LE",
        "matchup": "PvZ",
        "winner": "Undead",
        "game_length": "07:14",
        "players": [
            {"name": "Undead", "race": "Protoss"},
            {"name": "상대", "race": "Zerg"},
        ],
        "summary_metrics": {},
    }

    text = build_slack_text(
        facts,
        "경기 요약\n...",
        replay_name="sample.SC2Replay",
        focus_player={"name": "Undead", "race": "Protoss"},
    )

    assert "👤 *Undead 기준으로 리뷰했습니다.*" in text
