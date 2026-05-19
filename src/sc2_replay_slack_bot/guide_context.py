from __future__ import annotations

from pathlib import Path


def load_guide_context(guides_dir: Path, max_chars: int = 8000) -> str:
    guides_dir = Path(guides_dir)
    if not guides_dir.exists():
        return ""

    sections: list[str] = []
    total = 0
    for path in sorted(guides_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        section = f"## {path.name}\n{text}"
        remaining = max_chars - total
        if remaining <= 0:
            break
        section = section[:remaining]
        sections.append(section)
        total += len(section)

    if not sections:
        return ""

    body = "\n\n".join(sections)
    return f"BEGIN GUIDE CONTEXT\n{body}\nEND GUIDE CONTEXT"
