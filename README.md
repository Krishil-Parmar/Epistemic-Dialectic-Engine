# Epistemic Dialectic Engine (EDE)

> An LLM-mediated pedagogical scaffold that operationalizes the Mindset Elevation Framework for executive doctoral education.

**Status:** Pre-MVP. Research scaffold under construction.
**Principal Investigator (Framework):** the framework PI
**Engineering Lead:** Krishil Parmar
**Target Venue (eventual paper):** Computers & Education, Decision Sciences Journal of Innovative Education, or Academy of Management Learning & Education

---

## 1. Why This Project Exists

Standard LLMs answer questions. They do not improve the reasoning of the person asking. For executive doctoral students (EMBA, DBA, and Philosophy of Science cohorts), the core pedagogical bottleneck is not access to information. It is the inability to recognize and shift their own mindset when facing complex business and ethical dilemmas.

The Mindset Elevation Framework (described in Section 3) classifies a decision-maker's mindset along two axes (Interaction Mode and Scope), producing a 4x4 grid of 16 mindset states. The framework predicts that calibrated elevation along these axes produces more resilient and ethically robust decisions, provided the elevated advice is stress-tested against real-world risk.

This repository operationalizes that framework as a multi-layer LLM pipeline. Every user interaction is classified, an appropriate elevation target is selected, a constrained response is generated, the response is self-critiqued against the framework, and the entire transaction is logged for empirical evaluation.

**The research claim being built toward:**

> Among N executive doctoral students, exposure to the framework-scaffolded LLM produced a measurable shift in self-reported decision rationale toward higher Interaction and Scope dimensions compared to a baseline LLM, and the framework-calibrated classifier achieved Cohen's kappa of X against expert raters.

---

## 2. Scope and Non-Goals

### In scope

- A working multi-layer pipeline implementing the Mindset Elevation Framework
- Multi-provider LLM abstraction (Claude, Gemini, OpenAI) so layer-level provider choice is configurable
- Structured I/O between layers using Pydantic schemas
- Editable policy configuration (YAML) so the PI can refine elevation rules without touching code
- Per-interaction logging suitable for downstream empirical analysis
- A Streamlit demo surface for cohort exposure

### Explicitly out of scope (for v1)

- Full labeled dataset for classifier evaluation (deferred to Phase 2; see Section 11 for the risk this creates)
- Production-grade auth, multi-tenancy, or billing
- Mobile-native frontend
- Any layer that imitates Popperian falsification or Kuhnian paradigm shift. The framework is the PI's proprietary contribution; the engine operationalizes it, not external philosophy of science apparatus.
- Anything that is not directly accountable to the eventual paper's methodology section

---

## 3. The Theoretical Framework

The framework is the work of the framework PI. The summary below is engineering-facing. Authoritative descriptions live in `docs/framework/`.

### Axis 1: Interaction Mode

Measures the nature of the bond and the logic of the engagement.

| Level | Name            | Core Logic                                                                |
| ----- | --------------- | ------------------------------------------------------------------------- |
| 1     | Transactional   | Utility-based. Immediate exchange. Ends when the trade is complete.       |
| 2     | Reciprocal      | Trust-based. Long-term balance, expectation of giving back.               |
| 3     | Collaborative   | Synergy-based. Co-creation. 1+1=3 outcomes.                               |
| 4     | Co-Evolutionary | Purpose-based. Interaction transforms both parties and the system itself. |

### Axis 2: Scope

Measures the boundary of concern.

| Level | Name       | Boundary                                                     |
| ----- | ---------- | ------------------------------------------------------------ |
| 1     | Individual | Self. Personal gain, safety, achievement.                    |
| 2     | Relational | Team, partners, direct contacts with shared immediate goals. |
| 3     | Systemic   | Community, organization, industry, market.                   |
| 4     | Universal  | Global, generational, planetary, foundational principles.    |

### The 16 Cells

A user's mindset at any point is one of 16 cells, written `(Interaction, Scope)`. Example: `(Transactional, Individual)` is the lowest cell; `(Co-Evolutionary, Universal)` is the highest.

### The Pre-Mortem Layer

Before any elevated advice is delivered, the response must satisfy three resilience tests:

1. **Downside Test:** If the counterparty acts in bad faith, does the elevated advice expose the user dangerously? If yes, attach principled safeguards.
2. **Upside Test:** If the situation scales favorably, does the advice create a flywheel?
3. **Pivot Test:** If core assumptions change (deadline, budget, stakeholder), does the logic still hold?

### Open framework questions (must be resolved with the PI before Phase 2)

These are surfaced explicitly because the framework, as currently described, has gaps that will block empirical evaluation. They are not criticisms; they are necessary refinements.

1. **Cell boundary definitions.** What linguistic, structural, or topical signals separate Reciprocal from Collaborative? Relational from Systemic? Without operational definitions, the classifier in Layer 1 cannot achieve usable inter-rater reliability.
2. **The "stay" case.** The framework as described assumes elevation is always desirable. In hostile negotiations, fraud investigations, or contract enforcement, elevation toward Co-Evolutionary thinking would be actively harmful. The policy engine must support a "stay" decision with clear criteria.
3. **Pre-Mortem test redundancy.** The Downside Test and the Pivot Test overlap operationally. Both ask "what if conditions change adversely." A consolidated formulation may be cleaner.
4. **Combinatorial explosion.** 16 cells x 3 Pre-Mortem tests x query types produces a large policy surface. Without a labeled dataset and a defined policy table, the system cannot give consistent advice across sessions.

