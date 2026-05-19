from pathlib import Path


def test_korean_reference_markdown_exists_and_mentions_sources() -> None:
    path = Path('/Users/osori/workbench/sc2-replay-slack-bot/docs/guides/korean-reference-notes.md')
    text = path.read_text(encoding='utf-8')

    assert '나무위키' in text
    assert '주의' in text
    assert '프로토스' in text
    assert '테란' in text
    assert '저그' in text
