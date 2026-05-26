from types import SimpleNamespace

from sc2_replay_slack_bot.manual_analysis import extract_summary_metrics


PlayerStatsEvent = type("PlayerStatsEvent", (), {})
UpgradeCompleteEvent = type("UpgradeCompleteEvent", (), {})
UnitBornEvent = type("UnitBornEvent", (), {})
UnitDoneEvent = type("UnitDoneEvent", (), {})
UnitInitEvent = type("UnitInitEvent", (), {})
UnitDiedEvent = type("UnitDiedEvent", (), {})


class FakePlayer:
    def __init__(self, name: str, race: str, pid: int, units: list[SimpleNamespace]):
        self.name = name
        self.play_race = race
        self.pid = pid
        self.units = units


def _stats_event(pid: int, second: int, workers: int, killed: int, lost: int, food_used: int, food_made: int):
    event = PlayerStatsEvent()
    event.pid = pid
    event.second = second
    event.workers_active_count = workers
    event.resources_killed = killed
    event.resources_lost = lost
    event.food_used = food_used
    event.food_made = food_made
    return event


def _upgrade_event(player, second: int, name: str):
    event = UpgradeCompleteEvent()
    event.player = player
    event.second = second
    event.upgrade_type_name = name
    return event


def _unit_event(event_cls, owner, second: int, name: str):
    event = event_cls()
    event.second = second
    event.unit = SimpleNamespace(owner=owner, name=name)
    return event


def _death_event(second: int, killing_player, minerals: int, vespene: int):
    event = UnitDiedEvent()
    event.second = second
    event.killing_player = killing_player
    event.unit = SimpleNamespace(minerals=minerals, vespene=vespene)
    return event


def test_extract_summary_metrics_collects_worker_trends_composition_and_combat_swings() -> None:
    alpha = FakePlayer(
        name="Alpha",
        race="Protoss",
        pid=1,
        units=[SimpleNamespace(name="Stalker"), SimpleNamespace(name="Stalker"), SimpleNamespace(name="Zealot")],
    )
    bravo = FakePlayer(
        name="Bravo",
        race="Terran",
        pid=2,
        units=[SimpleNamespace(name="Marine"), SimpleNamespace(name="Marine"), SimpleNamespace(name="Marauder")],
    )
    replay = SimpleNamespace(
        players=[alpha, bravo],
        speed="Normal",
        tracker_events=[
            _stats_event(pid=1, second=120, workers=32, killed=0, lost=100, food_used=40, food_made=46),
            _stats_event(pid=2, second=120, workers=30, killed=100, lost=0, food_used=38, food_made=46),
            _stats_event(pid=1, second=360, workers=48, killed=800, lost=300, food_used=82, food_made=94),
            _stats_event(pid=2, second=360, workers=42, killed=300, lost=800, food_used=70, food_made=86),
            _stats_event(pid=1, second=600, workers=61, killed=1600, lost=700, food_used=132, food_made=150),
            _stats_event(pid=2, second=600, workers=50, killed=700, lost=1600, food_used=110, food_made=140),
            _upgrade_event(alpha, second=390, name="BlinkTech"),
            _unit_event(UnitDoneEvent, owner=alpha, second=420, name="RoboticsFacility"),
            _unit_event(UnitBornEvent, owner=bravo, second=405, name="Medivac"),
            _death_event(second=390, killing_player=alpha, minerals=225, vespene=100),
            _death_event(second=392, killing_player=alpha, minerals=50, vespene=0),
            _death_event(second=575, killing_player=bravo, minerals=150, vespene=50),
        ],
    )

    metrics = extract_summary_metrics(replay)

    assert metrics["economy"]["Alpha"]["workers_max"] == 61
    assert metrics["economy"]["Alpha"]["resource_efficiency_ratio"] > 2
    assert metrics["worker_trends"]["Alpha"][0]["time"] == "2:00"
    assert metrics["worker_trends"]["Alpha"][-1]["workers"] == 61
    assert metrics["composition"]["Alpha"][0] == ("추적자", 2)
    assert metrics["combat_swings"][0]["winner"] == "Alpha"
    assert metrics["combat_swings"][0]["window"] == "6:00-7:00"
    assert metrics["combat_swings"][0]["resource_delta"] == 375


