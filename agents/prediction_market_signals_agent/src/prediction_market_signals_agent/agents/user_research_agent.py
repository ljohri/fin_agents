import json
from pathlib import Path

import yaml
from fin_agents_common.common.config import load_yaml_config
from fin_agents_common.observability.decorators import trace_agent

from prediction_market_signals_agent.config import AgentSettings
from prediction_market_signals_agent.schemas.user_research import UserResearchContext


@trace_agent("prediction_market.user_research")
def load_user_research(settings: AgentSettings) -> UserResearchContext:
    d = settings.user_research_dir
    ctx = UserResearchContext()
    view_path = d / "user_view.md"
    if view_path.exists():
        ctx.user_view = view_path.read_text(encoding="utf-8")
    notes_dir = d / "notes"
    if notes_dir.exists():
        for p in sorted(notes_dir.glob("*.md")):
            ctx.notes.append(p.read_text(encoding="utf-8"))
    sites_path = d / "sources" / "websites.yaml"
    if sites_path.exists():
        data = yaml.safe_load(sites_path.read_text(encoding="utf-8")) or {}
        ctx.websites = data.get("websites", [])
    ctx.summaries = _optional_llamaindex_summaries(d, ctx)
    settings.intermediate_dir.mkdir(parents=True, exist_ok=True)
    (settings.intermediate_dir / "user_research_context.json").write_text(
        ctx.model_dump_json(indent=2), encoding="utf-8"
    )
    md = ["# User Research Context", "", ctx.user_view, "", "## Notes", *ctx.notes]
    (settings.intermediate_dir / "user_research_context.md").write_text(
        "\n\n".join(md), encoding="utf-8"
    )
    return ctx


def _optional_llamaindex_summaries(research_dir: Path, ctx: UserResearchContext) -> list[str]:
    try:
        from llama_index.core import Document, VectorStoreIndex
    except ImportError:
        return []
    docs = [Document(text=ctx.user_view)] + [Document(text=n) for n in ctx.notes]
    if not docs or not any(d.text.strip() for d in docs):
        return []
    index = VectorStoreIndex.from_documents(docs)
    qe = index.as_query_engine()
    summary = str(qe.query("Summarize the user's macro and political views for prediction market research."))
    return [summary]
