import json
from pathlib import Path

from jinja2 import Template

from ede.llm.base import LLMClient
from ede.schemas import MindsetClassification, ElevationDecision, DraftResponse

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "layer3_generator.md"
CELL_DEFS_PATH = Path(__file__).parent.parent.parent / "docs" / "framework" / "cell_definitions.md"


class ResponseGeneratorLayer:
    def __init__(self, client: LLMClient):
        self.client = client
        self._template = Template(PROMPT_PATH.read_text())
        self._cell_definitions = CELL_DEFS_PATH.read_text()

    async def run(
        self,
        query: str,
        classification: MindsetClassification,
        decision: ElevationDecision,
        critique_feedback: str | None = None,
        temperature: float = 0.4,
        max_tokens: int = 2000,
    ) -> DraftResponse:
        rendered = self._template.render(
            cell_definitions=self._cell_definitions,
            current_interaction=decision.current_interaction,
            current_scope=decision.current_scope,
            target_interaction=decision.target_interaction,
            target_scope=decision.target_scope,
            decision_type=decision.decision_type,
            rationale=decision.rationale,
            pre_mortem_priority=decision.pre_mortem_priority,
            user_query=query,
        )

        if critique_feedback:
            rendered += f"\n\n## Previous critique feedback\n\n{critique_feedback}"

        parts = rendered.split("# User", 1)
        system_prompt = parts[0].strip()
        user_prompt = ("# User" + parts[1]).strip() if len(parts) > 1 else query

        return await self.client.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=DraftResponse,
            temperature=temperature,
            max_tokens=max_tokens,
        )