These questions are the agenda for the next working session with the PI. See `docs/framework/open_questions.md` for the long-form versions to send her.

---

## 4. Architecture

The pipeline is decoupled. Each layer has a strict input schema, a strict output schema, and is independently testable. Layers communicate via Pydantic models, never via free-form text.

```
                         User Query
                              |
                              v
           +-----------------------------------+
           | Layer 1: Calibrated Mindset       |
           | Classifier                        |
           |                                   |
           | Output: probability distribution  |
           | over 16 cells, confidence,        |
           | clarification_needed flag         |
           +-----------------------------------+
                              |
                              v
           +-----------------------------------+
           | Layer 2: Elevation Policy Engine  |
           |                                   |
           | Pure code. Reads YAML policy.     |
           | Output: target cell, decision     |
           | type (elevate, stay, horizontal,  |
           | deepen), justification            |
           +-----------------------------------+
                              |
                              v
           +-----------------------------------+
           | Layer 3: Constrained Response     |
           | Generator                         |
           |                                   |
           | Generates draft satisfying target |
           | cell behavior + Pre-Mortem checks |
           +-----------------------------------+
                              |
                              v
           +-----------------------------------+
           | Layer 4: Self-Critique Against    |
           | Framework                         |
           |                                   |
           | Validates draft against target    |
           | cell + Pre-Mortem outputs.        |
           | Loops to Layer 3 if fails.        |
           +-----------------------------------+
                              |
                              v
                        Final Response
                              |
                              v
                  +----------------------+
                  | Logging Layer        |
                  | (every transaction)  |
                  +----------------------+
```

### Layer 1: Calibrated Mindset Classifier

**Purpose:** Diagnose the user's current mindset cell from their query.

**Input:** Raw user query (string), optional conversation history.

**Output:** `MindsetClassification` Pydantic model:

```python
class MindsetClassification(BaseModel):
    cell_probabilities: dict[Cell, float]  # Sums to 1.0 across 16 cells
    top_cell: Cell
    confidence: float  # 0.0 to 1.0
    justification: str  # One sentence per axis
    clarification_needed: bool
    clarification_question: Optional[str]
```

**Behavior:** If `confidence` falls below a configured threshold (default 0.6), the layer sets `clarification_needed=True` and emits a targeted clarification question. The pipeline halts and waits for user response.

**Provider configurability:** This layer benefits from the strongest reasoning model available. Default: Gemini 3.1 Pro. Configurable per Section 6.

### Layer 2: Elevation Policy Engine

**Purpose:** Decide where to take the user. Not "+1 on each axis." A learned or designed policy.

**Input:** `MindsetClassification` from Layer 1, query metadata (e.g., detected query type, presence of adversarial counterparty signals).

**Output:** `ElevationDecision` Pydantic model:

```python
class ElevationDecision(BaseModel):
    current_cell: Cell
    target_cell: Cell
    decision_type: Literal["elevate", "stay", "horizontal", "deepen"]
    rationale: str
    pre_mortem_priority: Literal["downside", "upside", "pivot", "all"]
```

**Implementation:** This layer is pure Python code reading a YAML policy table. No LLM call. This guarantees reproducibility and lets the PI edit the policy directly.

**Policy file location:** `config/elevation_policy.yaml`

**Policy file structure:**

```yaml
default_policy:
  - condition:
      current_interaction: "Transactional"
      current_scope: "Individual"
      query_type: "any"
    target_interaction: "Reciprocal"
    target_scope: "Relational"
    decision_type: "elevate"
    pre_mortem_priority: "downside"

stay_overrides:
  - condition:
      query_signals: ["adversarial_counterparty", "fraud", "enforcement"]
    decision_type: "stay"
    rationale: "Hostile context. Elevation here is actively harmful."
```

### Layer 3: Constrained Response Generator

**Purpose:** Generate the response that expresses target cell behavior and embeds Pre-Mortem-derived safeguards.

**Input:** Original user query, `MindsetClassification`, `ElevationDecision`.

**Output:** `DraftResponse` Pydantic model:

```python
class DraftResponse(BaseModel):
    response_text: str
    target_cell_expressed: Cell  # Self-claimed
    pre_mortem_outputs: PreMortemAnalysis
    safeguards_included: list[str]

class PreMortemAnalysis(BaseModel):
    downside_scenario: str
    downside_safeguards: list[str]
    upside_scenario: str
    flywheel_logic: Optional[str]
    pivot_scenario: str
    robustness_check: str
```

**Behavior:** The layer prompts the LLM with the target cell description, the user's current cell, and explicit Pre-Mortem instructions. Pre-Mortem outputs are required structured fields, not narrative asides. This is what allows Layer 4 to validate them.

### Layer 4: Self-Critique Against Framework

