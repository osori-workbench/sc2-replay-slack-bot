from pathlib import Path

from sc2_replay_slack_bot.guide_context import load_guide_context


def test_load_guide_context_returns_matchup_aware_file_reference_instructions(tmp_path: Path) -> None:
    guides_dir = tmp_path / "guides"
    guides_dir.mkdir()
    (guides_dir / "zerg.md").write_text("# ZvZ\n" + "z" * 300, encoding="utf-8")
    (guides_dir / "terran.md").write_text("# TvZ\n" + "t" * 300, encoding="utf-8")
    (guides_dir / "korean-reference-notes.md").write_text("# notes", encoding="utf-8")

    replay_facts = {
        "matchup": "ZvT",
        "players": [
            {"name": "Alpha", "race": "Zerg"},
            {"name": "Bravo", "race": "Terran"},
        ],
    }

    text = load_guide_context(guides_dir, replay_facts=replay_facts)

    assert "Read these local guide files" in text
    assert str(guides_dir / "zerg.md") in text
    assert str(guides_dir / "terran.md") in text
    assert str(guides_dir / "korean-reference-notes.md") in text
    assert "TvZ" not in text
    assert len(text) <= 4000


def test_missing_guide_directory_returns_empty_string(tmp_path: Path) -> None:
    text = load_guide_context(tmp_path / "missing")

    assert text == ""
