from sc2_replay_slack_bot.manual_analysis import build_manual_analysis
from sc2_replay_slack_bot.prompting import SYSTEM_ANALYSIS_INSTRUCTIONS


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
    assert "가장 큰 차이는 교환 효율" not in text
    assert "체제" in text or "빌드" in text
    assert "조합" in text
    assert "교전" in text or "한타" in text


def test_manual_analysis_stays_compact_for_slack() -> None:
    replay_facts = {
        "map_name": "White Rabbit LE",
        "matchup": "ZvT",
        "game_length": "14:38",
        "winner": "UMBRO",
        "players": [
            {"name": "스탠딩", "race": "Zerg", "result": "Loss"},
            {"name": "UMBRO", "race": "Terran", "result": "Win"},
        ],
        "summary_metrics": {
            "economy": {
                "스탠딩": {"workers_max": 72, "resources_lost": 6100, "resources_killed": 4800, "resource_efficiency_ratio": 0.79},
                "UMBRO": {"workers_max": 66, "resources_lost": 4800, "resources_killed": 6100, "resource_efficiency_ratio": 1.27},
            },
            "upgrades": {
                "스탠딩": ["4:55 저글링 발업", "6:20 맹독충 속업", "8:10 굴파기"],
                "UMBRO": ["5:00 자극제", "6:40 전투방패", "8:30 보병 공1"],
            },
            "tech": {
                "스탠딩": ["6:08 땅굴망", "6:24 땅굴벌레"],
                "UMBRO": ["6:18 의료선", "7:50 공성전차"],
            },
            "composition": {
                "스탠딩": [("저글링", 48), ("맹독충", 18), ("땅굴벌레", 2)],
                "UMBRO": [("해병", 42), ("불곰", 12), ("의료선", 4)],
            },
            "worker_trends": {
                "스탠딩": [
                    {"time": "5:00", "workers": 44, "resources_killed": 250, "resources_lost": 180},
                    {"time": "10:00", "workers": 72, "resources_killed": 1900, "resources_lost": 2600},
                ],
                "UMBRO": [
                    {"time": "5:00", "workers": 38, "resources_killed": 180, "resources_lost": 250},
                    {"time": "10:00", "workers": 66, "resources_killed": 2600, "resources_lost": 1900},
                ],
            },
            "combat_swings": [
                {"window": "8:00-9:00", "winner": "UMBRO", "resource_delta": 900},
            ],
        },
    }

    text = build_manual_analysis(replay_facts, guide_context="")

    non_empty_lines = [line for line in text.splitlines() if line.strip()]
    assert len(non_empty_lines) <= 11
    assert text.count("자원 효율") <= 1
    assert text.count("핵심 피드백 3개") == 1


def test_system_analysis_instructions_require_compact_output() -> None:
    assert "전체 분량" in SYSTEM_ANALYSIS_INSTRUCTIONS
    assert "1~2문장" in SYSTEM_ANALYSIS_INSTRUCTIONS
    assert "한 문장" in SYSTEM_ANALYSIS_INSTRUCTIONS