**Purpose:** Verify the draft actually expresses target cell behavior and carries the safeguards. If not, loop.

**Input:** `DraftResponse` from Layer 3, original query, `ElevationDecision`.

**Output:** `CritiqueResult` Pydantic model:

```python
class CritiqueResult(BaseModel):
    passed: bool
    target_cell_match_score: float  # 0.0 to 1.0
    pre_mortem_completeness_score: float
    issues: list[str]
    refined_response: Optional[str]  # If passed=False and refinement was generated
```

**Behavior:** If `passed=False`, the layer either returns a refined response directly or loops back to Layer 3 with the critique as additional context. Maximum 2 loops, then accept current draft and log the failure for later analysis.

### Logging Layer

**Purpose:** Capture the complete transaction for empirical analysis. This is the data spine of the eventual paper. Every field matters.

**Storage:** SQLite for MVP (file-based, zero infrastructure), schema-compatible migration path to Postgres for cohort-scale deployment.

**Schema:** See Section 7.

---

## 5. Repository Structure

```
epistemic-dialectic-engine/
|
|-- README.md                          # This file
|-- pyproject.toml                     # Dependencies, project metadata
|-- .env.example                       # Required env vars
|-- .gitignore
|
|-- ede/                               # Main package
|   |-- __init__.py
|   |-- schemas.py                     # All Pydantic models
|   |-- cells.py                       # Cell, Interaction, Scope enums
|   |
|   |-- llm/                           # Multi-provider abstraction
|   |   |-- __init__.py
|   |   |-- base.py                    # LLMClient protocol
|   |   |-- claude_client.py
|   |   |-- gemini_client.py
|   |   |-- openai_client.py
|   |   |-- registry.py                # Provider selection by config
|   |
|   |-- layers/
|   |   |-- __init__.py
|   |   |-- layer1_classifier.py
|   |   |-- layer2_policy.py
|   |   |-- layer3_generator.py
|   |   |-- layer4_critique.py
|   |
|   |-- pipeline.py                    # Orchestrates the four layers
|   |
|   |-- prompts/                       # Prompt templates per layer
|   |   |-- layer1_classifier.md
|   |   |-- layer3_generator.md
|   |   |-- layer4_critique.md
|   |
|   |-- logging/
|   |   |-- __init__.py
|   |   |-- store.py                   # SQLite logger
|   |   |-- schema.sql
|   |
|   |-- evaluation/                    # Phase 2: classifier evaluation harness
|   |   |-- __init__.py
|   |   |-- kappa.py                   # Cohen's kappa, Krippendorff's alpha
|   |   |-- dataset_loader.py
|
|-- config/
|   |-- elevation_policy.yaml          # Editable by the PI
|   |-- providers.yaml                 # Per-layer provider/model selection
|   |-- thresholds.yaml                # Confidence thresholds, loop limits
|
|-- docs/
|   |-- framework/
|   |   |-- framework_description.md         # Authoritative framework description
|   |   |-- cell_definitions.md        # Operational definitions per cell
|   |   |-- open_questions.md          # Questions for the PI
|   |-- methodology/
|   |   |-- evaluation_protocol.md     # Phase 2 protocol
|   |   |-- irb_notes.md               # Ethics approval planning
|
|-- ui/
|   |-- streamlit_app.py               # Demo interface
|
|-- tests/
|   |-- test_layer1.py
|   |-- test_layer2.py
|   |-- test_layer3.py
|   |-- test_layer4.py
|   |-- test_pipeline_integration.py
|   |-- fixtures/
|       |-- sample_queries.json        # Including the three the PI already saw
|
|-- data/
|   |-- ede.sqlite                     # Local logging database (gitignored)
```

---

## 6. Multi-Provider LLM Abstraction

Each layer that uses an LLM specifies its provider and model in `config/providers.yaml`. This lets you A/B test providers per layer without code changes, which matters for the paper (a referee will ask whether the results depend on provider choice).

### Provider configuration

```yaml
# config/providers.yaml

layer1_classifier:
  provider: "google"
  model: "gemini-3.1-pro-preview"
  temperature: 0.0
  max_tokens: 1500

layer3_generator:
  provider: "google"
  model: "gemini-3.1-pro-preview"
  temperature: 0.4
  max_tokens: 2000

layer4_critique:
  provider: "google"
  model: "gemini-3.1-pro-preview"
  temperature: 0.0
  max_tokens: 1000
```

### Client interface

```python
# ede/llm/base.py
from typing import Protocol, Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class LLMClient(Protocol):
    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> str: ...

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Type[T],
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> T: ...
```

Each provider implementation handles its own structured-output mechanism (Anthropic tool use, Gemini structured output, OpenAI function calling) but all return validated Pydantic instances of the requested schema. Schema validation failure triggers one retry with the validation error appended to the prompt, then raises.

### Why this matters for the paper

A reviewer will ask: "Is your classifier kappa a property of the framework or of the model you used?" By making provider per-layer configurable and logging which provider produced each output, you can run ablations and answer that question empirically.

---

## 7. Logging Schema

Every pipeline invocation produces one row in `transactions` and one or more rows in associated tables.

