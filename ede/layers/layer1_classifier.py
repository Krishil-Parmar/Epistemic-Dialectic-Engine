from pathlib import Path

import yaml
from jinja2 import Template

from ede.llm.base import LLMClient
from ede.schemas import MindsetClassification, ALL_16_CELLS

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "layer1_classifier.md"
CELL_DEFS_PATH = Path(__file__).parent.parent.parent / "docs" / "framework" / "cell_definitions.md"
THRESHOLDS_PATH = Path(__file__).parent.parent.parent / "config" / "thresholds.yaml"


class MindsetClassifierLayer:
    def __init__(self, client: LLMClient):
        self.client = client
        self._template = Template(PROMPT_PATH.read_text())
        self._cell_definitions = CELL_DEFS_PATH.read_text()
        thresholds = yaml.safe_load(THRESHOLDS_PATH.read_text())
        self._min_confidence = thresholds["classifier"]["min_confidence_for_proceed"]

    async def run(
        self, query: str, temperature: float = 0.0, max_tokens: int = 1500
    ) -> MindsetClassification:
        rendered = self._template.render(
            cell_definitions=self._cell_definitions,
            min_confidence=self._min_confidence,
            user_query=query,
        )

        parts = rendered.split("# User", 1)
        system_prompt = parts[0].strip()
        user_prompt = ("# User" + parts[1]).strip() if len(parts) > 1 else query

        result = await self.client.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=MindsetClassification,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if result.confidence < self._min_confidence:
            result.clarification_needed = True

        if not result.cell_probabilities:
            result.cell_probabilities = self._synthesize_probabilities(
                result.top_interaction, result.top_scope, result.confidence
            )

        return result

    @staticmethod
    def _synthesize_probabilities(
        top_interaction: str, top_scope: str, confidence: float
    ) -> dict[str, float]:
        top_cell = f"({top_interaction}, {top_scope})"
        remaining = 1.0 - confidence
        per_other = remaining / 15 if remaining > 0 else 0.0
        probs = {}
        for cell in ALL_16_CELLS:
            probs[cell] = confidence if cell == top_cell else per_other
        return probs
