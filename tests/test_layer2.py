import json
from pathlib import Path

import pytest

from ede.layers.layer2_policy import ElevationPolicyEngine
from ede.schemas import (
    MindsetClassification,
    DetectedSignal,
    ContextSignal,
)

FIXTURES_PATH = Path(__file__).parent / "fixtures" / "sample_queries.json"


@pytest.fixture
def engine():
    return ElevationPolicyEngine()


@pytest.fixture
def fixtures():
    return json.loads(FIXTURES_PATH.read_text())["queries"]


def _make_classification(
    interaction: str,
    scope: str,
    confidence: float = 0.85,
    context_signals: list[DetectedSignal] | None = None,
) -> MindsetClassification:
    return MindsetClassification(
        top_interaction=interaction,
        top_scope=scope,
        confidence=confidence,
        justification="test",
        clarification_needed=False,
        context_signals=context_signals or [],
    )


def test_elevate_transactional_individual(engine, fixtures):
    q = next(f for f in fixtures if f["id"] == "anchor_q1")
    classification = _make_classification(*q["expected_cell"])
    decision = engine.decide(classification, q["query"])

    assert decision.decision_type == "elevate"
    assert decision.target_interaction == "Reciprocal"
    assert decision.target_scope == "Relational"


def test_elevate_transactional_relational(engine, fixtures):
    q = next(f for f in fixtures if f["id"] == "anchor_q3")
    classification = _make_classification(*q["expected_cell"])
    decision = engine.decide(classification, q["query"])

    assert decision.decision_type == "elevate"
    assert decision.target_interaction == "Reciprocal"
    assert decision.target_scope == "Systemic"


def test_elevate_reciprocal_systemic(engine, fixtures):
    q = next(f for f in fixtures if f["id"] == "boundary_collaborative_systemic")
    classification = _make_classification(*q["expected_cell"])
    decision = engine.decide(classification, q["query"])

    assert decision.decision_type == "elevate"
    assert decision.target_interaction == "Collaborative"
    assert decision.target_scope == "Universal"


def test_stay_override_fraud_keywords(engine, fixtures):
    q = next(f for f in fixtures if f["id"] == "stay_override_fraud")
    classification = _make_classification(*q["expected_cell"])
    decision = engine.decide(classification, q["query"])

    assert decision.decision_type == "stay"
    assert decision.target_interaction == classification.top_interaction
    assert decision.target_scope == classification.top_scope


def test_stay_override_via_context_signals(engine, fixtures):
    """Bug 1: Context signals should trigger stay override even without keyword matches."""
    q = next(f for f in fixtures if f["id"] == "competing_company_breach")
    signals = [
        DetectedSignal(
            signal=ContextSignal.FRAUD_OR_BREACH,
            confidence=0.92,
            evidence="setting up competing company using shared client list",
        ),
        DetectedSignal(
            signal=ContextSignal.HOSTILE_COUNTERPARTY,
            confidence=0.88,
            evidence="secretly competing against the user",
        ),
    ]
    classification = _make_classification(
        *q["expected_cell"], context_signals=signals
    )
    decision = engine.decide(classification, q["query"])

    assert decision.decision_type == "stay"


def test_low_confidence_signals_do_not_trigger_stay(engine):
    """Signals below threshold (0.7) should not trigger stay override."""
    signals = [
        DetectedSignal(
            signal=ContextSignal.FRAUD_OR_BREACH,
            confidence=0.5,
            evidence="ambiguous mention",
        ),
    ]
    classification = _make_classification(
        "Transactional", "Relational", context_signals=signals
    )
    decision = engine.decide(classification, "some neutral query about a business issue")

    assert decision.decision_type == "elevate"


def test_cap_at_level_4_produces_deepen(engine):
    classification = _make_classification("Co-Evolutionary", "Universal")
    decision = engine.decide(classification, "test query")

    assert decision.decision_type == "deepen"
    assert decision.target_interaction == "Co-Evolutionary"
    assert decision.target_scope == "Universal"
    assert decision.pre_mortem_priority == "pivot"


def test_deepen_rationale_is_descriptive(engine):
    """Bug 4: Deepen rationale should not say 'elevate'."""
    classification = _make_classification("Co-Evolutionary", "Universal")
    decision = engine.decide(classification, "test query")

    assert "deepen" in decision.rationale.lower() or "Deepening" in decision.rationale


def test_pre_mortem_priority_low_levels(engine):
    classification = _make_classification("Transactional", "Individual")
    decision = engine.decide(classification, "test query")
    assert decision.pre_mortem_priority == "downside"


def test_pre_mortem_priority_high_levels(engine):
    classification = _make_classification("Collaborative", "Systemic")
    decision = engine.decide(classification, "test query")
    assert decision.pre_mortem_priority == "upside"