```sql
-- Primary transaction record
CREATE TABLE transactions (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_id TEXT,                        -- Anonymized cohort ID
    timestamp_utc TEXT NOT NULL,
    user_query TEXT NOT NULL,
    final_response TEXT NOT NULL,
    pipeline_version TEXT NOT NULL,
    completed_successfully INTEGER NOT NULL  -- Boolean
);

-- Layer 1 output
CREATE TABLE classifications (
    transaction_id TEXT PRIMARY KEY REFERENCES transactions(id),
    top_cell TEXT NOT NULL,
    confidence REAL NOT NULL,
    cell_probabilities_json TEXT NOT NULL,
    justification TEXT,
    clarification_needed INTEGER NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    latency_ms INTEGER
);

-- Layer 2 output
CREATE TABLE elevation_decisions (
    transaction_id TEXT PRIMARY KEY REFERENCES transactions(id),
    current_cell TEXT NOT NULL,
    target_cell TEXT NOT NULL,
    decision_type TEXT NOT NULL,
    rationale TEXT,
    pre_mortem_priority TEXT,
    policy_version TEXT NOT NULL
);

-- Layer 3 output
CREATE TABLE drafts (
    id TEXT PRIMARY KEY,
    transaction_id TEXT REFERENCES transactions(id),
    iteration INTEGER NOT NULL,            -- 1, 2 for loops
    response_text TEXT NOT NULL,
    target_cell_expressed TEXT NOT NULL,
    pre_mortem_json TEXT NOT NULL,
    safeguards_json TEXT,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    latency_ms INTEGER
);

-- Layer 4 output
CREATE TABLE critiques (
    id TEXT PRIMARY KEY,
    draft_id TEXT REFERENCES drafts(id),
    passed INTEGER NOT NULL,
    target_cell_match_score REAL,
    pre_mortem_completeness_score REAL,
    issues_json TEXT,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    latency_ms INTEGER
);

-- For Phase 2 expert evaluation
CREATE TABLE expert_ratings (
    id TEXT PRIMARY KEY,
    transaction_id TEXT REFERENCES transactions(id),
    rater_id TEXT NOT NULL,
    rated_cell TEXT NOT NULL,
    notes TEXT,
    timestamp_utc TEXT NOT NULL
);
```

---

## 8. Configuration Surface

Three YAML files cover everything the PI or you would change without touching code.

### `config/elevation_policy.yaml`

Owned by the PI. Defines the mapping from current cell + query signals to target cell. See Section 4.

### `config/providers.yaml`

Owned by engineering. Per-layer provider, model, and sampling parameters. See Section 6.

### `config/thresholds.yaml`

```yaml
classifier:
  min_confidence_for_proceed: 0.60
  min_confidence_for_stay_decision: 0.75

critique:
  min_target_cell_match: 0.70
  min_premortem_completeness: 0.80
  max_refinement_loops: 2
```

---

## 9. Prompt Templates

Prompts live in `ede/prompts/` as Markdown files with template variables. They are loaded at runtime and rendered with Jinja2. This separation lets you version prompts independently of code, which matters for the paper (you must report exactly what prompts produced your results).

Each prompt file has a YAML front-matter block declaring its version, target schema, and dependencies on configuration values. Example header:

```markdown
---
version: "0.1.0"
target_schema: "MindsetClassification"
requires_config: ["thresholds.classifier"]
---

# Layer 1: Mindset Classifier

You are evaluating a query from an executive doctoral student...
```

The classifier, generator, and critique prompts must each contain the operational definitions of the cells (loaded from `docs/framework/cell_definitions.md`). This is enforced by a startup check: if `cell_definitions.md` is missing or stale, the pipeline refuses to start. This prevents silent drift between the framework documentation and what the model actually sees.

---

## 10. Setup and Installation

### Prerequisites

- Python 3.11 or higher
- API keys for at least one provider (Anthropic, Google, or OpenAI)
- SQLite (bundled with Python)

### Installation

```bash
git clone <repository_url>
cd epistemic-dialectic-engine
python -m venv venv
source venv/bin/activate          # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
# Edit .env to add your API keys
```

### Environment variables

```
GOOGLE_API_KEY=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
EDE_LOG_LEVEL=INFO
EDE_DB_PATH=./data/ede.sqlite
```

### Running the demo

```bash
streamlit run ui/streamlit_app.py
```

### Running tests

```bash
pytest tests/ -v
pytest tests/test_pipeline_integration.py -v --slow  # Hits real APIs
```

---

## 11. Roadmap and Phased Plan

### Phase 0: Framework refinement (this week)

- Send the PI the open questions in `docs/framework/open_questions.md`
- Co-author operational cell definitions
- Lock the v0.1 policy table for the MVP

### Phase 1: MVP architecture (2 to 3 weeks)

- Implement Layers 1 to 4 with a single hardcoded policy
- Streamlit demo deployed (Streamlit Community Cloud, free tier)
- Send the PI a working link with the three test queries pre-loaded

### Phase 2: Empirical evaluation foundation (1 to 2 months)

**This phase is the research-critical bottleneck.** The MVP will appear to work in Phase 1 because LLMs produce fluent text. Without Phase 2, you cannot make any defensible claim about whether the classifier is actually classifying or just confabulating.

