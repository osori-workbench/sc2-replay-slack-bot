from pathlib import Path

from sc2_replay_slack_bot.guide_context import load_guide_context


def test_load_guide_context_combines_markdown_files_with_budget(tmp_path: Path) -> None:
    guides_dir = tmp_path / "guides"
    guides_dir.mkdir()
    (guides_dir / "zerg.md").write_text("# ZvZ\n" + "z" * 300, encoding="utf-8")
    (guides_dir / "terran.md").write_text("# TvZ\n" + "t" * 300, encoding="utf-8")

    text = load_guide_context(guides_dir, max_chars=250)

    assert "BEGIN GUIDE CONTEXT" in text
    assert "zerg.md" in text or "terran.md" in text
    assert len(text) <= 350


def test_missing_guide_directory_returns_empty_string(tmp_path: Path) -> None:
    text = load_guide_context(tmp_path / "missing")

    assert text == ""
