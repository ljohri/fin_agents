import argparse
import json
import sys

from prediction_market_research_agent.agent import PredictionMarketResearchAgent


def _print_markets(result) -> None:
    for market in result.kalshi_markets + result.polymarket_markets:
        price = f"{market.yes_price:.2%}" if market.yes_price is not None else "n/a"
        print(f"[{market.venue.value}] {market.title[:80]}")
        print(f"  id={market.market_id}  yes={price}  vol={market.volume}")
        if market.url:
            print(f"  {market.url}")
        print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prediction market research — Kalshi & Polymarket"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    list_cmd = sub.add_parser("list", help="List open markets from both venues")
    list_cmd.add_argument("--limit", type=int, default=10)

    kalshi_cmd = sub.add_parser("kalshi", help="Fetch a Kalshi market by ticker")
    kalshi_cmd.add_argument("ticker")

    poly_cmd = sub.add_parser("polymarket", help="Fetch a Polymarket market by slug")
    poly_cmd.add_argument("slug")

    json_cmd = sub.add_parser("list-json", help="List markets as JSON")
    json_cmd.add_argument("--limit", type=int, default=10)

    args = parser.parse_args(argv)
    agent = PredictionMarketResearchAgent()

    if args.command == "list":
        result = agent.list_open_markets(limit=args.limit)
        print(f"Found {result.total_count} markets ({len(result.kalshi_markets)} Kalshi, "
              f"{len(result.polymarket_markets)} Polymarket)\n")
        _print_markets(result)
        return 0

    if args.command == "list-json":
        result = agent.list_open_markets(limit=args.limit)
        print(result.model_dump_json(indent=2))
        return 0

    if args.command == "kalshi":
        market = agent.get_kalshi_market(args.ticker)
        print(json.dumps(market.model_dump(mode="json"), indent=2))
        return 0

    if args.command == "polymarket":
        market = agent.get_polymarket_market(args.slug)
        print(json.dumps(market.model_dump(mode="json"), indent=2))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
