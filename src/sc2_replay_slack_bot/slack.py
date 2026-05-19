from __future__ import annotations

from pathlib import Path

import requests


def build_slack_text(replay_facts: dict, analysis: str, replay_name: str) -> str:
    header = (
        f"*SC2 Replay 분석*\n"
        f"- 파일: `{replay_name}`\n"
        f"- 맵: {replay_facts.get('map_name', 'Unknown')}\n"
        f"- 매치업: {replay_facts.get('matchup', 'Unknown')}\n"
        f"- 승자: {replay_facts.get('winner', 'Unknown')}\n"
        f"- 경기 시간: {replay_facts.get('game_length', 'Unknown')}\n"
    )
    return f"{header}\n{analysis.strip()}"


def post_to_slack(webhook_url: str, text: str) -> requests.Response:
    response = requests.post(webhook_url, json={"text": text}, timeout=30)
    response.raise_for_status()
    return response
