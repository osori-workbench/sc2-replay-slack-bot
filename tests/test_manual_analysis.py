from sc2_replay_slack_bot.manual_analysis import build_manual_analysis


def test_manual_analysis_returns_grounded_korean_sections() -> None:
    replay_facts = {
        "map_name": "Mothership LE",
        "matchup": "PvT",
        "game_length": "13:44",
        "winner": "Kelazhur",
        "players": [
            {"name": "Geralt", "race": "Protoss", "result": "Loss"},
            {"name": "Kelazhur", "race": "Terran", "result": "Win"},
        ],
        "summary_metrics": {
            "economy": {
                "Protoss": {"workers_max": 76, "resources_lost": 4475, "resources_killed": 2200},
                "Terran": {"workers_max": 66, "resources_lost": 2200, "resources_killed": 4475},
            },
            "upgrades": {
                "Protoss": ["6:51 BlinkTech", "8:45 Charge", "10:09 PsiStormTech"],
                "Terran": ["10:05 Stimpack", "10:59 PunisherGrenades", "14:37 Ghost"],
            },
            "tech": {
                "Protoss": ["15:01 RoboticsFacility"],
                "Terran": ["6:42 SiegeTankSieged", "9:46 Medivac"],
            },
        },
    }

    guide_context = "PvT에서는 점멸 추적자 이후 관측선과 거신 연결이 중요하다."

    text = build_manual_analysis(replay_facts, guide_context=guide_context)

    assert "경기 요약" in text
    assert "승패 핵심 이유" in text
    assert "핵심 피드백 3개" in text
    assert "바로 연습할 체크리스트 3개" in text
    assert "로보" in text or "Robotics" in text
    assert "4475" in text
    assert "점멸" in text or "Blink" in text