Phase 2 deliverables:

- Labeled dataset of 200 to 300 business dilemmas, each tagged with the correct cell by the PI and one independent rater (likely another faculty member from the doctoral program)
- Inter-rater reliability calculation (Cohen's kappa minimum 0.70 between human raters before classifier evaluation begins; if humans cannot agree, the classifier has no ground truth)
- Classifier kappa evaluation against the human-tagged set
- Iteration on cell definitions and prompts until classifier kappa is acceptable

### Phase 3: Closed beta (semester duration)

- Deploy to the PI's doctoral cohort
- Collect interaction logs
- Pre-test, intervention, post-test design

### Phase 4: Analysis and paper draft

- Statistical analysis of pre/post mindset shift
- Qualitative coding of session transcripts
- Draft submitted to one of the target venues

### Risk register

| Risk                                   | Severity | Mitigation                                                                                            |
| -------------------------------------- | -------- | ----------------------------------------------------------------------------------------------------- |
| Classifier kappa below 0.70            | High     | Phase 2 cannot be skipped. If kappa is low, the framework definitions need refinement, not the model. |
| Policy table grows uncontrollably      | Medium   | Constrain to v0.1 transitions in MVP. Expand only based on Phase 2 evidence.                          |
| Provider behavior drift mid-study      | Medium   | Pin model versions in `providers.yaml`. Log provider+model on every call.                           |
| IRB approval delays                    | High     | Begin IRB conversation with SP Jain in parallel with Phase 1.                                         |
| Demand characteristics in cohort study | Medium   | Include a baseline-LLM control arm. Blind raters to condition.                                        |

---

## 12. Methodology Notes for the Paper

This section is a placeholder for the eventual Methods section. As the project progresses, decisions made here should be appended verbatim, so that the paper reflects what was actually done, not what was planned.

### Construct: "Epistemic Shift" / "Mindset Elevation"

Operationalized as the directional change in cell classification between a user's initial query in a session and their subsequent queries (or follow-up self-reported decision rationale, depending on study design). To be specified precisely in `docs/methodology/evaluation_protocol.md` before Phase 3.

### Control condition

Same user pool exposed to a baseline LLM (one of the providers used by EDE, with a neutral system prompt). Within-subjects or between-subjects design to be decided with the PI based on cohort size.

### Statistical analysis

Pre-registered. To be detailed in `docs/methodology/evaluation_protocol.md`.

---

## 13. Contributing

This is a research repository. Code changes should be tied to either an architectural decision or a methodological one, both documented. Prompt changes are versioned. Cell definition changes require the PI's sign-off and a corresponding migration note in the logging schema (so old transactions remain interpretable under the definition active when they were created).

---

## 14. License and Attribution

The Mindset Elevation Framework is the intellectual property of the framework PI. The engine code is authored by Krishil Parmar. Final license and authorship arrangement to be agreed before any external publication or release.

---

## Appendix A: Glossary

- **Cell:** One of 16 mindset states, written `(Interaction, Scope)`.
- **Elevation:** A move from a lower cell to a higher one along one or both axes.
- **Stay decision:** A diagnosis that the user's current cell is appropriate for the situation and elevation would be harmful.
- **Pre-Mortem:** The set of three resilience tests (Downside, Upside, Pivot) applied to elevated advice.
- **Cohen's kappa:** Statistical measure of inter-rater agreement, correcting for agreement by chance. The publication-relevant threshold for this work is 0.70.
- **Policy table:** YAML file mapping `(current_cell, query_signals)` to `(target_cell, decision_type)`. Owned by the framework PI, not engineering.

---

## Appendix B: Operational Cell Definitions (v0.1)

This appendix is the canonical source for what each cell means in operational terms. It is loaded into the Layer 1, 3, and 4 prompts at runtime. A copy lives at `docs/framework/cell_definitions.md` and the pipeline performs a hash check at startup to guarantee that what the model sees and what is documented here are identical. This document is v0.1 and must be co-refined with the PI before Phase 2.

### Reading the cells

A cell is written `(Interaction, Scope)` where Interaction is one of {Transactional, Reciprocal, Collaborative, Co-Evolutionary} and Scope is one of {Individual, Relational, Systemic, Universal}. Cells are not personality types. They are the mindset expressed in a specific query at a specific moment. The same person can be in different cells across queries, and the framework predicts that the cell expressed in a query is the appropriate diagnostic anchor, not the person's general disposition.

### Interaction Mode signals

**Transactional** is signaled by language of exchange, timing, and discrete completion. The user describes the situation as a deal, a trade, a one-off. They use phrases like "what do I get," "what's in it for me," "after this is done." The relationship in the query has a defined endpoint. Trust is not assumed; verification mechanisms (contracts, deliverables, conditions) are emphasized.

**Reciprocal** is signaled by language of long-term balance and ongoing exchange. The user describes the situation as a relationship with memory: past favors are remembered, future favors are expected, fairness is measured across time rather than within a single transaction. Phrases like "I'll owe them," "they helped me before," "next time," "build the relationship." Trust is assumed at the level of the relationship but accounted for at the level of specific exchanges.

**Collaborative** is signaled by language of co-creation and joint output. The user frames the situation as a problem that cannot be solved by one party acting alone. Phrases like "we need to figure this out together," "neither of us can do this without the other," "combining our strengths," "1+1=3." The output of the interaction is something that did not exist before either party engaged. Trust is operational, not just affective.

**Co-Evolutionary** is signaled by language of mutual transformation and systemic change. The user frames the situation as one where both parties (and the broader system they operate in) will be different at the end. Phrases like "this changes how we both work," "we are growing together," "the way our industry approaches this is shifting," "this becomes the new norm." The interaction is not just about producing outputs; it is about reshaping the conditions of future interaction. Note: this is not "altruistic." Co-Evolutionary mindset is calibrated and strategic; it just operates at a different level of abstraction.

### Scope signals

**Individual** is signaled by exclusive focus on the user's own outcomes. Stakeholders are mentioned only as instruments or obstacles. Phrases like "how do I," "I need," "what should I do," "for me." Decisions are evaluated against personal gain, safety, or achievement.

**Relational** is signaled by inclusion of named immediate counterparties whose outcomes the user genuinely cares about. Phrases like "my team," "my partner," "my co-founder," "my manager." The user can articulate what success looks like for the other party as well as themselves.

**Systemic** is signaled by reference to broader contexts the user is part of: a company, an industry, a market, a profession, an organizational culture. The user evaluates the decision against effects on this larger system. Phrases like "the team's morale," "our company culture," "the precedent this sets," "the industry standard," "what this means for the whole department."

**Universal** is signaled by reference to durations, populations, or principles that exceed the user's direct sphere. Phrases like "future generations," "the planet," "society," "the kind of leader I want to be remembered as," "fundamental fairness." Universal scope is rare in operational business queries and should be classified with caution; users frequently invoke universal language rhetorically while reasoning at Systemic or Relational scope.

### Disambiguation rules

These are the boundary calls Layer 1 will need to make. They are deliberately conservative; when in doubt, classify the lower cell.

**Transactional vs Reciprocal:** if the user mentions any expectation of future interaction with the same counterparty beyond completing the current item, classify Reciprocal. If the relationship ends at delivery, classify Transactional.

**Reciprocal vs Collaborative:** if the user describes the output as something each party could in principle produce alone (just better together), classify Reciprocal. If the user describes the output as genuinely joint (neither party could produce it alone in any form), classify Collaborative.

**Collaborative vs Co-Evolutionary:** if the user describes the interaction as producing a one-time output that ends when delivered, classify Collaborative. If the user describes the interaction as changing how either party will operate in future analogous situations, classify Co-Evolutionary.

**Individual vs Relational:** if the user mentions counterparties only to describe the situation but does not articulate their interests or outcomes, classify Individual. If the user articulates what success looks like for the counterparty, classify Relational.

**Relational vs Systemic:** if the user's concerns extend only to named individuals they directly interact with, classify Relational. If the user references effects on people beyond their direct sphere (the broader team, the company, the market), classify Systemic.

**Systemic vs Universal:** if the system the user references is bounded (a company, an industry), classify Systemic. If the system is unbounded (humanity, future generations, principles that apply across domains), classify Universal. Universal classification requires explicit textual evidence; do not infer Universal scope from rhetorical flourishes.

### Worked examples

The three queries Krishil already tested with the PI are calibration anchors. They are reproduced here with their v0.1 classifications for use in Layer 1 prompt few-shot examples.

**Query 1:** "I am doing an internship at a startup for last 4 months without pay. they really like my work and I have build major production grade components for them. how do I convince them for a paid role with atleast 2000 aud in stipend"

Classification: `(Transactional, Individual)`. Justification: query frames the situation as an exchange ("convince them for a paid role"), focuses on the user's own outcome (the stipend), and treats the startup as a counterparty rather than a partner whose interests are articulated.

**Query 2:** "How do I protect my job during layoffs?"

Classification: `(Transactional, Individual)`. Justification: defensive framing centered on self-preservation. No mention of team, manager, or company outcomes as objects of concern. The bot's elevated response correctly moved the user toward Reciprocal/Relational thinking.

**Query 3:** "My partner isn't pulling their weight on this project. What should I do?"

Classification: `(Transactional, Relational)`. Justification: the user names an immediate counterparty ("my partner") and engages with them as a person, but the framing is still about getting fair output rather than co-creating. The elevated response correctly moved toward Collaborative.

### Confidence calibration guidance for Layer 1

The classifier should report confidence below 0.6 (and trigger the clarification flow) when:

- The query is too short to extract meaningful signals (under roughly 15 words).
- The query mixes signals from non-adjacent cells (e.g., Transactional language with Universal scope claims).
- The query is ambiguous between two adjacent cells and the disambiguation rules above do not resolve it.

The classifier should report confidence above 0.85 when:

- Multiple independent signals point to the same cell.
- Linguistic markers are unambiguous.
- The query closely matches a worked example.

---

## Appendix C: v0.1 Elevation Policy

This is the policy file Layer 2 will load. It is intentionally simple. The default rule is "elevate one step on each axis, capped at level 4." Stay overrides handle hostile contexts. Phase 2 will add learned or evidence-based refinements.

```yaml
# config/elevation_policy.yaml
# v0.1 hand-authored, to be refined with the PI

version: "0.1.0"
last_updated: "2026-04-28"
owner: "the framework PI (framework), Krishil Parmar (engineering)"

# Default elevation: +1 on each axis, capped at level 4
default_policy:
  rule: "elevate_one_step_each_axis"
  description: "Move both Interaction and Scope up one level. If already at level 4 on an axis, hold that axis constant. The Pre-Mortem priority defaults to Downside for elevations from level 1 or 2 (where exposure risk is highest) and to Upside for elevations from level 3 (where flywheel logic matters more)."
  pre_mortem_priority_by_source_level:
    1: "downside"
    2: "downside"
    3: "upside"
    4: "pivot"

# Stay overrides: contexts where elevation is harmful and the bot must hold position
stay_overrides:
  - id: "hostile_negotiation"
    description: "User is in an adversarial negotiation where the counterparty's incentive structure rewards exploiting trust."
    triggers:
      keywords: ["lawsuit", "litigation", "fraud", "bad faith", "deceived", "cheated", "ripped off"]
      semantic_signals:
        - "Counterparty has demonstrably acted against the user's interests"
        - "Power asymmetry favors counterparty"
    decision_type: "stay"
    rationale: "Elevating to Reciprocal or Collaborative thinking in a hostile context exposes the user to further exploitation. Hold at current cell, deliver advice that protects the user's position, and surface the framework consideration as context rather than directive."

  - id: "fraud_or_enforcement"
    description: "User is investigating, exposing, or enforcing against fraudulent behavior."
    triggers:
      keywords: ["embezzlement", "stealing", "investigation", "compliance violation", "regulatory"]
    decision_type: "stay"
    rationale: "Enforcement contexts require Transactional rigor. Reciprocal or Collaborative framing would compromise the user's evidentiary position."

  - id: "safety_critical"
    description: "User's safety, or the safety of others, is at stake."
    triggers:
      keywords: ["abuse", "harassment", "violence", "threat", "dangerous"]
    decision_type: "stay"
    rationale: "Safety considerations override elevation logic. Refer to appropriate professional resources where applicable."

# Horizontal moves: cases where the user is at an appropriate level on one axis but needs to shift on the other
horizontal_overrides: []  # Phase 2: populate based on observed cohort patterns

# Deepening moves: user is at a high cell but the response should reinforce rather than elevate
deepen_overrides: []  # Phase 2: populate based on observed cohort patterns
```

---

## Appendix D: Prompt Templates (Skeletons)

These are starting drafts. Claude Code should treat them as scaffolding and refine them during implementation. Each prompt loads cell definitions from Appendix B at runtime via Jinja2 includes.

### `ede/prompts/layer1_classifier.md`

```markdown
---
version: "0.1.0"
target_schema: "MindsetClassification"
requires_config: ["thresholds.classifier"]
---

# System

You are a mindset classifier built on the Mindset Elevation Framework. Your job is to read a user's query and classify the mindset cell it expresses, not the user's personality or general disposition.

Two axes:
- Interaction Mode: Transactional, Reciprocal, Collaborative, Co-Evolutionary
- Scope: Individual, Relational, Systemic, Universal

You output a probability distribution over all 16 cells, your top choice, a confidence score, and a brief justification per axis.

## Operational cell definitions

{{ cell_definitions }}

## Worked examples

{{ worked_examples }}

## Confidence calibration

{{ confidence_guidance }}

## Output format

You must output a JSON object matching the MindsetClassification schema. Probabilities must sum to 1.0 across all 16 cells. If your confidence is below {{ thresholds.classifier.min_confidence_for_proceed }}, set clarification_needed=true and provide a targeted clarification_question.

# User

Query to classify:

{{ user_query }}
```

### `ede/prompts/layer3_generator.md`

```markdown
---
version: "0.1.0"
target_schema: "DraftResponse"
---

# System

You are an advisor operating within the Mindset Elevation Framework. The user's current mindset has been classified, and you have been given a target mindset cell to elevate them toward (or to hold them at, if the decision_type is "stay").

Your response must:
1. Express the target cell's interaction mode and scope explicitly in how you frame the advice.
2. Carry safeguards derived from the Pre-Mortem analysis, especially when the priority is "downside."
3. Avoid moralizing. Elevate by demonstrating practical wisdom, not by preaching.
4. Output structured Pre-Mortem analysis as a separate field, not embedded in the response prose.

## Cell definitions

{{ cell_definitions }}

## Current cell

{{ current_cell }}

## Target cell and decision rationale

{{ target_cell }} decision: {{ decision_type }}
Rationale: {{ rationale }}
Pre-Mortem priority: {{ pre_mortem_priority }}

## Output format

DraftResponse JSON. The response_text field is the user-facing message. The pre_mortem_outputs field is structured analysis the system uses for self-critique; the user does not see it directly.

# User

User's original query:

{{ user_query }}
```

### `ede/prompts/layer4_critique.md`

```markdown
---
version: "0.1.0"
target_schema: "CritiqueResult"
---

# System

You are evaluating whether a draft response correctly expresses the target mindset cell from the Mindset Elevation Framework and includes appropriate Pre-Mortem safeguards.

You are not evaluating whether the advice is "good" in a general sense. You are evaluating framework fidelity.

## Evaluation criteria

1. Target cell expression: does the response's framing, vocabulary, and reasoning match the target cell's operational definition?
2. Pre-Mortem completeness: are downside, upside, and pivot scenarios analyzed at the priority specified by Layer 2?
3. Safeguard inclusion: if Pre-Mortem priority is "downside," does the response include explicit principled safeguards in the user-facing text?

## Cell definitions

{{ cell_definitions }}

## Output format

CritiqueResult JSON. Set passed=true only if all three criteria are satisfied at or above their threshold. If passed=false and you can produce a refined response inline, include it; otherwise, leave refined_response null and the pipeline will loop back to Layer 3.

# User

Original query: {{ user_query }}

Target cell: {{ target_cell }}
Decision type: {{ decision_type }}
Pre-Mortem priority: {{ pre_mortem_priority }}

Draft response:
{{ draft_response_json }}
```

---

## Appendix E: Initial Test Fixtures

Place at `tests/fixtures/sample_queries.json`. These are the calibration anchors plus a small set of additional queries chosen to exercise the cell boundaries.

```json
{
  "version": "0.1.0",
  "queries": [
    {
      "id": "anchor_q1",
      "query": "I am doing an internship at a startup for last 4 months without pay. they really like my work and I have build major production grade components for them. how do I convince them for a paid role with atleast 2000 aud in stipend",
      "expected_cell": ["Transactional", "Individual"],
      "expected_target": ["Reciprocal", "Relational"],
      "notes": "Anchor case. Bot's existing response to this is good and should be reproduced or improved."
    },
    {
      "id": "anchor_q2",
      "query": "How do I protect my job during layoffs?",
      "expected_cell": ["Transactional", "Individual"],
      "expected_target": ["Reciprocal", "Relational"],
      "notes": "Anchor case. Defensive self-preservation framing."
    },
    {
      "id": "anchor_q3",
      "query": "My partner isn't pulling their weight on this project. What should I do?",
      "expected_cell": ["Transactional", "Relational"],
      "expected_target": ["Collaborative", "Relational"],
      "notes": "Anchor case. Tests Scope=Relational + low Interaction."
    },
    {
      "id": "boundary_collaborative_systemic",
      "query": "Our engineering team and the product team keep butting heads on roadmap priorities. How do I get them to work as one unit instead of two warring camps?",
      "expected_cell": ["Reciprocal", "Systemic"],
      "expected_target": ["Collaborative", "Systemic"],
      "notes": "Tests upper-mid range. User already at Systemic scope."
    },
    {
      "id": "stay_override_fraud",
      "query": "I have evidence my co-founder is running personal expenses through the company card. What should I do?",
      "expected_cell": ["Transactional", "Relational"],
      "expected_target": ["Transactional", "Relational"],
      "expected_decision_type": "stay",
      "notes": "Tests stay override for fraud/enforcement context. Elevation here would be harmful."
    },
    {
      "id": "low_confidence",
      "query": "What should I do?",
      "expected_clarification_needed": true,
      "notes": "Tests confidence threshold and clarification flow. Too short to classify."
    }
  ]
}
```

---

---

## Appendix G: Open Questions for the PI

Place at `docs/framework/open_questions.md`. Send with the demo email.

```markdown
# Open Framework Questions

These are refinements to the Mindset Elevation Framework that surfaced during
operationalization. Each one is a real engineering blocker, not a
philosophical aside.

## Question 1: Cell boundary signals

What linguistic, structural, or topical signals distinguish Reciprocal
from Collaborative? Relational from Systemic? Appendix B of the README
contains my v0.1 attempt at operational disambiguation rules. These need
your review and refinement before the classifier can be evaluated.

Specific request: please review the disambiguation rules in
README.md Appendix B and mark any that you would phrase differently or
that you disagree with.

## Question 2: The "stay" case

The framework as documented assumes elevation is always desirable. In
hostile negotiations, fraud investigations, and enforcement contexts,
elevation toward Co-Evolutionary thinking would be harmful. I have
implemented stay overrides for three categories (hostile negotiation,
fraud or enforcement, safety-critical). Please review whether this
captures the cases you want, and whether there are others.

## Question 3: Pre-Mortem test redundancy

The Downside Test and the Pivot Test overlap operationally. Both ask
"what if conditions change adversely." Should they be consolidated, or
do you see a sharp distinction worth preserving in the implementation?

## Question 4: Combinatorial coverage

16 cells x stay/elevate/horizontal/deepen decisions x 3 Pre-Mortem
priorities is a large policy surface. The v0.1 policy uses a simple
default rule (elevate one step on each axis). To make the system
empirically defensible, we need to know which transitions are most
common in your cohort's actual queries. The labeled dataset proposed
in the demo email is the path to answering this empirically rather
than by intuition.
```
