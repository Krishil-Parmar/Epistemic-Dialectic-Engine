import json
from pathlib import Path

import yaml
from jinja2 import Template

from ede.llm.base import LLMClient
from ede.schemas import ElevationDecision, DraftResponse, CritiqueResult

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "layer4_critique.md"
CELL_DEFS_PATH = Path(__file__).parent.parent.parent / "docs" / "framework" / "cell_definitions.md"
THRESHOLDS_PATH = Path(__file__).parent.parent.parent / "config" / "thresholds.yaml"


class CritiqueLayer:
    def __init__(self, client: LLMClient):
        self.client = client
        self._template = Template(PROMPT_PATH.read_text())
        self._cell_definitions = CELL_DEFS_PATH.read_text()
        thresholds = yaml.safe_load(THRESHOLDS_PATH.read_text())
        self._min_target_cell_match = thresholds["critique"]["min_target_cell_match"]
        self._min_premortem_completeness = thresholds["critique"]["min_premortem_completeness"]
        self._min_instruction_adherence = thresholds["critique"]["min_instruction_adherence"]

    async def run(
        self,
        query: str,
        decision: ElevationDecision,
        draft: DraftResponse,
        temperature: float = 0.0,
        max_tokens: int = 1000,
    ) -> CritiqueResult:
        rendered = self._template.render(
            cell_definitions=self._cell_definitions,
            min_target_cell_match=self._min_target_cell_match,
            min_premortem_completeness=self._min_premortem_completeness,
            min_instruction_adherence=self._min_instruction_adherence,
            user_query=query,
            target_interaction=decision.target_interaction,
            target_scope=decision.target_scope,
            decision_type=decision.decision_type,
            pre_mortem_priority=decision.pre_mortem_priority,
            draft_response_text=draft.response_text,
            pre_mortem_json=draft.pre_mortem_outputs.model_dump_json(indent=2),
            safeguards_json=json.dumps(draft.safeguards_included, indent=2),
        )

        parts = rendered.split("# User", 1)
        system_prompt = parts[0].strip()
        user_prompt = ("# User" + parts[1]).strip() if len(parts) > 1 else query

        return await self.client.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=CritiqueResult,
            temperature=temperature,
            max_tokens=max_tokens,
        )
