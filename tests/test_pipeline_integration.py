"""
Integration tests for the EDE pipeline.
These tests hit real LLM APIs and require GOOGLE_API_KEY to be set.
Run with: pytest tests/test_pipeline_integration.py -v
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from ede.pipeline import EDEPipeline
from ede.schemas import ALL_16_CELLS

FIXTURES_PATH = Path(__file__).parent / "fixtures" / "sample_queries.json"


@pytest.fixture(scope="module")
def pipeline():
    db_path = tempfile.mktemp(suffix=".sqlite")
    return EDEPipeline(db_path=db_path)


@pytest.fixture
def fixtures():
    return json.loads(FIXTURES_PATH.read_text())["queries"]


def _get_fixture(fixtures, fixture_id):
    return next(f for f in fixtures if f["id"] == fixture_id)


@pytest.mark.slow
def test_anchor_q1_full_pipeline(pipeline, fixtures):
    """Smoke test: full pipeline on anchor query produces valid response."""
    q = _get_fixture(fixtures, "anchor_q1")
    result = asyncio.run(pipeline.run(query=q["query"]))

    assert result["type"] == "response"
    assert len(result["response"]) > 50
    assert result["classification"]["top_interaction"] is not None
    assert result["classification"]["top_scope"] is not None
    assert result["decision"]["decision_type"] in ("elevate", "stay", "horizontal", "deepen")
    assert result["critique"]["instruction_adherence_score"] is not None


@pytest.mark.slow
def test_competing_company_breach_triggers_stay(pipeline, fixtures):
    """Bug 1 regression: semantic context signals should trigger stay override."""
    q = _get_fixture(fixtures, "competing_company_breach")
    result = asyncio.run(pipeline.run(query=q["query"]))

    if result["type"] == "clarification":
        pytest.skip("Classifier requested clarification; cannot test stay override")

    # Check context signals were detected
    signals = result["classification"].get("context_signals", [])
    signal_names = set()
    for s in signals:
        name = s.get("signal", "")
        conf = s.get("confidence", 0)
        if conf >= 0.7:
            signal_names.add(name)

    assert len(signal_names) > 0, (
        f"Expected FRAUD_OR_BREACH or HOSTILE_COUNTERPARTY with confidence >= 0.7, "
        f"got signals: {signals}"
    )
    expected = {"FRAUD_OR_BREACH", "HOSTILE_COUNTERPARTY"}
    assert signal_names & expected, (
        f"Expected at least one of {expected}, got {signal_names}"
    )

    assert result["decision"]["decision_type"] == "stay", (
        f"Expected stay, got {result['decision']['decision_type']}"
    )


@pytest.mark.slow
def test_clarification_schema_integrity(pipeline, fixtures):
    """Bug 2 regression: clarification responses must have valid probability distribution."""
    q = _get_fixture(fixtures, "clarification_cofounder_weird")
    result = asyncio.run(pipeline.run(query=q["query"]))

    assert result["type"] == "clarification"
    classification = result["classification"]
    probs = classification.get("cell_probabilities", {})
    assert len(probs) > 0, "cell_probabilities should not be empty even for clarification"
    total = sum(probs.values())
    assert abs(total - 1.0) < 0.05, f"cell_probabilities sum={total}, expected ~1.0"


@pytest.mark.slow
def test_high_cell_deepen(pipeline, fixtures):
    """Bug 4 regression: user at (Co-Evolutionary, Universal) gets deepen, not elevate."""
    q = _get_fixture(fixtures, "high_cell_deepen")
    result = asyncio.run(pipeline.run(query=q["query"]))

    if result["type"] == "clarification":
        pytest.skip("Classifier requested clarification")

    classification = result["classification"]
    # The query is explicitly Co-Evolutionary/Universal in framing
    assert classification["top_interaction"] in ("Co-Evolutionary", "Collaborative"), (
        f"Expected high interaction level, got {classification['top_interaction']}"
    )

    decision = result["decision"]
    if classification["top_interaction"] == "Co-Evolutionary" and classification["top_scope"] == "Universal":
        assert decision["decision_type"] == "deepen", (
            f"Expected deepen at max cell, got {decision['decision_type']}"
        )
        assert decision["pre_mortem_priority"] == "pivot"
