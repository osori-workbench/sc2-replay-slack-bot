from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone

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

MIN_REVIEW_GAME_LENGTH_SECONDS = 60
SKIP_PLAYER_KEYWORDS = ("치터", "인공지능")


def run_once(dry_run: bool = False, max_files: int = 10) -> list[dict]:
    config = load_config()
    config.replay_dir.mkdir(parents=True, exist_ok=True)
    store = ReplayStore(config.state_path)
    llm = LLMClient(
        api_key=config.llm_api_key,
        base_url=config.llm_api_base_url,
        model=config.llm_model,
    )

    pending_reviews: list[dict] = []
    processed: list[dict] = []
    for replay_path in find_replay_files(config.replay_dir, min_mtime=config.min_replay_mtime):
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

            skip_reason = _skip_reason(facts)
            if skip_reason:
                logger.info("Skipping replay review for %s: %s", replay_path.name, skip_reason)
                store.mark_processed(replay_path, status.sha256)
                continue

            pending_reviews.append(
                {
                    "replay_path": replay_path,
                    "status": status,
                    "facts": facts,
                }
            )
        except OSError as exc:
            logger.warning("Skipping unreadable replay %s: %s", replay_path, exc)
            continue
        except Exception:
            logger.exception("Replay preprocessing failed: %s", replay_path)
            continue

    pending_reviews.sort(key=lambda item: _replay_sort_key(item["facts"], item["replay_path"]))

    for item in pending_reviews[:max_files]:
        replay_path = item["replay_path"]
        status = item["status"]
        facts = item["facts"]

        try:
            logger.info("Processing replay: %s (%s)", replay_path.name, status.reason)
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

            slack_text = build_slack_text(facts, analysis, replay_name=replay_path.name, focus_player=focus_player)

            if not dry_run:
                if not config.slack_webhook_url:
                    raise ValueError("SLACK_WEBHOOK_URL is required unless --dry-run is used")
                logger.info("Posting replay analysis to Slack for %s", replay_path.name)
                post_to_slack(config.slack_webhook_url, slack_text)

            store.mark_processed(replay_path, status.sha256)
            logger.info(
                "Finished replay: %s winner=%s focus=%s",
                replay_path.name,
                facts.get("winner") or "unknown",
                (focus_player or {}).get("name", "general") if isinstance(focus_player, dict) else (focus_player or "general"),
            )
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
        except Exception:
            logger.exception("Replay processing failed: %s", replay_path)
            continue
    return processed


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Analyze new SC2 replay files and post summaries to Slack.")
    parser.add_argument("--dry-run", action="store_true", help="Analyze replays but do not send to Slack")
    parser.add_argument("--max-files", type=int, default=10, help="Maximum number of replay files to process")
    args = parser.parse_args()

    results = run_once(dry_run=args.dry_run, max_files=args.max_files)
    if results:
        summary = [
            {
                "replay": item.get("replay"),
                "status": item.get("status"),
                "winner": (item.get("facts") or {}).get("winner"),
            }
            for item in results
        ]
        print(json.dumps(summary, ensure_ascii=False, indent=2))



def _skip_reason(replay_facts: dict) -> str | None:
    is_ladder = replay_facts.get("replay_metadata", {}).get("is_ladder")
    category = str(replay_facts.get("category") or "Unknown")
    if not is_ladder:
        return f"replay was not a ladder game (category={category})"

    if replay_facts.get("game_length_seconds", 0) < MIN_REVIEW_GAME_LENGTH_SECONDS:
        return f"game length was {replay_facts.get('game_length_seconds', 0)} seconds"

    for player in replay_facts.get("players", []) or []:
        name = str(player.get("name") or "")
        for keyword in SKIP_PLAYER_KEYWORDS:
            if keyword in name:
                return f"player name matched filtered keyword '{keyword}': {name}"
    return None


def _replay_sort_key(replay_facts: dict, replay_path) -> tuple[float, str, str]:
    played_at = _parse_played_at(replay_facts.get("played_at"))
    if played_at is not None:
        return (played_at.timestamp(), replay_path.name, str(replay_path.parent))

    try:
        modified_at = replay_path.stat().st_mtime
    except OSError:
        modified_at = float("inf")
    return (modified_at, replay_path.name, str(replay_path.parent))


def _parse_played_at(played_at: object) -> datetime | None:
    if not played_at:
        return None

    text = str(played_at).strip()
    if not text or text == "Unknown":
        return None

    normalized = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


if __name__ == "__main__":
    main()
