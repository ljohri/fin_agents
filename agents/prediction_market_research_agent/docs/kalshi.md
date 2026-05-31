# Kalshi API

Official docs: [docs.kalshi.com](https://docs.kalshi.com/welcome)

This agent accesses Kalshi through **predmarket** (`KalshiRest.fetch_contracts`). See [Architecture](./README.md).

## Environments

| Environment | Base URL |
|-------------|----------|
| Production | `https://api.elections.kalshi.com/trade-api/v2` |
| Demo | `https://demo-api.kalshi.co/trade-api/v2` |

## Authentication

Authenticated requests require three headers:

- `KALSHI-ACCESS-KEY` — API key ID
- `KALSHI-ACCESS-TIMESTAMP` — Unix time in milliseconds
- `KALSHI-ACCESS-SIGNATURE` — RSA-PSS signature of `timestamp + method + path` (path only, no query string)

Generate keys in the Kalshi account settings. Use the demo environment for integration testing.

## Endpoints used by this agent

| Endpoint | Auth | Purpose |
|----------|------|---------|
| `GET /markets` | No | List markets (filter by `status`, `series_ticker`, etc.) |
| `GET /markets/{ticker}` | No | Single market details |
| `GET /markets/{ticker}/orderbook` | No | Yes/no bid ladder |
| `GET /events` | No | Event metadata and grouping |

## Price format

Kalshi returns prices in **cents** (0–100) and **dollar strings** (e.g. `yes_bid_dollars`). The client normalizes to a 0–1 probability for `yes_price`.

## Rate limits

See [Rate Limits](https://docs.kalshi.com/getting_started/rate_limits) in the official docs. Prefer pagination cursors over large single-page requests.
