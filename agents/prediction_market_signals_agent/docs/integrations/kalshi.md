# Kalshi Integration

Official docs: [docs.kalshi.com](https://docs.kalshi.com/welcome)

This unified agent accesses Kalshi through its internal `market_data.MarketDataClient`, which uses `predmarket` (`KalshiRest.fetch_contracts`) for market metadata and venue-native REST calls for order books.

## Environments

| Environment | Base URL |
|-------------|----------|
| Production | `https://api.elections.kalshi.com/trade-api/v2` |
| Demo | `https://demo-api.kalshi.co/trade-api/v2` |

## Authentication

Public market-data endpoints used by the signal pipeline do not require credentials.

Authenticated requests require three headers:

- `KALSHI-ACCESS-KEY` — API key ID
- `KALSHI-ACCESS-TIMESTAMP` — Unix time in milliseconds
- `KALSHI-ACCESS-SIGNATURE` — RSA-PSS signature of `timestamp + method + path` (path only, no query string)

Authenticated trading endpoints are out of scope for the current research workflow.

## Endpoints Used

| Endpoint | Auth | Purpose |
|----------|------|---------|
| `GET /markets` | No | List markets (via `predmarket`) |
| `GET /markets/{ticker}` | No | Single market details (via `predmarket`) |
| `GET /markets/{ticker}/orderbook` | No | Yes/no bid ladder |
| `GET /events` | No | Event metadata and grouping |

## Price Format

Kalshi returns prices in cents (0-100) and dollar strings such as `yes_bid_dollars`. The agent normalizes prices to 0-1 probabilities before deterministic scoring.

## Rate Limits

See [Rate Limits](https://docs.kalshi.com/getting_started/rate_limits) in the official docs. Prefer pagination cursors over large single-page requests.
