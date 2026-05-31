# Polymarket Integration

Official docs: [docs.polymarket.com](https://docs.polymarket.com/quickstart)

This unified agent uses `predmarket` for Gamma REST metadata (`PolymarketRest.fetch_contracts`) and a custom CLOB client for live midpoints and order books.

## Gamma API (Metadata)

Base URL: `https://gamma-api.polymarket.com`

No authentication is required for read-only access.

| Endpoint | Purpose |
|----------|---------|
| `GET /markets` | List markets (`active`, `closed`, `limit`, etc.) |
| `GET /events` | Events with nested markets |
| `GET /markets?slug={slug}` | Lookup by slug |

`outcomePrices` on Gamma can lag the live order book. The agent therefore enriches Polymarket markets with CLOB midpoints before signal scoring.

## CLOB API (Order Book And Trading)

Base URL: `https://clob.polymarket.com`

| Endpoint | Auth | Purpose |
|----------|------|---------|
| `GET /book?token_id={id}` | No | Full L2 order book |
| `GET /midpoint?token_id={id}` | No | Current midpoint price |
| `POST /order` | Yes (wallet) | Place orders |

Token IDs come from the `clobTokenIds` field on Gamma market objects (index 0 = Yes, 1 = No).

## Data API (Historical)

Base URL: `https://data-api.polymarket.com`

Useful for trade history and user activity; not yet wired into the signal pipeline.

## Authentication For Trading

CLOB write operations use wallet-derived API credentials (L1 to L2). Trading is out of scope for this research-only agent.
