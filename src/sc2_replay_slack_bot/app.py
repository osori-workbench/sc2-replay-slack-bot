from __future__ import annotations

import argparse
import json
import logging

import sc2reader

from .config import load_config
from .finder import find_replay_files
from .focus_player import detect_focus_player
from .guide_context import load_guide_context, select_guide_files
from .llm import LLMClient
from .manual_analysis import build_manual_analysis, extract_summary_metrics
from .parser import replay_to_facts
from .prompting import build_analysis_context, build_analysis_prompt
from .replay_store import ReplayStore
from .slack import build_slack_text, post_to_slack

logger = logging.getLogger(__name__)


def run_once(dry_run: bool = False, max_files: int = 10) -> list[dict]:
    config = load_config()
    config.replay_dir.mkdir(parents=True, exist_ok=True)
    store = ReplayStore(config.state_path)
    llm = LLMClient(
        api_key=config.llm_api_key,
        base_url=config.llm_api_base_url,
        model=config.llm_model,
    )

    processed: list[dict] = []
    for replay_path in find_replay_files(config.replay_dir, min_mtime=config.min_replay_mtime)[:max_files]:
        try:
            status = store.classify(replay_path)
        except OSError as exc:
            logger.warning("Skipping unreadable replay during hashing %s: %s", replay_path, exc)
            continue
        if not status.is_new:
            continue

        try:
            replay = sc2reader.load_replay(str(replay_path), load_level=4)
            facts = replay_to_facts(replay)
            facts["replay_path"] = str(replay_path)
            facts["sha256"] = status.sha256
            facts["summary_metrics"] = extract_summary_metrics(replay)
            focus_player = detect_focus_player(replay_path, facts)
            guide_context = load_guide_context(config.guides_dir, replay_facts=facts)
            guide_file_paths = select_guide_files(config.guides_dir, replay_facts=facts)

            if config.analyzer_mode == "manual":
                analysis = build_manual_analysis(facts, guide_context=guide_context)
            else:
                prompt = build_analysis_prompt(facts, guide_context=guide_context, focus_player=focus_player)
                context = build_analysis_context(
                    facts,
                    guide_context=guide_context,
                    guide_file_paths=guide_file_paths,
                    focus_player=focus_player,
                )
                analysis = llm.analyze(prompt, context=context)

            slack_text = build_slack_text(facts, analysis, replay_name=replay_path.name)

            if not dry_run:
                if not config.slack_webhook_url:
                    raise ValueError("SLACK_WEBHOOK_URL is required unless --dry-run is used")
                post_to_slack(config.slack_webhook_url, slack_text)

            processed.append(
                {
                    "replay": replay_path.name,
                    "status": status.reason,
                    "facts": facts,
                    "analysis": analysis,
                    "slack_text": slack_text,
                }
            )
        except OSError as exc:
            logger.warning("Skipping unreadable replay %s: %s", replay_path, exc)
            continue
    return processed


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze new SC2 replay files and post summaries to Slack.")
    parser.add_argument("--dry-run", action="store_true", help="Analyze replays but do not send to Slack")
    parser.add_argument("--max-files", type=int, default=10, help="Maximum number of replay files to process")
    args = parser.parse_args()

    results = run_once(dry_run=args.dry_run, max_files=args.max_files)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
