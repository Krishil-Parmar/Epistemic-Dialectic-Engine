"""Bug 2 regression tests: schema consistency for MindsetClassification."""

import pytest

from ede.schemas import (
    MindsetClassification,
    ALL_16_CELLS,
    CritiqueResult,
    DetectedSignal,
    ContextSignal,
)


def _uniform_probabilities() -> dict[str, float]:
    return {cell: 1.0 / 16 for cell in ALL_16_CELLS}


def test_valid_classification_constructs():
    mc = MindsetClassification(
        top_interaction="Transactional",
        top_scope="Individual",
        confidence=0.85,
        justification="test",
        clarification_needed=False,
        cell_probabilities=_uniform_probabilities(),
    )
    assert abs(sum(mc.cell_probabilities.values()) - 1.0) < 0.01


def test_probabilities_auto_normalized():
    """If probabilities don't sum to 1.0, the validator normalizes them."""
    probs = {cell: 0.1 for cell in ALL_16_CELLS}  # sum = 1.6
    mc = MindsetClassification(
        top_interaction="Transactional",
        top_scope="Individual",
        confidence=0.85,
        justification="test",
        clarification_needed=False,
        cell_probabilities=probs,
    )
    assert abs(sum(mc.cell_probabilities.values()) - 1.0) < 0.01


def test_clarification_still_has_probabilities():
    """Bug 2: Even with clarification_needed=true, probabilities must be valid."""
    mc = MindsetClassification(
        top_interaction="Transactional",
        top_scope="Individual",
        confidence=0.4,
        justification="too short to classify",
        clarification_needed=True,
        clarification_question="Could you provide more context about the situation?",
        cell_probabilities=_uniform_probabilities(),
    )
    assert mc.clarification_needed is True
    assert len(mc.cell_probabilities) == 16
    assert abs(sum(mc.cell_probabilities.values()) - 1.0) < 0.01


def test_empty_probabilities_allowed_but_flagged():
    """Empty dict is tolerated at construction (LLM may return it) but should be caught by pipeline."""
    mc = MindsetClassification(
        top_interaction="Transactional",
        top_scope="Individual",
        confidence=0.4,
        justification="test",
        clarification_needed=True,
        cell_probabilities={},
    )
    assert mc.cell_probabilities == {}


def test_context_signals_construction():
    signals = [
        DetectedSignal(
            signal=ContextSignal.FRAUD_OR_BREACH,
            confidence=0.9,
            evidence="partner stealing clients",
        )
    ]
    mc = MindsetClassification(
        top_interaction="Transactional",
        top_scope="Relational",
        confidence=0.85,
        justification="test",
        clarification_needed=False,
        context_signals=signals,
    )
    assert len(mc.context_signals) == 1
    assert mc.context_signals[0].signal == ContextSignal.FRAUD_OR_BREACH


def test_critique_result_has_instruction_adherence():
    """Bug 3: CritiqueResult must include instruction_adherence_score."""
    cr = CritiqueResult(
        passed=True,
        target_cell_match_score=0.85,
        pre_mortem_completeness_score=0.90,
        instruction_adherence_score=0.80,
        issues=[],
    )
    assert cr.instruction_adherence_score == 0.80
