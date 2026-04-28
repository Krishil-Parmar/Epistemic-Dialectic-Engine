from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, model_validator


class ContextSignal(str, Enum):
    HOSTILE_COUNTERPARTY = "HOSTILE_COUNTERPARTY"
    FRAUD_OR_BREACH = "FRAUD_OR_BREACH"
    SAFETY_CRITICAL = "SAFETY_CRITICAL"
    POWER_ASYMMETRY_AGAINST_USER = "POWER_ASYMMETRY_AGAINST_USER"
    REGULATORY_OR_LEGAL_EXPOSURE = "REGULATORY_OR_LEGAL_EXPOSURE"


class DetectedSignal(BaseModel):
    signal: ContextSignal
    confidence: float
    evidence: str


ALL_16_CELLS = [
    f"({i}, {s})"
    for i in ["Transactional", "Reciprocal", "Collaborative", "Co-Evolutionary"]
    for s in ["Individual", "Relational", "Systemic", "Universal"]
]


class MindsetClassification(BaseModel):
    top_interaction: str
    top_scope: str
    confidence: float
    justification: str
    clarification_needed: bool
    clarification_question: Optional[str] = None
    cell_probabilities: dict[str, float] = {}
    context_signals: list[DetectedSignal] = []

    @model_validator(mode="after")
    def validate_cell_probabilities(self) -> "MindsetClassification":
        if not self.cell_probabilities:
            return self
        total = sum(self.cell_probabilities.values())
        if abs(total - 1.0) > 0.05:
            factor = 1.0 / total if total > 0 else 0
            self.cell_probabilities = {
                k: round(v * factor, 4) for k, v in self.cell_probabilities.items()
            }
        return self


class ElevationDecision(BaseModel):
    current_interaction: str
    current_scope: str
    target_interaction: str
    target_scope: str
    decision_type: Literal["elevate", "stay", "horizontal", "deepen"]
    rationale: str
    pre_mortem_priority: Literal["downside", "upside", "pivot", "all"]


class PreMortemAnalysis(BaseModel):
    downside_scenario: str
    downside_safeguards: list[str]
    upside_scenario: str
    flywheel_logic: Optional[str] = None
    pivot_scenario: str
    robustness_check: str


class DraftResponse(BaseModel):
    response_text: str
    target_interaction_expressed: str
    target_scope_expressed: str
    pre_mortem_outputs: PreMortemAnalysis
    safeguards_included: list[str]


class CritiqueResult(BaseModel):
    passed: bool
    target_cell_match_score: float
    pre_mortem_completeness_score: float
    instruction_adherence_score: float
    issues: list[str]
    refined_response: Optional[str] = None
