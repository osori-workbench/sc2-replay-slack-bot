from types import SimpleNamespace

from sc2_replay_slack_bot.parser import replay_to_facts


class FakeTeam:
    def __init__(self, number, result, players):
        self.number = number
        self.result = result
        self.players = players


class FakePlayer:
    def __init__(self, name, pick_race, play_race, avg_apm, region="kr"):
        self.name = name
        self.pick_race = pick_race
        self.play_race = play_race
        self.avg_apm = avg_apm
        self.region = region
        self.result = None
        self.uid = None
        self.url = None
        self.units = []


def test_replay_to_facts_includes_replay_metadata_for_hermes_context() -> None:
    alpha = FakePlayer("Alpha", "Protoss", "Protoss", 200)
    bravo = FakePlayer("Bravo", "Terran", "Terran", 180)
    replay = SimpleNamespace(
        filename="sample.SC2Replay",
        map_name="Abyssal Reef",
        game_length=SimpleNamespace(seconds=321),
        date="2026-05-19",
        real_type="1v1",
        type="1v1",
        category="Ladder",
        expansion="LotV",
        release_string="5.0.14",
        speed="Faster",
        gateway="kr",
        region="kr",
        is_ladder=True,
        build=12345,
        teams=[
            FakeTeam(1, "Win", [alpha]),
            FakeTeam(2, "Loss", [bravo]),
        ],
        players=[alpha, bravo],
        observers=[],
    )

    facts = replay_to_facts(replay)

    assert facts["matchup"] == "PvT"
    assert facts["replay_metadata"]["release_string"] == "5.0.14"
    assert facts["replay_metadata"]["gateway"] == "kr"
    assert facts["replay_metadata"]["is_ladder"] is True
    assert facts["replay_metadata"]["teams"][0]["players"][0]["name"] == "Alpha"
    assert facts["replay_metadata"]["players"][1]["play_race"] == "Terran"
