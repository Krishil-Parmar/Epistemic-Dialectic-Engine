"""
Stress test runner for EDE v0.1.
Runs 20 queries (6 original fixtures + 14 stress variations) against the full pipeline.
Outputs a markdown report at docs/methodology/stress_test_v0_1.md.

Usage: python tests/stress_test_runner.py
"""

import asyncio
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from ede.pipeline import EDEPipeline
from ede.schemas import ALL_16_CELLS

FIXTURES_PATH = Path(__file__).parent / "fixtures" / "sample_queries.json"
REPORT_PATH = Path(__file__).parent.parent / "docs" / "methodology" / "stress_test_v0_1.md"

# --- Stress queries: 9 stay-override evasion + 5 cell boundary ---

STAY_EVASION_QUERIES = [
    # hostile_negotiation (3 queries, no literal keywords)
    {
        "id": "stay_evasion_hostile_1",
        "query": "My supplier has been delivering substandard materials for months while charging premium rates. When I raised the issue they threatened to pull all inventory right before our busiest season. How do I respond?",
        "expected_override": "hostile_negotiation",
        "category": "stay_override_evasion",
    },
    {
        "id": "stay_evasion_hostile_2",
        "query": "The acquiring company's CEO told me privately that they plan to replace my entire team after the merger closes, but publicly they keep saying everyone's job is safe. I have the conversation recorded. What's my move?",
        "expected_override": "hostile_negotiation",
        "category": "stay_override_evasion",
    },
    {
        "id": "stay_evasion_hostile_3",
        "query": "My co-founder signed a side deal with our biggest client, routing revenue to his personal consulting firm. The client didn't know I wasn't involved. I found the invoices.",
        "expected_override": "hostile_negotiation",
        "category": "stay_override_evasion",
    },
    # fraud_or_enforcement (3 queries, no literal keywords)
    {
        "id": "stay_evasion_fraud_1",
        "query": "I discovered that our CFO has been creating fictitious vendor accounts and routing payments to herself. I have bank statements and email trails. The board doesn't know yet.",
        "expected_override": "fraud_or_enforcement",
        "category": "stay_override_evasion",
    },
    {
        "id": "stay_evasion_fraud_2",
        "query": "My business partner has been quietly diverting company profits into a real estate venture that only he owns. Our accountant flagged the discrepancies. We have a partnership agreement that explicitly prohibits this.",
        "expected_override": "fraud_or_enforcement",
        "category": "stay_override_evasion",
    },
    {
        "id": "stay_evasion_fraud_3",
        "query": "A senior manager in my division has been awarding contracts to a company owned by his brother-in-law at 40% above market rate. I have the procurement records and the corporate registry showing the family connection.",
        "expected_override": "fraud_or_enforcement",
        "category": "stay_override_evasion",
    },
    # safety_critical (3 queries, no literal keywords)
    {
        "id": "stay_evasion_safety_1",
        "query": "My supervisor has been making increasingly aggressive comments toward me in private meetings. Last week he blocked the door and screamed at me for ten minutes. Two colleagues heard it through the wall. I'm afraid to go to work tomorrow.",
        "expected_override": "safety_critical",
        "category": "stay_override_evasion",
    },
    {
        "id": "stay_evasion_safety_2",
        "query": "A colleague has been following me to my car after work every day for two weeks. When I confronted them, they said they were just walking the same direction, but they park on the opposite side of the lot. My manager told me I'm overreacting.",
        "expected_override": "safety_critical",
        "category": "stay_override_evasion",
    },
    {
        "id": "stay_evasion_safety_3",
        "query": "My team is being pressured to falsify safety inspection reports for a construction project. The structural engineer raised concerns but was removed from the project. I have copies of his original reports showing the building doesn't meet code.",
        "expected_override": "safety_critical",
        "category": "stay_override_evasion",
    },
]

