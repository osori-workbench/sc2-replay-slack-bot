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
                "Protoss": {"workers_max": 76, "resources_lost": 4475, "resources_killed": 2200, "resource_efficiency_ratio": 0.49},
                "Terran": {"workers_max": 66, "resources_lost": 2200, "resources_killed": 4475, "resource_efficiency_ratio": 2.03},
            },
            "upgrades": {
                "Protoss": ["6:51 BlinkTech", "8:45 Charge", "10:09 PsiStormTech"],
                "Terran": ["10:05 Stimpack", "10:59 PunisherGrenades", "14:37 Ghost"],
            },
            "tech": {
                "Protoss": ["15:01 RoboticsFacility"],
                "Terran": ["6:42 SiegeTankSieged", "9:46 Medivac"],
            },
            "composition": {
                "Protoss": [("추적자", 22), ("광전사", 18), ("고위 기사", 6)],
                "Terran": [("해병", 40), ("불곰", 14), ("의료선", 6)],
            },
            "worker_trends": {
                "Protoss": [
                    {"time": "5:00", "workers": 44, "resources_killed": 300, "resources_lost": 200},
                    {"time": "10:00", "workers": 76, "resources_killed": 900, "resources_lost": 1200},
                ],
                "Terran": [
                    {"time": "5:00", "workers": 38, "resources_killed": 200, "resources_lost": 300},
                    {"time": "10:00", "workers": 66, "resources_killed": 2100, "resources_lost": 900},
                ],
            },
            "combat_swings": [
                {"window": "10:00-11:00", "winner": "Kelazhur", "resource_delta": 1350},
                {"window": "8:00-9:00", "winner": "Geralt", "resource_delta": 450},
            ],
        },
    }

    guide_context = "PvT에서는 점멸 추적자 이후 관측선과 거신 연결이 중요하다."

    text = build_manual_analysis(replay_facts, guide_context=guide_context)

    assert "경기 요약" in text
    assert "승패 핵심 이유" in text
    assert "핵심 피드백 3개" in text
    assert "바로 연습할 체크리스트" not in text
    assert "로봇공학 시설" in text
    assert "자원 교환" in text
    assert "4475" in text
    assert "점멸" in text
    assert "BlinkTech" not in text
    assert "RoboticsFacility" not in text
    assert "killed" not in text
    assert "유닛 조합" in text
    assert "추적자" in text
    assert "일꾼 수" in text
    assert "10:00-11:00" in text
    assert "프테전" in text
