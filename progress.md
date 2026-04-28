# EDE Progress Tracker

## Phase 1: Project Skeleton + Data Models — DONE
- [x] `pyproject.toml` with all dependencies
- [x] `.env.example`, `.gitignore`
- [x] `ede/cells.py` — Interaction/Scope enums, Cell type, helpers
- [x] `ede/schemas.py` — Pydantic models
- [x] `config/thresholds.yaml`, `config/providers.yaml`
- [x] `config/elevation_policy.yaml` (pre-existing)
- [x] `docs/framework/cell_definitions.md` (pre-existing)
- [x] `docs/framework/open_questions.md` (pre-existing)

## Phase 2: LLM Client + Layer 2 Policy Engine — DONE
- [x] `ede/llm/base.py`, `claude_client.py`, `gemini_client.py`, `registry.py`
- [x] `ede/layers/layer2_policy.py`
- [x] `tests/test_layer2.py`

## Phase 3-5: Layers, Pipeline, UI — DONE

## Bug Fix Sprint (v0.1 stress test) — DONE

### Bug 1: Stay-override triggers too brittle
- [x] Added `ContextSignal` enum and `DetectedSignal` model to `ede/schemas.py`
- [x] Updated Layer 1 prompt to detect context signals (fraud, hostility, safety, power asymmetry, legal exposure)
- [x] Updated `ede/layers/layer2_policy.py` to check context signals before keyword fallback
- [x] Added `signal_triggers` field to each stay override in `config/elevation_policy.yaml`
- [x] Added `competing_company_breach` test fixture and integration test

### Bug 2: Schema inconsistency in clarification responses
- [x] Added `model_validator` on `MindsetClassification` that auto-normalizes `cell_probabilities` if they don't sum to 1.0
- [x] Updated Layer 1 prompt to require all 16 cells in probability distribution even for low-confidence queries
- [x] Added `clarification_cofounder_weird` test fixture
- [x] Added `test_schemas.py` with 6 schema validation tests

### Bug 3: Layer 4 critique scope too narrow
- [x] Added `instruction_adherence_score` to `CritiqueResult` schema
- [x] Added `min_instruction_adherence: 0.75` to `config/thresholds.yaml`
- [x] Updated Layer 4 prompt with moralizing detection criteria and pass/fail examples
- [x] Updated `ede/logging/schema.sql` and `store.py` to log the new field
- [x] Updated `ede/pipeline.py` to pass the new field through

### Bug 4: No defined behavior at level-4 cap
- [x] Layer 2 already had deepen logic; added descriptive rationale and explicit `pivot` priority
- [x] Added deepen handling block to Layer 3 prompt (reinforce, sharpen, stress-test — no elevation)
- [x] Added `high_cell_deepen` test fixture

### Tests
- [x] `tests/test_layer2.py` — 10 tests (was 7), all pass
- [x] `tests/test_schemas.py` — 6 tests, all pass
- [x] `tests/test_pipeline_integration.py` — 4 integration tests (require API key)
- [x] `tests/stress_test_runner.py` — 20-query stress test with markdown report output

## Gemini Compatibility Fixes — DONE

### Fix 1: Context signals not detected by Gemini
- [x] Stripped `default` and `title` from Gemini schema to prevent Gemini from defaulting `context_signals` to `[]`
- [x] Made all fields `required` in cleaned schema sent to Gemini — forces Gemini to actively populate every field
- [x] Expanded keyword fallback: added "competing company", "client list", "diverting", "fictitious", "kickback" to fraud; "threatened", "blackmail", "retaliat", "sabotag" to hostile

### Fix 2: Malformed JSON from Gemini
- [x] Added trailing comma removal (`re.sub`) in `_extract_json()` — handles Gemini's common JSON malformation

### Fix 3: Empty cell_probabilities (Gemini can't return `dict[str, float]`)
- [x] Gemini doesn't support `additionalProperties` so `dict[str, float]` becomes `{"type": "object"}` → returns `{}`
- [x] Added `_synthesize_probabilities()` in Layer 1: generates weighted distribution from `top_interaction`, `top_scope`, `confidence` when Gemini returns empty dict

### Test Results (2026-04-28)
- [x] 16 unit tests — all pass
- [x] 4 integration tests — all pass (was 2/4 before fixes)
- [ ] Stress test report — running

## What's Next
- [ ] Review stress test report for remaining failures
- [ ] Send the demo link + open_questions.md

## Notes
- Using `gemini-3.1-pro-preview` across all layers (configurable in `config/providers.yaml`)
- Both Anthropic/Claude and Google/Gemini clients implemented
- Context signal detection is LLM-based (Layer 1), with keyword matching as fallback
- 16 unit tests pass without API key; 4 integration tests require GOOGLE_API_KEY
