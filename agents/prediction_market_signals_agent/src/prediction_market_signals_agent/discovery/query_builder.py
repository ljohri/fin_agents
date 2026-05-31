def build_search_queries(topic: str, category: str | None = None) -> list[str]:
    queries = [topic]
    if category:
        queries.append(f"{category} {topic}")
    return queries
