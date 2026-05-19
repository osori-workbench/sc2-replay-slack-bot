from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    replay_dir: Path
    state_path: Path
    guides_dir: Path
    slack_webhook_url: str
    analyzer_mode: str
    llm_api_key: str
    llm_api_base_url: str
    llm_model: str


def load_config() -> AppConfig:
    load_dotenv()
    project_dir = Path(__file__).resolve().parents[2]
    replay_dir = Path(os.getenv("REPLAY_DIR", project_dir / "sample_replays"))
    state_path = Path(os.getenv("STATE_PATH", project_dir / "state" / "processed_replays.json"))
    guides_dir = Path(os.getenv("GUIDES_DIR", project_dir / "docs" / "guides"))
    return AppConfig(
        replay_dir=replay_dir,
        state_path=state_path,
        guides_dir=guides_dir,
        slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL", ""),
        analyzer_mode=os.getenv("ANALYZER_MODE", "heuristic").strip().lower(),
        llm_api_key=os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", "")),
        llm_api_base_url=os.getenv("LLM_API_BASE_URL", os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")),
        llm_model=os.getenv("LLM_MODEL", os.getenv("OPENAI_MODEL", "gpt-4.1-mini")),
    )
