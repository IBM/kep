import json
from .base import PromptStrategy, register_strategy


@register_strategy("zero")
class ZeroShot(PromptStrategy):
    def placeholder_values(self):
        return {
            "PERSONA":      self.ph.get("PERSONA", ""),
            "TASK":         self.ph.get("TASK", ""),
            "INSTRUCTIONS": self.ph.get("INSTRUCTIONS", []),
            "SCHEMAS":      self.ph.get("SCHEMAS", {}),
            # EXAMPLE intentionally omitted in zero-shot
        }