#!/usr/bin/env python3
"""Run the prediction market signals pipeline."""

import argparse
import shutil
import sys
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = AGENT_ROOT.parent.parent
sys.path.insert(0, str(AGENT_ROOT / "src"))

from prediction_market_signals_agent.config import get_settings
from prediction_market_signals_agent.pipeline.run_signals_pipeline import run_pipeline_sync
from prediction_market_signals_agent.pipeline.state import PipelineState


def main() -> int:
    parser = argparse.ArgumentParser(description="Prediction market signals pipeline")
    parser.add_argument("--topics", default=str(AGENT_ROOT / "config/prediction_market_topics.yaml"))
    parser.add_argument("--user-research-dir", default=str(AGENT_ROOT / "data/user_research"))
    parser.add_argument("--output", default=str(AGENT_ROOT / "data/reports/pred_market_sights.md"))
    parser.add_argument("--venues", nargs="+", default=["kalshi", "polymarket"])
    parser.add_argument("--max-markets-per-topic", type=int, default=10)
    parser.add_argument("--offline-demo", action="store_true")
    parser.add_argument("--skip-llm", action="store_true")
    parser.add_argument("--skip-user-research", action="store_true")
    parser.add_argument("--write-intermediate", action="store_true")
    parser.add_argument("--observability-enabled", action="store_true")
    parser.add_argument("--llm-mode", choices=["local_library", "proxy"], default="local_library")
    parser.add_argument("--copy-to-root", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    settings.user_research_dir = Path(args.user_research_dir)
    output = Path(args.output)

    state = PipelineState(
        offline_demo=args.offline_demo,
        skip_llm=args.skip_llm or args.offline_demo,
        skip_user_research=args.skip_user_research,
    )

    result = run_pipeline_sync(
        venues=args.venues,
        max_markets_per_topic=args.max_markets_per_topic,
        settings=settings,
        state=state,
        output=output,
        observability_enabled=args.observability_enabled,
    )

    print(f"Report written to {result.report_path}")
    print(f"Signals: {len(result.signals)} | Markets: {len(result.markets)}")

    if args.copy_to_root:
        dest = REPO_ROOT / "pred_market_sights.md"
        shutil.copy(output, dest)
        print(f"Copied to {dest}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
