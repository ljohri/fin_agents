from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class AlgorithmResult(BaseModel):
    name: str
    score: float | None = None
    label: str | None = None
    details: dict = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class SignalAlgorithm(ABC):
    name: str

    @abstractmethod
    def run(self, context: dict) -> AlgorithmResult:
        pass