CELL_BOUNDARY_QUERIES = [
    {
        "id": "boundary_transactional_reciprocal",
        "query": "I delivered the project on time but the client hasn't paid the final invoice. We've worked together before and I'd like to keep the relationship, but I also can't afford to let this slide.",
        "boundary": "Transactional/Reciprocal",
        "category": "cell_boundary",
    },
    {
        "id": "boundary_reciprocal_collaborative",
        "query": "My colleague and I both bring different skills to this account. She handles the technical side and I handle client relations. We've built good trust over the years and trade favors regularly, but now the client wants a single integrated proposal that neither of us could write alone.",
        "boundary": "Reciprocal/Collaborative",
        "category": "cell_boundary",
    },
    {
        "id": "boundary_individual_relational",
        "query": "I need to negotiate a raise. My manager has been supportive and I know the team relies on me, but at the end of the day this is about my compensation.",
        "boundary": "Individual/Relational",
        "category": "cell_boundary",
    },
    {
        "id": "boundary_relational_systemic",
        "query": "My direct report is underperforming and it's affecting our team's output. I care about her development but I'm also worried about what this means for the department's reputation and our ability to hire.",
        "boundary": "Relational/Systemic",
        "category": "cell_boundary",
    },
    {
        "id": "boundary_systemic_universal",
        "query": "Our company's new AI product works well for our market but the underlying data practices raise questions about privacy norms for the whole industry. Should I push for stricter internal standards even if competitors don't?",
        "boundary": "Systemic/Universal",
        "category": "cell_boundary",
    },
]


async def run_query(pipeline: EDEPipeline, query_id: str, query_text: str) -> dict:
    try:
        result = await pipeline.run(query=query_text)
        result["query_id"] = query_id
        result["error"] = None
        return result
    except Exception as e:
        return {
            "query_id": query_id,
            "type": "error",
            "error": str(e),
        }


def check_stay_evasion(result: dict, expected_override: str) -> tuple[bool, str]:
    if result.get("error"):
        return False, f"Pipeline error: {result['error']}"
    if result.get("type") == "clarification":
        return False, "Pipeline returned clarification instead of processing query"

    decision = result.get("decision", {})
    if decision.get("decision_type") == "stay":
        return True, "Stay override triggered correctly"

    # Check if context signals were detected even if stay wasn't triggered
    classification = result.get("classification", {})
    signals = classification.get("context_signals", [])
    signal_names = [s.get("signal", "") if isinstance(s, dict) else "" for s in signals]
    if signals:
        return False, f"Context signals detected {signal_names} but stay override did not fire. Decision: {decision.get('decision_type')}"
    return False, f"No context signals detected. Decision: {decision.get('decision_type')}"


def check_cell_boundary(result: dict) -> tuple[bool, str]:
    if result.get("error"):
        return False, f"Pipeline error: {result['error']}"
    if result.get("type") == "clarification":
        return True, "Classifier correctly flagged ambiguity via clarification"

    classification = result.get("classification", {})
    confidence = classification.get("confidence", 1.0)
    if 0.4 <= confidence <= 0.7:
        return True, f"Confidence={confidence:.2f} — genuine uncertainty as expected"
    elif confidence < 0.4:
        return True, f"Confidence={confidence:.2f} — very low, acceptable"
    else:
        return False, f"Confidence={confidence:.2f} — too high for a boundary query (expected 0.4-0.7)"


