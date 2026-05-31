from pydantic import BaseModel, Field


class UserResearchContext(BaseModel):
    user_view: str = ""
    notes: list[str] = Field(default_factory=list)
    websites: list[dict] = Field(default_factory=list)
    summaries: list[str] = Field(default_factory=list)