def test_extract_summary_metrics_converts_faster_tracker_seconds_to_real_time() -> None:
    alpha = FakePlayer(
        name="Alpha",
        race="Protoss",
        pid=1,
        units=[SimpleNamespace(name="Stalker")],
    )
    bravo = FakePlayer(
        name="Bravo",
        race="Terran",
        pid=2,
        units=[SimpleNamespace(name="Marine")],
    )
    replay = SimpleNamespace(
        players=[alpha, bravo],
        speed="Faster",
        tracker_events=[
            _stats_event(pid=1, second=84, workers=13, killed=0, lost=0, food_used=13, food_made=15),
            _stats_event(pid=2, second=84, workers=13, killed=0, lost=0, food_used=13, food_made=15),
            _upgrade_event(alpha, second=840, name="BlinkTech"),
            _unit_event(UnitDoneEvent, owner=alpha, second=980, name="RoboticsFacility"),
            _death_event(second=840, killing_player=alpha, minerals=200, vespene=0),
            _death_event(second=845, killing_player=bravo, minerals=50, vespene=0),
        ],
    )

    metrics = extract_summary_metrics(replay)

    assert metrics["worker_trends"]["Alpha"][0]["time"] == "1:00"
    assert metrics["upgrades"]["Alpha"][0].startswith("10:00 ")
    assert metrics["tech"]["Alpha"][0].startswith("11:40 ")
    assert metrics["combat_swings"][0]["window"] == "10:00-11:00"


def test_extract_summary_metrics_includes_cross_race_signature_tech_and_units() -> None:
    alpha = FakePlayer(
        name="Alpha",
        race="Zerg",
        pid=1,
        units=[
            SimpleNamespace(name="Roach"),
            SimpleNamespace(name="Hydralisk"),
            SimpleNamespace(name="NydusWorm"),
        ],
    )
    bravo = FakePlayer(
        name="Bravo",
        race="Zerg",
        pid=2,
        units=[
            SimpleNamespace(name="Zergling"),
            SimpleNamespace(name="Mutalisk"),
            SimpleNamespace(name="Mutalisk"),
        ],
    )
    replay = SimpleNamespace(
        players=[alpha, bravo],
        speed="Faster",
        tracker_events=[
            _stats_event(pid=1, second=84, workers=13, killed=0, lost=0, food_used=13, food_made=15),
            _stats_event(pid=2, second=84, workers=13, killed=0, lost=0, food_used=13, food_made=15),
            _unit_event(UnitInitEvent, owner=bravo, second=437, name="Spire"),
            _unit_event(UnitDoneEvent, owner=bravo, second=529, name="Spire"),
            _unit_event(UnitBornEvent, owner=bravo, second=563, name="Mutalisk"),
            _unit_event(UnitInitEvent, owner=alpha, second=465, name="NydusNetwork"),
            _unit_event(UnitDoneEvent, owner=alpha, second=515, name="NydusNetwork"),
            _unit_event(UnitBornEvent, owner=alpha, second=538, name="NydusWorm"),
        ],
    )

    metrics = extract_summary_metrics(replay)

    assert any("둥지탑" in item for item in metrics["tech"]["Bravo"])
    assert any("땅굴망" in item for item in metrics["tech"]["Alpha"])
    assert any("뮤탈리스크" in item for item in metrics["signature_transitions"]["Bravo"])
    assert any("땅굴벌레" in item for item in metrics["signature_transitions"]["Alpha"])
    assert any(name == "뮤탈리스크" for name, _ in metrics["signature_units"]["Bravo"])
    assert any(name == "땅굴벌레" for name, _ in metrics["signature_units"]["Alpha"])


def test_extract_summary_metrics_matches_lowercase_upgrade_names_from_real_zerg_replays() -> None:
    alpha = FakePlayer(
        name="Alpha",
        race="Zerg",
        pid=1,
        units=[SimpleNamespace(name="Zergling")],
    )
    bravo = FakePlayer(
        name="Bravo",
        race="Terran",
        pid=2,
        units=[SimpleNamespace(name="Marine")],
    )
    replay = SimpleNamespace(
        players=[alpha, bravo],
        speed="Normal",
        tracker_events=[
            _stats_event(pid=1, second=120, workers=32, killed=0, lost=0, food_used=40, food_made=46),
            _stats_event(pid=2, second=120, workers=30, killed=0, lost=0, food_used=38, food_made=46),
            _upgrade_event(alpha, second=294, name="zerglingmovementspeed"),
        ],
    )

    metrics = extract_summary_metrics(replay)

    assert metrics["upgrades"]["Alpha"] == ["4:54 저글링 발업"]
