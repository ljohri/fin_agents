## Polymarket API (this agent)

Official docs: [docs.polymarket.com](https://docs.polymarket.com/quickstart)

This agent uses **predmarket** for Gamma REST (`PolymarketRest.fetch_contracts`) and a **custom CLOB client** for live midpoints. See [Architecture](./README.md).

## Gamma API (metadata)

Base URL: `https://gamma-api.polymarket.com`

No authentication required for read-only access.

| Endpoint | Purpose |
|----------|---------|
| `GET /markets` | List markets (`active`, `closed`, `limit`, etc.) |
| `GET /events` | Events with nested markets |
| `GET /markets?slug={slug}` | Lookup by slug |

**Note:** `outcomePrices` on Gamma can lag the live order book. Use CLOB midpoints for current pricing.

## CLOB API (order book & trading)

Base URL: `https://clob.polymarket.com`

| Endpoint | Auth | Purpose |
|----------|------|---------|
| `GET /book?token_id={id}` | No | Full L2 order book |
| `GET /midpoint?token_id={id}` | No | Current midpoint price |
| `POST /order` | Yes (wallet) | Place orders |

Token IDs come from the `clobTokenIds` field on Gamma market objects (index 0 = Yes, 1 = No).

## Data API (historical)

Base URL: `https://data-api.polymarket.com`

Useful for trade history and user activity; not yet wired in this agent.

## Authentication for trading

CLOB write operations use wallet-derived API credentials (L1 → L2). Not required for research-only market data fetching.