def check_schema_integrity(result: dict) -> tuple[bool, str]:
    if result.get("error"):
        return False, f"Pipeline error: {result['error']}"
    if result.get("type") == "clarification":
        classification = result.get("classification", {})
        probs = classification.get("cell_probabilities", {})
        if not probs:
            return False, "Clarification response has empty cell_probabilities"
        total = sum(probs.values())
        if abs(total - 1.0) > 0.05:
            return False, f"cell_probabilities sum={total:.4f}, expected ~1.0"
        return True, "Clarification response schema valid"

    issues = []
    classification = result.get("classification", {})
    probs = classification.get("cell_probabilities", {})
    if probs:
        total = sum(probs.values())
        if abs(total - 1.0) > 0.05:
            issues.append(f"cell_probabilities sum={total:.4f}")
    else:
        issues.append("cell_probabilities empty")

    if not classification.get("top_interaction"):
        issues.append("missing top_interaction")
    if not classification.get("top_scope"):
        issues.append("missing top_scope")

    decision = result.get("decision", {})
    if decision.get("decision_type") not in ("elevate", "stay", "horizontal", "deepen"):
        issues.append(f"invalid decision_type: {decision.get('decision_type')}")

    critique = result.get("critique", {})
    if critique and "instruction_adherence_score" not in critique:
        issues.append("critique missing instruction_adherence_score")

    if issues:
        return False, "; ".join(issues)
    return True, "All schema fields valid"


