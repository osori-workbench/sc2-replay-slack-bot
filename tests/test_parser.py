from types import SimpleNamespace

from sc2_replay_slack_bot.parser import replay_to_facts


class FakeTeam:
    def __init__(self, number, result, players):
        self.number = number
        self.result = result
        self.players = players


class FakePlayer:
    def __init__(self, name, pick_race, play_race, avg_apm):
        self.name = name
        self.pick_race = pick_race
        self.play_race = play_race
        self.avg_apm = avg_apm



def test_replay_to_facts_normalizes_core_fields() -> None:
    replay = SimpleNamespace(
        map_name="Post-Youth",
        game_length=SimpleNamespace(seconds=754),
        date="2026-05-19",
        real_type="1v1",
        category="Ladder",
        expansion="LotV",
        teams=[
            FakeTeam(1, "Win", [FakePlayer("Alpha", "Protoss", "Protoss", 210)]),
            FakeTeam(2, "Loss", [FakePlayer("Bravo", "Terran", "Terran", 180)]),
        ],
    )

    facts = replay_to_facts(replay)

    assert facts["map_name"] == "Post-Youth"
    assert facts["game_length"] == "12:34"
    assert facts["winner"] == "Alpha"
    assert facts["matchup"] == "PvT"
    assert facts["players"][0]["apm"] == 210
