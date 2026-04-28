from pathlib import Path

import yaml

from ede.cells import Interaction, Scope, INTERACTION_LABELS, SCOPE_LABELS
from ede.schemas import MindsetClassification, ElevationDecision

POLICY_PATH = Path(__file__).parent.parent.parent / "config" / "elevation_policy.yaml"


class ElevationPolicyEngine:
    def __init__(self, policy_path: Path = POLICY_PATH):
        self.policy = yaml.safe_load(policy_path.read_text())

    def decide(
        self, classification: MindsetClassification, query: str
    ) -> ElevationDecision:
        current_i = Interaction.from_string(classification.top_interaction)
        current_s = Scope.from_string(classification.top_scope)

        stay = self._check_stay_overrides(classification, query)
        if stay:
            return ElevationDecision(
                current_interaction=INTERACTION_LABELS[current_i],
                current_scope=SCOPE_LABELS[current_s],
                target_interaction=INTERACTION_LABELS[current_i],
                target_scope=SCOPE_LABELS[current_s],
                decision_type="stay",
                rationale=stay["rationale"],
                pre_mortem_priority="downside",
            )

        target_i = min(current_i + 1, Interaction.CO_EVOLUTIONARY)
        target_s = min(current_s + 1, Scope.UNIVERSAL)

        priority_map = self.policy["default_policy"]["pre_mortem_priority_by_source_level"]
        avg_level = (current_i + current_s) / 2
        source_key = min(int(avg_level), 4)
        source_key = max(source_key, 1)
        pre_mortem_priority = priority_map[source_key]

        if target_i == current_i and target_s == current_s:
            return ElevationDecision(
                current_interaction=INTERACTION_LABELS[current_i],
                current_scope=SCOPE_LABELS[current_s],
                target_interaction=INTERACTION_LABELS[Interaction(target_i)],
                target_scope=SCOPE_LABELS[Scope(target_s)],
                decision_type="deepen",
                rationale=f"User already at ({INTERACTION_LABELS[current_i]}, {SCOPE_LABELS[current_s]}). Deepening rather than elevating.",
                pre_mortem_priority="pivot",
            )

        return ElevationDecision(
            current_interaction=INTERACTION_LABELS[current_i],
            current_scope=SCOPE_LABELS[current_s],
            target_interaction=INTERACTION_LABELS[Interaction(target_i)],
            target_scope=SCOPE_LABELS[Scope(target_s)],
            decision_type="elevate",
            rationale=f"Default policy: elevate one step each axis from ({INTERACTION_LABELS[current_i]}, {SCOPE_LABELS[current_s]})",
            pre_mortem_priority=pre_mortem_priority,
        )

    def _check_stay_overrides(
        self, classification: MindsetClassification, query: str
    ) -> dict | None:
        signal_threshold = self.policy.get("signal_confidence_threshold", 0.7)

        # Check context signals first (semantic detection from Layer 1)
        if classification.context_signals:
            detected_signal_names = {
                sig.signal.value
                for sig in classification.context_signals
                if sig.confidence >= signal_threshold
            }
            if detected_signal_names:
                for override in self.policy.get("stay_overrides", []):
                    triggers = override.get("triggers", {})
                    signal_triggers = set(triggers.get("signal_triggers", []))
                    if signal_triggers & detected_signal_names:
                        return override

        # Keyword fallback
        query_lower = query.lower()
        for override in self.policy.get("stay_overrides", []):
            triggers = override.get("triggers", {})
            keywords = triggers.get("keywords", [])
            if any(kw in query_lower for kw in keywords):
                return override

        return None