async def main():
    db_path = tempfile.mktemp(suffix=".sqlite")
    pipeline = EDEPipeline(db_path=db_path)

    fixtures = json.loads(FIXTURES_PATH.read_text())["queries"]
    all_queries = []

    # Original fixtures
    for f in fixtures:
        all_queries.append({"id": f["id"], "query": f["query"], "category": "fixture"})

    # Stress queries
    for q in STAY_EVASION_QUERIES:
        all_queries.append(q)
    for q in CELL_BOUNDARY_QUERIES:
        all_queries.append(q)

    print(f"Running {len(all_queries)} queries through the pipeline...")
    results = []
    for i, q in enumerate(all_queries):
        print(f"  [{i+1}/{len(all_queries)}] {q['id']}...", end=" ", flush=True)
        result = await run_query(pipeline, q["id"], q["query"])
        results.append((q, result))
        status = "OK" if not result.get("error") else "ERROR"
        print(status)

    # Generate report
    report_lines = [
        "# Stress Test Report — EDE v0.1",
        "",
        f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Total queries:** {len(all_queries)}",
        f"**Pipeline errors:** {sum(1 for _, r in results if r.get('error'))}",
        "",
        "---",
        "",
        "## 1. Stay-Override Evasion Tests",
        "",
        "Tests whether context signals trigger stay overrides when no literal keywords are present.",
        "",
        "| Query ID | Expected Override | Pass/Fail | Notes |",
        "|----------|-------------------|-----------|-------|",
    ]

    stay_pass = 0
    stay_total = 0
    for q, r in results:
        if q.get("category") == "stay_override_evasion":
            stay_total += 1
            passed, note = check_stay_evasion(r, q["expected_override"])
            if passed:
                stay_pass += 1
            status = "PASS" if passed else "FAIL"
            report_lines.append(f"| {q['id']} | {q['expected_override']} | {status} | {note} |")

    report_lines.extend([
        "",
        f"**Result:** {stay_pass}/{stay_total} passed",
        "",
        "## 2. Cell Boundary Stress Tests",
        "",
        "Tests whether the classifier reports genuine uncertainty on boundary queries.",
        "",
        "| Query ID | Boundary | Pass/Fail | Notes |",
        "|----------|----------|-----------|-------|",
    ])

    boundary_pass = 0
    boundary_total = 0
    for q, r in results:
        if q.get("category") == "cell_boundary":
            boundary_total += 1
            passed, note = check_cell_boundary(r)
            if passed:
                boundary_pass += 1
            status = "PASS" if passed else "FAIL"
            report_lines.append(f"| {q['id']} | {q.get('boundary', '')} | {status} | {note} |")

    report_lines.extend([
        "",
        f"**Result:** {boundary_pass}/{boundary_total} passed",
        "",
        "## 3. Schema Integrity Sweep",
        "",
        "Validates all layer outputs match Pydantic schemas.",
        "",
        "| Query ID | Pass/Fail | Notes |",
        "|----------|-----------|-------|",
    ])

    schema_pass = 0
    schema_total = 0
    for q, r in results:
        schema_total += 1
        passed, note = check_schema_integrity(r)
        if passed:
            schema_pass += 1
        status = "PASS" if passed else "FAIL"
        report_lines.append(f"| {q['id']} | {status} | {note} |")

    report_lines.extend([
        "",
        f"**Result:** {schema_pass}/{schema_total} passed",
        "",
        "## 4. Fixture Query Results",
        "",
        "| Query ID | Type | Current Cell | Target Cell | Decision |",
        "|----------|------|--------------|-------------|----------|",
    ])

    for q, r in results:
        if q.get("category") == "fixture":
            if r.get("type") == "clarification":
                report_lines.append(f"| {q['id']} | clarification | — | — | — |")
            elif r.get("error"):
                report_lines.append(f"| {q['id']} | error | — | — | {r['error'][:60]} |")
            else:
                c = r.get("classification", {})
                d = r.get("decision", {})
                current = f"({c.get('top_interaction', '?')}, {c.get('top_scope', '?')})"
                target = f"({d.get('target_interaction', '?')}, {d.get('target_scope', '?')})"
                report_lines.append(f"| {q['id']} | {r.get('type')} | {current} | {target} | {d.get('decision_type', '?')} |")

    # Failures analysis
    failures = []
    for q, r in results:
        if r.get("error"):
            failures.append((q["id"], f"Pipeline error: {r['error'][:200]}"))
        elif q.get("category") == "stay_override_evasion":
            passed, note = check_stay_evasion(r, q.get("expected_override", ""))
            if not passed:
                failures.append((q["id"], note))
        elif q.get("category") == "cell_boundary":
            passed, note = check_cell_boundary(r)
            if not passed:
                failures.append((q["id"], note))

    if failures:
        report_lines.extend([
            "",
            "## 5. Failure Analysis",
            "",
        ])
        for qid, note in failures:
            report_lines.extend([
                f"### {qid}",
                "",
                note,
                "",
            ])

    report_lines.extend([
        "",
        "## Known Limitations",
        "",
        "### Framework-level issues (out of scope for code fixes)",
        "",
        "1. **Multi-cell users:** The 4x4 cell framework cannot represent users operating at different cells across substance and process (e.g., a doctoral student whose research topic is Co-Evolutionary/Universal but whose immediate advisor relationship is Reciprocal/Relational). Any attempt to 'fix' this by averaging cells or picking one is wrong. This requires framework PI input.",
        "",
        "2. **Default elevation policy is a placeholder:** The '+1 each axis' rule is v0.1. Real policy refinement requires labeled cohort data that does not yet exist. Do not invent learned policies.",
        "",
        "### Implementation-level issues (fixable)",
        "",
        "1. **Cell boundary confidence calibration:** The classifier may report high confidence on genuinely ambiguous queries. This is a prompt calibration issue, not a framework issue. Fixable by adding more boundary worked examples to the Layer 1 prompt.",
        "",
        "2. **Stay-override signal detection depends on LLM judgment:** Unlike keyword matching, context signal detection is probabilistic. A query about borderline misconduct may or may not trigger FRAUD_OR_BREACH depending on the model's interpretation. The confidence threshold (0.7) provides a tuning knob.",
        "",
        "## Next Priority",
        "",
        "The single most impactful change: **add 5-8 more worked examples to the Layer 1 prompt covering stay-override scenarios and cell boundary cases.** The classifier's few-shot examples currently only cover low-cell queries. Adding examples of fraud detection, hostile contexts, and boundary disambiguation would improve both signal detection accuracy and confidence calibration without any code changes.",
    ])

    total_pass = stay_pass + boundary_pass + schema_pass
    total_tests = stay_total + boundary_total + schema_total
    report_lines.insert(4, f"**Overall pass rate:** {total_pass}/{total_tests} checks")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(report_lines))
    print(f"\nReport written to {REPORT_PATH}")
    print(f"Overall: {total_pass}/{total_tests} checks passed")


if __name__ == "__main__":
    asyncio.run(main())
