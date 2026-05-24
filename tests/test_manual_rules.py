from sc2_replay_slack_bot.manual_analysis import build_manual_analysis


def test_zvt_analysis_uses_zerg_specific_korean_feedback() -> None:
    replay_facts = {
        "map_name": "Alcyone",
        "matchup": "ZvT",
        "game_length": "09:55",
        "winner": "Alpha",
        "players": [
            {"name": "Alpha", "race": "Zerg", "result": "Win"},
            {"name": "Bravo", "race": "Terran", "result": "Loss"},
        ],
        "summary_metrics": {
            "economy": {
                "Alpha": {"race": "Zerg", "workers_max": 72, "resources_lost": 2600, "resources_killed": 5100},
                "Bravo": {"race": "Terran", "workers_max": 51, "resources_lost": 5100, "resources_killed": 2600},
            },
            "upgrades": {
                "Alpha": ["5:20 ZerglingMovementSpeed", "8:00 BanelingSpeed"],
                "Bravo": ["5:15 Stimpack", "5:55 ShieldWall"],
            },
            "tech": {
                "Alpha": ["4:30 BanelingNest", "7:20 Lair"],
                "Bravo": ["3:50 Factory", "4:30 Medivac"],
            },
        },
    }

    text = build_manual_analysis(replay_facts, guide_context="ZvT에서는 4~5분 정찰 확정과 점막/여왕 위치가 중요하다.")

    assert "점막" in text
    assert "여왕" in text
    assert "정찰" in text
    assert "저글링" in text or "맹독충" in text
    assert "Stimpack" not in text



def test_manual_analysis_highlights_upgrade_timing_importance() -> None:
    replay_facts = {
        "map_name": "Site Delta",
        "matchup": "PvT",
        "game_length": "12:34",
        "winner": "Bravo",
        "players": [
            {"name": "Alpha", "race": "Protoss", "result": "Loss"},
            {"name": "Bravo", "race": "Terran", "result": "Win"},
        ],
        "summary_metrics": {
            "economy": {
                "Alpha": {"race": "Protoss", "workers_max": 48, "resources_lost": 6200, "resources_killed": 3500},
                "Bravo": {"race": "Terran", "workers_max": 52, "resources_lost": 3500, "resources_killed": 6200},
            },
            "upgrades": {
                "Alpha": ["7:40 지상 공업 1단계"],
                "Bravo": ["5:15 자극제", "5:55 전투방패"],
            },
            "tech": {
                "Alpha": ["5:20 로봇공학 시설", "6:40 황혼 의회"],
                "Bravo": ["3:50 군수공장", "4:30 의료선"],
            },
        },
    }

    text = build_manual_analysis(replay_facts)

    assert "공업" in text or "방업" in text
    assert "늦" in text or "빠" in text
    assert "같이" in text
