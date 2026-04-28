import json
import time
from uuid import uuid4

import yaml
from pathlib import Path

from ede.llm.registry import get_client, get_layer_config
from ede.layers.layer1_classifier import MindsetClassifierLayer
from ede.layers.layer2_policy import ElevationPolicyEngine
from ede.layers.layer3_generator import ResponseGeneratorLayer
from ede.layers.layer4_critique import CritiqueLayer
from ede.logging.store import TransactionLogger

THRESHOLDS_PATH = Path(__file__).parent.parent / "config" / "thresholds.yaml"


class EDEPipeline:
    def __init__(self, db_path: str | None = None):
        thresholds = yaml.safe_load(THRESHOLDS_PATH.read_text())
        self._max_loops = thresholds["critique"]["max_refinement_loops"]

        l1_config = get_layer_config("layer1_classifier")
        l3_config = get_layer_config("layer3_generator")
        l4_config = get_layer_config("layer4_critique")

        self.classifier = MindsetClassifierLayer(get_client("layer1_classifier"))
        self.policy = ElevationPolicyEngine()
        self.generator = ResponseGeneratorLayer(get_client("layer3_generator"))
        self.critic = CritiqueLayer(get_client("layer4_critique"))

        self._l1_config = l1_config
        self._l3_config = l3_config
        self._l4_config = l4_config

        if db_path:
            self.logger = TransactionLogger(db_path)
        else:
            self.logger = TransactionLogger()

    async def run(
        self,
        query: str,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        transaction_id = str(uuid4())
        session_id = session_id or str(uuid4())

        # Layer 1: Classify
        t0 = time.monotonic()
        classification = await self.classifier.run(
            query,
            temperature=self._l1_config["temperature"],
            max_tokens=self._l1_config["max_tokens"],
        )
        l1_ms = int((time.monotonic() - t0) * 1000)

        self.logger.log_classification(
            transaction_id=transaction_id,
            top_cell=f"({classification.top_interaction}, {classification.top_scope})",
            confidence=classification.confidence,
            cell_probabilities=classification.cell_probabilities,
            justification=classification.justification,
            clarification_needed=classification.clarification_needed,
            provider=self._l1_config["provider"],
            model=self._l1_config["model"],
            latency_ms=l1_ms,
        )

        if classification.clarification_needed:
            self.logger.log_transaction(
                transaction_id=transaction_id,
                session_id=session_id,
                user_query=query,
                final_response=classification.clarification_question or "Could you provide more context?",
                completed_successfully=False,
                user_id=user_id,
            )
            return {
                "type": "clarification",
                "question": classification.clarification_question or "Could you provide more context?",
                "classification": classification.model_dump(),
                "transaction_id": transaction_id,
            }

        # Layer 2: Policy decision
        decision = self.policy.decide(classification, query)

        self.logger.log_elevation(
            transaction_id=transaction_id,
            current_cell=f"({decision.current_interaction}, {decision.current_scope})",
            target_cell=f"({decision.target_interaction}, {decision.target_scope})",
            decision_type=decision.decision_type,
            rationale=decision.rationale,
            pre_mortem_priority=decision.pre_mortem_priority,
        )

        # Layer 3 + 4: Generate and critique loop
        critique_feedback = None
        final_response = None
        final_draft = None
        final_critique = None

        for iteration in range(1, self._max_loops + 2):
            t0 = time.monotonic()
            draft = await self.generator.run(
                query, classification, decision,
                critique_feedback=critique_feedback,
                temperature=self._l3_config["temperature"],
                max_tokens=self._l3_config["max_tokens"],
            )
            l3_ms = int((time.monotonic() - t0) * 1000)

            draft_id = self.logger.log_draft(
                transaction_id=transaction_id,
                iteration=iteration,
                response_text=draft.response_text,
                target_cell_expressed=f"({draft.target_interaction_expressed}, {draft.target_scope_expressed})",
                pre_mortem_json=draft.pre_mortem_outputs.model_dump_json(),
                safeguards_json=json.dumps(draft.safeguards_included),
                provider=self._l3_config["provider"],
                model=self._l3_config["model"],
                latency_ms=l3_ms,
            )

            t0 = time.monotonic()
            critique = await self.critic.run(
                query, decision, draft,
                temperature=self._l4_config["temperature"],
                max_tokens=self._l4_config["max_tokens"],
            )
            l4_ms = int((time.monotonic() - t0) * 1000)

            self.logger.log_critique(
                draft_id=draft_id,
                passed=critique.passed,
                target_cell_match_score=critique.target_cell_match_score,
                pre_mortem_completeness_score=critique.pre_mortem_completeness_score,
                instruction_adherence_score=critique.instruction_adherence_score,
                issues=critique.issues,
                provider=self._l4_config["provider"],
                model=self._l4_config["model"],
                latency_ms=l4_ms,
            )

            if critique.passed:
                final_response = draft.response_text
                final_draft = draft
                final_critique = critique
                break

            if critique.refined_response:
                final_response = critique.refined_response
                final_draft = draft
                final_critique = critique
                break

            critique_feedback = f"Issues: {'; '.join(critique.issues)}"

        if final_response is None:
            final_response = draft.response_text
            final_draft = draft
            final_critique = critique

        self.logger.log_transaction(
            transaction_id=transaction_id,
            session_id=session_id,
            user_query=query,
            final_response=final_response,
            completed_successfully=True,
            user_id=user_id,
        )

        return {
            "type": "response",
            "response": final_response,
            "classification": classification.model_dump(),
            "decision": decision.model_dump(),
            "draft": final_draft.model_dump() if final_draft else None,
            "critique": final_critique.model_dump() if final_critique else None,
            "transaction_id": transaction_id,
        }
